from business.services.providers import get_search_user_api
from business.services.security import get_api_key

def get_current_user_id() -> int:
    api_key = get_api_key()

    print("##########|")
    print(api_key)

    search_user_api = get_search_user_api()

    user = search_user_api.get_current_user(
        _request_auth=search_user_api.api_client.create_auth_settings("apiKeyAuth", api_key),
    )

    print("USER ID: {}".format(user.id))

    return user.id