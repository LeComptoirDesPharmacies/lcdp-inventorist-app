import json
import os
import unittest

from business.mappers.excel_lines_mapper import LaboratoryExcelLinesMapper, ProductExcelLinesMapper
from tests.constant import LABORATORY_SALE_OFFER_EXCEL, IMPORT_PRODUCT_EXCEL
from tests.utils import to_json

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class TestExcelLinesMapper(unittest.TestCase):
    maxDiff = None

    def test_laboratory_excel_lines_mapper(self):
        mapper = LaboratoryExcelLinesMapper(LABORATORY_SALE_OFFER_EXCEL)
        file = open(os.path.join(CURRENT_DIR, 'resources/expected_laboratory_excel_lines_mapper.json'), "r")
        # Permet de réécrire le json de test si le mapper évolue
        # file.write(json.dumps(mapper.map_to_obj(), default=to_json, indent=4))
        expected = json.loads(file.read())
        file.close()
        result = json.loads(json.dumps(mapper.map_to_obj(), default=to_json))
        self.assertEqual(expected, result)

    def test_product_excel_lines_mapper(self):
        mapper = ProductExcelLinesMapper(IMPORT_PRODUCT_EXCEL)
        file = open(os.path.join(CURRENT_DIR, 'resources/expected_product_excel_lines_mapper.json'), "r")
        # Permet de réécrire le json de test si le mapper évolue
        # file.write(json.dumps(mapper.map_to_obj(), default=to_json, indent=4))
        expected = json.loads(file.read())
        file.close()
        result = json.loads(json.dumps(mapper.map_to_obj(), default=to_json))
        self.assertEqual(expected, result)


