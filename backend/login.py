import time
import logging
from PySide6.QtCore import QObject, Slot, Signal, QSettings

from business.services.authentication import authenticate


class Login(QObject):
    def __init__(self):
        QObject.__init__(self)
    
    signalLoginState = Signal(str, bool)
    signalUserName = Signal(str)
    signalConnected = Signal(bool)
    signalLoading = Signal(bool)

    @Slot(str, str)
    def login(self, email, password):
        try:
            self.signalLoading.emit(True)
            self.signalLoginState.emit("Connexion en cours...", False)
            user = authenticate(email, password)
            if user:
                self.signalConnected.emit(True)
                self.signalUserName.emit(user.firstname)
                self.signalLoginState.emit("Connecté", False)
        except Exception as err:
            self.signalConnected.emit(False)
            self.signalLoginState.emit("Email ou mot de passe érroné", True)
            logging.exception("An exception occur during authentication", err)
        finally:
            self.signalLoading.emit(False)