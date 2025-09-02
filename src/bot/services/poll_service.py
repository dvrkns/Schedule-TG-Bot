import datetime
import pathlib
import re
import logging
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

def get_group_and_thread_id():
    """Получение GroupID и ThreadID из src.utils.secrets"""
    from src.utils.secrets import GROUP_ID, THREAD_ID
    return GROUP_ID, THREAD_ID

async def send_presence_poll(bot: Bot, date: datetime.date):
    """Отправить опрос о присутствии в тему группы"""
    group_id, thread_id = get_group_and_thread_id()
    if not group_id or not thread_id:
        return
    poll_question = f"Отметка на {date.day:02d}.{date.month:02d}"
    options = ["+", "-"]
    await bot.send_poll(
        chat_id=group_id,
        question=poll_question,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False,
        message_thread_id=thread_id,
    )


class PollScheduler:
    """Класс для планирования ежедневных опросов."""

    def __init__(self, scheduler: AsyncIOScheduler, app):
        self.scheduler = scheduler
        self.app = app
        self.logger = logging.getLogger("tg_schedule_bot")
        self._init_daily_poll_job()

    def _init_daily_poll_job(self):
        """Инициализировать ежедневную задачу планирования опросов."""
        # Запускать планирование опроса каждый день в 00:01
        self.scheduler.add_job(
            self._daily_poll_job,
            'cron',
            hour=0,
            minute=1,
            id='schedule_daily_poll_job'
        )
        self.logger.info("Ежедневная задача планирования опросов запланирована на 00:01")

        # Также планируем опрос на сегодня при запуске (если бот стартует не ночью)
        self._daily_poll_job()

    def _daily_poll_job(self):
        """Ежедневная задача планирования опросов."""
        today = datetime.date.today()
        self._schedule_poll_for_day(today)

    def _schedule_poll_for_day(self, target_date):
        """Запланировать опрос для заданной даты."""
        from src.bot.services.poll_plan_utils import get_poll_plan_for_day, MINUTES_BEFORE_PAIR

        poll_time = get_poll_plan_for_day(target_date)
        if poll_time:
            now = datetime.datetime.now()
            delay = (poll_time - now).total_seconds()
            self.logger.info(f"Планирование опроса: poll_time={poll_time}, now={now}, delay={delay}, minutes_before_pair={MINUTES_BEFORE_PAIR}")
            if delay > 0:
                self.scheduler.add_job(
                    send_presence_poll,
                    'date',
                    run_date=poll_time,
                    args=[self.app.bot, target_date],
                    id=f"presence_poll_{target_date.isoformat()}"
                )
                self.logger.info(f"Опрос запланирован на {poll_time}")
            else:
                self.logger.info(f"Время для опроса уже прошло, задача не запланирована.")
        else:
            self.logger.info(f"Нет ни одной пары для {target_date.strftime('%A')} ({target_date})")
