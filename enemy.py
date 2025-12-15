"""
Класс врага и фабрика для создания врагов.
"""

import pygame
import os
import random
from typing import Optional
import config


class Enemy(pygame.sprite.Sprite):
    """
    Класс врага, движущегося сверху вниз.
    
    Имеет здоровье, получает урон от пуль и удаляется при выходе за экран.
    """
    
    # Загрузка изображений как атрибут класса (один раз для всех экземпляров)
    _images = {}
    
    @classmethod
    def _load_image(cls, enemy_type: str) -> pygame.Surface:
        """
        Загрузка изображения врага по типу.
        
        Args:
            enemy_type: Тип врага.
        
        Returns:
            Поверхность с изображением врага.
        """
        if enemy_type not in cls._images:
            width = config.ENEMY_WIDTH
            height = config.ENEMY_HEIGHT
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if enemy_type == "basic":
                # UFO‑спрайт из файла
                image_path = os.path.join(
                    os.path.dirname(__file__),
                    'assets',
                    'enemy_ufo.png'
                )
                try:
                    image = pygame.image.load(image_path).convert_alpha()
                    surface = pygame.transform.scale(
                        image,
                        (width, height)
                    )
                except (pygame.error, FileNotFoundError):
                    pygame.draw.ellipse(
                        surface,
                        config.ENEMY_COLOR,
                        (0, height // 4, width, height // 2)
                    )
            elif enemy_type == "fast":
                # Быстрый — маленький треугольник яркого цвета
                points = [
                    (width // 2, 0),
                    (0, height),
                    (width, height),
                ]
                pygame.draw.polygon(surface, config.COLOR_YELLOW, points)
            elif enemy_type == "heavy":
                # Тяжёлый — большой прямоугольник с рамкой
                pygame.draw.rect(
                    surface,
                    config.COLOR_RED,
                    (0, 0, width, height)
                )
                pygame.draw.rect(
                    surface,
                    config.COLOR_WHITE,
                    (3, 3, width - 6, height - 6),
                    2
                )
            elif enemy_type == "tank":
                # Танк — круг с толстой окантовкой
                radius = min(width, height) // 2 - 2
                center = (width // 2, height // 2)
                pygame.draw.circle(
                    surface,
                    config.COLOR_GREEN,
                    center,
                    radius
                )
                pygame.draw.circle(
                    surface,
                    config.COLOR_BLACK,
                    center,
                    radius,
                    3
                )
            else:
                # Неизвестный тип — базовый прямоугольник
                pygame.draw.rect(
                    surface,
                    config.ENEMY_COLOR,
                    (0, 0, width, height)
                )
            
            cls._images[enemy_type] = surface
        return cls._images[enemy_type]

    def __init__(
        self,
        x: int,
        y: int,
        speed: int,
        hp: int,
        enemy_type: str = "basic"
    ) -> None:
        """
        Инициализация врага.
        
        Args:
            x: Начальная позиция по оси X.
            y: Начальная позиция по оси Y.
            speed: Скорость движения вниз.
            hp: Здоровье врага.
            enemy_type: Тип врага.
        """
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.max_hp = hp
        self.hp = hp
        self.enemy_type = enemy_type
        self.rect = pygame.Rect(
            int(self.x),
            int(self.y),
            config.ENEMY_WIDTH,
            config.ENEMY_HEIGHT
        )
        # Очки за уничтожение зависят от типа
        if enemy_type == "basic":
            self.points = 10
        elif enemy_type == "fast":
            self.points = 15
        elif enemy_type == "heavy":
            self.points = 25
        elif enemy_type == "tank":
            self.points = 50
        else:
            self.points = 10
        
        # Загрузка изображения для данного типа врага
        self.image = self._load_image(enemy_type)

    def update(self) -> None:
        """
        Обновление позиции врага и удаление при выходе за экран.
        """
        self.y += self.speed
        self.rect.y = int(self.y)
        
        # Удаление при выходе за нижнюю границу
        if self.y > config.SCREEN_HEIGHT:
            self.kill()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовка врага и индикатора здоровья.
        
        Args:
            surface: Поверхность для отрисовки.
        """
        # Отрисовка изображения врага
        surface.blit(self.image, self.rect)
        
        # Индикатор здоровья (полоска над врагом)
        if self.max_hp > 0:
            bar_width = self.rect.width
            bar_height = 4
            bar_x = self.rect.x
            bar_y = self.rect.y - 8
            
            # Фон полоски (красный)
            pygame.draw.rect(
                surface,
                config.COLOR_RED,
                (bar_x, bar_y, bar_width, bar_height)
            )
            
            # Здоровье (зелёный)
            health_width = int(
                bar_width * (self.hp / self.max_hp)
            )
            if health_width > 0:
                pygame.draw.rect(
                    surface,
                    config.COLOR_GREEN,
                    (bar_x, bar_y, health_width, bar_height)
                )

    def take_damage(self, damage: int) -> bool:
        """
        Получение урона врагом.
        
        Args:
            damage: Количество урона.
        
        Returns:
            True, если враг уничтожен.
        """
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
            return True
        return False


def spawn_enemy(
    enemy_type: str,
    screen_width: int,
    speed: int | None = None,
    hp: int | None = None,
) -> Enemy:
    """
    Фабрика для создания врагов в случайной позиции сверху.
    
    Args:
        enemy_type: Тип врага.
        screen_width: Ширина экрана.
        speed: Скорость движения вниз. Если None, берётся из config.
        hp: Здоровье врага. Если None, берётся из config.
    
    Returns:
        Новый объект Enemy.
    """
    x = random.randint(0, screen_width - config.ENEMY_WIDTH)
    y = -config.ENEMY_HEIGHT
    if speed is None:
        speed = config.ENEMY_SPEED
    if hp is None:
        hp = config.ENEMY_BASIC_HP
    
    return Enemy(x, y, speed, hp, enemy_type)
