from abc import ABC, abstractmethod
from dataclasses import dataclass, fields


class ValidationExceptionGroup(ExceptionGroup):
    """Custom validation class for NonBlockingValidationDataclass class"""


class AttrValidator(ABC):

    def __init__(self, value):
        self.value = value

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


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
            # Рекурсивно сериализируем вложенные датаклассы
            return value.as_dict()
        elif isinstance(value, list):
            # Обрабатываем списки
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

    @classmethod
    def from_dict(cls, dict_data):
        """
        Метод для валидации входящей даты через датакласс

        validated_dataclass = Dataclass.from_dict(dict_data)

        Возвращает провалидированный инстанс датакласса со всеми вложенными датаклассами.
        """
        # TODO: CHECK EACH FIELD IS FORMATTED CORRECTLY: metadata, validator, input_field
        formatting_errors = []
        for field in fields(cls):
            try:
                field.metadata.get('validator')
                field.metadata.get('input_field')
            except AttributeError as err:
                formatting_errors.append(err)
        if formatting_errors:
            raise ValidationExceptionGroup("Formating Errors", formatting_errors)

        validation_errors = []
        instance = cls()

        for field in fields(cls):
            field_name = field.name
            value = dict_data.get(field_name)
            validator: AttrValidator = field.metadata.get('validator')

            if validator:
                try:
                    setattr(instance, field_name, value)
                except ValueError as e:
                    validation_errors.append(e)

        if validation_errors:
            raise ValidationExceptionGroup("Validation Errors", validation_errors)

        return instance
