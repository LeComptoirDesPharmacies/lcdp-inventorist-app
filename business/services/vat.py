from functools import lru_cache

from business.exceptions import VatNotFound
from business.services.providers import get_search_vat_api
from business.services.security import get_api_key


@lru_cache(maxsize=128)
def get_vat_by_value(value):
    if value is not None:
        api = get_search_vat_api()
        vats = api.get_vats(_request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),)
        vat_iterator = filter(lambda x: x.value == value/100 or x.value == value, vats)
        vat = next(vat_iterator, None)
        if not vat:
            raise VatNotFound()
        return vat
