"""Утилита для планирования ежедневной отправки расписания."""

# Настройки времени отправки расписания на следующий день
DAILY_SCHEDULE_HOUR = 18    # Час отправки (0-23, по умолчанию 18:00)
DAILY_SCHEDULE_MINUTE = 0   # Минута отправки (0-59)

def get_daily_schedule_time():
    """Получить время для ежедневной отправки расписания."""
    return DAILY_SCHEDULE_HOUR, DAILY_SCHEDULE_MINUTE

def get_daily_schedule_time_str():
    """Получить время для ежедневной отправки расписания в виде строки."""
    return f"{DAILY_SCHEDULE_HOUR:02d}:{DAILY_SCHEDULE_MINUTE:02d}"
