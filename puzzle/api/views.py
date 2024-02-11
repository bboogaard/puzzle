from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from puzzle.api.serializers import PuzzleSerializer
from puzzle.models import Puzzle


class PuzzleView(GenericAPIView):

    renderer_classes = (CamelCaseJSONRenderer,)

    serializer_class = PuzzleSerializer

    def get(self, request, puzzle_type, *args, **kwargs):
        instance = self.get_queryset().first()
        if not instance:
            return Response(status=404)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        return Puzzle.objects.filter(puzzle_type=self.kwargs['puzzle_type']).order_by('?')
