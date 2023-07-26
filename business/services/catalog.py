import logging

from api.consume.gen.catalog import ApiException
from api.consume.gen.catalog.model.product_insight_create_or_update_parameters import \
    ProductInsightCreateOrUpdateParameters
from business.exceptions import TooManyProductInsight
from business.services.providers import get_manage_product_insight_api, get_search_product_insight_api
from business.services.security import get_api_key
from business.utils import clean_none_from_dict

def update_or_create_product_insight(product, excel_product, product_type, vat, laboratory):
    if product.source.lcdp_catalog and product.source.lcdp_catalog.id:
        logging.info(f'Product insight already link with product. Update insight {product.source.lcdp_catalog.id}')
        return __update_product_insight(product.source.lcdp_catalog.id, product.barcodes, excel_product, product_type, vat, laboratory)

    product_insight = __get_product_insight_by_barcodes(product.barcodes)
    if product_insight:
        logging.info(f'Product insight found by barcode. Update insight {product.source.lcdp_catalog.id}')
        return __update_product_insight(product_insight.id, product.barcodes, excel_product, product_type, vat, laboratory)

    logging.info(f'Create a new product insight')
    return __create_product_insight(product, excel_product, product_type, vat, laboratory)

def __update_product_insight(product_insight_id, barcodes, excel_product, product_type, vat, laboratory):
    api = get_manage_product_insight_api()
    payload = clean_none_from_dict({
        'signatures': __create_product_insight_signature(barcodes),
        'name': excel_product.name,
        'dci': excel_product.dci,
        'unit_weight': excel_product.weight,
        'unit_price': excel_product.unit_price,
        'type_id': product_type.id if product_type else None,
        'vat_id': vat.id if vat else None,
        'laboratory_id': laboratory.id if laboratory else None,
    })
    try:
        product_insight = api.update_product_insight(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
            product_insight_id=product_insight_id,
            product_insight_create_or_update_parameters=ProductInsightCreateOrUpdateParameters(**payload)
        )
        return product_insight
    except ApiException as apiError:
        if str(apiError.status) == '409':
            raise TooManyProductInsight()
        raise apiError

def __get_product_insight_by_barcodes(barcodes):
    api = get_search_product_insight_api()
    product_insights = api.get_product_insights(
        _request_auths = [api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
        signatures_anyeq = __create_product_insight_signature(barcodes), p=0, pp=2
    )
    if product_insights and len(product_insights.records) > 1:
        raise TooManyProductInsight()
    return next(iter(product_insights.records), None)


def __create_product_insight(product, excel_product, product_type, vat, laboratory):
    api = get_manage_product_insight_api()
    payload = clean_none_from_dict({
        'signatures': __create_product_insight_signature(product.barcodes),
        'name': excel_product.name,
        'dci': excel_product.dci,
        'unit_weight': excel_product.weight,
        'unit_price': excel_product.unit_price,
        'type_id': product_type.id if product_type else None,
        'vat_id': vat.id if vat else None,
        'laboratory_id': laboratory.id if laboratory else None,
    })
    try:
        product_insight = api.create_product_insight(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
            product_insight_create_or_update_parameters=ProductInsightCreateOrUpdateParameters(**payload)
        )
        return product_insight
    except ApiException as apiError:
        if str(apiError.status) == '409':
            raise TooManyProductInsight()
        raise apiError

def __create_product_insight_signature(barcodes):
    signatures = set([])
    if barcodes:
        for code_name in barcodes.attribute_map.keys():
            code_value = barcodes.get(code_name)
            if code_value:
                if type(code_value) == list:
                    signatures.update(code_value)
                else:
                    signatures.add(code_value)
    return list(signatures)