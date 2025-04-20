from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from ticket_api.tickets.ai import AIService

from ..auth.dependencies import get_user_repository
from ..dependencies import get_async_session
from .repository import MessageRepository, TicketRepository, TicketStatusRepository
from .service import TicketService


async def get_ticket_repository(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[TicketService, None]:
    yield TicketRepository(session)


async def get_ticket_status_repository(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[TicketService, None]:
    yield TicketStatusRepository(session)


async def get_message_repository(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[TicketService, None]:
    yield MessageRepository(session)


async def get_ticket_service(
    ticket_repository: TicketRepository = Depends(get_ticket_repository),
    ticket_status_repository: TicketStatusRepository = Depends(
        get_ticket_status_repository
    ),
    message_repository: MessageRepository = Depends(get_message_repository),
    user_repository: SQLAlchemyUserDatabase = Depends(get_user_repository),
) -> AsyncGenerator[TicketService, None]:
    yield TicketService(
        ticket_repository=ticket_repository,
        ticket_status_repository=ticket_status_repository,
        message_repository=message_repository,
        user_repository=user_repository,
    )


async def get_ai_service() -> AsyncGenerator[AIService, None]:
    yield AIService()
