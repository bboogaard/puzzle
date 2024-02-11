import base64
import os
import tempfile
import uuid
from io import BytesIO
from typing import BinaryIO, Dict

import matplotlib.pyplot as plt
import seaborn as sns
from django.conf import settings
from django.core.validators import MaxValueValidator, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageDraw, ImageFont

from puzzle.common.fields import BoardField
from puzzle.knight_move import fields as knight_move_fields
from puzzle.knight_move import utils as knight_move_utils
from puzzle.pie_slice.utils import obfuscate_word
from puzzle.word_finder import fields as word_finder_fields
from puzzle.word_finder import utils as word_finder_utils
from puzzle.word_finder.exceptions import WordFinderCreateError
from puzzle.word_finder.models import CreateWordFinderRequest
from puzzle.word_square import fields as word_square_fields
from puzzle.word_square import utils as word_square_utils


def image_upload_to(instance, filename):
    return f'images/{uuid.uuid4()}.png'


class PuzzleQuerySet(models.QuerySet):

    def get_narrow(self, pk):
        obj = self.get(pk=pk)
        model = {
            Puzzle.PuzzleType.KNIGHT_MOVE: KnightMove,
            Puzzle.PuzzleType.PIE_SLICE: PieSlice,
            Puzzle.PuzzleType.WORD_FINDER: WordFinder,
            Puzzle.PuzzleType.WORD_SQUARE: WordSquare
        }.get(obj.puzzle_type)
        return model.objects.get(pk=pk)


class Puzzle(models.Model):

    class PuzzleType(models.TextChoices):
        KNIGHT_MOVE = 'knight_move', _('Knight move')
        PIE_SLICE = 'pie_slice', _('Pie slice')
        WORD_FINDER = 'word_finder', _('Word finder')
        WORD_SQUARE = 'word_square', _('Word square')

    image = models.ImageField(null=True, blank=True, upload_to=image_upload_to)

    puzzle_time = models.DateTimeField(auto_now=True)

    puzzle_type = models.CharField(max_length=12, choices=PuzzleType.choices)

    objects = PuzzleQuerySet.as_manager()

    class Meta:
        ordering = ("-puzzle_time",)

    def save(self, generate: bool = True, *args, **kwargs):
        self.puzzle_type = self.get_puzzle_type()
        if not self.image and generate:
            self.generate()
        super().save(*args, **kwargs)

    def get_puzzle_type(self):
        raise NotImplementedError()

    def generate(self):
        raise NotImplementedError()

    def import_puzzle(self, **kwargs):
        raise NotImplementedError()

    def get_puzzle_data(self):
        raise NotImplementedError()


class WordPuzzleQuerySet(models.QuerySet):

    def validate_word(self, instance, word_length: int):
        if len(instance.word) != word_length:
            raise ValidationError(f"Word should be {word_length} characters")
        queryset = self.filter(word__iexact=instance.word)
        if not instance._state.adding:
            queryset = queryset.exclude(pk=instance.pk)
        if queryset.exists():
            raise ValidationError(f"There already is a puzzle with word {instance.word}")


class KnightMove(Puzzle):

    board = BoardField(board_class=knight_move_fields.Board)

    word = models.CharField(max_length=8, unique=True)

    objects = WordPuzzleQuerySet.as_manager()

    def __str__(self):
        return self.word

    def clean(self):
        manager = self.__class__.objects
        manager.validate_word(self, 8)

    def save(self, *args, **kwargs):
        self.word = self.word.upper()
        super().save(*args, **kwargs)

    def get_puzzle_type(self):
        return self.PuzzleType.KNIGHT_MOVE

    def get_puzzle_data(self):
        return {
            'data': base64.b64encode(self.image.open().read()).decode(),
            'solution': self.word
        }

    def generate(self):
        letters = knight_move_utils.generate_knight_move(self.word)
        self.board = knight_move_fields.Board.deserialize(letters)
        self.image.save(f'{self.word}.png', self.draw_image(self.board))

    def import_puzzle(self, **kwargs):
        self.board = knight_move_fields.Board.deserialize(kwargs.get('slots', []))
        self.image.save(f'{self.word}.png', self.draw_image(self.board))

    @staticmethod
    def draw_image(board: knight_move_fields.Board) -> BinaryIO:
        width = 300
        height = 300
        image = Image.new(mode='L', size=(width + 1, height + 1), color=255)

        # Draw some lines
        draw = ImageDraw.Draw(image)
        y_start = 0
        y_end = height
        step_size = int(width / 3)

        for x in range(0, width + step_size, step_size):
            line = ((x, y_start), (x, y_end))
            draw.line(line, fill=128)

        x_start = 0
        x_end = width

        for y in range(0, height + step_size, step_size):
            line = ((x_start, y), (x_end, y))
            draw.line(line, fill=128)

        font = ImageFont.truetype(os.path.join(settings.PROJECT_DIR, 'puzzle', 'Arial.ttf'), 50)

        for board_y, x in enumerate(range(0, width, step_size)):
            for board_x, y in enumerate(range(0, height, step_size)):
                letter = board[(board_x, board_y)].letter
                inc_size = 32 if letter == '*' else 25
                draw.text((x + inc_size, y + inc_size), letter, font=font)

        del draw

        fh = BytesIO()
        image.save(fh, format='PNG')
        return fh


class PieSlice(Puzzle):

    obfuscated_word = models.CharField(max_length=9)

    word = models.CharField(max_length=9, unique=True)

    objects = WordPuzzleQuerySet.as_manager()

    def __str__(self):
        return self.word

    def clean(self):
        manager = self.__class__.objects
        manager.validate_word(self, 9)

    def save(self, *args, **kwargs):
        self.word = self.word.upper()
        super().save(*args, **kwargs)

    def get_puzzle_type(self):
        return self.PuzzleType.PIE_SLICE

    def get_puzzle_data(self):
        return {
            'data': base64.b64encode(self.image.open().read()).decode(),
            'solution': self.word
        }

    def generate(self):
        self.obfuscated_word = obfuscate_word(self.word)
        self.image.save(f'{self.word}.png', self.draw_image(self.obfuscated_word))

    def import_puzzle(self, **kwargs):
        self.image.save(f'{self.word}.png', self.draw_image(self.obfuscated_word))

    @staticmethod
    def draw_image(word: str):
        sns.set(font_scale=1.2)
        fig = plt.figure(figsize=(10, 10))
        fig.patch.set_facecolor("red")

        patches, texts = plt.pie(
            x=9 * [100 / 9],
            labels=list(word),
            colors=["white"],
            startangle=90,
            # Bring labels inside the pie
            labeldistance=0.7,
            wedgeprops={"edgecolor": "black", 'linewidth': 1, 'linestyle': 'solid', 'antialiased': True}
        )

        # iterate over the text labels
        # make each label bold and center-aligned
        for text in texts:
            text.set_fontweight('bold')
            text.set_horizontalalignment('center')

        tmp = tempfile.NamedTemporaryFile(suffix='.png')
        plt.show()
        plt.savefig(tmp.name)
        fh = open(tmp.name, 'rb')
        fh.seek(0)
        return fh


class WordFinder(Puzzle):

    board = BoardField(board_class=word_finder_fields.Board)

    hints = models.TextField(blank=True)

    size = models.PositiveIntegerField(validators=[MaxValueValidator(11)])

    solution = models.CharField(max_length=11, blank=True)

    words = models.TextField(blank=True)

    def __str__(self):
        return self.solution

    def clean(self):
        self.words = '\n'.join(map(lambda w: w.strip().upper(), self.words.splitlines()))
        if not self.image and self.size:
            try:
                response = word_finder_utils.generate_word_finder(CreateWordFinderRequest(
                    words=self.words.splitlines(),
                    size=self.size
                ))
                self.hints = '\n'.join(response.hints)
                self.solution = response.solution
                self.board = word_finder_fields.Board.deserialize(response.words)
            except WordFinderCreateError:
                raise ValidationError("Could not create a solution")

    def get_puzzle_type(self):
        return self.PuzzleType.WORD_FINDER

    def get_puzzle_data(self):
        return {
            'data': self.board.serialize(),
            'hints': self.hints.splitlines(),
            'words': self.board.words(self.hints.splitlines()),
            'solution': self.solution
        }

    def generate(self):
        self.image.save('word_finder.png', self.draw_image(self.board))

    def import_puzzle(self, **kwargs):
        words = kwargs.get('words', [])
        self.board = word_finder_fields.Board.deserialize(words)
        self.image.save('word_finder.png', self.draw_image(self.board))

    def draw_image(self, board: word_finder_fields.Board) -> BinaryIO:
        words = board.simple()
        width = 100 * self.size
        height = 100 * self.size
        image = Image.new(mode='L', size=(width + 1, height + 1), color=255)

        # Draw some lines
        draw = ImageDraw.Draw(image)
        y_start = 0
        y_end = height
        step_size = int(width / self.size)

        for x in range(0, width + step_size, step_size):
            line = ((x, y_start), (x, y_end))
            draw.line(line, fill=128)

        x_start = 0
        x_end = width

        for y in range(0, height + step_size, step_size):
            line = ((x_start, y), (x_end, y))
            draw.line(line, fill=128)

        font = ImageFont.truetype(os.path.join(settings.PROJECT_DIR, 'puzzle', 'Arial.ttf'), 50)

        for board_x, y in enumerate(range(0, width, step_size)):
            for board_y, x in enumerate(range(0, height, step_size)):
                letter = words[board_x][board_y]
                inc_size = 25
                draw.text((x + inc_size, y + inc_size), letter, font=font)

        del draw

        fh = BytesIO()
        image.save(fh, format='PNG')
        return fh


class WordQuerySet(models.QuerySet):

    def get_for_tokens(self, tokens: Dict[int, str]):
        queryset = self._clone()
        clause = models.Q()
        for index, token in tokens.items():
            clause &= models.Q(
                models.Exists(
                    WordToken.objects.filter(
                        word__pk=models.OuterRef('pk'),
                        index=index,
                        token=token
                    )
                )
            )
        return queryset.filter(clause)


class Word(models.Model):

    word = models.CharField(max_length=10, unique=True)

    size = models.PositiveIntegerField()

    objects = WordQuerySet.as_manager()

    class Meta:
        ordering = ('word',)

    def __str__(self):
        return self.word

    def save(self, *args, **kwargs):
        self.word = self.word.upper()
        self.size = len(self.word)
        super().save(*args, **kwargs)


class WordToken(models.Model):

    word = models.ForeignKey(Word, related_name='tokens', on_delete=models.CASCADE)

    index = models.PositiveIntegerField()

    token = models.CharField(max_length=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('word', 'index'),
                name='Unique constraint on word and index'
            )
        ]
        ordering = ('word', 'index')

    def __str__(self):
        return f'{self.word} - {self.index}'


class WordSquare(Puzzle):

    board = BoardField(board_class=word_square_fields.Board)

    size = models.PositiveIntegerField(validators=[MaxValueValidator(11)])

    solution = BoardField(board_class=word_square_fields.Board)

    solution_image = models.ImageField(null=True, blank=True, upload_to=image_upload_to)

    def __str__(self):
        return 'word square'

    def get_puzzle_type(self):
        return self.PuzzleType.WORD_SQUARE

    def get_puzzle_data(self):
        return {
            'data': self.board.serialize(),
            'hints': [
                self.solution[(slot.x, slot.y)]
                for slot in self.board.open()
            ],
            'solution': self.solution.serialize()
        }

    def generate(self):
        words = word_square_utils.generate_word_square(self.size)
        self.solution = word_square_fields.Board.deserialize(words)
        self.board = word_square_utils.obfuscate_board(self.solution)
        self.image.save('word_square.png', self.draw_image(self.board))
        self.solution_image.save('word_square.png', self.draw_image(self.solution))

    def import_puzzle(self, **kwargs):
        words = kwargs.get('words', [])
        self.solution = word_square_fields.Board.deserialize(words)
        self.board = word_square_utils.obfuscate_board(self.solution)
        self.image.save('word_square.png', self.draw_image(self.board))
        self.solution_image.save('word_square.png', self.draw_image(self.solution))

    def draw_image(self, board: word_square_fields.Board) -> BinaryIO:
        words = board.simple()
        width = 100 * self.size
        height = 100 * self.size
        image = Image.new(mode='L', size=(width + 1, height + 1), color=255)

        # Draw some lines
        draw = ImageDraw.Draw(image)
        y_start = 0
        y_end = height
        step_size = int(width / self.size)

        for x in range(0, width + step_size, step_size):
            line = ((x, y_start), (x, y_end))
            draw.line(line, fill=128)

        x_start = 0
        x_end = width

        for y in range(0, height + step_size, step_size):
            line = ((x_start, y), (x_end, y))
            draw.line(line, fill=128)

        font = ImageFont.truetype(os.path.join(settings.PROJECT_DIR, 'puzzle', 'Arial.ttf'), 50)

        for board_x, y in enumerate(range(0, width, step_size)):
            for board_y, x in enumerate(range(0, height, step_size)):
                letter = words[board_x][board_y]
                inc_size = 25
                draw.text((x + inc_size, y + inc_size), letter, font=font)

        del draw

        fh = BytesIO()
        image.save(fh, format='PNG')
        return fh
