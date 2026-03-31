from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database
    # The connection string format should be changed in .env as needed:
    # "postgressql://username:password@localhost:5432/database-name"
    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/bearcat-marketplace"

    # JWT/Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email
    SMTP_SERVER: str = "mail.uc.edu"
    SMTP_PORT: int = 587
    SENDER_EMAIL: str
    SENDER_PASSWORD: str

    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EXPIRE_HOURS: int = 24

    RESEND_API_KEY: str
    FROM_EMAIL: str = "onboarding@resend.dev"

    FRONTEND_URL: str = "http://localhost:5173/"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()