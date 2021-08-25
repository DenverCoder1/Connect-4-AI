import time

import pygame

from alpha_beta_pruning import minimax
from game import Game
from player import Player
from player_type import PlayerType


def determine_player_type(number: int) -> PlayerType:
    """
    Prompts user to enter whether a player is human or AI.

    Args:
        number: the player number to tell the user

    Returns:
        PlayerType.HUMAN or PlayerType.AI
    """
    response = input(f"Is player {number} a human or AI? [h/A] ")
    return PlayerType.HUMAN if response.lower() in ("h", "human") else PlayerType.AI


def play_game():
    players = (
        Player("X", "Red", determine_player_type(1)),
        Player("O", "Yellow", determine_player_type(2)),
    )

    game = Game(players)

    while not game.board.is_game_over():

        for event in pygame.event.get():
            # if the user clicked close
            if event.type == pygame.QUIT:
                return
            # user clicks a cell
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)

        if not game.board.is_human_turn():
            start = time.time()
            _, game.board = minimax(game.board)
            print(f"Found move in {time.time() - start} seconds")
            game.draw_board()

    # print the end game status (who won)
    game.draw_board()

    # delay a few seconds
    time.sleep(3)


if __name__ == "__main__":
    play_game()
