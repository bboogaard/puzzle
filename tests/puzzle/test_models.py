from unittest import mock

from django.core.validators import ValidationError
from django.test.testcases import TestCase

from puzzle.knight_move.utils import random
from puzzle.models import KnightMove, PieSlice, WordFinder, WordSquare
from puzzle.word_finder.models import Slot
from puzzle.word_square.exceptions import WordSquareCreateError
from puzzle.word_square.models import Slot as WordSquareSlot
from tests.puzzle.factories import WordFactory


class TestKnightMove(TestCase):

    @mock.patch.object(random, 'randint')
    def test_generate(self, mock_int):

        def mock_choice(slots):
            return slots[0]

        mock_int.return_value = 1
        puzzle = KnightMove(word='password')
        puzzle.full_clean(exclude=('puzzle_type',))
        with mock.patch.object(random, 'choice', mock_choice):
            puzzle.save()
        self.assertEqual(puzzle.board.serialize(), [
            ['S', 'P', 'O'],
            ['R', '*', 'S'],
            ['A', 'W', 'D'],
        ])
        self.assertIsNotNone(puzzle.image)

    def test_generate_invalid_length(self):
        puzzle = KnightMove(word='foobar')
        with self.assertRaises(ValidationError):
            puzzle.full_clean(exclude=('puzzle_type',))


class TestPieSlice(TestCase):

    @mock.patch.object(random, 'randint')
    @mock.patch.object(random, 'choice')
    def test_generate(self, mock_choice, mock_int):
        mock_int.side_effect = [3, 6]
        mock_choice.return_value = 'out'
        puzzle = PieSlice(word='foobarqux')
        puzzle.full_clean(exclude=('obfuscated_word', 'puzzle_type',))
        puzzle.save()
        self.assertEqual(puzzle.obfuscated_word, 'QUXFOO?AR')
        self.assertIsNotNone(puzzle.image)

    def test_generate_invalid_length(self):
        puzzle = PieSlice(word='foobar')
        with self.assertRaises(ValidationError):
            puzzle.full_clean(exclude=('obfuscated_word', 'puzzle_type',))


class TestWordFinder(TestCase):

    def test_generate(self):

        def mock_shuffle(val):
            if isinstance(val, list) and all(isinstance(v, str) for v in val):
                return ['LOW', 'CRY', 'BEFORE']
            elif isinstance(val, list) and all(isinstance(v, list) for v in val):
                if mock_shuffle.call_count == 0:
                    return [
                        [Slot(x=0, y=0, letter=' '), Slot(x=1, y=0, letter=' '), Slot(x=2, y=0, letter=' ')],
                        [Slot(x=0, y=0, letter=' '), Slot(x=1, y=1, letter=' '), Slot(x=2, y=2, letter=' ')],
                        [Slot(x=0, y=1, letter=' '), Slot(x=1, y=1, letter=' '), Slot(x=2, y=1, letter=' ')],
                        [Slot(x=0, y=0, letter=' '), Slot(x=0, y=1, letter=' '), Slot(x=0, y=2, letter=' ')],
                        [Slot(x=2, y=0, letter=' '), Slot(x=2, y=1, letter=' '), Slot(x=2, y=2, letter=' ')],
                        [Slot(x=0, y=1, letter=' '), Slot(x=1, y=2, letter=' ')],
                        [Slot(x=1, y=0, letter=' '), Slot(x=1, y=1, letter=' '), Slot(x=1, y=2, letter=' ')],
                        [Slot(x=2, y=0, letter=' ')],
                        [Slot(x=0, y=2, letter=' '), Slot(x=1, y=2, letter=' '), Slot(x=2, y=2, letter=' ')],
                        [Slot(x=1, y=0, letter=' '), Slot(x=2, y=1, letter=' ')]
                    ]
                elif mock_shuffle.call_count == 1:
                    return [
                        [Slot(x=0, y=0, letter=' '), Slot(x=0, y=1, letter=' '), Slot(x=0, y=2, letter=' ')],
                        [Slot(x=0, y=0, letter=' '), Slot(x=1, y=1, letter=' '), Slot(x=2, y=2, letter=' ')],
                        [Slot(x=2, y=0, letter=' ')],
                        [Slot(x=0, y=1, letter=' '), Slot(x=1, y=1, letter=' '), Slot(x=2, y=1, letter=' ')],
                        [Slot(x=1, y=0, letter=' '), Slot(x=2, y=1, letter=' ')],
                        [Slot(x=2, y=0, letter=' '), Slot(x=2, y=1, letter=' '), Slot(x=2, y=2, letter=' ')],
                        [Slot(x=0, y=2, letter=' '), Slot(x=1, y=2, letter=' '), Slot(x=2, y=2, letter=' ')],
                        [Slot(x=0, y=0, letter=' '), Slot(x=1, y=0, letter=' '), Slot(x=2, y=0, letter=' ')],
                        [Slot(x=1, y=0, letter=' '), Slot(x=1, y=1, letter=' '), Slot(x=1, y=2, letter=' ')],
                        [Slot(x=0, y=1, letter=' '), Slot(x=1, y=2, letter=' ')]
                    ]
                mock_shuffle.call_count += 1
            elif isinstance(val, list) and all(isinstance(v, Slot) for v in val):
                return [
                    Slot(x=1, y=1, letter=' '), Slot(x=2, y=0, letter=' '), Slot(x=2, y=2, letter=' '),
                    Slot(x=1, y=2, letter=' '), Slot(x=1, y=0, letter=' '), Slot(x=2, y=1, letter=' ')
                ]

            mock_shuffle.call_count = 0

        with mock.patch.object(random, 'shuffle', mock_shuffle):
            puzzle = WordFinder(words='LOW\nBEFORE\nCRY', size=3)
            puzzle.full_clean(exclude=('puzzle_type',))
            puzzle.save()

        self.assertEqual(puzzle.solution, 'BEFORE')
        self.assertEqual(puzzle.hints, 'CRY')
        self.assertIsNotNone(puzzle.image)


class TestWordSquare(TestCase):

    @mock.patch.object(random, 'choice')
    @mock.patch.object(random, 'randint')
    def test_generate(self, mock_int, mock_choice):
        mock_int.side_effect = [0, 2, 0, 1, 0, 0, 0, 0]
        mock_choice.side_effect = [
            WordSquareSlot(0, 0),
            WordSquareSlot(1, 1),
            WordSquareSlot(2, 2),
            WordSquareSlot(3, 3)
        ]
        WordFactory(word='ABAC')
        WordFactory(word='LOBE')
        WordFactory(word='PREP')
        WordFactory(word='SADE')
        WordFactory(word='ALPS')
        WordFactory(word='BORA')
        WordFactory(word='ABED')
        WordFactory(word='CEPE')

        def mock_order(instance, *args):
            if instance.query.is_sliced:
                raise TypeError("Cannot reorder a query once a slice has been taken.")
            obj = instance._chain()
            obj.query.clear_ordering(force=True, clear_default=False)
            obj.query.add_ordering('word')
            return obj

        with mock.patch('django.db.models.query.QuerySet.order_by', mock_order):
            puzzle = WordSquare(size=4)
            puzzle.save()

        self.assertEqual(
            puzzle.board.serialize(),
            [
                [" ", "B", "A", "C"], ["L", " ", "B", "E"], ["P", "R", " ", "P"], ["S", "A", "D", " "]
            ]
        )
        self.assertEqual(
            puzzle.solution.serialize(),
            [

                ["A", "B", "A", "C"], ["L", "O", "B", "E"], ["P", "R", "E", "P"], ["S", "A", "D", "E"]
            ]
        )
        self.assertIsNotNone(puzzle.image)
        self.assertIsNotNone(puzzle.solution_image)

    @mock.patch.object(random, 'randint')
    def test_generate_with_error(self, mock_int):
        mock_int.side_effect = [3]
        WordFactory(word='ABAC')
        WordFactory(word='LOBE')
        WordFactory(word='PREP')
        WordFactory(word='SADE')
        WordFactory(word='ALPS')
        WordFactory(word='BORA')
        WordFactory(word='ABED')
        WordFactory(word='CEPE')

        def mock_order(instance, *args):
            if instance.query.is_sliced:
                raise TypeError("Cannot reorder a query once a slice has been taken.")
            obj = instance._chain()
            obj.query.clear_ordering(force=True, clear_default=False)
            obj.query.add_ordering('word')
            return obj

        with mock.patch('django.db.models.query.QuerySet.order_by', mock_order):
            with self.assertRaises(WordSquareCreateError):
                puzzle = WordSquare(size=4)
                puzzle.save()
