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
            if enemy_type == "basic":
                image_path = os.path.join(
                    os.path.dirname(__file__),
                    'assets',
                    'enemy_ufo.png'
                )
                try:
                    image = pygame.image.load(image_path).convert_alpha()
                    # Масштабирование до нужного размера
                    cls._images[enemy_type] = pygame.transform.scale(
                        image,
                        (config.ENEMY_WIDTH, config.ENEMY_HEIGHT)
                    )
                except (pygame.error, FileNotFoundError):
                    # Если изображение не загружено, создаём простой спрайт
                    cls._images[enemy_type] = pygame.Surface(
                        (config.ENEMY_WIDTH, config.ENEMY_HEIGHT),
                        pygame.SRCALPHA
                    )
                    pygame.draw.rect(
                        cls._images[enemy_type],
                        config.ENEMY_COLOR,
                        (0, 0, config.ENEMY_WIDTH, config.ENEMY_HEIGHT)
                    )
            else:
                # Для других типов врагов создаём простой спрайт
                cls._images[enemy_type] = pygame.Surface(
                    (config.ENEMY_WIDTH, config.ENEMY_HEIGHT),
                    pygame.SRCALPHA
                )
                pygame.draw.rect(
                    cls._images[enemy_type],
                    config.ENEMY_COLOR,
                    (0, 0, config.ENEMY_WIDTH, config.ENEMY_HEIGHT)
                )
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
        self.points = 10 if enemy_type == "basic" else 20
        
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
