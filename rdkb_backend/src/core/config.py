from functools import lru_cache
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CORSConfig(BaseModel):
    """CORS configuration."""
    allow_origins: List[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS origins")
    allow_credentials: bool = True
    allow_methods: List[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS methods")
    allow_headers: List[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS headers")


class AppSettings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_name: str = Field("RDKB Backend API", description="Application name for OpenAPI and logging")
    app_env: str = Field("development", description="Environment (development/staging/production)")
    app_debug: bool = Field(True, description="Enable debug mode")
    app_host: str = Field("0.0.0.0", description="Host to bind server")
    app_port: int = Field(8000, description="Port to bind server")

    secret_key: str = Field("change-this-in-production", description="Secret key for auth tokens")
    access_token_expire_minutes: int = Field(60, description="Token expiry in minutes")

    cors_allow_origins: str = Field("*", description="Comma-separated allowed origins for CORS")

    db_driver: str = Field("postgresql", description="Database driver (postgresql/mysql/sqlite)")
    db_host: str = Field("localhost", description="Database host")
    db_port: int = Field(5432, description="Database port")
    db_user: str = Field("rdkb_user", description="Database user")
    db_password: str = Field("rdkb_password", description="Database password")
    db_name: str = Field("rdkb", description="Database name")

    site_url: Optional[str] = Field(default="http://localhost:3000", description="Site URL for redirects/integrations")

    # PUBLIC_INTERFACE
    def database_url(self) -> str:
        """Return the SQLAlchemy-compatible database URL built from individual fields."""
        if self.db_driver == "sqlite":
            return f"sqlite:///{self.db_name}.db"
        return f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # PUBLIC_INTERFACE
    def cors(self) -> CORSConfig:
        """Build CORS config using csv origins."""
        origins = [o.strip() for o in self.cors_allow_origins.split(",")] if self.cors_allow_origins else ["*"]
        return CORSConfig(allow_origins=origins)


@lru_cache
# PUBLIC_INTERFACE
def get_settings() -> AppSettings:
    """Get cached application settings loaded from environment variables."""
    return AppSettings()
