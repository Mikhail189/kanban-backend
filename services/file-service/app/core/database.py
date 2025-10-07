from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://fileuser:filepass@file-db:5432/filedb"
)

# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql+asyncpg://fileuser:filepass@localhost:5433/filedb"
# )

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()