import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from ..auth.router import get_current_active_user, get_current_active_superuser
from ..auth.schemas import UserRead
from .dependencies import get_ticket_service
from .schemas import (
    TicketCreate,
    TicketRead,
    TicketStatusCreate,
    TicketStatusRead,
    TicketUpdate,
)
from .service import TicketService

router = APIRouter()


@router.post("/statuses", response_model=TicketStatusRead)
async def create_ticket_status(
    ticket_status_create: TicketStatusCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
    _: UserRead = Depends(get_current_active_superuser),
) -> TicketStatusRead:
    """
    Create a new ticket status.
    """

    return await ticket_service.create_ticket_status(ticket_status_create)


@router.get("/statuses", response_model=list[TicketStatusRead])
async def get_all_ticket_statuses(
    ticket_service: TicketService = Depends(get_ticket_service),
    _: UserRead = Depends(get_current_active_superuser),
) -> list[TicketStatusRead]:
    """
    Get all ticket statuses.
    """

    return await ticket_service.get_all_ticket_statuses()


@router.get("/statuses/{ticket_status_id}", response_model=TicketStatusRead)
async def get_ticket_status(
    ticket_status_id: uuid.UUID,
    ticket_service: TicketService = Depends(get_ticket_service),
    _: UserRead = Depends(get_current_active_superuser),
) -> TicketStatusRead:
    """
    Get a ticket status by ID.
    """

    return await ticket_service.get_ticket_status(ticket_status_id)


@router.get("", response_model=list[TicketRead])
async def get_all_tickets(
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> list[TicketRead]:
    """
    Get all tickets.
    """
    return await ticket_service.get_all_tickets_by_user(current_user.id)


@router.post("", response_model=TicketRead)
async def create_ticket(
    ticket_create: TicketCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> TicketRead:
    """
    Create a new ticket.
    """
    if ticket_create.user_id != current_user.id and current_user.is_superuser is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create tickets for other users.",
        )

    return await ticket_service.create_ticket(ticket_create)


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket(
    ticket_id: uuid.UUID,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> TicketRead:
    """
    Get a ticket by ID.
    """

    if (
        not ticket_service.is_ticket_accessible(ticket_id, current_user.id)
        and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this ticket.",
        )

    return await ticket_service.get_ticket(ticket_id)


@router.put("/{ticket_id}", response_model=TicketRead)
async def update_ticket(
    ticket_id: uuid.UUID,
    ticket_update: TicketUpdate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> TicketRead:
    """
    Update a ticket by ID.
    """
    if (
        not ticket_service.is_ticket_accessible(ticket_id, current_user.id)
        and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this ticket.",
        )

    return await ticket_service.update_ticket(ticket_id, ticket_update)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: uuid.UUID,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user: UserRead = Depends(get_current_active_user),
) -> None:
    """
    Delete a ticket by ID.
    """
    if (
        not ticket_service.is_ticket_accessible(ticket_id, current_user.id)
        and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this ticket.",
        )

    await ticket_service.delete_ticket(ticket_id)
