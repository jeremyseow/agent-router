from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "agent-router"
    
    # DB Configuration
    postgres_user: str = "agent_user"
    postgres_password: str = "agent_pass"
    postgres_db: str = "agent_router"
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_ssl_enabled: str = "disable"
    
    # Gemini
    gemini_api_key: str = ""
    
    # Logfire
    logfire_token: Optional[str] = None

    @property
    def is_ssl_enabled(self) -> bool | None:
        """Returns True if SSL is enabled, None if disabled (for asyncpg)."""
        val = self.postgres_ssl_enabled.lower()
        if val in ("disable", "false", "0", "none"):
            return None
        return True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def db_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings()
