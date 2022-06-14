# This Python file uses the following encoding: utf-8
import json
import os
import sys
import logging
from pathlib import Path

import sentry_sdk
from PySide6.QtCore import QUrl

from business.constant import APPLICATION_NAME, ORGANIZATION_DOMAIN, ORGANIZATION_NAME

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from settings import get_settings

from backend.app import App
from business.services.authentication import delete_api_key
from backend.login import Login

CURRENT_DIRECTORY = Path(__file__).resolve().parent


def on_exit():
    try:
        delete_api_key()
    except Exception:
        logging.exception("Unabled to delete api key")


def configure_sentry():
    settings = get_settings()
    sentry_dsn = settings.value("SENTRY_DSN")
    lcdp_environment = settings.value("LCDP_ENVIRONMENT")
    version = settings.value("VERSION")
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=lcdp_environment,
        release=version,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    logging.info("Starting app")

    logging.info("Configure app")
    QGuiApplication.setOrganizationName(ORGANIZATION_NAME)
    QGuiApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
    QGuiApplication.setApplicationName(APPLICATION_NAME)

    configure_sentry()

    logging.info("Start app engine")
    app = QGuiApplication(sys.argv)
    app.aboutToQuit.connect(on_exit)
    app.setWindowIcon(QIcon(os.path.join(CURRENT_DIRECTORY, "images", "icon.ico")))
    engine = QQmlApplicationEngine()

    login_backend = Login()
    app_backend = App()
    engine.rootContext().setContextProperty("loginBackend", login_backend)
    engine.rootContext().setContextProperty("appBackend", app_backend)
    filename = os.fspath(CURRENT_DIRECTORY / "qml" / "login.qml")
    url = QUrl.fromLocalFile(filename)
    engine.load(url)

    if not engine.rootObjects():
         sys.exit(-1)
    sys.exit(app.exec())
