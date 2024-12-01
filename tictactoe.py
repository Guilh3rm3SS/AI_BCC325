"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)

    if x_count <= o_count:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    possible_actions = set()
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if (cell == None):
                possible_actions.add((i, j))
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if not (0 <= i < len(board) and 0 <= j < len(board[0])):
        raise ValueError("Action is out of bounds.")

    new_board = [row[:] for row in board]
    current_player = player(board)

    if (new_board[action[0]][action[1]] == None):
        new_board[action[0]][action[1]] = current_player
        return new_board
    else:
        raise ValueError("Cell is already occupied.")


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        # row check
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != None:
            return board[i][0]
        # column check
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != None:
            return board[0][i]

    # diagonals check
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != None:
        return board[0][0]

    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != None:
        return board[0][2]

    # No winner
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if (winner(board) != None):  #the game still has not a winner
        return True

    count = sum(row.count(None) for row in board)
    if count == 0:
        return True
    
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    winner_value = winner(board)

    if winner_value == X:
        return 1

    if winner_value == O:
        return -1

    else:
        return 0


def max_value(board):
    #return the optimal action for the X player
    if (terminal(board)):
        return utility(board)

    optimal_value = -math.inf
    for action in actions(board):
        actual_value = min_value(result(board,action))
        if (actual_value > optimal_value):
            optimal_value = actual_value
    return optimal_value


def min_value(board):
    #return the optimal action for the O player
    if (terminal(board)):
        return utility(board)

    optimal_value = math.inf
    for action in actions(board):
        actual_value = max_value(result(board,action))
        if (actual_value < optimal_value):
            optimal_value = actual_value
    return optimal_value


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # raise NotImplementedError

    if terminal(board):
        return None

    current_player = player(board)
    possible_actions = actions(board)
    
    best_action = None
    
    if current_player == X:
        best_value = -math.inf
        for action in possible_actions:
            current_value = min_value(result(board, action))
            if(current_value > best_value):
                best_value = current_value
                best_action = action

    else:
        best_value = math.inf
        for action in possible_actions:
            current_value = max_value(result(board, action))
            if(current_value < best_value):
                best_value = current_value
                best_action = action

    return best_action
