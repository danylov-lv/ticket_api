import uuid

from fastapi import HTTPException, status
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.exc import IntegrityError

from .repository import MessageRepository, TicketRepository, TicketStatusRepository
from .schemas import (
    MessageCreate,
    MessageRead,
    TicketCreate,
    TicketRead,
    TicketStatusCreate,
    TicketStatusRead,
    TicketUpdate,
)


class TicketService:
    """Service class for managing tickets, ticket statuses, and messages.

    This class provides methods to create, read, update, and delete tickets, ticket statuses, and messages.
    To separate different tables, we have different repositories for each table.
    It also provides methods to check if a ticket is accessible by a user and to create messages associated with tickets.
    The service uses FastAPI's HTTPException to handle errors and return appropriate HTTP status codes.


    Attributes:
        ticket_repository (TicketRepository): Repository for managing tickets.
        ticket_status_repository (TicketStatusRepository): Repository for managing ticket statuses.
        message_repository (MessageRepository): Repository for managing messages.
        user_repository (SQLAlchemyUserDatabase): Additional repository to validate if the user exists and has the right permissions.
    """

    def __init__(
        self,
        ticket_repository: TicketRepository,
        ticket_status_repository: TicketStatusRepository,
        message_repository: MessageRepository,
        user_repository: SQLAlchemyUserDatabase,
    ):
        self.ticket_repository = ticket_repository
        self.ticket_status_repository = ticket_status_repository
        self.message_repository = message_repository
        self.user_repository = user_repository

    async def create_ticket(self, ticket_create: TicketCreate) -> TicketRead:
        """Create a new ticket.

        Args:
            ticket_create (TicketCreate): The ticket data to create.

        Returns:
            TicketRead: The created ticket data.

        """
        if not await self.ticket_status_repository.exists(ticket_create.status_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket status not found",
            )

        db_ticket = await self.ticket_repository.create(ticket_create)
        return TicketRead.model_validate(db_ticket)

    async def get_ticket(self, ticket_id: uuid.UUID) -> TicketRead:
        """Get a ticket by ID.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to retrieve.

        Returns:
            TicketRead: The ticket data.

        Raises:
            HTTPException[status_code=404]: If the ticket is not found.
        """

        db_ticket = await self.ticket_repository.get(ticket_id)
        if not db_ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )
        return TicketRead.model_validate(db_ticket)

    async def get_all_tickets(self) -> list[TicketRead]:
        """Get all tickets.

        Returns:
            list[TicketRead]: A list of all tickets.

        """

        db_tickets = await self.ticket_repository.get_all()
        return [TicketRead.model_validate(ticket) for ticket in db_tickets]

    async def get_all_tickets_by_user(self, user_id: uuid.UUID) -> list[TicketRead]:
        """Get all tickets for a specific user.

        Args:
            user_id (uuid.UUID): The ID of the user whose tickets to retrieve.

        Returns:
            list[TicketRead]: A list of tickets for the specified user.

        Raises:
            HTTPException[status_code=404]: If the user is not found.

        """

        if not await self.user_repository.get(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        db_tickets = await self.ticket_repository.get_all_by_user(user_id)
        return [TicketRead.model_validate(ticket) for ticket in db_tickets]

    async def update_ticket(
        self,
        ticket_id: uuid.UUID,
        ticket_update: TicketUpdate,
    ) -> TicketRead:
        """Update a ticket.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to update.
            ticket_update (TicketUpdate): The updated ticket data.

        Returns:
            TicketRead: The updated ticket data.

        Raises:
            HTTPException[status_code=404]: If the ticket is not found.
            HTTPException[status_code=404]: If the ticket status is not found.

        """

        if not await self.ticket_repository.exists(ticket_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        if ticket_update.status_id and not await self.ticket_status_repository.exists(
            ticket_update.status_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket status not found",
            )

        db_ticket = await self.ticket_repository.update(ticket_id, ticket_update)
        return TicketRead.model_validate(db_ticket)

    async def delete_ticket(self, ticket_id: uuid.UUID) -> None:
        """Delete a ticket.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to delete.

        Raises:
            HTTPException[status_code=404]: If the ticket is not found.

        """

        if not await self.ticket_repository.exists(ticket_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        await self.ticket_repository.delete(ticket_id)

    async def is_ticket_accessible(
        self,
        ticket_id: uuid.UUID,
        user_id: uuid.UUID,
    ):
        """Check if a ticket is accessible by a user.

        It checks if both the ticket and user exist, and if the user is either the owner of the ticket or a superuser.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to check.
            user_id (uuid.UUID): The ID of the user to check.

        Raises:
            HTTPException[status_code=404]: If the ticket or user is not found.
            HTTPException[status_code=403]: If the user does not have permission to access the ticket.

        """

        user = await self.user_repository.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        db_ticket = await self.ticket_repository.get(ticket_id)
        if not db_ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        if not db_ticket.user_id == user_id and not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this ticket.",
            )

    async def create_ticket_status(
        self,
        ticket_status_create: TicketStatusCreate,
    ) -> TicketStatusRead:
        """Create a new ticket status.

        Args:
            ticket_status_create (TicketStatusCreate): The ticket status data to create.

        Returns:
            TicketStatusRead: The created ticket status data.

        Raises:
            HTTPException[status_code=409]: If a ticket status with the same name already exists.
        """
        try:
            db_ticket_status = await self.ticket_status_repository.create(
                ticket_status_create
            )
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticket status with this name already exists",
            )

        return TicketStatusRead.model_validate(db_ticket_status)

    async def get_ticket_status(
        self,
        ticket_status_id: uuid.UUID,
    ) -> TicketStatusRead:
        """Get a ticket status by ID.

        Args:
            ticket_status_id (uuid.UUID): The ID of the ticket status to retrieve.

        Returns:
            TicketStatusRead: The ticket status data.

        """

        db_ticket_status = await self.ticket_status_repository.get(ticket_status_id)
        if not db_ticket_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket status not found",
            )
        return TicketStatusRead.model_validate(db_ticket_status)

    async def get_all_ticket_statuses(self) -> list[TicketStatusRead]:
        """Get all ticket statuses.

        Returns:
            list[TicketStatusRead]: A list of all ticket statuses.

        """
        db_ticket_statuses = await self.ticket_status_repository.get_all()
        return [
            TicketStatusRead.model_validate(ticket_status)
            for ticket_status in db_ticket_statuses
        ]

    async def delete_ticket_status(
        self,
        ticket_status_id: uuid.UUID,
    ) -> None:
        """Delete a ticket status.

        Args:
            ticket_status_id (uuid.UUID): The ID of the ticket status to delete.

        Raises:
            HTTPException[status_code=404]: If the ticket status is not found.

        """
        if not await self.ticket_status_repository.exists(ticket_status_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket status not found",
            )

        await self.ticket_status_repository.delete(ticket_status_id)

    async def create_message(
        self,
        ticket_id: uuid.UUID,
        message_create: MessageCreate,
    ) -> MessageRead:
        """Create a new message for a ticket.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to which the message belongs.
            message_create (MessageCreate): The message data to create.

        Returns:
            MessageRead: The created message data.

        """

        db_ticket = await self.ticket_repository.get(ticket_id)
        if not db_ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        db_message = await self.message_repository.create(
            ticket_id,
            message_create,
        )
        return MessageRead.model_validate(db_message)

    async def get_ticket_messages(
        self,
        ticket_id: uuid.UUID,
    ) -> list[MessageRead]:
        """Get all messages for a ticket.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to retrieve messages for.

        Returns:
            list[MessageRead]: A list of messages for the specified ticket.

        Raises:
            HTTPException[status_code=404]: If the ticket is not found.
        """

        db_ticket = await self.ticket_repository.get(ticket_id)
        if not db_ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        db_messages = await self.message_repository.get_all_by_ticket(ticket_id)
        return [MessageRead.model_validate(message) for message in db_messages]

    async def get_last_customer_message(
        self,
        ticket_id: uuid.UUID,
    ) -> MessageRead | None:
        """Get the last customer message for a ticket.

        Args:
            ticket_id (uuid.UUID): The ID of the ticket to retrieve the last customer message for.

        Returns:
            MessageRead | None: The last customer message for the specified ticket, or None if not found.

        """

        db_ticket = await self.ticket_repository.get(ticket_id)
        if not db_ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        db_message = await self.message_repository.get_last_customer_message(ticket_id)
        return MessageRead.model_validate(db_message) if db_message else None
