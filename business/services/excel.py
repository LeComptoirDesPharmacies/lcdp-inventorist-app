import logging
import tempfile
import time
import os

from openpyxl import load_workbook, Workbook
from api.consume.gen.sale_offer import ApiException as SaleOfferApiException
from api.consume.gen.product import ApiException as ProductApiException
from api.consume.gen.laboratory import ApiException as LaboratoryApiException
from api.consume.gen.configuration import ApiException as ConfigurationApiException
from business.factories.excel_lines_factory import LaboratoryExcelLinesBuilder
from business.factories.receipts import error_receipt
from business.mappers.api_error import sale_offer_api_exception_to_muggle, product_api_exception_to_muggle, \
    api_exception_to_muggle
from business.services.product import find_or_create_product
from business.services.sale_offer import create_or_edit_sale_offer


def create_sale_offer_from_excel(excel_path, receipt):
    lines = __read_excel(excel_path, receipt)
    logging.info(f"{len(lines)} excel line(s) are candide for sale offer creation")
    results = list(map(__create_sale_offer_from_excel_line, lines))
    return results


def create_excel_summary(results, receipt):
    wb = Workbook()
    wb.remove_sheet(wb.active)

    dirpath = tempfile.mkdtemp()
    current_time = int(time.time())

    summary_path = os.path.join(dirpath, str(current_time) + "-summary.xlsx")

    succeeded_lines = list(filter(lambda o: o['result'] is not None, results))
    __create_success_sheet(wb, receipt, succeeded_lines, wb.active)

    errors_lines = list(filter(lambda o: o['error'] is not None, results))
    __create_error_sheet(wb, receipt, errors_lines)

    logging.info(f"{len(succeeded_lines)} sale offer(s) has been created")
    logging.info(f"{len(errors_lines)} line have an error")
    wb.save(filename=summary_path)
    return summary_path


def __create_success_sheet(wb, receipt, lines, sheet=None):
    if not sheet:
        sheet = wb.create_sheet(title="Succès")
    else:
        sheet.title = "Succès"
    sheet.append(list(map(lambda x: x.excel_column_name, receipt)))
    for line in lines:
        sheet.append(list(map(lambda x: x.get_from_obj(line['excel_line']), receipt)))
    return sheet


def __create_error_sheet(wb, receipt, lines, sheet=None):
    if not sheet:
        sheet = wb.create_sheet(title="Erreur")
    else:
        sheet.title = "Erreur"

    summary_error_receipt = receipt + error_receipt
    headers = list(map(lambda x: x.excel_column_name, summary_error_receipt))
    headers.append("Erreur application")
    sheet.append(headers)

    for line in lines:
        sheet.append(list(map(
            lambda x: x.get_from_obj(line['excel_line']), summary_error_receipt
        )) + [line["error"]])
    return sheet


def __read_excel(excel_url, receipt):
    wb = load_workbook(excel_url, read_only=True)
    #TODO: change this method to be more generic
    rows = wb['Annonces'].iter_rows(5)
    builder = LaboratoryExcelLinesBuilder(rows, receipt).build()
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
        except SaleOfferApiException as sale_offer_api_err:
            logging.error('An API error occur in sale offer api', sale_offer_api_err)
            error = sale_offer_api_exception_to_muggle(sale_offer_api_err)
        except ProductApiException as product_api_err:
            logging.error('An API error occur in product api', product_api_err)
            error = product_api_exception_to_muggle(product_api_err)
        except (LaboratoryApiException, ConfigurationApiException) as api_err:
            logging.error('An API error occur in laboratory api on configuration api', api_err)
            error = api_exception_to_muggle(api_err)
        except Exception as err:
            logging.error('An error occur during line processing', err)
            error = str(err)

    return {
        'excel_line': excel_line,
        'result': sale_offer,
        'error': error
    }
