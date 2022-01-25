from api.consume.gen.configuration.api_client_utils import create_search_vat_api
from api.consume.gen.laboratory.api_client_utils import create_search_laboratory_api, create_manage_laboratory_api
from api.consume.gen.product.api_client_utils import create_search_product_api, create_search_product_metadata_api, \
    create_manage_product_api
from api.consume.gen.sale_offer.api_client_utils import create_manage_sale_offer_api, create_search_sale_offer_api

_search_laboratory_api = None
_manage_laboratory_api = None
_search_product_api = None
_search_product_metadata_api = None
_search_vat_api = None
_manage_product_api = None
_manage_sale_offer_api = None
_search_sale_offer_api = None


def get_search_vat_api():
    global _search_vat_api
    if not _search_vat_api:
        _search_vat_api = create_search_vat_api()
    return _search_vat_api


def get_search_product_api():
    global _search_product_api
    if not _search_product_api:
        _search_product_api = create_search_product_api()
    return _search_product_api


def get_search_product_metadata_api():
    global _search_product_metadata_api
    if not _search_product_metadata_api:
        _search_product_metadata_api = create_search_product_metadata_api()
    return _search_product_metadata_api


def get_search_laboratory_api():
    global _search_laboratory_api
    if not _search_laboratory_api:
        _search_laboratory_api = create_search_laboratory_api()
    return _search_laboratory_api


def get_manage_laboratory_api():
    global _manage_laboratory_api
    if not _manage_laboratory_api:
        _manage_laboratory_api = create_manage_laboratory_api()
    return _manage_laboratory_api


def get_manage_product_api():
    global _manage_product_api
    if not _manage_product_api:
        _manage_product_api = create_manage_product_api()
    return _manage_product_api


def get_manage_sale_offer_api():
    global _manage_sale_offer_api
    if not _manage_sale_offer_api:
        _manage_sale_offer_api = create_manage_sale_offer_api()
    return _manage_sale_offer_api


def get_search_sale_offer_api():
    global _search_sale_offer_api
    if not _search_sale_offer_api:
        _search_sale_offer_api = create_search_sale_offer_api()
    return _search_sale_offer_api
