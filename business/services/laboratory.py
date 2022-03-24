import logging

from api.consume.gen.laboratory.model.laboratory_creation_parameters import LaboratoryCreationParameters
from business.exceptions import TooManyLaboratory
from business.services.providers import get_search_laboratory_api, get_manage_laboratory_api
from business.services.security import get_api_key


def find_or_create_laboratory(laboratory_name):
    if laboratory_name:
        logging.info(f'Name {laboratory_name} : Try to find laboratory')
        laboratory = __get_laboratory_by_name(laboratory_name)
        if not laboratory:
            logging.info(f'Name {laboratory_name} : '
                         f'Laboratory not found, try to create laboratory')
            laboratory = __create_laboratory(laboratory_name)
        return laboratory


def __get_laboratory_by_name(name):
    api = get_search_laboratory_api()
    laboratories = api.get_laboratories(
        _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
        name_eq=name, p=0, pp=2
    )
    if laboratories and len(laboratories.records) > 1:
        raise TooManyLaboratory()
    return next(iter(laboratories.records), None)


def __create_laboratory(name):
    api = get_manage_laboratory_api()
    laboratory = api.create_laboratory(
        _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
        laboratory_creation_parameters=LaboratoryCreationParameters(name=name)
    )
    return laboratory
