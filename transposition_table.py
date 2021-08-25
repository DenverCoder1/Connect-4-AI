from board import Board
from collections import OrderedDict


class TranspositionTable(OrderedDict):
    """
    LRU Cache with limited capacity. Removes least recently used when full.
    Source: https://docs.python.org/3/library/collections.html#collections.OrderedDict
    """

    def __init__(self, maxsize, *args, **kwds):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


class CacheEntry:
    """Class representing a transposition table entry."""

    def __init__(
        self,
        value: int,
        best_move: Board,
        min: bool = False,
        max: bool = False,
    ):
        self.value = value
        self.best_move = best_move
        self.min = min
        self.max = max
