from unittest import mock

from django.core.management import call_command
from django.test.testcases import TestCase

from puzzle.models import WordLadder, WordSquare
from puzzle.word_ladder.models import Slot as WordLadderSlot
from puzzle.word_square.models import Slot as WordSquareSlot
from puzzle.word_square.utils import random

from tests.puzzle.factories import WordFactory


class TestCommands(TestCase):

    @mock.patch.object(random, 'choice')
    @mock.patch.object(random, 'randint')
    def test_generate_word_squares(self, mock_int, mock_choice):
        mock_int.side_effect = [3, 0, 2, 0, 1, 0, 0, 0, 0]
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
            call_command('generate_word_squares', 4, 1)

        word_squares = WordSquare.objects.all()
        self.assertEqual(len(word_squares), 1)
        word_square = word_squares[0]
        self.assertEqual(
            word_square.board.serialize(),
            [
                [" ", "B", "A", "C"], ["L", " ", "B", "E"], ["P", "R", " ", "P"], ["S", "A", "D", " "]
            ]
        )
        self.assertEqual(
            word_square.solution.serialize(),
            [

                ["A", "B", "A", "C"], ["L", "O", "B", "E"], ["P", "R", "E", "P"], ["S", "A", "D", "E"]
            ]
        )
        self.assertIsNotNone(word_square.image)
        self.assertIsNotNone(word_square.solution_image)

    @mock.patch.object(random, 'choice')
    def test_generate_word_ladders(self, mock_choice):
        mock_choice.side_effect = ['QUIZ', 'POOL']
        WordFactory(word='POOL')
        WordFactory(word='COOL')
        WordFactory(word='COOK')
        WordFactory(word='BOOK')
        WordFactory(word='BOOT')
        WordFactory(word='BOAT')
        WordFactory(word='BRAT')

        def mock_order(instance, *args):
            if instance.query.is_sliced:
                raise TypeError("Cannot reorder a query once a slice has been taken.")
            obj = instance._chain()
            obj.query.clear_ordering(force=True, clear_default=False)
            obj.query.add_ordering('word')
            return obj

        with mock.patch('django.db.models.query.QuerySet.order_by', mock_order):
            call_command('generate_word_ladders', 4, 1)

        word_ladders = WordLadder.objects.all()
        self.assertEqual(len(word_ladders), 1)
        word_ladder = word_ladders[0]

        self.assertEqual(
            word_ladder.board.serialize(),
            [
                ["P", "O", "O", "L"], [" ", " ", " ", " "], [" ", " ", " ", " "], [" ", " ", " ", " "],
                [" ", " ", " ", " "], [" ", " ", " ", " "], ["B", "R", "A", "T"]]
        )
        self.assertEqual(
            word_ladder.solution.serialize(),
            [
                ["P", "O", "O", "L"], ["C", "O", "O", "L"], ["C", "O", "O", "K"], ["B", "O", "O", "K"],
                ["B", "O", "O", "T"], ["B", "O", "A", "T"], ["B", "R", "A", "T"]
            ]
        )
        self.assertIsNotNone(word_ladder.image)
        self.assertIsNotNone(word_ladder.solution_image)
