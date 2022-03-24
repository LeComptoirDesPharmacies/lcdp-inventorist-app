from settings import get_settings


def set_setting(key, value):
    settings = get_settings()
    settings.setValue(key, value)


def get_setting(key):
    settings = get_settings()
    return settings.value(key)


def remove_setting(key):
    settings = get_settings()
    settings.remove(key)
