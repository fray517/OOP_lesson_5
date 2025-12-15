"""Основной класс игры с логикой состояний.

Включает волны врагов, бонусы, эффекты, HUD и звуки.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
import random

import pygame

import config
from bullet import Bullet
from enemy import Enemy, spawn_enemy
from explosion import Explosion, HitEffect, PickupEffect
from player import Player
from powerup import PowerUp
from sound_manager import SoundManager


class GameState(Enum):
    """Состояния игры."""

    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    SETTINGS = 5


class Game:
    """Основной класс игры, управляющий состоянием и логикой."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Инициализация игры."""
        self.screen = screen
        self.state = GameState.MENU
        self.clock = pygame.time.Clock()

        # Менеджер звука
        self.sound = SoundManager()

        # Группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()

        # Игрок
        self.player: Optional[Player] = None

        # Игровые параметры
        self.score = 0
        self.best_score = 0
        self.wave = 1
        self.base_difficulty = 1
        self.difficulty_level = self.base_difficulty

        # Волны
        self.enemies_in_wave = 5
        self.enemies_spawned = 0
        self.wave_complete = False
        self.wave_pause_timer = 0
        self.wave_pause_duration = 3000

        # Усложнение
        self.base_spawn_interval = config.ENEMY_SPAWN_INTERVAL
        self.min_spawn_interval = 500
        self.base_enemy_speed = config.ENEMY_SPEED
        self.max_enemy_speed = 8
        self.base_enemy_hp = config.ENEMY_BASIC_HP
        self.max_enemy_hp = 100

        # Таймеры
        self.last_enemy_spawn = 0
        self.start_time = 0

        # Главное меню
        self.menu_options = ["Play", "Settings", "Quit"]
        self.menu_selected = 0
        self.menu_message: Optional[str] = None
        self.menu_message_time = 0

        # Шрифт
        try:
            self.font = pygame.font.Font(None, 36)
        except Exception:
            self.font = pygame.font.SysFont("arial", 36)

    # ------------------------------------------------------------------
    # Запуск / рестарт
    # ------------------------------------------------------------------
    def start_game(self) -> None:
        """Начало новой игры."""
        self.all_sprites.empty()
        self.bullets.empty()
        self.enemies.empty()
        self.powerups.empty()
        self.effects.empty()

        self.player = Player(
            config.SCREEN_WIDTH // 2 - config.PLAYER_WIDTH // 2,
            config.SCREEN_HEIGHT - config.PLAYER_HEIGHT - 20,
        )
        self.all_sprites.add(self.player)

        self.score = 0
        self.wave = 1
        self.difficulty_level = self.base_difficulty
        self.enemies_in_wave = 5
        self.enemies_spawned = 0
        self.wave_complete = False
        self.wave_pause_timer = 0

        now = pygame.time.get_ticks()
        self.last_enemy_spawn = now
        self.start_time = now

        # Запуск музыки (если доступна)
        self.sound.play_music(loop=True)

        self.state = GameState.PLAYING

    def reset_game(self) -> None:
        """Полный сброс игры для рестарта."""
        self.start_game()

    # ------------------------------------------------------------------
    # Обработка ввода по состояниям
    # ------------------------------------------------------------------
    def handle_menu_input(self, event: pygame.event.Event) -> None:
        """Обработка ввода в главном меню."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_selected = (self.menu_selected - 1) % len(
                self.menu_options
            )
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_selected = (self.menu_selected + 1) % len(
                self.menu_options
            )
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._execute_menu_option()
        elif event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _execute_menu_option(self) -> None:
        """Выполнение выбранного пункта меню."""
        option = self.menu_options[self.menu_selected]
        if option == "Play":
            self.start_game()
        elif option == "Settings":
            self.state = GameState.SETTINGS
        elif option == "Quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_pause_input(self, event: pygame.event.Event) -> None:
        """Обработка ввода на экране паузы.""" 
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_p:
            self.state = GameState.PLAYING
        elif event.key == pygame.K_ESCAPE:
            self.state = GameState.MENU

    def handle_settings_input(self, event: pygame.event.Event) -> None:
        """Обработка ввода на экране настроек.""" 
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.base_difficulty = max(1, self.base_difficulty - 1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.base_difficulty = min(10, self.base_difficulty + 1)
        elif event.key in (
            pygame.K_RETURN,
            pygame.K_SPACE,
            pygame.K_ESCAPE,
        ):
            self.state = GameState.MENU

    def handle_events(self, event: pygame.event.Event) -> None:
        """Глобальная обработка событий."""
        if event.type == pygame.QUIT:
            return

        if self.state == GameState.MENU:
            self.handle_menu_input(event)
            return

        if self.state == GameState.SETTINGS:
            self.handle_settings_input(event)
            return

        if self.state == GameState.PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.player:
                    current_time = pygame.time.get_ticks()
                    bullets = self.player.shoot(current_time)
                    if bullets:
                        self.sound.play_shoot()
                        for bullet in bullets:
                            self.bullets.add(bullet)
                            self.all_sprites.add(bullet)
                elif event.key == pygame.K_p:
                    self.state = GameState.PAUSED
            return

        if self.state == GameState.PAUSED:
            self.handle_pause_input(event)
            return

        if self.state == GameState.GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU

    # ------------------------------------------------------------------
    # Логика обновления
    # ------------------------------------------------------------------
    def update(self) -> None:
        """Обновление состояния игры (один кадр)."""
        if self.state != GameState.PLAYING:
            return

        if not self.player or not self.player.is_alive():
            if self.score > self.best_score:
                self.best_score = self.score
            self.state = GameState.GAME_OVER
            return

        current_time = pygame.time.get_ticks()

        # Игрок
        keys = pygame.key.get_pressed()
        if self.player:
            self.player.handle_input(keys)
            self.player.update(current_time)

        # Остальные спрайты
        self.bullets.update()
        self.enemies.update()
        self.powerups.update()
        self.effects.update()

        # Волны и сложность
        self._update_waves_and_difficulty(current_time)

        # Столкновения
        self._handle_collisions(current_time)

    def _update_waves_and_difficulty(self, current_time: int) -> None:
        """Обновление системы волн и параметров сложности."""
        if (not self.wave_complete
                and self.enemies_spawned >= self.enemies_in_wave
                and len(self.enemies) == 0):
            self.wave_complete = True
            self.wave_pause_timer = current_time

        if self.wave_complete:
            if current_time - self.wave_pause_timer >= \
                    self.wave_pause_duration:
                self.wave += 1
                self.enemies_in_wave = 5 + (self.wave - 1) * 2
                self.enemies_spawned = 0
                self.wave_complete = False
                self.difficulty_level = min(
                    self.base_difficulty + self.wave // 3,
                    10,
                )
                self.last_enemy_spawn = current_time

        spawn_interval = max(
            self.base_spawn_interval - (self.difficulty_level - 1) * 150,
            self.min_spawn_interval,
        )
        enemy_type = self._choose_enemy_type()

        base_speed = min(
            self.base_enemy_speed + (self.difficulty_level - 1),
            self.max_enemy_speed,
        )
        base_hp = min(
            self.base_enemy_hp + (self.difficulty_level - 1) * 5,
            self.max_enemy_hp,
        )

        speed_mult, hp_mult = self._get_enemy_multipliers(enemy_type)
        enemy_speed = min(int(base_speed * speed_mult), self.max_enemy_speed)
        enemy_hp = min(int(base_hp * hp_mult), self.max_enemy_hp)

        if (not self.wave_complete
                and self.enemies_spawned < self.enemies_in_wave
                and current_time - self.last_enemy_spawn >= spawn_interval):
            enemy = spawn_enemy(
                enemy_type,
                config.SCREEN_WIDTH,
                speed=enemy_speed,
                hp=enemy_hp,
            )
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            self.enemies_spawned += 1
            self.last_enemy_spawn = current_time

    def _handle_collisions(self, current_time: int) -> None:
        """Обработка всех столкновений спрайтов."""
        # Пули и враги
        bullet_hits = pygame.sprite.groupcollide(
            self.bullets,
            self.enemies,
            False,
            False,
        )
        for bullet, enemies in bullet_hits.items():
            for enemy in enemies:
                if enemy.take_damage(bullet.damage):
                    self.score += enemy.points
                    self._maybe_spawn_powerup(enemy)
                    explosion = Explosion(
                        enemy.rect.centerx,
                        enemy.rect.centery,
                    )
                    self.effects.add(explosion)
                    self.all_sprites.add(explosion)
                    self.sound.play_explosion()
                hit_effect = HitEffect(
                    bullet.rect.centerx,
                    bullet.rect.centery,
                )
                self.effects.add(hit_effect)
                self.all_sprites.add(hit_effect)
                bullet.kill()
                break

        # Игрок и враги
        if self.player and not self.player.is_invincible:
            enemy_hits = pygame.sprite.spritecollide(
                self.player,
                self.enemies,
                True,
            )
            if enemy_hits:
                self.player.take_damage(10, current_time)
                self.sound.play_damage()

        # Игрок и бонусы
        if self.player:
            powerup_hits = pygame.sprite.spritecollide(
                self.player,
                self.powerups,
                True,
            )
            for powerup in powerup_hits:
                powerup.apply_effect(self.player, current_time)
                pickup_effect = PickupEffect(
                    powerup.rect.centerx,
                    powerup.rect.centery,
                )
                self.effects.add(pickup_effect)
                self.all_sprites.add(pickup_effect)
                self.sound.play_powerup()

    def _maybe_spawn_powerup(self, enemy: Enemy) -> None:
        """С шансом создать бонус на месте уничтоженного врага."""
        if random.random() > config.POWERUP_CHANCE:
            return
        kind = PowerUp.random_kind()
        powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, kind)
        self.powerups.add(powerup)
        self.all_sprites.add(powerup)

    def _choose_enemy_type(self) -> str:
        """Выбор типа врага в зависимости от сложности и волны."""
        level = self.difficulty_level
        wave = self.wave

        if level <= 2 and wave < 3:
            return "basic"

        enemy_types = ["basic"]
        if level >= 2 or wave >= 2:
            enemy_types.append("fast")
        if level >= 3 or wave >= 4:
            enemy_types.append("heavy")
        if level >= 5 or wave >= 6:
            enemy_types.append("tank")

        weights: list[int] = []
        for etype in enemy_types:
            if etype == "basic":
                weights.append(4)
            elif etype == "fast":
                weights.append(3)
            elif etype == "heavy":
                weights.append(2)
            elif etype == "tank":
                weights.append(1)

        return random.choices(enemy_types, weights=weights, k=1)[0]

    def _get_enemy_multipliers(self, enemy_type: str) -> tuple[float, float]:
        """Множители скорости и HP для разных типов врагов."""
        if enemy_type == "fast":
            return (1.8, 0.6)
        if enemy_type == "heavy":
            return (0.7, 2.0)
        if enemy_type == "tank":
            return (0.5, 3.0)
        return (1.0, 1.0)

    # ------------------------------------------------------------------
    # Отрисовка
    # ------------------------------------------------------------------
    def draw(self) -> None:
        """Отрисовка текущего состояния игры."""
        self.screen.fill(config.COLOR_BLACK)

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_paused()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

        pygame.display.flip()

    def draw_menu(self) -> None:
        """Отрисовка главного меню."""
        title = self.font.render(
            "Top-Down Shooter",
            True,
            config.COLOR_WHITE,
        )
        title_rect = title.get_rect(
            center=(config.SCREEN_WIDTH // 2, 200),
        )
        self.screen.blit(title, title_rect)

        start_y = 260
        spacing = 50
        for idx, option in enumerate(self.menu_options):
            color = config.COLOR_WHITE
            if idx == self.menu_selected:
                color = config.COLOR_YELLOW
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(
                center=(config.SCREEN_WIDTH // 2, start_y + idx * spacing),
            )
            if idx == self.menu_selected:
                highlight_rect = pygame.Rect(
                    text_rect.x - 20,
                    text_rect.y - 5,
                    text_rect.width + 40,
                    text_rect.height + 10,
                )
                pygame.draw.rect(
                    self.screen,
                    config.COLOR_CYAN,
                    highlight_rect,
                    border_radius=6,
                )
            self.screen.blit(text, text_rect)

        hint = self.font.render(
            "↑/↓ или W/S — выбор, ENTER/SPACE — подтвердить, ESC — выход",
            True,
            config.COLOR_WHITE,
        )
        hint_rect = hint.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 80),
        )
        self.screen.blit(hint, hint_rect)

    def draw_game(self) -> None:
        """Отрисовка игрового процесса."""
        current_time = pygame.time.get_ticks()

        for bullet in self.bullets:
            bullet.draw(self.screen)

        self.enemies.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        for powerup in self.powerups:
            self.screen.blit(powerup.image, powerup.rect)

        self.effects.draw(self.screen)

        if self.player:
            self.player.draw(self.screen, current_time)

        self._draw_wave_overlay()
        self.draw_hud()

    def _draw_wave_overlay(self) -> None:
        """Сообщение о завершении волны."""
        if not self.wave_complete:
            return

        overlay = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        )
        overlay.set_alpha(128)
        overlay.fill(config.COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))

        next_wave_text = self.font.render(
            f"Wave {self.wave} Complete!",
            True,
            config.COLOR_GREEN,
        )
        next_wave_rect = next_wave_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 40),
        )
        self.screen.blit(next_wave_text, next_wave_rect)

        preparing_text = self.font.render(
            f"Preparing Wave {self.wave + 1}...",
            True,
            config.COLOR_WHITE,
        )
        preparing_rect = preparing_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2),
        )
        self.screen.blit(preparing_text, preparing_rect)

    def draw_hud(self) -> None:
        """Отрисовка HUD."""
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            config.COLOR_WHITE,
        )
        self.screen.blit(score_text, (10, 10))

        if self.player:
            lives_text = self.font.render(
                f"Lives: {self.player.lives}",
                True,
                config.COLOR_WHITE,
            )
            self.screen.blit(lives_text, (10, 50))

            hp_text = self.font.render(
                f"HP: {self.player.hp}/{self.player.max_hp}",
                True,
                config.COLOR_WHITE,
            )
            self.screen.blit(hp_text, (10, 90))

            bar_width = 160
            bar_height = 12
            bar_x = 10
            bar_y = 120
            pygame.draw.rect(
                self.screen,
                config.COLOR_RED,
                (bar_x, bar_y, bar_width, bar_height),
            )
            hp_width = int(
                bar_width * (self.player.hp / self.player.max_hp),
            )
            if hp_width > 0:
                pygame.draw.rect(
                    self.screen,
                    config.COLOR_GREEN,
                    (bar_x, bar_y, hp_width, bar_height),
                )

        wave_text = self.font.render(
            f"Wave: {self.wave}",
            True,
            config.COLOR_WHITE,
        )
        self.screen.blit(wave_text, (10, 170))

        if not self.wave_complete:
            progress_text = self.font.render(
                f"Enemies: {self.enemies_spawned}/{self.enemies_in_wave}",
                True,
                config.COLOR_WHITE,
            )
            self.screen.blit(progress_text, (10, 210))

        difficulty_text = self.font.render(
            f"Difficulty: {self.difficulty_level}",
            True,
            config.COLOR_WHITE,
        )
        self.screen.blit(difficulty_text, (10, 250))

        elapsed_ms = pygame.time.get_ticks() - self.start_time
        elapsed_seconds = elapsed_ms // 1000
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        timer_text = self.font.render(
            f"Time: {minutes:02d}:{seconds:02d}",
            True,
            config.COLOR_WHITE,
        )
        self.screen.blit(timer_text, (10, 290))

        if self.player and self.player.active_effects:
            effects_str = ", ".join(sorted(self.player.active_effects))
            effects_text = self.font.render(
                f"Effects: {effects_str}",
                True,
                config.COLOR_CYAN,
            )
            self.screen.blit(effects_text, (10, 330))

        if self.best_score > 0:
            best_text = self.font.render(
                f"Best: {self.best_score}",
                True,
                config.COLOR_YELLOW,
            )
            self.screen.blit(best_text, (10, 370))

    def draw_paused(self) -> None:
        """Отрисовка экрана паузы."""
        overlay = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        )
        overlay.set_alpha(128)
        overlay.fill(config.COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font.render(
            "PAUSED",
            True,
            config.COLOR_WHITE,
        )
        pause_rect = pause_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2),
        )
        self.screen.blit(pause_text, pause_rect)

        instruction = self.font.render(
            "Нажмите P для продолжения",
            True,
            config.COLOR_WHITE,
        )
        inst_rect = instruction.get_rect(
            center=(
                config.SCREEN_WIDTH // 2,
                config.SCREEN_HEIGHT // 2 + 50,
            ),
        )
        self.screen.blit(instruction, inst_rect)

        to_menu = self.font.render(
            "ESC — выход в меню",
            True,
            config.COLOR_WHITE,
        )
        menu_rect = to_menu.get_rect(
            center=(
                config.SCREEN_WIDTH // 2,
                config.SCREEN_HEIGHT // 2 + 90,
            ),
        )
        self.screen.blit(to_menu, menu_rect)

    def draw_settings(self) -> None:
        """Отрисовка экрана настроек."""
        overlay = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        )
        overlay.fill(config.COLOR_BLACK)
        overlay.set_alpha(220)
        self.screen.blit(overlay, (0, 0))

        title = self.font.render(
            "Settings",
            True,
            config.COLOR_WHITE,
        )
        title_rect = title.get_rect(
            center=(config.SCREEN_WIDTH // 2, 120),
        )
        self.screen.blit(title, title_rect)

        diff_text = self.font.render(
            "Стартовая сложность:",
            True,
            config.COLOR_WHITE,
        )
        diff_rect = diff_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, 200),
        )
        self.screen.blit(diff_text, diff_rect)

        value_text = self.font.render(
            f"{self.base_difficulty}",
            True,
            config.COLOR_YELLOW,
        )
        value_rect = value_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, 250),
        )
        self.screen.blit(value_text, value_rect)

        hint = self.font.render(
            "←/→ или A/D — изменить, ENTER/SPACE/ESC — назад",
            True,
            config.COLOR_WHITE,
        )
        hint_rect = hint.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 100),
        )
        self.screen.blit(hint, hint_rect)

    def draw_game_over(self) -> None:
        """Отрисовка экрана окончания игры."""
        game_over_text = self.font.render(
            "GAME OVER",
            True,
            config.COLOR_RED,
        )
        go_rect = game_over_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, 200),
        )
        self.screen.blit(game_over_text, go_rect)

        score_text = self.font.render(
            f"Final Score: {self.score}",
            True,
            config.COLOR_WHITE,
        )
        score_rect = score_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, 300),
        )
        self.screen.blit(score_text, score_rect)

        if self.best_score > 0:
            best_text = self.font.render(
                f"Best Score: {self.best_score}",
                True,
                config.COLOR_YELLOW,
            )
            best_rect = best_text.get_rect(
                center=(config.SCREEN_WIDTH // 2, 340),
            )
            self.screen.blit(best_text, best_rect)

        instruction = self.font.render(
            "Нажмите R для рестарта или ESC для выхода в меню",
            True,
            config.COLOR_WHITE,
        )
        inst_rect = instruction.get_rect(
            center=(config.SCREEN_WIDTH // 2, 400),
        )
        self.screen.blit(instruction, inst_rect)
