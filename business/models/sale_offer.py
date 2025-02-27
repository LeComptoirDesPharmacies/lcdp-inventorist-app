from business.models.errors import CreateSaleOfferError
from business.models.product import Product
from business.models.stock import Stock
from business.models.supervisor import SupervisedEntity
import numbers

from business.utils import cast_or_default

UNITARY_DISTRIBUTION = 'unitaire'
RANGE_DISTRIBUTION = 'palier'
QUOTATION_DISTRIBUTION = 'devis'


class Range(SupervisedEntity):
    def __init__(self, supervisor):
        super().__init__(supervisor)
        self._sold_by = None
        self._discounted_price = None
        self._free_unit = None

    @property
    def sold_by(self):
        return self._sold_by

    @sold_by.setter
    def sold_by(self, sold_by):
        self._sold_by = sold_by

    @property
    def discounted_price(self):
        return self._discounted_price

    @discounted_price.setter
    def discounted_price(self, discounted_price):
        self._discounted_price = cast_or_default(discounted_price, float)

    @property
    def free_unit(self):
        return self._free_unit

    @free_unit.setter
    def free_unit(self, free_unit):
        self._free_unit = free_unit

    def is_valid_discounted_price(self):
        return self.discounted_price and isinstance(self.discounted_price, numbers.Number)

    def is_valid_sold_by(self):
        return self.sold_by and isinstance(self.sold_by, numbers.Number)

    def __eq__(self, obj):
        return isinstance(obj, Range) \
               and self.free_unit == obj.free_unit \
               and self.discounted_price == obj.discounted_price \
               and self.sold_by == obj.sold_by

    def report_errors(self):
        errors = []
        if not self.is_valid_discounted_price() or not self.is_valid_sold_by():
            errors.append(CreateSaleOfferError.INVALID_RANGE)
        return errors


# The problem is that I need to set distribution type before any other attribute otherwise
# my object will not be usable.
# Excel mapper should not be constructed depended on this issue
# TODO: Create a Draft class with all value of the excel and then create models objects
class Distribution(SupervisedEntity):

    def __init__(self, supervisor, distribution_type=None):
        super().__init__(supervisor)
        self._type = distribution_type
        self._sold_by = None
        self._maximal_quantity = None
        self._discounted_price = None
        self._free_unit = None
        if distribution_type == RANGE_DISTRIBUTION:
            self._ranges = [Range(self.supervisor)]
        else:
            self._ranges = []
        self._is_empty = True

    def __setattr__(self, name, value):
        super(Distribution, self).__setattr__(name, value)
        if name != '_is_empty' and value is not None:
            self._is_empty = False

    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, distribution_type):
        self._type = distribution_type
    
    @property
    def ranges(self):
        return self._ranges

    @ranges.setter
    def ranges(self, ranges):
        self._ranges = ranges
    
    @property
    def sold_by(self):
        if self.type == RANGE_DISTRIBUTION:
            return repr(list(map(lambda r: r.sold_by, self.ranges)))
        return self._sold_by

    @sold_by.setter
    def sold_by(self, sold_by):
        if self.type == RANGE_DISTRIBUTION:
            self.ranges[-1].sold_by = sold_by
        else:
            self._sold_by = sold_by

    @property
    def maximal_quantity(self):
        return self._maximal_quantity

    @maximal_quantity.setter
    def maximal_quantity(self, maximal_quantity):
        self._maximal_quantity = maximal_quantity

    @property
    def discounted_price(self):
        if self.type == RANGE_DISTRIBUTION:
            return repr(list(map(lambda r: r.discounted_price, self.ranges)))
        return self._discounted_price

    @discounted_price.setter
    def discounted_price(self, discounted_price):
        if self.type == RANGE_DISTRIBUTION:
            self.ranges[-1].discounted_price = cast_or_default(discounted_price, float)
        else:
            self._discounted_price = cast_or_default(discounted_price, float)

    @property
    def free_unit(self):
        if self.type == RANGE_DISTRIBUTION:
            return repr(list(map(lambda r: r.free_unit, self.ranges)))
        return self._free_unit

    @free_unit.setter
    def free_unit(self, free_unit):
        if self.type == RANGE_DISTRIBUTION:
            self.ranges[-1].free_unit = cast_or_default(free_unit, int, 0)
        else:
            self._free_unit = cast_or_default(free_unit, int, 0)

    def is_valid_maximal_quantity(self):
        return self.maximal_quantity is None or (self.maximal_quantity and isinstance(self.sold_by, numbers.Number))

    def report_errors(self):
        errors = []
        if not self.type or self.type not in [UNITARY_DISTRIBUTION, RANGE_DISTRIBUTION, QUOTATION_DISTRIBUTION]:
            errors.append(CreateSaleOfferError.INVALID_DISTRIBUTION)
        # Unitary
        if self.type and self.type == UNITARY_DISTRIBUTION:
            if not self.discounted_price or not isinstance(self.discounted_price, numbers.Number):
                errors.append(CreateSaleOfferError.INVALID_DISCOUNTED_PRICE)
            if not self.sold_by or not isinstance(self.sold_by, numbers.Number):
                errors.append(CreateSaleOfferError.INVALID_SOLD_BY)
            if not self.is_valid_maximal_quantity():
                errors.append(CreateSaleOfferError.INVALID_MAXIMAL_QUANTITY)
        if (self.discounted_price or self.maximal_quantity) and not self.sold_by:
            errors.append(CreateSaleOfferError.MISSING_SOLD_BY)
        if (self.sold_by or self.maximal_quantity) and not self.discounted_price:
            errors.append(CreateSaleOfferError.MISSING_DISCOUNTED_PRICE)
        return errors

    def is_empty(self):
        return self._is_empty

class SaleOffer(SupervisedEntity):

    def __init__(self, supervisor):
        super().__init__(supervisor)
        self._product = Product(supervisor)
        self._stock = Stock(supervisor)
        self._reference = None
        self._distribution_type = None
        self._distribution = None
        self._rank = None
        self._owner_id = None
        self._description = None
        self._status = None

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, reference):
        self._reference = cast_or_default(reference, str)

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, stock):
        self._stock = stock

    @property
    def owner_id(self):
        return self._owner_id

    @owner_id.setter
    def owner_id(self, owner_id):
        self._owner_id = owner_id

    @property
    def product(self):
        return self._product

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, rank):
        self._rank = rank

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def distribution_type(self):
        return self._distribution_type

    @distribution_type.setter
    def distribution_type(self, distribution_type):
        if distribution_type:
            self._distribution = Distribution(self.supervisor, distribution_type)
        else:
            self._distribution = Distribution(self.supervisor)
        self._distribution_type = distribution_type

    @property
    def distribution(self):
        return self._distribution

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    def should_merge(self, next_sale_offer):
        return self.distribution and \
                self.distribution.type == RANGE_DISTRIBUTION and \
                next_sale_offer.distribution and \
                next_sale_offer.distribution.type == RANGE_DISTRIBUTION and \
                self.product.principal_barcode == next_sale_offer.product.principal_barcode

    def merge(self, sale_offer):
        self.distribution.ranges.extend(sale_offer.distribution.ranges)

    def report_errors(self):
        errors = []
        if not self.owner_id or not isinstance(self.owner_id, numbers.Number):
            errors.append(CreateSaleOfferError.INVALID_SELLER_ID)
        if not self.distribution or not isinstance(self.distribution, Distribution):
            errors.append(CreateSaleOfferError.INVALID_DISTRIBUTION)
        return errors
