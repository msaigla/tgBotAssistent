from typing import Union

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine as _create_async_engine
from sqlalchemy.orm import sessionmaker


def create_async_engine(url: Union[URL, str]) -> AsyncEngine:
    return _create_async_engine(url=url, echo=False, pool_use_lifo=True)


@DeprecationWarning
async def proceed_schemas(engine: AsyncEngine, metadata) -> None:
    # async with engine.begin() as conn:
    #     await conn.run_sync(metadata.create_all)
    ...


def get_session_maker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(bind=engine, class_=AsyncSession)
