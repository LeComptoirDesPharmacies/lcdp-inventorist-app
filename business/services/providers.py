from api.consume.gen.auth.api_client_utils import create_auth_api, create_manage_api_key_api
from api.consume.gen.user.api_client_utils import create_search_user_api
from api.consume.gen.factory.api_client_utils import create_manage_assembly_api, create_search_assembly_api
from api.consume.gen.product.api_client_utils import create_search_product_metadata_api
from api.consume.gen.configuration.api_client_utils import create_search_vat_api
from settings import get_settings

_auth_api = None
_search_user_api = None
_manage_api_key_api = None
_search_assembly_api = None
_manage_assembly_api = None

settings = get_settings()

configuration = {
    'host': settings.value("PROVIDER_HOST"),
    'is_secured': settings.value("IS_PROVIDER_SECURE") == "True"
}

def get_auth_api():
    global _auth_api
    if not _auth_api:
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

def get_search_product_metadata_api():
    global _search_product_metadata_api
    if not _search_product_metadata_api:
        _search_product_metadata_api = create_search_product_metadata_api(configuration)
    return _search_product_metadata_api

def get_search_assembly_api():
    global _search_assembly_api
    if not _search_assembly_api:
        _search_assembly_api = create_search_assembly_api(configuration)
    return _search_assembly_api

def get_manage_assembly_api():
    global _manage_assembly_api
    if not _manage_assembly_api:
        _manage_assembly_api = create_manage_assembly_api(configuration)
    return _manage_assembly_api
