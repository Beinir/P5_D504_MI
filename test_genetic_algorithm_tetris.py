
import unittest
import Tetromino
from Tetromino import Chromosome


class TestGenetic(unittest.TestCase):

    @classmethod
    def setUpClass(cls): #Bliver kaldt en gang før testene
        print('setupClass')


    @classmethod
    def tearDownClass(cls): # Bliver kaldt en gang efter testene
        print('teardownClass')


    def setUp(self):
        # gets run before every test is run, able to create stuff needed before test
        # skal laves med self. foran (pga. instance attributes)
        # Når man bruger instance attributes skal der skrives self. foran igen
        pass


    def tearDown(self):
        # Kunne bruges til at slette filer som metoder laver fx.
        # Bruges til at rydde op
        pass


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
        population = Tetromino.create_population()
        self.assertEqual(Tetromino.POPULATION_SIZE, len(population))

        # Check that population only contains chromosome
        for i in range(len(population)):
            with self.subTest(i=i):
                self.assertIsInstance(population[i], Chromosome)


    def test_crossover(self):
        population = Tetromino.create_population()

        new_population = crossover(population)

        self.assertNotEqual()

    # endregion



if __name__ == '__main__':
    unittest.main()


# class TestGeneticMethods(unittest.TestCase):
#
#     def test_get_best_chromosome_attributes(self):
#         population = create_population()
#
#         best_chromosome = get_best_chromosome(population)
#         for i in range(len(best_chromosome.attributes)):
#             with self.subTest(i=i):
#                 self.assertEqual(best_chromosome.attributes[i], 0)
#
#     def test_create_population_high_score(self):
#         population = create_population()
#
#         for i in range(len(population)):
#             with self.subTest(i=i):
#                 self.assertEqual(population[i].high_score, 0)
