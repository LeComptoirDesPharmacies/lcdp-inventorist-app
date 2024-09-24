import logging
import os
import subprocess
import sys
from sentry_sdk import capture_exception
import traceback

from threading import Thread
from time import sleep

from PySide6.QtCore import QObject, Slot, Signal, QThreadPool, QRunnable, Property, QUrl, QTimer

from business.mappers.assembly_mapper import fromAssemblyToTable, fromAssembliesToTable, fromAssemblyTypeToString, fromAssemblyStatusToString, get_action, computePercent

from api.consume.gen.user.exceptions import ForbiddenException

from business.actions import detailed_actions, simple_actions
from business.services.assembly import get_user_assemblies
from PySide6.QtCore import QObject, Signal, Slot
from business.services.assembly import get_assembly_output
import os
from business.services.excel import dict_to_excel
import json


class Worker(QRunnable):
    def __init__(self, action, excel_path, loading_signal, state_signal, results_signal, reset, should_clean):
        super().__init__()
        self.action = action
        self.excel_path = excel_path
        self.loading_signal = loading_signal
        self.state_signal = state_signal
        self.results_signal = results_signal
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
        executor(lines, clean=self.should_clean)


def open_file_operating_system(file_path):
    if sys.platform == "win32":
        os.startfile(file_path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, file_path])



class App(QObject):
    signalLoading = Signal(bool)
    signalCanClean = Signal(bool)
    signalState = Signal(str, str)
    signalReports = Signal(list)
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
        self.__results_timer = QTimer(self)
        self.__results_timer.timeout.connect(self.refresh_data)
        self.__results_timer.start(5000)
        #self.__results_timer.timeout.emit()  # force an immediate update

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
            results_signal=self.signalReports,
            state_signal=self.signalState,
            reset=self.do_reset,
            should_clean=self._should_clean
        )
        self.thread_pool.start(worker)

    @Slot()
    def refresh_data(self):
        try:
            user_id = 14
            # get_current_user_id()
            if user_id:
                print("--- POLL")
                # print("----------------------------- POLL RESULT -----------------------------")
                assemblies = get_user_assemblies(user_id)
                #
                # print("----------------------------- Emit Signal -----------------------------")
                self.signalReports.emit(fromAssembliesToTable(assemblies))
                print("signal emit")
            else:
                print("not logged yet")
        except ForbiddenException:
            # User is forbidden so maybe api key is not working
            print("-------------------------------> ForbiddenException")
            pass
        except Exception as err:
            print("-------------------------------> EXCeption")
            logging.exception('Error while retrieving results', err)

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
        open_file_operating_system(file_path)

    @Slot(QUrl)
    def set_excel_path(self, url):
        if url:
            self.excel_path = os.path.abspath(url.toLocalFile())
        else:
            self.excel_path = None

    @Slot(str)
    def downloadFile(self, id: str):
        try:
            output = get_assembly_output(id)

            download_path = os.path.join(os.path.expanduser("~"), "Downloads")
            download_file = os.path.join(download_path, 'Rapport de {}.xlsx'.format(id))
            output = json.loads(output)

            dict_to_excel(download_file, output)
            open_file_operating_system(download_file)

        except Exception as e:
            print(f"Erreur lors du téléchargement : {e}")
