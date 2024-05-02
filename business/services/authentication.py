from api.consume.gen.auth.model.login_credential import LoginCredential
from business.services.providers import get_auth_api, get_search_user_api, get_manage_api_key_api
from business.services.security import API_KEY_NAME, persist_api_key, get_api_key
from business.services.settings import get_setting, set_setting, remove_setting
from business.constant import API_KEY_ID_NAME


def __create_api_key(email, password):
    auth_api = get_auth_api()
    response = auth_api.login(any_authentication_credential=LoginCredential(
        grant_type='password',
        login=email,
        password=password,
    ))
    search_user_api = get_search_user_api()
    user = search_user_api.get_current_user(
        _request_auths=[search_user_api.api_client.create_auth_settings('bearerAuth', response.access_token)]
    )
    manage_api_key_api = get_manage_api_key_api()
    token = manage_api_key_api.create_api_key(
        {'name': API_KEY_NAME, 'owner_id': user.id, 'is_internal': False},
        _request_auths=[manage_api_key_api.api_client.create_auth_settings('bearerAuth', response.access_token)]
    )
    return token, user


def authenticate(email, password):
    # if app crashes, apiKeyId is not deleted from keyring and always exists
    delete_api_key()

    token, user = __create_api_key(email, password)
    persist_api_key(token.value)
    set_setting(API_KEY_ID_NAME, token.id)
    return user


def delete_api_key():
    api_key = get_api_key()
    api_key_id = get_setting(API_KEY_ID_NAME)

    if api_key and api_key_id:
        try:
            # if user open and close app, without login, try to delete old api_key
            if isinstance(api_key_id, str):
                api_key_id = int(api_key_id)

            manage_api_key_api = get_manage_api_key_api()
            manage_api_key_api.delete_api_key(
                _request_auths=[manage_api_key_api.api_client.create_auth_settings("apiKeyAuth", api_key)],
                api_key_id=api_key_id
            )
        finally:
            remove_setting(API_KEY_ID_NAME)
