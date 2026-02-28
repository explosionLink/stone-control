# app/Controllers/order_controller.py

from typing import Annotated, List
from fastapi import Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.Infrastructure.db_supabase import get_db
from app.Services.pdf_processing_service import PDFProcessingService
from app.Models.order import Order
from app.Models.polygon import Polygon
from app.Models.hole import Hole
from app.Schemas.order import OrderRead
from uuid import UUID
from pathlib import Path
import shutil

class OrderController:
    def __init__(self):
        self.pdf_svc = PDFProcessingService(imports_dir="backend/imports", outputs_dir="backend/outputs")

    async def list_orders(
        self,
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> List[OrderRead]:
        stmt = select(Order).options(
            selectinload(Order.polygons).selectinload(Polygon.holes)
        ).order_by(Order.created_at.desc())
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [OrderRead.model_validate(r) for r in rows]

    async def import_pdf(
        self,
        db: Annotated[AsyncSession, Depends(get_db)],
        file: UploadFile = File(...),
        claims: dict = None # Will be passed from router if needed
    ) -> OrderRead:
        # 1. Salva il file PDF (sanitizzazione base del nome file)
        safe_filename = Path(file.filename).name
        file_id = Path(safe_filename).stem
        import_path = self.pdf_svc.imports_dir / safe_filename
        with import_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Elaborazione
        processing_results = self.pdf_svc.process_pdf(import_path, file_id)
        if not processing_results:
            raise HTTPException(status_code=400, detail="Nessuna quota valida trovata nel PDF")

        # 3. Salvataggio nel DB
        user_id = UUID(claims["sub"]) if claims and "sub" in claims else None

        # Default client for now: Veneta Cucine
        from app.Models.client import Client
        stmt_client = select(Client).where(Client.code == "VENETA_CUCINE")
        res_client = await db.execute(stmt_client)
        client = res_client.scalar_one_or_none()
        client_id = client.id if client else None

        # Cerca se l'ordine esiste già o creane uno nuovo
        stmt = select(Order).where(Order.code == file_id)
        existing = await db.execute(stmt)
        order = existing.scalar_one_or_none()

        if not order:
            order = Order(code=file_id, user_id=user_id, client_id=client_id)
            db.add(order)
            await db.flush()
        else:
            # Opzionale: pulisci poligoni vecchi se stai ri-importando
            pass

        for res in processing_results:
            poly = Polygon(
                order_id=order.id,
                label=res["label"],
                width_mm=res["width_mm"],
                height_mm=res["height_mm"],
                dxf_path=res["dxf_path"],
                preview_path=res["preview_path"],
                is_mirrored=res.get("is_mirrored", False),
                is_machining=res.get("is_machining", False),
                material=res.get("material"),
                thickness_mm=res.get("thickness_mm")
            )
            db.add(poly)
            await db.flush()

            for h_res in res["holes"]:
                hole = Hole(
                    polygon_id=poly.id,
                    type=h_res["type"],
                    x_mm=h_res["x_mm"],
                    y_mm=h_res["y_mm"],
                    width_mm=h_res.get("width_mm"),
                    height_mm=h_res.get("height_mm"),
                    diameter_mm=h_res.get("diameter_mm"),
                    depth_mm=h_res.get("depth_mm")
                )
                db.add(hole)

        await db.commit()
        await db.refresh(order)

        # Ricarica con relazioni per la risposta
        stmt = select(Order).where(Order.id == order.id).options(
            selectinload(Order.polygons).selectinload(Polygon.holes)
        )
        result = await db.execute(stmt)
        return OrderRead.model_validate(result.scalar_one())

    async def get_order(
        self,
        order_id: UUID,
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> OrderRead:
        stmt = select(Order).where(Order.id == order_id).options(
            selectinload(Order.polygons).selectinload(Polygon.holes)
        )
        result = await db.execute(stmt)
        row = result.scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail="Ordine non trovato")
        return OrderRead.model_validate(row)
