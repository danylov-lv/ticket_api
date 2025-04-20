import pytest
import pytest_asyncio
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from ticket_api.auth.schemas import UserRead
from ticket_api.tickets.repository import (
    MessageRepository,
    TicketRepository,
    TicketStatusRepository,
)
from ticket_api.tickets.schemas import (
    MessageCreate,
    TicketCreate,
    TicketRead,
    TicketStatusCreate,
    TicketStatusRead,
)
from ticket_api.tickets.service import TicketService


@pytest.fixture
def ticket_repository(async_session: AsyncSession) -> TicketRepository:
    return TicketRepository(async_session)


@pytest.fixture
def ticket_status_repository(async_session: AsyncSession) -> TicketStatusRepository:
    return TicketStatusRepository(async_session)


@pytest.fixture
def message_repository(async_session: AsyncSession) -> MessageRepository:
    return MessageRepository(async_session)


@pytest.fixture
def ticket_service(
    ticket_repository: TicketRepository,
    ticket_status_repository: TicketStatusRepository,
    message_repository: MessageRepository,
    user_repository: SQLAlchemyUserDatabase,
) -> TicketService:
    return TicketService(
        ticket_repository=ticket_repository,
        ticket_status_repository=ticket_status_repository,
        message_repository=message_repository,
        user_repository=user_repository,
    )


@pytest_asyncio.fixture
async def ticket_status(ticket_service: TicketService):
    ticket_status_create = TicketStatusCreate(
        name="Open",
    )
    ticket_status = await ticket_service.create_ticket_status(ticket_status_create)
    return ticket_status


@pytest_asyncio.fixture
async def ticket(
    ticket_service: TicketService,
    user: UserRead,
    ticket_status: TicketStatusRead,
):
    ticket_create = TicketCreate(
        title="Test Ticket",
        description="This is a test ticket.",
        user_id=user.id,
        status_id=ticket_status.id,
    )
    ticket = await ticket_service.create_ticket(ticket_create)
    return ticket


@pytest_asyncio.fixture
async def superuser_ticket(
    ticket_service: TicketService,
    superuser: UserRead,
    ticket_status: TicketStatusRead,
):
    ticket_create = TicketCreate(
        title="Test Ticket",
        description="This is a test ticket.",
        user_id=superuser.id,
        status_id=ticket_status.id,
    )
    ticket = await ticket_service.create_ticket(ticket_create)
    return ticket


@pytest_asyncio.fixture
async def message(
    ticket_service: TicketService,
    ticket: TicketRead,
):
    message_create = MessageCreate(
        content="This is a test message.",
    )
    message = await ticket_service.create_message(
        ticket.id,
        message_create,
    )
    return message


@pytest_asyncio.fixture
async def ai_message(
    ticket_service: TicketService,
    ticket: TicketRead,
):
    message_create = MessageCreate(
        content="This is a test AI message.",
        is_ai=True,
    )
    message = await ticket_service.create_message(
        ticket.id,
        message_create,
    )
    return message
