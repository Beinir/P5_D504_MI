import pyautogui as gui
import Tetromino as tet
import copy
import random
import sys
#region Constants
discount_rate = 0.6
learning_rate = 0.1

explore_change = 1.0
max_explore_change = 1.0
min_explore_change = 0.01
decay_rate = 0.01

weights = [-1, -1, -1, -30]
"""
    weights list of four floats:
    * Sum of all column heights.
    * Absolute column difference.
    * Maximum height on the board.
    * Number of holes on the board.
"""
score = 0
optimal_move = [0, 0]  # [Rotation, Lateral movement]
temp_move = [0, 0]  # [Rotation, Lateral movement]
#endregion


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
    heights = [0] * tet.BOARDWIDTH
    holes = 0

    # Finds the maximum height of each column.
    # Starts at the top of a column and moves down until an occupied block is found.
    for i in range(0, tet.BOARDWIDTH):
        for j in range(0, tet.BOARDHEIGHT):

            if int(board[i][j]) > 0:  # If the cell is occupied the height is stored
                heights[i] = tet.BOARDHEIGHT - j
                break

    # Find the difference between the tallest and shortest columns
    diffs_heights = max(heights) - min(heights)

    # Finds the number of holes
    for i in range(0, tet.BOARDWIDTH):
        occupied = 0  # For every column occupied is set to 0.
        for j in range(0, tet.BOARDHEIGHT):
            if int(board[i][j]) > 0:  # If the column is occupied, occupied is set to 1
                occupied = 1
            if int(board[i][j]) == 0 and occupied == 1:    # If occupied is 1 and there is a hole,
                                                                # increment holes by 1
                holes += 1

    return sum(heights), diffs_heights, max(heights), holes


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
    reference_height = get_parameters(test_board)[0]
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

    height_sum, diff_heights, max_height, holes = get_parameters(test_board)
    one_step_reward = 5 * (test_lines_removed * test_lines_removed) - holes
    return test_board, one_step_reward


def get_expected_score(test_board, weights):
    height_sum, diff_heights, max_height, holes = get_parameters(test_board)
    A = weights[0]
    B = weights[1]
    C = weights[2]
    D = weights[3]
    return float(A * height_sum + B * diff_heights + C * max_height + D * holes)


def find_best_move(board, piece, weights, explore_change):
    move_list = []
    score_list = []
    for rot in range(0, len(tet.SHAPES[piece['shape']])):
        for lateral in range(-5, 6):
            move = [rot, lateral]
            test_board = copy.deepcopy(board)
            #test_board2 = list(test_board)
            test_piece = copy.deepcopy(piece)
            test_board = simulate_board(test_board, test_piece, move)
            if test_board is not None:
                move_list.append(move)
                test_score = get_expected_score(test_board[0], weights)
                score_list.append(test_score)
    best_score = max(score_list)
    best_move = move_list[score_list.index(best_score)]

    if random.random() < explore_change:
        return move_list[random.randint(0, len(move_list) - 1)]
    else:
        return best_move


def get_reward(board, weights, test_score):
    params = get_parameters(board)
    return (test_score * test_score) + weights[0] * params[0] + weights[1] * params[1] + weights[2] * params[2] + weights[3] * params[3]


def reinforcement_learning(board, piece, weights, explore_change):
    move = find_best_move(board, piece, weights, explore_change)
    old_params = get_parameters(board)
    test_board = copy.deepcopy(board)
    test_piece = copy.deepcopy(piece)
    test_board = simulate_board(test_board, test_piece, move)

    if test_board is not None:
        new_params = get_parameters(test_board[0])
        one_step_reward = test_board[1]
    for i in range(0, len(weights)):
        weights[i] = weights[i] + learning_rate * (one_step_reward - old_params[i] + discount_rate * new_params[i])
    return move, weights
