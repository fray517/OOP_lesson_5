"""
Класс врага и фабрика для создания врагов.
"""

import pygame
import random
from typing import Optional
import config


class Enemy(pygame.sprite.Sprite):
    """
    Класс врага, движущегося сверху вниз.
    
    Имеет здоровье, получает урон от пуль и удаляется при выходе за экран.
    """

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
        self.points = 10 if enemy_type == "basic" else 20

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
        # Отрисовка врага
        pygame.draw.rect(
            surface,
            config.ENEMY_COLOR,
            self.rect
        )
        
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


def spawn_enemy(enemy_type: str, screen_width: int) -> Enemy:
    """
    Фабрика для создания врагов в случайной горизонтальной позиции.
    
    Args:
        enemy_type: Тип врага.
        screen_width: Ширина экрана.
    
    Returns:
        Новый объект Enemy.
    """
    x = random.randint(
        0,
        screen_width - config.ENEMY_WIDTH
    )
    y = -config.ENEMY_HEIGHT
    speed = config.ENEMY_SPEED
    hp = config.ENEMY_BASIC_HP
    
    return Enemy(x, y, speed, hp, enemy_type)
