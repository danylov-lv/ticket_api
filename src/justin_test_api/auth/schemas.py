import uuid

from fastapi_users import schemas

from ..tickets.schemas import TicketRead


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class UserRead(schemas.BaseUser[uuid.UUID]):
    tickets: list["TicketRead"]
