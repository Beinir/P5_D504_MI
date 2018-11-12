
import unittest
import Tetromino
from Tetromino import Chromosome


class TestGenetic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Creates empty board
        TestGenetic.board = Tetromino.get_blank_board()

        # region Create board 1
        TestGenetic.board_1 = Tetromino.get_blank_board()

        # Creates board with 2 holes and 4 aggregate height (left side)
        TestGenetic.board_1[0][19] = "1"
        TestGenetic.board_1[0][17] = "1"
        TestGenetic.board_1[1][19] = "1"
        TestGenetic.board_1[1][18] = "1"
        TestGenetic.board_1[1][17] = "1"
        TestGenetic.board_1[1][16] = "1"
        TestGenetic.board_1[2][19] = "1"
        TestGenetic.board_1[2][17] = "1"
        # endregion

        # region Create board 2
        TestGenetic.board_2 = Tetromino.get_blank_board()

        # Creates board with 2 holes and 4 aggregate height (right side)
        TestGenetic.board_2[7][19] = "1"
        TestGenetic.board_2[7][17] = "1"
        TestGenetic.board_2[8][19] = "1"
        TestGenetic.board_2[8][18] = "1"
        TestGenetic.board_2[8][17] = "1"
        TestGenetic.board_2[8][16] = "1"
        TestGenetic.board_2[9][19] = "1"
        TestGenetic.board_2[9][17] = "1"
        # endregion

        # region Create board 3
        TestGenetic.board_3 = Tetromino.get_blank_board()

        for i in range(0, 10):
            TestGenetic.board_3[i][15] = '1'
        # endregion

        # region Create board 4
        TestGenetic.board_4 = Tetromino.get_blank_board()

        for i in range(0, 10):
            TestGenetic.board_4[i][15 - i] = '1'
        # endregion


    def setUp(self):
        self.population = Tetromino.create_population()
        self.chromosome = Chromosome()
        pass

    # Test start

    # region Genetic algorithm test
    def test_chromosome(self):
        x = Chromosome()

        self.assertEqual(0, x.high_score)
        self.assertEqual(len(x.genes), Tetromino.CHROMOSOME_SIZE)

        # Checks that all genes of a chromosome is between -10 and 10
        for i in range(len(x.genes)):
            with self.subTest(i=i):
                self.assertTrue((-10 < x.genes[i]) & (x.genes[i] < 10))

    def test_create_population(self):
        self.assertEqual(Tetromino.POPULATION_SIZE, len(self.population))

        # Check that population only contains chromosome
        for i in range(len(self.population)):
            with self.subTest(i=i):
                self.assertIsInstance(self.population[i], Chromosome)

    def test_crossover(self):
        parent1 = Chromosome()
        parent2 = Chromosome()

        offspring1, offspring2 = Tetromino.crossover(parent1, parent2)

        self.assertNotEqual(offspring1, parent1)
        self.assertNotEqual(offspring1, parent2)
        self.assertNotEqual(offspring2, parent1)
        self.assertNotEqual(offspring2, parent2)

        for i in range(Tetromino.CHROMOSOME_SIZE):
            with self.subTest(i=i):
                if (i < Tetromino.CHROMOSOME_SIZE / 2):
                    self.assertEqual(offspring1.genes[i], parent1.genes[i])
                    self.assertEqual(offspring2.genes[i], parent2.genes[i])
                else:
                    self.assertEqual(offspring1.genes[i], parent2.genes[i])
                    self.assertEqual(offspring2.genes[i], parent1.genes[i])
    # endregion

    # region Test get_bumpiness
    def test_bumpiness_empty_board(self):
        bumpiness = Tetromino.get_bumpiness(TestGenetic.board)

        self.assertEqual(bumpiness, 0)

    def test_get_bumpiness_populated_board_1(self):
        bumpiness = Tetromino.get_bumpiness(TestGenetic.board_1)

        self.assertEqual(bumpiness, 5)

    def test_get_bumpiness_populated_board_2(self):
        bumpiness = Tetromino.get_bumpiness(TestGenetic.board_2)

        self.assertEqual(bumpiness, 5)

    def test_get_bumpiness_populated_board_3(self):
        bumpiness = Tetromino.get_bumpiness(TestGenetic.board_3)

        self.assertEqual(bumpiness, 0)

    def test_get_bumpiness_populated_board_4(self):
        bumpiness = Tetromino.get_bumpiness(TestGenetic.board_4)

        self.assertEqual(bumpiness, 9)
    # endregion

    # region Test get_number_of_holes
    def test_get_number_of_holes_empty_board(self):
        holes = Tetromino.get_number_of_holes(TestGenetic.board)

        self.assertEqual(holes, 0)

    def test_get_number_of_holes_empty_board_1(self):
        holes = Tetromino.get_number_of_holes(TestGenetic.board_1)

        self.assertEqual(holes, 2)

    def test_get_number_of_holes_empty_board_2(self):
        holes = Tetromino.get_number_of_holes(TestGenetic.board_2)

        self.assertEqual(holes, 2)

    def test_get_number_of_holes_empty_board_3(self):
        holes = Tetromino.get_number_of_holes(TestGenetic.board_3)

        self.assertEqual(holes, 40)

    def test_get_number_of_holes_empty_board_4(self):
        holes = Tetromino.get_number_of_holes(TestGenetic.board_4)

        self.assertEqual(holes, 85)
    # endregion

    # region Test get_aggregate_height
    def test_get_aggregate_height_empty_board(self):
        aggregate_height = Tetromino.get_aggregate_height(Tetromino.get_blank_board())

        height = 0
        result = height * Tetromino.WEIGHT_AGGREGATE_HEIGHT

        self.assertEqual(aggregate_height, result)

    def test_get_aggregate_height_board_1(self):
        aggregate_height = Tetromino.get_aggregate_height(TestGenetic.board_1)

        height = 34
        result = height * Tetromino.WEIGHT_AGGREGATE_HEIGHT

        self.assertEqual(aggregate_height, result)

    def test_get_aggregate_height_board_2(self):
        aggregate_height = Tetromino.get_aggregate_height(TestGenetic.board_2)

        height = 34
        result = height * Tetromino.WEIGHT_AGGREGATE_HEIGHT

        self.assertEqual(aggregate_height, result)

    def test_get_aggregate_height_board_3(self):
        aggregate_height = Tetromino.get_aggregate_height(TestGenetic.board_3)

        height = 250
        result = height * Tetromino.WEIGHT_AGGREGATE_HEIGHT

        self.assertEqual(aggregate_height, result)

    def test_get_aggregate_height_board_4(self):
        aggregate_height = Tetromino.get_aggregate_height(TestGenetic.board_4)

        height = 985
        result = height * Tetromino.WEIGHT_AGGREGATE_HEIGHT

        self.assertEqual(aggregate_height, result)
    # endregion

    def test_get_best_chromosome(self):

        for i in range(len(self.population)):
            self.population[i].high_score = i

        bc = Tetromino.get_best_chromosome(self.population)
        self.assertEqual(bc, self.population[len(self.population) - 1])

        self.population[3].high_score = 100
        bc = Tetromino.get_best_chromosome(self.population)
        self.assertEqual(bc, self.population[3])

    def test_simulate_move(self):
        board = TestGenetic.board

        # Fills the four lowest rows, apart from the last column
        for i in range(0, 9):
            for j in range(16, 20):
                board[i][j] = "1"

        piece = {
            'shape': list(Tetromino.PIECES.keys())[4],
            'rotation': 1,
            'x': int(Tetromino.BOARDWIDTH / 2) - int(Tetromino.TEMPLATEWIDTH / 2),
            'y': -2,  # start it above the board (i.e. less than 0)
            'color': 1
        }

        move = [1, 4]

        new_board = Tetromino.simulate_board(board, piece, move)

        self.assertEqual(new_board[1], 4)
        self.assertEqual(new_board[0], TestGenetic.board)

    def test_find_best_move(self):
        board = TestGenetic.board

        # Fills the four lowest rows, apart from the last column
        for i in range(0, 9):
            for j in range(16, 20):
                board[i][j] = "1"

        piece = {
            'shape': list(Tetromino.PIECES.keys())[4],
            'rotation': 1,
            'x': int(Tetromino.BOARDWIDTH / 2) - int(Tetromino.TEMPLATEWIDTH / 2),
            'y': -2,  # start it above the board (i.e. less than 0)
            'color': 1
        }

        self.chromosome.genes[0] = -2
        self.chromosome.genes[1] = 10
        self.chromosome.genes[2] = -2

        best_move = Tetromino.find_best_move(board, piece, self.chromosome)

        self.assertEqual(best_move, [1, 4])

if __name__ == '__main__':
    unittest.main()


