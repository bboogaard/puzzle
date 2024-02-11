from django.core.management import BaseCommand

from puzzle.models import WordSquare
from puzzle.word_square.exceptions import WordSquareCreateError


class Command(BaseCommand):

    help = "Management command to generate word square puzzles"

    def add_arguments(self, parser):
        parser.add_argument('size', type=int, nargs=1)
        parser.add_argument('num_puzzles', type=int, nargs=1)

    def handle(self, *args, **options):
        num_generated = 0
        num_puzzles = options['num_puzzles'][0]
        while True:
            if num_generated == num_puzzles:
                break
            try:
                word_square = WordSquare(size=options['size'][0])
                word_square.generate()
                num_generated += 1
                print(f'{num_generated}/{num_puzzles} puzzles generated')
            except WordSquareCreateError:
                ...
