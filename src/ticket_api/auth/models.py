from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from ..tickets.models import Ticket


class User(SQLAlchemyBaseUserTableUUID, Base):
    """ "User model for Authentication.

    Inherits from SQLAlchemyBaseUserTableUUID to provide UUID-based user management.

    Attributes:
        id (UUID): Unique identifier for the user.
        email (str): Email address of the user.
        hashed_password (str): Hashed password of the user.
        is_active (bool): Indicates if the user is active. (Created by default, unused)
        is_superuser (bool): Indicates if the user has superuser privileges.
        is_verified (bool): Indicates if the user's email is verified. (Created by default, unused)
        tickets (list[Ticket]): List of tickets associated with the user.
    """

    __tablename__ = "users"

    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="user",
        lazy="selectin",
    )
