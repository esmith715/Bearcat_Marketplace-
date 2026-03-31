from pydantic import BaseModel
from uuid import UUID

from fastapi import APIRouter
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
async def create_report(report: ReportCreate):
    async with get_connection() as conn:
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
async def get_reports():
    async with get_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT * FROM listing_reports JOIN listings ON listing_reports.listing_id = listings.id
            """
        )
    return {"status": "success", "reports": [dict(row) for row in rows]}

#========#
#  Patch #
#========#
@router.patch("/{report_id}")
async def update_report(report_id: UUID, update: ReportUpdate):
    async with get_connection() as conn:
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
                    WHERE id = $1
                    """,
                    report_id
                )   
    return {"status": "success", "message": "Report updated successfully"}

#========#
# Delete #
#========#
@router.delete("/{report_id}")
async def delete_report(report_id: UUID):
    async with get_connection() as conn:
        await conn.execute(
            """
            DELETE FROM listing_reports
            WHERE id = $1
            """,
            (report_id,)
        )
    return {"status": "success", "message": "Report deleted successfully"}  