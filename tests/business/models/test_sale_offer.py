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
         },
        {
            'sale_offer_1': build_sale_offer(123, None, None),
            'sale_offer_2':  build_sale_offer(123, None, None),
            'sale_offer_1_code': 'barcode',
            'sale_offer_2_code': 'barcode'
         },
        {
            'sale_offer_1': SaleOffer(Supervisor()),
            'sale_offer_2':  SaleOffer(Supervisor()),
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

    def test_sale_offer_distribution_attribute_can_be_set_without_distribution_type(self):
        # The "Distribution*" column may be left empty while "Vendu par (nombre) - colisage*" is
        # filled : writing through sale_offer.distribution must not raise (LDS-6203).
        sale_offer = SaleOffer(Supervisor())
        sale_offer.owner_id = 123

        sale_offer.distribution.sold_by = 10

        self.assertEqual(10, sale_offer.distribution.sold_by)
        self.assertIsNone(sale_offer.distribution_type)

    def test_sale_offer_without_distribution_type_reports_invalid_distribution(self):
        sale_offer = SaleOffer(Supervisor())
        sale_offer.owner_id = 123
        sale_offer.distribution.sold_by = 10

        sale_offer.supervisor.identify_errors()

        errors = sale_offer.supervisor.errors
        self.assertEqual(1, errors.count(CreateSaleOfferError.INVALID_DISTRIBUTION))

    def test_sale_offer_distribution_type_keeps_the_distribution_empty(self):
        # The type may come from a mapper default: alone, it is not a value typed by the user, so
        # no distribution mode must be built from it (see excel.__build_distribution_mode).
        sale_offer = build_sale_offer(123, None, 'unitaire')
        self.assertTrue(sale_offer.distribution.is_empty())
        self.assertEqual('unitaire', sale_offer.distribution.type)

        sale_offer.distribution.sold_by = 10

        self.assertFalse(sale_offer.distribution.is_empty())

    def test_sale_offer_range_distribution_type_opens_a_first_range(self):
        sale_offer = build_sale_offer(123, None, 'palier')
        self.assertEqual(1, len(sale_offer.distribution.ranges))
        self.assertTrue(sale_offer.distribution.is_empty())

        sale_offer.distribution.sold_by = 10

        self.assertEqual(10, sale_offer.distribution.ranges[0].sold_by)
        self.assertFalse(sale_offer.distribution.is_empty())

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




