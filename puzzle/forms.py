from django import forms
from django.core.exceptions import ImproperlyConfigured

from puzzle.common.utils import chunks, import_words
from puzzle.models import KnightMove, PieSlice, WordFinder, WordLadder, WordSquare
from puzzle.knight_move import fields as knight_move_fields
from puzzle.pie_slice.utils import validate_obfuscated_word
from puzzle.word_finder import fields as word_finder_fields
from puzzle.word_ladder import fields as word_ladder_fields
from puzzle.word_square import fields as word_square_fields


class GridWidget(forms.Widget):

    template_name = 'forms/widgets/grid.html'

    class Media:
        css = {
            "all": ["forms/widgets/grid-widget.css"],
        }
        js = ["forms/widgets/grid-widget.js"]

    def __init__(self, min_size=None, max_size=None, min_width=None, max_width=None,
                 min_height=None, max_height=None, is_square=False, attrs=None):
        super().__init__(attrs)
        self.min_size = min_size
        self.max_size = max_size
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height
        self.is_square = is_square

    @property
    def min_dim(self):
        return (self.min_size, self.min_size) if self.is_square else (self.min_width, self.min_height)

    def format_value(self, value):
        if value == "" or value is None:
            return [
                self.min_dim[0] * ['']
                for _ in range(self.min_dim[1])
            ]

        return value

    def get_dim_field(self, name):
        return name + '-size' if self.is_square else name + '-width'

    def value_from_datadict(self, data, files, name):
        dim = int(data.get(self.get_dim_field(name), self.min_dim[0]))
        return chunks(data.getlist(name), dim)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'min_size': self.min_size,
            'max_size': self.max_size,
            'min_width': self.min_width,
            'max_width': self.max_width,
            'min_height': self.min_height,
            'max_height': self.max_height,
            'is_square': self.is_square
        })
        if self.is_square:
            context['widget']['size'] = len(value[0]) if value else self.min_size
        else:
            context['widget']['width'] = len(value[0]) if value else self.min_width
        return context


class GridField(forms.Field):

    def __init__(self, min_size=None, max_size=None, min_width=None, max_width=None,
                 min_height=None, max_height=None, *args, **kwargs):
        if any([min_size, max_size]):
            if not all([min_size, max_size]):
                raise ImproperlyConfigured(
                    "Either pass all of 'min_size, max_size' or all of 'min_width, max_width, min_height, max_height'")
            if any([min_width, max_width, min_height, max_height]):
                raise ImproperlyConfigured(
                    "Either pass all of 'min_size, max_size' or all of 'min_width, max_width, min_height, max_height'")
            min_width = min_size
            max_width = max_size
            min_height = min_size
            max_height = max_size
            is_square = True
        elif not all([min_width, max_width, min_height, max_height]):
            raise ImproperlyConfigured(
                "Either pass all of 'min_size, max_size' or all of 'min_width, max_width, min_height, max_height'")
        else:
            is_square = False
        super().__init__(
            widget=GridWidget(
                min_size=min_size,
                max_size=max_size,
                min_width=min_width,
                max_width=max_width,
                min_height=min_height,
                max_height=max_height,
                is_square=is_square
            ),
            *args, **kwargs
        )
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

    def validate(self, value):
        super().validate(value)
        if self.required and any(val == '' for row in value for val in row):
            raise forms.ValidationError(self.error_messages["required"], code="required")

    def to_python(self, value):
        if not self.required and value in self.empty_values:
            return value

        return list(map(lambda r: [c.upper() for c in r], value))


class ImportKnightMoveForm(forms.ModelForm):

    slots = GridField(min_size=3, max_size=3)

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

    slots = GridField(min_size=4, max_size=11)

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

    slots = GridField(min_size=4, max_size=10)

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


class ImportWordLadderForm(forms.Form):

    slots = GridField(min_width=4, max_width=6, min_height=1, max_height=10)

    def clean(self):
        data = self.cleaned_data
        if data:
            slots = self.cleaned_data.get('slots')
            if slots:
                board = word_ladder_fields.Board.deserialize(slots)
                if not board.is_valid():
                    raise forms.ValidationError("Puzzle is invalid")
                data['width'] = board.size
        return data

    def save(self):
        instance = WordLadder(width=self.cleaned_data.get('width'))
        instance.import_puzzle(words=self.cleaned_data.get('slots', []))
        return instance
