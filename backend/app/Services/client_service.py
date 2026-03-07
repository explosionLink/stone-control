# app/Services/client_service.py

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.client import Client
from app.Repositories.client_repository import ClientRepository

class ClientService:
    def __init__(self, session: AsyncSession):
        self.repo = ClientRepository(session)

    async def get_all(self) -> List[Client]:
        return await self.repo.get_all()

    async def get_by_id(self, id: UUID) -> Optional[Client]:
        return await self.repo.get_by_id(id)

    async def get_by_code(self, code: str) -> Optional[Client]:
        # BaseRepository doesn't have get_by_code, let's use search or custom query
        from sqlalchemy import select
        stmt = select(Client).where(Client.code == code)
        result = await self.repo.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, obj_in) -> Client:
        return await self.repo.create(obj_in)

    async def update(self, id: UUID, obj_in) -> Optional[Client]:
        return await self.repo.update(id, obj_in)

    async def delete(self, id: UUID) -> bool:
        return await self.repo.delete(id)
