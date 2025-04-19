import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from ..auth.models import User


class TicketStatus(Base):
    __tablename__ = "ticket_statuses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="status",
        lazy="selectin",
    )


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False, default="")
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    status_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ticket_statuses.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(
        back_populates="tickets",
        lazy="selectin",
    )
    status: Mapped["TicketStatus"] = relationship(
        back_populates="tickets",
        lazy="selectin",
    )
