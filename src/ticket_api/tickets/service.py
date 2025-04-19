import uuid
from .repository import TicketRepository, TicketStatusRepository
from .schemas import (
    TicketCreate,
    TicketRead,
    TicketStatusCreate,
    TicketStatusRead,
    TicketUpdate,
)
from fastapi import HTTPException, status
from fastapi_users.db import SQLAlchemyUserDatabase


class TicketService:
    def __init__(
        self,
        ticket_repository: TicketRepository,
        ticket_status_repository: TicketStatusRepository,
        user_repository: SQLAlchemyUserDatabase,
    ):
        self.ticket_repository = ticket_repository
        self.ticket_status_repository = ticket_status_repository
        self.user_repository = user_repository

    async def create_ticket(self, ticket_create: TicketCreate) -> TicketRead:
        if not await self.ticket_status_repository.exists(ticket_create.status_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket status not found",
            )

        db_ticket = await self.ticket_repository.create(ticket_create)
        return TicketRead.model_validate(db_ticket)

    async def get_ticket(self, ticket_id: uuid.UUID) -> TicketRead:
        db_ticket = await self.ticket_repository.get(ticket_id)
        if not db_ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )
        return TicketRead.model_validate(db_ticket)

    async def get_all_tickets(self) -> list[TicketRead]:
        db_tickets = await self.ticket_repository.get_all()
        return [TicketRead.model_validate(ticket) for ticket in db_tickets]

    async def get_all_tickets_by_user(self, user_id: uuid.UUID) -> list[TicketRead]:
        if not await self.user_repository.get(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        db_tickets = await self.ticket_repository.get_all_by_user(user_id)
        return [TicketRead.model_validate(ticket) for ticket in db_tickets]

    async def update_ticket(
        self, ticket_id: uuid.UUID, ticket_update: TicketUpdate
    ) -> TicketRead:
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
    ) -> bool:
        if not await self.user_repository.get(user_id):
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

        return db_ticket.user_id == user_id

    async def create_ticket_status(
        self,
        ticket_status_create: TicketStatusCreate,
    ) -> TicketStatusRead:
        db_ticket_status = await self.ticket_status_repository.create(
            ticket_status_create
        )
        return TicketStatusRead.model_validate(db_ticket_status)

    async def get_ticket_status(
        self,
        ticket_status_id: uuid.UUID,
    ) -> TicketStatusRead:
        db_ticket_status = await self.ticket_status_repository.get(ticket_status_id)
        if not db_ticket_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket status not found",
            )
        return TicketStatusRead.model_validate(db_ticket_status)

    async def get_all_ticket_statuses(self) -> list[TicketStatusRead]:
        db_ticket_statuses = await self.ticket_status_repository.get_all()
        return [
            TicketStatusRead.model_validate(ticket_status)
            for ticket_status in db_ticket_statuses
        ]
