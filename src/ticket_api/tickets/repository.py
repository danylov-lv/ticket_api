import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete, exists
from .models import Ticket, TicketStatus
from .schemas import TicketCreate, TicketStatusCreate


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, ticket_create: TicketCreate) -> Ticket:
        ticket_data = ticket_create.model_dump(mode="json")
        stmt = insert(Ticket).values(**ticket_data).returning(Ticket.id)
        result = await self.session.execute(stmt)
        ticket_id = result.scalar_one()
        await self.session.commit()
        return await self.get(ticket_id)

    async def exists(self, ticket_id: uuid.UUID) -> bool:
        stmt = select(exists().where(Ticket.id == ticket_id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get(self, ticket_id: uuid.UUID) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Ticket]:
        stmt = select(Ticket)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, ticket_id: uuid.UUID, ticket_update: TicketCreate) -> Ticket:
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
        stmt = delete(Ticket).where(Ticket.id == ticket_id)
        await self.session.execute(stmt)
        await self.session.commit()


class TicketStatusRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, ticket_status_create: TicketStatusCreate) -> TicketStatus:
        ticket_status_data = ticket_status_create.model_dump(mode="json")
        stmt = (
            insert(TicketStatus).values(**ticket_status_data).returning(TicketStatus.id)
        )
        result = await self.session.execute(stmt)
        ticket_status_id = result.scalar_one()
        await self.session.commit()
        return await self.get(ticket_status_id)

    async def exists(self, ticket_status_id: uuid.UUID) -> bool:
        stmt = select(exists().where(TicketStatus.id == ticket_status_id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get(self, ticket_status_id: uuid.UUID) -> TicketStatus | None:
        stmt = select(TicketStatus).where(TicketStatus.id == ticket_status_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[TicketStatus]:
        stmt = select(TicketStatus)
        result = await self.session.execute(stmt)
        return result.scalars().all()
