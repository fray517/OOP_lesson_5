"""Класс бонусов (PowerUp)."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

import config

if TYPE_CHECKING:  # только для типов, без циклических импортов
    from player import Player


POWERUP_TYPES = [
    "HEALTH",
    "LIFE",
    "RAPID_FIRE",
    "DOUBLE_SHOT",
    "TRIPLE_SHOT",
]


class PowerUp(pygame.sprite.Sprite):
    """Падающий бонус для игрока."""

    def __init__(self, x: int, y: int, kind: str) -> None:
        """Создать бонус.

        Args:
            x: Позиция по оси X (центр).
            y: Позиция по оси Y (старт сверху врага).
            kind: Тип бонуса (один из POWERUP_TYPES).
        """
        super().__init__()
        self.kind = kind
        self.speed = config.POWERUP_SPEED

        width = config.POWERUP_WIDTH
        height = config.POWERUP_HEIGHT
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        color = self._get_color()
        pygame.draw.circle(
            self.image,
            color,
            (width // 2, height // 2),
            min(width, height) // 2,
        )

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y

    def _get_color(self) -> tuple[int, int, int]:
        """Цвет бонуса по типу."""
        if self.kind == "HEALTH":
            return config.COLOR_GREEN
        if self.kind == "LIFE":
            return config.COLOR_YELLOW
        if self.kind == "RAPID_FIRE":
            return config.COLOR_CYAN
        if self.kind == "DOUBLE_SHOT":
            return config.COLOR_BLUE
        if self.kind == "TRIPLE_SHOT":
            return config.COLOR_RED
        return config.COLOR_WHITE

    def update(self) -> None:
        """Движение бонуса вниз и удаление за экраном."""
        self.rect.y += self.speed
        if self.rect.top > config.SCREEN_HEIGHT:
            self.kill()

    def apply_effect(self, player: "Player", current_time: int) -> None:
        """Применить эффект бонуса к игроку."""
        if self.kind == "HEALTH":
            heal = config.PLAYER_MAX_HP // 2
            player.hp = min(player.max_hp, player.hp + heal)
        elif self.kind == "LIFE":
            player.lives += 1
        elif self.kind in ("RAPID_FIRE", "DOUBLE_SHOT", "TRIPLE_SHOT"):
            duration = config.POWERUP_DURATION
            expire_at = current_time + duration
            player.active_effects[self.kind] = expire_at

    @staticmethod
    def random_kind() -> str:
        """Случайный тип бонуса с простыми весами."""
        kinds = POWERUP_TYPES
        weights = [3, 1, 2, 2, 1]  # HEALTH/LIFE реже, но RAPID/SHOTS тоже важны
        return random.choices(kinds, weights=weights, k=1)[0]
