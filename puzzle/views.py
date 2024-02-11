from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from staff_view.views import StaffView

from puzzle.forms import ImportKnightMoveForm, ImportPieSliceForm, ImportWordFinderForm, ImportWordsForm, \
    ImportWordSquareForm
from puzzle.models import KnightMove, PieSlice, WordFinder, WordSquare


class KnightMoveView(TemplateView):

    model = KnightMove

    template_name = 'knight_move.html'


class PieSliceView(TemplateView):

    model = PieSlice

    template_name = 'pie_slice.html'


class WordFinderView(TemplateView):

    model = WordFinder

    template_name = 'wordfinder.html'


class WordSquareView(TemplateView):

    model = WordSquare

    template_name = 'word_square.html'


class ImportKnightMoveView(StaffView):

    title = 'Import Knight Move'

    form_class = ImportKnightMoveForm

    def form_valid(self, form):
        knight_move = form.save()
        return redirect(reverse('admin:puzzle_knightmove_change', args=[knight_move.pk]))


class ImportPieSliceView(StaffView):

    title = 'Import Pie Slice'

    form_class = ImportPieSliceForm

    def form_valid(self, form):
        pie_slice = form.save()
        return redirect(reverse('admin:puzzle_pieslice_change', args=[pie_slice.pk]))


class ImportWordFinderView(StaffView):

    title = 'Import Word Finder'

    form_class = ImportWordFinderForm

    def form_valid(self, form):
        word_finder = form.save()
        return redirect(reverse('admin:puzzle_wordfinder_change', args=[word_finder.pk]))


class ImportWordsView(StaffView):

    title = 'Import Words'

    form_class = ImportWordsForm

    def form_valid(self, form):
        form.save()
        return redirect(reverse('admin:puzzle_word_changelist'))


class ImportWordSquareView(StaffView):

    title = 'Import Word Square'

    form_class = ImportWordSquareForm

    def form_valid(self, form):
        word_square = form.save()
        return redirect(reverse('admin:puzzle_wordsquare_change', args=[word_square.pk]))
