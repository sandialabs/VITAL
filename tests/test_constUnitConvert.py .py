import unittest
import sys
import os
import math

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from constUnitConvert import ConstantsUnitConversion

class TestConstantsUnitConversion(unittest.TestCase):
    def setUp(self):
        self.constants = ConstantsUnitConversion()

    def test_sec2days(self):
        self.assertAlmostEqual(self.constants.sec2days, 1 / (24.0 * 3600.0))

    def test_mile2m(self):
        self.assertEqual(self.constants.mile2m, 1609.34)

    def test_m2mile(self):
        self.assertAlmostEqual(self.constants.m2mile, 1 / 1609.34)

    def test_m2km(self):
        self.assertEqual(self.constants.m2km, 1e-3)

    def test_W2MW(self):
        self.assertEqual(self.constants.W2MW, 1e-6)

    def test_W2kW(self):
        self.assertEqual(self.constants.W2kW, 1e-3)

    def test_kE2E(self):
        self.assertEqual(self.constants.kE2E, 1e3)

    def test_N2mTon(self):
        self.assertEqual(self.constants.N2mTon, 1.019716e-4)

    def test_N2kN(self):
        self.assertEqual(self.constants.N2kN, 1e-3)

    def test_euro2dollar(self):
        self.assertAlmostEqual(self.constants.euro2dollar, 1.26 * 1.1304)

    def test_ft2m(self):
        self.assertEqual(self.constants.ft2m, 0.3048)

    def test_cms2ms(self):
        self.assertEqual(self.constants.cms2ms, 1e-2)

    def test_rads2rpm(self):
        self.assertAlmostEqual(self.constants.rads2rpm, 60.0 / (2.0 * math.pi))

    def test_m32cm3(self):
        self.assertEqual(self.constants.m32cm3, 1e6)

    def test_hrs2days(self):
        self.assertAlmostEqual(self.constants.hrs2days, 1 / 24.0)

if __name__ == '__main__':
    unittest.main()
