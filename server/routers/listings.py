from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from server.db.database import get_connection
from server.dependencies import get_current_user
from server.schemas.listing import Listing, ListingCreate, ListingUpdate, ListingType, ListingStatus
from server.schemas.user import User
from server.services import listings_service

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
    current_user: User = Depends(get_current_user)
):
    """
    Create a listing. Must be authenticated to create a listing.
    """
    
    try:
        listing = await listings_service.create_listing(conn, current_user.id, listing_data)
        return listing
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        print(f"Error creating listing: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create listing")


#=====#
# Get #
#=====#
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
):
    """
    Update an existing listing
    """
    
    try:
        updated_listing = await listings_service.update_listing(conn, listing_id, listing_update_data)
        if updated_listing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details="Listing not found")
        
        return updated_listing
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        print(f"Error creating listing: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not Update listing")


#========#
# Delete #
#========#
@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: UUID,
    conn: Connection = Depends(get_connection),
):
    """
    Delete a listing
    """

    deleted = await listings_service.delete_listing(conn, listing_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    
    return
