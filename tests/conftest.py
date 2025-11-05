import pytest_asyncio
from fastapi import Depends
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from auth.schemes import oauth2_scheme
from src.auth.service import get_current_user
from auth.utils import hash_password
from src.main import app as fastapi_app
from src.auth.dependencies import get_async_session
from src.database.models import Base, Users
from fastapi.security import OAuth2PasswordBearer

# Переопределяем oauth2_scheme, чтобы он не требовал реальный токен
fastapi_app.dependency_overrides[oauth2_scheme] = lambda: "mocked_token"


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture()
async def test_db_session() -> AsyncSession:
    async with TestSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(autouse=True)
async def override_get_async_session(test_db_session: AsyncSession):
    async def _override():
        yield test_db_session
    fastapi_app.dependency_overrides[get_async_session] = _override


@pytest_asyncio.fixture()
async def client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(autouse=True)
async def override_user(test_db_session: AsyncSession):
    user = Users(
        email="testuser@example.com",
        password=hash_password("arseniyilana611"),
        is_confirmed=True
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    # ВАЖНО: убираем Depends, чтобы FastAPI не вызывал oauth2_scheme
    async def mock_get_current_user():
        return {"user": user, "scopes": ["user:read"]}

    fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user