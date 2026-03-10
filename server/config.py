from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/bearcat-marketplace"

    SECRET_KEY: str = "4b6d0a20ea076bb451e1cf6b47857160614c105e0be19e1b3739501b583af342" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SMTP_SERVER: str = "mail.uc.edu"
    SMTP_PORT: int = 587
    SENDER_EMAIL: str = "myemail@mail.uc.edu"
    SENDER_PASSWORD: str = "Secret"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()