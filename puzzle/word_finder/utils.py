import random

from puzzle.word_finder.exceptions import WordFinderCreateError
from puzzle.word_finder.fields import Board
from puzzle.word_finder.models import CreateWordFinderRequest, CreateWordFinderResponse


def generate_word_finder(request: CreateWordFinderRequest) -> CreateWordFinderResponse:
    board = Board(request.size)
    remainder = []
    hints = []
    solution = None
    words = request.words[:]
    random.shuffle(words)
    while True:
        if not words:
            break
        open_slots = board.open()
        if solution := next(filter(lambda r: len(r) == len(open_slots), remainder), None):
            random.shuffle(open_slots)
            for i, sl in enumerate(open_slots):
                board[(sl.x, sl.y)] = solution[i]
            break
        w = words.pop()
        series = board.series[:]
        random.shuffle(series)
        opt_set = False
        for s in series:
            if w in s.words:
                continue
            for n in range(len(s)):
                if n + len(w) - 1 < len(s):
                    opt = s[n:n + len(w)]
                    if all(opt[x].letter == w[x] or opt[x].letter == ' ' for x in range(len(opt))):
                        for i, sl in enumerate(opt):
                            board[(sl.x, sl.y)] = w[i]
                        s.words.append(w)
                        hints.append(w)
                        opt_set = True
                        break
            if opt_set:
                break
        else:
            remainder.append(w)
    if solution is None:
        raise WordFinderCreateError()
    return CreateWordFinderResponse(
        words=board.simple(),
        hints=list(sorted(hints)),
        solution=solution
    )
