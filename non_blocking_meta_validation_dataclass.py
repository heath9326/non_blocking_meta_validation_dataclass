from abc import ABC, abstractmethod
from dataclasses import dataclass, fields, field
from typing import List, Any, Type

from rest_framework.exceptions import ValidationError


class ValidationExceptionGroup(ExceptionGroup):
    """Custom validation class for NonBlockingValidationDataclass class"""


class AttrValidator(ABC):

    def __init__(self, value, field_name: str):
        self.value = value
        self.field_name = field_name

    def __call__(self, type: Type, *args, **kwargs):
        if not isinstance(self.value, type):
            raise ValidationError(f"Field: {self.field_name} raised ValidationError. "
                                  f"Value: '{self.value}' is not of type: {type}")


@dataclass
class NonBlockingValidationDataclass:
    """
    Format of fields:
    attr1: int = field(default=None, metadata={'validator': Attr1Validator(int, nullable=True)})
    attr2: int = field(default=None, metadata={'validator': Attr2Validator(str, nullable=True)})
    attr3: int = field(default=None, metadata={'validator': Attr3Validator(int, nullable=True)})
    """

    def convert_value(self, value):
        if isinstance(value, NonBlockingValidationDataclass):
            # Recursively serialize nested dataclasses
            return value.as_dict()
        elif isinstance(value, list):
            # Handle lists
            return [self.convert_value(item) for item in value]
        else:
            return value

    def as_dict(self) -> dict:
        """Метод для экспорта датакласс в дикт влючая вложенные датаклассы и проперти."""
        obj_dict = {}

        class_keys = set(self.__class__.__dict__.keys())
        for prop in class_keys:
            if isinstance(getattr(self.__class__, prop), property):
                obj_dict[prop] = self.convert_value(getattr(self, prop))

        class_fields = set(fields(self))
        for field in class_fields:
            if field.init:
                obj_dict[field.name] = self.convert_value(getattr(self, field.name))

        return obj_dict

    # @staticmethod
    # def flat_dict_only_leaf_values(d):
    #     """
    #     Flatten the dict to only have leaf values:
    #     data = {                                              data = {
    #         'field_01': 'Example',                                'field_01': 'Example',
    #         'field_02': 10,                                       'field_02': 10,
    #         'field_03': {                                         'nested_field_01': 'Example',
    #             'nested_field_01': 'Example',       =>            'nested_field_02': 10,
    #             'nested_field_02': 10                             'field_04': [0, 1, 2]
    #         },                                                }
    #         'field_04': [0, 1, 2]
    #     }
    #     """
    #     def _flatten_dict(d):
    #         items = []
    #         for k, v in d.items():
    #             if isinstance(v, dict):
    #                 items.extend(_flatten_dict(v).items())
    #             else:
    #                 items.append((k, v))
    #         return dict(items)
    #
    #     return _flatten_dict(d)
    @classmethod
    def flatten_list_recursive(cls, list_to_flatten: List[Any]) -> List[Any]:
        """
        Recursively flatten list of lists
        [element1, [element2, element3, [element4]]  ->->->   [element1, element2, element3, element4]
        """
        flattened_list = []
        for item in list_to_flatten:
            if isinstance(item, list):
                flattened_list.extend(cls.flatten_list_recursive(item))
            else:
                flattened_list.append(item)
        return flattened_list

    @staticmethod
    def _get_field_type(dataclass_field: field) -> type:
        if hasattr(dataclass_field, "__origin__"):
            return dataclass_field.__origin__
        return dataclass_field.type

    @classmethod
    def _validate_field_formatting(cls, dataclass_field: field, dict_data: dict):
        field_formatting_errors = []
        field_type = cls._get_field_type(dataclass_field)

        if not issubclass(field_type, NonBlockingValidationDataclass):
            try:
                if not dataclass_field.metadata.get('validator'):
                    raise AttributeError(f"Field '{dataclass_field.name}' has no validator attribute in field metadata")
            except AttributeError as err:
                field_formatting_errors.append(err)

            try:
                if not dataclass_field.metadata.get('input_field') and dataclass_field.name not in dict_data:
                    raise AttributeError(f"Field '{dataclass_field.name}' has no input_field attribute in field metadata "
                                         f"and field '{dataclass_field.name}' not present in input data.")
            except AttributeError as err:
                field_formatting_errors.append(err)

        if isinstance(field_type, type) and issubclass(field_type, NonBlockingValidationDataclass):
            nested_field_formatting_errors = [
                cls._validate_field_formatting(nested_dataclass_field, dict_data) for nested_dataclass_field
                in fields(field_type)
            ]
            field_formatting_errors.extend(nested_field_formatting_errors)

        #TODO: Add validation though custom validator
        #TODO: Make custom Validator optional - use strict type validation in validator not included
        return field_formatting_errors

    @classmethod
    def from_dict(cls, dict_data: dict):
        """
        Validate input_data and get formatted dataclass with all nested dataclasses and properties via one function:

        Usage:
        validated_dataclass = Dataclass.from_dict(dict_data)
        """
        formatting_errors = cls.flatten_list_recursive(
            [cls._validate_field_formatting(dataclass_field, dict_data) for dataclass_field in fields(cls)]
        )

        if formatting_errors:
            raise ValidationExceptionGroup("Formating Errors", formatting_errors)

        validation_errors = []
        instance = cls()

        for field in fields(cls):
            field_name = field.name

            is_metadata_input_field_provided = field.metadata.get('input_field', False)
            if is_metadata_input_field_provided:
                value = dict_data.get(is_metadata_input_field_provided)
            else:
                value = dict_data.get(field_name)

            validator: AttrValidator = field.metadata.get('validator')
            if validator:
                try:
                    validator(value, field_name)()
                    setattr(instance, field_name, value)
                except ValidationError as e:
                    validation_errors.append(e)

        if validation_errors:
            raise ValidationExceptionGroup("Validation Errors", validation_errors)

        return instance

    @classmethod
    def to_dict(cls):
        # TODO: Add reverse serialization into a dict
        pass
