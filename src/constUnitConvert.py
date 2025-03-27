import math

class ConstantsUnitConversion:
    """
    A class to hold constants for various unit conversions.
    """
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConstantsUnitConversion, cls).__new__(cls)
        return cls._instance

    @property
    def sec2days(self):
        """Convert seconds to days"""
        return 1 / (24.0 * 3600.0)

    @property
    def mile2m(self):
        """Convert miles to meters"""
        return 1609.34

    @property
    def m2mile(self):
        """Convert meters to miles"""
        return 1 / self.mile2m

    @property
    def m2km(self):
        """Convert meters to kilometers"""
        return 1e-3

    @property
    def W2MW(self):
        """Convert Watts to MegaWatts"""
        return 1e-6

    @property
    def W2kW(self):
        """Convert Watts to kiloWatts"""
        return 1e-3

    @property
    def kE2E(self):
        """Convert kilo euros to euros"""
        return 1e3

    @property
    def N2mTon(self):
        """Convert Newtons to metric tons"""
        return 1.019716e-4

    @property
    def N2kN(self):
        """Convert Newtons to kilo Newtons"""
        return 1e-3

    @property
    def euro2dollar(self):
        """Convert euros to dollars"""
        return 1.26 * 1.1304

    @property
    def ft2m(self):
        """Convert feet to meters"""
        return 0.3048

    @property
    def cms2ms(self):
        """Convert cm/s to m/s"""
        return 1e-2

    @property
    def rads2rpm(self):
        """Convert rad/s to rpm"""
        return 60.0 / (2.0 * math.pi)

    @property
    def m32cm3(self):
        """Convert cubic meters to cubic centimeters"""
        return 1e6

    @property
    def hrs2days(self):
        """Convert hours to days"""
        return 1 / 24.0
