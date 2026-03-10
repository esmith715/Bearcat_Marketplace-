from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg

from server.utils.jwt import decode_token

from server.services import users_service
from server.schemas.user import User, UserRole
from server.db.database import get_connection

security = HTTPBearer()

async def get_current_user(
    conn: asyncpg.Connection = Depends(get_connection),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to extract and validate the current authenticated user from JWT token.
    Use this in any route that requires authentication.
    """

    token = credentials.credentials
    token_data = decode_token(token, "access")
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    current_user = await users_service.get_user_by_id(conn, token_data.id)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user is an admin.
    Use this in any route that should be restricted to admins.
    """

    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return current_user
