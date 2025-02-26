from abc import ABC
from typing import Type

from rest_framework.exceptions import ValidationError


class ValidationExceptionGroup(ExceptionGroup):
    """Custom validation class for NonBlockingValidationDataclass class"""


class AttrValidator(ABC):
    type: Type

    def __init__(self, value, field_name: str):
        self.value = value
        self.field_name = field_name

    def __call__(self, type: Type, *args, **kwargs):
        if not isinstance(self.value, type):
            raise ValidationError(f"Field: {self.field_name} raised ValidationError. "
                                  f"Value: '{self.value}' is not of type: {type}")


class BasicIntFieldValidator(AttrValidator):
    type = int

    def __call__(self, *args, **kwargs):
        super().__call__(self.type)


class BasicDictFieldValidator(AttrValidator):
    type = dict

    def __call__(self, *args, **kwargs):
        super().__call__(self.type)


class BasicStringFieldValidator(AttrValidator):
    type = str

    def __call__(self, *args, **kwargs):
        super().__call__(self.type)
