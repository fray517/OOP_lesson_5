"""
Класс игрока.
"""

import pygame
from typing import Optional
import config


class Player(pygame.sprite.Sprite):
    """
    Класс игрока, управляемого пользователем.
    
    Отвечает за движение, стрельбу, получение урона и отображение.
    """

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
        self.rect = pygame.Rect(
            int(self.x),
            int(self.y),
            config.PLAYER_WIDTH,
            config.PLAYER_HEIGHT
        )
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
            config.SCREEN_WIDTH - config.PLAYER_WIDTH,
            self.x + dx
        ))
        self.y = max(0, min(
            config.SCREEN_HEIGHT - config.PLAYER_HEIGHT,
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

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовка игрока с учётом мигания при неуязвимости.
        
        Args:
            surface: Поверхность для отрисовки.
        """
        if not self.is_invincible or \
                (pygame.time.get_ticks() // 100) % 2 == 0:
            pygame.draw.rect(
                surface,
                config.PLAYER_COLOR,
                self.rect
            )

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
