import uuid
import pytest

from ticket_api.auth.schemas import UserRead
from ticket_api.tickets.schemas import (
    MessageCreate,
    MessageRead,
    TicketCreate,
    TicketRead,
    TicketStatusCreate,
    TicketStatusRead,
    TicketUpdate,
)
from ticket_api.tickets.service import TicketService
from fastapi import HTTPException, status


@pytest.mark.asyncio(loop_scope="session")
class TestTicketService:
    async def test_create_ticket_status(
        self,
        ticket_service: TicketService,
    ):
        ticket_status_create = TicketStatusCreate(
            name="Open",
        )
        ticket_status = await ticket_service.create_ticket_status(ticket_status_create)
        assert ticket_status is not None
        assert isinstance(ticket_status, TicketStatusRead)
        assert ticket_status.id is not None
        assert ticket_status.name == ticket_status_create.name

    async def test_create_duplicate_ticket_status(
        self,
        ticket_service: TicketService,
        ticket_status: TicketStatusRead,
    ):
        ticket_status_create = TicketStatusCreate(
            name=ticket_status.name,
        )
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.create_ticket_status(ticket_status_create)

        assert excinfo.value.status_code == status.HTTP_409_CONFLICT

    async def test_get_ticket_status(
        self,
        ticket_service: TicketService,
        ticket_status: TicketStatusRead,
    ):
        ticket_status_read = await ticket_service.get_ticket_status(ticket_status.id)
        assert ticket_status_read is not None
        assert isinstance(ticket_status_read, TicketStatusRead)
        assert ticket_status_read.id == ticket_status.id
        assert ticket_status_read.name == ticket_status.name

    async def test_get_ticket_status_not_found(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_ticket_status(uuid.uuid4())

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_ticket_status_not_uuid(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_ticket_status("not-a-uuid")

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_all_ticket_statuses(
        self,
        ticket_service: TicketService,
        ticket_status: TicketStatusRead,
    ):
        ticket_statuses = await ticket_service.get_all_ticket_statuses()
        assert ticket_statuses is not None
        assert isinstance(ticket_statuses, list)
        assert len(ticket_statuses) > 0
        assert all(isinstance(ts, TicketStatusRead) for ts in ticket_statuses)
        assert any(ts.id == ticket_status.id for ts in ticket_statuses)
        assert any(ts.name == ticket_status.name for ts in ticket_statuses)

    async def test_get_all_ticket_statuses_empty(
        self,
        ticket_service: TicketService,
    ):
        ticket_statuses = await ticket_service.get_all_ticket_statuses()
        assert ticket_statuses is not None
        assert isinstance(ticket_statuses, list)
        assert len(ticket_statuses) == 0

    async def test_delete_ticket_status(
        self,
        ticket_service: TicketService,
        ticket_status: TicketStatusRead,
    ):
        await ticket_service.delete_ticket_status(ticket_status.id)
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_ticket_status(ticket_status.id)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_ticket_status_not_found(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.delete_ticket_status(uuid.uuid4())

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_ticket_status_not_uuid(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.delete_ticket_status("not-a-uuid")

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_ticket(
        self,
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
        assert ticket is not None
        assert isinstance(ticket, TicketRead)
        assert ticket.id is not None
        assert ticket.title == ticket_create.title
        assert ticket.description == ticket_create.description
        assert ticket.user_id == user.id
        assert ticket.status_id == ticket_status.id
        assert ticket.created_at is not None

    async def test_create_ticket_invalid_user(
        self,
        ticket_service: TicketService,
        ticket_status: TicketStatusRead,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="This is a test ticket.",
            user_id=uuid.uuid4(),  # Invalid user ID
            status_id=ticket_status.id,
        )
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.create_ticket(ticket_create)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "User not found"

    async def test_create_ticket_invalid_status(
        self,
        ticket_service: TicketService,
        user: UserRead,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="This is a test ticket.",
            user_id=user.id,
            status_id=uuid.uuid4(),  # Invalid status ID
        )
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.create_ticket(ticket_create)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Ticket status not found"

    async def test_get_ticket(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
    ):
        ticket_read = await ticket_service.get_ticket(ticket.id)
        assert ticket_read is not None
        assert isinstance(ticket_read, TicketRead)
        assert ticket_read.id == ticket.id
        assert ticket_read.title == ticket.title
        assert ticket_read.description == ticket.description
        assert ticket_read.user_id == ticket.user_id
        assert ticket_read.status_id == ticket.status_id
        assert ticket_read.created_at == ticket.created_at

    async def test_get_ticket_not_found(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_ticket(uuid.uuid4())

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Ticket not found"

    async def test_get_ticket_not_uuid(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_ticket("not-a-uuid")

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_all_tickets(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
    ):
        tickets = await ticket_service.get_all_tickets()
        assert tickets is not None
        assert isinstance(tickets, list)
        assert len(tickets) > 0
        assert all(isinstance(t, TicketRead) for t in tickets)
        assert any(t.id == ticket.id for t in tickets)
        assert any(t.title == ticket.title for t in tickets)
        assert any(t.description == ticket.description for t in tickets)

    async def test_get_all_tickets_empty(
        self,
        ticket_service: TicketService,
    ):
        tickets = await ticket_service.get_all_tickets()
        assert tickets is not None
        assert isinstance(tickets, list)
        assert len(tickets) == 0

    async def test_get_all_tickets_by_user(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
        user: UserRead,
    ):
        tickets = await ticket_service.get_all_tickets_by_user(user.id)
        assert tickets is not None
        assert isinstance(tickets, list)
        assert len(tickets) > 0
        assert all(isinstance(t, TicketRead) for t in tickets)
        assert any(t.id == ticket.id for t in tickets)
        assert any(t.title == ticket.title for t in tickets)
        assert any(t.description == ticket.description for t in tickets)
        assert all(t.user_id == user.id for t in tickets)

    async def test_get_all_tickets_by_user_not_found(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_all_tickets_by_user(uuid.uuid4())

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "User not found"

    async def test_get_all_tickets_by_user_not_uuid(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_all_tickets_by_user("not-a-uuid")

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_update_ticket(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
    ):
        ticket_update = TicketUpdate(
            title="Updated Test Ticket",
            description="This is an updated test ticket.",
        )

        updated_ticket = await ticket_service.update_ticket(ticket.id, ticket_update)
        assert updated_ticket is not None
        assert isinstance(updated_ticket, TicketRead)
        assert updated_ticket.id == ticket.id
        assert updated_ticket.title == ticket_update.title
        assert updated_ticket.description == ticket_update.description
        assert updated_ticket.user_id == ticket.user_id
        assert updated_ticket.status_id == ticket.status_id

    async def test_update_ticket_only_title(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
    ):
        ticket_update = TicketUpdate(
            title="Updated Test Ticket",
        )

        updated_ticket = await ticket_service.update_ticket(ticket.id, ticket_update)
        assert updated_ticket is not None
        assert isinstance(updated_ticket, TicketRead)
        assert updated_ticket.id == ticket.id
        assert updated_ticket.title == ticket_update.title
        assert updated_ticket.description == ticket.description
        assert updated_ticket.user_id == ticket.user_id
        assert updated_ticket.status_id == ticket.status_id

    async def test_update_ticket_not_found(
        self,
        ticket_service: TicketService,
    ):
        ticket_update = TicketUpdate(
            title="Updated Test Ticket",
            description="This is an updated test ticket.",
        )
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.update_ticket(uuid.uuid4(), ticket_update)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Ticket not found"

    async def test_update_ticket_not_uuid(
        self,
        ticket_service: TicketService,
    ):
        ticket_update = TicketUpdate(
            title="Updated Test Ticket",
            description="This is an updated test ticket.",
        )
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.update_ticket("not-a-uuid", ticket_update)

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_delete_ticket(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
    ):
        await ticket_service.delete_ticket(ticket.id)
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_ticket(ticket.id)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Ticket not found"

    async def test_delete_ticket_not_found(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.delete_ticket(uuid.uuid4())

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Ticket not found"

    async def test_delete_ticket_not_uuid(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.delete_ticket("not-a-uuid")

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_is_ticket_accessible(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
        user: UserRead,
    ):
        assert ticket.user_id == user.id
        assert user.is_superuser is False

        is_accessible = await ticket_service.is_ticket_accessible(
            ticket.id,
            user.id,
        )
        assert is_accessible is True

    async def test_is_ticket_accessible_not_owner(
        self,
        ticket_service: TicketService,
        superuser_ticket: TicketRead,
        user: UserRead,
    ):
        assert superuser_ticket.user_id != user.id
        assert user.is_superuser is False

        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.is_ticket_accessible(
                superuser_ticket.id,
                user.id,
            )

        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

    async def test_is_ticket_accessible_superuser(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
        superuser: UserRead,
    ):
        assert ticket.user_id != superuser.id
        assert superuser.is_superuser is True

        is_accessible = await ticket_service.is_ticket_accessible(
            ticket.id,
            superuser.id,
        )
        assert is_accessible is True

    async def test_is_ticket_accessible_ticket_not_found(
        self,
        ticket_service: TicketService,
        user: UserRead,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.is_ticket_accessible(uuid.uuid4(), user.id)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Ticket not found"

    async def test_is_ticket_accessible_user_not_found(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.is_ticket_accessible(ticket.id, uuid.uuid4())

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "User not found"

    async def test_is_ticket_accessible_ticket_not_uuid(
        self,
        ticket_service: TicketService,
        user: UserRead,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.is_ticket_accessible("not-a-uuid", user.id)

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_is_ticket_accessible_user_not_uuid(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.is_ticket_accessible(ticket.id, "not-a-uuid")

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_message(
        self,
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
        assert message is not None
        assert isinstance(message, MessageRead)
        assert message.id is not None
        assert message.content == message_create.content
        assert message.ticket_id == ticket.id
        assert message.created_at is not None
        assert message.is_ai is False

    async def test_create_message_ticket_not_found(
        self,
        ticket_service: TicketService,
    ):
        message_create = MessageCreate(
            content="This is a test message.",
        )
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.create_message(uuid.uuid4(), message_create)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Ticket not found"

    async def test_create_message_ticket_not_uuid(
        self,
        ticket_service: TicketService,
    ):
        message_create = MessageCreate(
            content="This is a test message.",
        )
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.create_message("not-a-uuid", message_create)

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_ticket_messages(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
        message: MessageRead,
    ):
        messages = await ticket_service.get_ticket_messages(ticket.id)
        assert messages is not None
        assert isinstance(messages, list)
        assert len(messages) > 0
        assert all(isinstance(m, MessageRead) for m in messages)
        assert any(m.ticket_id == ticket.id for m in messages)
        assert any(m.id == message.id for m in messages)
        assert any(m.content == message.content for m in messages)
        assert any(m.is_ai is message.is_ai for m in messages)

        # Validate order of messages

        assert messages == sorted(
            messages,
            key=lambda m: m.created_at,
        )

    async def test_get_ticket_messages_empty(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
    ):
        messages = await ticket_service.get_ticket_messages(ticket.id)
        assert messages is not None
        assert isinstance(messages, list)
        assert len(messages) == 0

    async def test_get_ticket_messages_ticket_not_found(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_ticket_messages(uuid.uuid4())

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Ticket not found"

    async def test_get_ticket_messages_ticket_not_uuid(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_ticket_messages("not-a-uuid")

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_last_customer_message(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
        message: MessageRead,
    ):
        last_message = await ticket_service.get_last_customer_message(ticket.id)
        assert last_message is not None
        assert isinstance(last_message, MessageRead)
        assert last_message.id == message.id
        assert last_message.content == message.content
        assert last_message.ticket_id == ticket.id
        assert last_message.is_ai is False

    async def test_get_last_customer_message_no_messages(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
    ):
        last_message = await ticket_service.get_last_customer_message(ticket.id)
        assert last_message is None

    async def test_get_last_customer_message_no_customer_messages(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
        ai_message: MessageRead,
    ):
        last_message = await ticket_service.get_last_customer_message(ticket.id)
        assert last_message is None
        assert ai_message.is_ai is True
        assert ai_message.ticket_id == ticket.id

    async def test_get_last_customer_message_both_messages(
        self,
        ticket_service: TicketService,
        ticket: TicketRead,
        message: MessageRead,
        ai_message: MessageRead,
    ):
        last_message = await ticket_service.get_last_customer_message(ticket.id)
        assert last_message is not None
        assert isinstance(last_message, MessageRead)
        assert last_message.id == message.id
        assert last_message.content == message.content
        assert last_message.ticket_id == ticket.id
        assert last_message.is_ai is False
        assert ai_message.is_ai is True

    async def test_get_last_customer_message_ticket_not_found(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_last_customer_message(uuid.uuid4())

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Ticket not found"

    async def test_get_last_customer_message_ticket_not_uuid(
        self,
        ticket_service: TicketService,
    ):
        with pytest.raises(HTTPException) as excinfo:
            await ticket_service.get_last_customer_message("not-a-uuid")

        assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
