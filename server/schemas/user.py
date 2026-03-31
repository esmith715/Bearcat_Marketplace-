from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID

#=======#
# Enums #
#=======#
class UserRole(Enum):
    student = "student"
    admin = "admin"


#=========#
# Request #
#=========#
class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=20)
    password: Optional[str] = Field(default=None, min_length=3)


#==========#
# Response #
#==========#
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str = Field(min_length=3, max_length=20)
    role: UserRole = UserRole.student
    is_email_verified: bool
    admin_approved: bool
    created_at: datetime
    updated_at: datetime


#==========#
# Database #
#==========#
class UserInDB(UserResponse):
    password_hash: str

    def to_response(self) -> UserResponse:
        return UserResponse.model_validate(self.model_dump())