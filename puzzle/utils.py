import csv
from typing import List, TextIO


def csv_to_grid(fh: TextIO) -> List[List[str]]:
    infile = csv.reader(fh)
    return [
        [col for col in row]
        for row in infile
    ]
