import random
from typing import List

from Levenshtein import distance

from puzzle.common.utils import tokenize_word
from puzzle.word_ladder.exceptions import WordLadderCreateError
from puzzle.word_ladder.fields import Board


MAX_HEIGHT = 10


def generate_word_ladder(size: int) -> List[List[str]]:
    from puzzle.models import Word

    board = Board(size)

    def get_words(wd: str = None) -> List[str]:
        queryset = Word.objects.filter(size=size)
        if board.words:
            queryset = queryset.exclude(word__in=board.words)
        if wd:
            tokens = {
                iex: token
                for iex, token in tokenize_word(wd).items()
                if token != ' '
            }
            return list(queryset.get_for_tokens(tokens).values_list('word', flat=True))
        return list(queryset.order_by('?').values_list('word', flat=True)[:1])

    max_dist = 0
    while True:
        if not board.rows:
            if not (words := get_words()):
                break
            word = random.choice(words)
            board.add_row(word)
            continue
        elif board.is_valid():
            break
        elif board.height > MAX_HEIGHT:
            break

        previous = board.words[len(board.words) - 1]
        for idx in range(len(previous)):
            word = previous[:idx] + ' ' + previous[(idx + 1):]
            if words := get_words(word):
                for wrd in words:
                    dist = distance(wrd, board.words[0])
                    if dist > max_dist:
                        max_dist = dist
                        break
                    elif dist == max_dist:
                        break
                else:
                    continue
                board.add_row(wrd)
                break
        else:
            break

    if not board.is_valid():
        raise WordLadderCreateError()
    return board.simple()


def obfuscate_board(board: Board) -> Board:
    brd = board.clone()
    for row in brd.rows[1:-1]:
        for slot in row:
            del brd[(slot.x, slot.y)]
    return brd
