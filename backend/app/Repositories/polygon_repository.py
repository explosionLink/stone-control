# app/Repositories/polygon_repository.py

from app.Core.base_repository import BaseRepository
from app.Models.polygon import Polygon
from app.Schemas.order import PolygonBase # Use PolygonBase from order schemas
from sqlalchemy.ext.asyncio import AsyncSession

class PolygonRepository(BaseRepository[Polygon, PolygonBase, PolygonBase]):
    def __init__(self, session: AsyncSession):
        super().__init__(Polygon, session)
