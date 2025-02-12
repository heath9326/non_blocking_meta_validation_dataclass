from dataclasses import dataclass, field
from unittest import TestCase

from rest_framework.exceptions import ValidationError

from non_blocking_meta_validation_dataclass import AttrValidator, NonBlockingValidationDataclass, \
    ValidationExceptionGroup


class BasicIntFieldValidator(AttrValidator):

    def __call__(self, *args, **kwargs):
        pass


class BasicDictFieldValidator(AttrValidator):

    def __call__(self, *args, **kwargs):
        pass


class BasicStringFieldValidator(AttrValidator):

    def __call__(self, *args, **kwargs):
        pass


@dataclass
class NestedDataclass02(NonBlockingValidationDataclass):
    inner_nested_attr_01: int = field(default=None, metadata={'validator': BasicIntFieldValidator, 'input_field': 'inner_nested_attr_01'})
    inner_nested_attr_02: dict = field(default=None, metadata={'validator': BasicDictFieldValidator, 'input_field': 'inner_nested_attr_02'})
    inner_nested_attr_03: int = field(default=None, metadata={'validator': BasicStringFieldValidator, 'input_field': 'inner_nested_attr_03'})


@dataclass
class NestedDataclass01(NonBlockingValidationDataclass):
    nested_attr_01: NestedDataclass02
    nested_attr_02: int = field(default=None, metadata={'validator': BasicIntFieldValidator, 'input_field': 'nested_attr_02'})


@dataclass
class Dataclass01(NonBlockingValidationDataclass):
    attr_01: NestedDataclass01
    attr_02: int = field(default=None, metadata={'validator': BasicIntFieldValidator, 'input_field': 'attr_02'})
    attr_03: dict = field(default=None, metadata={'validator': BasicDictFieldValidator, 'input_field': 'attr_03'})
    attr_04: str = field(default=None, metadata={'validator': BasicStringFieldValidator, 'input_field': 'attr_04'})


class TestDataclassImproved(TestCase):

    def test_dataclass_formatted_incorrectly__should_raise_exception_field_formatted_incorrectly(self):
        '''
        All fields are formatter correctly (have 'validator' and 'input_field' in metadata),
        otherwise raise  ExceptionGroup exception
        '''

        EXPECTED_ERRORS = (
            AttributeError('Field attr_02 has no validator attribute in field metadata'),
            AttributeError('Field attr_03 has no input_field attribute in field metadata'),
            AttributeError('Field attr_04 has no validator attribute in field metadata'),
            AttributeError('Field attr_04 has no input_field attribute in field metadata')
        )

        data = {
            'attr_02': 3,
            'attr_01': {'example_key': 'example_value'},
            'attr_03': {'example_key': 'example_value'},
            'attr_04': 0
        }

        @dataclass
        class DataclassForFormatterErrors(NonBlockingValidationDataclass):
            attr_01: dict = field(default=None, metadata={'validator': BasicDictFieldValidator, 'input_field': 'attr_01'})
            attr_02: int = field(default=None, metadata={'input_field': 'attr_02'})
            attr_03: dict = field(default=None, metadata={'validator': BasicDictFieldValidator})
            attr_04: int = field(default=None)


        with self.assertRaises(ValidationExceptionGroup) as context:
            DataclassForFormatterErrors.from_dict(data)
        self.assertEqual(EXPECTED_ERRORS, context.exception.exceptions)
