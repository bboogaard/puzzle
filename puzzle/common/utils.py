from typing import Dict, List


def import_words(words: List[str]):
    from puzzle.models import Word, WordToken

    wds = []
    for wd in words:
        if 4 <= len(wd) <= 10:
            wds.append(Word(word=wd.upper(), size=len(wd)))
    words = Word.objects.bulk_create(wds)
    tks = []
    for word in words:
        tokens = tokenize_word(word.word)
        for index, token in tokens.items():
            tks.append(WordToken(word=word, index=index, token=token))
    WordToken.objects.bulk_create(tks)


def tokenize_word(word: str) -> Dict[int, str]:
    return {
        idx: token
        for idx, token in enumerate(word)
    }


def chunks(iterable, size):
    result = []
    pos = 0
    while True:
        chunk = iterable[pos:(pos + size)]
        if not chunk:
            break
        result.append(chunk)
        pos = pos + size
    return result
