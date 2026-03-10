from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from server.db.database import get_connection
from server.schemas import user as user_schemas
from server.services import users_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

#======#
# Post #
#======#
@router.post("/", response_model=user_schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: user_schemas.UserCreate, 
    conn: Connection = Depends(get_connection)
):
    """
    Create a user. Ensures email is unique and hashes the password.
    Enforces UC email domain check.
    """

    try:
        user = await users_service.create_user(conn, user_data)
        return user
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user")


#=====#
# Get #
#=====#
@router.get("/{user_id}", response_model=user_schemas.User)
async def get_user(
    user_id: UUID,
    conn: Connection = Depends(get_connection),
):
    """
    Retrieve a user by their ID
    """

    # TODO: Only admins should be able to request user data?
    user = await users_service.get_user_by_id(conn, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

@router.get("/", response_model=List[user_schemas.User])
async def get_all_users(
    conn: Connection = Depends(get_connection),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve a list of all users
    """

    # TODO: Only admins should be able to request all user data?
    users = await users_service.get_all_users(conn, skip, limit)
    return users


#=======#
# Patch #
#=======#
@router.patch("/{user_id}", response_model=user_schemas.User)
async def update_user(
    user_id: UUID,
    user_update_data: user_schemas.UserUpdate,
    conn: Connection = Depends(get_connection),
):
    """
    Update an existing user
    """

    try:
        updated_user = await users_service.update_user(conn, user_id, user_update_data)
        if update_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return updated_user
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update user")


#========#
# Delete #
#========#
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, conn: Connection = Depends(get_connection)):
    """
    Delete a user
    """

    deleted = await users_service.delete_user(conn, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return
