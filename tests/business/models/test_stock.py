import unittest
import datetime

from nose2.tools import params

from business.models.errors import CreateSaleOfferError
from business.models.supervisor import Supervisor
from business.models.stock import Stock


class TestLaboratory(unittest.TestCase):

    def test_complete_stock_valid_instantiation(self):
        supervisor = Supervisor()
        stock = Stock(supervisor)
        stock.lapsing_date = datetime.datetime.today()
        stock.remaining_quantity = 1
        stock.batch = 'BATCH'
        expected = []
        result = stock.report_errors()
        self.assertEqual(expected, result)

    def test_unset_stock_valid_instantiation(self):
        supervisor = Supervisor()
        stock = Stock(supervisor)
        expected = []
        result = stock.report_errors()
        self.assertEqual(expected, result)

    @params(
        (datetime.datetime.today(), None, 'BATCH', [CreateSaleOfferError.INVALID_REMAINING_QUANTITY]),
        (datetime.datetime.today(), 1, None, [CreateSaleOfferError.INVALID_BATCH]),
        (None, 1, 'BATCH', [CreateSaleOfferError.INVALID_LAPSING_DATE]),
        (None, None, 'BATCH', [CreateSaleOfferError.INVALID_REMAINING_QUANTITY,
                               CreateSaleOfferError.INVALID_LAPSING_DATE]),
        (datetime.datetime.today(), None, None, [CreateSaleOfferError.INVALID_REMAINING_QUANTITY,
                                             CreateSaleOfferError.INVALID_BATCH]),
        (None, 1, None, [CreateSaleOfferError.INVALID_LAPSING_DATE, CreateSaleOfferError.INVALID_BATCH]),
    )
    def test_invalid_stock_when_one_attribute_is_none(self, lapsing_date, remaining_quantity, batch, expected):
        supervisor = Supervisor()
        stock = Stock(supervisor)
        stock.lapsing_date = lapsing_date
        stock.remaining_quantity = remaining_quantity
        stock.batch = batch
        expected = expected
        result = stock.report_errors()
        self.assertEqual(expected, result)
