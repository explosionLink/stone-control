# app/Controllers/polygon_controller.py

from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db_supabase import get_db
from app.Services.polygon_service import PolygonService
from app.Schemas.order import PolygonRead, PolygonBase
from app.Router.supabase_auth import get_current_claims

router = APIRouter(prefix="/polygons", tags=["Polygons"])

def get_service(session: Annotated[AsyncSession, Depends(get_db)]) -> PolygonService:
    return PolygonService(session)

@router.get("/{id}", response_model=PolygonRead)
async def get_polygon(
    id: UUID,
    service: Annotated[PolygonService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    poly = await service.get_by_id(id)
    if not poly:
        raise HTTPException(status_code=404, detail="Poligono non trovato")
    return poly

@router.patch("/{id}", response_model=PolygonRead)
async def update_polygon(
    id: UUID,
    schema: PolygonBase,
    service: Annotated[PolygonService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    updated = await service.update(id, schema)
    if not updated:
        raise HTTPException(status_code=404, detail="Poligono non trovato")
    return updated

@router.delete("/{id}")
async def delete_polygon(
    id: UUID,
    service: Annotated[PolygonService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    success = await service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Poligono non trovato")
    return {"deleted": True}
