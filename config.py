"""
Константы и настройки игры.
"""

# Размеры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Скорости
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 3

# Интервалы
BULLET_COOLDOWN = 300  # миллисекунды между выстрелами
ENEMY_SPAWN_INTERVAL = 2000  # миллисекунды между спавном врагов

# Здоровье и жизни
PLAYER_MAX_HP = 100
PLAYER_START_LIVES = 3
ENEMY_BASIC_HP = 20

# Размеры объектов
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
ENEMY_WIDTH = 30
ENEMY_HEIGHT = 30

# Цвета
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_CYAN = (0, 255, 255)

# Цвета игровых объектов
PLAYER_COLOR = COLOR_CYAN
BULLET_COLOR = COLOR_YELLOW
ENEMY_COLOR = COLOR_RED

# Неуязвимость
INVINCIBILITY_DURATION = 2000  # миллисекунды
