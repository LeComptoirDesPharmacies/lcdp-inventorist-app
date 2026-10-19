import unittest
from unittest import mock

from business.services import authentication, security


class TestDeleteSessionApiKey(unittest.TestCase):

    def setUp(self):
        security._api_key_persisted = False

    def tearDown(self):
        security._api_key_persisted = False

    @mock.patch('business.services.security.keyring')
    def test_does_not_touch_keyring_without_login(self, keyring):
        authentication.delete_session_api_key()

        keyring.get_password.assert_not_called()
        keyring.delete_password.assert_not_called()

    @mock.patch('business.services.authentication.remove_setting')
    @mock.patch('business.services.authentication.get_setting', return_value='42')
    @mock.patch('business.services.authentication.get_manage_api_key_api')
    @mock.patch('business.services.security.keyring')
    def test_deletes_api_key_persisted_by_this_session(self, keyring, get_manage_api_key_api, _get_setting,
                                                      remove_setting):
        keyring.get_password.return_value = 'api-key'

        security.persist_api_key('api-key')
        authentication.delete_session_api_key()

        get_manage_api_key_api.return_value.delete_api_key.assert_called_once()
        self.assertEqual(get_manage_api_key_api.return_value.delete_api_key.call_args.kwargs['api_key_id'], 42)
        remove_setting.assert_called_once()

    @mock.patch('business.services.security.keyring')
    def test_failed_keyring_write_does_not_mark_key_as_persisted(self, keyring):
        keyring.set_password.side_effect = RuntimeError('Keychain Access Denied')

        with self.assertRaises(RuntimeError):
            security.persist_api_key('api-key')

        self.assertFalse(security.is_api_key_persisted())


if __name__ == '__main__':
    unittest.main()
