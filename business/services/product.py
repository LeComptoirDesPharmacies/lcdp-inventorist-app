import logging
from functools import lru_cache

import backoff
import requests

import api.consume.gen.product.exceptions
from api.consume.gen.product import ApiException
from api.consume.gen.product.model.barcodes import Barcodes
from api.consume.gen.product.model.product_creation_or_update_parameters import ProductCreationOrUpdateParameters
from api.consume.gen.product.model.product_status import ProductStatus
from business.exceptions import CannotCreateProduct
from business.services.catalog import update_or_create_product_insight
from business.services.laboratory import find_or_create_laboratory
from business.services.providers import get_search_product_api, get_search_product_metadata_api, \
    get_manage_product_api
from business.services.security import get_api_key
from business.services.vat import get_vat_by_value


def product_excel_is_different_from_product(product, result_product):
    return ((product.unit_price is not None
             and product.unit_price != result_product.unit_price)
            or (product.name is not None
                and product.name != result_product.name)
            or (product.dci is not None
                and product.dci != result_product.dci)
            or (product.laboratory.name is not None
                and product.laboratory.name != result_product.laboratory.get('name', None))
            or (product.weight is not None
                and product.weight != result_product.unit_weight)
            or (product.product_type.name is not None
                and product.product_type.name != result_product.type.get('name', None))
            or (product.vat.value is not None
                # TVA from file is in percentage, TVA from insight is in value
                and (product.vat.value / 100) != result_product.vat.get('value', None)))


def service_unavailable_status_code(e):
    # do not retry if status code is different to 503
    return e.status != 503


@backoff.on_exception(backoff.expo,
                      api.consume.gen.product.exceptions.ServiceException,
                      max_tries=3,
                      max_time=20,
                      giveup=service_unavailable_status_code)
def update_or_create_product(map_products, product, can_create_product_from_scratch):
    if product and not product.is_empty():
        product_type = __find_product_type_by_name(product.product_type.name)
        vat = get_vat_by_value(product.vat.value)
        laboratory = find_or_create_laboratory(product.laboratory.name)

        logging.info(f'Barcode {product.principal_barcode} : Try to find or create product with barcode')
        result_product = __get_product_by_barcode(map_products,
                                                  product.principal_barcode) or __create_product_with_barcode(
            product.principal_barcode)

        if result_product:
            # check if product excel are equals to the product
            if product_excel_is_different_from_product(product, result_product):
                logging.info(f'Barcode {product.principal_barcode} : Update product insight with excel data')
                update_or_create_product_insight(
                    product=result_product,
                    excel_product=product,
                    product_type=product_type,
                    vat=vat,
                    laboratory=laboratory
                )
                return __sync_product(result_product.id)
            else:
                logging.info(f'Barcode {product.principal_barcode} : Product is up to date')
                return result_product

        # Create product from scratch
        if can_create_product_from_scratch:
            logging.info(f'Barcode {product.principal_barcode} : Create product from scratch')
            return __create_product_from_scratch(
                product,
                product_type,
                vat,
                laboratory
            )

        logging.info(f'Cannot find and create product')
        raise CannotCreateProduct()


def __get_products_by_barcodes(barcodes):
    if not len(barcodes):
        return None

    api = get_search_product_api()

    try:
        products = api.get_products(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
            barcodes_anyeq=barcodes,
            st_eq=['VALIDATED', 'WAITING_FOR_VALIDATION'],
            p=0,
            pp=len(barcodes)
        )
    except Exception as exc:
        logging.error(f'Error while searching products by barcodes {barcodes}', exc)
        return []

    return products.records if products else []


def __get_product_by_barcode(map_products, barcode):
    if not barcode:
        return None

    if barcode in map_products:
        return map_products[barcode]

    logging.info(f'Product {barcode} not found in map, search in API')

    api = get_search_product_api()

    products = api.get_products(
        _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
        barcodes_anyeq=[barcode],
        st_eq=['VALIDATED', 'WAITING_FOR_VALIDATION'],
        p=0, pp=1
    )

    return next(iter(products.records), None)


def __get_product_by_id(product_id):
    try:
        api = get_search_product_api()
        return api.get_product(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
            product_id=int(product_id)
        )
    except ApiException as apiError:
        raise apiError


@lru_cache(maxsize=128)
def __find_product_type_by_name(name):
    if name:
        api = get_search_product_metadata_api()
        product_types = api.get_product_types(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())]
        )
        type_iterator = filter(lambda x: x.name == name, product_types)
        return next(type_iterator, None)


def __create_product_with_barcode(principal_barcode):
    try:
        api = get_manage_product_api()
        payload = ProductCreationOrUpdateParameters(
            barcodes=Barcodes(principal=principal_barcode)
        )
        product = api.create_product(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
            x_with_sync=True,
            product_creation_or_update_parameters=payload
        )
        return product
    except ApiException as apiError:
        if str(apiError.status) == '400':
            return None
        if str(apiError.status) == '409':
            return __get_product_by_id(apiError.body)
        raise apiError


def __sync_product(product_id):
    api = get_manage_product_api()
    try:
        product = api.update_product(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
            x_with_sync=True,
            product_id=product_id,
            product_creation_or_update_parameters=ProductCreationOrUpdateParameters()
        )
        return product
    except ApiException as apiError:
        raise apiError


def __create_product_from_scratch(product, product_type, vat, laboratory):
    api = get_manage_product_api()
    product = api.create_product(
        _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
        x_with_sync=True,
        product_creation_or_update_parameters=ProductCreationOrUpdateParameters(
            name=product.name,
            dci=product.dci,
            unit_weight=product.weight,
            unit_price=product.unit_price,
            type_id=product_type.id if product_type else None,
            laboratory_id=laboratory.id,
            vat_id=vat.id,
            barcodes=Barcodes(
                eans=[product.principal_barcode],
                principal=product.principal_barcode
            )
        )
    )
    return product


def __set_product_status(product, status):
    try:
        api = get_manage_product_api()
        api.update_product(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
            product_id=product.id,
            product_creation_or_update_parameters=ProductCreationOrUpdateParameters(
                status=ProductStatus(value=status)
            )
        )
    except ApiException as ape:
        logging.exception("Failed to set product status", ape)


def change_product_status(product, new_status):
    if product and new_status:
        __set_product_status(product, new_status)
