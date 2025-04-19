from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from justin_test_api.auth.service import UserService

from ..dependencies import get_async_session
from .models import User


async def get_user_repository(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_service(
    user_repository: SQLAlchemyUserDatabase = Depends(get_user_repository),
):
    yield UserService(user_repository)
