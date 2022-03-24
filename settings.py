import json
import logging
import os
import sys

from PySide6.QtCore import QSettings

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def setup_settings():
    try:
        config_file = open(os.path.join(CURRENT_DIR, 'config.json'), "r")
        config_json = json.loads(config_file.read())
        new_settings = QSettings(QSettings.NativeFormat, QSettings.UserScope, None)
        new_settings.setValue("SENTRY_DSN", config_json['SENTRY_DSN'])
        new_settings.setValue("LCDP_ENVIRONMENT", config_json['LCDP_ENVIRONMENT'])
        new_settings.setValue("PROVIDER_HOST", config_json['PROVIDER_HOST'])
        new_settings.setValue("IS_PROVIDER_SECURE", config_json['IS_PROVIDER_SECURE'])
        return new_settings
    except OSError as osErr:
        logging.exception("Cannot read config.json file, please execute prepare.py", osErr)
        sys.exit(-1)


_settings = None


def get_settings():
    global _settings
    if not _settings:
        _settings = setup_settings()
        return _settings
    else:
        return _settings
