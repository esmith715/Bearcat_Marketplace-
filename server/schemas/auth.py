from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

#=======#
# Enums #
#=======#
class TokenType(Enum):
    access = "access"
    refresh = "refresh"


#=========#
# Schemas #
#=========#
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email_or_username: str
    password: str

class TokenData(BaseModel):
    id: UUID | None = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str
