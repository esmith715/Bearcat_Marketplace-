from passlib.context import CryptContext
import secrets
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    """

    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """
    Hash a password
    """

    return pwd_context.hash(password)

def generate_verification_token(length: int = 32) -> str:
    """
    Generate a random token for email verification
    """

    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))