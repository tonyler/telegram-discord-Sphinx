from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    CSV_DATA_DIR: str = "data"
    SECRET_KEY: str = "default-secret-key-change-in-production"

    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    DISCORD_REDIRECT_URI: str

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_USERNAME: str

    BASE_URL: str = "http://localhost:8000"
    ENVIRONMENT: str = "development"

    # Google Sheets Configuration
    GOOGLE_SHEETS_ENABLED: bool = False
    GOOGLE_SHEETS_ID: str = ""
    GOOGLE_SERVICE_ACCOUNT_FILE: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
