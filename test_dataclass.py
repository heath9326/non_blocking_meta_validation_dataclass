from dataclasses import dataclass, field
from unittest import TestCase

from rest_framework.exceptions import ValidationError

from non_blocking_meta_validation_dataclass import (
    AttrValidator,
    NonBlockingValidationDataclass,
    ValidationExceptionGroup
)


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


class TestFormatting(TestCase):
    @staticmethod
    def extract_verbose_errors_from_exception_groups(context):
        return tuple(exc.args[0] for exc in context.exception.exceptions)

    def test_dataclass_formatted_incorrectly__should_raise_exception_field_formatted_incorrectly(self):
        """
        All fields are formatter correctly:
           - have 'validator'
           - 'input_field' in metadata or key of the same name is present in input_data
        Otherwise raise  ExceptionGroup exception with all the exceptions for each field present.
        """
        @dataclass
        class DataclassForFormatterErrors(NonBlockingValidationDataclass):
            attr_01: str = field(default=None, metadata={'validator': BasicStringFieldValidator})                          # CORRECT: validator present, NO 'input_field' AND but key with the same name IS in input_data
            attr_02: dict = field(default=None, metadata={'validator': BasicDictFieldValidator, 'input_field': 'attr_01'}) # CORRECT: both attributes present, input field matches the attr name
            attr_03: int = field(default=None, metadata={'input_field': 'attr_06'})                                        # ERROR: no validator, custom input_field is present and present in input_data
            attr_04: dict = field(default=None, metadata={'validator': BasicDictFieldValidator})                           # CORRECT: validator present, input_field is missing in metadata, but key with the same name in input_data
            attr_05: int = field(default=None)                                                                             # ERROR: NO validator, NO 'input_field' AND key of this name is NOT in input_data
            attr_06: dict = field(default=None, metadata={'validator': BasicDictFieldValidator})                           # CORRECT: validator is present, key of this name IS in input_data

        EXPECTED_ERRORS = (
            'Field attr_03 has no validator attribute in field metadata',
            'Field attr_05 has no validator attribute in field metadata',
            'Field attr_05 has no input_field attribute in field metadata'
        )

        data = {
            'attr_01': 'example string',
            'attr_02': {'example_key': 'example_value'},
            'attr_04': {'example_key': 'example_value'},
            'attr_07': {'example_key': 'example_value'},
            'attr_06': 3,
        }

        with self.assertRaises(ValidationExceptionGroup) as context:
            DataclassForFormatterErrors.from_dict(data)

        self.assertEqual(EXPECTED_ERRORS, self.extract_verbose_errors_from_exception_groups(context))

    def test_dataclass_formatted_correctly__should_return_dataclass_instance(self):
        """
        All fields are formatter correctly:
           - have 'validator'
           - 'input_field' in metadata or key of the same name is present in input_data
        Otherwise raise  ExceptionGroup exception with all the exceptions for each field present.
        """
        @dataclass
        class DataclassForFormatterCorrect(NonBlockingValidationDataclass):
            attr_01: str = field(default=None, metadata={'validator': BasicStringFieldValidator})                          # CORRECT: validator present, NO 'input_field' AND but key with the same name IS in input_data
            attr_02: dict = field(default=None, metadata={'validator': BasicDictFieldValidator, 'input_field': 'attr_01'}) # CORRECT: both attributes present, input field matches the attr name
            attr_03: int = field(default=None, metadata={'validator': BasicIntFieldValidator, 'input_field': 'attr_06'})   # CORRECT: validator is present, custom input_field is present and present in input_data
            attr_04: dict = field(default=None, metadata={'validator': BasicDictFieldValidator})                           # CORRECT: validator present, input_field is missing in metadata, but key with the same name in input_data
            attr_05: int = field(default=None, metadata={'validator': BasicDictFieldValidator})                            # CORRECT: validator is present, input_field is missing in metadata, but key with the same name in input_data

        data = {
            'attr_01': 'example string',
            'attr_02': {'example_key': 'example_value'},
            'attr_04': {'example_key': 'example_value'},
            'attr_05': 123,
            'attr_07': {'example_key': 'example_value'},
        }

        result_dataclass = DataclassForFormatterCorrect.from_dict(data)
        self.assertIsInstance(result_dataclass, DataclassForFormatterCorrect)

    def test_dataclass_formatter_correctly_with_nested_dataclass_fields__should_return_dataclass_instance(self):
        """
        All fields are formatter correctly:
           - have 'validator'
           - 'input_field' in metadata or key of the same name is present in input_data
        Otherwise raise  ExceptionGroup exception with all the exceptions for each field present.
        :return: validated formatted dataclass with nested dataclass fields
        """
        @dataclass
        class DoubleNestedDataclass(NonBlockingValidationDataclass):
            attr_05: int = field(default=None, metadata={'validator': BasicDictFieldValidator})

        @dataclass
        class NestedDataclass(NonBlockingValidationDataclass):
            nested_field_01: str = field(default=None, metadata={'validator': BasicStringFieldValidator})
            nested_field_02: DoubleNestedDataclass = field(default=None, metadata={'validator': BasicStringFieldValidator})

        @dataclass
        class DataclassForFormatterCorrect(NonBlockingValidationDataclass):
            attr_01: str = field(default=None, metadata={'validator': BasicStringFieldValidator})                           # CORRECT: validator present, NO 'input_field' AND but key with the same name IS in input_data
            attr_02: dict = field(default=None, metadata={'validator': BasicDictFieldValidator, 'input_field': 'attr_01'})  # CORRECT: both attributes present, input field matches the attr name
            attr_03: NestedDataclass = NestedDataclass

        data = {
            'attr_01': 'example string',
            'attr_02': {'example_key': 'example_value'},
            'attr_04': {'example_key': 'example_value'},
            'attr_05': 123,
            'attr_07': {'example_key': 'example_value'},
        }

        EXPECTED_ERRORS = set()

        with self.assertRaises(ValidationExceptionGroup) as context:
            DataclassForFormatterCorrect.from_dict(data)

        self.assertEqual(EXPECTED_ERRORS, self.extract_verbose_errors_from_exception_groups(context))
