from business.models.column import Column
from business.models.sale_offer import UNITARY_DISTRIBUTION
from business.models.update_policy import UpdatePolicy


error_mapper = [
    Column("Erreur de saisie", "supervisor.readable_errors")
]

# TODO: add column name and asterisk as constant ? But if one change should update all excel

create_laboratory_sale_offer_mapper = [
    Column("Classement produit sur le store**", 'sale_offer.rank'),
    Column("CIP/ACL ou EAN*", 'sale_offer.product.principal_barcode'),
    Column("Désignation - Nom du produit***", 'sale_offer.product.name'),
    Column("Dénomination Commune Internationale ( DCI )***", 'sale_offer.product.dci'),
    Column("Laboratoire***", 'sale_offer.product.laboratory.name'),
    Column("Poid unitaire en gramme (approximatif ) **", 'sale_offer.product.weight'),
    Column("Type de produit***", 'sale_offer.product.product_type.name'),
    Column("TVA***", 'sale_offer.product.vat.value'),
    Column("Description produit", 'sale_offer.description'),
    Column("Distribution*", 'sale_offer.distribution_type'),
    Column("Vendu par (nombre) - colisage*", 'sale_offer.distribution.sold_by'),
    Column("Unité gratuite", 'sale_offer.distribution.free_unit'),
    Column("PU HT catalogue***", 'sale_offer.product.unit_price'),
    Column("PU HT remisé*", 'sale_offer.distribution.discounted_price'),
    Column("Identifiant vendeur", 'sale_offer.owner_id'),
    Column("Politique de mise à jour", 'sale_offer.update_policy', UpdatePolicy.PRODUCT_BARCODE.value),
    Column("Synchronistation externe", 'sale_offer.product.external_sync', False)
]


create_update_product_mapper = [
    Column("CIP/ACL ou EAN*", 'sale_offer.product.principal_barcode'),
    Column("PU HT catalogue", 'sale_offer.product.unit_price'),
    Column("Désignation - Nom du produit", 'sale_offer.product.name'),
    Column("Dénomination Commune Internationale ( DCI )", 'sale_offer.product.dci'),
    Column("Laboratoire", 'sale_offer.product.laboratory.name'),
    Column("Poid unitaire en gramme (approximatif )", 'sale_offer.product.weight'),
    Column("Type de produit", 'sale_offer.product.product_type.name'),
    Column("TVA", 'sale_offer.product.vat.value'),
]


parameter_mapper = [
    Column("Sheet", "sheet_name"),
    Column("Header Line", "header_line"),
    Column("Content First Line", "content_start_line"),
]


create_update_drugstore_sale_offer_mapper = [
    Column("Référence annonce", 'sale_offer.reference'),
    Column("CIP/ACL ou EAN*", 'sale_offer.product.principal_barcode'),
    Column("Désignation - Nom du produit***", 'sale_offer.product.name'),
    Column("Dénomination Commune Internationale ( DCI )***", 'sale_offer.product.dci'),
    Column("Laboratoire***", 'sale_offer.product.laboratory.name'),
    Column("Poid unitaire en gramme (approximatif ) **", 'sale_offer.product.weight'),
    Column("Type de produit***", 'sale_offer.product.product_type.name'),
    Column("TVA***", 'sale_offer.product.vat.value'),
    Column("Date de péremption*", 'sale_offer.stock.lapsing_date'),
    Column("Distribution*", 'sale_offer.distribution_type', UNITARY_DISTRIBUTION),
    Column("N° de lot*", 'sale_offer.stock.batch'),
    Column("Vendu par (nombre) - colisage*", 'sale_offer.distribution.sold_by'),
    Column("Stock*", 'sale_offer.stock.remaining_quantity'),
    Column("PU HT catalogue***", 'sale_offer.product.unit_price'),
    Column("PU HT remisé*", 'sale_offer.distribution.discounted_price'),
    Column("Identifiant vendeur", 'sale_offer.owner_id'),
    Column("Politique de mise à jour", 'sale_offer.update_policy', UpdatePolicy.SALE_OFFER_REFERENCE.value),
]
