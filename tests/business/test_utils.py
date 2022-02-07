import unittest

from business.utils import cast_or_default, rsetattr, rgetattr


class A:
    def __init__(self):
        self.prop1 = 1
        self.prop2 = "2"
        self.class_b = B()


class B:
    def __init__(self, prop1=3):
        self.prop1 = prop1
        self.prop2 = 4


class TestUtils(unittest.TestCase):

    def test_cast_or_default_with_none_value(self):
        result = cast_or_default(None, str)
        self.assertIsNone(result)

    def test_cast_or_default_with_invalid_value(self):
        result = cast_or_default('Hello', float)
        self.assertIsNone(result)

    def test_cast_or_default(self):
        expected = 12
        result = cast_or_default(12.23, int)
        self.assertEqual(expected, result)

    def test_rsetattr(self):
        class_a = A()
        expected = 6
        rsetattr(class_a, 'class_b.prop2', expected)
        result = class_a.class_b.prop2
        self.assertEqual(expected, result)

    def test_rgetattr(self):
        class_a = A()
        expected = class_a.class_b.prop1
        result = rgetattr(class_a, 'class_b.prop1')
        self.assertEqual(expected, result)
