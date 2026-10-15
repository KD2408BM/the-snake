from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

DIRECTION_MAP = {
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
DEFAULT_SPEED = 20
MIN_SPEED = 5
MAX_SPEED = 40
SPEED_STEP = 5

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=BOARD_BACKGROUND_COLOR):
        """Инициализировать игровой объект."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """Отрисовать объект на игровом поле."""
        raise NotImplementedError(
            f'Метод draw() должен быть переопределен в классе '
            f'{self.__class__.__name__}.'
        )

    def draw_cell(self, position=None, body_color=None, with_border=True):
        """Отрисовать одну ячейку."""
        cell_position = self.position if position is None else position
        cell_color = self.body_color if body_color is None else body_color
        rect = pg.Rect(cell_position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, cell_color, rect)
        if with_border:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, occupied_position=None):
        """Инициализировать яблоко."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied_position or [])

    def randomize_position(self, occupied_position):
        """Установить случайную позицию яблока на поле."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in occupied_position:
                break

    def draw(self):
        """Отрисовать яблоко в игровом поле."""
        self.draw_cell()


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        """Инициализировать змейку."""
        super().__init__(body_color=SNAKE_COLOR)
        self.start_position = self.position
        self.reset()
        self.direction = RIGHT

    def get_head_position(self):
        """Вернуть позицию головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновить направление движения змейки."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Переместить змейку на один шаг."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_head_position = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head_position)
        self.position = new_head_position

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовать змейку на игровом поле."""
        if self.last:
            self.draw_cell(
                self.last,
                BOARD_BACKGROUND_COLOR,
                with_border=False
            )

        for position in self.positions:
            self.draw_cell(position)

    def reset(self):
        """Сбросить змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.start_position]
        self.direction = choice(DIRECTIONS)
        self.next_direction = None
        self.last = None


def handle_keys(game_object, speed):
    """Обработать действия пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit

        if event.type != pg.KEYDOWN:
            continue

        if event.key == pg.K_ESCAPE:
            pg.quit()
            raise SystemExit

        new_direction = DIRECTION_MAP.get((game_object.direction, event.key))
        if new_direction is not None:
            game_object.next_direction = new_direction
        elif event.key in (pg.K_PLUS, pg.K_EQUALS, pg.K_KP_PLUS):
            speed = min(MAX_SPEED, speed + SPEED_STEP)
        elif event.key in (pg.K_MINUS, pg.K_KP_MINUS):
            speed = max(MIN_SPEED, speed - SPEED_STEP)
    return speed


def main():
    """Запустить основной игровой цикл."""
    pg.init()

    snake = Snake()
    apple = Apple(snake.positions)
    speed = DEFAULT_SPEED

    while True:
        clock.tick(speed)
        speed = handle_keys(snake, speed)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
