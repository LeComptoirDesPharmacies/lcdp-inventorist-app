import logging
import os
import tempfile
import time

from api.consume.gen.factory.models.assembly_creation_parameters import  AssemblyCreationParameters
from api.consume.gen.factory.models.any_factory import AnyFactory
from api.consume.gen.factory.models.any_distribution_mode import AnyDistributionMode

from openpyxl import load_workbook, Workbook

from business.constant import CHUNK_SIZE
from business.mappers.excel_mapper import error_mapper
from business.utils import rgetattr, execution_time

from business.services.security import get_api_key
from business.services.providers import get_manage_assembly_api, get_search_user_api

from business.services.vat import get_vat_by_value
from business.services.product import get_product_type_by_name
from business.services.user import get_current_user_id

from business.models.sale_offer import UNITARY_DISTRIBUTION, RANGE_DISTRIBUTION, QUOTATION_DISTRIBUTION

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


def __build_product_upsert(product_line):
    product_type = get_product_type_by_name(product_line.product_type.name)
    vat = get_vat_by_value(product_line.vat.value)

    product_upsert = dict()

    if product_line.principal_barcode:
        product_upsert['principal_barcode'] = product_line.principal_barcode

    if product_line.name:
        product_upsert['name'] = product_line.name

    if product_line.dci:
        product_upsert['dci'] = product_line.dci

    if product_line.laboratory.name:
        product_upsert['laboratory_name'] = product_line.laboratory.name

    if product_line.weight:
        product_upsert['unit_weight'] = product_line.weight

    if product_line.unit_price:
        product_upsert['unit_price'] = product_line.unit_price

    if product_line.status:
        product_upsert['status'] = product_line.status.upper()

    if product_type:
        product_upsert['type_id'] = product_type.id

    if vat:
        product_upsert['vat_id'] = vat.id

def __build_distribution_mode(sale_offer_line):
    if sale_offer_line.sale_offer.distribution_type == RANGE_DISTRIBUTION:
        ranges = []
        for range in sale_offer_line.sale_offer.distribution.ranges:
            new_range = {
                'quantity': range.sold_by,
                'unit_price': range.discounted_price,
                'free_units': range.free_unit
            }
            ranges.append(new_range)
        distribution_mode = {
            'type': 'RANGE',
            'ranges': ranges,
            'minimal_quantity': 1,
            'maximal_quantity': sale_offer_line.sale_offer.distribution.maximal_quantity
        }
    elif sale_offer_line.sale_offer.distribution_type == UNITARY_DISTRIBUTION:
        distribution_mode = {
            'type': 'UNITARY',
            'unit_price': sale_offer_line.sale_offer.distribution.discounted_price,
            'sold_by': sale_offer_line.sale_offer.distribution.sold_by,
            'minimal_quantity': 1,
            'maximal_quantity': sale_offer_line.sale_offer.distribution.maximal_quantity
        }
    elif sale_offer_line.sale_offer.distribution_type == QUOTATION_DISTRIBUTION:
        distribution_mode = {
            'type': 'QUOTATION',
            'sold_by': sale_offer_line.sale_offer.distribution.sold_by,
            'minimal_quantity': 1,
            'maximal_quantity': sale_offer_line.sale_offer.distribution.maximal_quantity
        }
    else:
        distribution_mode = dict()

    return distribution_mode

def __build_stock(stock_line):
    stock = dict()

    if stock_line.remaining_quantity:
        stock['remaining_quantity'] = stock_line.remaining_quantity

    if stock_line.lapsing_date:
        stock['lapsing_date'] = stock_line.lapsing_date

    if stock_line.batch:
        stock['batch'] = stock_line.batch

    return stock

@execution_time
def sale_offer_upsert_from_excel_lines(lines, clean=False, **kwargs):
    logging.info(f"{len(lines)} excel line(s) are candide for sale offer modification/creation")


    items = []

    for line in lines:
        product_upsert = __build_product_upsert(line.sale_offer.product)
        distribution_mode = __build_distribution_mode(line)
        stock = __build_stock(line.sale_offer.stock)

        new_item = dict()

        if product_upsert:
            new_item['product'] = product_upsert

        if distribution_mode:
            new_item['distributionMode'] = AnyDistributionMode(distribution_mode)

        if stock:
            new_item['stock'] = stock

        if line.sale_offer.status:
            new_item['status'] = line.sale_offer.status.upper()

        if line.sale_offer.rank:
            new_item['rank'] = line.sale_offer.rank

        if line.sale_offer.description:
            new_item['description'] = line.sale_offer.description

        if line.sale_offer.owner_id:
            new_item['owner_id'] = line.sale_offer.owner_id

        items.append(new_item)

    manage_assembly_api = get_manage_assembly_api()

    assembly = manage_assembly_api.create_assembly(
        AssemblyCreationParameters(
            owner_id= get_current_user_id(),
            factory = AnyFactory({
                'type': 'SALE_OFFER_UPSERT',
                'clean': clean,
                'records': items,
            }),
        ),
        _request_auth=manage_assembly_api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
    )

    results = []

    return results

@execution_time
def create_offer_planificiation_from_excel_lines(lines, clean=False, **kwargs):
    logging.info(f"{len(lines)} excel line(s) are candide for sale offer modification/creation")

    items = []

    for line in lines:
        product_upsert = __build_product_upsert(line.sale_offer.product)
        distribution_mode = __build_distribution_mode(line)
        stock = __build_stock(line.sale_offer.stock)

        new_item = dict()

        if product_upsert:
            new_item['product'] = product_upsert

        if distribution_mode:
            new_item['distributionMode'] = AnyDistributionMode(distribution_mode)

        if stock:
            new_item['stock'] = stock

        if line.sale_offer.status:
            new_item['status'] = line.sale_offer.status.upper()

        if line.sale_offer.rank:
            new_item['rank'] = line.sale_offer.rank

        if line.sale_offer.description:
            new_item['description'] = line.sale_offer.description

        if line.sale_offer.owner_id:
            new_item['owner_id'] = line.sale_offer.owner_id

        items.append(new_item)

    manage_assembly_api = get_manage_assembly_api()

    assembly = manage_assembly_api.create_assembly(
        AssemblyCreationParameters(
            owner_id= get_current_user_id(),
            factory= AnyFactory({
                'type': 'OFFER_PLANIFICATION',
                'clean': clean,
                'records': items
            })),
        _request_auth=manage_assembly_api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
    )


    results = []

    return results


@execution_time
def product_upsert_from_excel_lines(lines, **kwargs):
    logging.info(f"{len(lines)} excel line(s) are candide for product modification/creation")


    items = []

    for line in lines:
        product_upsert = __build_product_upsert(line.sale_offer.product)

        items.append(product_upsert)

    manage_assembly_api = get_manage_assembly_api()


    assembly = manage_assembly_api.create_assembly(
        AssemblyCreationParameters(
            owner_id= get_current_user_id(),
            factory= AnyFactory({
                'type': 'PRODUCT_UPSERT',
                'records': items,
            })
        ),
        _request_auth=manage_assembly_api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
    )

    results = []

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

            cells = {
                column_indices[col]: int(value) if isinstance(value, float) and value.is_integer() else value
                for col, value in enumerate(row)
                if value is not None
            }

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



