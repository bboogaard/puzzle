import random

from django.core.validators import ValidationError


def obfuscate_word(word: str) -> str:

    def _shift(value: str, index: int):
        return value[index:] + value[:index]

    direction = random.choice(('out', 'in'))
    pop_letter = random.randint(0, len(word) - 1)
    word = word[:pop_letter] + '?' + word[(pop_letter + 1):]
    word = ''.join(reversed(list(word))) if direction == 'in' else word
    begin_letter = random.randint(0, len(word) - 1)
    return _shift(word, begin_letter)


def validate_obfuscated_word(word: str, obfuscated_word: str):

    def _unshift(value: str, index: int):
        return value[:index] + value[index:]

    def _unmask(value: str, index: int, direction: str):
        value = ''.join(reversed(list(value))) if direction == 'in' else value
        return value.replace('?', word[index])

    if len(word) != len(obfuscated_word):
        raise ValidationError("Lengths of words do not match")

    if '?' not in obfuscated_word:
        raise ValidationError("No mask found")

    for i in range(len(obfuscated_word)):
        restored = _unshift(obfuscated_word, i)
        if _unmask(restored, i, 'out') or _unmask(restored, i, 'in'):
            break
    else:
        raise ValidationError("Could not restore word")
