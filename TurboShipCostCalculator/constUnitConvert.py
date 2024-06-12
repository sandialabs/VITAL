## https://www.exchangerates.org.uk/EUR-USD-spot-exchange-rates-history-2017.html
# Best exchange rate: 1.2035 USD on 09 Sep 2017. 
# Average exchange rate in 2017: 1.1304 USD. 
# Worst exchange rate: 1.0418 USD on 03 Jan 2017.
## inflation calculator
# https://www.usinflationcalculator.com/
# $1 in 2017 = $1.26 in 2024

import math

class ConstantsUnitConversion:
    """
    A class to hold constants for various unit conversions.
    """
    sec2days = 1/(24.0*3600.0)      # second to days
    mile2m = 1609.34            # miles to meter
    m2mile = 1/mile2m         	# meter to miles
    m2km = 1e-3                 # meter to kilometer
    W2MW = 1e-6                 # Watt to MegaWatt
    W2kW = 1e-3                 # Watt to kiloWatt
    kE2E = 1e3                  # kilo euro to euro
    N2mTon = 1.019716e-4        # newton to metric tons
    N2kN = 1e-3                 # newton to kilo newton
    euro2dollar = 1.26*1.1304   # euro to dollar
    ft2m = 0.3048               # feet to meter
    cms2ms = 1e-2               # cm/s to m/s
    rads2rpm = 60.0/(2.0*math.pi)     # rad/s to rpm
    m32cm3 = 1e+6				# cubic meter to cubic centimeter
    hrs2days = 1/24.0             # hours to days

    def __setattr__(self, name, value):
        """
        Prevents reassignment of constants.
        """
        raise AttributeError(f"can't reassign constant '{name}'")