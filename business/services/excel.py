import logging

from openpyxl import load_workbook

from api.consume.gen.auth import ApiException
from business.factories.excel_factory import LaboratoryExcelLineBuilder
from business.factories.receipts import create_laboratory_sale_offer_receipt
from business.services.product import find_or_create_product
from business.services.sale_offer import create_or_edit_sale_offer


def create_sale_offer_from_excel(excel_path):
    results = []
    lines = __read_laboratory_excel(excel_path)
    logging.info(f"{len(lines)} excel line(s) are candide for sale offer creation")
    results = list(map(__create_sale_offer_from_excel_line, lines))
    succeeded_lines = len(list(filter(lambda o: o['result'] is not None, results)))
    errors_lines = len(list(filter(lambda o: o['error'] is not None, results)))
    logging.info(f"{succeeded_lines} sale offer(s) has been created")
    logging.info(f"{errors_lines} line have an error")


def __read_laboratory_excel(excel_url):
    wb = load_workbook(excel_url, read_only=True)
    rows = wb['Annonces'].iter_rows(5)
    builder = LaboratoryExcelLineBuilder(rows, create_laboratory_sale_offer_receipt).build()
    lines = builder.get_lines()
    return lines


def __create_sale_offer_from_excel_line(excel_line):
    sale_offer = None
    error = None
    if excel_line.can_create_sale_offer():
        try:
            product = find_or_create_product(excel_line.sale_offer.product,
                                             excel_line.can_create_product_from_scratch())
            sale_offer = create_or_edit_sale_offer(excel_line.sale_offer, product)
        except ApiException as apiErr:
            logging.error('An API error occur', apiErr)
            error = str(apiErr)
        except Exception as err:
            logging.error('An error occur during line processing', err)
            error = str(err)

    return {
        'excel_line': excel_line,
        'result': sale_offer,
        'error': error
    }
