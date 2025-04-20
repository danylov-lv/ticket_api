import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from ..auth.router import get_current_active_superuser, get_current_active_user
from ..auth.schemas import UserRead
from .ai import AIService
from .dependencies import get_ai_service, get_ticket_service
from .schemas import (
    MessageCreate,
    MessageRead,
    TicketCreate,
    TicketRead,
    TicketStatusCreate,
    TicketStatusRead,
    TicketUpdate,
)
from .service import TicketService

router = APIRouter()


@router.post(
    "/statuses",
    response_model=TicketStatusRead,
)
async def create_ticket_status(
    ticket_status_create: TicketStatusCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
    _: UserRead = Depends(get_current_active_superuser),
) -> TicketStatusRead:
    """
    Create a new ticket status.
    """

    return await ticket_service.create_ticket_status(ticket_status_create)


@router.get(
    "/statuses",
    response_model=list[TicketStatusRead],
)
async def get_all_ticket_statuses(
    ticket_service: TicketService = Depends(get_ticket_service),
    _: UserRead = Depends(get_current_active_user),
) -> list[TicketStatusRead]:
    """
    Get all ticket statuses.
    """

    return await ticket_service.get_all_ticket_statuses()


@router.delete(
    "/statuses/{ticket_status_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ticket_status(
    ticket_status_id: uuid.UUID,
    ticket_service: TicketService = Depends(get_ticket_service),
    _: UserRead = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a ticket status by ID.
    """

    await ticket_service.delete_ticket_status(ticket_status_id)


@router.get(
    "",
    response_model=list[TicketRead],
)
async def get_all_tickets(
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> list[TicketRead]:
    """
    Get all tickets.
    """
    return await ticket_service.get_all_tickets_by_user(current_user.id)


@router.post(
    "",
    response_model=TicketRead,
)
async def create_ticket(
    ticket_create: TicketCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> TicketRead:
    """
    Create a new ticket.

    If `user_id` is not provided in the request, it will default to the current user's ID.
    If the current user is not a superuser, they can only create tickets for themselves.
    If the current user is a superuser, they can create tickets for any user.
    """
    if ticket_create.user_id is None:
        ticket_create.user_id = current_user.id

    if ticket_create.user_id != current_user.id and current_user.is_superuser is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create tickets for other users.",
        )

    return await ticket_service.create_ticket(ticket_create)


@router.get(
    "/{ticket_id}",
    response_model=TicketRead,
)
async def get_ticket(
    ticket_id: uuid.UUID,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> TicketRead:
    """
    Get a ticket by ID.
    """

    ticket_service.is_ticket_accessible(ticket_id, current_user.id)

    return await ticket_service.get_ticket(ticket_id)


@router.put(
    "/{ticket_id}",
    response_model=TicketRead,
)
async def update_ticket(
    ticket_id: uuid.UUID,
    ticket_update: TicketUpdate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> TicketRead:
    """
    Update a ticket by ID.
    """
    ticket_service.is_ticket_accessible(ticket_id, current_user.id)

    return await ticket_service.update_ticket(ticket_id, ticket_update)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ticket(
    ticket_id: uuid.UUID,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> None:
    """
    Delete a ticket by ID.
    """
    ticket_service.is_ticket_accessible(ticket_id, current_user.id)

    await ticket_service.delete_ticket(ticket_id)


@router.post(
    "/{ticket_id}/messages",
    response_model=MessageRead,
)
async def create_message(
    ticket_id: uuid.UUID,
    message_create: MessageCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> MessageRead:
    """
    Create a new message for a ticket.
    """

    if message_create.is_ai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI messages cannot be created manually.",
        )

    ticket_service.is_ticket_accessible(ticket_id, current_user.id)

    return await ticket_service.create_message(ticket_id, message_create)


@router.get(
    "/{ticket_id}/ai-response",
    response_model=MessageRead,
    response_class=EventSourceResponse,
)
async def stream_ai_response(
    ticket_id: uuid.UUID,
    ticket_service: TicketService = Depends(get_ticket_service),
    ai_service: AIService = Depends(get_ai_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> EventSourceResponse:
    """
    Stream AI response for a ticket.

    This endpoint streams the AI-generated response for a ticket in real-time using Server-Sent Events (SSE).
    The AI model processes the ticket description and message history to generate a response.
    After this, to keep track of the conversation, the AI response is saved as a message in the ticket.

    """
    ticket_service.is_ticket_accessible(ticket_id, current_user.id)

    ticket = await ticket_service.get_ticket(ticket_id)
    message_history = await ticket_service.get_ticket_messages(ticket_id)
    customer_last_message = await ticket_service.get_last_customer_message(
        ticket_id=ticket_id,
    )

    prompt = ai_service.build_prompt(ticket, message_history, customer_last_message)

    async def event_generator():
        content = ""

        async for chunk in ai_service.stream_response(prompt):
            if chunk is None:
                break
            content += chunk
            yield chunk

        message_create = MessageCreate(
            content=content,
            is_ai=True,
        )
        await ticket_service.create_message(
            ticket_id=ticket_id,
            message_create=message_create,
        )

    return EventSourceResponse(event_generator())
