from player_type import PlayerType


class Player:
    """
    Class representing a player.
    A player has a symbol they play as and can be a human or AI
    """

    def __init__(self, symbol: str, color_name: str, player_type: PlayerType):
        self.__symbol = symbol
        self.__color_name = color_name
        self.__type = player_type

    @property
    def symbol(self) -> str:
        return self.__symbol

    @property
    def color_name(self) -> str:
        return self.__color_name

    @property
    def type(self) -> PlayerType:
        return self.__type

    def __eq__(self, other) -> bool:
        return isinstance(other, Player) and self.__symbol == other.__symbol

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.__symbol
