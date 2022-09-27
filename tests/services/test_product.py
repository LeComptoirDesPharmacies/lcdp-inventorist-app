import unittest
from unittest.mock import patch, MagicMock, Mock

from api.consume.gen.product import ApiException
from business.exceptions import CannotCreateProduct, TooManyProduct
from business.models.product import Product
from business.services.product import update_or_create_product


MY_PRODUCT_TYPES = [
    Mock(id=1, name="medicament"),
    Mock(id=2, name="homeopathie"),
    Mock(id=3, name="parapharmacie"),
    Mock(id=4, name="dm"),
    Mock(id=5, name="veterinaire"),
    Mock(id=6, name="complement"),
]


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.search_product_meta_patch = patch('business.services.product.get_search_product_metadata_api')
        self.search_vat_patch = patch('business.services.product.get_vat_by_value')
        self.search_manage_laboratory_patch = patch('business.services.product.find_or_create_laboratory')
        self.search_product_patch = patch('business.services.product.get_search_product_api')
        self.manage_product_patch = patch('business.services.product.get_manage_product_api')
        self.get_api_key_patch = patch('business.services.product.get_api_key')

        search_product_meta_mock = self.search_product_meta_patch.start()
        search_product_mock = self.search_product_patch.start()
        manage_product_mock = self.manage_product_patch.start()
        search_vat_mock = self.search_vat_patch.start()
        search_manage_laboratory_mock = self.search_manage_laboratory_patch.start()
        get_api_key_patch_mock = self.get_api_key_patch.start()
        get_api_key_patch_mock.return_value = {}

        self.search_product_api = search_product_mock.return_value
        self.manage_product_api = manage_product_mock.return_value
        self.search_product_meta_api = search_product_meta_mock.return_value

        self.search_product_meta_api.get_product_types.return_value = MY_PRODUCT_TYPES
        search_vat_mock.return_value = MagicMock(id='VAT1', value=0.2)
        search_manage_laboratory_mock.return_value = MagicMock(id=1, name="My laboratory")

        self.mocked_product = MagicMock(Product)
        self.mocked_product.id = 1
        self.mocked_product.name = "Product name"
        self.mocked_product.dci = "D.C.I"
        self.mocked_product.weight = 100.0
        self.mocked_product.unit_price = 10.20
        self.mocked_product.product_type.name = "medicament"
        self.mocked_product.principal_barcode = "My barcode"
        self.mocked_product.external_sync = True

    def tearDown(self):
        self.search_product_meta_patch.stop()
        self.search_vat_patch.stop()
        self.search_manage_laboratory_patch.stop()
        self.search_product_patch.stop()
        self.manage_product_patch.stop()
        self.get_api_key_patch.stop()

    def test_update_or_create_product_with_none_product(self):
        with self.assertRaises(CannotCreateProduct):
            update_or_create_product(None, True)

    def test_update_or_create_product_with_product_found_by_barcode(self):
        expected = MagicMock(id=2, name="new product name")
        self.search_product_api.get_products.return_value = MagicMock(
            records=[MagicMock(id=2, name=self.mocked_product.name)]
        )

        self.manage_product_api.update_product.return_value = expected
        result = update_or_create_product(self.mocked_product, True)

        self.manage_product_api.create_product.assert_not_called()
        self.assertEqual(expected, result)

    def test_update_or_create_product_with_two_product_found_by_barcode(self):
        expected = MagicMock(id=2, name="new product name")
        self.search_product_api.get_products.return_value = MagicMock(
            records=[MagicMock(id=2, name=self.mocked_product.name), MagicMock(id=1, name=self.mocked_product.name)]
        )

        self.manage_product_api.update_product.return_value = expected
        with self.assertRaises(TooManyProduct):
            update_or_create_product(self.mocked_product, True)
            self.manage_product_api.create_product.assert_not_called()

    def test_update_or_create_product_with_product_creation_by_barcode(self):
        expected = MagicMock(id=2, name="new product name")
        self.search_product_api.get_products.return_value = MagicMock(
            records=[]
        )

        self.manage_product_api.create_product.return_value = MagicMock(id=2, name=self.mocked_product.name)
        self.manage_product_api.update_product.return_value = expected

        result = update_or_create_product(self.mocked_product, True)

        self.search_product_api.get_products.assert_called_once()
        self.assertEqual(expected, result)

    def test_update_or_create_product_with_product_creation_by_barcode_api_exception_400(self):
        self.search_product_api.get_products.return_value = MagicMock(
            records=[]
        )

        self.manage_product_api.create_product.side_effect = ApiException(status=400)

        with self.assertRaises(CannotCreateProduct):
            update_or_create_product(self.mocked_product, False)

    def test_update_or_create_product_with_product_creation_by_barcode_api_exception_409(self):
        expected = MagicMock(id=2, name="new product name")

        self.search_product_api.get_product.return_value = expected
        self.manage_product_api.update_product.return_value = expected
        self.search_product_api.get_products.return_value = MagicMock(
            records=[]
        )
        self.manage_product_api.create_product.side_effect = ApiException(
            http_resp=Mock(status=409, data='2', getheaders=lambda: None, reason="Product already exist")
        )
        result = update_or_create_product(self.mocked_product, False)
        self.search_product_api.get_product.assert_called_once()
        self.assertEqual(expected, result)

    def test_update_or_create_product_with_product_creation_by_barcode_api_exception(self):
        self.search_product_api.get_products.return_value = MagicMock(
            records=[]
        )

        self.manage_product_api.create_product.side_effect = ApiException(status=500)

        with self.assertRaises(ApiException):
            update_or_create_product(self.mocked_product, False)

    @patch('business.services.product.__create_product_with_barcode')
    def test_update_or_create_product_with_product_creation_from_scratch(self, create_product_with_barcode_mock):
        expected = MagicMock(id=2, name="new product name")
        self.search_product_api.get_products.return_value = MagicMock(
            records=[]
        )

        create_product_with_barcode_mock.return_value = None

        self.manage_product_api.create_product.return_value = expected

        result = update_or_create_product(self.mocked_product, True)

        self.search_product_api.get_products.assert_called_once()
        self.search_product_api.update_product.assert_not_called()
        self.assertEqual(expected, result)

    def test_update_or_create_product_with_inability_to_create_product(self):
        self.search_product_api.get_products.return_value = MagicMock(
            records=[]
        )

        self.manage_product_api.create_product.return_value = None

        with self.assertRaises(CannotCreateProduct):
            update_or_create_product(self.mocked_product, False)
            self.search_product_api.get_products.assert_called_once()
            self.search_product_api.update_product.assert_not_called()
