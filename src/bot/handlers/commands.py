"""Обработчики команд."""
from telegram import Update, constants
from telegram.constants import ChatType
from telegram.ext import ContextTypes

from src.bot.keyboards.keyboards import KeyboardBuilder
from src.bot.services.schedule_service import ScheduleService
from src.bot.services.building_service import BuildingService
from src.bot.utils.helpers import current_week_parity, is_admin


class CommandHandlers:
    """Обработчики команд."""

    def __init__(self):
        self.schedule_service = ScheduleService()
        self.building_service = BuildingService()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start."""
        # Проверяем, что команда вызвана в личных сообщениях
        if update.effective_chat.type != ChatType.PRIVATE:
            return

        # Сброс состояния ожидания аудитории, если было
        context.user_data.pop("awaiting_room", None)
        parity_text = current_week_parity()
        message_text = f"<b>Сейчас идёт {parity_text} неделя.</b>"

        await update.message.reply_text(
            message_text,
            reply_markup=KeyboardBuilder.build_main_menu_keyboard(),
            parse_mode=constants.ParseMode.HTML,
        )

    async def campus(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /campus."""
        photo_path = "assets/campus.jpg"
        caption = "Карта территории кампуса."
        try:
            with open(photo_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption=caption,
                    parse_mode=constants.ParseMode.HTML
                )
        except FileNotFoundError:
            text = "Изображение кампуса не найдено."
            if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode=constants.ParseMode.HTML
                )
            else:
                await update.message.reply_text(text, parse_mode=constants.ParseMode.HTML)

    async def today(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /today."""
        text = self.schedule_service.build_today_schedule_text()
        if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode=constants.ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                text,
                parse_mode=constants.ParseMode.HTML
            )

    async def tomorrow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /tomorrow."""
        text = self.schedule_service.build_tomorrow_schedule_text()
        if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode=constants.ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                text,
                parse_mode=constants.ParseMode.HTML
            )

    async def timetable(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /timetable."""
        text = self.schedule_service.build_bell_schedule_text()
        if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode=constants.ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                text,
                parse_mode=constants.ParseMode.HTML
            )

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /search."""
        if context.args:
            await self._lookup_room(update, context, context.args[0])
        else:
            text = "Введите после команды номер аудитории."
            if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text
                )
            else:
                await update.message.reply_text(text)

    async def dev(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /dev."""
        msg = (
            "<b>👨‍💻 Разработчик бота:</b> @secnd_chance\n"
            "<b>💻 Использованные технологии:</b>\n"
            "└ 🤖 <b>Бот:</b> Python 3.9.6 + python-telegram-bot\n"
            "└ ⏰ <b>Планировщик:</b> APScheduler\n"
            "<b>🔡 Исходный код:</b> https://github.com/dvrkns/Schedule-TG-Bot"
        )
        if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=msg,
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(msg, parse_mode="HTML")

    async def msg(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /msg для администратора."""
        # Проверяем, что команда вызвана в личных сообщениях
        if update.effective_chat.type != ChatType.PRIVATE:
            return

        # Проверяем, что пользователь является администратором
        user_id = update.effective_user.id
        if not is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return

        # Получаем текст сообщения из аргументов команды
        if not context.args:
            await update.message.reply_text(
                "❌ Использование: /msg текст сообщения\n"
                "Пример: /msg Важное объявление"
            )
            return

        # Объединяем все аргументы в одно сообщение
        message_text = " ".join(context.args)

        # Отправляем сообщение в группу в тот же тред, куда отправляется расписание
        from src.utils.secrets import GROUP_ID, SCHEDULE_THREAD_ID

        try:
            try:
                # Пытаемся отправить в тред (как в daily_schedule_service)
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=message_text,
                    message_thread_id=SCHEDULE_THREAD_ID
                )
                await update.message.reply_text("✅ Сообщение успешно отправлено в группу.")
            except Exception:
                # Если не удалось отправить в тред, отправляем без указания треда
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=message_text
                )
                await update.message.reply_text("✅ Сообщение успешно отправлено в группу.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при отправке сообщения: {e}")

    async def _lookup_room(self, update: Update, context: ContextTypes.DEFAULT_TYPE, room_text: str) -> None:
        """Поиск корпуса по номеру аудитории."""
        result = self.building_service.get_building_by_room(room_text)

        if not result:
            text = "Данный номер аудитории некорректен."
            if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text
                )
            else:
                await update.message.reply_text(text)
            return

        building_num, caption, photo_path, coordinates = result

        try:
            with open(photo_path, "rb") as f:
                await context.bot.send_photo(
                    update.effective_chat.id,
                    f,
                    caption=caption,
                    parse_mode=constants.ParseMode.HTML
                )
        except FileNotFoundError:
            if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=caption,
                    parse_mode=constants.ParseMode.HTML
                )
            else:
                await update.message.reply_text(caption, parse_mode=constants.ParseMode.HTML)

        lat, lon = coordinates
        await context.bot.send_location(update.effective_chat.id, latitude=lat, longitude=lon)
