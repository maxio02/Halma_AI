import pygame
import pygame.gfxdraw
import numpy as np
import math
from heuristics import choose_best_move, get_valid_moves, get_count_of_pieces_in_goal
from constants import GAME_BOARD_SIZE, CAMP_SIZE

player_1_pieces = set()
player_2_pieces = set()
player_pieces = [0, player_1_pieces, player_2_pieces]


def fill_halma_board(board):
    global player_1_pieces, player_2_pieces

    for i in range(CAMP_SIZE):
        for j in range(CAMP_SIZE - i):
            if i == CAMP_SIZE - 1 or j == CAMP_SIZE - 1:
                break
            board[i][j] = 1
            player_1_pieces.add((i, j))

    for i in range(GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1 - CAMP_SIZE, -1):
        for j in range(GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE -1- i % (GAME_BOARD_SIZE - CAMP_SIZE) - 1, -1):
            if i == GAME_BOARD_SIZE - CAMP_SIZE or j == GAME_BOARD_SIZE - CAMP_SIZE:
                break
            board[i][j] = 2
            player_2_pieces.add((i, j))
    return board


def evaluate_next_move():
    pass


def draw_grid(rows, cols, cell_size, margin):
    grid_color = (0, 0, 0)

    # Draw the vertical lines
    for i in range(cols + 1):
        pygame.draw.line(screen, grid_color,
                         (i * cell_size + margin, margin),
                         (i * cell_size + margin, height - margin), 2)

    # Draw the horizontal lines
    for i in range(rows + 1):
        pygame.draw.line(screen, grid_color,
                         (margin, i * cell_size + margin),
                         (width - margin, i * cell_size + margin), 2)


def draw_board(board_array, cell_size):
    for i, row in enumerate(board_array):
        for j, cell in enumerate(row):
            if cell == 1:
                pygame.gfxdraw.filled_circle(screen, math.ceil(i * cell_size + cell_size / 2),
                                             math.ceil(j * cell_size + cell_size / 2), int(cell_size * 0.4), (0, 0, 0))
                pygame.gfxdraw.aacircle(screen, math.ceil(i * cell_size + cell_size / 2),
                                        math.ceil(j * cell_size + cell_size / 2), int(cell_size * 0.4), (0, 0, 0))
            elif cell == 2:
                pygame.gfxdraw.filled_circle(screen, math.ceil(i * cell_size + cell_size / 2),
                                             math.ceil(j * cell_size + cell_size / 2), int(cell_size * 0.4),
                                             (255, 255, 255))
                pygame.gfxdraw.aacircle(screen, math.ceil(i * cell_size + cell_size / 2),
                                        math.ceil(j * cell_size + cell_size / 2), int(cell_size * 0.4), (255, 255, 255))


def draw_valid_moves(valid_moves):
    for spot in valid_moves:
        pygame.draw.rect(screen, (0, 200, 0),
                         (math.ceil(spot[0] * cell_size), math.ceil(spot[1] * cell_size), cell_size, cell_size))


def draw_background(cell_size):
    screen.fill((0, 127, 0))

    for i in range(CAMP_SIZE):
        for j in range(CAMP_SIZE - i):
            if i == CAMP_SIZE - 1 or j == CAMP_SIZE - 1:
                break
            pygame.draw.rect(screen, (0, 150, 90),
                             (math.ceil(i * cell_size), math.ceil(j * cell_size), cell_size, cell_size))

    for i in range(GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1- CAMP_SIZE, -1):
        for j in range(GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1- i % (GAME_BOARD_SIZE - CAMP_SIZE) - 1, -1):
            if i == GAME_BOARD_SIZE - CAMP_SIZE or j == GAME_BOARD_SIZE - CAMP_SIZE:
                break
            pygame.draw.rect(screen, (0, 150, 90),
                             (math.ceil(i * cell_size), math.ceil(j * cell_size), cell_size, cell_size))


def move_piece(from_pos, to_pos, player):
    if player == 1:
        player_1_pieces.remove(from_pos)
        player_1_pieces.add(to_pos)
    elif player == 2:
        player_2_pieces.remove(from_pos)
        player_2_pieces.add(to_pos)
    game_board[from_pos] = 0
    game_board[to_pos] = player


def check_for_win_conditions(board):
    triangle_size = 6

    if get_count_of_pieces_in_goal(board, 2) == 19:
        return 1

    winning_pieces = 0
    for i in range(GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1- triangle_size, -1):
        for j in range(GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1- i % 10 - 1, -1):
            if i == 10 or j == 10:
                break
            if board[i][j] == 1:
                winning_pieces += 1
    if winning_pieces == 19:
        return 2

    return 0


def end_game(winner):
    winning_font = pygame.font.SysFont('Comic Sans MS', 150)
    match winner:
        case 1:
            text_surface = winning_font.render('BLACK WON', False, (0, 0, 0))
        case 2:
            text_surface = winning_font.render('WHITE WON', False, (0, 0, 0))
    screen.blit(text_surface, (0, 500))


if __name__ == '__main__':

    pygame.init()
    size = width, height = 1000, 1000
    screen = pygame.display.set_mode(size)
    running = True
    dragging = False
    game_board = np.zeros((GAME_BOARD_SIZE , GAME_BOARD_SIZE ), dtype=int)
    last_mouse_position = 0, 0
    cell_size = width / GAME_BOARD_SIZE 
    picked_up = 0

    game_board = fill_halma_board(game_board)

    valid_moves = set()
    clock = pygame.time.Clock()
    fps = 60

    while running:

        draw_background(cell_size)

        draw_board(game_board, width / GAME_BOARD_SIZE )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click pushed
                    dragging = True

                    mouse_x, mouse_y = event.pos
                    picked_up_cell_x, picked_up_cell_y = int(mouse_x // (width / GAME_BOARD_SIZE )), int(mouse_y // (width / GAME_BOARD_SIZE ))
                    picked_up = game_board[picked_up_cell_x, picked_up_cell_y]
                    if game_board[picked_up_cell_x][picked_up_cell_y] != 0:
                        valid_moves = get_valid_moves(player_pieces, (picked_up_cell_x, picked_up_cell_y))
                        game_board[picked_up_cell_x, picked_up_cell_y] = 0


            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click released
                    dragging = False

                    mouse_x, mouse_y = event.pos
                    cell_x, cell_y = int(mouse_x // (width / GAME_BOARD_SIZE )), int(mouse_y // (width / GAME_BOARD_SIZE ))
                    if (cell_x, cell_y) in valid_moves:
                        game_board[cell_x, cell_y] = picked_up
                        move_piece((picked_up_cell_x, picked_up_cell_y), (cell_x, cell_y), picked_up)
                        winner = check_for_win_conditions(game_board)
                        if winner in {1, 2}:
                            end_game(winner)
                        from_pos, to_pos = choose_best_move(player_pieces, 2, depth=1  )
                        move_piece(from_pos, to_pos, 2)
                        draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)

                    else:
                        game_board[picked_up_cell_x][picked_up_cell_y] = picked_up
            elif event.type == pygame.MOUSEMOTION:
                last_mouse_position = event.pos

        from_pos, to_pos = choose_best_move(player_pieces, 2, depth=3)
        move_piece(from_pos, to_pos, 2)
        draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)
        pygame.display.flip()
        draw_background(cell_size)

        draw_board(game_board, width / GAME_BOARD_SIZE )
        from_pos, to_pos = choose_best_move(player_pieces, 1, depth=3)
        move_piece(from_pos, to_pos, 1)


        draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)
        if dragging:
            match picked_up:
                case 0:
                    pass
                case 1:
                    draw_valid_moves(valid_moves)
                    draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)
                    pygame.gfxdraw.filled_circle(screen, int(last_mouse_position[0]), int(last_mouse_position[1]),
                                                 int(cell_size * 0.5), (0, 0, 0))
                    pygame.gfxdraw.aacircle(screen, int(last_mouse_position[0]), int(last_mouse_position[1]),
                                            int(cell_size * 0.5), (0, 0, 0))

                case 2:
                    draw_valid_moves(valid_moves)
                    draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)
                    pygame.gfxdraw.filled_circle(screen, int(last_mouse_position[0]), int(last_mouse_position[1]),
                                                 int(cell_size * 0.5), (255, 255, 255))
                    pygame.gfxdraw.aacircle(screen, int(last_mouse_position[0]), int(last_mouse_position[1]),
                                            int(cell_size * 0.5), (255, 255, 255))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()