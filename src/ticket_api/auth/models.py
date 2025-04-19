from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from ..tickets.models import Ticket


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
