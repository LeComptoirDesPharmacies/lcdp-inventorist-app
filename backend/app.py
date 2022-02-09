import logging
import os
import subprocess
import sys
from urllib.parse import urlparse

from PySide6.QtCore import QObject, Slot, Signal, QThreadPool, QRunnable, Property

from business.actions import detailed_actions, simple_actions
from business.services.excel import create_excel_summary


class Worker(QRunnable):
    def __init__(self, action, excel_path, loading_signal, state_signal, result_signal):
        super().__init__()
        self.action = action
        self.excel_path = excel_path
        self.loading_signal = loading_signal
        self.state_signal = state_signal
        self.result_signal = result_signal

    def run(self):
        try:
            self.loading_signal.emit(True)

            self.state_signal.emit("Récupération du fichier excel...")
            parsed_url = urlparse(self.excel_path)
            excel_os_path = os.path.abspath(os.path.join(parsed_url.netloc, parsed_url.path))
            self.execute(excel_os_path)
        except Exception as Err:
            logging.exception('Cannot read excel with url {}'.format(self.excel_path))
        finally:
            self.loading_signal.emit(False)

    def execute(self, excel_path):
        self.state_signal.emit("Récupération des ressources dans le fichier...")
        mapper_class = self.action['mapper']
        mapper = mapper_class(excel_path)
        lines = mapper.map_to_obj()

        self.state_signal.emit("Création/Modification des ressources...")
        executor = self.action['executor']
        results = executor(lines)

        self.state_signal.emit("Création du rapport...")
        report_path = create_excel_summary(results, mapper.excel_mapper)
        self.result_signal.emit(report_path)
        self.state_signal.emit("Le fichier a bien été traité")


class App(QObject):
    signalLoading = Signal(bool)
    signalChangeState = Signal(str)
    signalReportPath = Signal(str)
    signalTemplateUrl = Signal(str)
    signalActions = Signal(list)

    def __init__(self):
        QObject.__init__(self)
        self.thread_pool = QThreadPool()
        self._actions = simple_actions
        self.selected_action = None
        self.signalActions.emit(simple_actions)

    excel_path = None

    @Slot(str)
    def select_action(self, action_type):
        if action_type in detailed_actions:
            self.selected_action = detailed_actions[action_type]
        if self.selected_action:
            self.signalTemplateUrl.emit(self.selected_action['template'])

    @Slot()
    def start(self):
        worker = Worker(
            self.selected_action,
            self.excel_path,
            loading_signal=self.signalLoading,
            result_signal=self.signalReportPath,
            state_signal=self.signalChangeState
        )
        self.thread_pool.start(worker)

    @Slot(str)
    def set_excel_path(self, excel_path):
        self.excel_path = excel_path

    @Property(type=list, constant=True)
    def actions(self):
        return self._actions

    @Slot(str)
    def open_file(self, file_path):
        if sys.platform == "win32":
            os.startfile(file_path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, file_path])
