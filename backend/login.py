import logging
import traceback
from PySide6.QtCore import QObject, Slot, Signal, QRunnable, QThreadPool
from sentry_sdk import capture_exception
from api.consume.gen.auth import ApiException as AuthApiException

from business.services.authentication import authenticate


class Worker(QRunnable):
    def __init__(self, email, password, loading_signal, state_signal, connected_signal):
        super().__init__()
        self.email = email
        self.password = password
        self.loading_signal = loading_signal
        self.state_signal = state_signal
        self.connected_signal = connected_signal

    def run(self):
        try:
            self.loading_signal.emit(True)
            self.state_signal.emit("Connexion en cours...", "INFO")
            user = authenticate(self.email, self.password)
            if user:
                self.connected_signal.emit(True)
                self.state_signal.emit("Connecté", "SUCCESS")
        except AuthApiException as auth_ex:
            self.connected_signal.emit(False)
            self.state_signal.emit("Email ou mot de passe érroné", "ERROR")
            logging.exception("An AuthApiException occur during authentication", auth_ex)
        except Exception as err:
            self.state_signal.emit("Une erreur s'est produite, veuillez contacter l'administrateur", "ERROR")
            logging.exception("An unknown exception occur during authentication", err)
            capture_exception(err)
        finally:
            traceback.print_exc()
            self.loading_signal.emit(False)


class Login(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.thread_pool = QThreadPool()
    
    signalState = Signal(str, str)
    signalConnected = Signal(bool)
    signalLoading = Signal(bool)

    @Slot(str, str)
    def login(self, email, password):
        worker = Worker(
            email,
            password,
            loading_signal=self.signalLoading,
            connected_signal=self.signalConnected,
            state_signal=self.signalState
        )
        self.thread_pool.start(worker)
