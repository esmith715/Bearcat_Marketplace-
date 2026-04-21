from fastapi import APIRouter, Depends, Query
from asyncpg import Connection
from typing import Optional
from server.db.database import get_connection

router = APIRouter(
    prefix="/search",
    tags=["search"],
)

#========#
#  Get   #
#========#
@router.get("/")
async def search(
    query: Optional[str] = Query(None),          # text search
    type: Optional[str] = Query(None),            # e.g. "book", "furniture", "misc"
    condition: Optional[str] = Query(None),       # e.g. "new", "like_new", "good", "fair"
    min_price: Optional[int] = Query(None),       # in cents, e.g. 500 = $5.00
    max_price: Optional[int] = Query(None),       # in cents, e.g. 10000 = $100.00
    sort: Optional[str] = Query("relevance"),     # "relevance" | "price_asc" | "price_desc" | "newest"
    conn: Connection = Depends(get_connection),
):
    """
    It does search stuff
    """

    conditions = ["status = 'active'"]
    args = []
    idx = 1  # tracks the current parameter number

    # Text search — only add if a query string was provided
    if query and query.strip():
        conditions.append(
            f"(title % ${idx} OR description % ${idx})"
        )
        args.append(query.strip())
        idx += 1

    # Category/type filter
    if type:
        conditions.append(f"type = ${idx}")
        args.append(type)
        idx += 1

    # Condition filter
    if condition:
        conditions.append(f"item_condition = ${idx}")
        args.append(condition)
        idx += 1

    # Price range filters
    if min_price is not None:
        conditions.append(f"price_cents >= ${idx}")
        args.append(min_price)
        idx += 1

    if max_price is not None:
        conditions.append(f"price_cents <= ${idx}")
        args.append(max_price)
        idx += 1

    # ── Build ORDER BY clause ─────────────────────────────────────────────
    # Only use similarity ranking if there's actually a text query.
    # Otherwise fall back to the chosen sort option.
    if query and query.strip() and sort == "relevance":
        order = f"similarity(title, ${idx}) DESC"
        args.append(query.strip())
        idx += 1
    elif sort == "price_asc":
        order = "price_cents ASC"
    elif sort == "price_desc":
        order = "price_cents DESC"
    else:  # "newest" or default fallback
        order = "created_at DESC"

    where_clause = " AND ".join(conditions)

    sql = f"""
        SELECT
            id, title, description, price_cents, type, item_condition, created_at,
            (
                SELECT image_path
                FROM listing_images
                WHERE listing_id = listings.id AND is_primary = true
                ORDER BY sort_order ASC, created_at ASC
                LIMIT 1
            ) AS image_url
        FROM listings
        WHERE {where_clause}
        ORDER BY {order}
        LIMIT 50
    """

    rows = await conn.fetch(sql, *args)
    return {"status": "success", "results": [dict(row) for row in rows]}   

  