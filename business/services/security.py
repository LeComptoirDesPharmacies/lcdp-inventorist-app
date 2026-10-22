import keyring
from business.constant import APPLICATION_NAME

API_KEY_NAME = 'import-app-api-key'

# Set once this process has written the api key to the keyring (successful login
# and keychain access granted). Reading the keyring otherwise is not free: on macOS
# an unsigned build triggers the keychain access prompt (LDS-6282).
_api_key_persisted = False


def persist_api_key(api_key):
    global _api_key_persisted
    keyring.set_password(APPLICATION_NAME, API_KEY_NAME, api_key)
    _api_key_persisted = True


def is_api_key_persisted():
    return _api_key_persisted


def delete_api_key():
    if get_api_key():
        keyring.delete_password(APPLICATION_NAME, API_KEY_NAME)


def get_api_key():
    api_key = keyring.get_password(APPLICATION_NAME, API_KEY_NAME)
    return api_key
