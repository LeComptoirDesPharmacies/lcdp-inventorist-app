import json
import unittest

from business.mappers.excel_lines_mapper import LaboratoryExcelLinesMapper
from tests.constant import LABORATORY_SALE_OFFER_EXCEL
from tests.utils import to_json


class TestExcelLinesFactory(unittest.TestCase):
    maxDiff = None

    def test_laboratory_excel_lines_builder(self):
        builder = LaboratoryExcelLinesMapper(LABORATORY_SALE_OFFER_EXCEL)
        file = open('resources/expected_laboratory_excel_lines_builder.json', "r")
        expected = json.loads(file.read())
        file.close()
        result = json.loads(json.dumps(builder.map_to_obj(), default=to_json))
        self.assertEqual(expected, result)

