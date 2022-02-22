from enum import Enum, auto, unique


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


@unique
class UpdatePolicy(AutoName):
    PRODUCT_BARCODE = auto()
    SALE_OFFER_REFERENCE = auto()
