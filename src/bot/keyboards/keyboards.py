"""Модуль для создания клавиатур."""
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.utils.helpers import current_week_parity, highlight


class KeyboardBuilder:
    """Класс для создания клавиатур."""

    # Кнопки дней недели
    WEEKDAY_BUTTONS = [
        ("Пн", "Понедельник"),
        ("Вт", "Вторник"),
        ("Ср", "Среда"),
        ("Чт", "Четверг"),
        ("Пт", "Пятница"),
        ("Сб", "Суббота"),
    ]

    # Кнопки дней недели включая воскресенье для уведомлений
    WEEKDAY_BUTTONS_7 = WEEKDAY_BUTTONS + [("Вс", "Воскресенье")]

    @classmethod
    def build_main_menu_keyboard(cls) -> InlineKeyboardMarkup:
        """Создать клавиатуру главного меню."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 Расписание по дням", callback_data="schedule_by_day")],
            [
                InlineKeyboardButton("⚡ Сегодня", callback_data="today"),
                InlineKeyboardButton("⚡ Завтра", callback_data="tomorrow"),
            ],
            [InlineKeyboardButton("🕔 Расписание звонков", callback_data="bells")],
            [InlineKeyboardButton("🏠 Найти корпус по аудитории", callback_data="find_building")],
            [InlineKeyboardButton("🔔 Ежедневные уведомления", callback_data="daily_notifications")],
        ])

    @classmethod
    def build_back_to_main_keyboard(cls) -> InlineKeyboardMarkup:
        """Создать клавиатуру с кнопкой возврата в главное меню."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 В главное меню", callback_data="to_main")]
        ])

    @classmethod
    def build_cancel_keyboard(cls) -> InlineKeyboardMarkup:
        """Создать клавиатуру с кнопкой отмены."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Отмена", callback_data="to_main")]
        ])

    @classmethod
    def build_schedule_by_day_keyboard(cls) -> InlineKeyboardMarkup:
        """Создать клавиатуру выбора недели и дня."""
        parity_text = current_week_parity()
        current_letter = "Ч" if parity_text.startswith("чёт") else "Н"

        rows = []
        for letter in ("Н", "Ч"):
            label = f"[{letter}]" if letter == current_letter else letter
            row = [InlineKeyboardButton(label, callback_data="noop")]

            for short, full in cls.WEEKDAY_BUTTONS:
                if letter == current_letter:
                    today_idx = datetime.date.today().weekday()
                    # Безопасно вычисляем обозначение сегодняшнего дня.
                    if 0 <= today_idx < len(cls.WEEKDAY_BUTTONS):
                        today_short = cls.WEEKDAY_BUTTONS[today_idx][0]
                    else:
                        today_short = None

                    label_day = highlight(short) if today_short and short == today_short else short
                else:
                    label_day = short
                cb = f"wd_{letter}_{full}"
                row.append(InlineKeyboardButton(label_day, callback_data=cb))
            rows.append(row)

        rows.append([InlineKeyboardButton("🔄 В главное меню", callback_data="to_main")])

        return InlineKeyboardMarkup(rows)

    @classmethod
    def build_notification_days_keyboard(cls) -> InlineKeyboardMarkup:
        """Создать клавиатуру выбора дня для уведомлений."""
        day_row = [
            InlineKeyboardButton(short, callback_data=f"notif_{full}")
            for short, full in cls.WEEKDAY_BUTTONS_7
        ]

        rows = [day_row, [InlineKeyboardButton("🔄 В главное меню", callback_data="to_main")]]

        return InlineKeyboardMarkup(rows)

    @classmethod
    def build_notification_edit_keyboard(cls, full_day: str) -> InlineKeyboardMarkup:
        """Создать клавиатуру редактирования уведомления."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✍️ Изменить", callback_data=f"edit_notif_{full_day}")],
            [InlineKeyboardButton("❌ Удалить", callback_data=f"del_notif_{full_day}")],
            [InlineKeyboardButton("🔄 В главное меню", callback_data="to_main")],
        ])

    @classmethod
    def build_notification_cancel_keyboard(cls) -> InlineKeyboardMarkup:
        """Создать клавиатуру отмены уведомления."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Отмена", callback_data="cancel_notif")]
        ])

    @classmethod
    def build_schedule_back_keyboard(cls) -> InlineKeyboardMarkup:
        """Создать клавиатуру с кнопками назад для расписания."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ Назад", callback_data="schedule_by_day")],
            [InlineKeyboardButton("🔄 В главное меню", callback_data="to_main")],
        ])