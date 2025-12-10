"""Загрузка настроек из окружения и .env через Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Настройки приложения"""

    bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    chat_id: str | None = Field(default=None, alias="TELEGRAM_CHAT_ID")

    model_config = SettingsConfigDict(
        populate_by_name=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


def load_settings() -> AppSettings:
    """Возвращает экземпляр настроек"""
    return AppSettings()

