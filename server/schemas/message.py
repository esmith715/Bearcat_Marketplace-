from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: UUID
    from_user_id: UUID
    to_user_id: UUID
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: UUID
    from_user_id: UUID
    to_user_id: UUID
    content: str
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None

    class Config:
        from_attributes = True
