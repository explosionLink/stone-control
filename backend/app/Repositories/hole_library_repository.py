# app/Repositories/hole_library_repository.py

from app.Core.base_repository import BaseRepository
from app.Models.hole_library import HoleLibrary
from app.Schemas.hole_library import HoleLibraryCreate, HoleLibraryUpdate
from sqlalchemy.ext.asyncio import AsyncSession

class HoleLibraryRepository(BaseRepository[HoleLibrary, HoleLibraryCreate, HoleLibraryUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(HoleLibrary, session)
