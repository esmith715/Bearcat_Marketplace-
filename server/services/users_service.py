from asyncpg import Connection, Record, UniqueViolationError
from typing import List, Optional
from uuid import UUID

from server.schemas.user import User, UserCreate, UserUpdate
from server.utils.security import hash_password

#========#
# Create #
#========#
async def create_user(
    conn: Connection,
    user_data: UserCreate
) -> User:
    """
    Create a user. Hashes password before storing.
    Ensures email is authorized(@mail.uc.edu) and not associated with an existing account.
    """

    # Email must have uc domain
    if not user_data.email.lower().endswith('@mail.uc.edu'):
        raise ValueError("Email must be a valid @mail.uc.edu address")
    
    hashed_password = hash_password(user_data.password)
    print(hashed_password)

    query = """
        INSERT INTO users (email, username, password_hash, verification_token, role, is_email_verified, admin_approved)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, email, username, verification_token, role, is_email_verified, admin_approved, created_at, updated_at
    """

    try:
        record = await conn.fetchrow(
            query,
            user_data.email,
            user_data.username,
            hashed_password,
            user_data.verification_token,
            user_data.role.value,
            user_data.is_email_verified,
            user_data.admin_approved
        )

        if not record:
            raise ValueError("Failed to insert user into database")
        
        return User.model_validate(dict(record))
    
    except UniqueViolationError:
        raise ValueError("User with this email or username already exists")
    
    except Exception as e:
        print(f"Error in create_user service: {e}")
        raise ValueError(f"Could not create user: {e}")


#=====#
# Get #
#=====#
async def get_user_by_email(
    conn: Connection,
    email: str,
) -> Optional[User]:
    """
    Retrieve a user by email. Returns None if user not found
    """

    query = """
        SELECT id, email, username, password_hash, verification_token, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        WHERE email = $1
    """

    record = await conn.fetchrow(query, email)
    if record is None:
        raise ValueError("Email not found")
    
    return User.model_validate(dict(record))

async def get_user_by_username(
    conn: Connection,
    username: str
) -> Optional[User]:
    """
    Retrieve a user by username. Returns None if user not found
    """

    query = """
        SELECT id, email, username, password_hash, verification_token, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        WHERE username = $1
    """

    record = await conn.fetchrow(query, username)
    return User.model_validate(dict(record))

async def get_user_by_id(
    conn: Connection,
    user_id: UUID
) -> Optional[User]:
    """
    Retrieve a user by ID. Returns None if user not found
    """

    query = """
        SELECT id, email, username, password_hash, verification_token, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        WHERE id = $1
    """

    record = await conn.fetchrow(query, user_id)
    return User.model_validate(dict(record))

async def get_all_users(
    conn: Connection, 
    skip: int = 0, 
    limit: int = 100
) -> List[User]:
    """
    Retrieve a List of all users
    """

    query = """
        SELECT id, email, username, password_hash, verification_token, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        OFFSET $1 
        LIMIT $2
    """

    records = await conn.fetch(query, skip, limit)
    return [User.model_validate(dict(record)) for record in records]


#========#
# Update #
#========#
async def update_user(
    conn: Connection,
    user_id: UUID,
    user_update_data: UserUpdate 
) -> Optional[User]:
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

    if user_update_data.username is not None:
        update_fields.append(f"username = ${param_count}")
        update_values.appned(user_update_data.username)
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
        RETURNING id, email, username, password_hash, verification_token, role, is_email_verified, admin_approved, created_at, updated_at
    """

    try:
        record = await conn.fetchrow(query, *update_values, user_id)
        return User.model_validate(dict(record))
    
    except UniqueViolationError:
        raise ValueError("User with this email already exists")
    
    except Exception as e:
        print(f"Error updating user: {e}")
        raise ValueError(f"Could not update user: {e}")


#========#
# Delete #
#========#
async def delete_user(
    conn: Connection,
    user_id: UUID
) -> bool:
    """
    Delete a user. Returns True if exactly 1 user was deleted
    """

    result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)

    # Return true if exactly 1 row was deleted
    return result == "DELETE 1"