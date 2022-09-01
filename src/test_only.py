import unittest
from OnlyPython import *


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual(difference(11, 1), 2)
        self.assertEqual(difference(1, 6), 5)

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
