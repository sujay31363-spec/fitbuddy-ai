from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = ""

    gemini_plan_model: str = "gemini-3.1-pro-preview"

    gemini_tip_model: str = "gemini-3.8-flash"

    ai_enabled: bool = True

    admin_username: str = "admin"

    admin_password: str = "change-me"

    database_url: str = "sqlite:///./fitbuddy.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()