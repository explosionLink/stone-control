# app/Services/pdf_processing_service.py

import re
import math
import uuid
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

import pdfplumber
import ezdxf
from shapely.geometry import LineString, Polygon as ShapelyPolygon
from shapely.ops import unary_union, polygonize, snap
from PIL import Image

class PDFProcessingService:
    def __init__(self, imports_dir: str = "imports", outputs_dir: str = "outputs"):
        self.imports_dir = Path(imports_dir)
        self.outputs_dir = Path(outputs_dir)
        self.imports_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        # Configurazione parsing
        self.MIN_EDGE_LEN = 20.0
        self.SNAP_TOL = 1.0
        self.PAGE_BORDER_MARGIN = 6.0
        self.MAX_PAGE_FILL_FRAC = 0.95
        self.MIN_HOLE_AREA_FRAC = 0.002
        self.MAX_HOLE_AREA_FRAC = 0.60

    def extract_top_dims(self, text: str) -> Optional[Tuple[float, float]]:
        m = re.search(r"(\d{3,5})\s*x\s*20\s*x\s*(\d{3,5})", text, flags=re.IGNORECASE)
        if not m:
            return None
        return float(m.group(1)), float(m.group(2))

    def edges_to_lines(self, page) -> List[LineString]:
        lines: List[LineString] = []
        for e in page.edges:
            dx = float(e["x1"]) - float(e["x0"])
            dy = float(e["bottom"]) - float(e["top"])
            if math.hypot(dx, dy) < self.MIN_EDGE_LEN:
                continue
            lines.append(LineString([(float(e["x0"]), float(e["top"])), (float(e["x1"]), float(e["bottom"]))]))
        return lines

    def lines_to_polygons(self, lines: List[LineString]) -> List[ShapelyPolygon]:
        if not lines:
            return []
        merged = unary_union(lines)
        merged_snapped = snap(merged, merged, self.SNAP_TOL)
        polys = list(polygonize(merged_snapped))
        return [p for p in polys if isinstance(p, ShapelyPolygon) and p.area > 0]

    def pick_outer_polygon(self, polys: List[ShapelyPolygon], page_w: float, page_h: float, expected_aspect: float) -> Optional[ShapelyPolygon]:
        page_area = page_w * page_h
        candidates = []
        for p in polys:
            minx, miny, maxx, maxy = p.bounds
            w, h = maxx - minx, maxy - miny
            if w <= 0 or h <= 0 or (p.area / page_area) > self.MAX_PAGE_FILL_FRAC:
                continue

            # Check border
            if minx <= self.PAGE_BORDER_MARGIN or miny <= self.PAGE_BORDER_MARGIN or \
               (page_w - maxx) <= self.PAGE_BORDER_MARGIN or (page_h - maxy) <= self.PAGE_BORDER_MARGIN:
                continue

            aspect = w / h
            score_aspect = abs(math.log(aspect / expected_aspect))
            candidates.append((score_aspect, -p.area, p))

        if not candidates:
            filtered = [p for p in polys if (p.area / page_area) <= self.MAX_PAGE_FILL_FRAC]
            return max(filtered, key=lambda g: g.area) if filtered else (max(polys, key=lambda g: g.area) if polys else None)

        candidates.sort(key=lambda t: (t[0], t[1]))
        return candidates[0][2]

    def pick_holes(self, polys: List[ShapelyPolygon], outer: ShapelyPolygon) -> List[ShapelyPolygon]:
        holes = []
        outer_area = outer.area
        for p in polys:
            if p.equals(outer) or not p.within(outer):
                continue
            frac = p.area / outer_area
            if self.MIN_HOLE_AREA_FRAC <= frac <= self.MAX_HOLE_AREA_FRAC:
                holes.append(p)

        holes.sort(key=lambda g: g.area, reverse=True)
        pruned = []
        for h in holes:
            if not any(h.within(big) for big in pruned):
                pruned.append(h)
        return pruned

    def repair_polygon(self, poly: ShapelyPolygon) -> ShapelyPolygon:
        if poly.is_valid and not poly.is_empty:
            return poly
        fixed = poly.buffer(0)
        if fixed.is_empty: return fixed
        return max(list(fixed.geoms), key=lambda g: g.area) if fixed.geom_type == "MultiPolygon" else fixed

    def process_pdf(self, pdf_path: Path, order_code: str) -> List[Dict[str, Any]]:
        results = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for pageno, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                dims = self.extract_top_dims(text)
                if not dims:
                    continue

                L_mm, P_mm = dims
                lines = self.edges_to_lines(page)
                if not lines: continue

                polys = self.lines_to_polygons(lines)
                if not polys: continue

                outer = self.pick_outer_polygon(polys, float(page.width), float(page.height), L_mm / P_mm)
                if not outer: continue
                outer = self.repair_polygon(outer)

                holes = self.pick_holes(polys, outer)
                holes = [self.repair_polygon(h) for h in holes]

                # Generazione DXF
                dxf_filename = f"{order_code}_{pageno}.dxf"
                dxf_path = self.outputs_dir / dxf_filename
                self.write_dxf(dxf_path, outer, holes, L_mm, P_mm)

                # Generazione Preview
                preview_filename = f"{order_code}_{pageno}.png"
                preview_path = self.outputs_dir / preview_filename
                self.save_preview(page, preview_path)

                # Dati fori per DB
                holes_data = []
                minx, miny, maxx, maxy = outer.bounds
                ow, oh = maxx - minx, maxy - miny
                for h in holes:
                    h_minx, h_miny, h_maxx, h_maxy = h.bounds
                    h_w_mm = ((h_maxx - h_minx) / ow) * L_mm
                    h_h_mm = ((h_maxy - h_miny) / oh) * P_mm
                    h_x_mm = ((h_minx - minx) / ow) * L_mm
                    h_y_mm = (1.0 - (h_miny - miny) / oh) * P_mm - h_h_mm # Invert Y

                    holes_data.append({
                        "x_mm": h_x_mm,
                        "y_mm": h_y_mm,
                        "width_mm": h_w_mm,
                        "height_mm": h_h_mm,
                        "type": "foro" # Default
                    })

                results.append({
                    "label": f"Pagina {pageno}",
                    "width_mm": L_mm,
                    "height_mm": P_mm,
                    "dxf_path": dxf_filename, # Salva solo il nome file
                    "preview_path": preview_filename, # Salva solo il nome file
                    "holes": holes_data
                })
        return results

    def write_dxf(self, path: Path, outer: ShapelyPolygon, holes: List[ShapelyPolygon], L_mm: float, P_mm: float):
        doc = ezdxf.new("R2010")
        doc.units = ezdxf.units.MM
        msp = doc.modelspace()

        minx, miny, maxx, maxy = outer.bounds
        ow, oh = maxx - minx, maxy - miny

        def transform(x, y):
            tx = ((x - minx) / ow) * L_mm
            ty = (1.0 - (y - miny) / oh) * P_mm
            return float(tx), float(ty)

        outer_coords = [transform(x, y) for x, y in outer.exterior.coords]
        msp.add_lwpolyline(outer_coords[:-1], close=True, dxfattribs={"layer": "OUTER"})

        for h in holes:
            h_coords = [transform(x, y) for x, y in h.exterior.coords]
            msp.add_lwpolyline(h_coords[:-1], close=True, dxfattribs={"layer": "INNER"})

        doc.saveas(str(path))

    def save_preview(self, page, path: Path):
        im = page.to_image(resolution=150)
        im.save(str(path))
