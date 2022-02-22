import filecmp
import json
import os
import unittest

from business.mappers.excel_mapper import parameter_mapper, create_laboratory_sale_offer_mapper, \
    create_update_drugstore_sale_offer_mapper
from business.models.excel_line import ExcelLine
from business.models.excel_parameter import ExcelParameter
from business.services.excel import excel_to_dict
from tests.constant import LABORATORY_SALE_OFFER_EXCEL, DRUGSTORE_SALE_OFFER_EXCEL
from tests.utils import generate_temp_json_file, compare_file_error_msg

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class TestExcel(unittest.TestCase):
    def test_excel_to_dict_with_parameters(self):
        my_dict = excel_to_dict(
            obj_class=ExcelParameter,
            excel_path=LABORATORY_SALE_OFFER_EXCEL,
            excel_mapper=parameter_mapper,
            sheet_name="Parametre",
            header_row=1,
            min_row=2,
            max_row=2
        )
        expected = json.dumps({"0": {"sheet_name": "Annonces", "header_line": 3, "content_start_line": 5}})
        result = json.dumps(my_dict, default=lambda x: x.__dict__)
        self.assertEqual(expected, result)

    def test_excel_to_dict_with_laboratory_sale_offers(self):
        my_dict = excel_to_dict(
            obj_class=ExcelLine,
            excel_path=LABORATORY_SALE_OFFER_EXCEL,
            excel_mapper=create_laboratory_sale_offer_mapper,
            sheet_name="Annonces",
            header_row=3,
            min_row=5,
            max_row=5
        )

        expected = open(os.path.join(CURRENT_DIR, 'resources/expected_laboratory_sale_offer.json'), "r")
        result = generate_temp_json_file(my_dict)
        expected.close()
        self.assertTrue(filecmp.cmp(expected.name, result.name), compare_file_error_msg(expected, result))

    def test_excel_to_dict_with_drugstore_sale_offers(self):
        my_dict = excel_to_dict(
            obj_class=ExcelLine,
            excel_path=DRUGSTORE_SALE_OFFER_EXCEL,
            excel_mapper=create_update_drugstore_sale_offer_mapper,
            sheet_name="Annonces",
            header_row=2,
            min_row=4,
            max_row=4
        )

        expected = open(os.path.join(CURRENT_DIR, 'resources/expected_drugstore_sale_offer.json'), "r")
        result = generate_temp_json_file(my_dict)
        expected.close()
        self.assertTrue(filecmp.cmp(expected.name, result.name), compare_file_error_msg(expected, result))
