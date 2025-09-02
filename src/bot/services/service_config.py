"""Конфигурация сервисов бота."""

# Настройки включения/выключения сервисов
ENABLE_DAILY_SCHEDULE_SERVICE = True   # Включить автоматическую отправку расписания на завтра
ENABLE_POLL_SERVICE = True              # Включить планировщик опросов
ENABLE_NOTIFICATION_SERVICE = True      # Включить сервис уведомлений

# Функции для проверки статуса сервисов
def is_daily_schedule_enabled():
    """Проверить, включен ли сервис ежедневной отправки расписания."""
    return ENABLE_DAILY_SCHEDULE_SERVICE

def is_poll_service_enabled():
    """Проверить, включен ли сервис опросов."""
    return ENABLE_POLL_SERVICE

def is_notification_service_enabled():
    """Проверить, включен ли сервис уведомлений."""
    return ENABLE_NOTIFICATION_SERVICE

def get_enabled_services():
    """Получить список включенных сервисов."""
    services = []
    if ENABLE_DAILY_SCHEDULE_SERVICE:
        services.append("DailyScheduleService")
    if ENABLE_POLL_SERVICE:
        services.append("PollScheduler")
    if ENABLE_NOTIFICATION_SERVICE:
        services.append("NotificationService")
    return services
