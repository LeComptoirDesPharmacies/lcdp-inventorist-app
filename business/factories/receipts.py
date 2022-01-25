from business.utils import rsetattr

create_laboratory_sale_offer_receipt = {
        0: lambda line, value: rsetattr(line, 'sale_offer.rank', value),
        1: lambda line, value: rsetattr(line, 'sale_offer.product.name', value),
        2: lambda line, value: rsetattr(line, 'sale_offer.product.dci', value),
        3: lambda line, value: rsetattr(line, 'sale_offer.product.principal_barcode', value),
        4: lambda line, value: rsetattr(line, 'sale_offer.product.laboratory.name', value),
        5: lambda line, value: rsetattr(line, 'sale_offer.product.weight', value),
        6: lambda line, value: rsetattr(line, 'sale_offer.product.product_type.name', value),
        7: lambda line, value: rsetattr(line, 'sale_offer.product.vat.value', value),
        8: lambda line, value: rsetattr(line, 'sale_offer.product.unit_price', value),
        9: lambda line, value: rsetattr(line, 'sale_offer.description', value),
        10: lambda line, value: rsetattr(line, 'sale_offer.distribution', value),
        11: lambda line, value: rsetattr(line, 'sale_offer.distribution.discounted_price', value),
        12: lambda line, value: rsetattr(line, 'sale_offer.distribution.sold_by', value),
        13: lambda line, value: rsetattr(line, 'sale_offer.distribution.free_unit', value),
        14: lambda line, value: rsetattr(line, 'sale_offer.owner_id', value),
    }