# This Python file uses the following encoding: utf-8
import logging
import os
import sys
from pathlib import Path

import psutil
import requests
import sentry_sdk
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMessageBox

from backend.app import App
from backend.login import Login
from business.constant import APPLICATION_NAME, ORGANIZATION_DOMAIN, ORGANIZATION_NAME, GITHUB_REPOSITORY_LATEST_RELEASE
from business.services.authentication import delete_api_key
from settings import get_settings

CURRENT_DIRECTORY = Path(__file__).resolve().parent
import faulthandler

with open('fault_log.txt', 'a') as f:
    faulthandler.enable(file=f)


def on_exit():
    try:
        delete_api_key()
    except Exception:
        logging.exception("Unabled to delete api key")


def configure_sentry(settings):
    sentry_dsn = settings.value("SENTRY_DSN")
    lcdp_environment = settings.value("LCDP_ENVIRONMENT")
    version = settings.value("VERSION")
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=lcdp_environment,
        release=version,
    )


def check_single_instance():
    current_pid = os.getpid()
    current_process = psutil.Process(current_pid)
    current_process_name = current_process.name()

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            print(f'Process name: {proc.info["name"]}, PID: {proc.info["pid"]}')
            if proc.info['name'] == current_process_name and proc.info['pid'] != current_pid:
                print(
                    f"Une autre instance de l'application est déjà en cours d'exécution avec le PID {proc.info['pid']}.")
                return False
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return True


def show_alert(message):
    QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setText(message)
    msg_box.setWindowTitle("Alerte")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    settings = get_settings()
    lcdp_environment = settings.value("LCDP_ENVIRONMENT")

    if lcdp_environment == "dev":
        print(
            "Dev mode. No check for concurrent run. Change LCDP_ENVIRONMENT to other value as 'dev' to enable check for new version")
    else:
        if not check_single_instance():
            show_alert("Une autre instance de l'application est déjà en cours d'exécution.")
            sys.exit(1)

    logging.info("Starting app")

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

    if lcdp_environment == "dev":
        print(
            "Dev mode. No check for new version. Change LCDP_ENVIRONMENT to other value as 'dev' to enable check for new version")
    else:
        try:
            latestRelease = requests.get(GITHUB_REPOSITORY_LATEST_RELEASE).json()
            latestAppTag = latestRelease.get("name")
            if latestAppTag != settings.value("VERSION"):
                logging.info("New version available")
                engine.rootContext().setContextProperty("newVersionAvailable",
                                                        "Nouvelle version disponible : " + latestAppTag)
                engine.rootContext().setContextProperty("newVersionUrl", latestRelease.get("html_url"))
        except Exception as e:
            logging.info("Error while getting latest tag from github")

    login_backend = Login()
    app_backend = App()
    app.aboutToQuit.connect(app_backend.on_exit)
    engine.rootContext().setContextProperty("version", settings.value("VERSION"))
    engine.rootContext().setContextProperty("loginBackend", login_backend)
    engine.rootContext().setContextProperty("appBackend", app_backend)

    filename = os.fspath(CURRENT_DIRECTORY / "qml" / "login.qml")
    url = QUrl.fromLocalFile(filename)
    engine.load(url)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
