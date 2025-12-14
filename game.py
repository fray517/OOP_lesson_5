"""
Основной класс игры с логикой состояний.
"""

import pygame
from enum import Enum
from typing import Optional
import config
from player import Player
from enemy import Enemy, spawn_enemy
from bullet import Bullet


class GameState(Enum):
    """Состояния игры."""
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4


class Game:
    """
    Основной класс игры, управляющий состоянием и логикой.
    
    Отвечает за инициализацию, обновление, отрисовку и обработку событий.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        """
        Инициализация игры.
        
        Args:
            screen: Поверхность для отрисовки.
        """
        self.screen = screen
        self.state = GameState.MENU
        self.clock = pygame.time.Clock()
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Игрок
        self.player: Optional[Player] = None
        
        # Игровые параметры
        self.score = 0
        self.wave = 1
        self.difficulty_level = 1
        
        # Таймеры
        self.last_enemy_spawn = 0
        
        # Шрифт для HUD
        try:
            self.font = pygame.font.Font(None, 36)
        except Exception:
            self.font = pygame.font.SysFont('arial', 36)

    def start_game(self) -> None:
        """Начало новой игры."""
        # Очистка групп
        self.all_sprites.empty()
        self.bullets.empty()
        self.enemies.empty()
        
        # Создание игрока
        self.player = Player(
            config.SCREEN_WIDTH // 2 - config.PLAYER_WIDTH // 2,
            config.SCREEN_HEIGHT - config.PLAYER_HEIGHT - 20
        )
        self.all_sprites.add(self.player)
        
        # Сброс параметров
        self.score = 0
        self.wave = 1
        self.difficulty_level = 1
        self.last_enemy_spawn = pygame.time.get_ticks()
        
        self.state = GameState.PLAYING

    def handle_events(self, event: pygame.event.Event) -> None:
        """
        Обработка событий игры.
        
        Args:
            event: Событие Pygame.
        """
        if event.type == pygame.QUIT:
            return
        
        if self.state == GameState.MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    return
        
        elif self.state == GameState.PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.player:
                        current_time = pygame.time.get_ticks()
                        bullet = self.player.shoot(current_time)
                        if bullet:
                            self.bullets.add(bullet)
                            self.all_sprites.add(bullet)
                elif event.key == pygame.K_p:
                    self.state = GameState.PAUSED
        
        elif self.state == GameState.PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.state = GameState.PLAYING
        
        elif self.state == GameState.GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU

    def update(self) -> None:
        """Обновление состояния игры."""
        if self.state != GameState.PLAYING:
            return
        
        if not self.player or not self.player.is_alive():
            self.state = GameState.GAME_OVER
            return
        
        current_time = pygame.time.get_ticks()
        
        # Обработка ввода для движения
        keys = pygame.key.get_pressed()
        if self.player:
            self.player.handle_input(keys)
            self.player.update(current_time)
        
        # Обновление пуль
        self.bullets.update()
        
        # Обновление врагов
        self.enemies.update()
        
        # Спавн врагов
        if (current_time - self.last_enemy_spawn >=
                config.ENEMY_SPAWN_INTERVAL):
            enemy = spawn_enemy("basic", config.SCREEN_WIDTH)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            self.last_enemy_spawn = current_time
        
        # Проверка столкновений пуль и врагов
        for bullet in self.bullets:
            hit_enemies = pygame.sprite.spritecollide(
                bullet,
                self.enemies,
                False
            )
            for enemy in hit_enemies:
                if enemy.take_damage(bullet.damage):
                    self.score += enemy.points
                bullet.kill()
        
        # Проверка столкновений игрока и врагов
        if self.player:
            hit_enemies = pygame.sprite.spritecollide(
                self.player,
                self.enemies,
                True
            )
            for enemy in hit_enemies:
                self.player.take_damage(10, current_time)

    def draw(self) -> None:
        """Отрисовка игры."""
        self.screen.fill(config.COLOR_BLACK)
        
        if self.state == GameState.MENU:
            self.draw_menu()
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
            config.COLOR_WHITE
        )
        title_rect = title.get_rect(
            center=(config.SCREEN_WIDTH // 2, 200)
        )
        self.screen.blit(title, title_rect)
        
        instruction = self.font.render(
            "Нажмите ENTER или SPACE для начала",
            True,
            config.COLOR_WHITE
        )
        inst_rect = instruction.get_rect(
            center=(config.SCREEN_WIDTH // 2, 300)
        )
        self.screen.blit(instruction, inst_rect)

    def draw_game(self) -> None:
        """Отрисовка игрового процесса."""
        # Отрисовка пуль
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Отрисовка врагов
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Отрисовка игрока (для мигания при неуязвимости)
        if self.player:
            self.player.draw(self.screen)
        
        # Отрисовка HUD
        self.draw_hud()

    def draw_hud(self) -> None:
        """Отрисовка интерфейса."""
        # Счёт
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            config.COLOR_WHITE
        )
        self.screen.blit(score_text, (10, 10))
        
        # Жизни и здоровье
        if self.player:
            lives_text = self.font.render(
                f"Lives: {self.player.lives}",
                True,
                config.COLOR_WHITE
            )
            self.screen.blit(lives_text, (10, 50))
            
            hp_text = self.font.render(
                f"HP: {self.player.hp}/{self.player.max_hp}",
                True,
                config.COLOR_WHITE
            )
            self.screen.blit(hp_text, (10, 90))
        
        # Волна
        wave_text = self.font.render(
            f"Wave: {self.wave}",
            True,
            config.COLOR_WHITE
        )
        self.screen.blit(wave_text, (10, 130))

    def draw_paused(self) -> None:
        """Отрисовка экрана паузы."""
        overlay = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        overlay.set_alpha(128)
        overlay.fill(config.COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render(
            "PAUSED",
            True,
            config.COLOR_WHITE
        )
        pause_rect = pause_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        )
        self.screen.blit(pause_text, pause_rect)
        
        instruction = self.font.render(
            "Нажмите P для продолжения",
            True,
            config.COLOR_WHITE
        )
        inst_rect = instruction.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 50)
        )
        self.screen.blit(instruction, inst_rect)

    def draw_game_over(self) -> None:
        """Отрисовка экрана окончания игры."""
        game_over_text = self.font.render(
            "GAME OVER",
            True,
            config.COLOR_RED
        )
        go_rect = game_over_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, 200)
        )
        self.screen.blit(game_over_text, go_rect)
        
        score_text = self.font.render(
            f"Final Score: {self.score}",
            True,
            config.COLOR_WHITE
        )
        score_rect = score_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, 300)
        )
        self.screen.blit(score_text, score_rect)
        
        instruction = self.font.render(
            "Нажмите R для рестарта или ESC для выхода в меню",
            True,
            config.COLOR_WHITE
        )
        inst_rect = instruction.get_rect(
            center=(config.SCREEN_WIDTH // 2, 400)
        )
        self.screen.blit(instruction, inst_rect)
