from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_async_session
from .models import User
from .service import UserService


async def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_service(
    user_repository: SQLAlchemyUserDatabase = Depends(get_user_repository),
) -> AsyncGenerator[UserService, None]:
    yield UserService(user_repository)
