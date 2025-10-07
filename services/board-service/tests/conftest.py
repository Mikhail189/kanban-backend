import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from app.main import app
from app.core import database
from app.core.database_test import engine_test, async_session_test


# Подмена движка и зависимостей FastAPI
database.engine = engine_test
database.async_session = async_session_test

async def override_get_db():
    async with async_session_test() as session:
        yield session

app.dependency_overrides[database.get_db] = override_get_db


#Клиент FastAPI
@pytest_asyncio.fixture(scope="session")
async def client():
    """HTTP-клиент для тестов (общий для всех тестов)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


#Сессия БД (создаётся для каждого теста)
@pytest_asyncio.fixture
async def db():
    async with async_session_test() as session:
        yield session


# Очистка таблиц перед каждым тестом
@pytest_asyncio.fixture(autouse=True)
async def clear_db(db):
    await db.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE;"))
    await db.commit()
