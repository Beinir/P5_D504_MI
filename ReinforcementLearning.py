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