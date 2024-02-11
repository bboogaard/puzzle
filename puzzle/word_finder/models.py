from collections import UserList
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Slot:
    x: int
    y: int
    letter: Optional[str] = ' '


class Series(UserList):
    words: List[str]

    def __init__(self, initlist=None):
        super().__init__(initlist)
        self.words = []


@dataclass
class CreateWordFinderRequest:
    words: List[str]
    size: int


@dataclass
class CreateWordFinderResponse:
    words: List[List[str]]
    hints: List[str]
    solution: str
