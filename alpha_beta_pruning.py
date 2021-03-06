import math
from typing import Optional, Tuple, Union

from board import Board
from transposition_table import CacheEntry, TranspositionTable

MAX_DEPTH = 5

# transposition table for looking up previously computed positions
transposition_table = TranspositionTable(8192)


def minimax(
    board: Board,
    maximizing: Optional[bool] = None,
    depth: int = MAX_DEPTH,
    alpha: float = -math.inf,
    beta: float = math.inf,
) -> Union[Tuple[float, Board], None]:
    """
    Minimax algorithm with alpha-beta pruning.

    Args:
        board: the board position to minimize/maximize
        maximizing: whether the current board should be maximized and not minimized
            if maximizing is not specified, it will be the default based on the active_player
        depth: the current search depth
        alpha: alpha value for maximizing player to maximize
        beta: beta value for minimizing player to minimize

    Returns:
        Tuple containing the board value and board for the best move.
        Returns None if no move is found.
    """
    maximizing = maximizing if maximizing is not None else board.player_1_is_active()
    alpha_0 = alpha

    if board.key() in transposition_table:
        entry: CacheEntry = transposition_table[board.key()]
        # lower bound was stored in the transposition table
        if entry.max:
            alpha = max(alpha, entry.value)
        # upper bound was stored in the transposition table
        elif entry.min:
            beta = min(beta, entry.value)
        # exact value was stored in the transposition table
        else:
            return entry.value, entry.best_move
        # prune if the value is outside the bounds
        if alpha >= beta:
            return entry.value, entry.best_move

    # return if game is over or reached maximum depth
    if depth == 0 or board.is_game_over():
        return board.heuristic_value(), board

    # find best move
    best_value = -math.inf if maximizing else math.inf
    best_move = None
    for successor in board.successors():
        # recursively call the function for minimization if max_player, or for maximizing otherwise
        value, _ = minimax(successor, not maximizing, depth - 1, alpha, beta)
        if maximizing and value > best_value or not maximizing and value < best_value:
            best_value, best_move = value, successor
        # update alpha/beta values
        if maximizing:
            alpha = max(alpha, best_value)
        else:
            beta = min(beta, best_value)
        # prune if the value is outside the bounds
        if alpha >= beta:
            break

    # store the value in the transposition table
    if best_value <= alpha_0:
        transposition_table[board.key()] = CacheEntry(best_value, best_move, max=True)
    elif best_value >= beta:
        transposition_table[board.key()] = CacheEntry(best_value, best_move, min=True)
    else:
        transposition_table[board.key()] = CacheEntry(best_value, best_move)

    return best_value, best_move
