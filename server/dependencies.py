from fastapi import Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg

from server.utils.tokens import decode_token

from server.services import users_service
from server.schemas.user import UserInDB, UserRole
from server.schemas.auth import TokenType
from server.db.database import get_connection

security = HTTPBearer()

async def get_current_user(
    conn: asyncpg.Connection = Depends(get_connection),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInDB:
    """
    Dependency to extract and validate the current authenticated user from JWT token.
    Use this in any route that requires authentication.
    """

    token = credentials.credentials
    token_data = decode_token(token, TokenType.access)
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
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
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


#============#
# Websockets #
#============#
async def get_current_user_ws(
    websocket: WebSocket,
    token: str = Query(...),
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    WebSocket-specific auth dependency.
    Validates JWT from query param and returns the current user.
    """
    await websocket.accept() 
    print(f"WebSocket accepted, validating token...")

    try:
        payload = decode_token(token, TokenType.access)
        user_id = payload.id

        if user_id is None:
            await websocket.close(code=1008)
            return None

        user = await users_service.get_user_by_id(conn, user_id)
        print(f"Auth passed for user: {user_id}")

        if user is None:
            await websocket.close(code=1008)
            return None

        return user

    except Exception as e:
        print(f"WebSocket auth failed: {e}")
        await websocket.close(code=1008)
        return None
