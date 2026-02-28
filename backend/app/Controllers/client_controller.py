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
