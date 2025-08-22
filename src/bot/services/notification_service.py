"""Сервис для работы с уведомлениями."""
import json
import logging
from typing import Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.bot.utils.helpers import current_week_parity

logger = logging.getLogger("tg_schedule_bot")

# Ключи для отслеживания состояния ожидания
AWAIT_KEY = "awaiting_room"
AWAIT_TIME_KEY = "awaiting_time"

# Файл для хранения уведомлений
NOTIF_FILE = "notifications/notifications.json"

# Соответствие русских названий дню недели cron
DOW_MAP = {
    "Понедельник": "mon",
    "Вторник": "tue",
    "Среда": "wed",
    "Четверг": "thu",
    "Пятница": "fri",
    "Суббота": "sat",
    "Воскресенье": "sun",
}


class NotificationService:
    """Сервис для работы с уведомлениями."""

    def __init__(self, scheduler: AsyncIOScheduler, app):
        self.scheduler = scheduler
        self.app = app
        self.user_notifs: Dict[str, Dict[str, str]] = self._load_notifications()
        self._init_schedule_jobs()

    def _load_notifications(self) -> Dict[str, Dict[str, str]]:
        """Загрузить уведомления из файла."""
        try:
            with open(NOTIF_FILE, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_notifications(self) -> None:
        """Сохранить уведомления в файл."""
        with open(NOTIF_FILE, "w", encoding="utf-8") as fp:
            json.dump(self.user_notifs, fp, ensure_ascii=False, indent=2)

    def get_user_notifications(self, user_id: str) -> Dict[str, str]:
        """Получить уведомления пользователя."""
        return self.user_notifs.get(user_id, {})

    def add_notification(self, user_id: str, day: str, time: str) -> None:
        """Добавить уведомление для пользователя."""
        self.user_notifs.setdefault(user_id, {})[day] = time
        self._save_notifications()
        self._schedule_job(int(user_id), day, time)

    def remove_notification(self, user_id: str, day: str) -> None:
        """Удалить уведомление пользователя."""
        user_map = self.user_notifs.get(user_id, {})
        if day in user_map:
            user_map.pop(day)
            if not user_map:
                self.user_notifs.pop(user_id, None)
            self._save_notifications()
            self._remove_job(int(user_id), day)

    def _schedule_job(self, chat_id: int, full_day: str, time_str: str) -> None:
        """Запланировать задачу уведомления."""
        day_cron = DOW_MAP[full_day]
        hour, minute = map(int, time_str.split(":"))
        job_id = f"{chat_id}_{full_day}"

        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        self.scheduler.add_job(
            self._send_daily_notification,
            "cron",
            day_of_week=day_cron,
            hour=hour,
            minute=minute,
            args=[chat_id, full_day, time_str],
            id=job_id,
        )

    def _remove_job(self, chat_id: int, full_day: str) -> None:
        """Удалить задачу уведомления."""
        job_id = f"{chat_id}_{full_day}"
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            pass

    async def _send_daily_notification(self, chat_id: int, full_day: str, time_str: str) -> None:
        """Отправить ежедневное уведомление."""
        from src.bot.services.schedule_service import ScheduleService

        # Определяем, отправляем ли расписание на сегодня или завтра
        import datetime
        from datetime import timedelta

        now = datetime.datetime.now()
        hour = int(time_str.split(":")[0])

        if hour < 15:
            send_date = now.date()
            schedule_label = "<b>Расписание на сегодня</b>"
        else:
            send_date = now.date() + timedelta(days=1)
            schedule_label = "<b>Расписание на завтра</b>"

        schedule_service = ScheduleService()
        text = schedule_service.build_schedule_text_for_day(send_date)

        try:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=f"<b>Запланированное уведомление</b>\n\n{schedule_label}\n" + text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning(f"Failed to send scheduled message to {chat_id}: {e}")

    def _init_schedule_jobs(self) -> None:
        """Инициализировать запланированные задачи при запуске."""
        for uid, mapping in self.user_notifs.items():
            for day, time in mapping.items():
                self._schedule_job(int(uid), day, time)
