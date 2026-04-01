import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from server.db.database import get_connection
from server.dependencies import get_current_user
from server.schemas.auth import TokenResponse, RefreshTokenRequest, TokenType, UserLogin, UserRegister
from server.schemas.user import UserInDB, UserResponse
from server.services import users_service, emailing_service, tokens_service
from server.utils.security import verify_password
from server.utils.tokens import create_access_token, create_refresh_token, decode_token, generate_verification_token


router = APIRouter(prefix="/auth", tags=["auth"])


#======#
# Post #
#======#
@router.post("/register", response_model=UserResponse)
async def register(
    registration_info: UserRegister,
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Register a new user.
    Ensures email is unique and hashes the password.
    Enforces UC email domain check.
    """

    try:
        user = await users_service.register_user(conn, registration_info)
        return user.to_response()
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
        )


@router.post("/send-verification-email")
async def send_verification_email(
    email: str,
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Sends verification email to provided email address
    """

    try:
        user = await users_service.get_user_by_email(conn, email)

        email_verification_token = generate_verification_token()
        await tokens_service.store_token(conn, user, TokenType.email_verification, email_verification_token)

        await emailing_service.send_verification_email(email, email_verification_token)
        return {"message": "Email sent successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    
    except Exception as e:
        print(f"Error sending verification email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )


@router.post("/verify-email")
async def verify_email(
    token: str,
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Verifies if token exists in database and updates the user's is_email_verified property accordingly
    """

    try:
        await users_service.verify_email(conn, token)
        return {"message": "Email verified successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    
    except Exception as e:
        print(f"Error verifying email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )


@router.post("/request-password-reset")
async def request_password_reset(
    email: str,
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Sends an email with password reset link to provided email address
    """

    try:
        user = await users_service.get_user_by_email(conn, email)

        password_reset_token = generate_verification_token()
        await tokens_service.store_token(conn, user, TokenType.password_reset, password_reset_token)

        await emailing_service.send_password_reset_email(email, password_reset_token)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset link"
        )


@router.post("/reset-password")
async def reset_password(
    password_reset_token: str,
    new_password: str,
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Updates database with new password if provided token is not expired
    """

    try:
        await users_service.reset_password(conn, password_reset_token, new_password)
        return {"message": "Password reset successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        print(f"Error resetting password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_info: UserLogin,
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Login user and return access and refresh tokens
    """

    try:
        # Figure out if an email or username was entered and query appropriately
        if '@' in login_info.email_or_username:
            user = await users_service.get_user_by_email(conn, login_info.email_or_username)

        else:
            user = await users_service.get_user_by_username(conn, login_info.email_or_username)

        if not verify_password(login_info.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        access_token = create_access_token(data={"sub" : str(user.id)})
        refresh_token = create_refresh_token(data={"sub" : str(user.id)})

        async with conn.transaction():
            # Clear old refresh tokens for this user so only one is valid at a time
            await tokens_service.delete_old_tokens(conn, user, TokenType.refresh)

            # Store the new refresh token in the DB
            await tokens_service.store_token(conn, user, TokenType.refresh, refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token, 
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
    except Exception as e:
        print(f"Error logging in: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Use a refresh token to get a new access token
    """

    try:
        token_data = decode_token(request.refresh_token, TokenType.refresh)

        user = await users_service.get_user_by_id(conn, token_data.id)
        access_token = create_access_token({"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,
            token_type="bearer"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
    except Exception as e:
        print(f"Error refreshing access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh access token"
        )


#=====#
# Get #
#=====#
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """
    Get the currently logged in user
    """

    return current_user.to_response()
