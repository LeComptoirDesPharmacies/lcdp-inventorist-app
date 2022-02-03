from business.models.laboratory import Laboratory
from business.models.errors import CreateProductError, CreateSaleOfferError
import numbers

from business.models.supervisor import SupervisedEntity
from business.utils import cast_or_default


class ProductType:
    def __init__(self):
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name


class Vat(SupervisedEntity):
    def __init__(self, supervisor):
        super().__init__(supervisor)
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def report_errors(self):
        errors = []
        if not self.value or not isinstance(self.value, numbers.Number):
            errors.append(CreateProductError.INVALID_VAT)
        return errors


class Product(SupervisedEntity):

    def __init__(self, supervisor):
        super().__init__(supervisor)
        self._vat = Vat(supervisor)
        self._product_type = ProductType()
        self._laboratory = Laboratory(supervisor)
        self._principal_barcode = None
        self._name = None
        self._weight = None
        self._unit_price = None
        self._dci = None

    @property
    def principal_barcode(self):
        return self._principal_barcode

    @principal_barcode.setter
    def principal_barcode(self, principal_barcode):
        self._principal_barcode = cast_or_default(principal_barcode, str)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, weight):
        self._weight = cast_or_default(weight, float)

    @property
    def vat(self):
        return self._vat

    @property
    def product_type(self):
        return self._product_type

    @property
    def unit_price(self):
        return self._unit_price

    @unit_price.setter
    def unit_price(self, unit_price):
        self._unit_price = cast_or_default(unit_price, float)

    @property
    def dci(self):
        return self._dci

    @dci.setter
    def dci(self, dci):
        self._dci = dci

    @property
    def laboratory(self):
        return self._laboratory

    def report_errors(self):
        errors = []
        if not self.principal_barcode:
            errors.append(CreateSaleOfferError.INVALID_CIP)
        if self.weight and not isinstance(self.weight, numbers.Number):
            errors.append(CreateProductError.INVALID_WEIGHT)
        if not self.unit_price or not isinstance(self.unit_price, numbers.Number):
            errors.append(CreateProductError.INVALID_UNIT_PRICE)
        return errors
