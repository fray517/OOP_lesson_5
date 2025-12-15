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
    SETTINGS = 5


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
        
        # Sprite groups для оптимизации
        # all_sprites — все спрайты для отрисовки
        self.all_sprites = pygame.sprite.Group()
        # bullets — все пули игрока
        self.bullets = pygame.sprite.Group()
        # enemies — все враги
        self.enemies = pygame.sprite.Group()
        
        # Игрок
        self.player: Optional[Player] = None
        
        # Игровые параметры
        self.score = 0
        self.best_score = 0
        self.wave = 1
        self.base_difficulty = 1  # Стартовая сложность (можно менять в Settings)
        self.difficulty_level = self.base_difficulty
        
        # Система волн
        self.enemies_in_wave = 5  # Количество врагов в первой волне
        self.enemies_spawned = 0  # Количество заспавненных врагов в текущей волне
        self.wave_complete = False  # Флаг завершения волны
        self.wave_pause_timer = 0  # Таймер паузы между волнами
        self.wave_pause_duration = 3000  # Длительность паузы (мс)
        
        # Таймеры
        self.last_enemy_spawn = 0
        self.start_time = 0  # Время начала текущей игры
        
        # Главное меню
        self.menu_options = ["Play", "Settings", "Quit"]
        self.menu_selected = 0
        self.menu_message: Optional[str] = None
        self.menu_message_time = 0
        
        # Шрифт для HUD
        try:
            self.font = pygame.font.Font(None, 36)
        except Exception:
            self.font = pygame.font.SysFont('arial', 36)
    
    def cleanup(self) -> None:
        """
        Периодическая очистка неактивных объектов.
        
        Удаляет объекты, которые были помечены kill(), но ещё не удалены
        из групп. В основном используется для отладки, так как kill()
        автоматически удаляет объекты из sprite groups.
        """
        # Проверяем пули
        for bullet in list(self.bullets):
            if not bullet.alive():
                self.bullets.remove(bullet)
                if bullet in self.all_sprites:
                    self.all_sprites.remove(bullet)
        
        # Проверяем врагов
        for enemy in list(self.enemies):
            if not enemy.alive():
                self.enemies.remove(enemy)
                if enemy in self.all_sprites:
                    self.all_sprites.remove(enemy)

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
        self.difficulty_level = self.base_difficulty
        self.enemies_in_wave = 5
        self.enemies_spawned = 0
        self.wave_complete = False
        self.wave_pause_timer = 0
        self.start_time = pygame.time.get_ticks()
        self.last_enemy_spawn = pygame.time.get_ticks()
        
        self.state = GameState.PLAYING

    def reset_game(self) -> None:
        """
        Полный сброс игры для рестарта.
        
        Сбрасывает положение игрока, очищает группы спрайтов, счёт и волны.
        Используется при рестарте из состояния GAME_OVER.
        """
        self.start_game()
    
    def handle_menu_input(self, event: pygame.event.Event) -> None:
        """
        Обработка ввода в главном меню.
        """
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
        """
        Выполнение выбранного пункта меню.
        """
        option = self.menu_options[self.menu_selected]
        if option == "Play":
            self.start_game()
        elif option == "Settings":
            self.state = GameState.SETTINGS
        elif option == "Quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def handle_pause_input(self, event: pygame.event.Event) -> None:
        """
        Обработка ввода на экране паузы.
        """
        if event.type != pygame.KEYDOWN:
            return
        
        if event.key == pygame.K_p:
            self.state = GameState.PLAYING
        elif event.key == pygame.K_ESCAPE:
            self.state = GameState.MENU

    def handle_settings_input(self, event: pygame.event.Event) -> None:
        """
        Обработка ввода на экране настроек.
        """
        if event.type != pygame.KEYDOWN:
            return
        
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.base_difficulty = max(1, self.base_difficulty - 1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.base_difficulty = min(10, self.base_difficulty + 1)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
            # Возврат в меню
            self.state = GameState.MENU

    def handle_events(self, event: pygame.event.Event) -> None:
        """
        Обработка событий игры.
        
        Args:
            event: Событие Pygame.
        """
        if event.type == pygame.QUIT:
            return
        
        if self.state == GameState.MENU:
            self.handle_menu_input(event)
        elif self.state == GameState.SETTINGS:
            self.handle_settings_input(event)
        
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
            self.handle_pause_input(event)
        
        elif self.state == GameState.GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU

    def update(self) -> None:
        """Обновление состояния игры."""
        if self.state != GameState.PLAYING:
            return
        
        if not self.player or not self.player.is_alive():
            # Обновляем лучший счёт перед переходом в GAME_OVER
            if self.score > self.best_score:
                self.best_score = self.score
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
        
        # Проверка завершения волны (все враги уничтожены)
        if (not self.wave_complete and 
                self.enemies_spawned >= self.enemies_in_wave and
                len(self.enemies) == 0):
            self.wave_complete = True
            self.wave_pause_timer = current_time
        
        # Пауза между волнами
        if self.wave_complete:
            if current_time - self.wave_pause_timer >= self.wave_pause_duration:
                # Переход к следующей волне
                self.wave += 1
                self.enemies_in_wave = 5 + (self.wave - 1) * 2  # Увеличение врагов
                self.enemies_spawned = 0
                self.wave_complete = False
                self.difficulty_level = min(
                    self.base_difficulty + self.wave // 3, 10
                )  # Увеличение сложности с учётом базовой
                self.last_enemy_spawn = current_time
        
        # Спавн врагов (только если волна не завершена)
        if (not self.wave_complete and 
                self.enemies_spawned < self.enemies_in_wave and
                current_time - self.last_enemy_spawn >=
                config.ENEMY_SPAWN_INTERVAL):
            enemy = spawn_enemy("basic", config.SCREEN_WIDTH)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            self.enemies_spawned += 1
            self.last_enemy_spawn = current_time
        
        # Проверка столкновений пуль и врагов (оптимизированная)
        # Используем spritecollide для каждой пули
        # Создаём копию списка пуль, чтобы избежать проблем при удалении
        bullets_to_check = list(self.bullets)
        for bullet in bullets_to_check:
            # Проверяем столкновение пули с группой врагов
            hit_enemies = pygame.sprite.spritecollide(
                bullet,
                self.enemies,
                False
            )
            if hit_enemies:
                # Обрабатываем первое столкновение
                enemy = hit_enemies[0]
                if enemy.take_damage(bullet.damage):
                    # Враг уничтожен — увеличиваем счёт
                    self.score += enemy.points
                    # Здесь можно добавить эффект взрыва (опционально)
                # Пулю удаляем после попадания
                bullet.kill()
        
        # Проверка столкновений игрока и врагов (оптимизированная)
        if self.player and not self.player.is_invincible:
            # Проверяем столкновение игрока с группой врагов
            # True означает автоматическое удаление врагов из группы
            hit_enemies = pygame.sprite.spritecollide(
                self.player,
                self.enemies,
                True
            )
            if hit_enemies:
                # При столкновении игрок получает урон
                # Обрабатываем только первое столкновение за кадр
                self.player.take_damage(10, current_time)

    def draw(self) -> None:
        """Отрисовка игры."""
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
            config.COLOR_WHITE
        )
        title_rect = title.get_rect(
            center=(config.SCREEN_WIDTH // 2, 200)
        )
        self.screen.blit(title, title_rect)
        
        # Пункты меню
        start_y = 260
        spacing = 50
        for idx, option in enumerate(self.menu_options):
            color = config.COLOR_WHITE
            if idx == self.menu_selected:
                color = config.COLOR_YELLOW
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(
                center=(config.SCREEN_WIDTH // 2, start_y + idx * spacing)
            )
            # Подсветка выбранного пункта
            if idx == self.menu_selected:
                highlight_rect = pygame.Rect(
                    text_rect.x - 20,
                    text_rect.y - 5,
                    text_rect.width + 40,
                    text_rect.height + 10
                )
                pygame.draw.rect(
                    self.screen,
                    config.COLOR_CYAN,
                    highlight_rect,
                    border_radius=6
                )
            self.screen.blit(text, text_rect)
        
        # Подсказки
        hint = self.font.render(
            "↑/↓ или W/S — выбор, ENTER/SPACE — подтвердить, ESC — выход",
            True,
            config.COLOR_WHITE
        )
        hint_rect = hint.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 80)
        )
        self.screen.blit(hint, hint_rect)
        
        # Сообщение (например, для Settings)
        if self.menu_message:
            if pygame.time.get_ticks() - self.menu_message_time < 2000:
                message = self.font.render(
                    self.menu_message,
                    True,
                    config.COLOR_YELLOW
                )
                msg_rect = message.get_rect(
                    center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 130)
                )
                self.screen.blit(message, msg_rect)
            else:
                self.menu_message = None

    def draw_game(self) -> None:
        """
        Отрисовка игрового процесса.
        
        Использует sprite groups для оптимизированной отрисовки.
        """
        current_time = pygame.time.get_ticks()
        
        # Автоматическая отрисовка базовых спрайтов через sprite groups
        # group.draw() использует атрибуты image и rect для отрисовки
        # Для пуль используем кастомный метод draw() (с яркой точкой)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Для врагов используем group.draw() для базовой отрисовки
        self.enemies.draw(self.screen)
        
        # Дополнительная отрисовка кастомных элементов
        # (индикатор здоровья для врагов)
        for enemy in self.enemies:
            # Отрисовка индикатора здоровья поверх базового спрайта
            if enemy.max_hp > 0:
                bar_width = enemy.rect.width
                bar_height = 4
                bar_x = enemy.rect.x
                bar_y = enemy.rect.y - 8
                
                # Фон полоски (красный)
                pygame.draw.rect(
                    self.screen,
                    config.COLOR_RED,
                    (bar_x, bar_y, bar_width, bar_height)
                )
                
                # Здоровье (зелёный)
                health_width = int(
                    bar_width * (enemy.hp / enemy.max_hp)
                )
                if health_width > 0:
                    pygame.draw.rect(
                        self.screen,
                        config.COLOR_GREEN,
                        (bar_x, bar_y, health_width, bar_height)
                    )
        
        # Отрисовка игрока (отдельно для мигания при неуязвимости)
        if self.player:
            self.player.draw(self.screen, current_time)
        
        # Отрисовка сообщения о переходе к следующей волне
        if self.wave_complete:
            overlay = pygame.Surface(
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
            )
            overlay.set_alpha(128)
            overlay.fill(config.COLOR_BLACK)
            self.screen.blit(overlay, (0, 0))
            
            next_wave_text = self.font.render(
                f"Wave {self.wave} Complete!",
                True,
                config.COLOR_GREEN
            )
            next_wave_rect = next_wave_text.get_rect(
                center=(
                    config.SCREEN_WIDTH // 2,
                    config.SCREEN_HEIGHT // 2 - 50
                )
            )
            self.screen.blit(next_wave_text, next_wave_rect)
            
            preparing_text = self.font.render(
                f"Preparing Wave {self.wave + 1}...",
                True,
                config.COLOR_WHITE
            )
            preparing_rect = preparing_text.get_rect(
                center=(
                    config.SCREEN_WIDTH // 2,
                    config.SCREEN_HEIGHT // 2
                )
            )
            self.screen.blit(preparing_text, preparing_rect)
        
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
            
            # Полоска здоровья игрока
            bar_width = 160
            bar_height = 12
            bar_x = 10
            bar_y = 120
            pygame.draw.rect(
                self.screen,
                config.COLOR_RED,
                (bar_x, bar_y, bar_width, bar_height)
            )
            hp_width = int(
                bar_width * (self.player.hp / self.player.max_hp)
            )
            if hp_width > 0:
                pygame.draw.rect(
                    self.screen,
                    config.COLOR_GREEN,
                    (bar_x, bar_y, hp_width, bar_height)
                )
        
        # Волна
        wave_text = self.font.render(
            f"Wave: {self.wave}",
            True,
            config.COLOR_WHITE
        )
        self.screen.blit(wave_text, (10, 170))
        
        # Прогресс волны
        if not self.wave_complete:
            progress_text = self.font.render(
                f"Enemies: {self.enemies_spawned}/{self.enemies_in_wave}",
                True,
                config.COLOR_WHITE
            )
            self.screen.blit(progress_text, (10, 210))
        
        # Уровень сложности
        difficulty_text = self.font.render(
            f"Difficulty: {self.difficulty_level}",
            True,
            config.COLOR_WHITE
        )
        self.screen.blit(difficulty_text, (10, 250))
        
        # Таймер игры (мм:сс)
        elapsed_ms = pygame.time.get_ticks() - self.start_time
        elapsed_seconds = elapsed_ms // 1000
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        timer_text = self.font.render(
            f"Time: {minutes:02d}:{seconds:02d}",
            True,
            config.COLOR_WHITE
        )
        self.screen.blit(timer_text, (10, 290))

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
        
        to_menu = self.font.render(
            "ESC — выход в меню",
            True,
            config.COLOR_WHITE
        )
        menu_rect = to_menu.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 90)
        )
        self.screen.blit(to_menu, menu_rect)
    
    def draw_settings(self) -> None:
        """Отрисовка экрана настроек."""
        overlay = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        overlay.fill(config.COLOR_BLACK)
        overlay.set_alpha(220)
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render(
            "Settings",
            True,
            config.COLOR_WHITE
        )
        title_rect = title.get_rect(
            center=(config.SCREEN_WIDTH // 2, 120)
        )
        self.screen.blit(title, title_rect)
        
        # Настройка стартовой сложности
        diff_text = self.font.render(
            "Стартовая сложность:",
            True,
            config.COLOR_WHITE
        )
        diff_rect = diff_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, 200)
        )
        self.screen.blit(diff_text, diff_rect)
        
        value_text = self.font.render(
            f"{self.base_difficulty}",
            True,
            config.COLOR_YELLOW
        )
        value_rect = value_text.get_rect(
            center=(config.SCREEN_WIDTH // 2, 250)
        )
        self.screen.blit(value_text, value_rect)
        
        hint = self.font.render(
            "←/→ или A/D — изменить, ENTER/SPACE/ESC — назад",
            True,
            config.COLOR_WHITE
        )
        hint_rect = hint.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 100)
        )
        self.screen.blit(hint, hint_rect)

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
        
        # Лучший результат за сессию
        if self.best_score > 0:
            best_text = self.font.render(
                f"Best Score: {self.best_score}",
                True,
                config.COLOR_YELLOW
            )
            best_rect = best_text.get_rect(
                center=(config.SCREEN_WIDTH // 2, 340)
            )
            self.screen.blit(best_text, best_rect)
        
        instruction = self.font.render(
            "Нажмите R для рестарта или ESC для выхода в меню",
            True,
            config.COLOR_WHITE
        )
        inst_rect = instruction.get_rect(
            center=(config.SCREEN_WIDTH // 2, 400)
        )
        self.screen.blit(instruction, inst_rect)
