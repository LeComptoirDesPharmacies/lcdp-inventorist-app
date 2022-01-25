from business.models.errors import ProcessingError


class ProcessingException(Exception):
    def __init__(self, error):
        super().__init__()
        self.error = error


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
