# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Creative Commons BY-NC-SA 3.0 US
import random, time, pygame, sys
from pygame.locals import *
import ReinforcementLearning as rl
import math
# region constants
FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '0'
MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1
XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5
# endregion
# region shape colors
#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)
# endregion
# region color constants and template constants
BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color
TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5
# endregionx
# region shapes
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

SHAPES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}
# endregion


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')

    show_text_screen('Tetromino')
    while True: # game loop
        runGame(rl.weights, rl.explore_change)
        #pygame.mixer.music.stop()
        show_text_screen('Game Over')


def runGame(weights, explore_change):
    # setup variables for the start of the game
    board = get_blank_board()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False # note: there is no movingUp variable
    movingLeft = False
    movingRight = False
    #score = 0
    level, fallFreq = get_level_and_fall_freq(rl.score)
    fallingPiece = get_new_piece()
    nextPiece = get_new_piece()
    current_move = [0, 0]

    while True: # main game loop
        if fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            fallingPiece = nextPiece
            nextPiece = get_new_piece()
            lastFallTime = time.time() # reset lastFallTime

            if not is_valid_position(board, fallingPiece):
                return # can't fit a new piece on the board, so game over
            current_move = rl.find_best_move(board, fallingPiece, rl.weights, rl.explore_change)

        check_for_quit()
        current_move = rl.make_move(current_move)
        for event in pygame.event.get():  # event handling loop
            if event.type == KEYUP:
                if (event.key == K_p):
                    # Pausing the game
                    DISPLAYSURF.fill(BGCOLOR)
                    # pygame.mixer.music.stop()
                    show_text_screen('Paused') # pause until a key press
                    # pygame.mixer.music.play(-1, 0.0)
                    lastFallTime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()
                elif (event.key == K_LEFT or event.key == K_a):
                    movingLeft = False
                elif (event.key == K_RIGHT or event.key == K_d):
                    movingRight = False
                elif (event.key == K_DOWN or event.key == K_s):
                    movingDown = False

            elif event.type == KEYDOWN:
                # moving the block sideways
                if (event.key == K_LEFT or event.key == K_a) and is_valid_position(board, fallingPiece, adj_x=-1):
                    fallingPiece['x'] -= 1
                    movingLeft = True
                    movingRight = False
                    lastMoveSidewaysTime = time.time()

                elif (event.key == K_RIGHT or event.key == K_d) and is_valid_position(board, fallingPiece, adj_x=1):
                    fallingPiece['x'] += 1
                    movingRight = True
                    movingLeft = False
                    lastMoveSidewaysTime = time.time()

                # rotating the block (if there is room to rotate)
                elif (event.key == K_UP or event.key == K_w):
                    fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(SHAPES[fallingPiece['shape']])
                    if not is_valid_position(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(SHAPES[fallingPiece['shape']])
                elif (event.key == K_q): # rotate the other direction
                    fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(SHAPES[fallingPiece['shape']])
                    if not is_valid_position(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(SHAPES[fallingPiece['shape']])

                # making the block fall faster with the down key
                elif (event.key == K_DOWN or event.key == K_s):
                    movingDown = True
                    if is_valid_position(board, fallingPiece, adj_y=1):
                        fallingPiece['y'] += 1
                    lastMoveDownTime = time.time()

                # move the current block all the way down
                elif event.key == K_SPACE:
                    movingDown = False
                    movingLeft = False
                    movingRight = False
                    for i in range(1, BOARDHEIGHT):
                        if not is_valid_position(board, fallingPiece, adj_y=i):
                            break
                    fallingPiece['y'] += i - 1

        # handle moving the block because of user input
        if (movingLeft or movingRight) and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
            if movingLeft and is_valid_position(board, fallingPiece, adj_x=-1):
                fallingPiece['x'] -= 1
            elif movingRight and is_valid_position(board, fallingPiece, adj_x=1):
                fallingPiece['x'] += 1
            lastMoveSidewaysTime = time.time()

        if movingDown and time.time() - lastMoveDownTime > MOVEDOWNFREQ and is_valid_position(board, fallingPiece, adj_y=1):
            fallingPiece['y'] += 1
            lastMoveDownTime = time.time()

        # let the piece fall if it is time to fall
        if time.time() - lastFallTime > fallFreq:
            # see if the piece has landed
            if not is_valid_position(board, fallingPiece, adj_y=1):
                # falling piece has landed, set it on the board
                add_to_board(board, fallingPiece)
                lines, board = remove_complete_lines(board)
                rl.score = lines * lines
                level, fallFreq = get_level_and_fall_freq(rl.score)
                fallingPiece = None
            else:
                # piece did not land, just move the block down
                fallingPiece['y'] += 1
                lastFallTime = time.time()

        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        draw_status(rl.score, level, current_move)
        draw_next_piece(nextPiece)
        if fallingPiece != None:
            draw_piece(fallingPiece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def make_text_objs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    log1 = open("log/RL_weights.txt", "w")
    for element in rl.weights:
        print(element, file=log1)
    print(rl.score, file=log1)
    sys.exit()


def check_for_key_press():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    check_for_quit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
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
    for event in pygame.event.get(QUIT):  # get all the QUIT events
        terminate()  # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP):  # get all the KEYUP events
        if event.key == K_ESCAPE:
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
    shape = random.choice(list(SHAPES.keys()))
    new_piece = {
        'shape': shape,
        'rotation': random.randint(0,
                                   len(SHAPES[shape]) - 1),
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
            if SHAPES[piece['shape']][piece['rotation']][y][x] != BLANK and x + piece['x'] < 10 and y + piece['y'] < 20:
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
        for y in range(TEMPLATEHEIGHT):
            is_above_board = y + piece['y'] + adj_y < 0
            if is_above_board or SHAPES[piece['shape']][piece['rotation']][y][x] == BLANK:
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


def draw_piece(piece, pixelx=None, pixely=None):
    shape_to_draw = SHAPES[piece['shape']][piece['rotation']]
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
    next_rect.topleft = (WINDOWWIDTH - 120, 160)
    DISPLAYSURF.blit(next_surf, next_rect)
    # draw the "next" piece

if __name__ == '__main__':
    main()
