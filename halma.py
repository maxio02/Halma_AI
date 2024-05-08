import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import pygame.gfxdraw
import numpy as np
import math
from heuristics import choose_best_move, get_valid_moves, get_count_of_pieces_in_goal, calculate_distances, game_is_running, choose_random_move
from constants import GAME_BOARD_SIZE, CAMP_SIZE

player_1_pieces = set()
player_2_pieces = set()
player_pieces = [0, player_1_pieces, player_2_pieces]
py_game_interrupt = False
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


def end_game(winner):
    winning_font = pygame.font.SysFont('Comic Sans MS', 150)
    match winner:
        case 1:
            text_surface = winning_font.render('BLACK WON', False, (0, 0, 0))
        case 2:
            text_surface = winning_font.render('WHITE WON', False, (0, 0, 0))
    screen.blit(text_surface, (0, 500))

# 
def play_cmd_move(is_first_to_move = True, player = 1, depth = 2):

    def play_move_and_print_to_cmd():
        from_pos, to_pos = choose_best_move(player_pieces, player, depth)
        draw_background(cell_size)
        move_piece(from_pos, to_pos, player)
        draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)
        draw_board(game_board, width / GAME_BOARD_SIZE )
        print(str(from_pos[1]*GAME_BOARD_SIZE + from_pos[0]) + ' ' + str(to_pos[1]*GAME_BOARD_SIZE + to_pos[0]))
        pygame.display.flip()

    def play_move_from_cmd_input():
        new_move = input()
        from_pos, to_pos = new_move.split(' ')
        from_pos = (int(from_pos)%GAME_BOARD_SIZE, int(from_pos)//GAME_BOARD_SIZE)
        to_pos = (int(to_pos)%GAME_BOARD_SIZE, int(to_pos)// GAME_BOARD_SIZE)
        move_piece(from_pos, to_pos, 2 if 1 else 1)
        draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)
        draw_board(game_board, width / GAME_BOARD_SIZE )

    if is_first_to_move:
        play_move_and_print_to_cmd()
        play_move_from_cmd_input()
    else:
        play_move_from_cmd_input()
        play_move_and_print_to_cmd()

def handle_pygame_inputs():
    global py_game_interrupt
    global running
    global dragging
    global last_mouse_position
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            py_game_interrupt = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click pushed
                dragging = True

                mouse_x, mouse_y = event.pos
                handle_pygame_inputs.picked_up_cell = (int(mouse_x // (width / GAME_BOARD_SIZE )), int(mouse_y // (width / GAME_BOARD_SIZE )))
                handle_pygame_inputs.picked_up = game_board[handle_pygame_inputs.picked_up_cell[0]][handle_pygame_inputs.picked_up_cell[1]]
                if game_board[handle_pygame_inputs.picked_up_cell[0]][handle_pygame_inputs.picked_up_cell[1]] != 0:
                    handle_pygame_inputs.valid_moves = get_valid_moves(player_pieces, handle_pygame_inputs.picked_up_cell, handle_pygame_inputs.picked_up)
                    game_board[handle_pygame_inputs.picked_up_cell[0]][handle_pygame_inputs.picked_up_cell[1]] = 0


        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click released
                dragging = False

                mouse_x, mouse_y = event.pos
                cell_x, cell_y = int(mouse_x // (width / GAME_BOARD_SIZE )), int(mouse_y // (width / GAME_BOARD_SIZE ))
                if (cell_x, cell_y) in handle_pygame_inputs.valid_moves:
                    game_board[cell_x, cell_y] = handle_pygame_inputs.picked_up
                    move_piece(handle_pygame_inputs.picked_up_cell, (cell_x, cell_y), handle_pygame_inputs.picked_up)
                    from_pos, to_pos = choose_best_move(player_pieces, 2, depth=3)
                    move_piece(from_pos, to_pos, 2)
                    draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)

                else:
                    game_board[handle_pygame_inputs.picked_up_cell[0]][handle_pygame_inputs.picked_up_cell[1]] = handle_pygame_inputs.picked_up
        elif event.type == pygame.MOUSEMOTION:
            last_mouse_position = event.pos

    if dragging:
        match handle_pygame_inputs.picked_up:
            case 0:
                pass
            case 1:
                draw_valid_moves(handle_pygame_inputs.valid_moves)
                draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)
                pygame.gfxdraw.filled_circle(screen, int(last_mouse_position[0]), int(last_mouse_position[1]),
                                                int(cell_size * 0.5), (0, 0, 0))
                pygame.gfxdraw.aacircle(screen, int(last_mouse_position[0]), int(last_mouse_position[1]),
                                        int(cell_size * 0.5), (0, 0, 0))

            case 2:
                draw_valid_moves(handle_pygame_inputs.valid_moves)
                draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)
                pygame.gfxdraw.filled_circle(screen, int(last_mouse_position[0]), int(last_mouse_position[1]),
                                                int(cell_size * 0.5), (255, 255, 255))
                pygame.gfxdraw.aacircle(screen, int(last_mouse_position[0]), int(last_mouse_position[1]),
                                        int(cell_size * 0.5), (255, 255, 255))
handle_pygame_inputs.picked_up = 0
handle_pygame_inputs.valid_moves = set()
handle_pygame_inputs.picked_up_cell = (0,0)
if __name__ == '__main__':

    pygame.init()
    size = width, height = 1000, 1000
    screen = pygame.display.set_mode(size)
    running = True
    dragging = False
    game_board = np.zeros((GAME_BOARD_SIZE , GAME_BOARD_SIZE ), dtype=int)
    last_mouse_position = 0, 0
    cell_size = width / GAME_BOARD_SIZE

    game_board = fill_halma_board(game_board)
    calculate_distances()
    clock = pygame.time.Clock()
    fps = 600
    input()
    while game_is_running(player_pieces) and not py_game_interrupt:

        draw_background(cell_size)
        draw_board(game_board, width / GAME_BOARD_SIZE )
        draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)

        move = choose_best_move(player_pieces, 2, depth=1)
        if move is None:
            break
        from_pos, to_pos = move
        move_piece(from_pos, to_pos, 2)
        draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)
        pygame.display.flip()
        draw_background(cell_size)
        
        draw_board(game_board, width / GAME_BOARD_SIZE )

        move = choose_best_move(player_pieces, 1, depth=1)
        if move is None:
            break
        from_pos, to_pos = move
        move_piece(from_pos, to_pos, 1)


        # move = choose_random_move(player_pieces, 1)
        # from_pos, to_pos = move
        # move_piece(from_pos, to_pos, 1)

        handle_pygame_inputs()
        # play_cmd_move(depth=2)

        draw_grid(GAME_BOARD_SIZE + 1, GAME_BOARD_SIZE + 1, width / GAME_BOARD_SIZE , 0)
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()