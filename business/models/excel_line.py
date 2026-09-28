from business.models.sale_offer import SaleOffer


class ExcelLine:
    def __init__(self):
        self._sale_offer = SaleOffer()

    @property
    def sale_offer(self):
        return self._sale_offer
