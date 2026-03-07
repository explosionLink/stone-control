# app/Services/order_service.py

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.Models.order import Order
from app.Models.polygon import Polygon
from app.Repositories.order_repository import OrderRepository

class OrderService:
    def __init__(self, session: AsyncSession):
        self.repo = OrderRepository(session)

    async def get_all(self) -> List[Order]:
        stmt = select(Order).options(
            selectinload(Order.polygons).selectinload(Polygon.holes)
        ).order_by(Order.created_at.desc())
        result = await self.repo.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, id: UUID) -> Optional[Order]:
        stmt = select(Order).where(Order.id == id).options(
            selectinload(Order.polygons).selectinload(Polygon.holes)
        )
        result = await self.repo.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, obj_in) -> Order:
        return await self.repo.create(obj_in)

    async def update(self, id: UUID, obj_in) -> Optional[Order]:
        return await self.repo.update(id, obj_in)

    async def delete(self, id: UUID) -> bool:
        return await self.repo.delete(id)
