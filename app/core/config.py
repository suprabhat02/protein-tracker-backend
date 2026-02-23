from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = Field(default="Protein SaaS API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    frontend_origin: str = Field(
        default="http://localhost:5173", alias="FRONTEND_ORIGIN"
    )
    frontend_origins: str | None = Field(default=None, alias="FRONTEND_ORIGINS")

    mongodb_uri: str = Field(alias="MONGODB_URI")
    mongodb_db: str = Field(alias="MONGODB_DB")

    jwt_access_secret: str = Field(alias="JWT_ACCESS_SECRET")
    jwt_refresh_secret: str = Field(alias="JWT_REFRESH_SECRET")
    jwt_access_ttl_minutes: int = Field(default=15, alias="JWT_ACCESS_TTL_MINUTES")
    jwt_refresh_ttl_days: int = Field(default=30, alias="JWT_REFRESH_TTL_DAYS")

    hashids_salt: str = Field(alias="HASHIDS_SALT")
    google_client_id: str = Field(alias="GOOGLE_CLIENT_ID")

    cookie_domain: str = Field(default="localhost", alias="COOKIE_DOMAIN")
    cookie_secure: bool = Field(default=False, alias="COOKIE_SECURE")
    csrf_cookie_name: str = Field(default="csrf_token", alias="CSRF_COOKIE_NAME")
    access_cookie_name: str = Field(default="access_token", alias="ACCESS_COOKIE_NAME")
    refresh_cookie_name: str = Field(
        default="refresh_token", alias="REFRESH_COOKIE_NAME"
    )

    rate_limit_per_minute: int = Field(default=120, alias="RATE_LIMIT_PER_MINUTE")
    max_payload_bytes: int = Field(default=1_048_576, alias="MAX_PAYLOAD_BYTES")

    @property
    def cors_allow_origins(self) -> list[str]:
        origins: list[str] = []
        if self.frontend_origins:
            origins.extend(
                [item.strip() for item in self.frontend_origins.split(",") if item.strip()]
            )

        if self.frontend_origin.strip():
            origins.append(self.frontend_origin.strip())

        unique_origins: list[str] = []
        for origin in origins:
            if origin not in unique_origins:
                unique_origins.append(origin)
        return unique_origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
