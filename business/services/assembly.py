from business.services.providers import get_search_assembly_api
from business.services.security import get_api_key


def get_user_assemblies(user_id: int):
    api = get_search_assembly_api()
    assemblies = api.get_assemblies(
        p=1,
        pp=10,
        order_by='CREATED_AT:desc',
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key())
    )
    return assemblies
