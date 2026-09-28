from enum import Enum


class ProcessingError(Enum):
    TOO_MANY_PRODUCT = 'Plusieurs produits sont lié à ce cip'
    TOO_MANY_LABORATORY = 'Plusieurs laboratoires sont lié à ce nom'
    TOO_MANY_PRODUCT_INSIGHT = 'Plusieurs fiches catalogues sont lié à ce produit'
    VAT_NOT_FOUND = "La TVA saisi n'a pas été trouvé"
    FAILED_TO_CREATE_LABORATORY = "Impossible de créer ce laboratoire"
    CANNOT_CREATE_PRODUCT = "Produit non trouvé avec ce cip et impossible de le créer"
    CANNOT_CREATE_SALE_OFFER = "Annonce non trouvé et impossible de la créer"
    CANNOT_UPDATE_SALE_OFFER_BY_REFERENCE = "Annonce non trouvé avec la référence donnée, mise à jour impossible"
    CANNOT_UPDATE_SALE_OFFER_STATUS = "Impossible de modifier le status de l'annonce"
