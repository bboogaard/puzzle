from collections import UserList
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


@dataclass
class Slot:
    x: int
    y: int
    letter: Optional[str] = ' '

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)


class SeriesType(Enum):
    ROW = 'row'
    COLUMN = 'column'


class Series(UserList):

    series_type: SeriesType

    def __contains__(self, item):
        return (item.x, item.y) in [(slot.x, slot.y) for slot in self]

    def __eq__(self, other):
        return [(slot.x, slot.y) for slot in self] == [(slot.x, slot.y) for slot in other]


def create_series(initlist: List[Slot], series_type: SeriesType) -> Series:
    series = Series(initlist)
    series.series_type = series_type
    return series
