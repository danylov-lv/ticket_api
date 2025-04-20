from fastapi import HTTPException, Request
import pytest
import pytest_asyncio
from fastapi_users.db import SQLAlchemyUserDatabase
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.postgres import PostgresContainer

from ticket_api.api import app
from ticket_api.auth.models import User
from ticket_api.auth.schemas import UserCreate, UserRead
from ticket_api.auth.service import UserService
from ticket_api.db.base import DatabaseSessionManager
from ticket_api.dependencies import get_async_session
from ticket_api.auth.router import get_current_active_user


@pytest.fixture(scope="session")
def test_db():
    with PostgresContainer("postgres:latest", driver="asyncpg") as postgres:
        wait_for_logs(postgres, "database system is ready to accept connections")
        yield postgres


@pytest_asyncio.fixture(scope="session", autouse=True)
async def sessionmanager(test_db: PostgresContainer):
    sessionmanager = DatabaseSessionManager(test_db.get_connection_url())
    yield sessionmanager
    await sessionmanager.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def create_tables(sessionmanager: DatabaseSessionManager):
    async with sessionmanager.connect() as connection:
        await sessionmanager.drop_all(connection)
        await sessionmanager.create_all(connection)
        await connection.commit()


@pytest_asyncio.fixture(scope="function")
async def async_session(sessionmanager: DatabaseSessionManager):
    async with sessionmanager.session() as async_session:
        yield async_session


@pytest_asyncio.fixture(scope="session")
async def async_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


@pytest.fixture
def user_repository(async_session: AsyncSession):
    return SQLAlchemyUserDatabase(async_session, User)


@pytest.fixture
def user_service(user_repository: SQLAlchemyUserDatabase):
    return UserService(user_repository)


@pytest_asyncio.fixture
async def user(user_service: UserService):
    user_create = UserCreate(
        email="test@example.com",
        password="qQ123456!",
    )
    user = await user_service.create(user_create)
    return user


@pytest_asyncio.fixture
async def superuser(user_service: UserService):
    superuser_create = UserCreate(
        email="superuser@example.com",
        password="qQ123456!",
        is_superuser=True,
    )
    superuser = await user_service.create(superuser_create)
    return superuser


@pytest.fixture
def authentication_token():
    return "Bearer authentication_token"


@pytest.fixture
def superuser_authentication_token():
    return "Bearer superuser_authentication_token"


@pytest_asyncio.fixture(scope="function", autouse=True)
async def dependency_overrides(
    sessionmanager: DatabaseSessionManager,
    user: UserRead,
    superuser: UserRead,
    authentication_token: str,
):
    async def get_async_session_override():
        async with sessionmanager.session() as async_session:
            yield async_session

    async def get_current_active_user_override(request: Request):
        token = request.headers.get("Authorization")
        if token == authentication_token:
            return user
        elif token == superuser_authentication_token:
            return superuser
        else:
            raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[get_async_session] = get_async_session_override
    app.dependency_overrides[get_current_active_user] = get_current_active_user_override
