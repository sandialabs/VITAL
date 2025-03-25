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
        return 1 / (24.0 * 3600.0)  # second to days

    @property
    def mile2m(self):
        return 1609.34  # miles to meter

    @property
    def m2mile(self):
        return 1 / self.mile2m  # meter to miles

    @property
    def m2km(self):
        return 1e-3  # meter to kilometer

    @property
    def W2MW(self):
        return 1e-6  # Watt to MegaWatt

    @property
    def W2kW(self):
        return 1e-3  # Watt to kiloWatt

    @property
    def kE2E(self):
        return 1e3  # kilo euro to euro

    @property
    def N2mTon(self):
        return 1.019716e-4  # newton to metric tons

    @property
    def N2kN(self):
        return 1e-3  # newton to kilo newton

    @property
    def euro2dollar(self):
        return 1.26 * 1.1304  # euro to dollar

    @property
    def ft2m(self):
        return 0.3048  # feet to meter

    @property
    def cms2ms(self):
        return 1e-2  # cm/s to m/s

    @property
    def rads2rpm(self):
        return 60.0 / (2.0 * math.pi)  # rad/s to rpm

    @property
    def m32cm3(self):
        return 1e6  # cubic meter to cubic centimeter

    @property
    def hrs2days(self):
        return 1 / 24.0  # hours to days
