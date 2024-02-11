import json

from django.db import models


class Board:

    def __str__(self):
        return json.dumps(self.serialize())

    def serialize(self):
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, value):
        raise NotImplementedError()


class BoardDescriptor:

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # The instance dict contains whatever was originally assigned in
        # __set__.
        if self.field.name in instance.__dict__:
            value = instance.__dict__[self.field.name]
        else:
            instance.refresh_from_db(fields=[self.field.name])
            value = getattr(instance, self.field.name)
        return value

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = self.to_python(value)

    @staticmethod
    def to_python(value):
        if isinstance(value, Board):
            return value

        return Board.deserialize(value)


class BoardField(models.Field):

    description = 'Board'

    def __init__(self, board_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.board_class = board_class

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Perform preliminary non-db specific value checks and conversions.
        """
        return json.dumps(value.serialize()) if isinstance(value, Board) else value

    def from_db_value(self, value, expression, connection):
        return self.board_class.deserialize(json.loads(value))

    def to_python(self, value):
        if isinstance(value, Board):
            return value
        return self.board_class.deserialize(value)

    def contribute_to_class(self, cls, name, *args, **kwargs):
        super().contribute_to_class(cls, name, *args, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    def get_internal_type(self):
        return "TextField"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["board_class"] = self.board_class
        return name, path, args, kwargs
