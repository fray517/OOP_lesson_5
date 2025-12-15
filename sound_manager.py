"""Управление звуками и музыкой игры."""

from __future__ import annotations

import os
from typing import Optional

import pygame

import config


class SoundManager:
    """Загрузка и воспроизведение звуковых эффектов и музыки.

    Все методы безопасны: если звуки/музыка не загрузились, вызовы
    просто ничего не делают.
    """

    def __init__(self) -> None:
        self.enabled = True
        self._mixer_ok = False
        self.shoot_sound: Optional[pygame.mixer.Sound] = None
        self.explosion_sound: Optional[pygame.mixer.Sound] = None
        self.powerup_sound: Optional[pygame.mixer.Sound] = None
        self.damage_sound: Optional[pygame.mixer.Sound] = None

        self._init_mixer()
        self._load_sounds()

    def _init_mixer(self) -> None:
        """Инициализировать pygame.mixer, если возможно."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._mixer_ok = True
        except Exception:
            self._mixer_ok = False
            self.enabled = False

    def _load_sounds(self) -> None:
        """Загрузить базовые звуки (если файлы существуют)."""
        if not self._mixer_ok:
            return

        base_dir = os.path.join(os.path.dirname(__file__), "assets", "sounds")

        def load(name: str) -> Optional[pygame.mixer.Sound]:
            path = os.path.join(base_dir, name)
            if not os.path.exists(path):
                return None
            try:
                return pygame.mixer.Sound(path)
            except Exception:
                return None

        self.shoot_sound = load("shoot.wav")
        self.explosion_sound = load("explosion.wav")
        self.powerup_sound = load("powerup.wav")
        self.damage_sound = load("damage.wav")

        # Фоновая музыка (опционально)
        music_path = os.path.join(base_dir, "music.ogg")
        if os.path.exists(music_path) and self._mixer_ok:
            try:
                pygame.mixer.music.load(music_path)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Служебный метод
    # ------------------------------------------------------------------
    def _play(self, sound: Optional[pygame.mixer.Sound]) -> None:
        if not self.enabled or not self._mixer_ok or sound is None:
            return
        try:
            sound.play()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Публичные методы эффектов
    # ------------------------------------------------------------------
    def play_shoot(self) -> None:
        """Звук выстрела."""
        self._play(self.shoot_sound)

    def play_explosion(self) -> None:
        """Звук взрыва."""
        self._play(self.explosion_sound)

    def play_powerup(self) -> None:
        """Звук подбора бонуса."""
        self._play(self.powerup_sound)

    def play_damage(self) -> None:
        """Звук получения урона игроком."""
        self._play(self.damage_sound)

    # ------------------------------------------------------------------
    # Музыка и громкость
    # ------------------------------------------------------------------
    def play_music(self, loop: bool = True) -> None:
        """Воспроизвести фоновую музыку (если загружена)."""
        if not self.enabled or not self._mixer_ok:
            return
        try:
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception:
            pass

    def stop_music(self) -> None:
        if not self._mixer_ok:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def set_volume(self, volume: float) -> None:
        """Установить громкость 0.0–1.0 для всех звуков и музыки."""
        if not self._mixer_ok:
            return
        volume = max(0.0, min(1.0, volume))
        try:
            if self.shoot_sound:
                self.shoot_sound.set_volume(volume)
            if self.explosion_sound:
                self.explosion_sound.set_volume(volume)
            if self.powerup_sound:
                self.powerup_sound.set_volume(volume)
            if self.damage_sound:
                self.damage_sound.set_volume(volume)
            pygame.mixer.music.set_volume(volume)
        except Exception:
            pass
