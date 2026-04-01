from fastapi import APIRouter, Depends
from asyncpg import Connection
from server.db.database import get_connection

router = APIRouter(
    prefix="/search",
    tags=["search"],
)

#========#
#  Get   #
#========#
@router.get("/")
async def search(query: str, conn: Connection = Depends(get_connection)):
    rows = await conn.fetch(
        """
        SELECT id, title, description, price_cents, type, 
        similarity(title, $1) as similarity 
        FROM listings 
        WHERE (title % $1 OR description % $1)
        AND status = 'active'
        ORDER BY similarity DESC
        LIMIT 25
        """,
        query
    )
    return {"status": "success", "results": [dict(row) for row in rows]}   

  