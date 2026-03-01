from asyncpg import Connection, Record
from typing import List, Optional
from uuid import UUID

from server.schemas import listing as listing_schemas

#========#
# Create #
#========#
async def create_listing(
    listing_data: listing_schemas.ListingCreate, 
    created_by_user_id: UUID, 
    conn: Connection
) -> listing_schemas.Listing:
    """
    Create a listing. Returns None if listing failed to insert into db.
    """

    print(created_by_user_id)

    if listing_data.book_id is not None and not await conn.fetchval("SELECT EXISTS(SELECT 1 FROM books WHERE id = $1)", listing_data.book_id):
        raise ValueError("Book ID not found")
        
    if listing_data.course_id and not await conn.fetchval("SELECT EXISTS(SELECT 1 FROM courses WHERE id = $1)", listing_data.course_id):
        raise ValueError("Course ID not found")
        
    query = """
        INSERT INTO listings (
            type, status, title, description, price_cents, item_condition, created_by,
            book_id, course_id, isbn, measurements
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING id, type, status, title, description, price_cents, item_condition, created_by,
            created_at, updated_at, book_id, course_id, isbn, measurements, sold_at, sold_to
    """

    record = await conn.fetchrow(
        query,
        listing_data.type.value,
        listing_schemas.ListingStatus.active.value,
        listing_data.title,
        listing_data.description,
        listing_data.price_cents,
        listing_data.item_condition,
        created_by_user_id,
        listing_data.book_id,
        listing_data.course_id,
        listing_data.isbn,
        listing_data.measurements
    )

    return _record_to_listing_schema(record)


#=====#
# Get #
#=====#
async def get_listing_by_id(
    listing_id: UUID, 
    conn: Connection
) -> Optional[listing_schemas.Listing]:
    """
    Retrieve a listing by ID. Returns None if listing not found
    """

    query = """
        SELECT id, type, status, title, description, price_cents, item_condition, created_by,
            created_at, updated_at, book_id, course_id, isbn, measurements, sold_at, sold_to
        FROM listings
        WHERE id = $1
    """

    record = await conn.fetchrow(query, listing_id)
    return _record_to_listing_schema(record)

async def get_all_listings(
    conn: Connection,
    skip: int = 0,
    limit: int = 100,
    listing_type: Optional[listing_schemas.ListingType] = None,
    status: Optional[listing_schemas.ListingStatus] = None,
) -> List[listing_schemas.Listing]:
    """
    Retrieve a List of all listings
    """

    query = """
        SELECT id, type, status, title, description, price_cents, item_condition, created_by,
            created_at, updated_at, book_id, course_id, isbn, measurements, sold_at, sold_to
        FROM listings
    """

    conditions = []
    params = []
    param_count = 1

    if listing_type is not None:
        conditions.append(f"type = ${param_count}")
        params.append(listing_type.value)
        param_count += 1

    if status is not None:
        conditions.append(f"status = ${param_count}")
        params.append(status.value)
        param_count += 1

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += f" OFFSET ${param_count} LIMIT ${param_count + 1}"
    params.append(skip)
    params.append(limit)
        
    records = await conn.fetch(query, *params)
    return [_record_to_listing_schema(record) for record in records]


#========#
# Update #
#========#
async def update_listing(
    listing_id: UUID, 
    listing_update_data: listing_schemas.ListingUpdate, 
    conn: Connection
) -> Optional[listing_schemas.Listing]:
    """
    Update a listing. Values listed as None in listing_update_data are left untouched.
    """

    update_fields = []
    update_values = []
    param_count = 1

    # Update modified values only
    if listing_update_data.type is not None:
        update_fields.append(f"type = ${param_count}")
        update_values.append(listing_update_data.type.value)
        param_count += 1

    if listing_update_data.status is not None:
        update_fields.append(f"status = ${param_count}")
        update_values.append(listing_update_data.status.value)
        param_count += 1

    if listing_update_data.title is not None:
        update_fields.append(f"title = ${param_count}")
        update_values.append(listing_update_data.title)
        param_count += 1

    if listing_update_data.description is not None:
        update_fields.append(f"description = ${param_count}")
        update_values.append(listing_update_data.description)
        param_count += 1

    if listing_update_data.price_cents is not None:
        update_fields.append(f"price_cents = ${param_count}")
        update_values.append(listing_update_data.price_cents)
        param_count += 1

    if listing_update_data.item_condition is not None:
        update_fields.append(f"item_condition = ${param_count}")
        update_values.append(listing_update_data.item_condition)
        param_count += 1

    if listing_update_data.book_id is not None:
        if not await conn.fetchval("SELECT EXISTS(SELECT 1 FROM courses WHERE id = $1)", listing_update_data.book_id):
            raise ValueError("Book ID not found")
        
        update_fields.append(f"book_id = ${param_count}")
        update_values.append(listing_update_data.book_id)
        param_count += 1

    if listing_update_data.course_id is not None:
        if not await conn.fetchval("SELECT EXISTS(SELECT 1 FROM courses WHERE id = $1)", listing_update_data.course_id):
            raise ValueError("Course ID not found")
        
        update_fields.append(f"course_id = ${param_count}")
        update_values.append(listing_update_data.course_id)
        param_count += 1

    if listing_update_data.isbn is not None:
        update_fields.append(f"isbn = ${param_count}")
        update_values.append(listing_update_data.isbn)
        param_count += 1

    if listing_update_data.measurements is not None:
        update_fields.append(f"measurements = ${param_count}")
        update_values.append(listing_update_data.measurements)
        param_count += 1

    if listing_update_data.sold_at is not None:
        update_fields.append(f"sold_at = ${param_count}")
        update_values.append(listing_update_data.sold_at)
        param_count += 1
        
    if listing_update_data.sold_to is not None:
        if not await conn.fetchval("SELECT EXISTS(SELECT 1 FROM courses WHERE id = $1)", listing_update_data.sold_to):
            raise ValueError("sold_to User ID not found")
        
        update_fields.append(f"sold_to = ${param_count}")
        update_values.append(listing_update_data.sold_to)
        param_count += 1

    if not update_fields:
        return await get_listing_by_id(listing_id, conn)
    
    update_fields_str = ", ".join(update_fields)

    query = f"""
        UPDATE listings
        SET {update_fields_str}, updated_at = NOW()
        WHERE id = ${param_count}
        RETURNING id, type, status, title, description, price_cents, item_condition, created_by,
            created_at, updated_at, book_id, course_id, isbn, measurements, sold_at, sold_to
    """

    record = await conn.fetchrow(query, *update_values, listing_id)
    return _record_to_listing_schema(record)


#========#
# Delete #
#========#
async def delete_listing(
    listing_id: UUID, 
    conn: Connection
) -> bool:
    """
    Delete a listing. Returns True if exactly 1 listing was deleted
    """

    result = await conn.execute("DELETE FROM listings WHERE id = $1", listing_id)

    # Return true if exactly 1 row was deleted
    return result == "DELETE 1"


#=======#
# Utils #
#=======#
# TODO: I think this function can be depricated but I'm too lazy right now.
# Will rework in the future.
def _record_to_listing_schema(record: Record) -> Optional[listing_schemas.Listing]:
    """
    Convert asyncpg.Record to a Pydantic Listing schema
    """

    if not record:
        return None

    return listing_schemas.Listing(
        id=record["id"],
        type=listing_schemas.ListingType(record["type"]),
        status=listing_schemas.ListingStatus(record["status"]),
        title=record["title"],
        description=record["description"],
        price_cents=record["price_cents"],
        item_condition=record["item_condition"],
        created_by=record["created_by"],
        created_at=record["created_at"],
        updated_at=record["updated_at"],
        book_id=record["book_id"],
        course_id=record["course_id"],
        isbn=record["isbn"],
        measurements=record["measurements"],
        sold_at=record["sold_at"],
        sold_to=record["sold_to"],
    )