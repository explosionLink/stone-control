# app/Infrastructure/db_supabase.py
from __future__ import annotations

from typing import AsyncGenerator
import ssl
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.Core.config import settings

# Base class for SQLAlchemy models (SQLAlchemy 2.0 style)
# Utilizzando una classe che eredita da DeclarativeBase risolviamo gli errori di tipo in Pylance
class Base(DeclarativeBase):
    pass

# Import all models here to ensure they are registered with SQLAlchemy's Base
# before any operation that needs them is executed. This prevents circular
# dependency errors between models with relationships.
from app.Models.user_supabase import UserSupabase
from app.Models.role import Role
from app.Models.user_supabase_role import UserSupabaseRole
from app.Models.client import Client
from app.Models.hole_library import HoleLibrary
from app.Models.order import Order
from app.Models.polygon import Polygon
from app.Models.hole import Hole


def _make_ssl_context() -> dict:
    """
    Configura il contesto SSL per la connessione al database.
    Supabase richiede SSL attivo. Usiamo 'require' come valore predefinito
    che è compatibile con asyncpg tramite SQLAlchemy.
    """
    if "+asyncpg" not in settings.DATABASE_URL:
        return {}

    # Per asyncpg, passare ssl="require" è il modo più semplice e compatibile
    # confermato funzionante con Supabase Session Pooler.
    return {"ssl": "require"}


# Ottimizzazione per Supabase: viene utilizzato NullPool quando un pooler esterno
# (come pgBouncer) è attivo, per evitare conflitti nella gestione delle connessioni.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args=_make_ssl_context(),
    poolclass=NullPool,
)

# Factory per le sessioni asincrone
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency per ottenere una sessione del database asincrona.
    Garantisce che il fuso orario della sessione sia impostato su UTC.
    """
    async with SessionLocal() as session:
        await session.execute(text("SET TIME ZONE 'UTC'"))
        yield session


async def check_connection() -> bool:
    """
    Verifica se la connessione al database è attiva.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def dispose_engine() -> None:
    """
    Chiude correttamente l'engine SQLAlchemy.
    """
    await engine.dispose()
