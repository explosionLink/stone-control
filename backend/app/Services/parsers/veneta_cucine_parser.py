# app/Services/parsers/veneta_cucine_parser.py

import re
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pdfplumber
import ezdxf
from shapely.geometry import LineString, Polygon as ShapelyPolygon, Point as ShapelyPoint
from shapely.ops import unary_union, polygonize, snap, transform
from .base_parser import BaseParser

class VenetaCucineParser(BaseParser):
    def __init__(self, outputs_dir: Path):
        super().__init__(outputs_dir)
        self.MIN_EDGE_LEN = 20.0
        self.SNAP_TOL = 1.0
        self.PAGE_BORDER_MARGIN = 6.0
        self.MAX_PAGE_FILL_FRAC = 0.95
        self.MIN_HOLE_AREA_FRAC = 0.001 # Reduced to catch smaller holes
        self.MAX_HOLE_AREA_FRAC = 0.60

    def get_client_code(self) -> str:
        return "VENETA_CUCINE"

    def extract_metadata(self, text: str) -> Dict[str, Any]:
        metadata = {
            "order_code": None,
            "width_mm": 0.0,
            "height_mm": 0.0,
            "thickness_mm": 20.0, # Default
            "material": None,
            "is_sottotop": False
        }

        # Dimensions: 2155 x 20 x 638
        dim_match = re.search(r"(\d{3,5})\s*x\s*(\d{1,3})\s*x\s*(\d{3,5})", text)
        if dim_match:
            metadata["width_mm"] = float(dim_match.group(1))
            metadata["thickness_mm"] = float(dim_match.group(2))
            metadata["height_mm"] = float(dim_match.group(3))

        # Order code (from text like "Ordine 3CAD 306230147")
        order_match = re.search(r"Ordine\s+3CAD\s+(\d+)", text)
        if order_match:
            metadata["order_code"] = order_match.group(1)

        # Sottotop check
        if "SOTTO TOP VEDI DIMA" in text.upper() or "SOTTOTOP" in text.upper():
            metadata["is_sottotop"] = True

        # Material (e.g. "Top Caranto Ker in Massa")
        mat_match = re.search(r"Top\s+(.*?)\s+Sp\.\d+", text)
        if mat_match:
            metadata["material"] = mat_match.group(1).strip()

        return metadata

    def parse(self, pdf_path: Path, order_code: str) -> List[Dict[str, Any]]:
        results = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for pageno, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                meta = self.extract_metadata(text)

                if meta["width_mm"] == 0 or meta["height_mm"] == 0:
                    continue

                lines = self.edges_to_lines(page)
                if not lines: continue

                polys = self.lines_to_polygons(lines)
                if not polys: continue

                expected_aspect = meta["width_mm"] / meta["height_mm"]
                outer = self.pick_outer_polygon(polys, float(page.width), float(page.height), expected_aspect)
                if not outer: continue
                outer = self.repair_polygon(outer)

                holes = self.pick_holes(polys, outer)
                holes = [self.repair_polygon(h) for h in holes]

                # Create the main piece
                piece_data = self.build_piece_result(
                    pageno, order_code, page, outer, holes, meta, is_mirrored=False
                )
                results.append(piece_data)

                # If Sottotop, create the mirrored piece with template holes
                if meta["is_sottotop"]:
                    mirrored_piece = self.build_piece_result(
                        pageno, order_code, page, outer, holes, meta, is_mirrored=True
                    )
                    results.append(mirrored_piece)

        return results

    def build_piece_result(self, pageno, order_code, page, outer, holes, meta, is_mirrored=False) -> Dict[str, Any]:
        suffix = "_mirrored" if is_mirrored else ""
        dxf_filename = f"{order_code}_{pageno}{suffix}.dxf"
        preview_filename = f"{order_code}_{pageno}{suffix}.png"

        # Transformations for mirroring if needed
        # In actual implementation, mirroring happens on the geometry before DXF export

        holes_data = []
        minx, miny, maxx, maxy = outer.bounds
        ow, oh = maxx - minx, maxy - miny

        for h in holes:
            h_minx, h_miny, h_maxx, h_maxy = h.bounds
            h_w_mm = ((h_maxx - h_minx) / ow) * meta["width_mm"]
            h_h_mm = ((h_maxy - h_miny) / oh) * meta["height_mm"]
            h_x_mm = ((h_minx - minx) / ow) * meta["width_mm"]
            h_y_mm = (1.0 - (h_miny - miny) / oh) * meta["height_mm"] - h_h_mm

            if is_mirrored:
                # Mirror X: X_new = Width - X_old - HoleWidth
                h_x_mm = meta["width_mm"] - h_x_mm - h_w_mm

            holes_data.append({
                "x_mm": h_x_mm,
                "y_mm": h_y_mm,
                "width_mm": h_w_mm,
                "height_mm": h_h_mm,
                "type": "foro_lavello" if meta["is_sottotop"] else "foro"
            })

        # Add template holes if mirrored (dima)
        if is_mirrored:
            # Logic to add small Ø12 holes around the main sink hole
            # This is a simplified version; in reality, we'd place them at corners + offset
            template_holes = self.generate_template_holes(holes_data)
            holes_data.extend(template_holes)

        # Generate DXF and PNG
        self.write_dxf(self.outputs_dir / dxf_filename, outer, holes_data, meta, is_mirrored)
        # Note: png preview for mirrored might just be the same or a flip of the original
        self.save_preview(page, self.outputs_dir / preview_filename, is_mirrored)

        return {
            "label": f"Pezzo {pageno}{' (Specchiato)' if is_mirrored else ''}",
            "width_mm": meta["width_mm"],
            "height_mm": meta["height_mm"],
            "material": meta["material"],
            "thickness_mm": meta["thickness_mm"],
            "is_mirrored": is_mirrored,
            "is_machining": is_mirrored,
            "dxf_path": dxf_filename,
            "preview_path": preview_filename,
            "holes": holes_data
        }

    def generate_template_holes(self, main_holes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        new_holes = []
        for mh in main_holes:
            if "lavello" in mh["type"]:
                # Place 4 holes at 20mm offset from corners
                offset = 20.0
                corners = [
                    (mh["x_mm"] - offset, mh["y_mm"] - offset),
                    (mh["x_mm"] + mh["width_mm"] + offset, mh["y_mm"] - offset),
                    (mh["x_mm"] - offset, mh["y_mm"] + mh["height_mm"] + offset),
                    (mh["x_mm"] + mh["width_mm"] + offset, mh["y_mm"] + mh["height_mm"] + offset)
                ]
                for cx, cy in corners:
                    new_holes.append({
                        "x_mm": cx, "y_mm": cy,
                        "diameter_mm": 12.0, "depth_mm": 15.0,
                        "type": "bussola"
                    })
        return new_holes

    # Helper methods (reused from previous implementation with minor tweaks)
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
        if not lines: return []
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
            if w <= 0 or h <= 0 or (p.area / page_area) > self.MAX_PAGE_FILL_FRAC: continue
            if minx <= self.PAGE_BORDER_MARGIN or miny <= self.PAGE_BORDER_MARGIN: continue

            aspect = w / h
            score_aspect = abs(math.log(aspect / expected_aspect))
            candidates.append((score_aspect, -p.area, p))

        candidates.sort(key=lambda t: (t[0], t[1]))
        return candidates[0][2] if candidates else None

    def pick_holes(self, polys: List[ShapelyPolygon], outer: ShapelyPolygon) -> List[ShapelyPolygon]:
        holes = []
        outer_area = outer.area
        for p in polys:
            if p.equals(outer) or not p.within(outer): continue
            frac = p.area / outer_area
            if self.MIN_HOLE_AREA_FRAC <= frac <= self.MAX_HOLE_AREA_FRAC:
                holes.append(p)
        return holes

    def repair_polygon(self, poly: ShapelyPolygon) -> ShapelyPolygon:
        if poly.is_valid and not poly.is_empty: return poly
        fixed = poly.buffer(0)
        return max(list(fixed.geoms), key=lambda g: g.area) if fixed.geom_type == "MultiPolygon" else fixed

    def write_dxf(self, path: Path, outer: ShapelyPolygon, holes_data: List[Dict[str, Any]], meta: Dict[str, Any], is_mirrored: bool):
        doc = ezdxf.new("R2010")
        doc.units = ezdxf.units.MM
        msp = doc.modelspace()

        minx, miny, maxx, maxy = outer.bounds
        ow, oh = maxx - minx, maxy - miny

        def transform_pt(x, y):
            tx = ((x - minx) / ow) * meta["width_mm"]
            ty = (1.0 - (y - miny) / oh) * meta["height_mm"]
            if is_mirrored:
                tx = meta["width_mm"] - tx
            return float(tx), float(ty)

        outer_coords = [transform_pt(x, y) for x, y in outer.exterior.coords]
        msp.add_lwpolyline(outer_coords[:-1], close=True, dxfattribs={"layer": "PERIMETRO"})

        for h in holes_data:
            if "diameter_mm" in h and h["diameter_mm"]:
                msp.add_circle((h["x_mm"], h["y_mm"]), h["diameter_mm"]/2, dxfattribs={"layer": "LAVORAZIONE"})
            else:
                # Rectangle hole
                pts = [
                    (h["x_mm"], h["y_mm"]),
                    (h["x_mm"] + h["width_mm"], h["y_mm"]),
                    (h["x_mm"] + h["width_mm"], h["y_mm"] + h["height_mm"]),
                    (h["x_mm"], h["y_mm"] + h["height_mm"])
                ]
                msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "LAVORAZIONE"})

        doc.saveas(str(path))

    def save_preview(self, page, path: Path, is_mirrored: bool):
        im = page.to_image(resolution=150).original
        if is_mirrored:
            im = im.transpose(method=0) # FLIP_LEFT_RIGHT is 0 in some PIL versions or use Image.FLIP_LEFT_RIGHT
        im.save(str(path))
