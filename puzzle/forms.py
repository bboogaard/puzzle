from django import forms

from puzzle.models import KnightMove, PieSlice, WordFinder, WordSquare
from puzzle.knight_move import fields as knight_move_fields
from puzzle.pie_slice.utils import validate_obfuscated_word
from puzzle.utils import csv_to_grid
from puzzle.word_finder import fields as word_finder_fields
from puzzle.word_square import fields as word_square_fields
from puzzle.word_square.utils import import_words


class GridFileField(forms.FileField):

    def __init__(self, min_grid_size=None, max_grid_size=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_grid_size = min_grid_size
        self.max_grid_size = max_grid_size

    def clean(self, data, initial=None):
        data = super().clean(data, initial)
        data = csv_to_grid(data.open('r').read().decode().splitlines())
        if len(set(len(row) for row in data)) != 1:
            raise forms.ValidationError("All rows must be of the same size")
        if self.min_grid_size:
            if len(data) < self.min_grid_size or any(len(row) < self.min_grid_size for row in data):
                raise forms.ValidationError(f"Puzzle must have a min size of {self.min_grid_size}x{self.min_grid_size}")
        if self.max_grid_size:
            if len(data) > self.max_grid_size or any(len(row) > self.max_grid_size for row in data):
                raise forms.ValidationError(f"Puzzle must have a max size of {self.max_grid_size}x{self.max_grid_size}")
        return data


class ImportKnightMoveForm(forms.ModelForm):

    slots = GridFileField(min_grid_size=3, max_grid_size=3)

    class Meta:
        fields = ('word',)
        model = KnightMove

    def clean(self):
        data = self.cleaned_data
        if data:
            slots = self.cleaned_data.get('slots')
            if slots:
                board = knight_move_fields.Board.deserialize(slots)
                if not board.is_valid(data.get('word', '').upper()):
                    raise forms.ValidationError("Puzzle is invalid")
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.import_puzzle(slots=self.cleaned_data.get('slots', []))
        return instance


class ImportPieSliceForm(forms.ModelForm):

    class Meta:
        fields = ('obfuscated_word', 'word',)
        model = PieSlice

    def clean_obfuscated_word(self):
        data = self.cleaned_data.get('obfuscated_word', '')
        return data.upper()

    def clean(self):
        data = self.cleaned_data
        if data:
            word = data.get('word', "")
            obfuscated_word = data.get('obfuscated_word', "")
            try:
                validate_obfuscated_word(word, obfuscated_word)
            except forms.ValidationError:
                raise forms.ValidationError("Puzzle is invalid")
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.import_puzzle()
        return instance


class ImportWordFinderForm(forms.Form):

    hints = forms.CharField(widget=forms.Textarea())

    slots = GridFileField(max_grid_size=11)

    solution = forms.CharField(max_length=11)

    def clean_hints(self):
        data = self.cleaned_data.get('hints', '')
        return '\n'.join(map(lambda h: h.strip().upper(), data.splitlines()))

    def clean_solution(self):
        data = self.cleaned_data.get('solution', '')
        return data.upper()

    def clean(self):
        data = self.cleaned_data
        if data:
            slots = data.get('slots', [])
            hints = data.get('hints', [])
            solution = data.get('solution', '')
            board = word_finder_fields.Board.deserialize(slots)
            if not board.is_valid(hints.splitlines(), solution):
                raise forms.ValidationError("Puzzle is invalid")
        return data

    def save(self):
        instance = WordFinder(
            hints=self.cleaned_data['hints'],
            words=self.cleaned_data['hints'],
            solution=self.cleaned_data['solution'],
            size=len(self.cleaned_data['slots'])
        )
        instance.import_puzzle(words=self.cleaned_data['slots'])
        return instance


class ImportWordsForm(forms.Form):

    import_file = forms.FileField()

    def save(self):
        words = self.cleaned_data['import_file'].open('r').read().decode().splitlines()
        import_words(words)


class ImportWordSquareForm(forms.Form):

    slots = GridFileField(min_grid_size=4, max_grid_size=10)

    def clean(self):
        data = self.cleaned_data
        if data:
            slots = self.cleaned_data.get('slots')
            if slots:
                board = word_square_fields.Board.deserialize(slots)
                if not board.is_valid():
                    raise forms.ValidationError("Puzzle is invalid")
        return data

    def save(self):
        instance = WordSquare(size=len(self.cleaned_data.get('slots', [])))
        instance.import_puzzle(words=self.cleaned_data.get('slots', []))
        return instance
