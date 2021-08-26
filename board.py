import copy
from typing import Generator, List, Optional, Tuple

from exceptions import ColumnFullException, ColumnOutOfBoundsException
from player import Player
from player_type import PlayerType
from status import Status


class Board:
    """
    Class representing the state of the game including
    the board, active player, and value.
    """

    VICTORY_VALUE = 10 ** 8  # The value of a winning board (for max)
    LOSS_VALUE = -VICTORY_VALUE  # The value of a losing board (for max)
    SEQ_LENGTH = 4  # the length of winning sequence

    def __init__(
        self,
        rows: int = 6,
        columns: int = 7,
        players: Tuple[Player, Player] = (
            Player("X", "Red", PlayerType.HUMAN),
            Player("O", "Yellow", PlayerType.AI),
        ),
        active_player_index: int = 0,
        grid: Optional[List[List[Optional[Player]]]] = None,
    ):
        """
        Create a new instance of a board

        Args:
            rows: The number of rows in the board
            columns: The number of columns in the board
            players: Tuple with the symbol and types of the 2 players
            active_player: 0 for first player's turn, 1 for second player
            grid: 2d list of Players or None for empty (None for default)
        """
        self.__grid = grid or [[None for _ in range(columns)] for _ in range(rows)]
        self.__rows = rows
        self.__columns = columns
        self.__players = players
        self.__active_player_index = active_player_index
        self.__column_search_order = self.__column_search_order()

    @property
    def grid(self) -> List[List[Optional[Player]]]:
        """Returns the grid of the board"""
        return self.__grid

    @property
    def players(self) -> Tuple[Player, Player]:
        """Returns the players in the game"""
        return self.__players

    @property
    def active_player(self) -> Player:
        """Returns the active player"""
        return self.__players[self.__active_player_index]

    def __copy(self) -> "Board":
        """Returns a new board containing a copy of the current one"""
        new_board = Board(
            self.__rows, self.__columns, self.__players, self.__active_player_index
        )
        new_board.__grid = copy.deepcopy(self.__grid)
        return new_board

    def is_human_turn(self) -> bool:
        """Returns True if current player is a human, False otherwise."""
        return self.__players[self.__active_player_index].type == PlayerType.HUMAN

    def player_1_is_active(self) -> bool:
        """Returns True if player 1 is active, False otherwise."""
        return self.__active_player_index == 0

    def status(self) -> Status:
        """
        Checks if the game is won, tied, or ongoing.

        Returns:
            Status.PLAYER_1_WINS if the first player wins
            Status.PLAYER_2_WINS if the second player wins
            Status.TIE if the game has ended in a tie
            Status.ONGOING otherwise
        """
        # check for a win
        value = self.heuristic_value()
        if value >= self.VICTORY_VALUE:
            return Status.PLAYER_1_WINS
        if value <= self.LOSS_VALUE:
            return Status.PLAYER_2_WINS
        # if no values in the grid are None, it is a tie
        if self.__check_for_draw():
            return Status.TIE
        # game has not ended
        return Status.ONGOING

    def __check_for_draw(self) -> bool:
        """Returns True if the game has ended in a draw, False otherwise."""
        return all(self.__column_is_full(column) for column in range(self.__columns))

    def is_game_over(self) -> bool:
        """Returns True if the game is over, False otherwise."""
        return self.status() != Status.ONGOING

    def place_piece(self, column: int) -> None:
        """
        Places a piece in the grid in the next space in the given column.

        Args:
            column: the column to place the piece inis

        Raises:
            ColumnFullError if the column is full
        """
        if column < 0 or column >= self.__columns:
            raise ColumnOutOfBoundsException(column)
        row = self.__next_open_row(column)
        if row is None:
            raise ColumnFullException(column)
        self.__grid[row][column] = self.__players[self.__active_player_index]

    def change_turn(self) -> None:
        """Toggles the turn indicator between 0 and 1."""
        self.__active_player_index = 1 - self.__active_player_index

    def __next_open_row(self, column: int) -> Optional[int]:
        """
        Finds the next available row to place a piece in a column

        Args:
            column: the column to check for availability

        Returns:
            The last available row or None if the column is full
        """
        # return None if column is full
        if self.__column_is_full(column):
            return None
        # find first empty cell from bottom
        row = self.__rows - 1
        while row >= 0 and self.__grid[row][column] is not None:
            row -= 1
        return row

    def __column_is_full(self, column: int):
        """
        Checks if a column is full.

        Args:
            column: the column to check for availability

        Returns:
            True if column is full, False otherwise
        """
        return self.__grid[0][column] is not None

    def successors(self) -> Generator["Board", None, None]:
        """
        Find next states for the current board

        Yields:
            Board states that can be created by placing a piece
        """
        for column in self.__column_search_order:
            if self.__column_is_full(column):
                continue
            new_board = self.__copy()
            new_board.place_piece(column)
            new_board.change_turn()
            yield new_board

    def __column_search_order(self) -> Tuple[int, ...]:
        """
        Finds the optimal order to choose columns in for optimization

        Returns:
            A tuple of integers representing the order to choose columns in
        """
        # sort columns by distance from center
        order = lambda x: abs(x - self.__columns // 2)
        return tuple(sorted(range(self.__columns), key=order))

    def key(self) -> Tuple[Tuple[Optional[str]]]:
        """Returns a hashable key for the board"""
        return tuple(
            tuple(cell.symbol if cell is not None else None for cell in row)
            for row in self.__grid
        )

    def print(self) -> None:
        """Prints the information about the board"""
        print(str(self))

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        """Output information about the current board state"""
        # board
        output = ""
        for row in self.__grid:
            output += f'|{"|".join(str(cell) if cell else " " for cell in row)}|\n'
        # column numbers
        output += f' {" ".join(f"{i}" for i in range(self.__columns))}\n\n'
        return output

    def heuristic_value(self) -> float:
        """Returns the heuristic value for the board"""

        # score the board position
        score = 0

        # set players for maximizing and minimizing
        maximizing_player, minimizing_player = self.__players

        if self.__check_for_draw():
            return 0

        # score based on how many pieces are connected or close
        # the more connected pieces you have, the closer you are to winning

        def count_symbol(player: Player, *cells: Player) -> int:
            """Returns number of cells matching player"""
            return sum(cell == player for cell in cells if cell is not None)

        def score_group(*group: Player) -> int:
            """Return score to add for a group of cells"""
            # the more connected pieces you have, the closer you are to winning
            # each pair represents the number of your symbol and number of opponent's symbol
            POINTS_BY_COUNT = {
                # player has four in a row
                (self.SEQ_LENGTH, 0): 2 * self.VICTORY_VALUE,
                # player has three in a row
                (self.SEQ_LENGTH - 1, 0): 300,
                # player has two in a row
                (self.SEQ_LENGTH - 2, 0): 50,
                # player has one in a row
                (self.SEQ_LENGTH - 3, 0): 10,
            }
            # get number of max's pieces in the group
            count_max = count_symbol(maximizing_player, *group)
            # get number of min's pieces in the group
            count_min = count_symbol(minimizing_player, *group)
            # compute how much of an advantage each player has in the group
            max_advantage = POINTS_BY_COUNT.get((count_max, count_min), 0)
            min_advantage = POINTS_BY_COUNT.get((count_min, count_max), 0)
            return max_advantage - min_advantage

        # vertical groups
        for row in range(self.__rows - self.SEQ_LENGTH + 1):
            for col in range(self.__columns):
                group = [self.__grid[row + i][col] for i in range(self.SEQ_LENGTH)]
                score += score_group(*group)

        # horizontal groups
        for row in range(self.__rows):
            for col in range(self.__columns - self.SEQ_LENGTH + 1):
                group = [self.__grid[row][col + i] for i in range(self.SEQ_LENGTH)]
                score += score_group(*group)

        # diagonal down to the right
        for row in range(self.__rows - self.SEQ_LENGTH + 1):
            for col in range(self.__columns - self.SEQ_LENGTH + 1):
                group = [self.__grid[row + i][col + i] for i in range(self.SEQ_LENGTH)]
                score += score_group(*group)

        # diagonal down to the left
        for row in range(self.__rows - self.SEQ_LENGTH + 1):
            for col in range(self.SEQ_LENGTH - 1, self.__columns):
                group = [self.__grid[row + i][col - i] for i in range(self.SEQ_LENGTH)]
                score += score_group(*group)

        return score
