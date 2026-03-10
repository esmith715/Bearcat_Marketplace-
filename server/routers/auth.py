import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from server.db.database import get_connection
from server.dependencies import get_current_user
from server.schemas.auth import Token, RefreshTokenRequest, TokenType, UserLogin
from server.schemas.user import User
from server.services import users_service
from server.utils.jwt import create_access_token, create_refresh_token, decode_token
from server.utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

#======#
# Post #
#======#
@router.post("/login", response_model=Token)
async def login(
    login_info: UserLogin,
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Login user and return access and refresh tokens
    """

    # Figure out if an email or username was entered and query appropriately
    if '@' in login_info.email_or_username:
        user = await users_service.get_user_by_email(conn, login_info.email_or_username)

    else:
        user = await users_service.get_user_by_username(conn, login_info.email_or_username)

    if user is None or not verify_password(login_info.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub" : str(user.id)})
    refresh_token = create_refresh_token(data={"sub" : str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token, 
        token_type="bearer"
    )

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: RefreshTokenRequest,
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Use a refresh token to get a new access token
    """

    token_data = decode_token(request.refresh_token, TokenType.refresh)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user = await users_service.get_user_by_id(conn, token_data.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token = create_access_token({"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=request.refresh_token,
        token_type="bearer"
    )


#=====#
# Get #
#=====#
@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get the currently logged in user
    """

    return current_user
