import pygame
import random
import sys
from typing import List, Tuple

# Grid settings
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
TOP_LEFT_X = 50
TOP_LEFT_Y = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# Shape formats use a 4x4 matrix represented as strings
S = [
    ['.....',
     '.....',
     '..00.',
     '.00..',
     '.....'],
    ['.....',
     '..0..',
     '..00.',
     '...0.',
     '.....'],
]

Z = [
    ['.....',
     '.....',
     '.00..',
     '..00.',
     '.....'],
    ['.....',
     '..0..',
     '.00..',
     '.0...',
     '.....'],
]

I = [
    ['..0..',
     '..0..',
     '..0..',
     '..0..',
     '.....'],
    ['.....',
     '0000.',
     '.....',
     '.....',
     '.....'],
]

O = [
    ['.....',
     '.....',
     '.00..',
     '.00..',
     '.....'],
]

J = [
    ['.....',
     '.0...',
     '.000.',
     '.....',
     '.....'],
    ['.....',
     '..00.',
     '..0..',
     '..0..',
     '.....'],
    ['.....',
     '.....',
     '.000.',
     '...0.',
     '.....'],
    ['.....',
     '..0..',
     '..0..',
     '.00..',
     '.....'],
]

L = [
    ['.....',
     '...0.',
     '.000.',
     '.....',
     '.....'],
    ['.....',
     '..0..',
     '..0..',
     '..00.',
     '.....'],
    ['.....',
     '.....',
     '.000.',
     '.0...',
     '.....'],
    ['.....',
     '.00..',
     '..0..',
     '..0..',
     '.....'],
]

T = [
    ['.....',
     '..0..',
     '.000.',
     '.....',
     '.....'],
    ['.....',
     '..0..',
     '..00.',
     '..0..',
     '.....'],
    ['.....',
     '.....',
     '.000.',
     '..0..',
     '.....'],
    ['.....',
     '..0..',
     '.00..',
     '..0..',
     '.....'],
]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [GREEN, RED, CYAN, YELLOW, BLUE, ORANGE, PURPLE]


class Piece:
    def __init__(self, x: int, y: int, shape: List[List[str]], color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0


def create_grid(locked_positions: dict) -> List[List[Tuple[int, int, int]]]:
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid


def convert_shape_format(piece: Piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))

    return positions


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]):
    accepted_positions = [(j, i) for i in range(GRID_HEIGHT) for j in range(GRID_WIDTH) if grid[i][j] == BLACK]
    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(GRID_WIDTH // 2 - 2, 0, random.choice(SHAPES), random.choice(SHAPE_COLORS))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('arial', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(
        label,
        (
            TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2,
            TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() / 2,
        ),
    )


def draw_grid(surface, grid):
    for i in range(GRID_HEIGHT):
        pygame.draw.line(
            surface, LIGHT_GRAY, (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE), (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE)
        )
    for j in range(GRID_WIDTH):
        pygame.draw.line(
            surface, LIGHT_GRAY, (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT)
        )


def clear_rows(grid, locked):
    cleared_rows = []
    for i in range(GRID_HEIGHT - 1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            cleared_rows.append(i)
            for j in range(GRID_WIDTH):
                locked.pop((j, i), None)

    if cleared_rows:
        cleared_rows_set = set(cleared_rows)
        sorted_positions = sorted(list(locked), key=lambda pos: pos[1])[::-1]
        for key in sorted_positions:
            x, y = key
            drops = sum(1 for row in cleared_rows_set if y < row)
            if drops:
                locked[(x, y + drops)] = locked.pop(key)

    return len(cleared_rows)


def draw_next_shape(piece: Piece, surface):
    font = pygame.font.SysFont('arial', 24, bold=True)
    label = font.render('Next', True, WHITE)

    start_x = TOP_LEFT_X + PLAY_WIDTH + 40
    start_y = TOP_LEFT_Y + PLAY_HEIGHT / 2 - 100

    format = piece.shape[piece.rotation % len(piece.shape)]

    surface.blit(label, (start_x + 10, start_y - 30))
    for i, line in enumerate(format):
        for j, column in enumerate(line):
            if column == '0':
                pygame.draw.rect(
                    surface,
                    piece.color,
                    (start_x + j * BLOCK_SIZE // 2, start_y + i * BLOCK_SIZE // 2, BLOCK_SIZE // 2, BLOCK_SIZE // 2),
                )


def draw_window(surface, grid, score=0):
    surface.fill(GRAY)

    pygame.font.init()
    font = pygame.font.SysFont('arial', 36, bold=True)
    label = font.render('Tetris', True, WHITE)

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2, 10))

    score_font = pygame.font.SysFont('arial', 24, bold=True)
    score_label = score_font.render(f'Score: {score}', True, WHITE)

    surface.blit(score_label, (TOP_LEFT_X + PLAY_WIDTH + 40, TOP_LEFT_Y))

    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            pygame.draw.rect(
                surface,
                grid[i][j],
                (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
            )

    draw_grid(surface, grid)
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)


def main():
    pygame.init()
    surface = pygame.display.set_mode((TOP_LEFT_X * 2 + PLAY_WIDTH + 200, TOP_LEFT_Y * 2 + PLAY_HEIGHT))
    pygame.display.set_caption('Tetris')

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.6
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        shape_pos = convert_shape_format(current_piece)

        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            cleared = clear_rows(grid, locked_positions)
            if cleared:
                score += cleared * 100

        draw_window(surface, grid, score)
        draw_next_shape(next_piece, surface)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(surface, 'GAME OVER', 48, WHITE)
            pygame.display.update()
            pygame.time.delay(2000)
            run = False


def main_menu():
    pygame.init()
    surface = pygame.display.set_mode((TOP_LEFT_X * 2 + PLAY_WIDTH + 200, TOP_LEFT_Y * 2 + PLAY_HEIGHT))
    pygame.display.set_caption('Tetris')
    run = True
    while run:
        surface.fill(GRAY)
        draw_text_middle(surface, 'Press Any Key To Play', 32, WHITE)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()


if __name__ == '__main__':
    main_menu()
