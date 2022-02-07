import unittest

from business.models.errors import GetOrCreateLaboratoryError
from business.models.supervisor import Supervisor
from business.models.laboratory import Laboratory


class TestLaboratory(unittest.TestCase):

    def test_laboratory_minimal_valid_instantiation(self):
        supervisor = Supervisor()
        laboratory = Laboratory(supervisor)
        laboratory.name = "my_laboratory_name"
        expected = []
        result = laboratory.report_errors()
        self.assertEqual(expected, result)

    def test_laboratory_should_have_name(self):
        supervisor = Supervisor()
        laboratory = Laboratory(supervisor)
        laboratory.name = None
        expected = [GetOrCreateLaboratoryError.INVALID_LABORATORY_NAME]
        result = laboratory.report_errors()
        self.assertEqual(expected, result)
