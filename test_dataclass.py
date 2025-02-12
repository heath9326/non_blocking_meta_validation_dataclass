from dataclasses import dataclass, field
from unittest import TestCase

from rest_framework.exceptions import ValidationError

from non_blocking_meta_validation_dataclass import AttrValidator, NonBlockingValidationDataclass


class BasicIntFieldValidator(AttrValidator):

    def __call__(self, *args, **kwargs):
        pass


class Attr2Validator(AttrValidator):

    def __call__(self, *args, **kwargs):
        pass


class Attr3Validator(AttrValidator):

    def __call__(self, *args, **kwargs):
        pass


@dataclass
class NestedDataclass02(NonBlockingValidationDataclass):
    inner_nested_attr_01: int = field(default=None, metadata={'validator': BasicIntFieldValidator, 'input_field': 'inner_nested_attr_01'})
    inner_nested_attr_02: int = field(default=None, metadata={'validator': Attr2Validator, 'input_field': 'inner_nested_attr_02'})
    inner_nested_attr_03: int = field(default=None, metadata={'validator': Attr3Validator, 'input_field': 'inner_nested_attr_03'})


@dataclass
class NestedDataclass01(NonBlockingValidationDataclass):
    nested_attr_01: NestedDataclass02
    nested_attr_02: int = field(default=None, metadata={'validator': BasicIntFieldValidator, 'input_field': 'nested_attr_02'})


@dataclass
class Dataclass01(NonBlockingValidationDataclass):
    attr_01: NestedDataclass01
    attr_02: int = field(default=None, metadata={'validator': BasicIntFieldValidator, 'input_field': 'attr_02'})
    attr_03: dict = field(default=None, metadata={'validator': Attr2Validator, 'input_field': 'attr_03'})
    attr_04: str = field(default=None, metadata={'validator': Attr3Validator, 'input_field': 'attr_04'})


class TestDataclassImproved(TestCase):

    def test_dataclass_formatted_incorrectly__should_raise_exception_field_formatted_incorrectly(self):
        @dataclass
        class DataclassForFormatterErrors(NonBlockingValidationDataclass):
            attr_02: int = field(default=None, metadata={'validator': BasicIntFieldValidator, 'input_field': 'attr_02'})
            attr_03: dict = field(default=None, metadata={'validator': Attr2Validator, 'input_field': 'attr_03'})
            attr_04: int = field(default=None, metadata={'validator': Attr3Validator, 'input_field': 'attr_04'})

        with self.assertRaises(ValidationError) as context:
            validated_dataclass = Datalass_02.from_dict(data)
            self.assertIsInstance(validated_dataclass, Datalass_02)
