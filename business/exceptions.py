from business.models.errors import ProcessingError


class ProcessingException(Exception):
    def __init__(self, error):
        super().__init__(error.value)


class TooManyProduct(ProcessingException):
    def __init__(self):
        super().__init__(ProcessingError.TOO_MANY_PRODUCT)


class VatNotFound(ProcessingException):
    def __init__(self):
        super().__init__(ProcessingError.VAT_NOT_FOUND)


class TooManyLaboratory(ProcessingException):
    def __init__(self):
        super().__init__(ProcessingError.TOO_MANY_LABORATORY)


class CannotCreateProduct(ProcessingException):
    def __init__(self):
        super().__init__(ProcessingError.CANNOT_CREATE_PRODUCT)


class CannotCreateSaleOffer(ProcessingException):
    def __init__(self):
        super().__init__(ProcessingError.CANNOT_CREATE_SALE_OFFER)


class SaleOfferNotFoundByReference(ProcessingException):
    def __init__(self):
        super().__init__(ProcessingError.CANNOT_UPDATE_SALE_OFFER_BY_REFERENCE)


class CannotUpdateSaleOfferStatus(ProcessingException):
    def __init__(self):
        super().__init__(ProcessingError.CANNOT_UPDATE_SALE_OFFER_STATUS)
