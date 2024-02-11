from dataclasses import dataclass
from typing import Optional


@dataclass
class Slot:
    x: int
    y: int
    letter: Optional[str] = None
