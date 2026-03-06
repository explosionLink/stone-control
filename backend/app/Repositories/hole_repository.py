# app/Repositories/hole_repository.py

from app.Core.base_repository import BaseRepository
from app.Models.hole import Hole
from app.Schemas.order import HoleBase # Use HoleBase from order schemas
from sqlalchemy.ext.asyncio import AsyncSession

class HoleRepository(BaseRepository[Hole, HoleBase, HoleBase]):
    def __init__(self, session: AsyncSession):
        super().__init__(Hole, session)
