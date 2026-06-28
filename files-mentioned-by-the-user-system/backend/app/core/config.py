from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    project_name: str = Field(default="Chess LMS", alias="PROJECT_NAME")
    database_url: str = Field(
        default="postgresql+psycopg://chess_lms:change-me@postgres:5432/chess_lms",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    jwt_issuer: str = Field(default="chess-lms", alias="JWT_ISSUER")
    jwt_audience: str = Field(default="chess-lms-web", alias="JWT_AUDIENCE")
    jwt_private_key: str = Field(default="dev-only-private-key", alias="JWT_PRIVATE_KEY")
    access_token_ttl_seconds: int = Field(default=900, alias="ACCESS_TOKEN_TTL_SECONDS")
    refresh_token_ttl_days: int = Field(default=30, alias="REFRESH_TOKEN_TTL_DAYS")
    password_pepper: str = Field(default="dev-only-password-pepper", alias="PASSWORD_PEPPER")
    cors_allowed_origins_raw: str = Field(
        default="http://localhost:3000",
        alias="CORS_ALLOWED_ORIGINS",
    )

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins_raw.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
