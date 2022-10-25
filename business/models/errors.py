from enum import Enum


class GetOrCreateLaboratoryError(Enum):
    INVALID_LABORATORY_NAME = "Nom du laboratoire invalide"


class CreateProductError(Enum):
    INVALID_PRODUCT_NAME = 'Nom de produit invalide'
    INVALID_VAT = 'T.V.A invalide'
    INVALID_UNIT_PRICE = 'Prix unitaire du produit invalide'
    INVALID_WEIGHT = 'Poids invalide'


class CreateSaleOfferError(Enum):
    INVALID_DISTRIBUTION = 'Type de distribution invalide'
    INVALID_REMAINING_QUANTITY = 'Stock invalide'
    INVALID_LAPSING_DATE = 'Date de péremption invalide'
    INVALID_BATCH = 'Numéro de lot invalide'
    INVALID_SELLER_ID = 'Identifiant vendeur est invalide'
    INVALID_RANGE = 'Un ou plusieurs palier sont invalide'
    INVALID_DISCOUNTED_PRICE = 'Prix remisé invalide'
    INVALID_SOLD_BY = 'Le colisage est invalide'
    INVALID_CIP = 'CIP invalide'


class ProcessingError(Enum):
    TOO_MANY_PRODUCT = 'Plusieurs produits sont lié à ce cip'
    TOO_MANY_LABORATORY = 'Plusieurs laboratoires sont lié à ce nom'
    VAT_NOT_FOUND = "La TVA saisi n'a pas été trouvé"
    FAILED_TO_CREATE_LABORATORY = "Impossible de créer ce laboratoire"
    CANNOT_CREATE_PRODUCT = "Produit non trouvé avec ce cip et impossible de le créer"
    CANNOT_CREATE_SALE_OFFER = "Annonce non trouvé et impossible de la créer"
    CANNOT_UPDATE_SALE_OFFER_BY_REFERENCE = "Annonce non trouvé avec la référence donnée, mise à jour impossible"
    CANNOT_UPDATE_SALE_OFFER_STATUS = "Impossible de modifier le status de l'annonce"
