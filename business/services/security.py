import keyring
from business.constant import APPLICATION_NAME

API_KEY_NAME = 'import-app-api-key'


def persist_api_key(api_key):
    keyring.set_password(APPLICATION_NAME, API_KEY_NAME, api_key)


def delete_api_key():
    if get_api_key():
        keyring.delete_password(APPLICATION_NAME, API_KEY_NAME)


def get_api_key():
    api_key = keyring.get_password(APPLICATION_NAME, API_KEY_NAME)
    return api_key
