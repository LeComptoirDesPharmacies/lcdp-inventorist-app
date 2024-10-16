import logging
import subprocess
import sys
import os
from sentry_sdk import capture_exception

from PySide6.QtCore import QThreadPool, QRunnable, Property, QUrl
from PySide6.QtCore import QObject, Signal, Slot, Qt

from api.consume.gen.user.exceptions import ForbiddenException
from api.consume.gen.factory.exceptions import ApiException
from business.mappers.assembly_mapper import fromAssembliesToTable
from business.actions import detailed_actions, simple_actions
from business.services.assembly import get_user_assemblies
from business.services.assembly import get_assembly_output
from business.services.user import get_current_user_id
from business.services.excel import dict_to_excel


class Worker(QRunnable):
    def __init__(self, action, excel_path, loading_signal, state_signal, reset, connexion_status_signal, should_clean):
        super().__init__()
        self.action = action
        self.excel_path = excel_path
        self.loading_signal = loading_signal
        self.state_signal = state_signal
        self.reset = reset
        self.connexion_status_signal = connexion_status_signal
        self.should_clean = should_clean

    def run(self):
        try:
            self.loading_signal.emit(True)
            self.state_signal.emit("Récupération du fichier excel...", "INFO", "")
            self.execute(self.excel_path)
        except ApiException as e:
            if e.status == 409:
                self.state_signal.emit("Un import est déjà en cours pour ce client", "ERROR", str(e))
            else:
                raise Exception(e)

        except Exception as e:
            self.state_signal.emit("Une erreur s'est produite, veuillez contacter l'administrateur", "ERROR", str(e))
            logging.exception('Error during excel import, excel url: {}'.format(self.excel_path), e)
            capture_exception(e)
        finally:
            self.loading_signal.emit(False)

    def execute(self, excel_path):
        self.state_signal.emit("Récupération des ressources dans le fichier...", "INFO", "")
        mapper_class = self.action['mapper']
        mapper = mapper_class(excel_path)
        lines = mapper.map_to_obj()

        self.state_signal.emit("Création/Modification des ressources...", "INFO", "")

        executor = self.action['executor']
        executor(lines, clean=self.should_clean)


class FetchAssemblies(QRunnable):
    current_user_id = None

    def __init__(self, refresh_data_signal, connexion_status_signal):
        super().__init__()
        self.refresh_data_signal = refresh_data_signal
        self.connexion_status_signal = connexion_status_signal

    def run(self):
        try:
            if FetchAssemblies.current_user_id is None:
                FetchAssemblies.current_user_id = get_current_user_id()

            if FetchAssemblies.current_user_id:
                assemblies = get_user_assemblies(FetchAssemblies.current_user_id)
                self.refresh_data_signal.emit(fromAssembliesToTable(assemblies))
            self.connexion_status_signal.emit(True)
        except ForbiddenException:
            # User is forbidden so maybe api key is not working
            self.connexion_status_signal.emit(False)
            pass
        except Exception as err:
            logging.exception('Error while retrieving results', err)
            self.connexion_status_signal.emit(False)


def open_file_operating_system(file_path):
    if sys.platform == "win32":
        os.startfile(file_path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, file_path])


class App(QObject):
    signalLoading = Signal(bool)
    signalCanClean = Signal(bool)
    signalState = Signal(str, str, str)
    signalRefreshData = Signal(list)
    signalTemplateUrl = Signal(str)
    signalActions = Signal(list)
    signalReset = Signal()
    signalConnexionStatus = Signal(bool)
    downloadRequested = Signal(str)
    current_user_id = None

    def __init__(self):
        QObject.__init__(self)
        self.thread_pool = QThreadPool()
        self._actions = simple_actions
        self.selected_action = None
        self.signalActions.emit(simple_actions)
        self.excel_path = None
        self._should_clean = False
        self.downloadRequested.connect(self.downloadAndOpenFile, Qt.QueuedConnection)

    def on_exit(self):
        self.thread_pool.clear()
        self.thread_pool.waitForDone()

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
            state_signal=self.signalState,
            reset=self.do_reset,
            should_clean=self._should_clean,
            connexion_status_signal=self.signalConnexionStatus
        )
        self.thread_pool.start(worker)


    @Slot()
    def refresh_data(self):
        if self.current_user_id is None:
            self.current_user_id = get_current_user_id()

        worker = FetchAssemblies(
            refresh_data_signal = self.signalRefreshData,
			connexion_status_signal=self.signalConnexionStatus
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
        open_file_operating_system(file_path)

    @Slot(QUrl)
    def set_excel_path(self, url):
        if url:
            self.excel_path = os.path.abspath(url.toLocalFile())
        else:
            self.excel_path = None

    @Slot(str)
    def queueDownloadAndOpenFile(self, file_id):
        self.downloadRequested.emit(file_id)

    @Slot(str)
    def downloadAndOpenFile(self, assembly_id: str):
        try:
            output = get_assembly_output(assembly_id)

            # Create file in Download folder
            download_path = os.path.join(os.path.expanduser("~"), "Downloads")
            download_file = os.path.join(download_path, 'Rapport de {}.xlsx'.format(assembly_id))

            dict_to_excel(output, download_file)
            open_file_operating_system(download_file)
        except Exception as e:
            logging.exception(f"Erreur lors du téléchargement")