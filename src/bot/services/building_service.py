"""Сервис для работы с корпусами и аудиториями."""
import re
from typing import Tuple, Optional


class BuildingService:
    """Сервис для работы с корпусами и аудиториями."""

    def __init__(self):
        # Координаты корпусов (широта, долгота)
        self.building_coordinates = {
            1: (00.00, 00.00),
        }

        # Информация о корпусах
        self.building_info = {
            1: {
                "name": "Street, 13",
                "photo": "assets/building_1.jpg"
            },
        }

    def get_building_by_room(self, room_text: str) -> Optional[Tuple[int, str, str, Tuple[float, float]]]:
        """Определить корпус по номеру аудитории.

        Returns:
            Tuple[building_number, caption, photo_path, coordinates] или None
        """
        room_text = room_text.strip()

        # Паттерны для разных корпусов
        match_b1 = re.fullmatch(r"[1-9]\d?", room_text)  # 1-99

        if match_b1:
            building_num = 1
        else:
            return None

        building_info = self.building_info[building_num]
        coordinates = self.building_coordinates[building_num]

        caption = f"Аудитория {room_text} находится в корпусе №{building_num} (<i>{building_info['name']}</i>)."

        return (building_num, caption, building_info['photo'], coordinates)

    def is_valid_room(self, room_text: str) -> bool:
        """Проверить, является ли номер аудитории корректным."""
        return self.get_building_by_room(room_text) is not None
