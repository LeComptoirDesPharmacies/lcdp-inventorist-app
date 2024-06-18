import unittest
from unittest.mock import Mock, patch, MagicMock

from nose2.tools import params

from api.consume.gen.sale_offer.model.any_distribution_mode import AnyDistributionMode
from api.consume.gen.sale_offer.model.stock import Stock
from business.exceptions import CannotCreateSaleOffer, SaleOfferNotFoundByReference, CannotUpdateSaleOfferStatus
from business.models.product import Product
from business.models.sale_offer import SaleOffer
from business.models.update_policy import UpdatePolicy
from business.services.sale_offer import create_or_edit_sale_offer


class TestSaleOffer(unittest.TestCase):

    def setUp(self):
        self.search_sale_offer_patch = patch('business.services.sale_offer.get_search_sale_offer_api')
        self.manage_sale_offer_patch = patch('business.services.sale_offer.get_manage_sale_offer_api')
        self.distribution_to_dto_patch = patch('business.services.sale_offer.distribution_to_dto')
        self.stock_to_dto_patch = patch('business.services.sale_offer.stock_to_dto')
        self.get_api_key_patch = patch('business.services.sale_offer.get_api_key')

        search_sale_offer_mock = self.search_sale_offer_patch.start()
        manage_sale_offer_mock = self.manage_sale_offer_patch.start()
        distribution_to_dto_mock = self.distribution_to_dto_patch.start()
        stock_to_dto_mock = self.stock_to_dto_patch.start()
        get_api_key_patch_mock = self.get_api_key_patch.start()
        get_api_key_patch_mock.return_value = {}

        self.search_sale_offer_api = search_sale_offer_mock.return_value
        self.manage_sale_offer_api = manage_sale_offer_mock.return_value

        stock_to_dto_mock.return_value = Stock()
        distribution_to_dto_mock.return_value = AnyDistributionMode(type='QUOTATION', minimal_quantity=1,
                                                                    maximal_quantity=None, sold_by=1)

        self.mocked_product = MagicMock(Product)
        self.mocked_product.id = 1

        self.mocked_sale_offer = MagicMock(SaleOffer)
        self.mocked_sale_offer.product.principal_barcode = "My barcode"
        self.mocked_sale_offer.owner_id = 4
        self.mocked_sale_offer.description = "Ma description"
        self.mocked_sale_offer.rank = 90
        self.mocked_sale_offer.status = "enabled"

    def tearDown(self):
        self.search_sale_offer_patch.stop()
        self.manage_sale_offer_patch.stop()
        self.stock_to_dto_patch.stop()
        self.distribution_to_dto_patch.stop()
        self.get_api_key_patch.stop()

    @params(
        (Mock(SaleOffer), None),
        (None, Mock(Product)),
        (None, None),
    )
    def test_create_or_edit_sale_offer_with_none_product_or_sale_offer(self, sale_offer, product):
        with self.assertRaises(CannotCreateSaleOffer):
            create_or_edit_sale_offer({}, sale_offer, product, True)

    def test_create_or_edit_sale_offer_with_barcode_existing_sale_offer_found(self):
        expected = MagicMock(description="edit my sale offer")

        self.mocked_sale_offer.update_policy = UpdatePolicy.PRODUCT_BARCODE.value
        self.search_sale_offer_api.get_sale_offers.return_value = Mock(records=[MagicMock(description="My sale offer")])
        self.manage_sale_offer_api.create_sale_offer_version.return_value = expected

        result = create_or_edit_sale_offer({}, self.mocked_sale_offer, self.mocked_product, True)

        self.manage_sale_offer_api.create_sale_offer.assert_not_called()
        self.assertEqual(expected, result)

    def test_create_or_edit_sale_offer_with_barcode_existing_sale_offer_not_found(self):
        expected = MagicMock(description="create my sale offer")

        self.mocked_sale_offer.update_policy = UpdatePolicy.PRODUCT_BARCODE.value
        self.search_sale_offer_api.get_sale_offers.return_value = Mock(records=[])
        self.manage_sale_offer_api.create_sale_offer.return_value = expected

        result = create_or_edit_sale_offer({}, self.mocked_sale_offer, self.mocked_product, True)

        self.manage_sale_offer_api.create_sale_offer_version.assert_not_called()
        self.assertEqual(expected, result)

    def test_create_or_edit_sale_offer_with_barcode_existing_sale_offer_not_found_and_inability_to_create_sale_offer(
            self
    ):
        expected = MagicMock(description="create my sale offer")

        self.mocked_sale_offer.update_policy = UpdatePolicy.PRODUCT_BARCODE.value
        self.search_sale_offer_api.get_sale_offers.return_value = Mock(records=[])
        self.manage_sale_offer_api.create_sale_offer.return_value = expected

        with self.assertRaises(CannotCreateSaleOffer):
            create_or_edit_sale_offer({}, self.mocked_sale_offer, self.mocked_product, False)
            self.manage_sale_offer_api.create_sale_offer_version.assert_not_called()

    def test_create_or_edit_sale_offer_with_reference_existing_sale_offer_found(self):
        expected = MagicMock(description="edit my sale offer")

        self.mocked_sale_offer.update_policy = UpdatePolicy.SALE_OFFER_REFERENCE.value
        self.search_sale_offer_api.get_sale_offer.return_value = MagicMock(description="My sale offer")
        self.manage_sale_offer_api.create_sale_offer_version.return_value = expected

        result = create_or_edit_sale_offer({}, self.mocked_sale_offer, self.mocked_product, True)

        self.manage_sale_offer_api.create_sale_offer.assert_not_called()
        self.assertEqual(expected, result)

    def test_create_or_edit_sale_offer_with_reference_existing_sale_offer_not_found(self):
        self.mocked_sale_offer.update_policy = UpdatePolicy.SALE_OFFER_REFERENCE.value
        self.search_sale_offer_api.get_sale_offer.return_value = None

        with self.assertRaises(SaleOfferNotFoundByReference):
            create_or_edit_sale_offer({}, self.mocked_sale_offer, self.mocked_product, True)

    @patch("business.services.sale_offer.__find_existing_sale_offer")
    def test_create_or_edit_sale_offer_with_no_existing_sale_offer(self, find_existing_mock):
        expected = MagicMock(description="create my sale offer")
        find_existing_mock.return_value = None
        self.manage_sale_offer_api.create_sale_offer.return_value = expected
        result = create_or_edit_sale_offer({}, self.mocked_sale_offer, self.mocked_product, True)
        self.assertEqual(expected, result)

    @patch("business.services.sale_offer.__find_existing_sale_offer")
    def test_create_or_edit_sale_offer_with_no_existing_sale_offer_and_inability_to_create_sale_offer(
            self,
            find_existing_mock
    ):
        find_existing_mock.return_value = None
        with self.assertRaises(CannotCreateSaleOffer):
            create_or_edit_sale_offer({}, self.mocked_sale_offer, self.mocked_product, False)

    def test_create_or_edit_sale_offer_with_invalid_status(self):
        expected = MagicMock(description="My sale offer")

        self.mocked_sale_offer.status = 'invalid_status'
        self.search_sale_offer_api.get_sale_offers.return_value = Mock(records=[])
        self.manage_sale_offer_api.create_sale_offer.return_value = expected

        with self.assertRaises(CannotUpdateSaleOfferStatus):
            create_or_edit_sale_offer({}, self.mocked_sale_offer, self.mocked_product, True)
