import Tetromino as tet
import ReinforcementLearning as rl
import datetime


def create_and_append_log_file(game_score_arr, explore_change, weights, game_num):
    # Creates the new log
    log = open("log/RL_weights.txt", "a")

    log.write("Date: " + str(datetime.datetime.now()) + "\n")
    log.write("Prototype: 1\n")
    log.write("Game number: " + str(game_score_arr[game_num][0]) + "\n")
    log.write("Score: " + str(game_score_arr[game_num][1]) + "\n")
    log.write("Explore change: " + str(explore_change) + "\n")
    log.write("Weight 0: " + str(weights[0]) + "\n")
    log.write("Weight 1: " + str(weights[1]) + "\n")
    log.write("Weight 2: " + str(weights[2]) + "\n")
    log.write("Weight 3: " + str(weights[3]) + "\n\n")

    log.close()

