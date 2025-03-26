import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from constGlobal import ConstantsGlobal

class TestConstantsGlobal(unittest.TestCase):
    def setUp(self):
        self.constants = ConstantsGlobal()

    def test_rho(self):
        self.assertEqual(self.constants.rho, 1025.0)

    def test_Patm(self):
        self.assertEqual(self.constants.Patm, 101325.0)

    def test_Pvap(self):
        self.assertEqual(self.constants.Pvap, 3063.7485)

    def test_g(self):
        self.assertEqual(self.constants.g, 9.8)

if __name__ == '__main__':
    unittest.main()
