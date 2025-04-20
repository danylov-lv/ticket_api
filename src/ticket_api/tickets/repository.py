import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete, exists
from .models import Ticket, TicketStatus, Message
from .schemas import MessageCreate, TicketCreate, TicketStatusCreate, TicketUpdate
from ..db.repository import BaseRepository


class TicketRepository(BaseRepository):
    """Repository for managing tickets in the database.

    This class provides methods to create, read, update, and delete tickets,
    as well as to check if a ticket exists and to retrieve all tickets or tickets by user.

    It uses SQLAlchemy for database interactions and is designed to work with an asynchronous session.
    Instead of using a traditional ORM approach, it uses SQLAlchemy Core for more control over the SQL statements.

    This allows for more complex queries and better performance in some cases.

    The repository pattern is used to separate the data access logic from the business logic,
    making the code more modular and easier to maintain.

    The repository is initialized with an asynchronous session, which is used for all database operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, ticket_create: TicketCreate) -> Ticket:
        """Create a new ticket in the database.

        Args:
            ticket_create (TicketCreate): The data for the new ticket.

        Returns:
            Ticket: The created ticket object.

        """

        ticket_data = ticket_create.model_dump(mode="json")
        stmt = insert(Ticket).values(**ticket_data).returning(Ticket.id)
        result = await self.session.execute(stmt)
        ticket_id = result.scalar_one()
        await self.session.commit()
        return await self.get(ticket_id)

    async def exists(self, ticket_id: uuid.UUID) -> bool:
        """Check if a ticket exists in the database.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to check.

        Returns:
            bool: True if the ticket exists, False otherwise.

        """

        stmt = select(exists().where(Ticket.id == ticket_id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get(self, ticket_id: uuid.UUID) -> Ticket | None:
        """Get a ticket by its ID.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to retrieve.

        Returns:
            Ticket | None: The ticket object if found, None otherwise.

        """

        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Ticket]:
        """Get all tickets in the database.

        Returns:
            list[Ticket]: A list of all ticket objects.

        """

        stmt = select(Ticket)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[Ticket]:
        """Get all tickets for a specific user.

        Args:
            user_id (uuid.UUID): The ID of the user whose tickets to retrieve.

        Returns:
            list[Ticket]: A list of all ticket objects for the specified user.

        """

        stmt = select(Ticket).where(Ticket.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, ticket_id: uuid.UUID, ticket_update: TicketUpdate) -> Ticket:
        """Update a ticket by its ID.

        It supports partial updates, meaning that only the fields that are set in the `ticket_update` object will be updated.
        If a field is not set, it will not be included in the update statement.
        `exclude_unset=True` is used to exclude only unset fields from the update statement, so in case some value was set to None manually, it will not be skipped.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to update.
            ticket_update (TicketUpdate): The data to update the ticket with.

        Returns:
            Ticket: The updated ticket object.

        """

        ticket_data = ticket_update.model_dump(mode="json", exclude_unset=True)
        stmt = (
            update(Ticket)
            .where(Ticket.id == ticket_id)
            .values(**ticket_data)
            .returning(Ticket.id)
        )
        result = await self.session.execute(stmt)
        ticket_id = result.scalar_one()
        await self.session.commit()
        return await self.get(ticket_id)

    async def delete(self, ticket_id: uuid.UUID) -> None:
        """Delete a ticket by its ID.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to delete.

        """

        stmt = delete(Ticket).where(Ticket.id == ticket_id)
        await self.session.execute(stmt)
        await self.session.commit()


class TicketStatusRepository:
    """Repository for managing ticket statuses in the database."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, ticket_status_create: TicketStatusCreate) -> TicketStatus:
        """Create a new ticket status in the database.

        Args:
            ticket_status_create (TicketStatusCreate): The data for the new ticket status.

        Returns:
            TicketStatus: The created ticket status object.

        """

        ticket_status_data = ticket_status_create.model_dump(mode="json")
        stmt = (
            insert(TicketStatus).values(**ticket_status_data).returning(TicketStatus.id)
        )
        result = await self.session.execute(stmt)
        ticket_status_id = result.scalar_one()
        await self.session.commit()
        return await self.get(ticket_status_id)

    async def exists(self, ticket_status_id: uuid.UUID) -> bool:
        """Check if a ticket status exists in the database.

        Args:
            ticket_status_id (uuid.UUID): The ID of the ticket status to check.

        Returns:
            bool: True if the ticket status exists, False otherwise.

        """

        stmt = select(exists().where(TicketStatus.id == ticket_status_id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get(self, ticket_status_id: uuid.UUID) -> TicketStatus | None:
        """Get a ticket status by its ID.

        Args:
            ticket_status_id (uuid.UUID): The ID of the ticket status to retrieve.

        Returns:
            TicketStatus | None: The ticket status object if found, None otherwise.

        """

        stmt = select(TicketStatus).where(TicketStatus.id == ticket_status_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[TicketStatus]:
        """Get all ticket statuses in the database.

        Returns:
            list[TicketStatus]: A list of all ticket status objects.

        """

        stmt = select(TicketStatus)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete(self, ticket_status_id: uuid.UUID) -> None:
        """Delete a ticket status by its ID.

        Args:
            ticket_status_id (uuid.UUID): The ID of the ticket status to delete.

        """

        stmt = delete(TicketStatus).where(TicketStatus.id == ticket_status_id)
        await self.session.execute(stmt)
        await self.session.commit()


class MessageRepository:
    """Repository for managing messages in the database."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        ticket_id: uuid.UUID,
        message_create: MessageCreate,
    ) -> Message:
        """Create a new message in the database.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to which the message belongs.
            message_create (MessageCreate): The data for the new message.

        Returns:
            Message: The created message object.

        """

        message_data = message_create.model_dump(mode="json")
        message_data["ticket_id"] = ticket_id
        stmt = insert(Message).values(**message_data).returning(Message.id)
        result = await self.session.execute(stmt)
        message_id = result.scalar_one()
        await self.session.commit()
        return await self.get(message_id)

    async def exists(self, message_id: uuid.UUID) -> bool:
        """Check if a message exists in the database.

        Args:
            message_id (uuid.UUID): The ID of the message to check.

        Returns:
            bool: True if the message exists, False otherwise.

        """

        stmt = select(exists().where(Message.id == message_id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get(self, message_id: uuid.UUID) -> Message | None:
        """Get a message by its ID.

        Args:
            message_id (uuid.UUID): The ID of the message to retrieve.

        Returns:
            Message | None: The message object if found, None otherwise.

        """

        stmt = select(Message).where(Message.id == message_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_ticket(
        self,
        ticket_id: uuid.UUID,
    ) -> list[Message]:
        """Get all messages for a specific ticket.

        It retrieves all messages associated with the given ticket ID and orders them by creation date.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket whose messages to retrieve.

        Returns:
            list[Message]: A list of all message objects for the specified ticket.

        """

        stmt = (
            select(Message)
            .where(Message.ticket_id == ticket_id)
            .order_by(Message.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_last_customer_message(
        self,
        ticket_id: uuid.UUID,
    ) -> Message | None:
        """Get the last message from a customer for a specific ticket.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket whose last customer message to retrieve.

        Returns:
            Message | None: The last customer message object if found, None otherwise.

        """

        stmt = (
            select(Message)
            .where(Message.ticket_id == ticket_id, Message.is_ai.is_(False))
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
