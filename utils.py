"""
Вспомогательные функции для игры.
"""

import pygame
from typing import Tuple
import config


def check_collision(
    rect1: pygame.Rect,
    rect2: pygame.Rect
) -> bool:
    """
    Проверка столкновения двух прямоугольников.
    
    Args:
        rect1: Первый прямоугольник.
        rect2: Второй прямоугольник.
    
    Returns:
        True, если прямоугольники пересекаются.
    """
    return rect1.colliderect(rect2)


def clamp(
    value: float,
    min_value: float,
    max_value: float
) -> float:
    """
    Ограничение значения в заданном диапазоне.
    
    Args:
        value: Значение для ограничения.
        min_value: Минимальное значение.
        max_value: Максимальное значение.
    
    Returns:
        Ограниченное значение.
    """
    return max(min_value, min(max_value, value))


def get_random_spawn_position(
    screen_width: int,
    screen_height: int,
    object_width: int,
    object_height: int
) -> Tuple[int, int]:
    """
    Получение случайной позиции для спавна объекта.
    
    Args:
        screen_width: Ширина экрана.
        screen_height: Высота экрана.
        object_width: Ширина объекта.
        object_height: Высота объекта.
    
    Returns:
        Кортеж (x, y) с позицией.
    """
    import random
    x = random.randint(0, screen_width - object_width)
    y = random.randint(0, screen_height - object_height)
    return (x, y)
