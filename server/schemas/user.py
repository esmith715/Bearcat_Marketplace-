from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

#=======#
# Enums #
#=======#
class UserRole(Enum):
    student = "student"
    admin = "admin"


#=========#
# Schemas #
#=========#
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=20)
    verification_token: str
    role: UserRole = UserRole.student
    is_email_verified: bool = False
    admin_approved: bool = False

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: UUID
    password_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True