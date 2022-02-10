import functools


def cast_or_default(value, data_type, default=None):
    if not value:
        return default
    try:
        return data_type(value)
    except Exception:
        return default


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


def clean_none_from_dict(original):
    return {k: v for k, v in original.items() if v is not None}


class ConditionalDict(dict):
    def __init__(self, condition_func=None, merge_func=None, before_insert_func=None):
        super().__init__()
        self.condition_func = condition_func
        self.merge_func = merge_func
        self.before_insert_func = before_insert_func

    def __setitem__(self, key, value):
        if self.condition_func and self.condition_func(key, value):
            value = self.__merge(key, value)
            self.__insert(key, value)
        elif not self.condition_func:
            value = self.__merge(key, value)
            self.__insert(key, value)

    def __insert(self, key, value):
        if self.before_insert_func:
            value = self.before_insert_func(key, value)
        dict.__setitem__(self, key, value)

    def __merge(self, key, value):
        if key in self and self.merge_func:
            value = self.merge_func(key, self[key], value)
        return value
