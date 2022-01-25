from PySide6.QtCore import QSettings

settings = QSettings()


def set_setting(key, value):
    settings.setValue(key, value)


def get_setting(key):
    return settings.value(key)


def remove_setting(key):
    settings.remove(key)
