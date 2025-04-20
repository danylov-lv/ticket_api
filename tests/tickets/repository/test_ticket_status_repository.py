import uuid

import pytest
from sqlalchemy.exc import IntegrityError, DBAPIError

from ticket_api.tickets.models import TicketStatus
from ticket_api.tickets.repository import TicketStatusRepository
from ticket_api.tickets.schemas import TicketStatusCreate, TicketStatusRead


@pytest.mark.asyncio(loop_scope="session")
class TestTicketStatusRepository:
    async def test_create(
        self,
        ticket_status_repository: TicketStatusRepository,
    ):
        ticket_status_create = TicketStatusCreate(
            name="Open",
        )
        ticket_status = await ticket_status_repository.create(ticket_status_create)
        assert isinstance(ticket_status, TicketStatus)
        assert ticket_status.id is not None
        assert ticket_status.name == ticket_status_create.name

    async def test_create_duplicate_ticket_status(
        self,
        ticket_status_repository: TicketStatusRepository,
        ticket_status: TicketStatusRead,
    ):
        ticket_status_create = TicketStatusCreate(
            name=ticket_status.name,
        )
        with pytest.raises(IntegrityError):
            await ticket_status_repository.create(ticket_status_create)

    async def test_exists(
        self,
        ticket_status_repository: TicketStatusRepository,
        ticket_status: TicketStatusRead,
    ):
        exists = await ticket_status_repository.exists(ticket_status.id)
        assert exists is True

    async def test_exists_not_found(
        self,
        ticket_status_repository: TicketStatusRepository,
    ):
        exists = await ticket_status_repository.exists(uuid.uuid4())
        assert exists is False

    async def test_exists_not_uuid(
        self,
        ticket_status_repository: TicketStatusRepository,
    ):
        with pytest.raises(DBAPIError):
            await ticket_status_repository.exists("not-a-uuid")

    async def test_get(
        self,
        ticket_status_repository: TicketStatusRepository,
        ticket_status: TicketStatusRead,
    ):
        ticket_status_from_db = await ticket_status_repository.get(ticket_status.id)
        assert isinstance(ticket_status_from_db, TicketStatus)
        assert ticket_status_from_db.id == ticket_status.id
        assert ticket_status_from_db.name == ticket_status.name

    async def test_get_not_found(
        self,
        ticket_status_repository: TicketStatusRepository,
    ):
        ticket_status_from_db = await ticket_status_repository.get(uuid.uuid4())
        assert ticket_status_from_db is None

    async def test_get_not_uuid(
        self,
        ticket_status_repository: TicketStatusRepository,
    ):
        with pytest.raises(DBAPIError):
            await ticket_status_repository.get("not-a-uuid")

    async def test_get_all(
        self,
        ticket_status_repository: TicketStatusRepository,
        ticket_status: TicketStatusRead,
    ):
        ticket_statuses = await ticket_status_repository.get_all()
        assert isinstance(ticket_statuses, list)
        assert len(ticket_statuses) > 0
        assert all(isinstance(ts, TicketStatus) for ts in ticket_statuses)
        assert any(ts.id == ticket_status.id for ts in ticket_statuses)
        assert any(ts.name == ticket_status.name for ts in ticket_statuses)

    async def test_get_all_empty(
        self,
        ticket_status_repository: TicketStatusRepository,
    ):
        ticket_statuses = await ticket_status_repository.get_all()
        assert isinstance(ticket_statuses, list)
        assert len(ticket_statuses) == 0

    async def test_delete(
        self,
        ticket_status_repository: TicketStatusRepository,
        ticket_status: TicketStatusRead,
    ):
        await ticket_status_repository.delete(ticket_status.id)
        ticket_status_from_db = await ticket_status_repository.get(ticket_status.id)
        assert ticket_status_from_db is None

    async def test_delete_not_found(
        self,
        ticket_status_repository: TicketStatusRepository,
    ):
        await ticket_status_repository.delete(uuid.uuid4())

    async def test_delete_not_uuid(
        self,
        ticket_status_repository: TicketStatusRepository,
    ):
        with pytest.raises(DBAPIError):
            await ticket_status_repository.delete("not-a-uuid")
