from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID

#=======#
# Enums #
#=======#
class TokenType(Enum):
    access = "access"
    refresh = "refresh"
    email_verification = "email_verification"
    password_reset = "password_reset"


#=========#
# Schemas #
#=========#
class UserRegister(BaseModel):
    email: str
    username: str
    password: str = Field(min_length=4)

class UserLogin(BaseModel):
    email_or_username: str
    password: str

class TokenData(BaseModel):
    id: UUID | None = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    token: str
    type: TokenType
    expires_at: datetime
    created_at: datetime
    used_at: Optional[datetime] = None
