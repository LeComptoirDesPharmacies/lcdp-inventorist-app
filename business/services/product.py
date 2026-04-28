import logging

from business.models.product import ProductType

# Build a case-insensitive lookup from display name to enum value
_DISPLAY_NAME_TO_ENUM_CI = {k.lower(): v for k, v in ProductType.DISPLAY_NAME_TO_ENUM.items()}
_ENUM_VALUES = set(ProductType.DISPLAY_NAME_TO_ENUM.values())


def get_product_type_enum_by_name(name):
    """Convert a product type display name to its enum value using local mapping.
    Returns the enum string (e.g. 'MEDICAMENT') or None if not found."""
    if name:
        # If the name is already an enum value, return it directly
        upper_name = name.upper()
        if upper_name in _ENUM_VALUES:
            return upper_name
        # Case-insensitive lookup of display name
        enum_value = _DISPLAY_NAME_TO_ENUM_CI.get(name.lower())
        if enum_value is None:
            logging.warning(f"Unknown product type name: {name}")
        return enum_value
    return None
