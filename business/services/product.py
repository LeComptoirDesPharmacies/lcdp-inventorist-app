from api.consume.gen.product import ApiException
from api.consume.gen.product.model.barcodes import Barcodes
from api.consume.gen.product.model.product_creation_or_update_parameters import ProductCreationOrUpdateParameters
from business.exceptions import TooManyProduct, VatNotFound
from business.services.providers import get_search_product_api, get_search_product_metadata_api, get_search_vat_api, \
    get_manage_product_api
from business.services.security import get_api_key


def get_product_by_barcode(barcode):
    api = get_search_product_api()
    products = api.get_products(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        q=barcode, p=0, pp=2
    )
    if products and len(products.records) > 1:
        raise TooManyProduct()
    return next(iter(products.records), None)


def find_product_type_by_name(name):
    api = get_search_product_metadata_api()
    product_types = api.get_product_types(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key())
    )
    type_iterator = filter(lambda x: x.name == name, product_types)
    return next(type_iterator, None)


def get_vat_by_value(value):
    api = get_search_vat_api()
    vats = api.get_vats(_request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),)
    vat_iterator = filter(lambda x: x.value == value/100, vats)
    vat = next(vat_iterator, None)
    if not vat:
        raise VatNotFound()
    return vat


def create_product_with_barcode(principal_barcode):
    try:
        api = get_manage_product_api()
        payload = ProductCreationOrUpdateParameters(
            is_external_sync_enabled=True,
            barcodes=Barcodes(principal=principal_barcode)
        )
        product = api.create_product(
            _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
            product_creation_or_update_parameters=payload
        )
        # TODO: update product with name and price ??
        return product
    except ApiException as apiError:
        if str(apiError.status) == '400':
            return None
        raise apiError


def create_product_from_scratch(product, product_type, vat, laboratory):
    api = get_manage_product_api()
    product = api.create_product(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        product_creation_or_update_parameters=ProductCreationOrUpdateParameters(
            is_external_sync_enabled=False,
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
