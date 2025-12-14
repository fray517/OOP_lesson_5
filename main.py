"""
Точка входа в игру.
"""

import pygame
import sys
import config
from game import Game


def main() -> None:
    """Основная функция запуска игры."""
    # Инициализация Pygame
    pygame.init()
    
    # Создание окна
    screen = pygame.display.set_mode(
        (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    )
    pygame.display.set_caption("Top-Down Shooter")
    
    # Создание объекта Clock для контроля FPS
    clock = pygame.time.Clock()
    
    # Создание экземпляра игры
    game = Game(screen)
    
    # Основной цикл игры
    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_events(event)
        
        # Обновление состояния игры
        game.update()
        
        # Отрисовка игры
        game.draw()
        
        # Ограничение FPS
        clock.tick(config.FPS)
    
    # Корректное закрытие
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
