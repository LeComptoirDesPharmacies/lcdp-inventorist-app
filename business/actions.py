from business.constant import CREATE_LABORATORY_SALE_OFFER_TPL, CREATE_UPDATE_PRODUCT_TPL, \
    CREATE_UPDATE_DRUGSTORE_SALE_OFFER_TPL
from business.mappers.excel_lines_mapper import LaboratoryExcelLinesMapper, ProductExcelLinesMapper, \
    DrugstoreExcelLinesMapper

from business.services.excel import create_sale_offer_from_excel_lines, create_or_update_product_from_excel_lines

detailed_actions = {
    'CREATE_PHARMLAB_SALE_OFFER': {
     'name': 'Créer/Modifier des annonces PharmLab',
     'mapper': LaboratoryExcelLinesMapper,
     'executor': create_sale_offer_from_excel_lines,
     'template': CREATE_LABORATORY_SALE_OFFER_TPL
    },
    'CREATE_UPDATE_PRODUCT': {
     'name': 'Créer/Modifier des produits',
     'mapper': ProductExcelLinesMapper,
     'executor': create_or_update_product_from_excel_lines,
     'template': CREATE_UPDATE_PRODUCT_TPL
    },
    'CREATE_UPDATE_DESTOCK_SALE_OFFER': {
        'name': 'Créer/Modifier des annonces PharmDestock',
        'mapper': DrugstoreExcelLinesMapper,
        'executor': create_sale_offer_from_excel_lines,
        'template': CREATE_UPDATE_DRUGSTORE_SALE_OFFER_TPL
    }
}

simple_actions = list(map(lambda x: {'text': x[1]['name'], 'value': x[0]}, detailed_actions.items()))
