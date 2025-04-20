import uuid

from pydantic import ValidationError
import pytest

from ticket_api.auth.schemas import UserRead
from ticket_api.tickets.models import Ticket
from ticket_api.tickets.repository import TicketRepository
from ticket_api.tickets.schemas import (
    TicketCreate,
    TicketRead,
    TicketStatusRead,
    TicketUpdate,
)

from sqlalchemy.exc import IntegrityError, DBAPIError, NoResultFound


@pytest.mark.asyncio(loop_scope="session")
class TestTicketRepository:
    async def test_create(
        self,
        ticket_repository: TicketRepository,
        user: UserRead,
        ticket_status: TicketStatusRead,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="This is a test ticket.",
            user_id=user.id,
            status_id=ticket_status.id,
        )
        ticket = await ticket_repository.create(ticket_create)
        assert isinstance(ticket, Ticket)
        assert ticket.id is not None
        assert ticket.title == ticket_create.title
        assert ticket.description == ticket_create.description
        assert ticket.user_id == ticket_create.user_id
        assert ticket.status_id == ticket_create.status_id
        assert ticket.created_at is not None

    async def test_create_with_invalid_user(
        self,
        ticket_repository: TicketRepository,
        ticket_status: TicketStatusRead,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="This is a test ticket.",
            user_id=uuid.uuid4(),  # Invalid user ID
            status_id=ticket_status.id,
        )

        with pytest.raises(IntegrityError):
            await ticket_repository.create(ticket_create)

    async def test_create_with_invalid_status(
        self,
        ticket_repository: TicketRepository,
        user: UserRead,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="This is a test ticket.",
            user_id=user.id,
            status_id=uuid.uuid4(),  # Invalid status ID
        )

        with pytest.raises(IntegrityError):
            await ticket_repository.create(ticket_create)

    async def test_create_with_user_not_uuid(
        self,
        ticket_repository: TicketRepository,
        ticket_status: TicketStatusRead,
    ):
        with pytest.raises(ValidationError):
            ticket_create = TicketCreate(
                title="Test Ticket",
                description="This is a test ticket.",
                user_id="not-a-uuid",  # Invalid user ID
                status_id=ticket_status.id,
            )

            await ticket_repository.create(ticket_create)

    async def test_exists(
        self,
        ticket_repository: TicketRepository,
        ticket: TicketRead,
    ):
        exists = await ticket_repository.exists(ticket.id)
        assert exists is True

    async def test_exists_not_found(
        self,
        ticket_repository: TicketRepository,
    ):
        exists = await ticket_repository.exists(uuid.uuid4())
        assert exists is False

    async def test_exists_not_uuid(
        self,
        ticket_repository: TicketRepository,
    ):
        with pytest.raises(DBAPIError):
            await ticket_repository.exists("not-a-uuid")

    async def test_get(
        self,
        ticket_repository: TicketRepository,
        ticket: TicketRead,
    ):
        ticket_from_db = await ticket_repository.get(ticket.id)
        assert ticket_from_db is not None
        assert ticket_from_db.id == ticket.id
        assert ticket_from_db.title == ticket.title
        assert ticket_from_db.description == ticket.description
        assert ticket_from_db.user_id == ticket.user_id
        assert ticket_from_db.status_id == ticket.status_id
        assert ticket_from_db.created_at == ticket.created_at

    async def test_get_not_found(
        self,
        ticket_repository: TicketRepository,
    ):
        ticket_from_db = await ticket_repository.get(uuid.uuid4())
        assert ticket_from_db is None

    async def test_get_not_uuid(
        self,
        ticket_repository: TicketRepository,
    ):
        with pytest.raises(DBAPIError):
            await ticket_repository.get("not-a-uuid")

    async def test_get_all(
        self,
        ticket_repository: TicketRepository,
        ticket: TicketRead,
    ):
        tickets = await ticket_repository.get_all()
        assert isinstance(tickets, list)
        assert len(tickets) > 0
        assert all(isinstance(t, Ticket) for t in tickets)
        assert any(t.id == ticket.id for t in tickets)
        assert any(t.title == ticket.title for t in tickets)
        assert any(t.description == ticket.description for t in tickets)
        assert any(t.user_id == ticket.user_id for t in tickets)
        assert any(t.status_id == ticket.status_id for t in tickets)
        assert any(t.created_at == ticket.created_at for t in tickets)

    async def test_get_all_empty(
        self,
        ticket_repository: TicketRepository,
    ):
        tickets = await ticket_repository.get_all()
        assert isinstance(tickets, list)
        assert len(tickets) == 0

    async def test_get_all_by_user(
        self,
        ticket_repository: TicketRepository,
        ticket: TicketRead,
        user: UserRead,
    ):
        tickets = await ticket_repository.get_all_by_user(user.id)
        assert isinstance(tickets, list)
        assert len(tickets) > 0
        assert all(isinstance(t, Ticket) for t in tickets)
        assert any(t.id == ticket.id for t in tickets)
        assert any(t.title == ticket.title for t in tickets)
        assert any(t.description == ticket.description for t in tickets)
        assert any(t.user_id == ticket.user_id for t in tickets)
        assert any(t.status_id == ticket.status_id for t in tickets)
        assert any(t.created_at == ticket.created_at for t in tickets)

    async def test_get_all_by_user_empty(
        self,
        ticket_repository: TicketRepository,
        user: UserRead,
    ):
        tickets = await ticket_repository.get_all_by_user(user.id)
        assert isinstance(tickets, list)
        assert len(tickets) == 0

    async def test_get_all_by_user_not_found(
        self,
        ticket_repository: TicketRepository,
    ):
        tickets = await ticket_repository.get_all_by_user(uuid.uuid4())
        assert isinstance(tickets, list)
        assert len(tickets) == 0

    async def test_get_all_by_user_not_uuid(
        self,
        ticket_repository: TicketRepository,
    ):
        with pytest.raises(DBAPIError):
            await ticket_repository.get_all_by_user("not-a-uuid")

    async def test_update(
        self,
        ticket_repository: TicketRepository,
        ticket: TicketRead,
    ):
        ticket_update = TicketUpdate(
            title="Updated Title",
            description="Updated description.",
        )

        updated_ticket = await ticket_repository.update(ticket.id, ticket_update)
        assert updated_ticket is not None
        assert isinstance(updated_ticket, Ticket)
        assert updated_ticket.id == ticket.id
        assert updated_ticket.title == "Updated Title"
        assert updated_ticket.description == "Updated description."
        assert updated_ticket.user_id == ticket.user_id

    async def test_update_only_one_field(
        self,
        ticket_repository: TicketRepository,
        ticket: TicketRead,
    ):
        ticket_update = TicketUpdate(
            title="Updated Title",
        )

        updated_ticket = await ticket_repository.update(ticket.id, ticket_update)
        assert updated_ticket is not None
        assert isinstance(updated_ticket, Ticket)
        assert updated_ticket.id == ticket.id
        assert updated_ticket.title == "Updated Title"
        assert updated_ticket.description == ticket.description
        assert updated_ticket.user_id == ticket.user_id
        assert updated_ticket.status_id == ticket.status_id

    async def test_update_not_found(
        self,
        ticket_repository: TicketRepository,
    ):
        ticket_update = TicketUpdate(
            title="Updated Title",
            description="Updated description.",
        )

        with pytest.raises(NoResultFound):
            await ticket_repository.update(uuid.uuid4(), ticket_update)

    async def test_update_not_uuid(
        self,
        ticket_repository: TicketRepository,
    ):
        ticket_update = TicketUpdate(
            title="Updated Title",
            description="Updated description.",
        )

        with pytest.raises(DBAPIError):
            await ticket_repository.update("not-a-uuid", ticket_update)

    async def test_delete(
        self,
        ticket_repository: TicketRepository,
        ticket: TicketRead,
    ):
        await ticket_repository.delete(ticket.id)
        ticket_from_db = await ticket_repository.get(ticket.id)
        assert ticket_from_db is None

    async def test_delete_not_found(
        self,
        ticket_repository: TicketRepository,
    ):
        await ticket_repository.delete(uuid.uuid4())

    async def test_delete_not_uuid(
        self,
        ticket_repository: TicketRepository,
    ):
        with pytest.raises(DBAPIError):
            await ticket_repository.delete("not-a-uuid")
