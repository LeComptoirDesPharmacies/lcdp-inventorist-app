from api.consume.gen.laboratory.model.laboratory_creation_parameters import LaboratoryCreationParameters
from business.exceptions import TooManyLaboratory
from business.services.providers import get_search_laboratory_api, get_manage_laboratory_api
from business.services.security import get_api_key


def get_laboratory_by_name(name):
    api = get_search_laboratory_api()
    laboratories = api.get_laboratories(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        name_ili=name, p=0, pp=2
    )
    if laboratories and len(laboratories.records) > 1:
        raise TooManyLaboratory()
    return next(iter(laboratories.records), None)


def create_laboratory(name):
    api = get_manage_laboratory_api()
    laboratory = api.create_laboratory(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        laboratory_creation_parameters=LaboratoryCreationParameters(name=name)
    )
    return laboratory
