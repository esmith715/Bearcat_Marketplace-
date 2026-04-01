from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID

#=======#
# Enums #
#=======#
class ListingType(Enum):
    book = "book"
    furniture = "furniture"
    misc = "misc"

class ListingStatus(Enum):
    active = "active"
    pending = "pending"
    sold = "sold"
    inactive = "inactive"


#=========#
# Schemas #
#=========#
class ListingBase(BaseModel):
    type: ListingType
    title: str
    description: Optional[str] = None
    price_cents: int = Field(..., ge=0)
    item_condition: Optional[str] = None
    book_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    isbn: Optional[str] = None
    measurements: Optional[str] = None

class ListingCreate(ListingBase):
    pass

class ListingUpdate(ListingBase):
    status: Optional[ListingStatus] = None
    title: Optional[str] = None
    sold_at: Optional[datetime] = None
    sold_to: Optional[UUID] = None
    
    # Override from ListingBase to make Optional
    type: Optional[ListingType] = None
    title: Optional[str] = None
    price_cents: Optional[int] = Field(default=None, ge=0)

class Listing(ListingBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ListingStatus
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    sold_at: Optional[datetime] = None
    sold_to: Optional[UUID] = None
    image_url: Optional[str] = None