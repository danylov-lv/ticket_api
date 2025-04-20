import uuid
import pytest
from fastapi import status
from httpx import AsyncClient

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


@pytest.mark.asyncio(loop_scope="session")
class TestTicketRouter:
    async def test_create_ticket_status_unauthorized(
        self,
        async_client: AsyncClient,
    ):
        ticket_status_create = TicketStatusCreate(
            name="Test Status",
        )

        response = await async_client.post(
            "/tickets/statuses",
            json=ticket_status_create.model_dump(mode="json"),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_ticket_status_not_superuser(
        self,
        async_client: AsyncClient,
        user_token: str,
    ):
        ticket_status_create = TicketStatusCreate(
            name="Test Status",
        )

        response = await async_client.post(
            "/tickets/statuses",
            json=ticket_status_create.model_dump(mode="json"),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_ticket_status(
        self,
        async_client: AsyncClient,
        superuser_token: str,
    ):
        ticket_status_create = TicketStatusCreate(
            name="Test Status",
        )

        response = await async_client.post(
            "/tickets/statuses",
            json=ticket_status_create.model_dump(mode="json"),
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() is not None

        ticket_status = TicketStatusRead.model_validate(response.json())
        assert ticket_status.id is not None
        assert ticket_status.name == ticket_status_create.name

    async def test_create_ticket_status_duplicate(
        self,
        async_client: AsyncClient,
        ticket_status: TicketStatusRead,
        superuser_token: str,
    ):
        ticket_status_create = TicketStatusCreate(
            name=ticket_status.name,
        )

        response = await async_client.post(
            "/tickets/statuses",
            json=ticket_status_create.model_dump(mode="json"),
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_get_all_ticket_statuses_unauthorized(
        self,
        async_client: AsyncClient,
    ):
        response = await async_client.get("/tickets/statuses")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_all_ticket_statuses(
        self,
        async_client: AsyncClient,
        user_token: str,
        ticket_status: TicketStatusRead,
    ):
        response = await async_client.get(
            "/tickets/statuses",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None

        ticket_statuses = [
            TicketStatusRead.model_validate(item) for item in response.json()
        ]
        assert len(ticket_statuses) > 0
        assert all(ts.id is not None for ts in ticket_statuses)
        assert all(ts.name is not None for ts in ticket_statuses)
        assert any(ts.id == ticket_status.id for ts in ticket_statuses)
        assert any(ts.name == ticket_status.name for ts in ticket_statuses)

    async def test_delete_ticket_status_unauthorized(
        self,
        async_client: AsyncClient,
        ticket_status: TicketStatusRead,
    ):
        response = await async_client.delete(
            f"/tickets/statuses/{ticket_status.id}",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_ticket_status_not_superuser(
        self,
        async_client: AsyncClient,
        ticket_status: TicketStatusRead,
        user_token: str,
    ):
        response = await async_client.delete(
            f"/tickets/statuses/{ticket_status.id}",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_ticket_status(
        self,
        async_client: AsyncClient,
        ticket_status: TicketStatusRead,
        superuser_token: str,
    ):
        response = await async_client.delete(
            f"/tickets/statuses/{ticket_status.id}",
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify that the ticket status is deleted
        response = await async_client.get(
            "/tickets/statuses",
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None

        ticket_statuses = [
            TicketStatusRead.model_validate(item) for item in response.json()
        ]
        assert len(ticket_statuses) == 0

    async def test_delete_ticket_status_not_found(
        self,
        async_client: AsyncClient,
        superuser_token: str,
    ):
        response = await async_client.delete(
            f"/tickets/statuses/{uuid.uuid4()}",
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_ticket_status_not_uuid(
        self,
        async_client: AsyncClient,
        superuser_token: str,
    ):
        response = await async_client.delete(
            "/tickets/statuses/invalid-uuid",
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_ticket_unauthorized(
        self,
        async_client: AsyncClient,
        ticket_status: TicketStatusRead,
        user: UserRead,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="Test Description",
            status_id=ticket_status.id,
            user_id=user.id,
        )

        response = await async_client.post(
            "/tickets",
            json=ticket_create.model_dump(mode="json"),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_ticket(
        self,
        async_client: AsyncClient,
        ticket_status: TicketStatusRead,
        user: UserRead,
        user_token: str,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="Test Description",
            status_id=ticket_status.id,
            user_id=user.id,
        )

        response = await async_client.post(
            "/tickets",
            json=ticket_create.model_dump(mode="json"),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() is not None

        ticket = TicketRead.model_validate(response.json())
        assert ticket.id is not None
        assert ticket.title == ticket_create.title
        assert ticket.description == ticket_create.description
        assert ticket.status_id == ticket_create.status_id
        assert ticket.user_id == ticket_create.user_id
        assert ticket.status.id == ticket_status.id

    async def test_create_ticket_omit_user_id(
        self,
        async_client: AsyncClient,
        ticket_status: TicketStatusRead,
        user: UserRead,
        user_token: str,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="Test Description",
            status_id=ticket_status.id,
        )

        response = await async_client.post(
            "/tickets",
            json=ticket_create.model_dump(mode="json"),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() is not None

        ticket = TicketRead.model_validate(response.json())
        assert ticket.id is not None
        assert ticket.title == ticket_create.title
        assert ticket.description == ticket_create.description
        assert ticket.status_id == ticket_create.status_id
        assert ticket.user_id == user.id

    async def test_create_ticket_not_owner(
        self,
        async_client: AsyncClient,
        ticket_status: TicketStatusRead,
        user_token: str,
        superuser: UserRead,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="Test Description",
            status_id=ticket_status.id,
            user_id=superuser.id,
        )

        response = await async_client.post(
            "/tickets",
            json=ticket_create.model_dump(mode="json"),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_ticket_not_owner_superuser(
        self,
        async_client: AsyncClient,
        ticket_status: TicketStatusRead,
        superuser: UserRead,
        superuser_token: str,
        user: UserRead,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="Test Description",
            status_id=ticket_status.id,
            user_id=user.id,
        )

        response = await async_client.post(
            "/tickets",
            json=ticket_create.model_dump(mode="json"),
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() is not None

        ticket = TicketRead.model_validate(response.json())
        assert ticket.id is not None
        assert ticket.title == ticket_create.title
        assert ticket.user_id == user.id
        assert ticket.user_id != superuser.id

    async def test_create_ticket_status_not_found(
        self,
        async_client: AsyncClient,
        user_token: str,
        user: UserRead,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="Test Description",
            status_id=uuid.uuid4(),
            user_id=user.id,
        )

        response = await async_client.post(
            "/tickets",
            json=ticket_create.model_dump(mode="json"),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_ticket_user_not_found(
        self,
        async_client: AsyncClient,
        ticket_status: TicketStatusRead,
        superuser_token: str,
    ):
        ticket_create = TicketCreate(
            title="Test Ticket",
            description="Test Description",
            status_id=ticket_status.id,
            user_id=uuid.uuid4(),
        )

        response = await async_client.post(
            "/tickets",
            json=ticket_create.model_dump(mode="json"),
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_all_tickets_unauthorized(
        self,
        async_client: AsyncClient,
    ):
        response = await async_client.get("/tickets")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_all_tickets(
        self,
        async_client: AsyncClient,
        user_token: str,
        ticket: TicketRead,
    ):
        response = await async_client.get(
            "/tickets",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None

        tickets = [TicketRead.model_validate(item) for item in response.json()]
        assert len(tickets) > 0
        assert all(t.id is not None for t in tickets)
        assert all(t.title is not None for t in tickets)
        assert any(t.id == ticket.id for t in tickets)
        assert any(t.title == ticket.title for t in tickets)
        assert any(t.user_id == ticket.user_id for t in tickets)
        assert any(t.status.id == ticket.status.id for t in tickets)

    async def test_get_all_tickets_not_owner(
        self,
        async_client: AsyncClient,
        superuser_token: str,
        ticket: TicketRead,
    ):
        response = await async_client.get(
            "/tickets",
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None

        tickets = [TicketRead.model_validate(item) for item in response.json()]
        assert len(tickets) == 0

    async def test_get_ticket_unauthorized(
        self,
        async_client: AsyncClient,
        ticket: TicketRead,
    ):
        response = await async_client.get(f"/tickets/{ticket.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_ticket(
        self,
        async_client: AsyncClient,
        user_token: str,
        ticket: TicketRead,
    ):
        response = await async_client.get(
            f"/tickets/{ticket.id}",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None

        ticket_response = TicketRead.model_validate(response.json())
        assert ticket_response.id == ticket.id
        assert ticket_response.title == ticket.title
        assert ticket_response.description == ticket.description
        assert ticket_response.user_id == ticket.user_id
        assert ticket_response.status.id == ticket.status.id

    async def test_get_ticket_not_owner(
        self,
        async_client: AsyncClient,
        superuser_ticket: TicketRead,
        user: UserRead,
        user_token: str,
    ):
        assert superuser_ticket.user_id != user.id
        assert user.is_superuser is False

        response = await async_client.get(
            f"/tickets/{superuser_ticket.id}",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_ticket_not_owner_superuser(
        self,
        async_client: AsyncClient,
        ticket: TicketRead,
        superuser: UserRead,
        superuser_token: str,
    ):
        assert ticket.user_id != superuser.id
        assert superuser.is_superuser is True

        response = await async_client.get(
            f"/tickets/{ticket.id}",
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None

        ticket_response = TicketRead.model_validate(response.json())
        assert ticket_response.id == ticket.id
        assert ticket_response.title == ticket.title
        assert ticket_response.description == ticket.description
        assert ticket_response.user_id == ticket.user_id
        assert ticket_response.status.id == ticket.status.id

    async def test_get_ticket_not_found(
        self,
        async_client: AsyncClient,
        user_token: str,
    ):
        response = await async_client.get(
            f"/tickets/{uuid.uuid4()}",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_ticket_not_uuid(
        self,
        async_client: AsyncClient,
        user_token: str,
    ):
        response = await async_client.get(
            "/tickets/invalid-uuid",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_update_ticket_unauthorized(
        self,
        async_client: AsyncClient,
        ticket: TicketRead,
    ):
        ticket_update = TicketUpdate(
            title="Updated Title",
            description="Updated Description",
        )

        response = await async_client.put(
            f"/tickets/{ticket.id}",
            json=ticket_update.model_dump(mode="json"),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_ticket(
        self,
        async_client: AsyncClient,
        user_token: str,
        ticket: TicketRead,
    ):
        ticket_update = TicketUpdate(
            title="Updated Title",
            description="Updated Description",
        )

        response = await async_client.put(
            f"/tickets/{ticket.id}",
            json=ticket_update.model_dump(mode="json", exclude_unset=True),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None

        ticket_response = TicketRead.model_validate(response.json())
        assert ticket_response.id == ticket.id
        assert ticket_response.title == ticket_update.title
        assert ticket_response.description == ticket_update.description
        assert ticket_response.user_id == ticket.user_id

    async def test_update_ticket_not_owner(
        self,
        async_client: AsyncClient,
        superuser_ticket: TicketRead,
        user: UserRead,
        user_token: str,
    ):
        assert superuser_ticket.user_id != user.id
        assert user.is_superuser is False

        ticket_update = TicketUpdate(
            title="Updated Title",
            description="Updated Description",
        )

        response = await async_client.put(
            f"/tickets/{superuser_ticket.id}",
            json=ticket_update.model_dump(mode="json", exclude_unset=True),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_ticket_not_owner_superuser(
        self,
        async_client: AsyncClient,
        ticket: TicketRead,
        superuser: UserRead,
        superuser_token: str,
    ):
        assert ticket.user_id != superuser.id
        assert superuser.is_superuser is True

        ticket_update = TicketUpdate(
            title="Updated Title",
            description="Updated Description",
        )

        response = await async_client.put(
            f"/tickets/{ticket.id}",
            json=ticket_update.model_dump(mode="json", exclude_unset=True),
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None

        ticket_response = TicketRead.model_validate(response.json())
        assert ticket_response.id == ticket.id
        assert ticket_response.title == ticket_update.title
        assert ticket_response.description == ticket_update.description
        assert ticket_response.user_id == ticket.user_id

    async def test_update_ticket_not_found(
        self,
        async_client: AsyncClient,
        user_token: str,
    ):
        ticket_update = TicketUpdate(
            title="Updated Title",
            description="Updated Description",
        )

        response = await async_client.put(
            f"/tickets/{uuid.uuid4()}",
            json=ticket_update.model_dump(mode="json", exclude_unset=True),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_ticket_not_uuid(
        self,
        async_client: AsyncClient,
        user_token: str,
    ):
        ticket_update = TicketUpdate(
            title="Updated Title",
            description="Updated Description",
        )

        response = await async_client.put(
            "/tickets/invalid-uuid",
            json=ticket_update.model_dump(mode="json", exclude_unset=True),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_delete_ticket_unauthorized(
        self,
        async_client: AsyncClient,
        ticket: TicketRead,
    ):
        response = await async_client.delete(f"/tickets/{ticket.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_ticket(
        self,
        async_client: AsyncClient,
        user_token: str,
        ticket: TicketRead,
    ):
        response = await async_client.delete(
            f"/tickets/{ticket.id}",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify that the ticket is deleted
        response = await async_client.get(
            f"/tickets/{ticket.id}",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_ticket_not_owner(
        self,
        async_client: AsyncClient,
        superuser_ticket: TicketRead,
        user: UserRead,
        user_token: str,
    ):
        assert superuser_ticket.user_id != user.id
        assert user.is_superuser is False

        response = await async_client.delete(
            f"/tickets/{superuser_ticket.id}",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_ticket_not_owner_superuser(
        self,
        async_client: AsyncClient,
        ticket: TicketRead,
        superuser: UserRead,
        superuser_token: str,
    ):
        assert ticket.user_id != superuser.id
        assert superuser.is_superuser is True

        response = await async_client.delete(
            f"/tickets/{ticket.id}",
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify that the ticket is deleted
        response = await async_client.get(
            f"/tickets/{ticket.id}",
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_ticket_not_found(
        self,
        async_client: AsyncClient,
        user_token: str,
    ):
        response = await async_client.delete(
            f"/tickets/{uuid.uuid4()}",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_ticket_not_uuid(
        self,
        async_client: AsyncClient,
        user_token: str,
    ):
        response = await async_client.delete(
            "/tickets/invalid-uuid",
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_message_unauthorized(
        self,
        async_client: AsyncClient,
        ticket: TicketRead,
    ):
        message_create = MessageCreate(
            content="Test Message",
        )

        response = await async_client.post(
            f"/tickets/{ticket.id}/messages",
            json=message_create.model_dump(mode="json"),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_message(
        self,
        async_client: AsyncClient,
        user_token: str,
        ticket: TicketRead,
    ):
        message_create = MessageCreate(
            content="Test Message",
        )

        response = await async_client.post(
            f"/tickets/{ticket.id}/messages",
            json=message_create.model_dump(mode="json"),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() is not None

        message = MessageRead.model_validate(response.json())
        assert message.id is not None
        assert message.content == message_create.content
        assert message.ticket_id == ticket.id

    async def test_create_message_not_owner(
        self,
        async_client: AsyncClient,
        superuser_ticket: TicketRead,
        user: UserRead,
        user_token: str,
    ):
        assert superuser_ticket.user_id != user.id
        assert user.is_superuser is False

        message_create = MessageCreate(
            content="Test Message",
        )

        response = await async_client.post(
            f"/tickets/{superuser_ticket.id}/messages",
            json=message_create.model_dump(mode="json"),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_message_not_owner_superuser(
        self,
        async_client: AsyncClient,
        ticket: TicketRead,
        superuser: UserRead,
        superuser_token: str,
    ):
        assert ticket.user_id != superuser.id
        assert superuser.is_superuser is True

        message_create = MessageCreate(
            content="Test Message",
        )

        response = await async_client.post(
            f"/tickets/{ticket.id}/messages",
            json=message_create.model_dump(mode="json"),
            headers={"Authorization": superuser_token},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() is not None

        message = MessageRead.model_validate(response.json())
        assert message.id is not None
        assert message.content == message_create.content
        assert message.ticket_id == ticket.id

    async def test_create_message_ai_message(
        self,
        async_client: AsyncClient,
        user_token: str,
        ticket: TicketRead,
    ):
        message_create = MessageCreate(
            content="Test Message",
            is_ai=True,
        )

        response = await async_client.post(
            f"/tickets/{ticket.id}/messages",
            json=message_create.model_dump(mode="json"),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_message_ticket_not_found(
        self,
        async_client: AsyncClient,
        user_token: str,
    ):
        message_create = MessageCreate(
            content="Test Message",
        )

        response = await async_client.post(
            f"/tickets/{uuid.uuid4()}/messages",
            json=message_create.model_dump(mode="json"),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_message_ticket_not_uuid(
        self,
        async_client: AsyncClient,
        user_token: str,
    ):
        message_create = MessageCreate(
            content="Test Message",
        )

        response = await async_client.post(
            "/tickets/invalid-uuid/messages",
            json=message_create.model_dump(mode="json"),
            headers={"Authorization": user_token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_stream_ai_response_unauthorized(
        self,
        async_client: AsyncClient,
        ticket: TicketRead,
    ):
        response = await async_client.get(
            f"/tickets/{ticket.id}/ai-response",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # httpx doesn't work well with streaming responses, so we can't test this directly, test finishes but never closes the connection

    # async def test_stream_ai_response(
    #     self,
    #     async_client: AsyncClient,
    #     user_token: str,
    #     ticket: TicketRead,
    #     ai_response: str,
    # ):
    #     async with async_client.stream(
    #         "GET",
    #         f"/tickets/{ticket.id}/ai-response",
    #         headers={"Authorization": user_token},
    #     ) as response:
    #         assert response.status_code == status.HTTP_200_OK

    #         assert "text/event-stream" in response.headers["Content-Type"]

    #         events = []

    #         async for line in response.aiter_lines():
    #             if line.startswith("data: "):
    #                 events.append(line.replace("data: ", ""))

    #             if len(events) == len(ai_response):
    #                 break

    #         assert "".join(events) == ai_response

    #         await response.aclose()
    #     # Check created message in the database

    #     response = await async_client.get(
    #         f"/tickets/{ticket.id}",
    #         headers={"Authorization": user_token},
    #     )
    #     assert response.status_code == status.HTTP_200_OK

    #     assert response.json() is not None
    #     ticket_response = TicketRead.model_validate(response.json())
    #     messages = ticket_response.messages

    #     assert len(messages) > 0
    #     assert all(m.id is not None for m in messages)
    #     assert all(m.content is not None for m in messages)
    #     assert any(m.content == ai_response for m in messages)
    #     assert any(m.ticket_id == ticket.id for m in messages)
    #     assert any(m.is_ai is True for m in messages)
