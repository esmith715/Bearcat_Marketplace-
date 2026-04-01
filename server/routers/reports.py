from pydantic import BaseModel
from uuid import UUID

from fastapi import APIRouter, Depends
from asyncpg import Connection
from server.db.database import get_connection

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

#========#
# Schemas #
#========#
class ReportCreate(BaseModel):  
    listing_id: UUID
    reporter_id: UUID
    reason: str

class ReportUpdate(BaseModel):
    status: str
    resolution_notes: str | None = None
    reviewed_by: UUID


#========#
#  Post  #
#========#
@router.post("/")
async def create_report(report: ReportCreate, conn: Connection = Depends(get_connection)):
    await conn.execute(
            """
            INSERT INTO listing_reports (listing_id, reporter_id, reason)
            VALUES ($1, $2, $3)
            """,
            report.listing_id, report.reporter_id, report.reason
        )
    return {"status": "success", "message": "Report created successfully"}

#========#
#  Get   #
#========#
@router.get("/")
async def get_reports(conn: Connection = Depends(get_connection)):
    rows = await conn.fetch(
            """
            SELECT 
                r.id as report_id, r.listing_id, r.reporter_id, r.reason, r.status as report_status, 
                r.created_at as report_created_at, r.reviewed_at, r.reviewed_by, r.resolution_notes,
                l.title as listing_title, l.description as listing_description, l.status as listing_status
            FROM listing_reports r
            JOIN listings l ON r.listing_id = l.id
            ORDER BY r.created_at DESC
            """
        )
    return {"status": "success", "reports": [dict(row) for row in rows]}

#========#
#  Patch #
#========#
@router.patch("/{report_id}")
async def update_report(report_id: UUID, update: ReportUpdate, conn: Connection = Depends(get_connection)):
    async with conn.transaction():
            await conn.execute(
                """
                UPDATE listing_reports
                SET status = $1, resolution_notes = $2, reviewed_at = NOW(), reviewed_by = $3
                WHERE id = $4
                """,
                update.status, update.resolution_notes, update.reviewed_by, report_id
            )
            if update.status == "resolved":
                await conn.execute(
                    """
                    UPDATE listings
                    SET status = 'inactive'
                    WHERE id = (SELECT listing_id FROM listing_reports WHERE id = $1)
                    """,
                    report_id
                )   
    return {"status": "success", "message": "Report updated successfully"}

#========#
# Delete #
#========#
@router.delete("/{report_id}")
async def delete_report(report_id: UUID, conn: Connection = Depends(get_connection)):
    await conn.execute(
            """
            DELETE FROM listing_reports
            WHERE id = $1
            """,
            (report_id,)
        )
    return {"status": "success", "message": "Report deleted successfully"}  