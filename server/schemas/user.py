from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

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
    role: UserRole = UserRole.student
    is_email_verified: bool = False
    admin_approved: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True