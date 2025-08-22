import datetime
import pathlib
import re
from telegram import Bot

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
