from business.services.providers import get_search_assembly_api
from business.services.security import get_api_key

from api.consume.gen.factory.controllers import search_assembly_api

from uuid import UUID
import uuid
from api.consume.gen.factory.models.assembly import Assembly

from business.services.providers import get_search_assembly_api

def get_user_assemblies(user_id: int):
    api = get_search_assembly_api()
    assemblies = api.get_assemblies(
        o_eq=[user_id],
        p=0,
        pp=10,
        order_by='CREATED_AT:desc',
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key())
    )
    return assemblies

def get_assembly_output(assembly_id: str):
    search_assembly_api = get_search_assembly_api()
    output = search_assembly_api.get_assembly_output(
        str(assembly_id),
        _request_auth=search_assembly_api.api_client.create_auth_settings("apiKeyAuth", get_api_key())
    )
    return output

