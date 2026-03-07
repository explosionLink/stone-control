# app/Repositories/order_repository.py

from app.Core.base_repository import BaseRepository
from app.Models.order import Order
from app.Schemas.order import OrderBase, OrderRead # OrderUpdate and OrderCreate can be added to Schemas
from sqlalchemy.ext.asyncio import AsyncSession

class OrderRepository(BaseRepository[Order, OrderBase, OrderBase]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)
