import logging
import os
import subprocess
import sys
from urllib.parse import urlparse

from PySide6.QtCore import QObject, Slot, Signal

from business.factories.receipts import create_laboratory_sale_offer_receipt
from business.services.excel import create_sale_offer_from_excel, create_excel_summary


class App(QObject):
    def __init__(self):
        QObject.__init__(self)

    signalLoading = Signal(bool)
    signalReportPath = Signal(str)
    signalChangeState = Signal(str)
    signalTemplateUrl = Signal(str)

    receipt = None

    @Slot(str)
    def select_receipt(self, receipt_type):
        if receipt_type == 'PHARMLAB_STORE':
            self.receipt = create_laboratory_sale_offer_receipt
            self.signalTemplateUrl.emit("https://docs.google.com/spreadsheets/d/1NKjBQ0DDzRpkyn5YV396OUVlYq7_h0C7/edit?usp=sharing&ouid=110512712826531059999&rtpof=true&sd=true")

    @Slot(str)
    def get_excel(self, excel_url):
        try:
            self.signalLoading.emit(True)

            self.signalChangeState.emit("Récupération du fichier excel...")
            parsed_url = urlparse(excel_url)
            excel_path = os.path.abspath(os.path.join(parsed_url.netloc, parsed_url.path))

            self.signalChangeState.emit("Création/Modification des ressources...")
            results = create_sale_offer_from_excel(excel_path, self.receipt)

            self.signalChangeState.emit("Création du rapport...")
            report_path = create_excel_summary(results, self.receipt)
            self.signalReportPath.emit(report_path)
            self.signalChangeState.emit("Le fichier a bien été traité")
        except Exception as Err:
            logging.exception('Cannot read excel with url {}'.format(excel_url))
        finally:
            self.signalLoading.emit(False)

    @Slot(str)
    def open_file(self, file_path):
        if sys.platform == "win32":
            os.startfile(file_path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, file_path])
