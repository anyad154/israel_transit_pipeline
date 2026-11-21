from pathlib import Path
from typing import Literal
from urllib.parse import quote

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables and .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    postgres_user: str = "transit"
    postgres_db: str = "transit"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_password: SecretStr = Field(min_length=1)  # no default: must come from the environment

    # Storage
    data_dir: Path = Path("./data")

    # Sources
    gtfs_url: str
    stride_base_url: str

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @property
    def postgres_dsn(self) -> str:
        """Connection string, e.g. postgresql://user:pass@host:5432/db"""
        encoded_password = quote(self.postgres_password.get_secret_value(), safe="")
        encoded_username = quote(self.postgres_user, safe="")
        return (
            f"postgresql://{encoded_username}:{encoded_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def get_settings() -> Settings:
    return Settings()
