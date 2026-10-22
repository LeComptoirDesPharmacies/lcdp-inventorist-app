from business.models.product import Product
from business.models.stock import Stock
from business.utils import cast_or_default

UNITARY_DISTRIBUTION = 'unitaire'
RANGE_DISTRIBUTION = 'palier'
QUOTATION_DISTRIBUTION = 'devis'


class Range:
    def __init__(self):
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

    def __eq__(self, obj):
        return isinstance(obj, Range) \
               and self.free_unit == obj.free_unit \
               and self.discounted_price == obj.discounted_price \
               and self.sold_by == obj.sold_by


# The problem is that I need to set distribution type before any other attribute otherwise
# my object will not be usable.
# Excel mapper should not be constructed depended on this issue
# TODO: Create a Draft class with all value of the excel and then create models objects
class Distribution:
    # The values a user can type. Everything else (type, ranges) is structural: the type may come
    # from a mapper default, so it must not make the distribution non-empty.
    VALUE_FIELDS = ('sold_by', 'maximal_quantity', 'discounted_price', 'free_unit')

    def __init__(self, distribution_type=None):
        self._is_empty = True
        self._sold_by = None
        self._maximal_quantity = None
        self._discounted_price = None
        self._free_unit = None
        self.type = distribution_type

    def __setattr__(self, name, value):
        super(Distribution, self).__setattr__(name, value)
        if name in self.VALUE_FIELDS and value is not None:
            self._is_empty = False

    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, distribution_type):
        self._type = distribution_type
        # A range distribution starts with one range, the values are written into the last one.
        self._ranges = [Range()] if distribution_type == RANGE_DISTRIBUTION else []
    
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

    def is_empty(self):
        return self._is_empty

class SaleOffer:

    def __init__(self):
        self._product = Product()
        self._stock = Stock()
        self._reference = None
        # Always present: the excel mapper writes through this link ('sale_offer.distribution.sold_by')
        # even when the column carrying the distribution type is empty, in which case the type setter
        # never runs. A typeless Distribution is sent without distribution mode instead of crashing on None.
        self._distribution = Distribution()
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
        return self._distribution.type

    @distribution_type.setter
    def distribution_type(self, distribution_type):
        self._distribution.type = distribution_type or None

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
        return self.distribution.type == RANGE_DISTRIBUTION and \
                next_sale_offer.distribution.type == RANGE_DISTRIBUTION and \
                self.product.principal_barcode == next_sale_offer.product.principal_barcode

    def merge(self, sale_offer):
        self.distribution.ranges.extend(sale_offer.distribution.ranges)
