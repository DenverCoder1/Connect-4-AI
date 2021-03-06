from typing import Tuple

import pygame

from board import Board
from exceptions import IllegalMoveException
from player import Player
from status import Status


class Game:
    """
    This class handles interactions with the pygame user interface.
    """

    # colors
    BACKGROUND_COLOR = (20, 20, 20)
    PLAYER_1_COLOR = (255, 100, 100)
    PLAYER_2_COLOR = (255, 255, 130)
    CELL_BORDER_COLOR = (0, 115, 210)
    VALUE_FONT_COLOR = (220, 220, 220)

    # number of pixels from the top of the screen
    STATUS_TEXT_OFFSET = 4
    VALUE_TEXT_OFFSET = 42
    GRID_OFFSET = 80

    # number of rows and columns
    ROW_COUNT = 6
    COLUMN_COUNT = 7

    # width and height of the cell in pixels
    SQUARE_WIDTH = 50

    def __init__(self, players: Tuple[Player, Player]):
        pygame.init()
        self.STATUS_FONT = pygame.font.SysFont("Noto Sans", 26)
        self.VALUE_FONT = pygame.font.SysFont("Noto Sans", 18)
        self.__height = self.ROW_COUNT * self.SQUARE_WIDTH + self.GRID_OFFSET
        self.__width = self.COLUMN_COUNT * self.SQUARE_WIDTH
        self.__screen = pygame.display.set_mode((self.__width, self.__height))
        pygame.display.set_caption("Connect 4 Game")
        self.board = Board(
            rows=self.ROW_COUNT, columns=self.COLUMN_COUNT, players=players
        )
        self.draw_board()

    def draw_board(self):
        """
        Draws the board on the screen
        """
        # print to terminal
        self.board.print()

        # clear the screen
        self.__screen.fill(self.BACKGROUND_COLOR)

        # draw the board
        for row in range(self.ROW_COUNT):
            for column in range(self.COLUMN_COUNT):
                self.draw_cell(row, column)
                self.draw_piece(row, column)

        self.draw_text()
        pygame.display.update()

    def draw_cell(self, row: int, column: int):
        """
        Draws a cell on the screen
        """
        # blue background
        pygame.draw.rect(
            self.__screen,
            self.CELL_BORDER_COLOR,
            (
                column * self.SQUARE_WIDTH,
                row * self.SQUARE_WIDTH + self.GRID_OFFSET,
                self.SQUARE_WIDTH,
                self.SQUARE_WIDTH,
            ),
        )

    def draw_piece(self, row: int, column: int):
        """
        Draws a piece on the screen or black for empty cells
        """
        cell = self.board.grid[row][column]
        player_1, player_2 = self.board.players
        # empty - BLACK, player 1 - RED, player 2 - YELLOW
        color = self.PLAYER_1_COLOR if cell == player_1 else self.BACKGROUND_COLOR
        color = self.PLAYER_2_COLOR if cell == player_2 else color
        # draw piece
        pygame.draw.circle(
            self.__screen,
            color,
            (
                int(column * self.SQUARE_WIDTH + self.SQUARE_WIDTH / 2),
                int(row * self.SQUARE_WIDTH + self.SQUARE_WIDTH / 2 + self.GRID_OFFSET),
            ),
            int(self.SQUARE_WIDTH // 2) - 5,
        )

    def draw_text(self):
        """
        Draws the text on the screen
        """
        # active player text
        status_text = f"It's {self.board.active_player.color_name}'s turn"
        player_1_active = self.board.player_1_is_active()
        status_color = self.PLAYER_1_COLOR if player_1_active else self.PLAYER_2_COLOR

        # value text
        value = self.board.heuristic_value()
        # print game end state if game is over
        status = self.board.status()
        value_text = f"Value: {value}"
        if status != Status.ONGOING:
            # display winner
            status_text = status.value
            # display winner color
            player_1_won = status == Status.PLAYER_1_WINS
            status_color = self.PLAYER_1_COLOR if player_1_won else self.PLAYER_2_COLOR
        elif value != 0:
            winning_player_index = 1 - int(value > 0)
            winning_player = self.board.players[winning_player_index]
            value_text += f"  |  {winning_player.color_name} is winning"

        # draw status text
        status_text_render = self.STATUS_FONT.render(status_text, True, status_color)
        self.__screen.blit(
            status_text_render,
            (
                self.__width / 2 - status_text_render.get_width() / 2,
                self.STATUS_TEXT_OFFSET,
            ),
        )
        # draw value text
        value_text_render = self.VALUE_FONT.render(
            value_text, True, self.VALUE_FONT_COLOR
        )
        self.__screen.blit(
            value_text_render,
            (
                self.__width / 2 - value_text_render.get_width() / 2,
                self.VALUE_TEXT_OFFSET,
            ),
        )

    def handle_click(self, pos: Tuple[float, float]):
        """
        Handles a click on the board

        Args:
            pos: The x,y position of the click
        """
        # only handle clicks during human turns and if they are on the board
        if self.board.is_human_turn() and pos[1] > self.GRID_OFFSET:
            # get the column of the click
            column = int(pos[0] / self.SQUARE_WIDTH)
            try:
                # place the piece
                self.board.place_piece(column)
                self.board.change_turn()
            except IllegalMoveException as err:
                print(err.message)
        self.draw_board()
