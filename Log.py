import Tetromino as tet
import datetime


# def create_and_append_log_file(game_score_arr, explore_change, weights, game_num):
#     # Creates the new log
#     log = open("log/RL_weights.txt", "a")
#
#     log.write("Date: " + str(datetime.datetime.now()) + "\n")
#     log.write("Prototype: 1\n")
#     log.write("Game number: " + str(game_score_arr[game_num][0]) + "\n")
#     log.write("Score: " + str(game_score_arr[game_num][1]) + "\n")
#     log.write("Explore change: " + str(explore_change) + "\n")
#     log.write("Weight 0: " + str(weights[0]) + "\n")
#     log.write("Weight 1: " + str(weights[1]) + "\n")
#     log.write("Weight 2: " + str(weights[2]) + "\n\n")
#
#     log.close()

def create_and_append_log_file(game_score_arr, explore_change, weights, game_num):
    # Creates the new log
    log = open("log/Q_Table.txt", "a")

    log.write("Date: " + str(datetime.datetime.now()) + "\n")
    log.write("Prototype: 1\n")
    log.write("Game number: " + str(game_score_arr[game_num][0]) + "\n")
    log.write("Score: " + str(game_score_arr[game_num][1]) + "\n")
    log.write("Explore change: " + str(explore_change) + "\n")
    log.write("Weight 0: " + str(weights[0]) + "\n")
    log.write("Weight 1: " + str(weights[1]) + "\n")
    log.write("Weight 2: " + str(weights[2]) + "\n\n")

    log.close()

def create_log_file(q_table):
    # Opens file to read the number of this log
    file_log_number = open("log/LogNumber.txt", "r")
    number = int(file_log_number.read())
    file_log_number.close()

    # Updates the number for the next log
    file_log_number = open("LogNumber.txt", "w")
    file_log_number.write(str(number + 1))
    file_log_number.close()

    # Creates the new log
    new_file_name = "Log" + str(number)
    log = open(new_file_name, "w+")

    log.write("Date: " + str(datetime.datetime.now()) + "\n")
    log.write("Prototype: 1\n")
    log.write(q_table)
    # log.write("Population: " + str(POPULATION_SIZE) + "\n")
    # log.write("Chromosome size: " + str(CHROMOSOME_SIZE) + "\n")
    # log.write("Mutation: " + str(MUTATION) + "\n\n")

    log.close()

    return number