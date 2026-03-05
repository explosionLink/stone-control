# app/Controllers/hole_library_controller.py

from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db_supabase import get_db
from app.Services.hole_library_service import HoleLibraryService
from app.Schemas.hole_library import HoleLibraryRead, HoleLibraryCreate, HoleLibraryUpdate
from app.Router.supabase_auth import get_current_claims

router = APIRouter(prefix="/hole-library", tags=["Hole Library"])

# Dependency per il servizio
def get_service(session: Annotated[AsyncSession, Depends(get_db)]) -> HoleLibraryService:
    return HoleLibraryService(session)

@router.get("/", response_model=List[HoleLibraryRead])
async def list_holes(
    service: Annotated[HoleLibraryService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    return await service.get_all()

@router.post("/", response_model=HoleLibraryRead, status_code=status.HTTP_201_CREATED)
async def create_hole(
    schema: HoleLibraryCreate,
    service: Annotated[HoleLibraryService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    # Solo admin possono aggiungere alla libreria (RBAC check opzionale qui o via middleware)
    return await service.create(schema)

@router.patch("/{id}", response_model=HoleLibraryRead)
async def update_hole(
    id: Annotated[UUID, Path()],
    schema: HoleLibraryUpdate,
    service: Annotated[HoleLibraryService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    updated = await service.update(id, schema)
    if not updated:
        raise HTTPException(status_code=404, detail="Hole definition not found")
    return updated

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hole(
    id: Annotated[UUID, Path()],
    service: Annotated[HoleLibraryService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    success = await service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Hole definition not found")
