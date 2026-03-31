from asyncpg import Connection
from typing import Optional

from server.schemas.auth import TokenInDB, TokenType
from server.schemas.user import UserInDB
from server.utils.tokens import is_token_expired, get_token_expiry


async def store_token(
    conn: Connection,
    user: UserInDB,
    token_type: TokenType,
    token: str
):
    """
    Stores the provided token in the database
    """

    await conn.execute(
        """
        INSERT INTO tokens (
            user_id, token, type, expires_at 
        )
        VALUES ($1, $2, $3, $4)
        """,
        user.id,
        token,
        token_type.value,
        get_token_expiry(token_type)
    )


async def get_valid_token(
    conn: Connection,
    token_type: TokenType,
    token: str
) -> Optional[TokenInDB]:
    """
    Looks up a token from the tokens table by value and type.
    Returns None if not found, already used, or expired.
    """

    token_record = await conn.fetchrow(
        """
        SELECT id, user_id, token, type, expires_at, created_at, used_at
        FROM tokens
        WHERE token = $1
          AND type = $2
          AND used_at IS NULL
        """,
        token,
        token_type.value
    )

    if not token_record:
        return None

    token_record = TokenInDB.model_validate(dict(token_record))

    if is_token_expired(token_record.expires_at):
        return None

    return token_record

async def delete_old_tokens(
    conn: Connection,
    user: UserInDB,
    token_type: TokenType
) -> None:
    """Delete all existing refresh tokens for a user before issuing a new one."""

    query = """
        DELETE FROM tokens
        WHERE user_id = $1 
        AND type = $2
    """

    await conn.execute(query, user.id, token_type.value)