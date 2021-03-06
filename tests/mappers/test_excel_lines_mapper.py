import os
import unittest
import filecmp

from business.mappers.excel_lines_mapper import LaboratoryExcelLinesMapper, ProductExcelLinesMapper, \
    DrugstoreExcelLinesMapper
from tests.constant import LABORATORY_SALE_OFFER_EXCEL, IMPORT_PRODUCT_EXCEL, DRUGSTORE_SALE_OFFER_EXCEL
from tests.utils import generate_temp_json_file, compare_file_error_msg

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class TestExcelLinesMapper(unittest.TestCase):
    maxDiff = None

    def test_laboratory_excel_lines_mapper(self):
        mapper = LaboratoryExcelLinesMapper(LABORATORY_SALE_OFFER_EXCEL)

        result = generate_temp_json_file(mapper.map_to_obj())

        expected = open(os.path.join(CURRENT_DIR, 'resources', 'expected_laboratory_excel_lines_mapper.json'), "r")
        expected.close()
        self.assertTrue(filecmp.cmp(expected.name, result.name), compare_file_error_msg(expected, result))

    def test_product_excel_lines_mapper(self):
        mapper = ProductExcelLinesMapper(IMPORT_PRODUCT_EXCEL)

        result = generate_temp_json_file(mapper.map_to_obj())

        expected = open(os.path.join(CURRENT_DIR, 'resources', 'expected_product_excel_lines_mapper.json'), "r")
        expected.close()
        self.assertTrue(filecmp.cmp(expected.name, result.name), compare_file_error_msg(expected, result))

    def test_drugstore_excel_lines_mapper(self):
        mapper = DrugstoreExcelLinesMapper(DRUGSTORE_SALE_OFFER_EXCEL)

        result = generate_temp_json_file(mapper.map_to_obj())

        expected = open(os.path.join(CURRENT_DIR, 'resources', 'expected_drugstore_excel_lines_mapper.json'), "r")
        expected.close()
        self.assertTrue(filecmp.cmp(expected.name, result.name), compare_file_error_msg(expected, result))
