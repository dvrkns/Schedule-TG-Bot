"""Сервис для работы с расписанием."""
import datetime
from datetime import timedelta
from typing import List

from src.data import schedule


class ScheduleService:
    """Сервис для работы с расписанием."""

    # Русские названия дней недели (строчные) Понедельник=0
    WEEKDAYS_RU = [
        "понедельник",
        "вторник",
        "среда",
        "четверг",
        "пятница",
        "суббота",
        "воскресенье",
    ]

    def __init__(self):
        self.schedule = schedule.schedule
        self.pair_times = schedule.PAIR_TIMES

    def get_week_parity_key(self, human_readable: str) -> str:
        """Преобразовать строку «чётная»/«нечётная» в ключ even/odd."""
        return schedule.get_week_parity_key(human_readable)

    def build_schedule_text_for_day(self, target_date: datetime.date) -> str:
        """Возвращает отформатированный текст расписания для заданной даты."""
        parity_text = self._get_parity_for_date(target_date)

        weekday_idx = target_date.weekday()
        weekday_ru_lower = self.WEEKDAYS_RU[weekday_idx]
        weekday_ru_cap = weekday_ru_lower.capitalize()

        # Получаем сырой список пар для сегодня
        parity_key = self.get_week_parity_key(parity_text)
        pairs_raw = self.schedule.get(parity_key, {}).get(weekday_ru_cap, [])

        # Строим сообщение
        lines: List[str] = [
            f"<b>День недели</b>: {weekday_ru_lower}",
            f"<b>Неделя</b>: {parity_text}",
            "",
        ]

        # Проверяем, есть ли хотя бы одна пара
        has_pairs = any(pair is not None for pair in pairs_raw)

        if not has_pairs:
            # Если пар нет, выводим сообщение о выходных
            lines.append("")
            lines.append("<b>Удачных выходных!</b>")
            return "\n".join(lines)

        lines.append("")

        for idx, pair in enumerate(pairs_raw):
            if pair is None:
                continue
            time_span = self.pair_times[idx] if idx < len(self.pair_times) else ""
            lines.append(f"<u>Пара №{idx + 1} (<i>{time_span}</i>)</u>")

            # Предмет жирным, тег типа пары остается обычным
            lines.append(f"[ {pair.kind} ] <b>{pair.subject}</b>")

            # Строки аудитории и преподавателя с жирными метками
            lines.append(f"<b>Аудитория</b>: {pair.room}")
            lines.append(f"<b>Преподаватель</b>: {pair.teacher}")
            lines.append("")

        lines.extend([
            "[ Л ] - <b>лекция</b>",
            "[ ПЗ ] - <b>практическое занятие</b>",
            "[ ЛАБ ] - <b>лабораторное занятие</b>",
        ])

        return "\n".join(lines)

    def build_today_schedule_text(self) -> str:
        """Возвращает текст расписания на сегодня."""
        return self.build_schedule_text_for_day(datetime.date.today())

    def build_tomorrow_schedule_text(self) -> str:
        """Возвращает текст расписания на завтра."""
        return self.build_schedule_text_for_day(datetime.date.today() + timedelta(days=1))

    def build_schedule_text_for_named_day(self, parity_human: str, weekday_full: str) -> str:
        """Возвращает отформатированный текст расписания для заданной чётности и дня недели."""
        weekday_lower = weekday_full.lower()

        parity_key = self.get_week_parity_key(parity_human)
        pairs_raw = self.schedule.get(parity_key, {}).get(weekday_full, [])

        lines: List[str] = [
            f"<b>День недели</b>: {weekday_lower}",
            f"<b>Неделя</b>: {parity_human}",
            "",
        ]

        # Проверяем, есть ли хотя бы одна пара
        has_pairs = any(pair is not None for pair in pairs_raw)

        if not has_pairs:
            # Если пар нет, выводим сообщение о выходных
            lines.append("")
            lines.append("<b>Удачных выходных!</b>")
            return "\n".join(lines)

        lines.append("")

        for idx, pair in enumerate(pairs_raw):
            if pair is None:
                continue
            time_span = self.pair_times[idx] if idx < len(self.pair_times) else ""
            lines.append(f"<u>Пара №{idx + 1} (<i>{time_span}</i>)</u>")
            lines.append(f"[ {pair.kind} ] <b>{pair.subject}</b>")
            lines.append(f"<b>Аудитория</b>: {pair.room}")
            lines.append(f"<b>Преподаватель</b>: {pair.teacher}")
            lines.append("")

        lines.extend([
            "[ Л ] - <b>лекция</b>",
            "[ ПЗ ] - <b>практическое занятие</b>",
            "[ ЛАБ ] - <b>лабораторное занятие</b>",
        ])

        return "\n".join(lines)

    def build_bell_schedule_text(self) -> str:
        """Возвращает расписание звонков, отформатированное в моноширинной таблице."""
        header_text = "Расписание"
        # Строим строки таблицы
        lines = ["+---+-------------+", "| № |    Время    |", "+---+-------------+"]

        for idx, span in enumerate(self.pair_times, start=1):
            row = f"| {idx:<1} | {span:>11} |"
            lines.append(row)
        lines.append("+---+-------------+")

        border_len = len(lines[0])
        padding = max((border_len - len(header_text)) // 2, 0)
        # Неразрывные пробелы для центрирования
        spaces = '\u2007' * padding
        header_centered = f"<b>{spaces}{header_text}{spaces}</b>"

        table = "\n".join(lines)
        return f"{header_centered}\n\n<code>{table}</code>"

    def _get_parity_for_date(self, target_date: datetime.date) -> str:
        """Получить чётность недели для заданной даты."""
        iso_week = target_date.isocalendar()[1]
        return "нечётная" if iso_week % 2 == 0 else "чётная"
