import os
from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


def get_database_url() -> str:
    database_url = os.getenv(key="DATABASE_URL", default="postgres:postgres@postgres:5432/zbids")
    sqlalchemy_url = f"postgresql+psycopg://{database_url}"
    return sqlalchemy_url


async def get_engine():
    return create_async_engine(url=get_database_url(), echo=True)


def get_engine_sync():
    return create_engine(url=get_database_url(), echo=True)


async def init_db():
    engine = await get_engine()
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession]:
    engine = await get_engine()
    async with AsyncSession(engine) as session:
        yield session
