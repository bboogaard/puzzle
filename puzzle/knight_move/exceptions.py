class KnightMoveException(Exception):
    ...


class SlotOutOfRangeError(KnightMoveException):
    ...


class SlotNotAvailableError(KnightMoveException):
    ...


class NoMovesError(KnightMoveException):
    ...
