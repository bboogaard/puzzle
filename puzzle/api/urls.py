from django.urls import path

from puzzle.api.views import PuzzleView


app_name = 'api'


urlpatterns = [
    path('puzzles/<str:puzzle_type>/', PuzzleView.as_view(), name='puzzle'),
]
