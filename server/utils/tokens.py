from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import secrets
from typing import Optional
from uuid import UUID

from server.config import settings
from server.schemas.auth import TokenData, TokenType


#=======================#
# Access/Refresh Tokens #
#=======================#
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta

    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token
    """

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt
    

def decode_token(token: str, token_type: TokenType) -> Optional[TokenData]:
    """
    Decode and validate a JWT access or refresh token
    """

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != token_type.value:
            print("wrong type")
            return None
        
        user_id = UUID(payload.get("sub"))
        if user_id is None:
            print("no user ID")
            return None
        
        return TokenData(id=user_id)
    
    except JWTError:
        print("Failed to decode token")
        return None
    

#==============#    
# Other Tokens #
#==============#
def generate_verification_token(length: int = 32) -> str:
    """
    Generate a secure random token for email verification.
    Uses URL-safe base64 encoding.
    """

    return secrets.token_urlsafe(length)


def get_email_verification_expiry() -> datetime:
    """
    Get expiration time for email verification token (based on settings.EMAIL_VERIFICATION_EXPIRE_HOURS in config.py)
    """
    
    return datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)


def get_password_reset_expiry() -> datetime:
    """
    Get expiration time for password reset token (24 hours from now)
    """

    return datetime.now(timezone.utc) + timedelta(hours=settings.PASSWORD_RESET_EXPIRE_HOURS)

def get_refresh_token_expiry() -> datetime:
    """
    Get expiration time for password reset token (24 hours from now)
    """

    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

def get_token_expiry(token_type: TokenType) -> datetime:
    """
    Flexible function for getting the expiration date of any token.
    Throws an exception if provided token_type is not supported.
    """
    
    match token_type:
        case TokenType.email_verification:
            return get_email_verification_expiry()
        case TokenType.password_reset:
            return get_password_reset_expiry()
        case TokenType.refresh:
            return get_refresh_token_expiry()
        case _:
            raise Exception(f"get_token_expiry does not support {token_type.value} tokens")


def is_token_expired(expiry_time: datetime) -> bool:
    """
    Check if a token has expired
    
    Args:
        expiry_time: The expiration datetime to check
    
    Returns:
        True if token is expired, False otherwise
    """

    return datetime.now(timezone.utc) > expiry_time