from db import database

async def get_listing_by_id(listing_id: str):
    query = """
        SELECT id, title, price_cents
        FROM listings
        WHERE id = $1
    """
    row = await database.fetch_one(query, listing_id)

    if not row:
        return {"error": "Listing not found"}

    return {
        "id": row["id"],
        "title": row["title"],
        "price": row["price_cents"]
    }
