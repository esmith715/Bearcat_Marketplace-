from asyncpg import Connection, Record, UniqueViolationError
import bcrypt # NOTE: May want to look into other libraries. For now, using this for simplicity.
from typing import List, Optional
from uuid import UUID

from server.schemas import user as user_schemas

#========#
# Create #
#========#
async def create_user(user_data: user_schemas.UserCreate, conn: Connection) -> user_schemas.User:
    """
    Create a user. Hashes password before storing.
    Ensures email is authorized(@mail.uc.edu) and not associated with an existing account.
    """

    # Email must have uc domain
    if not user_data.email.lower().endswith('@mail.uc.edu'):
        raise ValueError("Email must be a valid @mail.uc.edu address")
    
    hashed_password = _hash_password(user_data.password)

    query = """
        INSERT INTO users (email, password_hash, role, is_email_verified, admin_approved)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, email, role, is_email_verified, admin_approved, created_at, updated_at
    """

    try:
        record = await conn.fetchrow(
            query,
            user_data.email,
            hashed_password,
            user_data.role.value,
            user_data.is_email_verified,
            user_data.admin_approved
        )

        if not record:
            raise ValueError("Failed to insert user into database")
        
        # Converts the asyncpg Record to a Pydantic User model.
        # Since the User schema does not have a hashed_password field, 
        # it will automatically be excluded from the returned model.
        return _record_to_user_schema(record)
    
    except UniqueViolationError:
        raise ValueError("User with this email already exists")
    
    except Exception as e:
        print(f"Error in create_user service: {e}")
        raise ValueError(f"Could not create user: {e}")


#=====#
# Get #
#=====#
async def get_user_by_email(
    email: str, 
    conn: Connection
) -> Optional[user_schemas.User]:
    """
    Retrieve a user by email. Returns None if user not found
    """

    query = """
        SELECT id, email, password_hash, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        WHERE email = $1
    """

    record = await conn.fetchrow(query, email)
    return _record_to_user_schema(record)

async def get_user_by_id(
    user_id: UUID, 
    conn: Connection
) -> Optional[user_schemas.User]:
    """
    Retrieve a user by ID. Returns None if user not found
    """

    query = """
        SELECT id, email, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        WHERE id = $1
    """

    record = await conn.fetchrow(query, user_id)
    return _record_to_user_schema(record)

async def get_all_users(
    conn: Connection, 
    skip: int = 0, 
    limit: int = 100
) -> List[user_schemas.User]:
    """
    Retrieve a List of all users
    """

    query = """
        SELECT id, email, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        OFFSET $1 
        LIMIT $2
    """

    records = await conn.fetch(query, skip, limit)
    return [_record_to_user_schema(record) for record in records]


#========#
# Update #
#========#
async def update_user(user_id: UUID, user_update_data: user_schemas.UserUpdate, conn: Connection) -> Optional[user_schemas.User]:
    """
    Update a user. Values listed as None in user_update_data are left untouched.
    Ensures email is authorized(@mail.uc.edu) and not associated with an existing account.
    """

    # Email must have uc domain
    if user_update_data.email is not None and not user_update_data.email.lower().endswith("@mail.uc.edu"):
        raise ValueError("Email must be a valid @mail.uc.edu address")
        
    update_fields = []
    update_values = []
    param_count = 1

    # Update modified values only
    if user_update_data.email is not None:
        update_fields.append(f"email = ${param_count}")
        update_values.append(user_update_data.email)
        param_count += 1

    if user_update_data.role is not None:
        update_fields.append(f"role = ${param_count}")
        update_values.append(user_update_data.role.value)
        param_count += 1

    if user_update_data.is_email_verified is not None:
        update_fields.append(f"is_email_verified = ${param_count}")
        update_values.append(user_update_data.is_email_verified)
        param_count += 1

    if user_update_data.admin_approved is not None:
        update_fields.append(f"admin_approved = ${param_count}")
        update_values.append(user_update_data.admin_approved)
        param_count += 1

    if not update_fields:
        return await get_user_by_id(user_id, conn)
    
    update_fields_str = ", ".join(update_fields)

    query = f"""
        UPDATE users
        SET {update_fields_str}, updated_at = NOW()
        WHERE id = ${param_count}
        RETURNING id, email, role, is_email_verified, admin_approved, created_at, updated_at
    """

    try:
        record = await conn.fetchrow(query, *update_values, user_id)
        return _record_to_user_schema(record)
    
    except UniqueViolationError:
        raise ValueError("User with this email already exists")
    
    except Exception as e:
        print(f"Error updating user: {e}")
        raise ValueError(f"Could not update user: {e}")


#========#
# Delete #
#========#
async def delete_user(user_id: UUID, conn: Connection) -> bool:
    """
    Delete a user. Returns True if exactly 1 user was deleted
    """

    result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)

    # Return true if exactly 1 row was deleted
    return result == "DELETE 1"


#=======#
# Utils #
#=======#
# TODO: I think this function can be depricated but I'm too lazy right now.
# Will rework in the future.
def _record_to_user_schema(record: Record) -> Optional[user_schemas.User]:
    """
    Convert asyncpg.Record to a Pydantic User schema
    """
    
    if not record:
        return None

    return user_schemas.User(
        id=record["id"],
        email=record["email"],
        role=record["role"],
        is_email_verified=record["is_email_verified"],
        admin_approved=record["admin_approved"],
        created_at=record["created_at"],
        updated_at=record["updated_at"],
        listings_created=[]
    )

# TODO: Below methods should probably be moved to different file designed for authentication utils
def _hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt
    """

    hashed_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against a hashed password
    """

    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())