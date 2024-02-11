from rest_framework.serializers import ModelSerializer, SerializerMethodField

from puzzle.models import Puzzle


class PuzzleSerializer(ModelSerializer):

    puzzle_data = SerializerMethodField()

    class Meta:
        model = Puzzle
        fields = ('puzzle_data',)

    @staticmethod
    def get_puzzle_data(obj):
        puzzle = Puzzle.objects.get_narrow(obj.pk)
        return puzzle.get_puzzle_data()
