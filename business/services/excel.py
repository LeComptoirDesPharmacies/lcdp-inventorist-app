from openpyxl import load_workbook

from business.factories.excel_factory import ExcelLineBuilder
from business.factories.receipts import laboratory_excel_receipt
from business.services.executor import create_sale_offer_from_excel_line


def create_sale_offer_from_excel(excel_path):
    lines = __read_laboratory_excel(excel_path)
    for line in lines:
        create_sale_offer_from_excel_line(line)


def __read_laboratory_excel(excel_url):
    wb = load_workbook(excel_url, read_only=True)
    rows = wb['Annonces'].iter_rows(2)
    builder = ExcelLineBuilder(rows, laboratory_excel_receipt).build()
    lines = builder.get_lines()
    return lines







