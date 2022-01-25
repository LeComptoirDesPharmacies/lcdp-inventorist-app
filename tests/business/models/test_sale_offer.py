import json
import unittest

from business.models.errors import CreateSaleOfferError
from business.models.sale_offer import SaleOffer, Range
from business.models.supervisor import Supervisor


def build_sale_offer(owner_id, rank, distribution_type):
    sale_offer = SaleOffer(Supervisor())
    sale_offer.owner_id = owner_id
    sale_offer.rank = rank
    sale_offer.distribution = distribution_type
    return sale_offer


class TestSaleOffer(unittest.TestCase):
    def test_sale_offer_minimal_instantiation(self):
        sale_offer = build_sale_offer(123, None, 'unitaire')
        expected = []
        result = sale_offer.rapport_errors()
        self.assertEqual(expected, result)

    def test_sale_offer_should_have_valid_owner_id(self):
        sale_offer = build_sale_offer('not_number_owner_id', None, 'unitaire')
        expected = [CreateSaleOfferError.INVALID_SELLER_ID]
        result = sale_offer.rapport_errors()
        self.assertEqual(expected, result)

    def test_sale_offer_should_have_owner_id_set(self):
        sale_offer = build_sale_offer(None, None, 'unitaire')
        expected = [CreateSaleOfferError.INVALID_SELLER_ID]
        result = sale_offer.rapport_errors()
        self.assertEqual(expected, result)

    def test_sale_offer_should_have_distribution_set(self):
        sale_offer = build_sale_offer(123, None, None)
        expected = [CreateSaleOfferError.INVALID_DISTRIBUTION]
        result = sale_offer.rapport_errors()
        self.assertEqual(expected, result)

    def test_sale_offer_can_be_merge(self):
        initial_sale_offer = build_sale_offer(123, None, 'palier')
        another_sale_offer = build_sale_offer(123, None, 'palier')
        initial_sale_offer.product.principal_barcode = 'barcode'
        another_sale_offer.product.principal_barcode = 'barcode'
        self.assertTrue(initial_sale_offer.should_merge(another_sale_offer))

    def test_sale_offer_cant_be_merge(self):
        initial_sale_offer = build_sale_offer(123, None, 'palier')
        another_sale_offer = build_sale_offer(123, None, 'palier')
        initial_sale_offer.product.principal_barcode = 'barcode'
        another_sale_offer.product.principal_barcode = 'new_barcode'
        self.assertFalse(initial_sale_offer.should_merge(another_sale_offer))

    #TODO: voir sur connexion comment c'était fait
    def test_sale_offer_cant_be_merge_2(self):
        initial_sale_offer = build_sale_offer(123, None, 'palier')
        another_sale_offer = build_sale_offer(123, None, 'unitaire')
        initial_sale_offer.product.principal_barcode = 'barcode'
        another_sale_offer.product.principal_barcode = 'new_barcode'
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




