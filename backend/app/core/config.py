from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "SupplyIQ"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/supplyiq"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        import re
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        url = url.replace("sslmode=require", "ssl=require")
        # asyncpg does not support channel_binding
        url = re.sub(r'[&?]channel_binding=[^&]*', '', url)
        # If the parameter list started with ?channel_binding and had more params with &, fix first & to ?
        if "?" not in url and "&" in url:
            url = url.replace("&", "?", 1)
        return url

    @property
    def SYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    # JWT
    SECRET_KEY: str = "supersecret-change-this-in-production-must-be-32-chars-minimum"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # AI (future)
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""


settings = Settings()
