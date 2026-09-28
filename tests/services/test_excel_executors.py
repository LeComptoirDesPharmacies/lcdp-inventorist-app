import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from openpyxl import load_workbook

import business.services.excel as excel
from business.mappers.excel_lines_mapper import LaboratoryExcelLinesMapper, DrugstoreExcelLinesMapper
from tests.constant import LABORATORY_SALE_OFFER_EXCEL, DRUGSTORE_SALE_OFFER_EXCEL


class Recorder:
    """Stands in for a generated API model: keeps what the executor built."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Vat:
    id = 42


def blank_cells(excel_path, sheet_name, header_row, content_row, column_names):
    """Copy the workbook to a temp file with the given cells of one content row emptied."""
    temp_path = os.path.join(tempfile.mkdtemp(), os.path.basename(excel_path))
    shutil.copy(excel_path, temp_path)
    wb = load_workbook(temp_path)
    ws = wb[sheet_name]
    for col in range(1, ws.max_column + 1):
        if ws.cell(header_row, col).value in column_names:
            ws.cell(content_row, col).value = None
    wb.save(temp_path)
    return temp_path


class TestExcelExecutors(unittest.TestCase):
    """The executors turn mapped lines into assembly records: check the distributionMode they build."""

    def run_executor(self, executor, lines):
        manage_assembly_api = MagicMock()
        distribution_modes = []

        def from_dict(distribution_mode):
            # Validate through the generated model, but keep the plain dict so the test can read it.
            real_from_dict(distribution_mode)
            distribution_modes.append(distribution_mode)
            return distribution_mode

        real_from_dict = excel.AnyDistributionMode.from_dict
        with patch.object(excel, 'get_manage_assembly_api', return_value=manage_assembly_api), \
                patch.object(excel, 'get_current_user_id', return_value=1), \
                patch.object(excel, 'get_api_key', return_value='api-key'), \
                patch.object(excel, 'get_vat_by_value', return_value=Vat()), \
                patch.object(excel, 'AssemblyCreationParameters', Recorder), \
                patch.object(excel, 'AnyFactory', Recorder), \
                patch.object(excel, 'SaleOfferUpsertFactoryAllOfRecords', Recorder), \
                patch.object(excel, 'OfferPlanificationFactoryAllOfRecords', Recorder), \
                patch.object(excel.AnyDistributionMode, 'from_dict', side_effect=from_dict):
            executor(lines, filename='import.xlsx')

        assemblies = {}
        for call in manage_assembly_api.create_assembly.call_args_list:
            factory = call.args[0].kwargs['factory'].args[0]
            assemblies[factory['sellerId']] = [record.kwargs for record in factory['records']]
        return assemblies

    def test_laboratory_sale_offer_upsert_builds_one_distribution_mode_per_type(self):
        lines = LaboratoryExcelLinesMapper(LABORATORY_SALE_OFFER_EXCEL).map_to_obj()

        assemblies = self.run_executor(excel.sale_offer_upsert_from_excel_lines, lines)

        records = assemblies[12]
        self.assertEqual(4, len(records))
        self.assertEqual({
            'type': 'RANGE',
            'ranges': [
                {'quantity': 20, 'unitPrice': 20.0, 'freeUnits': 10},
                {'quantity': 10, 'unitPrice': 10.0, 'freeUnits': 5},
            ],
            'minimalQuantity': 1,
            'maximalQuantity': None,
        }, records[0]['distributionMode'])
        self.assertEqual({
            'type': 'QUOTATION', 'soldBy': 6, 'minimalQuantity': 1, 'maximalQuantity': None,
        }, records[1]['distributionMode'])
        self.assertEqual({
            'type': 'UNITARY', 'unitPrice': 13.5225, 'soldBy': 6, 'minimalQuantity': 1, 'maximalQuantity': 12,
        }, records[2]['distributionMode'])
        self.assertEqual({
            'type': 'UNITARY', 'unitPrice': 20.0, 'soldBy': 6, 'minimalQuantity': 1, 'maximalQuantity': None,
        }, records[3]['distributionMode'])

    def test_offer_planification_builds_the_same_distribution_modes(self):
        lines = LaboratoryExcelLinesMapper(LABORATORY_SALE_OFFER_EXCEL).map_to_obj()

        upsert = self.run_executor(excel.sale_offer_upsert_from_excel_lines, lines)
        planification = self.run_executor(excel.create_offer_planificiation_from_excel_lines, lines)

        self.assertEqual([record['distributionMode'] for record in upsert[12]],
                         [record['distributionMode'] for record in planification[12]])

    def test_drugstore_sale_offer_upsert_defaults_to_unitary(self):
        # The drugstore template has no "Distribution*" column: the mapper default applies.
        lines = DrugstoreExcelLinesMapper(DRUGSTORE_SALE_OFFER_EXCEL).map_to_obj()

        assemblies = self.run_executor(excel.sale_offer_upsert_from_excel_lines, lines)

        records = assemblies[999]
        self.assertEqual(4, len(records))
        self.assertEqual(['UNITARY'] * 4, [record['distributionMode']['type'] for record in records])
        self.assertEqual({
            'type': 'UNITARY', 'unitPrice': 5.0, 'soldBy': 30, 'minimalQuantity': 1, 'maximalQuantity': 12,
        }, records[2]['distributionMode'])
        self.assertEqual('2103302923', records[2]['reference'])

    def test_drugstore_line_without_any_distribution_value_sends_no_distribution_mode(self):
        # Only the defaulted type is known: nothing typed by the user, so nothing must be sent.
        excel_path = blank_cells(DRUGSTORE_SALE_OFFER_EXCEL, 'Annonces', header_row=2, content_row=4, column_names=(
            'Vendu par (nombre) - colisage*', 'Quantité maximale (contingentement)', 'PU HT remisé*'))
        lines = DrugstoreExcelLinesMapper(excel_path).map_to_obj()

        assemblies = self.run_executor(excel.sale_offer_upsert_from_excel_lines, lines)

        records = assemblies[999]
        self.assertEqual(4, len(records))
        self.assertNotIn('distributionMode', records[0])
        self.assertEqual('2103302923', records[0]['reference'])
        self.assertEqual(['UNITARY'] * 3, [record['distributionMode']['type'] for record in records[1:]])

    def test_laboratory_line_without_distribution_type_does_not_stop_the_import(self):
        # LDS-6203: "Distribution*" left empty while the other distribution columns are filled used
        # to raise an AttributeError and abort the whole import. The line now goes to the assembly
        # without a distributionMode, the other lines are untouched.
        excel_path = blank_cells(LABORATORY_SALE_OFFER_EXCEL, 'Annonces', header_row=3, content_row=7,
                                 column_names=('Distribution*',))
        lines = LaboratoryExcelLinesMapper(excel_path).map_to_obj()

        with self.assertLogs(level='WARNING') as logs:
            assemblies = self.run_executor(excel.sale_offer_upsert_from_excel_lines, lines)

        records = assemblies[12]
        self.assertEqual(4, len(records))
        self.assertNotIn('distributionMode', records[2])
        self.assertEqual('3492270078112', records[2]['product']['principal_barcode'])
        self.assertEqual(1, len(logs.output))
        self.assertIn('3492270078112', logs.output[0])
        self.assertIn('unknown distribution type None', logs.output[0])
        self.assertEqual(['RANGE', 'QUOTATION', 'UNITARY'],
                         [records[i]['distributionMode']['type'] for i in (0, 1, 3)])
