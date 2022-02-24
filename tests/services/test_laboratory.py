import unittest
from unittest.mock import patch, MagicMock

from business.exceptions import TooManyLaboratory
from business.services.laboratory import find_or_create_laboratory


class TestLaboratory(unittest.TestCase):

    def setUp(self):
        self.search_patch = patch('business.services.laboratory.get_search_laboratory_api')
        self.manage_patch = patch('business.services.laboratory.get_manage_laboratory_api')
        search_mock = self.search_patch.start()
        manage_mock = self.manage_patch.start()
        self.search_api = search_mock.return_value
        self.manage_api = manage_mock.return_value

    def tearDown(self) -> None:
        self.search_patch.stop()
        self.manage_patch.stop()

    def test_find_or_create_laboratory_with_none_name(self):
        laboratory_name = None
        result = find_or_create_laboratory(laboratory_name)
        self.assertIsNone(result)

    def test_find_or_create_laboratory_with_existing_laboratory(self):
        laboratory_name = "my existing laboratory name"
        expected = {"name": laboratory_name}
        self.search_api.get_laboratories.return_value = MagicMock(records=[expected])
        result = find_or_create_laboratory(laboratory_name)

        self.manage_api.create_laboratory.assert_not_called()
        self.assertEqual(expected, result)

    def test_find_or_create_laboratory_with_not_existing_laboratory(self):
        laboratory_name = "my not existing laboratory name"
        expected = {"name": laboratory_name}
        self.manage_api.create_laboratory.return_value = expected

        result = find_or_create_laboratory(laboratory_name)

        self.search_api.get_laboratories.assert_called_once()
        self.assertEqual(expected, result)

    def test_find_or_create_laboratory_with_too_much_existing_laboratory(self):
        laboratory_name = "my existing two laboratory name"
        two_labs = [{"name": "fist laboratory"}, {"name": "second laboratory"}]
        self.search_api.get_laboratories.return_value = MagicMock(records=two_labs)
        with self.assertRaises(TooManyLaboratory):
            find_or_create_laboratory(laboratory_name)
