import random
from typing import List

from puzzle.common.utils import tokenize_word
from puzzle.word_square.exceptions import WordSquareCreateError
from puzzle.word_square.fields import Board
from puzzle.word_square.models import Series


def generate_word_square(size: int) -> List[List[str]]:
    from puzzle.models import Word

    board = Board(size)

    def get_words(wrd: str) -> List[str]:
        queryset = Word.objects.filter(size=size)
        tokens = {
            idx: token
            for idx, token in tokenize_word(wrd).items()
            if token != ' '
        }
        if tokens:
            return list(queryset.get_for_tokens(tokens).values_list('word', flat=True))
        return list(queryset.order_by('?').values_list('word', flat=True)[:1])

    def word_fits(wrd: str, sr: Series) -> bool:
        for idx, slt in enumerate(sr):
            token = wrd[idx]
            related = next(
                filter(
                    lambda s: s != sr,
                    board.related_series(slt)
                ),
                None
            )
            if all(st.letter != ' ' for st in related) and board[(slt.x, slt.y)] == token:
                continue
            joined = ""
            for st in related:
                if st != slt:
                    joined += st.letter
                elif st.letter == ' ' or st.letter == token:
                    joined += token
                else:
                    break
            else:
                if not get_words(joined):
                    break
            if len(joined) != len(wrd):
                break
        else:
            return True

        return False

    rows = board.rows[:]
    columns = board.columns[:]
    i = 0
    while True:
        if not rows and not columns:
            break
        series = rows if i % 2 == 0 else columns
        srs = series.pop(random.randint(0, len(series) - 1))
        if not (words := get_words(''.join(slot.letter for slot in srs))):
            break
        for word in words:
            if word_fits(word, srs):
                break
        else:
            break
        for index, slot in enumerate(srs):
            board[(slot.x, slot.y)] = word[index]
        i += 1
    if not board.is_valid():
        raise WordSquareCreateError()
    return board.simple()


def obfuscate_board(board: Board) -> Board:
    brd = board.clone()
    while len(brd.open()) < brd.size:
        slot = random.choice(brd.flat())
        del brd[(slot.x, slot.y)]
    return brd
