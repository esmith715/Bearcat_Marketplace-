from fastapi import APIRouter, Depends, HTTPException
from asyncpg import Connection
from uuid import UUID

from services import listings_service
from db.database import get_connection

router = APIRouter()

@router.get("/{listing_id}")
async def get_listing(
    listing_id: UUID,
    conn: Connection = Depends(get_connection),
):
    listing = await listings_service.get_listing_by_id(listing_id, conn)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing
