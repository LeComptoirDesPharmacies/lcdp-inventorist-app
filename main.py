# This Python file uses the following encoding: utf-8
import os
import sys
import logging
from pathlib import Path

import sentry_sdk
from PySide6.QtCore import QUrl

from business.constant import APPLICATION_NAME, ORGANIZATION_DOMAIN, ORGANIZATION_NAME

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from dotenv import load_dotenv

CURRENT_DIRECTORY = Path(__file__).resolve().parent

load_dotenv(override=False)

# Sentry configuration
sentry_dsn = os.getenv("SENTRY_DSN")
lcdp_environment = os.getenv("LCDP_ENVIRONMENT")
sentry_sdk.init(
    dsn=sentry_dsn,
    environment=lcdp_environment,
)


def on_exit():
    try:
        delete_api_key()
    except Exception:
        logging.exception("Unabled to delete api key")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting app")
    logging.info("Start generate api")
    from backend.app import App
    from business.services.authentication import delete_api_key
    from backend.login import Login
    logging.info("Finish generate api")

    QGuiApplication.setOrganizationName(ORGANIZATION_NAME)
    QGuiApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
    QGuiApplication.setApplicationName(APPLICATION_NAME)

    logging.info("Start app")
    app = QGuiApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "images", "logo.png")))
    app.aboutToQuit.connect(on_exit)
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
