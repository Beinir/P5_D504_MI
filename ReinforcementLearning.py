import pyautogui as gui
#region Constants
gamma = 0.6
learning_rate = 0.6

explore_change = 1.0
max_explore_change = 1.0
min_explore_change = 0.01
decay_rate = 0.01

weights = [-1, -1, -1, -30]
"""
    weights list of four floats:
    * Sum of all column heights.
    * Sum of absolute column differences.
    * Maximum height on the board.
    * Number of holes on the board.
"""
score = 0
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
            lateral -= 1
        elif lateral > 0:
            gui.press('right')
            lateral += 1

    return [rotation, lateral]


#def find_best_move():


#def make_test_board():


