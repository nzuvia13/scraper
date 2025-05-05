from collections.abc import Generator
from contextlib import contextmanager
from logging.config import fileConfig

from alembic import context
from sqlalchemy import MetaData

from rfp_scraper.db import get_database_url, get_engine_sync, models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This powers autogenerator support
target_metadata = models.SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


@contextmanager
def _configure_context(online: bool = False) -> Generator[None, None, None]:
    """Configure alembic context for online or offline mode."""
    default_arguments: dict[str, MetaData | dict[str, str] | bool] = {
        "target_metadata": target_metadata,
        "dialect_opts": {"paramstyle": "named"},
        "compare_type": True,  # Detects type changes
    }
    if online:
        engine = get_engine_sync()
        with engine.connect() as connection:
            context.configure(**default_arguments, connection=connection)  # pyright: ignore[reportArgumentType]
            yield
    else:
        context.configure(**default_arguments, url=get_database_url())  # pyright: ignore[reportArgumentType]
        yield


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    with _configure_context(), context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    with _configure_context(online=True), context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
