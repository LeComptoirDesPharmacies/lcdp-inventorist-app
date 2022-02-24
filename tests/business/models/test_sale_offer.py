import unittest

from business.models.errors import CreateSaleOfferError
from business.models.sale_offer import SaleOffer, Range
from business.models.supervisor import Supervisor

from nose2.tools import params


def build_sale_offer(owner_id, rank, distribution_type):
    sale_offer = SaleOffer(Supervisor())
    sale_offer.owner_id = owner_id
    sale_offer.rank = rank
    sale_offer.distribution_type = distribution_type
    return sale_offer


class TestSaleOffer(unittest.TestCase):
    def test_sale_offer_minimal_instantiation(self):
        sale_offer = build_sale_offer(123, None, 'unitaire')
        expected = []
        result = sale_offer.report_errors()
        self.assertEqual(expected, result)

    def test_sale_offer_should_have_valid_owner_id(self):
        sale_offer = build_sale_offer('not_number_owner_id', None, 'unitaire')
        expected = [CreateSaleOfferError.INVALID_SELLER_ID]
        result = sale_offer.report_errors()
        self.assertEqual(expected, result)

    def test_sale_offer_should_have_owner_id_set(self):
        sale_offer = build_sale_offer(None, None, 'unitaire')
        expected = [CreateSaleOfferError.INVALID_SELLER_ID]
        result = sale_offer.report_errors()
        self.assertEqual(expected, result)

    def test_sale_offer_can_be_merge(self):
        initial_sale_offer = build_sale_offer(123, None, 'palier')
        another_sale_offer = build_sale_offer(123, None, 'palier')
        initial_sale_offer.product.principal_barcode = 'barcode'
        another_sale_offer.product.principal_barcode = 'barcode'
        self.assertTrue(initial_sale_offer.should_merge(another_sale_offer))

    @params(
        {
            'sale_offer_1': build_sale_offer(123, None, 'palier'),
            'sale_offer_2':  build_sale_offer(123, None, 'palier'),
            'sale_offer_1_code': 'barcode',
            'sale_offer_2_code': 'new_barcode'
        },
        {
            'sale_offer_1': build_sale_offer(123, None, 'palier'),
            'sale_offer_2':  build_sale_offer(123, None, 'unitaire'),
            'sale_offer_1_code': 'barcode',
            'sale_offer_2_code': 'barcode'
         }
    )
    def test_sale_offer_cant_be_merge(self, sale_offers_dict):
        initial_sale_offer = sale_offers_dict['sale_offer_1']
        another_sale_offer = sale_offers_dict['sale_offer_2']
        initial_sale_offer.product.principal_barcode = sale_offers_dict['sale_offer_1_code']
        another_sale_offer.product.principal_barcode = sale_offers_dict['sale_offer_2_code']
        self.assertFalse(initial_sale_offer.should_merge(another_sale_offer))

    def test_sale_offer_merge(self):
        initial_sale_offer = build_sale_offer(123, None, 'palier')
        another_sale_offer = build_sale_offer(123, None, 'palier')

        range_1 = Range(Supervisor())
        range_1.sold_by = 1
        range_1.discounted_price = 123
        range_2 = Range(Supervisor())
        range_2.sold_by = 2
        range_2.discounted_price = 456
        initial_sale_offer.distribution.sold_by = range_1.sold_by
        initial_sale_offer.distribution.discounted_price = range_1.discounted_price
        another_sale_offer.distribution.sold_by = range_2.sold_by
        another_sale_offer.distribution.discounted_price = range_2.discounted_price

        initial_sale_offer.merge(another_sale_offer)

        expected = [range_1, range_2]
        result = initial_sale_offer.distribution.ranges

        self.assertEqual(expected, result)




