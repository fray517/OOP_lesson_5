"""
Класс игрока.
"""

from __future__ import annotations

import os
from typing import Optional

import pygame

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
        """Загрузка изображения корабля игрока."""
        if cls._image is None:
            image_path = os.path.join(
                os.path.dirname(__file__),
                'assets',
                'player_ship.png'
            )
            try:
                cls._image = pygame.image.load(image_path).convert_alpha()
                cls._image = pygame.transform.scale(
                    cls._image,
                    (config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
                )
            except (pygame.error, FileNotFoundError):
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
        """Инициализация игрока."""
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
        
        # Активные временные эффекты: имя -> время окончания (мс)
        self.active_effects: dict[str, int] = {}

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Обработка ввода для движения игрока."""
        dx = 0
        dy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
        
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

    def shoot(self, current_time: int):
        """Создание одной или нескольких пуль с учётом бонусов."""
        if current_time - self.last_shot_time < self.shoot_cooldown:
            return None
        self.last_shot_time = current_time
        
        from bullet import Bullet  # локальный импорт
        bullets: list[Bullet] = []
        
        # Базовая пуля по центру
        bullets.append(Bullet(
            self.rect.centerx,
            self.rect.top,
            -config.BULLET_SPEED
        ))
        
        # DOUBLE_SHOT / TRIPLE_SHOT
        has_double = "DOUBLE_SHOT" in self.active_effects
        has_triple = "TRIPLE_SHOT" in self.active_effects
        
        if has_triple:
            offset = 12
            bullets.append(Bullet(
                self.rect.centerx - offset,
                self.rect.top,
                -config.BULLET_SPEED
            ))
            bullets.append(Bullet(
                self.rect.centerx + offset,
                self.rect.top,
                -config.BULLET_SPEED
            ))
        elif has_double:
            offset = 10
            bullets.append(Bullet(
                self.rect.centerx - offset,
                self.rect.top,
                -config.BULLET_SPEED
            ))
            bullets.append(Bullet(
                self.rect.centerx + offset,
                self.rect.top,
                -config.BULLET_SPEED
            ))
        
        return bullets

    def update(self, current_time: int) -> None:
        """Обновление состояния игрока (эффекты, неуязвимость)."""
        # Обновление таймера неуязвимости
        if self.is_invincible:
            if current_time - self.invincibility_timer >= \
                    config.INVINCIBILITY_DURATION:
                self.is_invincible = False
                self.invincibility_timer = 0
        
        # Обновление временных эффектов
        expired = [
            name for name, end_time in self.active_effects.items()
            if current_time >= end_time
        ]
        for name in expired:
            del self.active_effects[name]
        
        # Пересчёт скорости стрельбы с учётом RAPID_FIRE
        if "RAPID_FIRE" in self.active_effects:
            self.shoot_cooldown = config.RAPID_FIRE_COOLDOWN
        else:
            self.shoot_cooldown = config.BULLET_COOLDOWN

    def draw(self, surface: pygame.Surface, current_time: int = None) -> None:
        """Отрисовка игрока с миганием при неуязвимости.""" 
        if current_time is None:
            current_time = pygame.time.get_ticks()
        
        should_draw = True
        if self.is_invincible:
            should_draw = (current_time // 100) % 2 == 0
        
        if should_draw:
            surface.blit(self.image, self.rect)

    def take_damage(self, damage: int, current_time: int) -> None:
        """Получение урона с активацией неуязвимости."""
        if not self.is_invincible:
            self.hp -= damage
            if self.hp <= 0:
                self.lives -= 1
                if self.lives > 0:
                    self.hp = self.max_hp
            self.is_invincible = True
            self.invincibility_timer = current_time

    def is_alive(self) -> bool:
        """Проверка, жив ли игрок."""
        return self.lives > 0 and self.hp > 0
