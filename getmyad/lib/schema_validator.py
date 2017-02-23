# -*- coding: UTF-8 -*-
from copy import deepcopy

import re


class ValidationError(Exception):
    def __init__(self, message="", current_position=None):
        self.message = message
        self.error_path = []
        self.current_position = current_position

    def __str__(self):
        return "%s (%s)" % (self.message, " in ".join(self.error_path))


class BadSchema(Exception):
    pass


class BaseValidator(object):
    class NO_DEFAULT:
        pass

    def __init__(self, default=NO_DEFAULT):
        self.default = default


class String(BaseValidator):
    def __init__(self, one_of=None, **kwargs):
        BaseValidator.__init__(self, **kwargs)
        self.one_of = one_of

    def validate(self, obj):
        if not isinstance(obj, basestring):
            raise ValidationError("%s is not String" % repr(obj))
        if self.one_of and obj not in self.one_of:
            raise ValidationError("%s is not String one of %s" %
                                  (repr(obj), repr(self.one_of)))


class Regex(BaseValidator):
    def __init__(self, regex, **kv):
        BaseValidator.__init__(self, **kv)
        self.regex = regex

    def validate(self, obj):
        String().validate(obj)
        if not re.match(self.regex, obj):
            raise ValidationError("%s doesn't matches Regex" % repr(obj))


class Integer(BaseValidator):
    def __init__(self, allow_convert=False, **kwargs):
        BaseValidator.__init__(self, **kwargs)
        self.allow_convert = allow_convert

    def validate(self, obj):
        if isinstance(obj, int):
            return obj
        if isinstance(obj, basestring) and self.allow_convert:
            try:
                return int(obj)
            except ValueError:
                pass
        raise ValidationError("%s is not Integer" % repr(obj))


class Float(BaseValidator):
    def __init__(self, allow_convert=False, **kwargs):
        BaseValidator.__init__(self, **kwargs)
        self.allow_convert = allow_convert

    def validate(self, obj):
        if isinstance(obj, float):
            return obj
        if isinstance(obj, basestring) and self.allow_convert:
            try:
                return float(obj)
            except ValueError:
                pass
        raise ValidationError("%s is not Float" % repr(obj))


class Boolean(BaseValidator):
    def validate(self, obj):
        if not isinstance(obj, bool):
            raise ValidationError("%s is not Boolean" % repr(obj))


class Nevermind(BaseValidator):
    def validate(self, obj):
        pass


class List(BaseValidator):
    def __init__(self, item=Nevermind, **kv):
        BaseValidator.__init__(self, **kv)
        self.item = item

    def validate(self, obj):
        if not isinstance(obj, list):
            raise ValidationError('%s is not List' % repr(obj))

        result = []
        for i, item in enumerate(obj):
            try:
                result.append(validate(item, self.item))
            except ValidationError as ex:
                ex.current_position = "List[%d]" % i
                raise ex
        return result


class Dictionary(BaseValidator):
    def __init__(self, schema=Nevermind, **kv):
        BaseValidator.__init__(self, **kv)
        self.schema = deepcopy(schema)

    def __setitem__(self, k, v):
        self.schema[k] = v

    def __getitem__(self, k):
        return self.schema[k]

    def copy(self):
        return deepcopy(self)

    def validate(self, obj):
        if not isinstance(obj, dict):
            raise ValidationError('%s is not Dictionary' % repr(obj))

        if self.schema == Nevermind:
            return obj

        result = {}
        for key, schema in self.schema.iteritems():
            try:
                result[key] = validate(obj[key], schema)
            except ValidationError as ex:
                ex.current_position = "Dictionary[%s]" % repr(key)
                raise ex
            except KeyError:
                if isinstance(schema, BaseValidator) and \
                                schema.default != BaseValidator.NO_DEFAULT:
                    result[key] = schema.default
                else:
                    raise ValidationError("Dictionary has no key %s" %
                                          repr(key))
        return result


class Function(BaseValidator):
    def validate(self, obj):
        if not hasattr(obj, '__call__'):
            raise ValidationError('%s is not Function' % repr(obj))


def validate(obj, schema):
    if schema.__class__ == type:
        schema = schema()

    if isinstance(schema, dict):
        schema = Dictionary(schema)

    if not isinstance(schema, BaseValidator):
        raise BadSchema()

    try:
        validated_result = schema.validate(obj)
        # Если вернули None и не бросили ValidationError, значит нужно
        # использовать obj. Если вернули не None, значит нужно использовать
        # это значение (например, это может быть значение по умолчанию)
        return validated_result or obj
    except ValidationError as ex:
        if schema.default != BaseValidator.NO_DEFAULT:
            return schema.default
        else:
            where = ex.current_position or schema.__class__.__name__
            ex.error_path.append(where)
            raise ex
