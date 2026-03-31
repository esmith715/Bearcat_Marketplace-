from asyncpg import Connection, Record, UniqueViolationError
from typing import List, Optional
from uuid import UUID

from server.schemas.auth import UserRegister, TokenType
from server.schemas.user import UserUpdateRequest, UserInDB, UserRole
from server.services import tokens_service
from server.utils.tokens import generate_verification_token
from server.utils.security import hash_password


#==========#
# Register #
#==========#
async def register_user(
    conn: Connection,
    registration_info: UserRegister
) -> UserInDB:
    """
    Registers a user in the database. 
    Hashes password before storing.
    Ensures email is authorized(@mail.uc.edu) and not associated with an existing account.
    """

    # Email must have uc domain
    # if not registration_info.email.lower().endswith('@mail.uc.edu'):
    #     raise ValueError("Email must be a valid @mail.uc.edu address")
    
    hashed_password = hash_password(registration_info.password)
    role = UserRole.student.value

    query = """
        INSERT INTO users (email, username, password_hash, role, is_email_verified, admin_approved)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, email, username, password_hash, role, is_email_verified, admin_approved, created_at, updated_at
    """

    try:
        # Create User
        user_record = await conn.fetchrow(
            query,
            registration_info.email,
            registration_info.username,
            hashed_password,
            role,
            False, # Email not verified yet
            False # Assume not admin approved
        )

        if not user_record:
            raise ValueError("Failed to insert user into database")
        
        return UserInDB.model_validate(dict(user_record))
    
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
) -> UserInDB:
    """
    Retrieve a user by email. Returns None if user not found
    """

    query = """
        SELECT id, email, username, password_hash, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        WHERE email = $1
    """

    record = await conn.fetchrow(query, email)
    if record is None:
        raise ValueError("Email not found")
    
    return UserInDB.model_validate(dict(record))


async def get_user_by_username(
    conn: Connection,
    username: str
) -> UserInDB:
    """
    Retrieve a user by username. Returns None if user not found
    """

    query = """
        SELECT id, email, username, password_hash, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        WHERE username = $1
    """

    record = await conn.fetchrow(query, username)
    if record is None:
        raise ValueError("Username not found")
    
    return UserInDB.model_validate(dict(record))


async def get_user_by_id(
    conn: Connection,
    user_id: UUID
) -> UserInDB:
    """
    Retrieve a user by ID. Returns None if user not found
    """

    query = """
        SELECT id, email, username, password_hash, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        WHERE id = $1
    """

    record = await conn.fetchrow(query, user_id)
    if record is None:
        raise ValueError("User ID not found")
    
    return UserInDB.model_validate(dict(record))


async def get_all_users(
    conn: Connection, 
    skip: int = 0, 
    limit: int = 100
) -> List[UserInDB]:
    """
    Retrieve a List of all users
    """

    query = """
        SELECT id, email, username, password_hash, role, is_email_verified, admin_approved, created_at, updated_at
        FROM users
        OFFSET $1 
        LIMIT $2
    """

    records = await conn.fetch(query, skip, limit)
    return [UserInDB.model_validate(dict(record)) for record in records]


#========#
# Update #
#========#
async def update_user(
    conn: Connection,
    user_id: UUID,
    user_update_data: UserUpdateRequest
) -> Optional[UserInDB]:
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
        update_values.append(user_update_data.username)
        param_count += 1

    if not update_fields:
        return await get_user_by_id(conn, user_id)
    
    update_fields_str = ", ".join(update_fields)

    query = f"""
        UPDATE users
        SET {update_fields_str}, updated_at = NOW()
        WHERE id = ${param_count}
        RETURNING id, email, username, password_hash, role, is_email_verified, admin_approved, created_at, updated_at
    """

    try:
        record = await conn.fetchrow(query, *update_values, user_id)
        return UserInDB.model_validate(dict(record))
    
    except UniqueViolationError:
        raise ValueError("User with this email already exists")
    
    except Exception as e:
        print(f"Error updating user: {e}")
        raise ValueError(f"Could not update user: {e}")


async def verify_email(
    conn: Connection,
    token: str
):
    """
    Updates value of is_email_verified in database if token is not expired
    """

    valid_token_record = await tokens_service.get_valid_token(conn, TokenType.email_verification, token)

    await conn.execute(
        """
        UPDATE tokens
        SET used_at = NOW()
        WHERE id = $1
        """,
        valid_token_record.id
    )

    await conn.execute(
        """
        UPDATE users
        SET is_email_verified = TRUE, updated_at = NOW()
        WHERE id = $1
        RETURNING id, email, username, password_hash, role, is_email_verified, admin_approved, refresh_token, refresh_token_expiration_date, created_at, updated_at
        """,
        valid_token_record.user_id
    )
    

async def reset_password(
    conn: Connection,
    password_reset_token: str,
    new_password: str
):
    """
    Updates database with new password if provided token is not expired.
    Hashed password before storing.
    """

    valid_token_record = await tokens_service.get_valid_token(conn, TokenType.password_reset, password_reset_token)

    if valid_token_record is None:
        pass

    new_password_hash = hash_password(new_password)

    await conn.execute(
        """
        UPDATE tokens
        SET used_at = NOW()
        WHERE id = $1
        """,
        valid_token_record.id
    )

    updated_user_record = await conn.fetchrow(
        """
        UPDATE users
        SET password_hash = $1, updated_at = NOW()
        WHERE id = $2
        RETURNING id, email, username, password_hash, role, is_email_verified, admin_approved, refresh_token, refresh_token_expiration_date, created_at, updated_at
        """,
        new_password_hash,
        valid_token_record.user_id
    )


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