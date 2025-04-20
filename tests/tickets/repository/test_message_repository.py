import uuid

import pytest
from sqlalchemy.exc import DBAPIError, IntegrityError

from ticket_api.tickets.models import Message
from ticket_api.tickets.repository import MessageRepository
from ticket_api.tickets.schemas import MessageCreate, MessageRead, TicketRead


@pytest.mark.asyncio(loop_scope="session")
class TestMessageRepository:
    async def test_create(
        self,
        message_repository: MessageRepository,
        ticket: TicketRead,
    ):
        message_create = MessageCreate(
            content="This is a test message.",
        )
        message = await message_repository.create(
            ticket.id,
            message_create,
        )
        assert isinstance(message, Message)
        assert message.id is not None
        assert message.content == message_create.content
        assert message.ticket_id == ticket.id
        assert message.created_at is not None

    async def test_create_with_invalid_ticket(
        self,
        message_repository: MessageRepository,
    ):
        message_create = MessageCreate(
            content="This is a test message.",
        )

        with pytest.raises(IntegrityError):
            await message_repository.create(
                uuid.uuid4(),  # Invalid ticket ID
                message_create,
            )

    async def test_create_with_ticket_not_uuid(
        self,
        message_repository: MessageRepository,
    ):
        message_create = MessageCreate(
            content="This is a test message.",
        )

        with pytest.raises(DBAPIError):
            await message_repository.create(
                "not-a-uuid",  # Invalid ticket ID
                message_create,
            )

    async def test_exists(
        self,
        message_repository: MessageRepository,
        message: MessageRead,
    ):
        exists = await message_repository.exists(message.id)
        assert exists is True

    async def test_exists_not_found(
        self,
        message_repository: MessageRepository,
    ):
        exists = await message_repository.exists(uuid.uuid4())
        assert exists is False

    async def test_exists_not_uuid(
        self,
        message_repository: MessageRepository,
    ):
        with pytest.raises(DBAPIError):
            await message_repository.exists("not-a-uuid")

    async def test_get(
        self,
        message_repository: MessageRepository,
        message: MessageRead,
    ):
        message_from_db = await message_repository.get(message.id)
        assert isinstance(message_from_db, Message)
        assert message_from_db.id == message.id
        assert message_from_db.content == message.content
        assert message_from_db.ticket_id == message.ticket_id
        assert message_from_db.created_at == message.created_at

    async def test_get_not_found(
        self,
        message_repository: MessageRepository,
    ):
        message_from_db = await message_repository.get(uuid.uuid4())
        assert message_from_db is None

    async def test_get_not_uuid(
        self,
        message_repository: MessageRepository,
    ):
        with pytest.raises(DBAPIError):
            await message_repository.get("not-a-uuid")

    async def test_get_all_by_ticket(
        self,
        message_repository: MessageRepository,
        ticket: TicketRead,
        message: MessageRead,
    ):
        messages = await message_repository.get_all_by_ticket(ticket.id)
        assert isinstance(messages, list)
        assert all(isinstance(m, Message) for m in messages)
        assert all(m.ticket_id == ticket.id for m in messages)
        assert any(m.id == message.id for m in messages)
        assert any(m.content == message.content for m in messages)
        assert any(m.created_at == message.created_at for m in messages)

        # Validate sorting by created_at
        assert messages == sorted(messages, key=lambda m: m.created_at)

    async def test_get_all_by_ticket_empty(
        self,
        message_repository: MessageRepository,
        ticket: TicketRead,
    ):
        messages = await message_repository.get_all_by_ticket(ticket.id)
        assert messages == []

    async def test_get_all_by_ticket_not_found(
        self,
        message_repository: MessageRepository,
    ):
        messages = await message_repository.get_all_by_ticket(uuid.uuid4())
        assert messages == []

    async def test_get_all_by_ticket_not_uuid(
        self,
        message_repository: MessageRepository,
    ):
        with pytest.raises(DBAPIError):
            await message_repository.get_all_by_ticket("not-a-uuid")

    async def test_get_last_customer_message(
        self,
        message_repository: MessageRepository,
        ticket: TicketRead,
        message: MessageRead,
    ):
        last_message = await message_repository.get_last_customer_message(ticket.id)
        assert isinstance(last_message, Message)
        assert last_message.id == message.id
        assert last_message.content == message.content
        assert last_message.ticket_id == ticket.id
        assert last_message.created_at == message.created_at

    async def test_get_last_customer_message_empty(
        self,
        message_repository: MessageRepository,
        ticket: TicketRead,
    ):
        last_message = await message_repository.get_last_customer_message(ticket.id)
        assert last_message is None

    async def test_get_last_customer_message_no_customer_message(
        self,
        message_repository: MessageRepository,
        ticket: TicketRead,
        ai_message: MessageRead,
    ):
        last_message = await message_repository.get_last_customer_message(ticket.id)
        assert last_message is None

    async def test_get_last_customer_message_both_messages(
        self,
        message_repository: MessageRepository,
        ticket: TicketRead,
        message: MessageRead,
        ai_message: MessageRead,
    ):
        last_message = await message_repository.get_last_customer_message(ticket.id)
        assert isinstance(last_message, Message)
        assert last_message.id == message.id
        assert last_message.content == message.content
        assert last_message.ticket_id == ticket.id
        assert last_message.created_at == message.created_at

    async def test_get_last_customer_message_not_found(
        self,
        message_repository: MessageRepository,
    ):
        last_message = await message_repository.get_last_customer_message(uuid.uuid4())
        assert last_message is None

    async def test_get_last_customer_message_not_uuid(
        self,
        message_repository: MessageRepository,
    ):
        with pytest.raises(DBAPIError):
            await message_repository.get_last_customer_message("not-a-uuid")
