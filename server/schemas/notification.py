from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

#=======#
# Enums #
#=======#
class NotificationType(Enum):
    new_message = "new_message"
    listing_updated = "listing_updated"
    listing_sold = "listing_sold"


#=========#
# Schemas #
#=========#
class NotificationBase(BaseModel):
    user_id: UUID
    type: NotificationType
    message_id: Optional[UUID] = None
    listing_id: Optional[UUID] = None

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: NotificationType
    is_read: bool
    created_at: datetime

    def to_websocket_payload(self) -> dict:
        """
        Serialize this notification into a WebSocket-ready payload
        """

        return {
            "type": "notification",
            "notification": {
                "id": str(self.id),
                "type": self.type.value,
                "is_read": self.is_read,
                "created_at": self.created_at.isoformat(),
                "message_id": str(self.message_id) if self.message_id else None,
                "listing_id": str(self.listing_id) if self.listing_id else None,
            }
        }