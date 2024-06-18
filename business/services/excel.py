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
from business.constant import CHUNK_SIZE
from business.exceptions import CannotUpdateSaleOfferStatus
from business.mappers.api_error import sale_offer_api_exception_to_muggle, product_api_exception_to_muggle, \
    api_exception_to_muggle, product_insight_api_exception_to_muggle
from business.mappers.excel_mapper import error_mapper
from business.models.update_policy import UpdatePolicy
from business.services.product import update_or_create_product, change_product_status, __get_products_by_barcodes
from business.services.sale_offer import create_or_edit_sale_offer, delete_deprecated_sale_offers, __get_sale_offers, \
    __get_latest_sale_offers
from business.utils import rgetattr, execution_time


def __prefetch(prefetch_type, keys_from_file, get_from_api, get_keys_from_api_object):
    packets = [list(keys_from_file)[i:i + CHUNK_SIZE] for i in range(0, len(keys_from_file), CHUNK_SIZE)]

    array_from_api = list(map(get_from_api, packets))

    flatten_array = []
    for sub_list in array_from_api:
        flatten_array.extend(sub_list)

    map_of_objects = {}
    for obj in flatten_array:
        keys = get_keys_from_api_object(obj)
        for key in keys:
            map_of_objects[key] = obj

    logging.info(f"Map of {prefetch_type} has {len(map_of_objects)} element(s)")

    return map_of_objects


@execution_time
def create_sale_offer_from_excel_lines(lines):
    logging.info(f"{len(lines)} excel line(s) are candide for sale offer modification/creation")

    products_barcodes = {x.sale_offer.product.principal_barcode for x in lines if
                         x.sale_offer.product.principal_barcode is not None}

    # [barcode, product]
    prefetched_products = __prefetch('products',
                                     products_barcodes,
                                     __get_products_by_barcodes,
                                     lambda x: list(
                                         filter(None, [x.barcodes.principal, x.barcodes.cip,
                                                       x.barcodes.cip13] + x.barcodes.eans)))

    # assume that all lines have the same update_policy
    update_policy = lines[0].sale_offer.update_policy

    if update_policy == UpdatePolicy.PRODUCT_BARCODE.value:
        logging.info("Update policy is PRODUCT_BARCODE, we will get the latest sale offers by product_id")

        # [owner_id, [product_id]]
        owner_id_barcodes = {}
        for line in lines:
            if (line.sale_offer.product.principal_barcode and
                    line.sale_offer.product.principal_barcode in prefetched_products):
                owner_id_barcodes.setdefault(line.sale_offer.owner_id, []).append(
                    prefetched_products[line.sale_offer.product.principal_barcode].id)

        # [(owner_id, product_id), sale_offer]
        prefetched_sale_offers = {}
        for (owner_id, product_ids) in owner_id_barcodes.items():
            prefetched_sale_offers = __prefetch('sale_offers enabled by (owner_id, product_id)',
                                                product_ids,
                                                lambda x: __get_latest_sale_offers(x, owner_id, ['ENABLED']),
                                                lambda x: [(owner_id, x.product.id)])

        product_ids_not_found = [product_id for (owner_id, product_ids) in owner_id_barcodes.items() for product_id in
                                 product_ids if (owner_id, product_id) not in prefetched_sale_offers]

        if len(product_ids_not_found):
            prefetched_sale_offers_others_status = __prefetch('sale_offers others status by (owner_id, product_id)',
                                                              product_ids_not_found,
                                                              lambda x: __get_latest_sale_offers(x, owner_id,
                                                                                                 ['WAITING_FOR_PRODUCT',
                                                                                                  'ASKING_FOR_INVOICE',
                                                                                                  'HOLIDAY',
                                                                                                  'DISABLED']),
                                                              lambda x: [(owner_id, x.product.id)])
            prefetched_sale_offers.update(prefetched_sale_offers_others_status)
    else:
        logging.info("Update policy is PRODUCT_REFERENCE, we will get the sale offers by reference")

        # [reference, sale_offer]
        sale_offers_reference = {x.sale_offer.reference for x in lines if
                                 x.sale_offer.reference is not None}

        prefetched_sale_offers = __prefetch('sale_offers by reference',
                                            sale_offers_reference,
                                            __get_sale_offers,
                                            lambda x: [x.reference])

    results = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(__create_sale_offer_from_excel_line,
                                   prefetched_sale_offers,
                                   prefetched_products,
                                   line): line for line in lines}
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logging.error(f"Error processing line {futures[future]}: {e}")

    return results


@execution_time
def create_or_update_product_from_excel_lines(lines):
    logging.info(f"{len(lines)} excel line(s) are candide for product modification/creation")

    products_barcodes = {x.sale_offer.product.principal_barcode for x in lines if
                         x.sale_offer.product.principal_barcode is not None}

    # [barcode, product]
    prefetched_products = __prefetch('products',
                                     products_barcodes,
                                     __get_products_by_barcodes,
                                     lambda x: list(
                                         filter(None, [x.barcodes.principal, x.barcodes.cip,
                                                       x.barcodes.cip13] + x.barcodes.eans)))

    results = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(__create_or_update_product_from_excel_line, prefetched_products, line): line for
                   line in lines}
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logging.error(f"Error processing line {futures[future]}: {e}")

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


def __create_sale_offer_from_excel_line(prefetched_sale_offers, prefetched_products, excel_line):
    sale_offer = None
    error = None
    try:
        product = update_or_create_product(prefetched_products, excel_line.sale_offer.product,
                                           excel_line.can_create_product_from_scratch())
        change_product_status(product=product, new_status=excel_line.sale_offer.product.status)
        sale_offer = create_or_edit_sale_offer(prefetched_sale_offers, excel_line.sale_offer, product,
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


def __create_or_update_product_from_excel_line(prefetched_products, excel_line):
    product = None
    error = None
    try:
        product = update_or_create_product(prefetched_products, excel_line.sale_offer.product,
                                           excel_line.can_create_product_from_scratch())
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
