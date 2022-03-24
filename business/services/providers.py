from api.consume.gen.auth.api_client_utils import create_auth_api, create_manage_api_key_api
from api.consume.gen.configuration.api_client_utils import create_search_vat_api
from api.consume.gen.laboratory.api_client_utils import create_search_laboratory_api, create_manage_laboratory_api
from api.consume.gen.product.api_client_utils import create_search_product_api, create_search_product_metadata_api, \
    create_manage_product_api
from api.consume.gen.sale_offer.api_client_utils import create_manage_sale_offer_api, create_search_sale_offer_api
from api.consume.gen.user.api_client_utils import create_search_user_api
from settings import get_settings

_auth_api = None
_search_user_api = None
_manage_api_key_api = None
_search_laboratory_api = None
_manage_laboratory_api = None
_search_product_api = None
_search_product_metadata_api = None
_search_vat_api = None
_manage_product_api = None
_manage_sale_offer_api = None
_search_sale_offer_api = None

settings = get_settings()

configuration = {
    'host': settings.value("PROVIDER_HOST"),
    'is_secured': settings.value("IS_PROVIDER_SECURE") == "True"
}

print('HOST', settings.value("PROVIDER_HOST"))


def get_auth_api():
    global _auth_api
    if not _auth_api:
        print('configuration', configuration)
        _auth_api = create_auth_api(configuration)
    return _auth_api


def get_search_user_api():
    global _search_user_api
    if not _search_user_api:
        _search_user_api = create_search_user_api(configuration)
    return _search_user_api


def get_manage_api_key_api():
    global _manage_api_key_api
    if not _manage_api_key_api:
        _manage_api_key_api = create_manage_api_key_api(configuration)
    return _manage_api_key_api


def get_search_vat_api():
    global _search_vat_api
    if not _search_vat_api:
        _search_vat_api = create_search_vat_api(configuration)
    return _search_vat_api


def get_search_product_api():
    global _search_product_api
    if not _search_product_api:
        _search_product_api = create_search_product_api(configuration)
    return _search_product_api


def get_search_product_metadata_api():
    global _search_product_metadata_api
    if not _search_product_metadata_api:
        _search_product_metadata_api = create_search_product_metadata_api(configuration)
    return _search_product_metadata_api


def get_search_laboratory_api():
    global _search_laboratory_api
    if not _search_laboratory_api:
        _search_laboratory_api = create_search_laboratory_api(configuration)
    return _search_laboratory_api


def get_manage_laboratory_api():
    global _manage_laboratory_api
    if not _manage_laboratory_api:
        _manage_laboratory_api = create_manage_laboratory_api(configuration)
    return _manage_laboratory_api


def get_manage_product_api():
    global _manage_product_api
    if not _manage_product_api:
        _manage_product_api = create_manage_product_api(configuration)
    return _manage_product_api


def get_manage_sale_offer_api():
    global _manage_sale_offer_api
    if not _manage_sale_offer_api:
        _manage_sale_offer_api = create_manage_sale_offer_api(configuration)
    return _manage_sale_offer_api


def get_search_sale_offer_api():
    global _search_sale_offer_api
    if not _search_sale_offer_api:
        _search_sale_offer_api = create_search_sale_offer_api(configuration)
    return _search_sale_offer_api
