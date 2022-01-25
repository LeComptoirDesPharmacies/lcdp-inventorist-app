from PySide6.QtCore import QObject, Slot
import logging
from business.services.import_sale_offer import read_laboratory_excel

import os
from urllib.parse import urlparse

from business.services.executor import process_line


class App(QObject):
    def __init__(self):
        QObject.__init__(self)

    @Slot(str)
    def get_excel(self, excel_url):
        try:
            parsed_url = urlparse(excel_url)
            excel_path = os.path.abspath(os.path.join(parsed_url.netloc, parsed_url.path))
            lines = read_laboratory_excel(excel_path)
            print("Lines are read : ", len(lines))
            for line in lines:
                process_line(line)
        except Exception as Err:
            logging.exception('Cannot read excel with url {}'.format(excel_url))
