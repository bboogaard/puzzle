import random
from typing import List

from puzzle.knight_move.exceptions import NoMovesError
from puzzle.knight_move.fields import Board


def generate_knight_move(word: str) -> List[List[str]]:
    board = Board.deserialize([
        [None, None, None],
        [None, '*', None],
        [None, None, None]
    ])
    options = [slot for slot in board if slot.letter != '*']
    slot = options[random.randint(0, len(options) - 1)]
    letter_index = 0
    board[(slot.x, slot.y)] = word[letter_index]
    while not board.is_full:
        if not (slots := board.get_moves(slot.x, slot.y)):
            raise NoMovesError()
        slot = random.choice(slots)
        letter_index += 1
        board[(slot.x, slot.y)] = word[letter_index]
    return board.serialize()
