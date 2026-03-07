# app/Services/hole_service.py

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.hole import Hole
from app.Repositories.hole_repository import HoleRepository

class HoleService:
    def __init__(self, session: AsyncSession):
        self.repo = HoleRepository(session)

    async def get_all(self) -> List[Hole]:
        return await self.repo.get_all()

    async def get_by_id(self, id: UUID) -> Optional[Hole]:
        return await self.repo.get_by_id(id)

    async def create(self, obj_in) -> Hole:
        return await self.repo.create(obj_in)

    async def update(self, id: UUID, obj_in) -> Optional[Hole]:
        return await self.repo.update(id, obj_in)

    async def delete(self, id: UUID) -> bool:
        return await self.repo.delete(id)
