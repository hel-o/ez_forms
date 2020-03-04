from typing import Optional, Dict, Tuple
from collections import OrderedDict

from .fields import Field
from .validators import ValidationError


__all__ = (
    'BaseForm',
    'check_form_for_result'
)


class EzMetaClass(type):

    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                current_fields.append((key, value))

        attrs['declared_fields'] = OrderedDict(current_fields)

        new_class = super().__new__(mcs, name, bases, attrs)

        declared_fields = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class


class BaseForm(object, metaclass=EzMetaClass):

    def __init__(self, data=None, **kwargs):
        self.data = data or {}
        self.kwargs = kwargs
        self.cleaned_data = {}
        self._errors = None

    def errors(self):
        if self._errors is None:
            self._validate()
            self.validate_business()
        return self._errors

    def is_ok(self):
        return not self.errors()

    def validate_business(self):
        # Hook - Optional custom validation:
        pass

    def save(self) -> Optional[Dict]:
        return None

    def update(self) -> Optional[Dict]:
        return None

    def _validate(self):
        self._errors = {}
        for name, field in self.base_fields.items():
            value = self.data.get(name)

            try:
                value = field.validate(value)
            except ValidationError as e:
                self.add_error(name, e)
            else:
                field.data = value
                self.cleaned_data[name] = value

    def add_error(self, field, error):
        if isinstance(error, ValidationError):
            self._errors[field] = error.message
        else:
            self._errors[field] = error


def check_form_for_result(form: BaseForm, http_status=201) -> Tuple[Dict, int]:
    if form.is_ok():
        if http_status == 201:
            result = form.save()
        else:
            result = form.update()

        if result is None:
            http_status = 500
    else:
        result = form.errors()
        http_status = 400

    return result, http_status
