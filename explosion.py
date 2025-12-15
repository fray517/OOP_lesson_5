"""Эффекты взрывов и вспышек."""

from __future__ import annotations

from typing import Tuple

import pygame

import config


class Explosion(pygame.sprite.Sprite):
    """Анимация взрыва при уничтожении врага."""

    def __init__(
        self,
        x: int,
        y: int,
        max_radius: int = 30,
        duration: int = 300,
    ) -> None:
        super().__init__()
        self.max_radius = max_radius
        self.duration = duration
        self.start_time = pygame.time.get_ticks()

        self.image = pygame.Surface(
            (max_radius * 2, max_radius * 2),
            pygame.SRCALPHA,
        )
        self.rect = self.image.get_rect(center=(x, y))

    def update(self) -> None:
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        if elapsed >= self.duration:
            self.kill()
            return

        progress = elapsed / float(self.duration)
        radius = int(self.max_radius * progress)
        alpha = int(255 * (1.0 - progress))

        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(
            self.image,
            (*config.COLOR_YELLOW, alpha),
            (self.max_radius, self.max_radius),
            max(radius, 1),
        )


class HitEffect(pygame.sprite.Sprite):
    """Короткая вспышка при попадании пули."""

    def __init__(
        self,
        x: int,
        y: int,
        radius: int = 10,
        duration: int = 120,
    ) -> None:
        super().__init__()
        self.radius = radius
        self.duration = duration
        self.start_time = pygame.time.get_ticks()

        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self) -> None:
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        if elapsed >= self.duration:
            self.kill()
            return

        progress = elapsed / float(self.duration)
        alpha = int(255 * (1.0 - progress))

        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(
            self.image,
            (*config.COLOR_WHITE, alpha),
            (self.radius, self.radius),
            self.radius,
        )


class PickupEffect(pygame.sprite.Sprite):
    """Вспышка при подборе бонуса."""

    def __init__(
        self,
        x: int,
        y: int,
        radius: int = 16,
        duration: int = 200,
    ) -> None:
        super().__init__()
        self.radius = radius
        self.duration = duration
        self.start_time = pygame.time.get_ticks()

        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self) -> None:
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        if elapsed >= self.duration:
            self.kill()
            return

        progress = elapsed / float(self.duration)
        inner_radius = int(self.radius * (1.0 - progress))
        alpha = int(200 * (1.0 - progress))

        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(
            self.image,
            (*config.COLOR_CYAN, alpha),
            (self.radius, self.radius),
            inner_radius,
        )
