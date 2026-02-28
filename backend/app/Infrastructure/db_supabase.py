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
    - Se l'URL utilizza asyncpg, viene costruito un SSLContext che utilizza il bundle CA di 'certifi'.
    - In ambienti non di produzione, se DB_SSL_VERIFY è disabilitato, la verifica viene saltata.
    """
    if "+asyncpg" not in settings.DATABASE_URL:
        return {}

    # Bypass della verifica SSL (solo per sviluppo)
    if settings.ENV != "prod" and not settings.DB_SSL_VERIFY:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return {"ssl": ctx}

    # Verifica stretta utilizzando certifi
    try:
        import certifi
        cafile = certifi.where()
        ctx = ssl.create_default_context(cafile=cafile)
        if hasattr(ssl, "PROTOCOL_TLS_CLIENT"):
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        return {"ssl": ctx}
    except Exception:
        # Fallback all'uso del trust store di sistema
        return {"ssl": True}


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
