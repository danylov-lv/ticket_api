import uuid

from fastapi_users import FastAPIUsers

from .backend import auth_backend
from .dependencies import get_user_service
from .models import User
from .schemas import UserCreate, UserRead, UserUpdate

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_service,
    [auth_backend],
)

auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(UserRead, UserCreate)
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)

get_current_active_user = fastapi_users.current_user(active=True)
get_current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
