from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy import create_engine
from alembic import context

from src.database.models import Base, GeoBase

# Конфигурация Alembic
config = context.config
fileConfig(config.config_file_name)

# Важно: используем синхронную строку подключения
config.set_main_option(
    "sqlalchemy.url",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/cupidon_db"
)

target_metadata = [Base.metadata, GeoBase.metadata]


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
