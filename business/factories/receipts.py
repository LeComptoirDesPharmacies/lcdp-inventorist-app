from business.models.column import OverwriteColumn, Column


def add_update_policy(receipt, policy):
    return receipt + [
        OverwriteColumn("Politique de mise à jour", "sale_offer.update_policy", policy)
    ]


error_receipt = [
    Column("Erreur de saisie", "supervisor.errors")
]


create_laboratory_sale_offer_receipt = [
            Column("Classement produit sur le store", 'sale_offer.rank'),
            Column("CIP/ACL ou EAN", 'sale_offer.product.principal_barcode'),
            Column("Désignation - Nom du produit", 'sale_offer.product.name'),
            Column("Dénomination Commune Internationale ( DCI )", 'sale_offer.product.dci'),
            Column("Laboratoire", 'sale_offer.product.laboratory.name'),
            Column("Poid unitaire en gramme", 'sale_offer.product.weight'),
            Column("Type de produit", 'sale_offer.product.product_type.name'),
            Column("TVA", 'sale_offer.product.vat.value'),
            Column("Description produit", 'sale_offer.description'),
            Column("Distribution", 'sale_offer.distribution_type'),
            Column("Vendu par (nombre) - colisage", 'sale_offer.distribution.sold_by'),
            Column("Unité gratuite", 'sale_offer.distribution.free_unit'),
            Column("PU HT catalogue", 'sale_offer.product.unit_price'),
            Column("PU HT remisé", 'sale_offer.distribution.discounted_price'),
            Column("Identifiant vendeur", 'sale_offer.owner_id')
        ]
