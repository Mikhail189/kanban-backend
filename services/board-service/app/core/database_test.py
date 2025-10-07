import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_TEST_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test_user:test_pass@kanban-db-test:5432/test_kanban",
)

print(f"✅ Using TEST DB: {DATABASE_TEST_URL}")

engine_test = create_async_engine(DATABASE_TEST_URL, echo=False)
async_session_test = async_sessionmaker(engine_test, expire_on_commit=False)