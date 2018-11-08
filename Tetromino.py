# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

# Imports
import random
import time
import pygame
import sys
import math
import copy
import pygame.locals as keys
import pyautogui
import matplotlib.pyplot as plt
import operator
from random import shuffle
import datetime

# genetic variables
MUTATION = 5
CHROMOSOME_SIZE = 3
POPULATION_SIZE = 2  # Population % 2 need to be zero
GENERATION_NUMBER = 1
BEST_CHROMOSOME_IN_GENERATION = None
CURRENT_CHROMOSOME = None
OVERALL_HIGHSCORE = 0
WEIGHT_AGGREGATE_HEIGHT = 0.025
K = 0.75  # Tournament selection parameter

# data plot variables
BEST_CHROMOSOME_GENERATION_HIGH_SCORES = []
GENERATION_NUMBERS = []
AVERAGE_A = []
AVERAGE_B = []
AVERAGE_C = []
AVERAGE_HIGH_SCORE = []

# Define settings and constants
pyautogui.PAUSE = 0.02
pyautogui.FAILSAFE = True


FPS = 50
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '0'
MOVESIDEWAYSFREQ = 0.075
MOVEDOWNFREQ = 0.05

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

# Define Color triplets in RGB
WHITE = (255, 255, 255)
GRAY = (185, 185, 185)
BLACK = (0, 0, 0)
RED = (155, 0, 0)
LIGHTRED = (175, 20, 20)
GREEN = (0, 155, 0)
LIGHTGREEN = (20, 175, 20)
BLUE = (0, 0, 155)
LIGHTBLUE = (20, 20, 175)
YELLOW = (155, 155, 0)
LIGHTYELLOW = (175, 175, 20)
CYAN = (0, 185, 185)
LIGHTCYAN = (0, 255, 255)
MAGENTA = (185, 0, 185)
LIGHTMAGENTA = (255, 0, 255)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS = (GRAY, BLUE, GRAY, GREEN, RED, YELLOW, CYAN, MAGENTA)
LIGHTCOLORS = (WHITE, LIGHTBLUE, WHITE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW,
               LIGHTCYAN, LIGHTMAGENTA)

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['00000', '00000', '00110', '01100', '00000'],
                    ['00000', '00100', '00110', '00010', '00000']]

Z_SHAPE_TEMPLATE = [['00000', '00000', '01100', '00110', '00000'],
                    ['00000', '00100', '01100', '01000', '00000']]

I_SHAPE_TEMPLATE = [['00100', '00100', '00100', '00100', '00000'],
                    ['00000', '00000', '11110', '00000', '00000']]

O_SHAPE_TEMPLATE = [['00000', '00000', '01100', '01100', '00000']]

J_SHAPE_TEMPLATE = [['00000', '01000', '01110', '00000',
                     '00000'], ['00000', '00110', '00100', '00100', '00000'],
                    ['00000', '00000', '01110', '00010',
                     '00000'], ['00000', '00100', '00100', '01100', '00000']]
L_SHAPE_TEMPLATE = [['00000', '00010', '01110', '00000',
                     '00000'], ['00000', '00100', '00100', '00110', '00000'],
                    ['00000', '00000', '01110', '01000',
                     '00000'], ['00000', '01100', '00100', '00100', '00000']]

T_SHAPE_TEMPLATE = [['00000', '00100', '01110', '00000',
                     '00000'], ['00000', '00100', '00110', '00100', '00000'],
                    ['00000', '00000', '01110', '00100',
                     '00000'], ['00000', '00100', '01100', '00100', '00000']]

PIECES = {
    'S': S_SHAPE_TEMPLATE,
    'Z': Z_SHAPE_TEMPLATE,
    'J': J_SHAPE_TEMPLATE,
    'L': L_SHAPE_TEMPLATE,
    'I': I_SHAPE_TEMPLATE,
    'O': O_SHAPE_TEMPLATE,
    'T': T_SHAPE_TEMPLATE
}


def run_game(chromosome):
    """Runs a full game of tetris, learning and updating the policy as the game progresses.

    Arguments:
        weights {list} -- list of four floats, defining the piece placement policy and denoting the respective weighting
                          of the four features:
                            * Sum of all column heights
                            * Sum of absolute column differences
                            * Maximum height on the board
                            * Number of holes on the board
        explore_change {float} -- A float between 0 and 1 which determines the probability that a random move will be
                                   selected instead of the best move per the current policy.

    Returns:
        score {int} -- The integer score of the finished game.
        weights {list} -- The same list as the argument, piped to allow for persistent learning across games.
        explore_change {float} -- The same parameter as the input argument, piped to allow for persistent learning
                                    across games.
    """

    # setup variables for the start of the game
    board = get_blank_board()
    last_move_down_time = time.time()
    last_lateral_time = time.time()
    last_fall_time = time.time()
    moving_down = False  # note: there is no movingUp variable
    moving_left = False
    moving_right = False
    score = 0
    level, fall_freq = get_level_and_fall_freq(score)
    current_move = [0, 0]  # Relative Rotation, lateral movement
    falling_piece = get_new_piece()
    next_piece = get_new_piece()

    while True:  # game loop

        if falling_piece is None:
            # No falling piece in play, so start a new piece at the top
            falling_piece = next_piece
            next_piece = get_new_piece()
            last_fall_time = time.time()  # reset last_fall_time

            if not is_valid_position(board, falling_piece):
                return

            current_move = find_best_move(board, falling_piece, chromosome)

        check_for_quit()
        current_move = make_move(current_move)
        for event in pygame.event.get():  # event handling loop
            if event.type == keys.KEYUP:
                if event.key == keys.K_p:
                    # Pausing the game
                    DISPLAYSURF.fill(BGCOLOR)
                    show_text_screen('Paused')  # pause until a key press
                    last_fall_time = time.time()
                    last_move_down_time = time.time()
                    last_lateral_time = time.time()
                elif (event.key == keys.K_LEFT or event.key == keys.K_a):
                    moving_left = False
                elif (event.key == keys.K_RIGHT or event.key == keys.K_d):
                    moving_right = False
                elif (event.key == keys.K_DOWN or event.key == keys.K_s):
                    moving_down = False

            elif event.type == keys.KEYDOWN:
                # moving the piece sideways
                if (event.key == keys.K_LEFT or event.key == keys.K_a) and is_valid_position(
                            board, falling_piece, adj_x=-1):
                    falling_piece['x'] -= 1
                    moving_left = True
                    moving_right = False
                    last_lateral_time = time.time()

                elif (event.key == keys.K_RIGHT or event.key == keys.K_d) and is_valid_position(
                          board, falling_piece, adj_x=1):
                    falling_piece['x'] += 1
                    moving_right = True
                    moving_left = False
                    last_lateral_time = time.time()

                # rotating the piece (if there is room to rotate)
                elif (event.key == keys.K_UP or event.key == keys.K_w):
                    falling_piece[
                        'rotation'] = (falling_piece['rotation'] + 1) % len(
                            PIECES[falling_piece['shape']])
                    if not is_valid_position(board, falling_piece):
                        falling_piece[
                            'rotation'] = (falling_piece['rotation'] - 1) % len(
                                PIECES[falling_piece['shape']])
                elif (event.key == keys.K_q):  # rotate the other direction
                    falling_piece[
                        'rotation'] = (falling_piece['rotation'] - 1) % len(
                            PIECES[falling_piece['shape']])
                    if not is_valid_position(board, falling_piece):
                        falling_piece[
                            'rotation'] = (falling_piece['rotation'] + 1) % len(
                                PIECES[falling_piece['shape']])

                # making the piece fall faster with the down key
                elif (event.key == keys.K_DOWN or event.key == keys.K_s):
                    moving_down = True
                    if is_valid_position(board, falling_piece, adj_y=1):
                        falling_piece['y'] += 1
                    last_move_down_time = time.time()

                # move the current piece all the way down
                elif event.key == keys.K_SPACE:
                    moving_down = False
                    moving_left = False
                    moving_right = False
                    for i in range(1, BOARDHEIGHT):
                        if not is_valid_position(board, falling_piece, adj_y=i):
                            break
                    falling_piece['y'] += i - 1

        # handle moving the piece because of user input
        if (moving_left or moving_right) and time.time() - last_lateral_time > MOVESIDEWAYSFREQ:
            if moving_left and is_valid_position(board, falling_piece, adj_x=-1):
                falling_piece['x'] -= 1
            elif moving_right and is_valid_position(board, falling_piece, adj_x=1):
                falling_piece['x'] += 1
            last_lateral_time = time.time()

        if moving_down and time.time(
        ) - last_move_down_time > MOVEDOWNFREQ and is_valid_position(
                board, falling_piece, adj_y=1):
            falling_piece['y'] += 1
            last_move_down_time = time.time()

        # let the piece fall if it is time to fall
        if time.time() - last_fall_time > fall_freq:
            # see if the piece has landed
            if not is_valid_position(board, falling_piece, adj_y=1):
                # falling piece has landed, set it on the board
                add_to_board(board, falling_piece)
                lines, board = remove_complete_lines(board)
                score += lines * lines
                level, fall_freq = get_level_and_fall_freq(score)
                falling_piece = None
            else:
                # piece did not land, just move the piece down
                falling_piece['y'] += 1
                last_fall_time = time.time()

        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        draw_status(score, level, current_move)
        draw_next_piece(next_piece)
        if falling_piece is not None:
            draw_piece(falling_piece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

        chromosome.high_score = score


def make_text_objs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def make_plots():
    # Plot high score per generation
    plt.figure(1)
    plt.plot(GENERATION_NUMBERS, BEST_CHROMOSOME_GENERATION_HIGH_SCORES)
    plt.xlabel('Generation')
    plt.ylabel('High Score')
    plt.title('Best chromosome high score per generation')
    # plt.axis([1, GENERATION_NUMBER + 1, 0, OVERALL_HIGHSCORE * 1.1])
    plt.xlim(1, GENERATION_NUMBER + 1)
    plt.ylim(0, OVERALL_HIGHSCORE * 1.1)
    plt.grid(True)

    plt.figure(2)
    plt.plot(GENERATION_NUMBERS, AVERAGE_A, 'bo-', label='a')
    plt.plot(GENERATION_NUMBERS, AVERAGE_B, 'ro-', label='b')
    plt.plot(GENERATION_NUMBERS, AVERAGE_C, 'go-', label='c')
    plt.xlabel('Generation')
    plt.ylabel('Value')
    plt.title('Average weights per generation')
    plt.xlim(1, GENERATION_NUMBER + 1)
    plt.ylim(-11, 11)
    plt.grid(True)
    plt.legend()

    plt.figure(3)
    plt.plot(GENERATION_NUMBERS, AVERAGE_HIGH_SCORE)
    plt.xlabel('Generation')
    plt.ylabel('High Score')
    plt.title('Average high score per generation')
    plt.xlim(1, GENERATION_NUMBER + 1)
    plt.ylim(0, max(AVERAGE_HIGH_SCORE) * 1.1)
    plt.grid(True)
    plt.show()


def terminate():
    make_plots()
    pygame.quit()
    sys.exit()


def check_for_key_press():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    check_for_quit()

    for event in pygame.event.get([keys.KEYDOWN, keys.KEYUP]):
        if event.type == keys.KEYDOWN:
            continue
        return event.key
    return None


def show_text_screen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the text
    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the additional "Press a key to play." text.
    press_key_surf, press_key_rect = make_text_objs('Please wait to continue.',
                                                    BASICFONT, TEXTCOLOR)
    press_key_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(press_key_surf, press_key_rect)

    pygame.display.update()
    FPSCLOCK.tick()
    time.sleep(0.5)


def check_for_quit():
    for event in pygame.event.get(keys.QUIT):  # get all the QUIT events
        terminate()  # terminate if any QUIT events are present
    for event in pygame.event.get(keys.KEYUP):  # get all the KEYUP events
        if event.key == keys.K_ESCAPE:
            terminate()  # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event)  # put the other KEYUP event objects back


def get_level_and_fall_freq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fall_freq = 0.07 * math.exp(
        (1 - level) / 3)  # 0.27 - (level * 0.02) default
    return level, fall_freq


def get_new_piece():
    # return a random new piece in a random rotation and color
    shape = random.choice(list(PIECES.keys()))
    new_piece = {
        'shape': shape,
        'rotation': random.randint(0,
                                   len(PIECES[shape]) - 1),
        'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
        'y': -2,  # start it above the board (i.e. less than 0)
        'color': random.randint(1,
                                len(COLORS) - 1)
    }
    return new_piece


def add_to_board(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK and x + piece['x'] < 10 and y + piece['y'] < 20:
                board[x + piece['x']][y + piece['y']] = piece['color']
                # DEBUGGING NOTE: SOMETIMES THIS IF STATEMENT ISN'T
                # SATISFIED, WHICH NORMALLY WOULD RAISE AN ERROR.
                # NOT SURE WHAT CAUSES THE INDICES TO BE THAT HIGH.
                # THIS IS A BAND-AID FIX


def get_blank_board():
    # create and return a new blank board data structure
    board = []
    for _ in range(BOARDWIDTH):
        board.append(['0'] * BOARDHEIGHT)
    return board


def is_on_board(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def is_valid_position(board, piece, adj_x=0, adj_y=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT - 1):
            is_above_board = y + piece['y'] + adj_y < 0
            if is_above_board or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not is_on_board(x + piece['x'] + adj_x, y + piece['y'] + adj_y):
                return False  # The piece is off the board
            if board[x + piece['x'] + adj_x][y + piece['y'] + adj_y] != BLANK:
                return False  # The piece collides
    return True


def is_complete_line(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True


def remove_complete_lines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    lines_removed = 0
    y = BOARDHEIGHT - 1  # start y at the bottom of the board
    while y >= 0:
        if is_complete_line(board, y):
            # Remove the line and pull boxes down by one line.
            for pull_down_y in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pull_down_y] = board[x][pull_down_y - 1]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            lines_removed += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1  # move on to check next row up
    return lines_removed, board


def convert_to_pixel_coords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def draw_box(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == BLANK:
        return
    if pixelx is None and pixely is None:
        pixelx, pixely = convert_to_pixel_coords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color],
                     (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color],
                     (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def draw_board(board):
    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR,
                     (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8,
                      (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(
        DISPLAYSURF, BGCOLOR,
        (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            draw_box(x, y, board[x][y])


def draw_status(score, level, best_move):
    # draw the score text
    score_surf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(score_surf, score_rect)

    # draw the level text
    level_surf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    level_rect = level_surf.get_rect()
    level_rect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(level_surf, level_rect)

    # draw the best_move text
    move_surf = BASICFONT.render('Current Move: %s' % best_move, True, TEXTCOLOR)
    move_rect = move_surf.get_rect()
    move_rect.topleft = (WINDOWWIDTH - 200, 110)
    DISPLAYSURF.blit(move_surf, move_rect)

    # draw generation info
    generation_surf = BASICFONT.render('Generation: %d' % GENERATION_NUMBER, True, TEXTCOLOR)
    generation_rect = generation_surf.get_rect()
    generation_rect.topleft = (WINDOWWIDTH - 625, 20)
    DISPLAYSURF.blit(generation_surf, generation_rect)

    # draw overall highscore
    OHS_surf = BASICFONT.render('OHS: %d' % OVERALL_HIGHSCORE, True, TEXTCOLOR)
    OHS_rect = OHS_surf.get_rect()
    OHS_rect.topleft = (WINDOWWIDTH - 625, 40)
    DISPLAYSURF.blit(OHS_surf, OHS_rect)

    # Draw current chromsome info
    if CURRENT_CHROMOSOME is None:
        return
    else:
        # draw current chromosome
        current_surf = BASICFONT.render('Current chromosome:', True, TEXTCOLOR)
        current_rect = current_surf.get_rect()
        current_rect.topleft = (WINDOWWIDTH - 200, 290)
        DISPLAYSURF.blit(current_surf, current_rect)

        # draw chromosome attribute a
        ca_surf = BASICFONT.render('a  =  %s' % round(CURRENT_CHROMOSOME.attributes[0], 3), True, TEXTCOLOR)
        ca_rect = ca_surf.get_rect()
        ca_rect.topleft = (WINDOWWIDTH - 200, 320)
        DISPLAYSURF.blit(ca_surf, ca_rect)

        # draw chromosome attribute b
        cb_surf = BASICFONT.render('b  =  %s' % round(CURRENT_CHROMOSOME.attributes[1], 3), True, TEXTCOLOR)
        cb_rect = cb_surf.get_rect()
        cb_rect.topleft = (WINDOWWIDTH - 200, 340)
        DISPLAYSURF.blit(cb_surf, cb_rect)

        # draw chromosome attribute c
        cc_surf = BASICFONT.render('c  =  %s' % round(CURRENT_CHROMOSOME.attributes[2], 3), True, TEXTCOLOR)
        cc_rect = cc_surf.get_rect()
        cc_rect.topleft = (WINDOWWIDTH - 200, 360)
        DISPLAYSURF.blit(cc_surf, cc_rect)

    # draw current chromosome text
    if BEST_CHROMOSOME_IN_GENERATION is None:
        return
    else:
        # draw best chromosome
        best_surf = BASICFONT.render('best chromosome:', True, TEXTCOLOR)
        best_rect = best_surf.get_rect()
        best_rect.topleft = (WINDOWWIDTH - 626, 80)
        DISPLAYSURF.blit(best_surf, best_rect)


        # draw chromosome attribute a
        a_surf = BASICFONT.render('a  =  %s' % round(BEST_CHROMOSOME_IN_GENERATION.attributes[0],3), True, TEXTCOLOR)
        a_rect = a_surf.get_rect()
        a_rect.topleft = (WINDOWWIDTH - 625, 110)
        DISPLAYSURF.blit(a_surf, a_rect)

        # draw chromosome attribute b
        b_surf = BASICFONT.render('b  =  %s' % round(BEST_CHROMOSOME_IN_GENERATION.attributes[1],3), True, TEXTCOLOR)
        b_rect = b_surf.get_rect()
        b_rect.topleft = (WINDOWWIDTH - 625, 130)
        DISPLAYSURF.blit(b_surf, b_rect)

        # draw chromosome attribute c
        c_surf = BASICFONT.render('c  =  %s' % round(BEST_CHROMOSOME_IN_GENERATION.attributes[2],3), True, TEXTCOLOR)
        c_rect = c_surf.get_rect()
        c_rect.topleft = (WINDOWWIDTH - 625, 150)
        DISPLAYSURF.blit(c_surf, c_rect)

        # draw chromosome high score
        high_score_surf = BASICFONT.render('CHS = %d' % BEST_CHROMOSOME_IN_GENERATION.high_score, True, TEXTCOLOR)
        high_score_rect = high_score_surf.get_rect()
        high_score_rect.topleft = (WINDOWWIDTH - 625, 190)
        DISPLAYSURF.blit(high_score_surf, high_score_rect)


def draw_piece(piece, pixelx=None, pixely=None):
    shape_to_draw = PIECES[piece['shape']][piece['rotation']]
    if pixelx is None and pixely is None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convert_to_pixel_coords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shape_to_draw[y][x] != BLANK:
                draw_box(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def draw_next_piece(piece):
    # draw the "next" text
    next_surf = BASICFONT.render('Next:', True, TEXTCOLOR)
    next_rect = next_surf.get_rect()
    next_rect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(next_surf, next_rect)
    # draw the "next" piece
    draw_piece(piece, pixelx=WINDOWWIDTH - 155, pixely=140)


# region Genetic algorithm
class Chromosome:

    def __init__(self):
        self.high_score = 0
        self.attributes = [0] * CHROMOSOME_SIZE

        for i in range(CHROMOSOME_SIZE):
            self.attributes[i] = (random.uniform(-10.0, 10.0))


def create_population():
    population = []

    for i in range(POPULATION_SIZE):
        population.append(Chromosome())

    return population


# Two point crossover
def crossover(parent1, parent2):
    offspring1 = Chromosome()
    offspring2 = Chromosome()

    first_crossover_point = 0
    second_crossover_point = 0

    remaining_genes = CHROMOSOME_SIZE  # Only used to split the gene up into three parts
    while remaining_genes > 0:
        if remaining_genes > 0:
            first_crossover_point += 1
            remaining_genes -= 1
        if remaining_genes > 0:
            second_crossover_point += 1
            remaining_genes -= 1

        remaining_genes -= 1  # The last gene, if any, is in the third part and won't be swapped

    second_crossover_point = first_crossover_point + second_crossover_point

    # Generates offspring -- Only the part between point1 and point2 are swapped
    for i in range(CHROMOSOME_SIZE):
        if first_crossover_point <= i & i <= second_crossover_point:
            offspring1.attributes[i] = parent2.attributes[i]
            offspring2.attributes[i] = parent1.attributes[i]
        else:
            offspring1.attributes[i] = parent1.attributes[i]
            offspring2.attributes[i] = parent2.attributes[i]

    print(parent1.attributes)
    print(offspring1.attributes)
    print("\n")

    print(parent2.attributes)
    print(offspring2.attributes)
    print("\n")
    return offspring1, offspring2


def selection(population):
    new_population = []

    for i in range(int(len(population) / 2)):
        parent1 = selectParent(population)
        parent2 = selectParent(population)

        offspring1, offspring2 = crossover(parent1, parent2)
        new_population.extend([offspring1, offspring2])

    return new_population


def selectParent(population):
    # Pops the first chromosome in order to not pick it again as the second
    chromosome1 = population.pop(random.randint(0, len(population) - 1))
    chromosome2 = population[random.randint(0, len(population) - 1)]

    population.append(chromosome1)  # Adds the chromosome so it can be picked in the next call to selectParent

    r = random.uniform(0, 1)

    if r < K:
        if chromosome1.high_score >= chromosome2.high_score:
            return chromosome1
        else:
            return chromosome2
    else:
        if chromosome1.high_score <= chromosome2.high_score:
            return chromosome1
        else:
            return chromosome2
# endregion


# region Board state methods
def get_aggregate_height(board):
    # Calculate the aggregate height of the board, by summing the
    # height of each column. Each row have a height penalty based on it's height (e.g. row_1 = 1...row_20 = 20)

    heights = [0]*BOARDWIDTH

    for i in range(0, BOARDWIDTH):  # Selects a column
        for j in range(0, BOARDHEIGHT):  # Goes down from the top of the selected column
            if int(board[i][j]) > 0:
                height = (BOARDHEIGHT - j)
                heights[i] = height * (height * WEIGHT_AGGREGATE_HEIGHT)
                break  # breaks to find the height of the next column

    return sum(heights)


def get_number_of_holes(board):
    # Calculates the number of holes on the board
    holes = 0

    for i in range(0, BOARDWIDTH):
        filled = False  # Set to True if the current square is occupied by a piece
        for j in range(0, BOARDHEIGHT):
            if int(board[i][j]) > 0 and not filled:
                filled = True
            if int(board[i][j]) == 0 and filled:  # If current square is empty and an square above it is filled
                holes += 1

    return holes


def get_bumpiness(board):
    # Calculate the bumpiness of the board, by taking the
    # difference in height between each pair of columns (e.g diff between column 1 and 2)

    heights = [0] * BOARDWIDTH
    bumpiness = 0

    for i in range(0, BOARDWIDTH):  # Selects a column
        for j in range(0, BOARDHEIGHT):  # Goes down from the top of the selected column
            if int(board[i][j]) > 0:
                heights[i] = BOARDHEIGHT - j  # Stores the height of the given column
                break  # breaks to find the height of the next column

    for i in range(BOARDWIDTH - 1):
        highest = max(heights[i], heights[i + 1])
        lowest = min(heights[i], heights[i + 1])
        bumpiness += highest - lowest

    return bumpiness
# endregion


# region Remaining methods
def get_expected_score(test_board, completed_lines, chromosome):
    # Calculates the score of a given board state given the attributes of the chromosome
    aggregate_height = get_aggregate_height(test_board)
    holes = get_number_of_holes(test_board)

    a = chromosome.attributes[0]
    b = chromosome.attributes[1]
    c = chromosome.attributes[2]

    expected_score = a * aggregate_height + b * completed_lines + c * holes

    return expected_score


def simulate_board(test_board, test_piece, move):
    rot = move[0]
    sideways = move[1]

    if test_piece is None:
        return None

    for i in range(0, rot):  # TODO: How does this work?
        test_piece['rotation'] = (test_piece['rotation'] + 1) % len(PIECES[test_piece['shape']])

    if not is_valid_position(test_board, test_piece, sideways, 0):
        return None

    test_piece['x'] += sideways
    for i in range(0, BOARDHEIGHT):
        if is_valid_position(test_board, test_piece, 0, 1):
            test_piece['y'] = i

    add_to_board(test_board, test_piece)
    completed_lines, test_board = remove_complete_lines(test_board)

    return test_board, completed_lines


def find_best_move(board, piece, chromosome):
    moves = []
    scores = []

    for rot in range(0, len(PIECES[piece['shape']])):
        for sideways in range(-5, 6):
            move = [rot, sideways]
            test_board = copy.deepcopy(board)
            test_piece = copy.deepcopy(piece)
            test_board = simulate_board(test_board, test_piece, move)
            if test_board is not None:
                moves.append(move)
                scores.append(get_expected_score(test_board[0], test_board[1], chromosome))

    highest_score = max(scores)
    best_move = moves[scores.index(highest_score)]

    return best_move


def make_move(move):
    rot = move[0]
    sideways = move[1]
    if rot != 0:
        pyautogui.press('up')
        rot -= 1
    else:
        if sideways == 0:
            pyautogui.press('space')
        if sideways < 0:
            pyautogui.press('left')
            sideways += 1
        if sideways > 0:
            pyautogui.press('right')
            sideways -= 1

    return [rot, sideways]
# endregion


def create_log_file():
    # Opens file to read the number of this log
    file_log_number = open("LogNumber.txt", "r")
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
    log.write("Population: " + str(POPULATION_SIZE) + "\n")
    log.write("Chromosome size: " + str(CHROMOSOME_SIZE) + "\n")
    log.write("Mutation: " + str(MUTATION) + "\n\n")

    log.close()

    return number


# Writes game data to a log file
def write_generation_to_log(Chromosome, log_number):

    log = open("Log" + str(log_number), "a")

    log.write("Generation: " + str(GENERATION_NUMBER) + "\n")
    log.write("a = " + str(Chromosome.attributes[0]) + "\n")
    log.write("b = " + str(Chromosome.attributes[1]) + "\n")
    log.write("c = " + str(Chromosome.attributes[2]) + "\n")
    log.write("High score = " + str(Chromosome.high_score) + "\n\n")

    log.close()


def get_best_chromosome(population):
    best_chromosome = population[0]

    for i in range(1, len(population)):
        if population[i].high_score > best_chromosome.high_score:
            best_chromosome = population[i]

    return best_chromosome


if __name__ == '__main__':
    assert(POPULATION_SIZE % 2 == 0)

    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')

    show_text_screen('Tetromino')

    population = create_population()

    log_number = create_log_file()
    while True:  # game loop
        sum_a = 0
        sum_b = 0
        sum_c = 0
        sum_high_score = 0

        for i in range(0, len(population)):  # chromosome loop(one per game)
            CURRENT_CHROMOSOME = population[i]
            run_game(population[i])
            show_text_screen('Game Over')

            # plot data
            sum_a += CURRENT_CHROMOSOME.attributes[0]
            sum_b += CURRENT_CHROMOSOME.attributes[1]
            sum_c += CURRENT_CHROMOSOME.attributes[2]
            sum_high_score += CURRENT_CHROMOSOME.high_score

        # Data for plotting
        GENERATION_NUMBERS.append(GENERATION_NUMBER)
        BEST_CHROMOSOME_IN_GENERATION = get_best_chromosome(population)
        BEST_CHROMOSOME_GENERATION_HIGH_SCORES.append(BEST_CHROMOSOME_IN_GENERATION.high_score)
        AVERAGE_A.append(sum_a / POPULATION_SIZE)
        AVERAGE_B.append(sum_b / POPULATION_SIZE)
        AVERAGE_C.append(sum_c / POPULATION_SIZE)
        AVERAGE_HIGH_SCORE.append(sum_high_score / POPULATION_SIZE)

        # Write to log
        write_generation_to_log(BEST_CHROMOSOME_IN_GENERATION, log_number)
        GENERATION_NUMBER += 1

        if BEST_CHROMOSOME_IN_GENERATION.high_score > OVERALL_HIGHSCORE:
            OVERALL_HIGHSCORE = BEST_CHROMOSOME_IN_GENERATION.high_score

        population = selection(population)










