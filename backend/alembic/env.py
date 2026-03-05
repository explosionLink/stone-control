import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Aggiunge la directory corrente (backend/) al path per poter importare 'app'
sys.path.append(os.getcwd())

from app.Core.config import settings
# Stampa diagnostica per aiutare l'utente a capire se Alembic sta usando i parametri corretti
settings.debug_print_config()

from app.Infrastructure.db_supabase import Base
# Importa i modelli per registrarli nel metadata
from app.Models.role import Role
from app.Models.user_supabase_role import UserSupabaseRole
from app.Models.user_supabase import UserSupabase
from app.Models.client import Client
from app.Models.hole_library import HoleLibrary
from app.Models.order import Order
from app.Models.polygon import Polygon
from app.Models.hole import Hole

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Sovrascrive l'URL del database con quello delle impostazioni
# Diamo priorità a DATABASE_ALEMBIC_URL se presente
if settings.DATABASE_ALEMBIC_URL:
    print("Alembic: Uso di DATABASE_ALEMBIC_URL per la migrazione.")
    db_url = settings.assemble_db_url(settings.DATABASE_ALEMBIC_URL)
else:
    print("Alembic: Uso di DATABASE_URL per la migrazione.")
    db_url = settings.DATABASE_URL

config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def include_object(object, name, type_, reflected, compare_to):
    """
    Esclude lo schema 'auth' gestito da Supabase dalle migrazioni autogenerate.
    """
    if type_ == "table" and getattr(object, "schema", None) == "auth":
        return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
