from io import BytesIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test.testcases import TestCase

from puzzle.models import KnightMove, PieSlice, Word, WordFinder, WordLadder, WordSquare
from puzzle.word_square.models import Slot
from puzzle.word_square.utils import random


User = get_user_model()


class TestKnightMoveView(TestCase):

    def test_get(self):
        response = self.client.get('/puzzle/knight-move/')
        self.assertEqual(response.status_code, 200)


class TestPieSliceView(TestCase):

    def test_get(self):
        response = self.client.get('/puzzle/pie-slice/')
        self.assertEqual(response.status_code, 200)


class TestWordFinderView(TestCase):

    def test_get(self):
        response = self.client.get('/puzzle/word-finder/')
        self.assertEqual(response.status_code, 200)


class TestImportKnightMoveView(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user('admin', password='welkom', is_staff=True)

    def test_get(self):
        self.client.login(username='admin', password='welkom')
        response = self.client.get('/puzzle/import-knight-move/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='admin', password='welkom')
        data = {
            'word': 'woonzorg',
            'slots': ['N', 'W', 'O', 'R', '*', 'O', 'O', 'Z', 'G'],
            'slot-size': 3
        }
        response = self.client.post('/puzzle/import-knight-move/', data=data)
        self.assertEqual(response.status_code, 302)
        knight_move = KnightMove.objects.first()
        self.assertIsNotNone(knight_move)
        self.assertEqual(knight_move.word, 'WOONZORG')
        self.assertEqual(knight_move.board.serialize(), [
            ['N', 'W', 'O'],
            ['R', '*', 'O'],
            ['O', 'Z', 'G'],
        ])
        self.assertIsNotNone(knight_move.image)

    def test_post_invalid(self):
        self.client.login(username='admin', password='welkom')
        data = {
            'word': 'woonzorg',
            'slots': ['N', 'W', 'O', 'R', '*', 'O'],
            'slot-size': 3
        }
        response = self.client.post('/puzzle/import-knight-move/', data=data)
        self.assertEqual(response.status_code, 200)


class TestImportPieSliceView(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user('admin', password='welkom', is_staff=True)

    def test_get(self):
        self.client.login(username='admin', password='welkom')
        response = self.client.get('/puzzle/import-pie-slice/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='admin', password='welkom')
        data = {
            'word': 'kattenbel',
            'obfuscated_word': 'nbelkat?e'
        }
        response = self.client.post('/puzzle/import-pie-slice/', data=data)
        self.assertEqual(response.status_code, 302)
        pie_slice = PieSlice.objects.first()
        self.assertIsNotNone(pie_slice)
        self.assertEqual(pie_slice.word, 'KATTENBEL')
        self.assertEqual(pie_slice.obfuscated_word, 'NBELKAT?E')
        self.assertIsNotNone(pie_slice.image)

    def test_post_invalid(self):
        self.client.login(username='admin', password='welkom')
        data = {
            'word': 'kattenbel',
            'obfuscated_word': 'belkat?e'
        }
        response = self.client.post('/puzzle/import-pie-slice/', data=data)
        self.assertEqual(response.status_code, 200)


class TestImportWordFinderView(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user('admin', password='welkom', is_staff=True)

    def test_get(self):
        self.client.login(username='admin', password='welkom')
        response = self.client.get('/puzzle/import-word-finder/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='admin', password='welkom')
        data = {
            'hints': 'aap\r\nriek\r\nezel\r\npeer\r\n',
            'slots': ['A', 'A', 'P', 'E', 'R', 'I', 'E', 'K', 'E', 'Z', 'E', 'L', 'N', 'E', 'R', 'N'],
            'slot-size': 4,
            'solution': 'neen'
        }
        response = self.client.post('/puzzle/import-word-finder/', data=data)
        self.assertEqual(response.status_code, 302)
        word_finder = WordFinder.objects.first()
        self.assertIsNotNone(word_finder)
        self.assertEqual(word_finder.hints, 'AAP\nRIEK\nEZEL\nPEER')
        self.assertEqual(word_finder.words, 'AAP\nRIEK\nEZEL\nPEER')
        self.assertEqual(word_finder.size, 4)
        self.assertEqual(word_finder.solution, 'NEEN')
        self.assertIsNotNone(word_finder.image)

    def test_post_invalid(self):
        self.client.login(username='admin', password='welkom')
        data = {
            'hints': 'aap\r\nriek\r\nezel\r\npeer\r\n',
            'slots': ['P', 'A', 'P', 'E', 'R', 'I', 'E', 'K', 'E', 'Z', 'E', 'L', 'N', 'E', 'R', 'N'],
            'solution': 'en'
        }
        response = self.client.post('/puzzle/import-word-finder/', data=data)
        self.assertEqual(response.status_code, 200)


class TestImportWordsView(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user('admin', password='welkom', is_staff=True)

    def test_get(self):
        self.client.login(username='admin', password='welkom')
        response = self.client.get('/puzzle/import-words/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='admin', password='welkom')
        fh = BytesIO(b'ABAC\r\nLOBE\r\nPREP\r\nSADE')
        fh = InMemoryUploadedFile(
            file=fh,
            field_name='import_file',
            name='words.csv',
            content_type='text/csv',
            size=fh.tell(),
            charset='utf-8'
        )
        data = {
            'import_file': fh,
        }
        response = self.client.post('/puzzle/import-words/', data=data)
        self.assertEqual(response.status_code, 302)
        words = Word.objects.all()
        self.assertEqual(len(words), 4)
        self.assertTrue(all(word.tokens.count() == 4 for word in words))

    def test_post_invalid(self):
        self.client.login(username='admin', password='welkom')
        data = {}
        response = self.client.post('/puzzle/import-words/', data=data)
        self.assertEqual(response.status_code, 200)


class TestImportWordSquareView(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user('admin', password='welkom', is_staff=True)

    def test_get(self):
        self.client.login(username='admin', password='welkom')
        response = self.client.get('/puzzle/import-word-square/')
        self.assertEqual(response.status_code, 200)

    @mock.patch.object(random, 'choice')
    def test_post(self, mock_choice):
        mock_choice.side_effect = [
            Slot(0, 0),
            Slot(1, 1),
            Slot(2, 2),
            Slot(3, 3)
        ]
        self.client.login(username='admin', password='welkom')
        data = {
            'slots': ["A", "B", "A", "C", "L", "O", "B", "E", "P", "R", "E", "P", "S", "A", "D", "E"],
            'slot-size': 4
        }
        response = self.client.post('/puzzle/import-word-square/', data=data)
        self.assertEqual(response.status_code, 302)
        word_square = WordSquare.objects.first()
        self.assertIsNotNone(word_square)
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

    def test_post_invalid(self):
        self.client.login(username='admin', password='welkom')
        data = {}
        response = self.client.post('/puzzle/import-word-square/', data=data)
        self.assertEqual(response.status_code, 200)


class TestImportWordLadderView(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user('admin', password='welkom', is_staff=True)

    def test_get(self):
        self.client.login(username='admin', password='welkom')
        response = self.client.get('/puzzle/import-word-ladder/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username='admin', password='welkom')
        data = {
            'slots': [
                "P", "O", "O", "L", "C", "O", "O", "L", "C", "O", "O", "K", "B", "O", "O", "K",
                "B", "O", "O", "T", "B", "O", "A", "T", "B", "R", "A", "T"
            ],
            'slot-width': 4
        }
        response = self.client.post('/puzzle/import-word-ladder/', data=data)
        self.assertEqual(response.status_code, 302)
        word_ladder = WordLadder.objects.first()
        self.assertIsNotNone(word_ladder)
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

    def test_post_invalid(self):
        self.client.login(username='admin', password='welkom')
        data = {}
        response = self.client.post('/puzzle/import-word-ladder/', data=data)
        self.assertEqual(response.status_code, 200)
