from decimal import Decimal, InvalidOperation

from . import validators
from .validators import ValidationError


__all__ = (
    'Field', 'TextField', 'IntegerField', 'FloatField', 'DecimalField',
    'ChoiceField'
)


class Field(object):
    empty_values = list(validators.EMPTY_VALUES)
    default_error_messages = {
        'required': 'Field required.',
    }

    def __init__(self, required=True, default_value=None, extra_validators=None, error_messages=None):
        self.required = required
        self.default_value = default_value
        self.validators = extra_validators or []

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))

        messages.update(error_messages or {})
        self.error_messages = messages

        self.data = None

    def validate(self, value):
        value = self.to_python(value)

        if self.required and value in self.empty_values:
            raise ValidationError(self.error_messages['required'], code='required')

        if value in self.empty_values:
            return self.default_value

        self._run_validators(value)

        return value

    def to_python(self, value):
        return value

    def _run_validators(self, value):
        if self.validators:
            errors = []
            for v in self.validators:
                try:
                    v(value)
                except ValidationError as e:
                    # custom message:
                    if self.error_messages.get(e.code):
                        errors.append(self.error_messages[e.code])
                    else:
                        errors.append(e.message)

            if errors:
                raise ValidationError('-'.join(errors))


class TextField(Field):

    def __init__(self, min_length=None, max_length=None, length=None, **kwargs):
        super().__init__(**kwargs)

        if min_length:
            self.validators.append(validators.MinLengthValidator(min_length=min_length))

        if max_length:
            self.validators.append(validators.MaxLengthValidator(max_length=max_length))

        if length:
            self.validators.append(validators.LengthValidator(length=length))

    def to_python(self, value):
        if value and value not in self.empty_values:
            value = str(value).strip()
        return value


class IntegerField(Field):
    default_error_messages = {
        'invalid': 'Invalid number.',
    }

    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)

        if min_value:
            self.validators.append(validators.MinValueValidator(min_value))

        if max_value:
            self.validators.append(validators.MaxValueValidator(max_value))

    def to_python(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValidationError(self.error_messages['invalid'], 'invalid')
        return value


class FloatField(IntegerField):

    def to_python(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValidationError(self.default_error_messages['invalid'], 'invalid')
        return value


class DecimalField(Field):
    default_error_messages = {
        'invalid': 'Invalid number.',
    }

    def __init__(self, decimals=2, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)

        self.decimals = decimals

        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))

        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))

    def to_python(self, value):
        """
        Need to check the rounding type:
        For reference:
        decimal.DefaultContext.rounding = decimal.ROUND_HALF_UP
        decimal.setcontext(decimal.DefaultContext)
        """
        if value in self.empty_values:
            return None

        decimal_places = f'{{0:.{self.decimals}f}}'
        decimal_places = decimal_places.format(0)
        try:
            value = Decimal(str(value)).quantize(Decimal(decimal_places))
        except (TypeError, InvalidOperation):
            raise ValidationError(self.error_messages['invalid'], 'invalid')
        return value


class ChoiceField(Field):
    default_error_messages = {
        'invalid': 'Invalid value'
    }

    def __init__(self, choices=None, **kwargs):
        super().__init__(**kwargs)
        self.choices = choices or ()

    def to_python(self, value):
        if value in self.empty_values:
            return ''
        return str(value)

    def validate(self, value):
        value = super().validate(value)

        if self.required and value not in self.choices:
            raise ValidationError(self.default_error_messages['invalid'], 'invalid')

        return value
