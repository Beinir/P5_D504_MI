
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
        self.assertEqual(len(x.attributes), Tetromino.CHROMOSOME_SIZE)

        # Checks that all attributes of a chromosome is between -10 and 10
        for i in range(len(x.attributes)):
            with self.subTest(i=i):
                self.assertTrue((-10 < x.attributes[i]) & (x.attributes[i] < 10))

    def test_create_population(self):
        self.assertEqual(Tetromino.POPULATION_SIZE, len(self.population))

        # Check that population only contains chromosome
        for i in range(len(self.population)):
            with self.subTest(i=i):
                self.assertIsInstance(self.population[i], Chromosome)

    def test_crossover(self):
        offspring = Tetromino.crossover(self.population)

        self.assertNotEqual(self.population, offspring)
        self.assertEqual(len(offspring), Tetromino.POPULATION_SIZE/2)  # Crossover creates half a new population

    def test_selection(self):
        new_population = Tetromino.selection(self.population)

        self.assertNotEqual(self.population, new_population)
        self.assertEqual(len(new_population), Tetromino.POPULATION_SIZE)
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

        self.assertEqual(aggregate_height, 0)

    def test_get_aggregate_height_board_1(self):
        aggregate_height = Tetromino.get_aggregate_height(TestGenetic.board_1)

        self.assertEqual(aggregate_height, 34)

    def test_get_aggregate_height_board_2(self):
        aggregate_height = Tetromino.get_aggregate_height(TestGenetic.board_2)

        self.assertEqual(aggregate_height, 34)

    def test_get_aggregate_height_board_3(self):
        aggregate_height = Tetromino.get_aggregate_height(TestGenetic.board_3)

        self.assertEqual(aggregate_height, 250)

    def test_get_aggregate_height_board_4(self):
        aggregate_height = Tetromino.get_aggregate_height(TestGenetic.board_4)

        self.assertEqual(aggregate_height, 985)
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

        self.chromosome.attributes[0] = -2
        self.chromosome.attributes[1] = 10
        self.chromosome.attributes[2] = -2

        best_move = Tetromino.find_best_move(board, piece, self.chromosome)

        self.assertEqual(best_move, [1, 4])

if __name__ == '__main__':
    unittest.main()


