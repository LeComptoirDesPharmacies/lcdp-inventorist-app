from api.consume.gen.auth.api_client_utils import create_auth_api, create_manage_api_key_api
from api.consume.gen.auth.model.login_credential import LoginCredential
from api.consume.gen.user.api_client_utils import create_search_user_api
from business.services.security import API_KEY_NAME, persist_api_key, get_api_key
from business.services.settings import get_setting, set_setting, remove_setting
from business.constant import API_KEY_ID_NAME


def __create_api_key(email, password):
    auth_api = create_auth_api()
    response = auth_api.login(any_authentication_credential=LoginCredential(
        grant_type='password',
        login=email,
        password=password,
    ))
    search_user_api = create_search_user_api({'access_token': response.access_token})
    user = search_user_api.get_current_user()
    manage_api_key_api = create_manage_api_key_api({'access_token': response.access_token})
    token = manage_api_key_api.create_api_key({'name': API_KEY_NAME, 'owner_id': user.id, 'is_internal': False})
    return token, user


def authenticate(email, password):
    token, user = __create_api_key(email, password)
    persist_api_key(token.value)
    set_setting(API_KEY_ID_NAME, token.id)
    return user


def delete_api_key():
    api_key = get_api_key()
    api_key_id = get_setting(API_KEY_ID_NAME)
    if api_key and api_key_id:
        manage_api_key_api = create_manage_api_key_api()
        manage_api_key_api.delete_api_key(
            _request_auth=manage_api_key_api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
            api_key_id=get_setting(API_KEY_ID_NAME)
        )
        remove_setting(API_KEY_ID_NAME)
