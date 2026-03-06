# app/Controllers/hole_controller.py

from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db_supabase import get_db
from app.Services.hole_service import HoleService
from app.Schemas.order import HoleRead, HoleBase
from app.Router.supabase_auth import get_current_claims

router = APIRouter(prefix="/holes", tags=["Holes"])

def get_service(session: Annotated[AsyncSession, Depends(get_db)]) -> HoleService:
    return HoleService(session)

@router.post("/", response_model=HoleRead)
async def create_hole(
    schema: HoleBase,
    service: Annotated[HoleService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    # Need polygon_id in schema to create
    return await service.create(schema)

@router.patch("/{id}", response_model=HoleRead)
async def update_hole(
    id: UUID,
    schema: HoleBase,
    service: Annotated[HoleService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    updated = await service.update(id, schema)
    if not updated:
        raise HTTPException(status_code=404, detail="Foro non trovato")
    return updated

@router.delete("/{id}")
async def delete_hole(
    id: UUID,
    service: Annotated[HoleService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    success = await service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Foro non trovato")
    return {"deleted": True}
