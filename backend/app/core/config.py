from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)


@dataclass(frozen=True)
class Settings:
    auth_secret: str = os.getenv("AUTH_SECRET", "dev-only-change-this-secret")
    access_token_expires_seconds: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_SECONDS", "1800"))
    refresh_token_expires_seconds: int = int(os.getenv("REFRESH_TOKEN_EXPIRES_SECONDS", "604800"))
    password_hash_iterations: int = int(os.getenv("PASSWORD_HASH_ITERATIONS", "120000"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/nextstep",
    )


settings = Settings()
