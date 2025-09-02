import datetime
from src.bot.services.schedule_service import ScheduleService

# Единое место для хранения времени до пары
MINUTES_BEFORE_PAIR = 15

def get_poll_plan_for_day(target_date):
    """
    Возвращает poll_time, если есть хотя бы одна пара в расписании на target_date.
    Если пар нет, возвращает None.
    """
    schedule_service = ScheduleService()
    parity_text = schedule_service._get_parity_for_date(target_date)
    weekday_idx = target_date.weekday()
    weekday_ru_cap = schedule_service.WEEKDAYS_RU[weekday_idx].capitalize()
    pairs_raw = schedule_service.schedule.get(schedule_service.get_week_parity_key(parity_text), {}).get(weekday_ru_cap, [])
    for idx, pair in enumerate(pairs_raw):
        if pair is not None:
            time_span = schedule_service.pair_times[idx]
            start_time = time_span.split('-')[0]
            hour, minute = map(int, start_time.split(':'))
            poll_time = datetime.datetime.combine(target_date, datetime.time(hour, minute)) - datetime.timedelta(minutes=MINUTES_BEFORE_PAIR)
            return poll_time
    return None
