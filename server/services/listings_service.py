from asyncpg import Connection
from uuid import UUID

async def get_listing_by_id(listing_id: UUID, conn: Connection):
    query = """
        SELECT id, title, price_cents
        FROM listings
        WHERE id = $1
    """
    row = await conn.fetchrow(query, listing_id)

    if row is None:
        return None

    return {
        "id": str(row["id"]),
        "title": row["title"],
        "price_cents": row["price_cents"],
    }

async def get_all_listings(conn: Connection):
    query = """
        SELECT id, title, description, price_cents
        FROM listings
    """
    rows = await conn.fetch(query)

    return [
        {
            "id": str(row["id"]),
            "title": row["title"],
            "description": row["description"],
            "price_cents": row["price_cents"],
        }
        for row in rows
    ]