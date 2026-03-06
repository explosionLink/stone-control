# app/Services/polygon_service.py

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.polygon import Polygon
from app.Repositories.polygon_repository import PolygonRepository

class PolygonService:
    def __init__(self, session: AsyncSession):
        self.repo = PolygonRepository(session)

    async def get_all(self) -> List[Polygon]:
        return await self.repo.get_all()

    async def get_by_id(self, id: UUID) -> Optional[Polygon]:
        return await self.repo.get_by_id(id)

    async def create(self, obj_in) -> Polygon:
        return await self.repo.create(obj_in)

    async def update(self, id: UUID, obj_in) -> Optional[Polygon]:
        return await self.repo.update(id, obj_in)

    async def delete(self, id: UUID) -> bool:
        return await self.repo.delete(id)
