import logging
import os
import subprocess
import sys
from urllib.parse import urlparse

from PySide6.QtCore import QObject, Slot, Signal, QThreadPool, QRunnable

from business.constant import CREATE_LABORATORY_SALE_OFFER_TPL
from business.factories.receipts import create_laboratory_sale_offer_receipt
from business.services.excel import create_sale_offer_from_excel, create_excel_summary


class Worker(QRunnable):
    def __init__(self, receipt, excel_path, loading_signal, state_signal, result_signal):
        super().__init__()
        self.receipt = receipt
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

            self.state_signal.emit("Création/Modification des ressources...")
            results = create_sale_offer_from_excel(excel_os_path, self.receipt)

            self.state_signal.emit("Création du rapport...")
            report_path = create_excel_summary(results, self.receipt)
            self.result_signal.emit(report_path)
            self.state_signal.emit("Le fichier a bien été traité")
        except Exception as Err:
            logging.exception('Cannot read excel with url {}'.format(self.excel_path))
        finally:
            self.loading_signal.emit(False)


class App(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.thread_pool = QThreadPool()

    signalLoading = Signal(bool)
    signalChangeState = Signal(str)
    signalReportPath = Signal(str)
    signalTemplateUrl = Signal(str)

    receipt = None
    excel_path = None

    @Slot(str)
    def select_receipt(self, receipt_type):
        if receipt_type == 'PHARMLAB_STORE':
            self.receipt = create_laboratory_sale_offer_receipt
            self.signalTemplateUrl.emit(CREATE_LABORATORY_SALE_OFFER_TPL)

    @Slot()
    def start(self):
        worker = Worker(
            self.receipt,
            self.excel_path,
            loading_signal=self.signalLoading,
            result_signal=self.signalReportPath,
            state_signal=self.signalChangeState
        )
        self.thread_pool.start(worker)

    @Slot(str)
    def get_excel(self, excel_path):
        self.excel_path = excel_path

    @Slot(str)
    def open_file(self, file_path):
        if sys.platform == "win32":
            os.startfile(file_path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, file_path])
