import uuid
from typing import Optional

from fastapi import Request
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin

from ..config import settings
from .models import User
from .schemas import UserCreate


class UserService(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ) -> None:
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"User {user.id} has forgotten their password. Token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def validate_password(self, password: str, user: UserCreate | User) -> None:
        """Password validation method override.

        This method is called when a user registers or changes their password.
        It checks if the password meets the required criteria:
        - At least 8 characters long
        - Contains at least one digit
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one special character from the defined set
        """

        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password must be at least 8 characters long."
            )
        if not any(char.isdigit() for char in password):
            raise InvalidPasswordException(
                reason="Password must contain at least one digit."
            )
        if not any(char.isupper() for char in password):
            raise InvalidPasswordException(
                reason="Password must contain at least one uppercase letter."
            )
        if not any(char.islower() for char in password):
            raise InvalidPasswordException(
                reason="Password must contain at least one lowercase letter."
            )
        if not any(char in settings.PASSWORD_SPECIAL_CHARS for char in password):
            raise InvalidPasswordException(
                reason="Password must contain at least one special character."
            )
