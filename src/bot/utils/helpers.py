"""Вспомогательные функции."""
import datetime


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором."""
    from src.utils.secrets import ADMIN_ID
    try:
        admin_id = int(ADMIN_ID)
        return user_id == admin_id
    except (ValueError, TypeError):
        return False


def current_week_parity() -> str:
    """Возвращает строку, описывающую чётность текущей учебной недели.

    Многие университеты считают первую учебную неделю как "нечётная",
    что часто противоположно чётности ISO-недели. Поэтому мы намеренно
    инвертируем обычную чётность ISO здесь.
    """
    iso_week = datetime.date.today().isocalendar()[1]
    # Инвертированная чётность: ISO чётная -> нечётная, ISO нечётная -> чётная
    return "нечётная" if iso_week % 2 == 0 else "чётная"


def highlight(text: str) -> str:
    """Обернуть текст в угловые кавычки для выделения."""
    return f"‹{text}›"
