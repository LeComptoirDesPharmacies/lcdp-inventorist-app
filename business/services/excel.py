import logging
import tempfile
import time
import os

from openpyxl import load_workbook, Workbook

from api.consume.gen.sale_offer import ApiException as SaleOfferApiException
from api.consume.gen.product import ApiException as ProductApiException
from api.consume.gen.laboratory import ApiException as LaboratoryApiException
from api.consume.gen.configuration import ApiException as ConfigurationApiException
from business.mappers.excel_mapper import error_mapper
from business.mappers.api_error import sale_offer_api_exception_to_muggle, product_api_exception_to_muggle, \
    api_exception_to_muggle
from business.services.product import update_or_create_product, change_product_status
from business.services.sale_offer import create_or_edit_sale_offer, delete_deprecated_sale_offers
from business.utils import rgetattr


def create_sale_offer_from_excel_lines(lines):
    logging.info(f"{len(lines)} excel line(s) are candide for sale offer modification/creation")
    results = list(map(__create_sale_offer_from_excel_line, lines))
    return results


def create_or_update_product_from_excel_lines(lines):
    logging.info(f"{len(lines)} excel line(s) are candide for product modification/creation")
    results = list(map(__create_or_update_product_from_excel_line, lines))
    return results


def create_excel_summary(results, excel_mapper):
    wb = Workbook()
    wb.remove_sheet(wb.active)

    dirpath = tempfile.mkdtemp()
    current_time = int(time.time())

    summary_path = os.path.join(dirpath, str(current_time) + "-summary.xlsx")

    succeeded_lines = list(filter(lambda o: o['result'] is not None, results))
    __create_success_sheet(wb, excel_mapper, succeeded_lines, wb.active)

    errors_lines = list(filter(lambda o: o['error'] is not None, results))
    __create_error_sheet(wb, excel_mapper, errors_lines)

    logging.info(f"{len(succeeded_lines)} sale offer(s) has been created")
    logging.info(f"{len(errors_lines)} line have an error")
    wb.save(filename=summary_path)
    return summary_path


def __create_success_sheet(wb, excel_mapper, lines, sheet=None):
    if not sheet:
        sheet = wb.create_sheet(title="Succès")
    else:
        sheet.title = "Succès"
    sheet.append(list(map(lambda x: x.excel_column_name, excel_mapper)))
    for line in lines:
        sheet.append(list(map(lambda x: x.get_from_obj(line['excel_line']), excel_mapper)))
    return sheet


def __create_error_sheet(wb, excel_mapper, lines, sheet=None):
    if not sheet:
        sheet = wb.create_sheet(title="Erreur")
    else:
        sheet.title = "Erreur"

    summary_error_excel_mapper = excel_mapper + error_mapper
    headers = list(map(lambda x: x.excel_column_name, summary_error_excel_mapper))
    headers.append("Erreur application")
    sheet.append(headers)

    for line in lines:
        sheet.append(list(map(
            lambda x: x.get_from_obj(line['excel_line']), summary_error_excel_mapper
        )) + [line["error"]])
    return sheet


def excel_to_dict(obj_class, excel_path, excel_mapper, sheet_name, header_row,
                  min_row, max_row=None, obj_unique_key=None, custom_dict=None):
    results = {}
    if isinstance(custom_dict, dict):
        results = custom_dict

    wb = load_workbook(excel_path, read_only=True)
    ws = wb[sheet_name]
    column_indices = {col: cell.value for col, cell in enumerate(ws[header_row])}
    for idx, row in enumerate(ws.iter_rows(min_row=min_row, max_row=max_row, values_only=True)):
        obj = obj_class()
        cells = {column_indices[col]: value for col, value in enumerate(row)}
        for col in excel_mapper:
            col.set_from_excel(obj, cells.get(col.excel_column_name, None))
        if obj_unique_key:
            obj_key = rgetattr(obj, obj_unique_key, None)
            results[obj_key] = obj
        else:
            results[idx] = obj

    return results


def __create_sale_offer_from_excel_line(excel_line):
    sale_offer = None
    error = None
    try:
        product = update_or_create_product(excel_line.sale_offer.product,
                                           excel_line.can_create_product_from_scratch())
        change_product_status(product=product, new_status=excel_line.sale_offer.product.status)
        sale_offer = create_or_edit_sale_offer(excel_line.sale_offer, product, excel_line.can_create_sale_offer())
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


def __create_or_update_product_from_excel_line(excel_line):
    product = None
    error = None
    try:
        product = update_or_create_product(excel_line.sale_offer.product, excel_line.can_create_product_from_scratch())
        change_product_status(product=product, new_status=excel_line.sale_offer.product.status)
    except ProductApiException as product_api_err:
        logging.error('An API error occur in product api', product_api_err)
        error = product_api_exception_to_muggle(product_api_err)
    except Exception as err:
        logging.error('An error occur during line processing', err)
        error = str(err)

    return {
        'excel_line': excel_line,
        'result': product,
        'error': error
    }


def clean_laboratory_sale_offers(lines):
    owner_id = next((line.sale_offer.owner_id for line in lines if line.sale_offer.owner_id), None)
    if owner_id:
        delete_deprecated_sale_offers(owner_id)
