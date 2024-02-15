from django.urls import path

from puzzle.views import ImportKnightMoveView, ImportPieSliceView, ImportWordFinderView, ImportWordsView, \
    ImportWordLadderView, ImportWordSquareView, KnightMoveView, PieSliceView, WordFinderView, WordLadderView, \
    WordSquareView


app_name = 'puzzle'


urlpatterns = [
    path('knight-move/', KnightMoveView.as_view(), name='knight_move'),
    path('pie-slice/', PieSliceView.as_view(), name='pie_slice'),
    path('word-finder/', WordFinderView.as_view(), name='word_finder'),
    path('word-square/', WordSquareView.as_view(), name='word_square'),
    path('word-ladder/', WordLadderView.as_view(), name='word_ladder'),
    path('import-knight-move/', ImportKnightMoveView.as_view(), name='import_knight_move'),
    path('import-pie-slice/', ImportPieSliceView.as_view(), name='import_pie_slice'),
    path('import-word-finder/', ImportWordFinderView.as_view(), name='import_word_finder'),
    path('import-words/', ImportWordsView.as_view(), name='import_words'),
    path('import-word-square/', ImportWordSquareView.as_view(), name='import_word_square'),
    path('import-word-ladder/', ImportWordLadderView.as_view(), name='import_word_ladder'),
]
