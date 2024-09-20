import logging
from PySide6.QtCore import QObject, Slot, Signal, QRunnable, QThreadPool, QAbstractTableModel, Qt
from sentry_sdk import capture_exception
from api.consume.gen.auth import ApiException as AuthApiException

from business.services.authentication import authenticate
from sentry_sdk import set_user

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
            print("---------------------------------------------------")
            print("|{}|".format(self.email))
            print("|{}|".format(self.password))
            print("---------------------------------------------------")
            user = authenticate(self.email, self.password)
            if user:
                set_user({"id": user.id, "email": user.email})
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
            self.loading_signal.emit(False)


# def fromAssembliesToTable(assemblies):
#     result = []
#     for assembly in assemblies.records:
#         result.append(fromAssemblyToTable(assembly))
#
#     return result
#
#
# def fromAssemblyToTable(assembly):
#     print("ASSEMBLY factory_type: {}".format(assembly.factory_type))
#     return dict({
#         'name': assembly.status,
#         'value': assembly.factory_type.type,
#         'percent': (assembly.cursor / assembly.total_steps) * 100
#     })



class Login(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.thread_pool = QThreadPool()
    
    signalState = Signal(str, str)
    signalConnected = Signal(bool)
    signalLoading = Signal(bool)
    signalReports = Signal(list)

    @Slot(str, str)
    def login(self, email, password):
        print("-----------------------------")
        print("LOGIN !")
        print("-----------------------------")
        worker = Worker(
            email,
            password,
            loading_signal=self.signalLoading,
            connected_signal=self.signalConnected,
            state_signal=self.signalState
        )
        self.thread_pool.start(worker)

    # @Slot()
    # def refresh_data(self):
    #     import random
    #
    #     user_id = get_current_user_id()
    #     if user_id:
    #         print("-----------------------------")
    #         print("POLL RESULT")
    #         print("-----------------------------")
    #         assemblies = get_user_assemblies(user_id)
    #
    #         print("-----------------------------")
    #         print("Emit Signal")
    #         print("-----------------------------")
    #         self.signalReports.emit(fromAssembliesToTable(assemblies))


        # # Ici, vous généreriez ou récupéreriez vos vraies données
        # # Pour cet exemple, nous créons des données aléatoires
        # new_data = [
        #     {"name": f"Item {i}", "value": random.randint(1, 100)}
        #     for i in range(10)  # Générons 10 items pour l'exemple
        # ]
        # print("refresh_data")
        # print(new_data)
        # self.signalReports.emit(new_data)
