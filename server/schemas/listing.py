import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
import enum

# Enums
class ListingType(enum.Enum):
    book = "book"
    furniture = "furniture"
    misc = "misc"

class ListingStatus(enum.Enum):
    active = "active"
    pending = "pending"
    sold = "sold"
    inactive = "inactive"

# Schema
class ListingBase(BaseModel):
    type: ListingType
    title: str
    description: Optional[str] = None
    price_cents: int = Field(..., ge=0)
    item_condition: Optional[str] = None
    book_id: Optional[uuid.UUID] = None
    course_id: Optional[uuid.UUID] = None
    isbn: Optional[str] = None
    measurements: Optional[str] = None

class ListingCreate(ListingBase):
    pass

class ListingUpdate(ListingBase):
    status: Optional[ListingStatus] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price_cents: int = Field(..., ge=0)
    item_condition: Optional[str] = None
    book_id: Optional[uuid.UUID] = None
    course_id: Optional[uuid.UUID] = None
    isbn: Optional[str] = None
    measurements: Optional[str] = None
    sold_at: Optional[datetime] = None
    sold_to: Optional[uuid.UUID] = None

class Listing(ListingBase):
    id: uuid.UUID
    status: ListingStatus
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    sold_at: Optional[datetime] = None
    sold_to: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True