from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    from_user_id: UUID
    to_user_id: UUID
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None

    def to_websocket_payload(self) -> dict:
        """
        Serialize this message into a WebSocket-ready payload
        """
        
        return {
            "type": "direct_message",
            "message": {
                "id": str(self.id),
                "listing_id": str(self.listing_id),
                "from_user_id": str(self.from_user_id),
                "to_user_id": str(self.to_user_id),
                "content": self.content,
                "is_read": self.is_read,
                "created_at": self.created_at.isoformat(),
                "read_at": self.read_at.isoformat() if self.read_at else None,
            }
        }