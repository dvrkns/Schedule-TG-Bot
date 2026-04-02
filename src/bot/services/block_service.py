"""Сервис для работы с блокировками пользователей."""
import json
import logging
from typing import Set

logger = logging.getLogger("tg_schedule_bot")

# Файл для хранения заблокированных пользователей
BLOCKED_USERS_FILE = "data/blocked_users.json"


class BlockService:
    """Сервис для работы с блокировками пользователей."""

    def __init__(self):
        self.blocked_users: Set[int] = self._load_blocked_users()

    def _load_blocked_users(self) -> Set[int]:
        """Загрузить список заблокированных пользователей из файла."""
        try:
            with open(BLOCKED_USERS_FILE, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                # Преобразуем список строк в множество целых чисел
                return {int(user_id) for user_id in data}
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return set()

    def _save_blocked_users(self) -> None:
        """Сохранить список заблокированных пользователей в файл."""
        import os
        # Создаём директорию, если её нет
        os.makedirs(os.path.dirname(BLOCKED_USERS_FILE), exist_ok=True)
        
        # Преобразуем множество в список строк для JSON
        data = [str(user_id) for user_id in self.blocked_users]
        with open(BLOCKED_USERS_FILE, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

    def is_blocked(self, user_id: int) -> bool:
        """Проверить, заблокирован ли пользователь."""
        return user_id in self.blocked_users

    def block_user(self, user_id: int) -> bool:
        """Заблокировать пользователя.
        
        Returns:
            True, если пользователь был успешно заблокирован
            False, если пользователь уже был заблокирован
        """
        if user_id in self.blocked_users:
            return False
        self.blocked_users.add(user_id)
        self._save_blocked_users()
        return True

    def unblock_user(self, user_id: int) -> bool:
        """Разблокировать пользователя.
        
        Returns:
            True, если пользователь был успешно разблокирован
            False, если пользователь не был заблокирован
        """
        if user_id not in self.blocked_users:
            return False
        self.blocked_users.remove(user_id)
        self._save_blocked_users()
        return True

    def get_blocked_users(self) -> Set[int]:
        """Получить множество всех заблокированных пользователей."""
        return self.blocked_users.copy()
