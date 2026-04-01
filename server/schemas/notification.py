from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID

#=======#
# Enums #
#=======#
class NotificationType(Enum):
    message = "message"
    listing_updated = "listing_updated"
    listing_sold = "listing_sold"


#=========#
# Schemas #
#=========#
class NotificationCreate(BaseModel):
    user_id: UUID
    type: NotificationType
    title: str
    body: str
    listing_id: Optional[UUID] = None
    actor_id: Optional[UUID] = None


class Notification(BaseModel):
    user_id: UUID
    type: NotificationType
    title: str
    body: str
    listing_id: Optional[UUID] = None
    actor_id: Optional[UUID] = None
    is_read: bool
    created_at: datetime