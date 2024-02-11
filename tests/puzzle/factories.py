import factory

from puzzle import models
from puzzle.word_square.utils import tokenize_word


class WordFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Word

    @factory.post_generation
    def tokens(self, create, extracted, *args, **kwargs):
        if not create:
            return

        if extracted:
            return

        tokens = tokenize_word(self.word)
        for index, token in tokens.items():
            WordTokenFactory(word=self, index=index, token=token)


class WordTokenFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.WordToken
