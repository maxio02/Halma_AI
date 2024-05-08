from functools import cache
import math, copy, numpy as np
from constants import GAME_BOARD_SIZE, CAMP_SIZE
from fixedSizeOrderedDict import FixedSizeOrderedDict
import random, time, sys

player_1_starting_area = set(
    [(x, y) for x in range(CAMP_SIZE) for y in range(CAMP_SIZE - x) if x != (CAMP_SIZE - 1) and y != (CAMP_SIZE - 1)])
player_2_starting_area = set(
    [(x, y) for x in range(GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1 - CAMP_SIZE, -1) for y in
     range(GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1 - x % (GAME_BOARD_SIZE - CAMP_SIZE) - 1, -1) if
     x != (GAME_BOARD_SIZE - CAMP_SIZE) and y != (GAME_BOARD_SIZE - CAMP_SIZE)])
player_bases = (0, player_1_starting_area, player_2_starting_area)
calculated_heuristic_values = FixedSizeOrderedDict(max=2000000)
max_length_to_corner = sum([math.sqrt((0 - x) ** 2 + (0 - y) ** 2) for x, y in player_bases[2]])
min_length_to_corner = sum([math.sqrt((0 - x) ** 2 + (0 - y) ** 2) for x, y in player_bases[1]])
heuristical_values_skipped = 0
heuristical_values_calculated = 0
move_calculations_skipped = 0
total_calculations = 0
turn = 0
precalculated_distances: dict[tuple[tuple[int, int], int], float] = dict()

def game_is_running(player_pieces):
    for player in range(1,3):
        if len(player_pieces[player] & player_bases[get_opponent(player)]) != len(player_bases[player]):
            return True
    print(f"Player {player} WON!!!", file=sys.stderr)
    return False

def calculate_distances():
    global precalculated_distances
    for player in range(1, 3):
        goal_x, goal_y = (GAME_BOARD_SIZE - 1, GAME_BOARD_SIZE - 1) if player == 1 else (0, 0)
        for cell in [(x, y) for x in range(0, GAME_BOARD_SIZE) for y in range(0, GAME_BOARD_SIZE)]:
            precalculated_distances[cell, player] = math.sqrt(
                (goal_x - cell[0]) ** 2 + (goal_y - cell[1]) ** 2) / max_length_to_corner


def get_opponent(player):
    return 2 if player == 1 else 1


# try to remember some of the moves
def get_count_of_pieces_in_goal(piece_positions, player):
    return len(player_bases[get_opponent(player)] & piece_positions[player])


def within_bounds(position):
    return 0 <= position[0] <= GAME_BOARD_SIZE - 1 and 0 <= position[1] <= GAME_BOARD_SIZE - 1

def valid_jump_moves(position, occupied_positions, player):
    stack = [position]
    valid_jump_moves = set()
    visited = set()
    while stack:
        current_position = stack.pop()
        visited.add(current_position)
        for dx, dy in get_valid_moves.directions:
            if (current_position[0] + dx, current_position[1] + dy) in occupied_positions:
                land_pos = (current_position[0] + 2 * dx, current_position[1] + 2 * dy)

                if within_bounds(land_pos) and land_pos not in visited and land_pos not in occupied_positions:
                    if current_position not in player_bases[get_opponent(player)] or land_pos in player_bases[get_opponent(player)]:
                        valid_jump_moves.add(land_pos)
                        stack.append(land_pos)
    return valid_jump_moves

def get_valid_moves(piece_positions, position, player):
    occupied_positions = piece_positions[1] | piece_positions[2]
    moves = set()
    for dx, dy in get_valid_moves.directions:
        move_pos = position[0] + dx, position[1] + dy
        if within_bounds(move_pos) and move_pos not in occupied_positions:
            if position not in player_bases[get_opponent(player)] or move_pos in player_bases[get_opponent(player)]:
                moves.add(move_pos)
    return moves | valid_jump_moves(position, occupied_positions, player)
get_valid_moves.directions = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]


def distance_heuristic_best_spot(piece_positions, player):
    min_distance = float('inf')

    for cell in player_bases[get_opponent(player)]:
        if cell not in piece_positions[1] and cell not in piece_positions[2]:
            total_distance = 0
            for position in piece_positions[player]:
                total_distance += precalculated_distances[position, player]
            min_distance = min(min_distance, total_distance)
    return min_distance if min_distance != float('inf') else 800


def distance_heuristic_corner(piece_positions, player):
    global precalculated_distances
    total_distance = 0
    for cell in piece_positions[player]:
        total_distance += precalculated_distances[cell, player] # 0 - 1

    return total_distance


def piece_count_heuristic(piece_positions, player):
    return get_count_of_pieces_in_goal(piece_positions, player)


def mobility_heuristic(piece_positions, player):
    return len(get_all_valid_moves(piece_positions, player))


def get_heuristic_value_for_move(piece_positions):
    global heuristical_values_skipped
    global heuristical_values_calculated
    hashable_board = tuple(piece_positions[1] | piece_positions[2])
    if hashable_board not in calculated_heuristic_values:
        w1, w2, w3 = 1, 5, 0.02
        normalized_h1 = (1-distance_heuristic_corner(piece_positions, 1)) - (1-distance_heuristic_corner(piece_positions, 2) )
        normalized_h2 = piece_count_heuristic(piece_positions, 1) / len(player_1_starting_area) - piece_count_heuristic(piece_positions, 2) / len(player_1_starting_area)
        normalized_h3 = mobility_heuristic(piece_positions, 1) / 120 -  mobility_heuristic(piece_positions, 2) / 120
        score = (w1 * normalized_h1 + w2 * normalized_h2 + w3 * normalized_h3 + random.random()/1000)
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
        return get_heuristic_value_for_move(piece_positions), piece_positions

    if is_maximizing:
        max_eval = float('-inf')
        max_move = None
        for move in get_all_valid_moves(piece_positions, player):
            evaluation, move = minimax(apply_move(piece_positions, move, player), depth - 1, False, get_opponent(player))

            if evaluation > max_eval:
                max_eval = evaluation
                max_move = move

        return max_eval, max_move
    else:
        min_eval = float('inf')
        min_move = None
        for move in get_all_valid_moves(piece_positions, player):
            evaluation, move = minimax(apply_move(piece_positions, move, player), depth - 1, True, get_opponent(player))
            if evaluation < min_eval:
                min_eval = evaluation
                min_move = move
        return min_eval, min_move

def alphabeta(piece_positions, depth, alpha, beta, is_maximizing, player, sort=True):
    if depth == 0:
        return get_heuristic_value_for_move(piece_positions), piece_positions

    if is_maximizing:
        max_eval = float('-inf')
        max_move = None
        valid_moves = list(get_all_valid_moves(piece_positions, player))
        if depth > 0: valid_moves.sort(key=lambda move: get_heuristic_value_for_move(apply_move(piece_positions, move, player)), reverse=True)
        for move in valid_moves:
            evaluation, move = alphabeta(apply_move(piece_positions, move, player), depth - 1, alpha, beta, False, get_opponent(player), False)
            if evaluation > max_eval:
                max_eval = evaluation
                max_move = move

            if max_eval >= beta:
                break
            alpha = max(alpha, max_eval)

        return max_eval, max_move
    else:
        min_eval = float('inf')
        min_move = None
        valid_moves = list(get_all_valid_moves(piece_positions, player))
        if depth > 0:
            valid_moves.sort(
                key=lambda move: get_heuristic_value_for_move(apply_move(piece_positions, move, player)))
        for move in valid_moves:
            evaluation, move = alphabeta(apply_move(piece_positions, move, player), depth - 1, alpha, beta, True, get_opponent(player), False)
            if evaluation < min_eval:
                min_eval = evaluation
                min_move = move

            if min_eval <= alpha:
                break
            beta = min(beta, min_eval)

        return min_eval, min_move


def get_all_valid_moves(piece_positions, player):
    
    moves = set()
    for position in piece_positions[player]:
        for move in get_valid_moves(piece_positions, position, player):
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
    global heuristical_values_calculated, heuristical_values_skipped, move_calculations_skipped, turn, total_calculations
    heuristical_values_calculated = 0
    heuristical_values_skipped = 0
    move_calculations_skipped = 0
    turn += 1
    # if turn > 150 :
    #     input()
    perf_t = time.perf_counter()
    # score, best_move = minimax(player_pieces, depth, True if player == 1 else False, player )

    # diff = heuristical_values_calculated + heuristical_values_skipped
    # heuristical_values_calculated = 0
    # heuristical_values_skipped = 0
    # move_calculations_skipped = 0
    score, best_move = alphabeta(player_pieces, depth, float('-inf'), float('inf'), True if player == 1 else False, player )
    total_calculations += heuristical_values_skipped + heuristical_values_calculated
    # alphabeta_prune = 100 - diff/(heuristical_values_calculated + heuristical_values_skipped)
    if best_move is None:
        return None
    from_pos = player_pieces[player].difference(best_move[player])
    to_pos = best_move[player].difference(player_pieces[player])
    eval_time = time.perf_counter() - perf_t
    print(f"Turn: {turn}, {str('BLACK') if player == 1 else str('WHITE')}", file=sys.stderr)
    print(f"Eval time: {eval_time:.3f}", file=sys.stderr)
    print(f"Avg time per calculation: {(eval_time / (heuristical_values_skipped + heuristical_values_calculated) * 1000000):.2f}µs", file=sys.stderr)
    print(f"Calculations: {heuristical_values_calculated}", file=sys.stderr)
    print(f"Skipped heuristic calculations: {heuristical_values_skipped}", file=sys.stderr)
    print(f"Average number of calculations per move: {total_calculations/turn}", file=sys.stderr)
    # print(f"Prune percentage: {alphabeta_prune:.2f}% \n", file=sys.stderr)

    return (from_pos.pop(), to_pos.pop())

def choose_random_move(player_pieces, player):
    valid_moves = list(get_all_valid_moves(player_pieces, player))
    return valid_moves[random.randint(0, len(valid_moves)-1)]


