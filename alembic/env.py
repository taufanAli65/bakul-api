import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.base_class import Base
from app.core.config import settings
from app.domain.users.models import MstUser
from app.domain.products.models import MstProduct, TrnProductStock
from app.domain.transactions.models import MstTransaction, TrnTransactionItem, TrnTransactionStatus
from app.domain.expeditions.models import MstExpeditionService
from app.domain.carts.models import MstCart

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_section_option(config.config_ini_section, "sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata

def do_run_migrations(connection):
    """
    Fungsi pembantu (synchronous) yang dipanggil di dalam run_sync.
    Alembic butuh context sync untuk menjalankan migrasi.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode menggunakan Async Engine."""
    
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())