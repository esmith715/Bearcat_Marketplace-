from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from server.db.database import get_connection
from server.dependencies import get_current_user, get_current_admin_user
from server.schemas.user import UserInDB, UserResponse, UserUpdateRequest, UserRole
from server.services import users_service


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


#=====#
# Get #
#=====#
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Retrieve a user by their ID
    """

    if user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view user")
    
    user = await users_service.get_user_by_id(conn, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user.to_response()


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    conn: Connection = Depends(get_connection),
    current_admin_user: UserInDB = Depends(get_current_admin_user)
):
    """
    Retrieve a list of all users.
    Only usable by admins.
    """

    users = await users_service.get_all_users(conn, skip, limit)
    return [user.to_response() for user in users]


#=======#
# Patch #
#=======#
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update_data: UserUpdateRequest,
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update an existing user
    """

    if user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update user")
    
    try:
        updated_user = await users_service.update_user(conn, user_id, user_update_data)
        if update_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return updated_user.to_response()
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update user")


#========#
# Delete #
#========#
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID, 
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a user
    """

    if user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete user")
    
    deleted = await users_service.delete_user(conn, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return
