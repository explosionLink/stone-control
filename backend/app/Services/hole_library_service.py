# app/Services/hole_library_service.py

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.hole_library import HoleLibrary
from app.Repositories.hole_library_repository import HoleLibraryRepository
from app.Schemas.hole_library import HoleLibraryCreate, HoleLibraryUpdate

class HoleLibraryService:
    def __init__(self, session: AsyncSession):
        self.repo = HoleLibraryRepository(session)

    async def get_all(self) -> List[HoleLibrary]:
        return await self.repo.get_all()

    async def get_by_id(self, id: UUID) -> Optional[HoleLibrary]:
        return await self.repo.get_by_id(id)

    async def create(self, schema: HoleLibraryCreate) -> HoleLibrary:
        return await self.repo.create(schema.model_dump())

    async def update(self, id: UUID, schema: HoleLibraryUpdate) -> Optional[HoleLibrary]:
        return await self.repo.update(id, schema.model_dump(exclude_unset=True))

    async def delete(self, id: UUID) -> bool:
        return await self.repo.delete(id)
