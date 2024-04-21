import asyncio
import logging
from importlib import import_module

from alembic import context, util
from alembic.operations.ops import MigrationScript
from alembic.runtime.migration import MigrationContext
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import PostgresConfig
from src.core.db.models import Base

logging.basicConfig(level=logging.INFO)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    db_config = PostgresConfig()

    context.configure(
        url=str(db_config.dsn),
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    def process_revision_directives(
        context: MigrationContext, _revision: tuple[str], directives: list[MigrationScript]
    ) -> None:
        if not context.config:
            return

        if (
            getattr(context.config.cmd_opts, "autogenerate", False)
            and directives[0].upgrade_ops
            and directives[0].upgrade_ops.is_empty()
        ):
            directives[:] = []
            context.config.print_stdout("No new upgrade operations detected.")

    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        compare_type=True,
        compare_server_default=True,
        process_revision_directives=process_revision_directives,  # type: ignore[arg-type]
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    db_config = PostgresConfig()

    connectable = create_async_engine(url=str(db_config.dsn), poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


def import_models() -> None:
    locations = context.config.get_main_option("model_locations")
    if not locations:
        return

    for module in locations.split():
        with util.status(f"Importing models from '{module}'"):
            import_module(module)


import_models()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
