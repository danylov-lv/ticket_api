from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field


class TicketStatusBase(BaseModel):
    name: str


class TicketStatusCreate(TicketStatusBase):
    pass


class TicketStatusRead(TicketStatusBase):
    model_config: ConfigDict = ConfigDict(from_attributes=True)

    id: str


class TicketBase(BaseModel):
    title: str
    description: str = ""
    user_id: uuid.UUID
    status_id: uuid.UUID


class TicketCreate(TicketBase):
    pass


class TicketUpdate(TicketBase):
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    status_id: uuid.UUID | None = Field(default=None)


class TicketRead(TicketBase):
    model_config: ConfigDict = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
