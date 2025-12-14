"""
Класс пули.
"""

import pygame
import config


class Bullet(pygame.sprite.Sprite):
    """
    Класс пули, выпускаемой игроком.
    
    Движется вверх и автоматически удаляется при выходе за экран.
    """

    def __init__(
        self,
        x: int,
        y: int,
        speed: int,
        damage: int = 10
    ) -> None:
        """
        Инициализация пули.
        
        Args:
            x: Начальная позиция по оси X.
            y: Начальная позиция по оси Y.
            speed: Скорость движения (отрицательная для движения вверх).
            damage: Урон пули.
        """
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.damage = damage
        self.rect = pygame.Rect(
            int(self.x - config.BULLET_WIDTH // 2),
            int(self.y),
            config.BULLET_WIDTH,
            config.BULLET_HEIGHT
        )
        self.bullet_type = "normal"
        # Создание изображения для совместимости со sprite groups
        self.image = pygame.Surface(
            (config.BULLET_WIDTH, config.BULLET_HEIGHT),
            pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.image,
            config.BULLET_COLOR,
            (0, 0, config.BULLET_WIDTH, config.BULLET_HEIGHT)
        )

    def update(self) -> None:
        """
        Обновление позиции пули и удаление при выходе за экран.
        """
        self.y += self.speed
        self.rect.y = int(self.y)
        
        # Удаление при выходе за экран
        if self.y < -config.BULLET_HEIGHT or \
                self.y > config.SCREEN_HEIGHT:
            self.kill()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовка пули.
        
        Args:
            surface: Поверхность для отрисовки.
        """
        # Отрисовка основного тела пули
        pygame.draw.rect(
            surface,
            config.BULLET_COLOR,
            self.rect
        )
        # Добавляем яркую точку в центре для эффекта свечения
        center_x = self.rect.centerx
        center_y = self.rect.centery
        pygame.draw.circle(
            surface,
            config.COLOR_WHITE,
            (center_x, center_y),
            2
        )
