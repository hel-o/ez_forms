EMPTY_VALUES = (None, '', [], (), {})


class ValidationError(Exception):

    def __init__(self, message=None, code=None):
        self.message = message
        self.code = code


class MinLengthValidator(object):
    message = 'Minimal length {}.'
    code = 'min_length'

    def __init__(self, min_length):
        self.min_length = min_length

    def __call__(self, value):
        if len(value) < self.min_length:
            raise ValidationError(self.message.format(self.min_length), code=self.code)


class MaxLengthValidator(object):
    message = 'Max length {}'
    code = 'max_length'

    def __init__(self, max_length):
        self.max_length = max_length

    def __call__(self, value):
        if len(value) > self.max_length:
            raise ValidationError(self.message.format(self.max_length), code=self.code)


class LengthValidator(object):
    message = 'Length must be {}'
    code = 'length'

    def __init__(self, length):
        self.length = length

    def __call__(self, value):
        if not len(value) == self.length:
            raise ValidationError(self.message.format(self.length), code=self.code)


class OnlyNumberValidator(object):
    message = 'Only have to be numbers'
    code = 'number'

    def __call__(self, value):
        if not value.isdigit():
            raise ValidationError(self.message, code=self.code)


class MinValueValidator(object):
    message = 'Must be greater than {}'
    code = 'min_value'

    def __init__(self, min_value):
        self.min_value = min_value

    def __call__(self, value):
        if value < self.min_value:
            raise ValidationError(self.message.format(self.min_value), code=self.code)


class MaxValueValidator(object):
    message = 'Must be less than {}'
    code = 'max_value'

    def __init__(self, max_value):
        self.max_value = max_value

    def __call__(self, value):
        if value > self.max_value:
            raise ValidationError(self.message.format(self.max_value), code=self.code)
