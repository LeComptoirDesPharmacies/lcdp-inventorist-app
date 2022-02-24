import unittest
from unittest.mock import patch, Mock

from nose2.tools import params

from business.exceptions import VatNotFound
from business.services.vat import get_vat_by_value

MY_VATS = [
    Mock(id='VAT1', value=0.055),
    Mock(id='VAT2', value=0.2),
    Mock(id='VAT3', value=0.021),
    Mock(id='VAT4', value=0.1),
    Mock(id='VAT5', value=0),
]


class TestVat(unittest.TestCase):

    def setUp(self):
        self.search_patch = patch('business.services.vat.get_search_vat_api')
        self.get_api_key_patch = patch('business.services.vat.get_api_key')
        search_mock = self.search_patch.start()
        self.search_api = search_mock.return_value
        get_api_key_patch_mock = self.get_api_key_patch.start()
        get_api_key_patch_mock.return_value = {}

    def tearDown(self) -> None:
        self.search_patch.stop()
        self.get_api_key_patch.stop()

    def test_get_vat_by_none_value(self):
        self.search_api.get_vats.return_value = MY_VATS
        result = get_vat_by_value(None)
        self.assertIsNone(result)

    @params(5.5, 20, 2.1, 10, 0)
    def test_get_vat_by_value(self, value):
        expected = value/100
        self.search_api.get_vats.return_value = MY_VATS
        result = get_vat_by_value(value)
        self.assertEqual(expected, result.value)

    @params(5, 2, 11, 3)
    def test_get_vat_by_not_found_value(self, value):
        self.search_api.get_vats.return_value = MY_VATS
        with self.assertRaises(VatNotFound):
            get_vat_by_value(value)
