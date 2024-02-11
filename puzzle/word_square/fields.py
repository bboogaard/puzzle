from typing import List

import numpy

from puzzle.common.fields import Board as BaseBoard
from puzzle.word_square.models import create_series, Series, SeriesType, Slot


class Board(BaseBoard):

    size: int

    slots: List[Series]

    def __init__(self, size: int):
        self.size = size
        self.slots = [
            create_series([Slot(row, col) for col in range(self.size)], SeriesType.ROW)
            for row in range(self.size)
        ]

    def clone(self):
        return Board.deserialize(self.serialize())

    def simple(self):
        return [
            [sl.letter for sl in row]
            for row in self.slots
        ]

    def flat(self):
        return [
            sl
            for row in self.slots
            for sl in row
        ]

    def open(self):
        return [
            sl
            for row in self.slots
            for sl in row if sl.letter == ' '
        ]

    def related_series(self, slot: Slot) -> List[Series]:
        return list(filter(lambda s: slot in s, self.series))

    @property
    def series(self):
        return self.rows + self.columns

    @property
    def rows(self):
        return self.slots[:]

    @property
    def columns(self):
        return [
            create_series(list(numpy.array(self.slots)[:, n]), SeriesType.COLUMN)
            for n in range(self.size)
        ]

    def is_valid(self):
        return len(self.open()) == 0

    def __getitem__(self, item):
        return self._get_slot(item).letter

    def __setitem__(self, key, value):
        self._get_slot(key).letter = value

    def __delitem__(self, item):
        self._get_slot(item).letter = ' '

    def _get_slot(self, key):
        try:
            x, y = key
            if not isinstance(x, int) or not isinstance(y, int):
                raise ValueError()
            return self.slots[x][y]
        except (IndexError, ValueError):
            raise KeyError("Slot not found")

    def serialize(self):
        return [
            [slot.letter for slot in row]
            for row in self.rows
        ]

    @classmethod
    def deserialize(cls, value):
        slots = [
            [Slot(x, y, letter) for y, letter in enumerate(row)]
            for x, row in enumerate(value)
        ]
        word_finder = cls(len(slots))
        word_finder.slots = slots
        return word_finder
