from PySide6.QtCore import QObject, Slot
import logging
from business.services.excel import create_sale_offer_from_excel

import os
from urllib.parse import urlparse


class App(QObject):
    def __init__(self):
        QObject.__init__(self)

    @Slot(str)
    def get_excel(self, excel_url):
        try:
            parsed_url = urlparse(excel_url)
            excel_path = os.path.abspath(os.path.join(parsed_url.netloc, parsed_url.path))
            create_sale_offer_from_excel(excel_path)
        except Exception as Err:
            logging.exception('Cannot read excel with url {}'.format(excel_url))
