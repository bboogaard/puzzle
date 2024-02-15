from dataclasses import dataclass
from typing import Optional


@dataclass
class Slot:
    x: int
    y: int
    letter: Optional[str] = ' '

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)
