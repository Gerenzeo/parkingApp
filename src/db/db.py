from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.config.config import settings

engine = create_async_engine(settings.sqlalchemy_postgresql_database_url, connect_args={"timeout": 30})
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# @asynccontextmanager
# async def get_db():
#     session = async_session()
#     try:
#         yield session
#     finally:
#         await session.close()