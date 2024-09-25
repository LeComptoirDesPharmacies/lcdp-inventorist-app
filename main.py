# This Python file uses the following encoding: utf-8
import logging
import os
import sys
from pathlib import Path

import requests
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from backend.app import App
from backend.login import Login
from business.constant import APPLICATION_NAME, ORGANIZATION_DOMAIN, ORGANIZATION_NAME, GITHUB_REPOSITORY_LATEST_RELEASE
from business.services.authentication import delete_api_key
from settings import get_settings

CURRENT_DIRECTORY = Path(__file__).resolve().parent
import faulthandler
faulthandler.enable()

def on_exit():
    try:
        delete_api_key()
    except Exception:
        logging.exception("Unabled to delete api key")


def configure_sentry(settings):
    sentry_dsn = settings.value("SENTRY_DSN")
    lcdp_environment = settings.value("LCDP_ENVIRONMENT")
    version = settings.value("VERSION")
    # sentry_sdk.init(
    #     dsn=sentry_dsn,
    #     environment=lcdp_environment,
    #     release=version,
    # )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    logging.info("Starting app")

    settings = get_settings()
    configure_sentry(settings)

    logging.info("Configure app")
    QGuiApplication.setOrganizationName(ORGANIZATION_NAME)
    QGuiApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
    QGuiApplication.setApplicationName(APPLICATION_NAME)
    QGuiApplication.setApplicationVersion(settings.value("VERSION"))

    logging.info("Start app engine")
    app = QGuiApplication(sys.argv)
    app.aboutToQuit.connect(on_exit)
    app.setWindowIcon(QIcon(os.path.join(CURRENT_DIRECTORY, "images", "icon.ico")))
    engine = QQmlApplicationEngine()

    engine.rootContext().setContextProperty("newVersionAvailable", "")
    engine.rootContext().setContextProperty("newVersionUrl", "")

    type_env = os.environ.get("LCDP_ENVIRONMENT")
    if type_env == "dev":
        print("Dev mode. No check for new version. Change LCDP_ENVIRONMENT to other value as 'dev' to enable check for new version")
    else:
        try:
            latestRelease = requests.get(GITHUB_REPOSITORY_LATEST_RELEASE).json()
            latestAppTag = latestRelease.get("name")
            if latestAppTag != settings.value("VERSION"):
                logging.info("New version available")
                engine.rootContext().setContextProperty("newVersionAvailable", "Nouvelle version disponible : " + latestAppTag)
                engine.rootContext().setContextProperty("newVersionUrl", latestRelease.get("html_url"))
        except Exception as e:
            logging.info("Error while getting latest tag from github")

    login_backend = Login()
    app_backend = App()
    engine.rootContext().setContextProperty("version", settings.value("VERSION"))
    engine.rootContext().setContextProperty("loginBackend", login_backend)
    engine.rootContext().setContextProperty("appBackend", app_backend)


    filename = os.fspath(CURRENT_DIRECTORY / "qml" / "login.qml")
    url = QUrl.fromLocalFile(filename)
    engine.load(url)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
