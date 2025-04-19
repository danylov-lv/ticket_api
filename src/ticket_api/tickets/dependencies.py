from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_user_repository
from ..dependencies import get_async_session
from .repository import TicketRepository, TicketStatusRepository
from .service import TicketService


async def get_ticket_repository(session: AsyncSession = Depends(get_async_session)):
    yield TicketRepository(session)


async def get_ticket_status_repository(
    session: AsyncSession = Depends(get_async_session),
):
    yield TicketStatusRepository(session)


async def get_ticket_service(
    ticket_repository: TicketRepository = Depends(get_ticket_repository),
    ticket_status_repository: TicketStatusRepository = Depends(
        get_ticket_status_repository
    ),
    user_repository: SQLAlchemyUserDatabase = Depends(get_user_repository),
) -> TicketService:
    return TicketService(
        ticket_repository,
        ticket_status_repository,
        user_repository,
    )
