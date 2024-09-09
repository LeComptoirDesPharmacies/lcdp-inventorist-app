from business.constant import CREATE_LABORATORY_SALE_OFFER_TPL, CREATE_UPDATE_PRODUCT_TPL, \
    CREATE_UPDATE_DRUGSTORE_SALE_OFFER_TPL
from business.mappers.excel_lines_mapper import LaboratoryExcelLinesMapper, ProductExcelLinesMapper, \
    DrugstoreExcelLinesMapper

from business.services.excel import create_offer_planificiation_from_excel_lines, \
    sale_offer_upsert_from_excel_lines, \
    product_upsert_from_excel_lines

detailed_actions = {
    'CREATE_PHARMLAB_SALE_OFFER': {
        'name': 'Créer/Modifier des annonces PharmLab',
        'mapper': LaboratoryExcelLinesMapper,
        'executor': create_offer_planificiation_from_excel_lines,
        'template': CREATE_LABORATORY_SALE_OFFER_TPL
    },
    'CREATE_UPDATE_PRODUCT': {
        'name': 'Créer/Modifier des produits',
        'mapper': ProductExcelLinesMapper,
        'executor': product_upsert_from_excel_lines,
        'template': CREATE_UPDATE_PRODUCT_TPL
    },
    'CREATE_UPDATE_DESTOCK_SALE_OFFER': {
        'name': 'Créer/Modifier des annonces PharmDestock',
        'mapper': DrugstoreExcelLinesMapper,
        'executor': sale_offer_upsert_from_excel_lines,
        'template': CREATE_UPDATE_DRUGSTORE_SALE_OFFER_TPL
    }
}

simple_actions = list(map(lambda x: {'text': x[1]['name'], 'value': x[0]}, detailed_actions.items()))
