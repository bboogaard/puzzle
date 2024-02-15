from typing import Any, List

from puzzle.common.fields import Board as BaseBoard
from puzzle.common.utils import chunks
from puzzle.knight_move.exceptions import SlotNotAvailableError, SlotOutOfRangeError
from puzzle.knight_move.models import Slot


class Board(BaseBoard):

    slots: List[Slot]

    def __init__(self, slots: List[Slot]):
        self.slots = slots

    def __setitem__(self, key, value):
        slot = self._get_slot(key)
        if slot.letter:
            raise SlotNotAvailableError()
        slot.letter = value

    def __getitem__(self, item):
        return self._get_slot(item)

    def __iter__(self):
        return iter(self.slots)

    def is_valid(self, word: str, slots: List[Slot] = None):
        slots = slots or [slot for slot in self.slots if slot.letter != '*']
        if len(slots) != len(word):
            return False

        if len(slots) == 1:
            return slots[0].letter == word[0]

        for slot in filter(lambda s: s.letter == word[0], slots):
            if not (slts := self.get_moves(slot.x, slot.y, should_be_empty=False)):
                break
            for slt in slts:
                if slt.letter == word[1]:
                    sls = slots[:]
                    sls.remove(slot)
                    if self.is_valid(word[1:], sls):
                        return True

        return False

    def get_moves(self, x: int, y: int, should_be_empty: bool = True) -> List[Slot]:
        result = []
        options = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for xx, yy in options:
            try:
                if not self[x + xx, y + yy].letter or not should_be_empty:
                    result.append(self[x + xx, y + yy])
            except SlotOutOfRangeError:
                ...
        return result

    @property
    def is_full(self):
        return all(slot.letter for slot in self.slots)

    @property
    def rows(self):
        return chunks(self.slots, 3)

    def _get_slot(self, key: Any) -> Slot:
        try:
            x, y = key
            if not isinstance(x, int) or not isinstance(y, int):
                raise ValueError()
        except ValueError:
            raise ValueError("Can only slice x, y coordinates")
        slot = next(filter(lambda s: s.x == x and s.y == y, self.slots), None)
        if slot is None:
            raise SlotOutOfRangeError()
        return slot

    def serialize(self):
        return [
            [slot.letter for slot in row]
            for row in self.rows
        ]

    @classmethod
    def deserialize(cls, value):
        return cls(
            [
                Slot(x, y, letter)
                for x, row in enumerate(value)
                for y, letter in enumerate(row)
            ]
        )
