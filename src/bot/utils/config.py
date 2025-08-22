"""Конфигурация бота."""
import os
import pathlib


def get_bot_token() -> str:
    """Получить токен Telegram бота."""
    from src.utils.secrets import TOKEN
    return TOKEN
