from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from server.db.database import get_connection
from server.dependencies import get_current_user
from server.schemas.listing import Listing, ListingCreate, ListingUpdate, ListingType, ListingStatus
from server.schemas.user import UserInDB, UserRole
from server.schemas.notification import NotificationCreate, NotificationType
from server.services import listings_service, favorites_service, notifications_service


router = APIRouter(
    prefix="/listings",
    tags=["listings"],
)


#======#
# Post #
#======#
@router.post("/", response_model=Listing, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_data: ListingCreate, 
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a listing. Must be authenticated to create a listing.
    """
  
    try:
        listing = await listings_service.create_listing(conn, listing_data, current_user.id)
        return listing
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        print(f"Error creating listing: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create listing")


#=====#
# Get #
#=====#
@router.get("/me", response_model=List[Listing])
async def get_my_listings(
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve listings created by the currently authenticated user.
    """

    try:
        listings = await listings_service.get_listings_by_user_id(
            conn,
            current_user.id,
            skip,
            limit
        )
        return listings

    except Exception as e:
        print(f"Error retrieving current user's listings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve your listings"
        )

@router.get("/{listing_id}", response_model=Listing)
async def get_listing(
    listing_id: UUID,
    conn: Connection = Depends(get_connection),
):
    """
    Retrieve a listing
    """

    listing = await listings_service.get_listing_by_id(conn, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    
    return listing


@router.get("/", response_model=List[Listing])
async def get_all_listings(
    conn: Connection = Depends(get_connection),
    skip: int = 0,
    limit: int = 100,
    listing_type: Optional[ListingType] = None,
    status: Optional[ListingStatus] = None
):
    """
    Retrieve a list of all listings, with optional filtering
    """

    listings = await listings_service.get_all_listings(conn, skip, limit, listing_type, status)
    return listings


#=======#
# Patch #
#=======#
@router.patch("/{listing_id}", response_model=Listing)
async def update_listing(
    listing_id: UUID,
    listing_update_data: ListingUpdate,
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update an existing listing.
    Send notification to anyone who has the listing bookmarked.
    """
    
    try:
        listing = await listings_service.get_listing_by_id(conn, listing_id)
        if listing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
        
        if listing.created_by != current_user.id and current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Only the creator of a listing can update it"
            )
        
        updated_listing = await listings_service.update_listing(conn, listing_id, listing_update_data)

        # Send notifications
        users_to_notify = await favorites_service.get_users_who_favorited_listing(conn, updated_listing.id)
        for user in users_to_notify:
            notification_data = NotificationCreate(
                user_id=user.id,
                type=NotificationType.listing_updated,
                listing_id=updated_listing.id
            )

            await notifications_service.create_notification(conn, notification_data)

        return updated_listing
    
    except HTTPException:
        raise
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        print(f"Error updating listing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update listing"
        )

#========#
# Delete #
#========#
@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: UUID,
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a listing
    """
    try:
        listing = await listings_service.get_listing_by_id(conn, listing_id)
        if listing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

        if listing.created_by != current_user.id and current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Only the creator of a listing can delete it"
            )

        deleted = await listings_service.delete_listing(conn, listing_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not deleted")

        return

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error deleting listing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete listing"
        )

