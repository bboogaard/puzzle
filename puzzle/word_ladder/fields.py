from typing import List

from Levenshtein import distance

from puzzle.common.fields import Board as BaseBoard
from puzzle.word_ladder.models import Slot


class Board(BaseBoard):

    size: int

    slots: List[List[Slot]]

    def __init__(self, size: int):
        self.size = size
        self.slots = []

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

    @property
    def rows(self):
        return self.slots[:]

    @property
    def height(self):
        return len(self.slots)

    @property
    def words(self):
        return list(map(lambda r: "".join(slot.letter for slot in r), self.rows))

    def add_row(self, word: str):
        row = [Slot(len(self.slots), x) for x in range(self.size)]
        self.slots.append(row)
        for index, slot in enumerate(row):
            self[(slot.x, slot.y)] = word[index]

    def is_valid(self):
        first_word = self.words[0] if self.words else None
        last_word = self.words[len(self.words) - 1] if self.words else None
        return distance(first_word, last_word) == self.size if first_word and last_word else False

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
        sizes = list(set(len(row) for row in slots))
        if len(sizes) != 1:
            raise ValueError("Deserialization error")
        word_ladder = cls(sizes[0])
        word_ladder.slots = slots
        return word_ladder
