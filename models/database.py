from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import declarative_base

engine=create_async_engine("sqlite+aiosqlite:///./etl.db",echo = True)
db_session=async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
Base=declarative_base()

async def get_db():
    async with db_session() as asyncdb:
        yield asyncdb
