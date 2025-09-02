"""Главный модуль бота."""
import logging
import sys
import signal
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from src.bot.utils.config import get_bot_token
from src.bot.handlers.commands import CommandHandlers
from src.bot.handlers.callbacks import CallbackHandlers
from src.bot.handlers.messages import MessageHandlers
from src.bot.services.notification_service import NotificationService
from src.bot.services.daily_schedule_service import DailyScheduleService
from src.bot.services.poll_service import PollScheduler


class Bot:
    """Основной класс бота."""

    def __init__(self):
        self.logger = logging.getLogger("schedule_tg_bot")
        self.scheduler = AsyncIOScheduler()
        self.application = None
        self.notification_service = None
        self.daily_schedule_service = None
        self.poll_scheduler = None
        self._shutdown_requested = False

        # Инициализация обработчиков
        self.command_handlers = CommandHandlers()
        self.callback_handlers = None  # Инициализируется после создания application
        self.message_handlers = None   # Инициализируется после создания notification_service

    async def _set_commands(self, app):
        """Установить команды бота."""
        cmds = [
            BotCommand("today", "Расписание на сегодня"),
            BotCommand("tomorrow", "Расписание на завтра"),
            BotCommand("timetable", "Расписание звонков"),
            BotCommand("campus", "Расположение корпусов"),
            BotCommand("search", "Найти корпус по аудитории"),
            BotCommand("dev", "Информация о разработчике и боте"),
        ]
        await app.bot.set_my_commands(cmds)

    def _shutdown_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения."""
        self.logger.info("Получен сигнал завершения.")
        self._shutdown_requested = True
        if self.application:
            self.application.stop()

    def setup_handlers(self):
        """Настроить обработчики."""
        # Инициализируем сервисы и обработчики
        self.notification_service = NotificationService(self.scheduler, self.application)
        self.daily_schedule_service = DailyScheduleService(self.scheduler, self.application)
        self.poll_scheduler = PollScheduler(self.scheduler, self.application)
        self.callback_handlers = CallbackHandlers(self.notification_service)
        self.message_handlers = MessageHandlers(self.notification_service)

        # Добавляем обработчики команд
        self.application.add_handler(CommandHandler("start", self.command_handlers.start))
        self.application.add_handler(CommandHandler("today", self.command_handlers.today))
        self.application.add_handler(CommandHandler("tomorrow", self.command_handlers.tomorrow))
        self.application.add_handler(CommandHandler("timetable", self.command_handlers.timetable))
        self.application.add_handler(CommandHandler("campus", self.command_handlers.campus))
        self.application.add_handler(CommandHandler("search", self.command_handlers.search))
        self.application.add_handler(CommandHandler("dev", self.command_handlers.dev))

        # Добавляем обработчики callback-запросов
        self.application.add_handler(
            CallbackQueryHandler(self.callback_handlers.handle_menu_callback)
        )

        # Добавляем обработчики сообщений
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & filters.Regex(r"^⚡ Сегодня$"),
                self.message_handlers.handle_today_message
            )
        )
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & (~filters.COMMAND),
                self.message_handlers.handle_text_message
            )
        )

    def run(self):
        """Запустить бота."""
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            filename="bot.log",
            filemode="a"
        )
        self.logger.setLevel(logging.INFO)

        # Настройка обработчиков сигналов
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)

        # Создание приложения
        self.application = (
            ApplicationBuilder()
            .token(get_bot_token())
            .post_init(self._set_commands)
            .build()
        )

        # Настройка обработчиков
        self.setup_handlers()

        # Запуск планировщика
        self.scheduler.start()
        self.logger.info("Запуск Telegram-бота…")

        # Запуск бота
        try:
            self.application.run_polling()
        except KeyboardInterrupt:
            self.logger.info("Получен сигнал остановки.")
        except Exception as e:
            self.logger.error(f"Ошибка: {e}")
        finally:
            # Печатаем перенос строки, чтобы ^C не слипалось с логом
            sys.stderr.write("\n")
            self.logger.info("Бот завершил работу.")

            # Безопасное завершение планировщика
            try:
                if self.scheduler.running:
                    self.scheduler.shutdown(wait=False)
            except Exception as e:
                self.logger.debug(f"Ошибка при завершении планировщика: {e}")
