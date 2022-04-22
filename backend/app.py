import logging
import os
import subprocess
import sys
from typing import Optional
from urllib.parse import urlparse
from sentry_sdk import capture_exception

from PySide6.QtCore import QObject, Slot, Signal, QThreadPool, QRunnable, Property, QUrl

from business.actions import detailed_actions, simple_actions
from business.services.excel import create_excel_summary


class Worker(QRunnable):
    def __init__(self, action, excel_path, loading_signal, state_signal, result_signal, reset, should_clean):
        super().__init__()
        self.action = action
        self.excel_path = excel_path
        self.loading_signal = loading_signal
        self.state_signal = state_signal
        self.result_signal = result_signal
        self.reset = reset
        self.should_clean = should_clean

    def run(self):
        try:
            self.loading_signal.emit(True)
            self.state_signal.emit("Récupération du fichier excel...", "INFO")
            self.execute(self.excel_path)
        except Exception as err:
            self.state_signal.emit("Une erreur s'est produite, veuillez contacter l'administrateur", "ERROR")
            logging.exception('Cannot read excel with url {}'.format(self.excel_path), err)
            capture_exception(err)
        finally:
            self.loading_signal.emit(False)

    def execute(self, excel_path):
        self.state_signal.emit("Récupération des ressources dans le fichier...", "INFO")
        mapper_class = self.action['mapper']
        mapper = mapper_class(excel_path)
        lines = mapper.map_to_obj()

        self.state_signal.emit("Création/Modification des ressources...", "INFO")
        executor = self.action['executor']
        results = executor(lines)

        if self.should_clean and self.action['cleaner']:
            self.state_signal.emit("Nettoyage en cours...", "INFO")
            cleaner = self.action['cleaner']
            cleaner(results)

        self.state_signal.emit("Création du rapport...", "INFO")
        report_path = create_excel_summary(results, mapper.excel_mapper)
        self.result_signal.emit(report_path)
        self.state_signal.emit("Le fichier a bien été traité", "SUCCESS")
        self.reset()


class App(QObject):
    signalLoading = Signal(bool)
    signalCanClean = Signal(bool)
    signalState = Signal(str, str)
    signalReportPath = Signal(str)
    signalTemplateUrl = Signal(str)
    signalActions = Signal(list)
    signalReset = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.thread_pool = QThreadPool()
        self._actions = simple_actions
        self.selected_action = None
        self.signalActions.emit(simple_actions)
        self.excel_path = None
        self._should_clean = False

    @Slot(str)
    def select_action(self, action_type):
        if action_type in detailed_actions:
            self.selected_action = detailed_actions[action_type]
        if self.selected_action:
            self.signalTemplateUrl.emit(self.selected_action['template'])
            self.signalCanClean.emit(self.selected_action['cleaner'] is not None)

    def do_reset(self):
        self.selected_action = None
        self.excel_path = None
        self.signalTemplateUrl.emit("")
        self.signalReset.emit()
        self.signalCanClean.emit(False)
        self.should_clean = False

    @Slot()
    def start(self):
        worker = Worker(
            self.selected_action,
            self.excel_path,
            loading_signal=self.signalLoading,
            result_signal=self.signalReportPath,
            state_signal=self.signalState,
            reset=self.do_reset,
            should_clean=self._should_clean,
        )
        self.thread_pool.start(worker)

    @Property(type=list, constant=True)
    def actions(self):
        return self._actions

    @Property(type=bool)
    def should_clean(self):
        return self._should_clean

    @should_clean.setter
    def should_clean(self, should_clean):
        self._should_clean = should_clean

    @Slot(str)
    def open_file(self, file_path):
        if sys.platform == "win32":
            os.startfile(file_path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, file_path])

    @Slot(QUrl)
    def set_excel_path(self, url):
        if url:
            self.excel_path = os.path.abspath(url.toLocalFile())
        else:
            self.excel_path = None
