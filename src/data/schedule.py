"""Модуль со статическим расписанием.

Структура данных упрощённая:
    schedule[week_parity][weekday] -> список строк с описанием занятий

• week_parity: "even" (чётная) или "odd" (нечётная)
• weekday     : название дня недели по-русски (с заглавной буквы)

Дальнейшая логика бота сможет импортировать эти данные и
выводить расписание по выбранным параметрам.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Pair:
    """Структура, описывающая одну учебную пару."""

    subject: str  # Название дисциплины
    teacher: str  # Фамилия И. О.
    kind: str  # «лекция», «практика», «лабораторная»
    room: str  # Аудитория

WeekParity = str  # Literal["even", "odd"]
Weekday = str

# Кол-во пар в учебном дне (можете увеличить при необходимости)
MAX_PAIRS_PER_DAY = 8

# Время начала-конца каждой пары (по умолчанию; можно изменить под ваше)
PAIR_TIMES = [
    "08:00-09:35",  # 1
    "09:45-11:20",  # 2
    "11:30-13:05",  # 3
    "13:20-14:55",  # 4
    "15:05-16:40",  # 5
    "16:50-18:25",  # 6
    "18:40-20:15",  # 7
    "20:25-22:00",  # 8
]

# Новый формат: список длиной MAX_PAIRS_PER_DAY.
# None = пары нет. Если первая пара отсутствует, ставим None на индекс 0;
# дальше расписание начинается со 2-й пары (индекс 1).

schedule: Dict[WeekParity, Dict[Weekday, List[Optional[Pair]]]] = {
    "even": {
        "Понедельник": [None],
        "Вторник": [None],
        "Среда": [None],
        "Четверг": [None],
        "Пятница": [None],
        "Суббота": [None],
    },
    "odd": {
        "Понедельник": [None],
        "Вторник": [None],
        "Среда": [None],
        "Четверг": [None],
        "Пятница": [None],
        "Суббота": [None],
    },
}

# ------------------------------------------------------------
# Автоматическое дополнение расписаний до MAX_PAIRS_PER_DAY
# ------------------------------------------------------------

for week in schedule.values():
    for day, lessons in week.items():
        if len(lessons) < MAX_PAIRS_PER_DAY:
            lessons.extend([None] * (MAX_PAIRS_PER_DAY - len(lessons)))


def get_week_parity_key(human_readable: str) -> WeekParity:
    """Преобразовать строку «чётная»/«нечётная» в ключ even/odd."""
    return "even" if human_readable.strip().startswith("чёт") else "odd"


# ----------------------------------------------------------------------------
# API-функции
# ----------------------------------------------------------------------------


def get_day_schedule(parity_human: str, weekday: Weekday) -> List[str]:
    """Вернуть форматированный список строк «N) время — предмет».

    • Пропускает отсутствующие пары (None).
    • Сохраняет реальный номер пары (если 1-й нет, список начнётся с «2) …»).
    """
    parity_key = get_week_parity_key(parity_human)
    raw_list = schedule.get(parity_key, {}).get(weekday, [])
    formatted: List[str] = []
    for idx, pair in enumerate(raw_list):
        if pair is None:
            continue  # пары нет, пропускаем
        pair_num = idx + 1  # индексация с 0
        time_span = PAIR_TIMES[idx] if idx < len(PAIR_TIMES) else ""
        formatted.append(
            f"{pair_num}) {time_span} — {pair.subject} "
            f"({pair.kind}, {pair.teacher}, {pair.room})"
        )
    return formatted
