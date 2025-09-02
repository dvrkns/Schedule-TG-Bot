"""Обработчики сообщений."""
import re
from telegram import Update, constants
from telegram.constants import ChatType
from telegram.ext import ContextTypes

from src.bot.keyboards.keyboards import KeyboardBuilder
from src.bot.services.building_service import BuildingService
from src.bot.services.notification_service import NotificationService
from src.bot.utils.helpers import current_week_parity


class MessageHandlers:
    """Обработчики сообщений."""

    def __init__(self, notification_service):
        self.building_service = BuildingService()
        self.notification_service = notification_service

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик текстовых сообщений."""
        # Проверяем, что сообщение отправлено в личных сообщениях
        if update.effective_chat.type != ChatType.PRIVATE:
            return

        # Обрабатываем только если ожидаем номер аудитории
        if not context.user_data.get("awaiting_room"):
            if context.user_data.get("awaiting_time"):
                await self._handle_time_input(update, context)
            else:
                # Отправляем главное меню по любому обычному сообщению
                await self._show_main_menu(update, context)
            return

        await self._handle_room_input(update, context)

    async def handle_today_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик сообщения '⚡ Сегодня'."""
        # Проверяем, что сообщение отправлено в личных сообщениях
        if update.effective_chat.type != ChatType.PRIVATE:
            return

        from src.bot.services.schedule_service import ScheduleService

        schedule_service = ScheduleService()
        text = schedule_service.build_today_schedule_text()
        await update.message.reply_text(text, parse_mode=constants.ParseMode.HTML)

    async def _handle_time_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка ввода времени для уведомления."""
        # Проверяем, доступен ли сервис уведомлений
        if not self.notification_service:
            await update.message.reply_text(
                "⚠️ Функция отправки ежедневных уведомлений в данный момент не работает.",
                reply_markup=KeyboardBuilder.build_back_to_main_keyboard()
            )
            return

        time_txt = update.message.text.strip()
        time_valid = re.fullmatch(r"([0-1]?\d|2[0-3]):[0-5]\d", time_txt)

        if not time_valid:
            await update.message.reply_text(
                "Вы ввели некорректное время. Повторите попытку или отмените действие:",
                reply_markup=KeyboardBuilder.build_notification_cancel_keyboard(),
            )
            return

        # Валидное время, устанавливаем уведомление
        weekday_set = context.user_data.pop("awaiting_time", None)
        day = weekday_set or ""
        uid = str(update.effective_user.id)

        self.notification_service.add_notification(uid, day, time_txt)

        confirm_text = f"⏰ Уведомление на {time_txt} установлено!"
        await update.message.reply_text(
            confirm_text,
            reply_markup=KeyboardBuilder.build_back_to_main_keyboard()
        )

    async def _handle_room_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка ввода номера аудитории."""
        room_text = update.message.text.strip()
        result = self.building_service.get_building_by_room(room_text)

        if not result:
            # Сохраняем состояние ожидания; запрашиваем снова
            context.user_data["awaiting_room"] = True
            await update.message.reply_text(
                "Данный номер аудитории некорректен. Повторите попытку или отмените действие:",
                reply_markup=KeyboardBuilder.build_cancel_keyboard(),
            )
            return

        building_num, caption, photo_path, coordinates = result

        # Отправляем фото
        try:
            with open(photo_path, "rb") as photo_file:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo_file,
                    caption=caption,
                    parse_mode=constants.ParseMode.HTML,
                )
        except FileNotFoundError:
            await update.message.reply_text(caption, parse_mode=constants.ParseMode.HTML)

        # Отправляем местоположение
        lat, lon = coordinates
        await context.bot.send_location(
            chat_id=update.effective_chat.id,
            latitude=lat,
            longitude=lon,
        )

        # Очищаем флаг ожидания
        context.user_data.pop("awaiting_room", None)

        # Отправляем главное меню
        await self._show_main_menu(update, context)

    async def _show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать главное меню."""
        parity_text = current_week_parity()
        await update.message.reply_text(
            f"<b>Сейчас идёт {parity_text} неделя.</b>",
            parse_mode=constants.ParseMode.HTML,
            reply_markup=KeyboardBuilder.build_main_menu_keyboard(),
        )