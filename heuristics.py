import math, copy, numpy as np
from constants import GAME_BOARD_SIZE, CAMP_SIZE
from fixedSizeOrderedDict import FixedSizeOrderedDict
import random, time, sys
player_1_starting_area = set(
    [(x, y) for x in range(CAMP_SIZE) for y in range(CAMP_SIZE - x) if x != (CAMP_SIZE - 1) and y != (CAMP_SIZE - 1)])
player_2_starting_area = set(
    [(x, y) for x in range(GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1 - CAMP_SIZE, -1) for y in range(GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1 - x % (GAME_BOARD_SIZE - CAMP_SIZE) - 1, -1) if x != (GAME_BOARD_SIZE - CAMP_SIZE) and y != (GAME_BOARD_SIZE - CAMP_SIZE)])
player_bases = (0, player_1_starting_area, player_2_starting_area)
calculated_heuristic_values = FixedSizeOrderedDict(max=2000000)
max_length_to_corner = sum([(0 - x) ** 2 + (0 - y) ** 2 for x, y in player_bases[2]])
min_length_to_corner = sum([(0 - x) ** 2 + (0 - y) ** 2 for x, y in player_bases[1]])
heuristical_values_skipped = 0
heuristical_values_calculated = 0
def get_opponent(player):
    return 2 if player == 1 else 1
#try to remember some of the moves

def get_count_of_pieces_in_goal(piece_positions, player):
    return len(player_bases[get_opponent(player)].intersection(piece_positions[player]))


def within_bounds(x, y):
    return 0 <= x <= GAME_BOARD_SIZE - 1 and 0 <= y <= GAME_BOARD_SIZE - 1


def get_valid_moves(piece_positions, position):
    moves = set()
    visited = set()

    # if position in player_bases

    def valid_jump_moves(x, y):
        visited.add((x, y))
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0: continue
                next_x, next_y = x + i, y + j
                if (next_x, next_y) in piece_positions[1] or (next_x, next_y) in piece_positions[2]:
                    land_x, land_y = x + i * 2, y + j * 2
                    if within_bounds(land_x, land_y) and (land_x, land_y) not in visited and (land_x, land_y) not in piece_positions[1] and (land_x, land_y) not in piece_positions[2]:
                        moves.add((land_x, land_y))
                        valid_jump_moves(land_x, land_y)

    for x in range(position[0] - 1, position[0] + 2):
        for y in range(position[1] - 1, position[1] + 2):
            if within_bounds(x, y) and (x, y) not in piece_positions[1] and (x, y) not in piece_positions[2]:
                moves.add((x, y))

    valid_jump_moves(position[0], position[1])

    return moves


def distance_heuristic_best_spot(piece_positions, player):
    min_distance = float('inf')

    for cell in player_bases[get_opponent(player)]:
        if cell not in piece_positions[1] and cell not in piece_positions[2]:
            total_distance = 0
            for position in piece_positions[player]:
                total_distance += math.sqrt((cell[1] - position[1]) ** 2 + (cell[0] - position[0]) ** 2)
            min_distance = min(min_distance, total_distance)
    return min_distance if min_distance != float('inf') else 800


def distance_heuristic_corner(piece_positions, player):
    total_distance = 0
    goal_x, goal_y = (GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1) if player == 1 else (0, 0)

    for x, y in piece_positions[player]:
        total_distance += (goal_x - x) ** 2 + (goal_y - y) ** 2

    return total_distance 

def piece_count_heuristic(piece_positions, player):
    return get_count_of_pieces_in_goal(piece_positions, player)


def mobility_heuristic(piece_positions, player):
    return len(get_all_valid_moves(piece_positions, player))


def get_heuristic_value_for_move(piece_positions, player):
    global heuristical_values_skipped
    global heuristical_values_calculated
    # Weights
    hashable_board = (tuple(piece_positions[1]), tuple(piece_positions[2]), player)
    if hashable_board not in calculated_heuristic_values:
        w1, w2, w3 = 1, 2, 0.02
        normalized_h1 = distance_heuristic_corner(piece_positions, player) / (max_length_to_corner)
        normalized_h2 = piece_count_heuristic(piece_positions, player) / len(player_1_starting_area)
        normalized_h3 = mobility_heuristic(piece_positions, player) / 120 #TODO standardize this value
        # + 
        score = (w1 * (1 - normalized_h1) + w2 * normalized_h2 + w3 * normalized_h3)
        calculated_heuristic_values[hashable_board] = score
        heuristical_values_calculated += 1
        return score
    else:
        heuristical_values_skipped += 1
        return calculated_heuristic_values[hashable_board]
    

def get_random_heuristic_value():
    return random.random()

def minimax(piece_positions, depth, is_maximizing, player):
    if depth == 0:
        return get_heuristic_value_for_move(piece_positions, player)

    if is_maximizing:
        max_eval = float('-inf')
        for move in get_all_valid_moves(piece_positions, player):
            evaluation = minimax(apply_move(piece_positions, move, player), depth - 1, False, get_opponent(player))
            max_eval = max(max_eval, evaluation)
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_all_valid_moves(piece_positions, player):
            evaluation = minimax(apply_move(piece_positions, move, player), depth - 1, True, get_opponent(player))
            min_eval = min(min_eval, evaluation)
        return min_eval


# https://en.wikipedia.org/wiki/Minimax

def alphabeta(piece_positions, depth, alpha, beta, is_maximizing, player):

    if depth == 0:
        return  get_heuristic_value_for_move(piece_positions, get_opponent(player)), piece_positions
        # return  get_random_heuristic_value() + get_heuristic_value_for_move(piece_positions, get_opponent(player)), piece_positions

    if is_maximizing:
        max_eval = float('-inf')
        max_move = None
        for move in get_all_valid_moves(piece_positions, player):
            evaluation, move = alphabeta(apply_move(piece_positions, move, player), depth - 1, alpha, beta, False, get_opponent(player))
            if(evaluation > max_eval):
                max_eval = evaluation
                max_move = move

            if max_eval > beta:
                break
            alpha = max(alpha, max_eval)

        return max_eval, max_move
    else:
        min_eval = float('inf')
        min_move = None
        for move in get_all_valid_moves(piece_positions, player):
            evaluation, move = alphabeta(apply_move(piece_positions, move, player), depth - 1, alpha, beta, True, get_opponent(player))
            if(evaluation < min_eval):
                min_eval = evaluation
                min_move = move

            if min_eval < alpha:
                break
            beta = min(beta, min_eval)


        return min_eval, min_move


def get_all_valid_moves(piece_positions, player):
    moves = set()
    for position in piece_positions[player]:
        for move in get_valid_moves(piece_positions, position):
            moves.add((position, move))  # ((from_x, from_y), (to_x, to_y))
    return moves

    


def apply_move(pieces: list, move, player):
    pieces_copy = pieces[:]

    pieces_copy[1] = pieces[1].copy()
    pieces_copy[2] = pieces[2].copy()

    from_pos, to_pos = move
    pieces_copy[player].remove(from_pos)
    pieces_copy[player].add(to_pos)

    return pieces_copy


def choose_best_move(player_pieces, player, depth=2):
    global heuristical_values_calculated, heuristical_values_skipped
    heuristical_values_calculated = 0
    heuristical_values_skipped = 0
    perf_t = time.perf_counter()
    score, best_move  = alphabeta(player_pieces, depth, float('-inf'), float('inf'), True, player)

    from_pos = player_pieces[player].difference(best_move[player])
    to_pos = best_move[player].difference(player_pieces[player])
    print(f"Eval time: {(time.perf_counter() - perf_t):.5f}", file=sys.stderr)
    print(f"Calculated nodes: {heuristical_values_calculated}", file=sys.stderr)
    print(f"Skipped nodes: {heuristical_values_skipped}", file=sys.stderr)
    return (from_pos.pop(), to_pos.pop())

# def choose_random_move(player_pieces, player):
    
