# app/Controllers/client_controller.py

from typing import List, Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db_supabase import get_db
from app.Services.client_service import ClientService
from app.Schemas.client import ClientRead
from app.Router.supabase_auth import get_current_claims

router = APIRouter(prefix="/clients", tags=["Clients"])

def get_service(session: Annotated[AsyncSession, Depends(get_db)]) -> ClientService:
    return ClientService(session)

@router.get("/", response_model=List[ClientRead])
async def list_clients(
    service: Annotated[ClientService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    return await service.get_all()

@router.get("/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: UUID,
    service: Annotated[ClientService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    client = await service.get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client non trovato")
    return client

from app.Schemas.client import ClientCreate, ClientUpdate

@router.post("/", response_model=ClientRead)
async def create_client(
    schema: ClientCreate,
    service: Annotated[ClientService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    return await service.create(schema)

@router.patch("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: UUID,
    schema: ClientUpdate,
    service: Annotated[ClientService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    updated = await service.update(client_id, schema)
    if not updated:
        raise HTTPException(status_code=404, detail="Client non trovato")
    return updated

@router.delete("/{client_id}")
async def delete_client(
    client_id: UUID,
    service: Annotated[ClientService, Depends(get_service)],
    user_claims: Annotated[dict, Depends(get_current_claims)]
):
    success = await service.delete(client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client non trovato")
    return {"deleted": True}
