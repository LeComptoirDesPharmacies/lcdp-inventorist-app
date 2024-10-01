import logging
from functools import lru_cache

from business.services.providers import get_search_product_metadata_api
from business.services.security import get_api_key
from business.services.vat import get_vat_by_value


def service_unavailable_status_code(e):
    # do not retry if status code is different to 503
    return e.status != 503


@lru_cache(maxsize=128)
def get_product_type_by_name(name):
    if name:
        api = get_search_product_metadata_api()
        product_types = api.get_product_types(
            _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key())
        )
        type_iterator = filter(lambda x: x.name == name, product_types)
        return next(type_iterator, None)
