# server/routers/favorites.py
from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from server.db.database import get_connection
from server.dependencies import get_current_user
from server.schemas.listing import Listing
from server.schemas.user import UserInDB
from server.services import favorites_service, listings_service

router = APIRouter(
    prefix="/favorites",
    tags=["favorites"],
)


@router.post("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def favorite_listing(
    listing_id: UUID,
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    listing = await listings_service.get_listing_by_id(conn, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    await favorites_service.add_favorite(conn, current_user.id, listing_id)
    return


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unfavorite_listing(
    listing_id: UUID,
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    await favorites_service.remove_favorite(conn, current_user.id, listing_id)
    return


@router.get("/me", response_model=List[Listing])
async def get_my_favorites(
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    return await favorites_service.get_favorite_listings_by_user_id(conn, current_user.id)


@router.get("/me/ids", response_model=List[UUID])
async def get_my_favorite_ids(
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    return await favorites_service.get_favorite_listing_ids_by_user_id(conn, current_user.id)
