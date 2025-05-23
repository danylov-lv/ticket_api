import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from ..auth.models import User


class TicketStatus(Base):
    """TicketStatus model for managing ticket statuses.

    Its used to define the various statuses a ticket can have in the system.
    It was designed as a separate model instead of an Enum to allow for dynamic updates and changes.
    Also, used migration system does not support Enum updates well.
    This allows for easy addition, removal, or modification of ticket statuses without requiring database migrations.

    Attributes:
        id (UUID): Unique identifier for the ticket status.
        name (str): Name of the ticket status.
        tickets (list[Ticket]): List of tickets associated with this status.

    """

    __tablename__ = "ticket_statuses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="status",
        lazy="selectin",
    )


class Ticket(Base):
    """Ticket model for managing support tickets.

    This model represents a support ticket in the system, including its title, description, status, and associated messages.

    Attributes:
        id (UUID): Unique identifier for the ticket.
        title (str): Title of the ticket.
        description (str): Description of the ticket.
        user_id (UUID): ID of the user who created the ticket.
        status_id (UUID): ID of the current status of the ticket.
        created_at (datetime): Timestamp when the ticket was created.
        user (User): The user who created the ticket.
        status (TicketStatus): The current status of the ticket.
        messages (list[Message]): List of messages associated with the ticket.

    """

    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False, default="")
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    status_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ticket_statuses.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
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
    messages: Mapped[list["Message"]] = relationship(
        back_populates="ticket",
        lazy="selectin",
    )


class Message(Base):
    """Message model for managing messages associated with tickets.

    This model represents a message exchanged in a support ticket, including its content, whether it's from an AI, and the timestamp of creation.

    Attributes:
        id (UUID): Unique identifier for the message.
        ticket_id (UUID): ID of the ticket associated with this message.
        content (str): Content of the message.
        is_ai (bool): Indicates if the message is generated by AI.
        created_at (datetime): Timestamp when the message was created.
        ticket (Ticket): The ticket associated with this message.

    """

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE")
    )
    content: Mapped[str] = mapped_column(nullable=False)
    is_ai: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    ticket: Mapped["Ticket"] = relationship(
        back_populates="messages",
        lazy="selectin",
    )
