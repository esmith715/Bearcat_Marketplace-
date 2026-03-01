from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from server.schemas import listing as listing_schemas
from server.db.database import get_connection
from server.services import listings_service

router = APIRouter(
    prefix="/listings",
    tags=["listings"],
)

@router.post("/", response_model=listing_schemas.Listing, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_data: listing_schemas.ListingCreate, 
    conn: Connection = Depends(get_connection),
):
    """
    Create a listing
    """
    
    # TODO: Once we have authentication implemented, use current users ID to create listing.
    # For now, using a made up user ID.
    created_by_user_id = UUID("c4204b75-3ee8-4063-abb7-a9c16fcd265b")

    try:
        listing = await listings_service.create_listing(listing_data, created_by_user_id, conn)
        return listing
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        print(f"Error creating listing: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create listing")

@router.get("/{listing_id}", response_model=listing_schemas.Listing)
async def get_listing(
    listing_id: UUID,
    conn: Connection = Depends(get_connection),
):
    """
    Retrieve a listing
    """

    listing = await listings_service.get_listing_by_id(listing_id, conn)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    
    return listing

@router.get("/", response_model=List[listing_schemas.Listing])
async def get_all_listings(
    conn: Connection = Depends(get_connection),
    skip: int = 0,
    limit: int = 100,
    listing_type: Optional[listing_schemas.ListingType] = None,
    status: Optional[listing_schemas.ListingStatus] = None
):
    """
    Retrieve a list of all listings, with optional filtering
    """

    listings = await listings_service.get_all_listings(conn, skip, limit, listing_type, status)
    return listings

@router.patch("/{listing_id}", response_model=listing_schemas.Listing)
async def update_listing(
    listing_id: UUID,
    listing_update_data: listing_schemas.ListingUpdate,
    conn: Connection = Depends(get_connection),
):
    """
    Update an existing listing
    """
    
    try:
        updated_listing = await listings_service.update_listing(listing_id, listing_update_data, conn)
        if updated_listing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details="Listing not found")
        
        return updated_listing
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        print(f"Error creating listing: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not Update listing")
    
@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: UUID,
    conn: Connection = Depends(get_connection),
):
    """
    Delete a listing
    """

    deleted = await listings_service.delete_listing(listing_id, conn)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    
    return
