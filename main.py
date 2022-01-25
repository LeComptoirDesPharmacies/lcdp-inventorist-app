# This Python file uses the following encoding: utf-8
import os
import sys
import logging

from python_openapi_generator_cli.codegen import generate_consumer
from business.constant import APPLICATION_NAME, ORGANIZATION_DOMAIN, ORGANIZATION_NAME

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


# Get current script dir
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def on_exit():
    try:
        delete_api_key()
    except Exception:
        logging.exception("Unabled to delete api key")


def run_codegen():
    generate_consumer("auth.yaml", CURRENT_DIR)
    generate_consumer("user.yaml", CURRENT_DIR)
    generate_consumer("laboratory.yaml", CURRENT_DIR)
    generate_consumer("product.yaml", CURRENT_DIR)
    generate_consumer("sale-offer.yaml", CURRENT_DIR)
    generate_consumer("configuration.yaml", CURRENT_DIR)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting app")
    logging.info("Start generate api")
    # TODO : A executer avant de package l'app pas au startup
    run_codegen()
    from backend.app import App
    from business.services.authentication import delete_api_key
    from backend.login import Login
    logging.info("Finish generate api")

    QGuiApplication.setOrganizationName(ORGANIZATION_NAME)
    QGuiApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
    QGuiApplication.setApplicationName(APPLICATION_NAME)

    logging.info("Start app")
    app = QGuiApplication(sys.argv)
    app.aboutToQuit.connect(on_exit)
    engine = QQmlApplicationEngine()

    login_backend = Login()
    app_backend = App()
    engine.rootContext().setContextProperty("loginBackend", login_backend)
    engine.rootContext().setContextProperty("appBackend", app_backend)
    engine.load(os.path.join(os.path.dirname(__file__), "qml/login.qml"))

    if not engine.rootObjects():
         sys.exit(-1)
    sys.exit(app.exec())
