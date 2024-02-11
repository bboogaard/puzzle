import json

from django.test.testcases import TestCase

from puzzle.models import KnightMove


class TestPuzzleView(TestCase):

    def test_get(self):
        puzzle = KnightMove(word='password')
        puzzle.full_clean(exclude=('puzzle_type',))
        puzzle.save()
        response = self.client.get('/api/puzzles/knight_move/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['puzzleData']['solution'], 'PASSWORD')
