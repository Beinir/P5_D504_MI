import pyautogui as gui
import Tetromino as tet
import numpy as np
import pyautogui
import copy
import random


class TabularQLearning:

    action_space = 4
    max_holes = 10 * 17 + 9
    max_bumpiness = 19 * 5
    max_aggregate_height = 19 * 9 + 18
    completed_lines = 4
    state_space = max_holes * max_bumpiness
    pieces = 7
    q_table = np.zeros((max_holes, max_bumpiness, pieces, action_space))

    total_episodes = 500000
    total_test_episodes = 100

    learning_rate = 0.1
    discount_rate = 0.1

    explore_change = 1.0
    max_explore_change = 1.0
    min_explore_change = 0.01
    decay_rate = 0.01

    @staticmethod
    def get_aggregate_height(board):
        # Calculate the aggregate height of the board, by summing the
        # height of each column. Each row have a height penalty based on it's height (e.g. row_1 = 1...row_20 = 20)

        heights = [0] * tet.BOARDWIDTH

        for i in range(0, tet.BOARDWIDTH):  # Selects a column
            for j in range(0, tet.BOARDHEIGHT):  # Goes down from the top of the selected column
                if int(board[i][j]) > 0:
                    height = (tet.BOARDHEIGHT - j)
                    heights[i] = height * (height * 0.1)
                    break  # breaks to find the height of the next column

        return sum(heights)

    @staticmethod
    def get_number_of_holes(board):
        # Calculates the number of holes on the board
        holes = 0

        for i in range(0, tet.BOARDWIDTH):
            filled = False  # Set to True if the current square is occupied by a piece
            for j in range(0, tet.BOARDHEIGHT):
                if int(board[i][j]) > 0 and not filled:
                    filled = True
                if int(board[i][j]) == 0 and filled:  # If current square is empty and an square above it is filled
                    holes += 1

        return holes

    @staticmethod
    def get_bumpiness(board):
        # Calculate the bumpiness of the board, by taking the
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

    # @staticmethod
    # def get_expected_score(test_board, completed_lines, chromosome):
    #     # Calculates the score of a given board state given the attributes of the chromosome
    #     aggregate_height = get_aggregate_height(test_board)
    #     holes = get_number_of_holes(test_board)
    #
    #     a = chromosome.attributes[0]
    #     b = chromosome.attributes[1]
    #     c = chromosome.attributes[2]
    #
    #     expected_score = a * aggregate_height + b * completed_lines + c * holes
    #
    #     return expected_score

    def simulate_board(self, test_board, test_piece, move):
        rot = move[0]
        sideways = move[1]
        game_over = False

        if test_piece is None:
            return None

        for i in range(0, rot):  # TODO: How does this work?
            test_piece['rotation'] = (test_piece['rotation'] + 1) % len(tet.PIECES[test_piece['shape']])

        if not tet.is_valid_position(test_board, test_piece, sideways, 0):
            game_over = True

        test_piece['x'] += sideways
        for i in range(0, tet.BOARDHEIGHT):
            if tet.is_valid_position(test_board, test_piece, 0, 1):
                test_piece['y'] = i

        tet.add_to_board(test_board, test_piece)
        completed_lines, test_board = tet.remove_complete_lines(test_board)

        new_state_index1, new_state_index2 = self.get_params(test_board)

        return new_state_index1, new_state_index2, completed_lines, game_over

    @staticmethod
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

    def get_params(self, board):
        bumpiness = self.get_bumpiness(board)
        holes = self.get_number_of_holes(board)
        return holes, bumpiness

    @staticmethod
    def get_move_from_action(action):
        if action == 0:
            return [1, 0]
        elif action == 1:
            return [0, -1]
        elif action == 2:
            return [0, 1]
        elif action == 3:
            return [0, 0]

    def make_move_get_params(self, action, board):
        move = self.get_move_from_action(action)
        self.make_move(move)
        holes, bumpiness = self.get_params(board)

    @staticmethod
    def get_piece_index(piece):
        # return tet.PIECES.index([piece['shape']])
        return list(tet.PIECES.keys()).index(piece['shape'])

    def q_learn(self):

        for episode in range(self.total_episodes):
            print(episode)
            board = tet.get_blank_board()
            piece = tet.get_new_piece()

            game_over = False

            state_index1 = self.get_number_of_holes(board)
            state_index2 = self.get_bumpiness(board)

            while game_over is not True:
                exp_exp_tradeoff = random.uniform(0, 1)

                piece_index = self.get_piece_index(piece)

                if exp_exp_tradeoff > self.explore_change:
                    action = np.argmax(self.q_table[state_index1, state_index2, piece_index, :])
                else:
                    action = random.randint(0, 3)

                move = self.get_move_from_action(action)
                new_state_index1, new_state_index2, reward, game_over = self.simulate_board(board, piece, move)

                self.q_table[state_index1, state_index2, piece_index, action] = self.q_table[state_index1, state_index2, piece_index, action] + self.learning_rate * (reward + self.discount_rate * np.max(self.q_table[new_state_index1, new_state_index2, piece_index, :]) - self.q_table[state_index1, state_index2, piece_index, action])

                state_index1 = new_state_index1
                state_index2 = new_state_index2
                piece = tet.get_new_piece()

            self.explore_change = self.min_explore_change + (self.max_explore_change - self.min_explore_change) * np.exp(-self.decay_rate * episode)

    def get_best_move_from_q_table(self, board, piece):
        state_index1 = self.get_number_of_holes(board)
        state_index2 = self.get_bumpiness(board)
        piece_index = self.get_piece_index(piece)

        action = np.argmax(self.q_table[state_index1, state_index2, piece_index, :])

        return self.get_move_from_action(action)



