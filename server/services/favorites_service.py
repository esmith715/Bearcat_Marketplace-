# server/services/favorites_service.py
from asyncpg import Connection
from typing import List
from uuid import UUID

from server.schemas.listing import Listing
from server.schemas.user import UserInDB


async def add_favorite(
    conn: Connection,
    user_id: UUID,
    listing_id: UUID
) -> None:
    await conn.execute(
        """
        INSERT INTO favorite_listings (user_id, listing_id)
        VALUES ($1, $2)
        ON CONFLICT (user_id, listing_id) DO NOTHING
        """,
        user_id,
        listing_id
    )


async def remove_favorite(
    conn: Connection,
    user_id: UUID,
    listing_id: UUID
) -> bool:
    result = await conn.execute(
        """
        DELETE FROM favorite_listings
        WHERE user_id = $1 AND listing_id = $2
        """,
        user_id,
        listing_id
    )
    return result == "DELETE 1"


async def get_favorite_listings_by_user_id(
    conn: Connection,
    user_id: UUID
) -> List[Listing]:
    records = await conn.fetch(
        """
        SELECT l.id, l.type, l.status, l.title, l.description, l.price_cents,
               l.item_condition, l.created_by, l.created_at, l.updated_at,
               l.book_id, l.course_id, l.isbn, l.measurements, l.sold_at, l.sold_to
        FROM favorite_listings f
        JOIN listings l ON l.id = f.listing_id
        WHERE f.user_id = $1
        ORDER BY f.created_at DESC
        """,
        user_id
    )

    return [Listing.model_validate(dict(record)) for record in records]


async def get_favorite_listing_ids_by_user_id(
    conn: Connection,
    user_id: UUID
) -> List[UUID]:
    records = await conn.fetch(
        """
        SELECT listing_id
        FROM favorite_listings
        WHERE user_id = $1
        ORDER BY created_at DESC
        """,
        user_id
    )

    return [record["listing_id"] for record in records]


async def get_users_who_favorited_listing(
    conn: Connection,
    listing_id: UUID
) -> List[UserInDB]:
    """
    Get all the users who currently have the provided listing_id marked as favorite
    """

    user_records = await conn.fetch(
        """
        SELECT user_id
        FROM favorite_listings
        WHERE listing_id = $1
        """,
        listing_id
    )

    return [UserInDB.model_validate(dict(record)) for record in user_records]
