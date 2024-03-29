import numbers
import datetime

from business.models.errors import CreateSaleOfferError
from business.models.supervisor import SupervisedEntity
from business.utils import cast_datetime_to_date, cast_or_default


class Stock(SupervisedEntity):

    def __init__(self, supervisor):
        super().__init__(supervisor)
        self._remaining_quantity = None
        self._lapsing_date = None
        self._batch = None
        self._is_empty = True

    def __setattr__(self, name, value):
        super(Stock, self).__setattr__(name, value)
        if name != '_is_empty' and value is not None:
            self._is_empty = False

    @property
    def remaining_quantity(self):
        return self._remaining_quantity

    @remaining_quantity.setter
    def remaining_quantity(self, remaining_quantity):
        self._remaining_quantity = remaining_quantity

    @property
    def lapsing_date(self):
        return self._lapsing_date

    @lapsing_date.setter
    def lapsing_date(self, lapsing_date):
        self._lapsing_date = cast_datetime_to_date(lapsing_date)

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, batch):
        self._batch = cast_or_default(batch, str)

    def is_empty(self):
        return self._is_empty

    def report_errors(self):
        errors = []
        if self.remaining_quantity and not isinstance(self.remaining_quantity, numbers.Number):
            errors.append(CreateSaleOfferError.INVALID_REMAINING_QUANTITY)

        if self.lapsing_date and not isinstance(self.lapsing_date, datetime.date):
            errors.append(CreateSaleOfferError.INVALID_LAPSING_DATE)

        return errors


