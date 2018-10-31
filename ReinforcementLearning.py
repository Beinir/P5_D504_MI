import pyautogui as gui
import Tetromino as tet
import copy
import random
import math
import sys
#region Constants
discount_rate = 0.1
learning_rate = 0.5

explore_change = 0.0
min_explore_change = 0.001
decay_rate = 0.99

weights = [-1, -30, 5]
"""
    weights list of four floats:
    * The bumpiness.
    * Number of holes on the board.
    * Score
"""

score = 0
game_score_arr = []  # Array of tuples containing the game number and associated score
game_num = 0
#endregion


def get_bumpiness(board):
    # Calculate the aggregate height of the board, by taking the
    # difference in height between each pair of columns (e.g diff between column 1 and 2)

    heights = [0] * tet.BOARDWIDTH
    bumpiness = 0

    for i in range(0, tet.BOARDWIDTH):  # Selects a column
        for j in range(0, tet.BOARDHEIGHT):  # Goes down from the top of the selected column
            if int(board[i][j]) > 0:
                heights[i] = tet.BOARDHEIGHT - j  # Stores the height of the given column
                break  # breaks to find the height of the next column

    for i in range(tet.BOARDWIDTH - 1):
        highest = max(heights[i], heights[i + 1])
        lowest = min(heights[i], heights[i + 1])
        bumpiness += highest - lowest

    return bumpiness


def make_move(current_move):
    rotation = current_move[0]
    lateral = current_move[1]

    if rotation != 0:
        gui.press('up')
        rotation -= 1
    else:
        if lateral == 0:
            gui.press('space')
        elif lateral < 0:
            gui.press('left')
            lateral += 1
        elif lateral > 0:
            gui.press('right')
            lateral -= 1

    return [rotation, lateral]


def get_parameters(board):
    # Returns number of holes, sum of heights, difference between tallest, shortest column and max height
    holes = 0

    # Finds the number of holes
    for i in range(0, tet.BOARDWIDTH):
        occupied = 0  # For every column occupied is set to 0.
        for j in range(0, tet.BOARDHEIGHT):
            if int(board[i][j]) > 0:  # If the column is occupied, occupied is set to 1
                occupied = 1
            if int(board[i][j]) == 0 and occupied == 1:    # If occupied is 1 and there is a hole,
                                                                # increment holes by 1
                holes += 1

    bumpiness = get_bumpiness(board)

    return bumpiness, holes


def simulate_board(test_board, test_piece, move):
    # This function simulates placing the current falling piece onto the
    # board, specified by 'move,' an array with two elements, 'rot' and 'sideways'.
    # 'rot' gives the number of times the piece is to be rotated ranging in [0:3]
    # 'sideways' gives the horizontal movement from the piece's current position, in [-9:9]
    # It removes complete lines and gives returns the next board state as well as the number
    # of lines cleared.

    rot = move[0]
    sideways = move[1]
    test_lines_removed = 0
    if test_piece is None:
        return None

    # Rotate test_piece to match the desired move
    for i in range(0, rot):
        test_piece['rotation'] = (test_piece['rotation'] + 1) % len(tet.SHAPES[test_piece['shape']])

    # Test for move validity!
    if not tet.is_valid_position(test_board, test_piece, adj_x=sideways, adj_y=0):
        # The move itself is not valid!
        return None

    # Move the test_piece to collide on the board
    test_piece['x'] += sideways
    for i in range(0, tet.BOARDHEIGHT):
        if tet.is_valid_position(test_board, test_piece, adj_x=0, adj_y=1):
            test_piece['y'] = i

    # Place the piece on the virtual board
    if tet.is_valid_position(test_board, test_piece, adj_x=0, adj_y=0):
        tet.add_to_board(test_board, test_piece)
        test_lines_removed, test_board = tet.remove_complete_lines(test_board)

    return test_board, test_lines_removed


def get_expected_score(test_board, weights):
    bumpiness, diff_heights, max_height, holes = get_parameters(test_board)
    A = weights[0]
    B = weights[1]
    C = weights[2]
    D = weights[3]
    return float(A * bumpiness + B * diff_heights + C * (max_height ** 2) + D * (holes ** 2))


def get_next_move_expected_score(board, piece, weights):
    scores = []

    for rot in range(0, len(tet.SHAPES[piece['shape']])):
        for sideways in range(-5, 6):
            move = [rot, sideways]
            test_board = copy.deepcopy(board)
            test_piece = copy.deepcopy(piece)
            test_board = simulate_board(test_board, test_piece, move)
            if test_board is not None:
                scores.append(get_one_step_reward(test_board[1], get_parameters(test_board[0]), weights))

    return max(scores)


def get_one_step_reward(score, params, weights):
    return float(params[0] * weights[0] + params[1] * weights[1] + score * weights[2])


# def find_best_move(board, piece, weights, explore_change):
#     move_list = []
#     score_list = []
#     for rot in range(0, len(tet.SHAPES[piece['shape']])):
#         for lateral in range(-5, 6):
#             move = [rot, lateral]
#             test_board = copy.deepcopy(board)
#             test_piece = copy.deepcopy(piece)
#             test_board = simulate_board(test_board, test_piece, move)
#             if test_board is not None:
#                 move_list.append(move)
#                 test_score = get_one_step_reward(test_board[1], get_parameters(test_board[0]), weights)
#                 # test_score = get_expected_score(test_board[0], weights)
#                 # test_score = float(test_board[1])
#                 score_list.append(test_score)
#     best_score = max(score_list)
#     best_move = move_list[score_list.index(best_score)]
#
#     if random.random() < explore_change:
#         return move_list[random.randint(0, len(move_list) - 1)]
#     else:
#         return best_move


def get_quality(current_piece_score, next_piece_score, params, weights):
    reward = get_one_step_reward(next_piece_score - current_piece_score, params, weights)
    return current_piece_score + learning_rate * (reward + discount_rate * next_piece_score - current_piece_score)


def find_best_move(board, piece, weights, explore_change, next_piece):
    move_list = []
    both_score_list = [[]]
    score_list = []
    board_list = []
    old_params = get_parameters(board)
    quality_list = []
    for rot in range(0, len(tet.SHAPES[piece['shape']])):
        for lateral in range(-5, 6):
            move = [rot, lateral]
            test_board = copy.deepcopy(board)
            test_piece = copy.deepcopy(piece)
            test_board = simulate_board(test_board, test_piece, move)
            if test_board is not None:
                new_params = get_parameters(test_board[0])
                params_diff = get_params_diff(new_params, old_params)
                move_list.append(move)
                current_piece_test_score = get_one_step_reward(test_board[1], get_parameters(test_board[0]), weights)
                next_piece_test_score = get_next_move_expected_score(test_board[0], next_piece, weights)
                # score_list.append(current_piece_test_score + next_piece_test_score)
                #score_list.append(get_one_step_reward(next_piece_test_score - current_piece_test_score, params, weights))
                # quality = current_piece_test_score + learning_rate * (get_one_step_reward(next_piece_test_score - current_piece_test_score, params, weights) + discount_rate * next_piece_test_score - current_piece_test_score)
                quality = get_quality(current_piece_test_score, next_piece_test_score, params_diff, weights)
                quality_list.append(quality)
    # if random.random() < explore_change:
    #     return move_list[random.randint(0, len(move_list) - 1)], best_scores
    # else:

    # best_score = max(score_list)
    # best_move = move_list[score_list.index(best_score)]
    # best_scores = both_score_list[score_list.index(best_score)]
    # best_board = board_list[score_list.index(best_score)]
    #
    # score_increase = best_scores[1] - best_scores[0]
    # params = get_parameters(best_board)

    best_quality = max(quality_list)
    best_move = move_list[quality_list.index(best_quality)]

    return best_move, weights


def get_params_diff(new_params, old_params):
    bumpiness_diff = new_params[0] - old_params[0]
    holes_diff = new_params[1] - old_params[1]
    return bumpiness_diff, holes_diff


# def find_move_update_weights(board, piece, weights, explore_change, next_piece):
#     move, test_board, one_step_reward = find_best_move(board, piece, weights, explore_change, next_piece)
#     # test_board = copy.deepcopy(board)
#     # test_piece = copy.deepcopy(piece)
#     # test_board = simulate_board(test_board, test_piece, move)
#     # if next_piece is not None:
#     #     next_weights = find_move_update_weights(test_board, next_piece, weights, explore_change, None)[1]
#     if test_board is not None:
#         params = get_parameters(test_board)
#         one_step_reward = (get_one_step_reward(test_board[1], params, weights))
#
#         for i in range(0, len(weights)):
#             # weights[i] = (1 - learning_rate) * weights[i] + learning_rate * (one_step_reward + discount_rate * next_weights[i] - weights[i])
#             weights[i] = weights[i] + learning_rate * (one_step_reward + discount_rate * next_weights[i] - weights[i])
#
#         regularization_term = abs(sum(weights))
#         for i in range(0, len(weights)):
#             weights[i] = 40 * weights[i] / regularization_term
#             weights[i] = math.floor(1e4 * weights[i]) / 1e4  # Rounds the weights
#         print(weights)
#
#     return move, weights

def update_weights(board, weights, score):
    params = get_parameters(board)
    for i in range(0, len(weights)):
        weights[i] = weights[i]

    return weights