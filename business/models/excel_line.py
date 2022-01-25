from business.models.errors import *
from business.models.sale_offer import SaleOffer
from business.models.supervisor import Supervisor


class ExcelLine:
    def __init__(self):
        self._supervisor = Supervisor()
        self._sale_offer = SaleOffer(self.supervisor)

    @property
    def sale_offer(self):
        return self._sale_offer

    @property
    def supervisor(self):
        return self._supervisor

    def can_create_sale_offer(self):
        return not self.supervisor.has_one_error_of(CreateSaleOfferError)

    def can_create_product_from_scratch(self):
        return not self.supervisor.has_one_error_of(CreateProductError) \
               and self.can_get_or_create_laboratory()

    def can_get_or_create_laboratory(self):
        return not self.supervisor.has_one_error_of(GetOrCreateLaboratoryError)
