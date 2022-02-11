import unittest

from business.models.errors import CreateSaleOfferError, CreateProductError
from business.models.product import Product, Vat
from business.models.supervisor import Supervisor


def build_product(principal_barcode, name, weight, unit_price, dci):
    product = Product(Supervisor())
    product.principal_barcode = principal_barcode
    product.name = name
    product.weight = weight
    product.unit_price = unit_price
    product.dci = dci
    return product


class TestProduct(unittest.TestCase):

    def test_product_minimal_valid_instantiation(self):
        product = build_product('barcode', None, None, 123, None)
        expected = []
        result = product.report_errors()
        self.assertEqual(expected, result)

    def test_product_should_have_valid_principal_barcode(self):
        product = build_product(None, 'product_name', 123, 123, 'my_dci')
        expected = [CreateSaleOfferError.INVALID_CIP]
        result = product.report_errors()
        self.assertEqual(expected, result)

    def test_product_should_have_valid_weight(self):
        product = build_product('barcode', 'product_name', 'not_number_weight', 123, 'my_dci')
        expected = []
        result = product.report_errors()
        self.assertEqual(expected, result)

    def test_product_should_have_unit_price_set(self):
        product = build_product('barcode', None, None, None, None)
        expected = [CreateProductError.INVALID_UNIT_PRICE]
        result = product.report_errors()
        self.assertEqual(expected, result)

    def test_product_should_have_valid_unit_price(self):
        product = build_product('barcode', None, None, 'not_number_unit_price', None)
        expected = [CreateProductError.INVALID_UNIT_PRICE]
        result = product.report_errors()
        self.assertEqual(expected, result)

    def test_vat_minimal_valid_instantiation(self):
        vat = Vat(Supervisor())
        vat.value = 2.3
        expected = []
        result = vat.report_errors()
        self.assertEqual(expected, result)

    def test_vat_should_have_value_set(self):
        vat = Vat(Supervisor())
        vat.value = None
        expected = [CreateProductError.INVALID_VAT]
        result = vat.report_errors()
        self.assertEqual(expected, result)

    def test_vat_should_have_valid_value(self):
        vat = Vat(Supervisor())
        vat.value = 'not_number_value'
        expected = [CreateProductError.INVALID_VAT]
        result = vat.report_errors()
        self.assertEqual(expected, result)

