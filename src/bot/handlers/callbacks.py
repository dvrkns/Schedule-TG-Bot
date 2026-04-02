"""Обработчики callback-запросов."""
from telegram import Update, constants
from telegram.constants import ChatType
from telegram.ext import ContextTypes

from src.bot.keyboards.keyboards import KeyboardBuilder
from src.bot.services.schedule_service import ScheduleService
from src.bot.services.notification_service import NotificationService
from src.bot.services.block_service import BlockService
from src.bot.utils.helpers import current_week_parity


class CallbackHandlers:
    """Обработчики callback-запросов."""

    def __init__(self, notification_service):
        self.schedule_service = ScheduleService()
        self.notification_service = notification_service
        self.block_service = BlockService()

    async def handle_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик нажатий кнопок главного меню."""
        # Проверяем, что callback отправлен в личных сообщениях
        if update.effective_chat.type != ChatType.PRIVATE:
            return

        # Проверяем блокировку пользователя
        user_id = update.effective_user.id
        if self.block_service.is_blocked(user_id):
            query = update.callback_query
            await query.answer()
            return

        query = update.callback_query
        await query.answer()

        if query.data in ("today", "tomorrow"):
            await self._handle_today_tomorrow(query, context)
        elif query.data == "bells":
            await self._handle_bells(query, context)
        elif query.data == "find_building":
            await self._handle_find_building(query, context)
        elif query.data == "to_main":
            await self._handle_to_main(query, context)
        elif query.data == "schedule_by_day":
            await self._handle_schedule_by_day(query, context)
        elif query.data.startswith("wd_"):
            await self._handle_weekday_selection(query, context)
        elif query.data == "daily_notifications":
            await self._handle_daily_notifications(query, context)
        elif query.data.startswith("notif_"):
            await self._handle_notification_day_selection(query, context)
        elif query.data.startswith("edit_notif_"):
            await self._handle_edit_notification(query, context)
        elif query.data.startswith("del_notif_"):
            await self._handle_delete_notification(query, context)
        elif query.data == "cancel_notif":
            await self._handle_cancel_notification(query, context)

    async def _handle_today_tomorrow(self, query, context):
        """Обработка кнопок 'Сегодня' и 'Завтра'."""
        text_builder = (
            self.schedule_service.build_today_schedule_text
            if query.data == "today"
            else self.schedule_service.build_tomorrow_schedule_text
        )
        text = text_builder()
        await query.edit_message_text(
            text=text,
            parse_mode=constants.ParseMode.HTML,
            reply_markup=KeyboardBuilder.build_back_to_main_keyboard()
        )

    async def _handle_bells(self, query, context):
        """Обработка кнопки 'Расписание звонков'."""
        text = self.schedule_service.build_bell_schedule_text()
        await query.edit_message_text(
            text=text,
            parse_mode=constants.ParseMode.HTML,
            reply_markup=KeyboardBuilder.build_back_to_main_keyboard()
        )

    async def _handle_find_building(self, query, context):
        """Обработка кнопки 'Найти корпус по аудитории'."""
        context.user_data["awaiting_room"] = True
        await query.edit_message_text(
            text="Отправьте номер аудитории:",
            reply_markup=KeyboardBuilder.build_cancel_keyboard()
        )

    async def _handle_to_main(self, query, context):
        """Обработка кнопки возврата в главное меню."""
        context.user_data.pop("awaiting_room", None)
        parity_text = current_week_parity()
        await query.edit_message_text(
            text=f"<b>Сейчас идёт {parity_text} неделя.</b>",
            parse_mode=constants.ParseMode.HTML,
            reply_markup=KeyboardBuilder.build_main_menu_keyboard(),
        )

    async def _handle_schedule_by_day(self, query, context):
        """Обработка кнопки 'Расписание по дням'."""
        header = (
            f"Выберите неделю и день (сейчас идёт {current_week_parity()}):"
        )
        await query.edit_message_text(
            text=header,
            reply_markup=KeyboardBuilder.build_schedule_by_day_keyboard(),
        )

    async def _handle_weekday_selection(self, query, context):
        """Обработка выбора дня недели."""
        # Parse selection wd_letter_full
        _, letter, full_day = query.data.split("_", 2)
        parity_human = "нечётная" if letter == "Н" else "чётная"

        text_day = self.schedule_service.build_schedule_text_for_named_day(parity_human, full_day)

        await query.edit_message_text(
            text=text_day,
            parse_mode=constants.ParseMode.HTML,
            reply_markup=KeyboardBuilder.build_schedule_back_keyboard(),
        )

    async def _handle_daily_notifications(self, query, context):
        """Обработка кнопки 'Ежедневные уведомления'."""
        # Проверяем, доступен ли сервис уведомлений
        if not self.notification_service:
            await query.edit_message_text(
                text="⚠️ Функция отправки ежедневных уведомлений в данный момент не работает.",
                reply_markup=KeyboardBuilder.build_back_to_main_keyboard()
            )
            return

        uid = str(query.from_user.id)
        user_map = self.notification_service.get_user_notifications(uid)

        if user_map:
            lines = [
                "Дни недели, по которым вы получаете уведомления с расписанием:\n",
            ]
            for day, t in user_map.items():
                lines.append(f"{day}: {t}")
            header = "\n".join(lines)
            header += "\n\nХотите изменить время, добавить или удалить напоминания? Выберите день:"
        else:
            header = (
                "Уведомления с расписанием отсутствуют.\n"
                "Выберите день недели для установки времени автоматической отправки расписания:"
            )

        await query.edit_message_text(
            text=header,
            reply_markup=KeyboardBuilder.build_notification_days_keyboard()
        )

    async def _handle_notification_day_selection(self, query, context):
        """Обработка выбора дня для уведомления."""
        # Проверяем, доступен ли сервис уведомлений
        if not self.notification_service:
            await query.edit_message_text(
                text="⚠️ Функция отправки ежедневных уведомлений в данный момент не работает.",
                reply_markup=KeyboardBuilder.build_back_to_main_keyboard()
            )
            return

        _, full_day = query.data.split("_", 1)
        uid = str(query.from_user.id)
        user_map = self.notification_service.get_user_notifications(uid)

        if full_day in user_map:
            # Показать меню изменения/удаления
            msg = f"Изменение напоминания ({full_day.lower()}):"
            await query.edit_message_text(
                text=msg,
                reply_markup=KeyboardBuilder.build_notification_edit_keyboard(full_day)
            )
        else:
            # Перейти к добавлению нового времени
            context.user_data["awaiting_time"] = full_day

            msg = (
                f"Добавление напоминания ({full_day.lower()})\n\n"
                "Введите время, в которое вы хотите получать расписание:\n"
                "————————————————————\n"
                "Если введённое время в диапазоне от 00:00 до 14:59, то бот отправит расписание на сегодня.\n"
                "Если же введённое время в диапазоне от 15:00 до 23:59, то расписание на завтра."
            )

            await query.edit_message_text(
                text=msg,
                reply_markup=KeyboardBuilder.build_notification_cancel_keyboard()
            )

    async def _handle_edit_notification(self, query, context):
        """Обработка редактирования уведомления."""
        # Проверяем, доступен ли сервис уведомлений
        if not self.notification_service:
            await query.edit_message_text(
                text="⚠️ Функция отправки ежедневных уведомлений в данный момент не работает.",
                reply_markup=KeyboardBuilder.build_back_to_main_keyboard()
            )
            return

        _, _, full_day = query.data.split("_", 2)
        context.user_data["awaiting_time"] = full_day

        uid = str(query.from_user.id)
        current_time = self.notification_service.get_user_notifications(uid).get(full_day, "—")

        msg = (
            f"Сейчас вы получаете расписание ({full_day.lower()}) в {current_time}.\n"
            "Введите время, в которое вы хотите получать расписание:\n"
            "————————————————————\n"
            "Если введённое время в диапазоне от 00:00 до 14:59, то бот отправит расписание на сегодня.\n"
            "Если же введённое время в диапазоне от 15:00 до 23:59, то расписание на завтра."
        )

        await query.edit_message_text(
            text=msg,
            reply_markup=KeyboardBuilder.build_notification_cancel_keyboard()
        )

    async def _handle_delete_notification(self, query, context):
        """Обработка удаления уведомления."""
        # Проверяем, доступен ли сервис уведомлений
        if not self.notification_service:
            await query.edit_message_text(
                text="⚠️ Функция отправки ежедневных уведомлений в данный момент не работает.",
                reply_markup=KeyboardBuilder.build_back_to_main_keyboard()
            )
            return

        _, _, full_day = query.data.split("_", 2)
        uid = str(query.from_user.id)
        self.notification_service.remove_notification(uid, full_day)

        await query.edit_message_text(
            text=f"Уведомление ({full_day.lower()}) выключено.",
            reply_markup=KeyboardBuilder.build_back_to_main_keyboard(),
        )

    async def _handle_cancel_notification(self, query, context):
        """Обработка отмены уведомления."""
        context.user_data.pop("awaiting_time", None)
        parity_text = current_week_parity()
        await query.edit_message_text(
            text=f"<b>Сейчас идёт {parity_text} неделя.</b>",
            parse_mode=constants.ParseMode.HTML,
            reply_markup=KeyboardBuilder.build_main_menu_keyboard(),
        )