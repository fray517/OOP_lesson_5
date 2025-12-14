"""
Класс игрока.
"""

import pygame
import os
from typing import Optional
import config


class Player(pygame.sprite.Sprite):
    """
    Класс игрока, управляемого пользователем.
    
    Отвечает за движение, стрельбу, получение урона и отображение.
    """
    
    # Загрузка изображения как атрибут класса (один раз для всех экземпляров)
    _image = None
    
    @classmethod
    def _load_image(cls) -> pygame.Surface:
        """
        Загрузка изображения корабля игрока.
        
        Returns:
            Поверхность с изображением корабля.
        """
        if cls._image is None:
            image_path = os.path.join(
                os.path.dirname(__file__),
                'assets',
                'player_ship.png'
            )
            try:
                cls._image = pygame.image.load(image_path).convert_alpha()
                # Масштабирование до нужного размера
                cls._image = pygame.transform.scale(
                    cls._image,
                    (config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
                )
            except (pygame.error, FileNotFoundError):
                # Если изображение не загружено, создаём простой спрайт
                cls._image = pygame.Surface(
                    (config.PLAYER_WIDTH, config.PLAYER_HEIGHT),
                    pygame.SRCALPHA
                )
                pygame.draw.rect(
                    cls._image,
                    config.PLAYER_COLOR,
                    (0, 0, config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
                )
        return cls._image

    def __init__(self, x: int, y: int) -> None:
        """
        Инициализация игрока.
        
        Args:
            x: Начальная позиция по оси X.
            y: Начальная позиция по оси Y.
        """
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.speed = config.PLAYER_SPEED
        
        # Загрузка изображения
        self.image = self._load_image()
        
        self.rect = self.image.get_rect()
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        self.max_hp = config.PLAYER_MAX_HP
        self.hp = self.max_hp
        self.lives = config.PLAYER_START_LIVES
        self.last_shot_time = 0
        self.shoot_cooldown = config.BULLET_COOLDOWN
        self.is_invincible = False
        self.invincibility_timer = 0

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """
        Обработка ввода для движения игрока.
        
        Args:
            keys: Состояние клавиатуры.
        """
        # Движение по WASD или стрелкам
        dx = 0
        dy = 0
        
        if (keys[pygame.K_w] or keys[pygame.K_UP]):
            dy = -self.speed
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]):
            dy = self.speed
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]):
            dx = -self.speed
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            dx = self.speed
        
        # Ограничение по границам окна
        self.x = max(0, min(
            config.SCREEN_WIDTH - self.rect.width,
            self.x + dx
        ))
        self.y = max(0, min(
            config.SCREEN_HEIGHT - self.rect.height,
            self.y + dy
        ))
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def shoot(self, current_time: int) -> Optional['Bullet']:
        """
        Создание пули при нажатии пробела с учётом задержки.
        
        Args:
            current_time: Текущее время в миллисекундах.
        
        Returns:
            Объект Bullet или None, если выстрел невозможен.
        """
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            # Импорт здесь, чтобы избежать циклических зависимостей
            from bullet import Bullet
            bullet = Bullet(
                self.rect.centerx,
                self.rect.top,
                -config.BULLET_SPEED
            )
            return bullet
        return None

    def update(self, current_time: int) -> None:
        """
        Обновление состояния игрока.
        
        Args:
            current_time: Текущее время в миллисекундах.
        """
        # Обновление таймера неуязвимости
        if self.is_invincible:
            if current_time - self.invincibility_timer >= \
                    config.INVINCIBILITY_DURATION:
                self.is_invincible = False
                self.invincibility_timer = 0

    def draw(self, surface: pygame.Surface, current_time: int = None) -> None:
        """
        Отрисовка игрока с учётом мигания при неуязвимости.
        
        Args:
            surface: Поверхность для отрисовки.
            current_time: Текущее время в миллисекундах для мигания.
        """
        if current_time is None:
            current_time = pygame.time.get_ticks()
        
        # Мигание при неуязвимости (каждые 100 мс)
        should_draw = True
        if self.is_invincible:
            should_draw = (current_time // 100) % 2 == 0
        
        if should_draw:
            # Отрисовка изображения корабля
            surface.blit(self.image, self.rect)

    def take_damage(self, damage: int, current_time: int) -> None:
        """
        Получение урона с активацией неуязвимости.
        
        Args:
            damage: Количество урона.
            current_time: Текущее время в миллисекундах.
        """
        if not self.is_invincible:
            self.hp -= damage
            if self.hp <= 0:
                self.lives -= 1
                if self.lives > 0:
                    self.hp = self.max_hp
            self.is_invincible = True
            self.invincibility_timer = current_time

    def is_alive(self) -> bool:
        """
        Проверка, жив ли игрок.
        
        Returns:
            True, если игрок жив (есть жизни и здоровье).
        """
        return self.lives > 0 and self.hp > 0
