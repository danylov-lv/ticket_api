from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TicketStatusBase(BaseModel):
    name: str

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.lower().strip()
        if not value:
            raise ValueError("Name cannot be empty.")
        return value


class TicketStatusCreate(TicketStatusBase):
    pass


class TicketStatusRead(TicketStatusBase):
    model_config: ConfigDict = ConfigDict(from_attributes=True)

    id: uuid.UUID


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
    status: TicketStatusRead
    created_at: datetime
