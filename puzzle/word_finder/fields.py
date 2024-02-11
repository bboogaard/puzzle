from typing import List, Tuple

import numpy

from puzzle.common.fields import Board as BaseBoard
from puzzle.word_finder.models import Series, Slot


class Board(BaseBoard):

    size: int

    slots: List[List[Slot]]

    def __init__(self, size: int):
        self.size = size
        self.slots = [
            [Slot(row, col) for col in range(self.size)]
            for row in range(self.size)
        ]

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

    def filled(self):
        return [
            sl
            for row in self.slots
            for sl in row if sl.letter != ' '
        ]

    @property
    def series(self):
        return self.rows + self.columns + self.diagonals

    @property
    def rows(self):
        return [
            Series(row)
            for row in self.slots
        ]

    @property
    def columns(self):
        return [
            Series(list(numpy.array(self.slots)[:, n]))
            for n in range(self.size)
        ]

    @property
    def diagonals(self):
        return [
            Series(list(numpy.diag(numpy.array(self.slots), n)))
            for n in range(-(self.size - 1), self.size - 1)
        ]

    def is_valid(self, hints: List[str], solution: str):
        for word in self.words(hints):
            for x, y in word:
                del self[(x, y)]
        solution_letters = [slot.letter for slot in self.filled()]
        for letter in solution:
            try:
                solution_letters.pop(solution_letters.index(letter))
            except ValueError:
                return False
        if solution_letters:
            return False
        return True

    def words(self, hints: List[str]) -> List[List[Tuple[int, int]]]:
        result = []
        for hint in hints:
            for series in self.series:
                joined = ''.join(slot.letter for slot in series)
                if (index := joined.find(hint)) != -1:
                    slots = series[index:(index + len(hint))]
                    word = []
                    for slot in slots:
                        word.append((slot.x, slot.y))
                    result.append(word)
                    break
            else:
                break
        return result

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
