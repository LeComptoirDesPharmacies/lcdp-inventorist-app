import logging
import os
import tempfile
import time
from concurrent.futures import as_completed, ThreadPoolExecutor

from openpyxl import load_workbook, Workbook

from api.consume.gen.catalog import ApiException as ProductInsightApiException
from api.consume.gen.configuration import ApiException as ConfigurationApiException
from api.consume.gen.laboratory import ApiException as LaboratoryApiException
from api.consume.gen.product import ApiException as ProductApiException
from api.consume.gen.sale_offer import ApiException as SaleOfferApiException
from business.exceptions import CannotUpdateSaleOfferStatus
from business.mappers.api_error import sale_offer_api_exception_to_muggle, product_api_exception_to_muggle, \
    api_exception_to_muggle, product_insight_api_exception_to_muggle
from business.mappers.excel_mapper import error_mapper
from business.services.product import update_or_create_product, change_product_status, __get_products_by_barcodes
from business.services.sale_offer import create_or_edit_sale_offer, delete_deprecated_sale_offers, __get_sale_offers
from business.utils import rgetattr, execution_time


@execution_time
def create_sale_offer_from_excel_lines(lines):
    logging.info(f"{len(lines)} excel line(s) are candide for sale offer modification/creation")

    # excel_line.sale_offer.product
    arrayOfBarcode = [x.sale_offer.product.principal_barcode for x in lines if
                      x.sale_offer.product.principal_barcode is not None]
    # logging.info(f"List of barcode: {arrayOfBarcode}")

    chunk_size = 50
    packets = [arrayOfBarcode[i:i + chunk_size] for i in range(0, len(arrayOfBarcode), chunk_size)]
    # logging.info(f"List of packets: {packets}")

    array_of_existing_products = list(map(__get_products_by_barcodes, packets))
    # existing_products = __create_or_update_product_from_excel_line(packets[0])
    # records = __create_or_update_product_from_excel_line(packets[0])

    existing_products = []
    for sub_list in array_of_existing_products:
        existing_products.extend(sub_list)

    map_products = {}
    for product in existing_products:
        principal_barcode = product.barcodes.principal
        map_products[principal_barcode] = product

    # excel_line.sale_offer.reference
    # list of sale_offer.reference
    arrayOfReference = [x.sale_offer.reference for x in lines if x.sale_offer.reference is not None]
    # logging.info(f"List of reference: {arrayOfReference}")
    # chunk_size = 50
    packets = [arrayOfReference[i:i + chunk_size] for i in range(0, len(arrayOfReference), chunk_size)]
    # logging.info(f"List of packets: {packets}")

    array_of_existing_sale_offers = list(map(__get_sale_offers, packets))
    # existing_sale_offers = __find_existing_sale_offers(packets)
    # records = __find_existing_sale_offers(packets[0])

    existing_sale_offers = []
    for sub_list in array_of_existing_sale_offers:
        existing_sale_offers.extend(sub_list)

    map_sale_offers = {}
    for sale_offer in existing_sale_offers:
        reference = sale_offer.reference
        map_sale_offers[reference] = sale_offer

    # records = __find_existing_sale_offers(arrayOfReference)
    # logging.info(f"map: {map_sale_offers}")

    # results = list(map(lambda line: __create_sale_offer_from_excel_line(map_sale_offers, map_products, line), lines))

    results = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(__create_sale_offer_from_excel_line, map_sale_offers, map_products, line): line for
                   line in lines}
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logging.error(f"Error processing line {futures[future]}: {e}")

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
    try:
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
    finally:
        wb.close()

    return results


def __create_sale_offer_from_excel_line(map_sale_offers, map_products, excel_line):
    sale_offer = None
    error = None
    try:
        product = update_or_create_product(map_products, excel_line.sale_offer.product,
                                           excel_line.can_create_product_from_scratch())
        change_product_status(product=product, new_status=excel_line.sale_offer.product.status)
        sale_offer = create_or_edit_sale_offer(map_sale_offers, excel_line.sale_offer, product,
                                               excel_line.can_create_sale_offer())
    except SaleOfferApiException as sale_offer_api_err:
        logging.error('An API error occur in sale offer api', sale_offer_api_err)
        error = sale_offer_api_exception_to_muggle(sale_offer_api_err)
    except CannotUpdateSaleOfferStatus as sale_offer_status_error:
        logging.error('An API error occur during the sale offer status update', sale_offer_status_error)
        error = str(sale_offer_status_error)
    except ProductApiException as product_api_err:
        logging.error('An API error occur in product api', product_api_err)
        error = product_api_exception_to_muggle(product_api_err)
    except (LaboratoryApiException, ConfigurationApiException) as api_err:
        logging.error('An API error occur in laboratory api or configuration api', api_err)
        error = api_exception_to_muggle(api_err)
    except ProductInsightApiException as product_insight_api_err:
        logging.error('An API error occur in product insight api', product_insight_api_err)
        error = product_insight_api_exception_to_muggle(product_insight_api_err)
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
    except ProductInsightApiException as product_insight_api_err:
        logging.error('An API error occur in product insight api', product_insight_api_err)
        error = product_insight_api_exception_to_muggle(product_insight_api_err)
    except Exception as err:
        logging.error('An error occur during line processing', err)
        error = str(err)

    return {
        'excel_line': excel_line,
        'result': product,
        'error': error
    }


def clean_sale_offers(lines):
    owner_id = next((line.sale_offer.owner_id for line in lines if line.sale_offer.owner_id), None)
    if owner_id:
        delete_deprecated_sale_offers(owner_id)
