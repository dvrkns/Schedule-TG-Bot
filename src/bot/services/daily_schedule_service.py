"""Сервис для ежедневной отправки расписания на следующий день."""
import logging
import datetime
from datetime import timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.bot.services.schedule_service import ScheduleService
from src.utils.secrets import THREAD_ID, GROUP_ID
from src.bot.services.daily_schedule_service_utils import get_daily_schedule_time

logger = logging.getLogger("tg_schedule_bot")


class DailyScheduleService:
    """Сервис для ежедневной отправки расписания на следующий день."""

    def __init__(self, scheduler: AsyncIOScheduler, app):
        self.scheduler = scheduler
        self.app = app
        self.schedule_service = ScheduleService()
        self._check_chat_accessibility()
        self._init_daily_schedule_job()

    def _init_daily_schedule_job(self):
        """Инициализировать ежедневную задачу отправки расписания."""
        # Отправляем расписание каждый день в заданное время
        hour, minute = get_daily_schedule_time()
        self.scheduler.add_job(
            self._send_tomorrow_schedule,
            'cron',
            hour=hour,
            minute=minute,
            id='daily_schedule_job'
        )
        logger.info(f"Ежедневная задача отправки расписания запланирована на {hour:02d}:{minute:02d}")

    def _check_chat_accessibility(self):
        """Проверить доступность чатов для отправки."""
        logger.info(f"Проверка доступности чатов:")
        logger.info(f"THREAD_ID: {THREAD_ID}")
        logger.info(f"GROUP_ID: {GROUP_ID}")

        # Проверяем, что ID не являются placeholder'ами
        if THREAD_ID == "Thread number":
            logger.warning("THREAD_ID не настроен (используется placeholder)")
        if GROUP_ID == "Group ID":
            logger.warning("GROUP_ID не настроен (используется placeholder)")

    async def _send_tomorrow_schedule(self):
        """Отправить расписание на следующий день."""
        try:
            tomorrow = datetime.date.today() + timedelta(days=1)

            # Проверяем, есть ли пары на завтра
            if not self._has_pairs_for_date(tomorrow):
                logger.info(f"На {tomorrow.strftime('%d.%m.%Y')} нет пар, расписание не отправляется")
                return

            # Получаем текст расписания на завтра
            schedule_text = self.schedule_service.build_schedule_text_for_day(tomorrow)

            # Формируем сообщение
            message_text = (
                f"<b>📅 Расписание на завтра ({tomorrow.strftime('%d.%m.%Y')})</b>\n\n"
                f"{schedule_text}"
            )

            # Пытаемся отправить в THREAD_ID, если не получится - в GROUP_ID
            chat_id = THREAD_ID
            message_thread_id = None

            try:
                # Сначала пробуем отправить в тред
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    parse_mode="HTML"
                )
                logger.info(f"Расписание на {tomorrow.strftime('%d.%m.%Y')} успешно отправлено в THREAD_ID")

            except Exception as thread_error:
                logger.warning(f"Не удалось отправить в THREAD_ID ({THREAD_ID}): {thread_error}")

                # Пробуем отправить в группу
                try:
                    chat_id = GROUP_ID
                    await self.app.bot.send_message(
                        chat_id=chat_id,
                        text=message_text,
                        parse_mode="HTML"
                    )
                    logger.info(f"Расписание на {tomorrow.strftime('%d.%m.%Y')} успешно отправлено в GROUP_ID")

                except Exception as group_error:
                    logger.error(f"Не удалось отправить ни в THREAD_ID, ни в GROUP_ID: {group_error}")
                    raise group_error

        except Exception as e:
            logger.error(f"Ошибка при отправке расписания на завтра: {e}")

    def _has_pairs_for_date(self, target_date: datetime.date) -> bool:
        """Проверить, есть ли пары на заданную дату."""
        try:
            # Получаем расписание для даты
            schedule_text = self.schedule_service.build_schedule_text_for_day(target_date)

            # Проверяем, содержит ли расписание пары (не только заголовки)
            lines = schedule_text.split('\n')

            # Ищем строки с парами (они содержат "Пара №")
            # Если таких строк нет, значит на этот день нет занятий
            for line in lines:
                if "Пара №" in line:
                    return True

            return False

        except Exception as e:
            logger.error(f"Ошибка при проверке наличия пар для {target_date}: {e}")
            return False
