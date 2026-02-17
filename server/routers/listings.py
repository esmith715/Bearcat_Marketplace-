from fastapi import APIRouter, Depends
from services import listings_service

router = APIRouter()

@router.get("/{listing_id}")
async def get_listing(listing_id: str):
    return await listings_service.get_listing_by_id(listing_id)
