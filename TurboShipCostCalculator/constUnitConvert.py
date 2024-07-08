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
    
    sec2days: float = 1 / (24.0 * 3600.0)  # second to days
    mile2m: float = 1609.34                # miles to meter
    m2mile: float = 1 / mile2m             # meter to miles
    m2km: float = 1e-3                     # meter to kilometer
    W2MW: float = 1e-6                     # Watt to MegaWatt
    W2kW: float = 1e-3                     # Watt to kiloWatt
    kE2E: float = 1e3                      # kilo euro to euro
    N2mTon: float = 1.019716e-4            # newton to metric tons
    N2kN: float = 1e-3                     # newton to kilo newton
    euro2dollar: float = 1.26 * 1.1304     # euro to dollar
    ft2m: float = 0.3048                   # feet to meter
    cms2ms: float = 1e-2                   # cm/s to m/s
    rads2rpm: float = 60.0 / (2.0 * math.pi)  # rad/s to rpm
    m32cm3: float = 1e6                    # cubic meter to cubic centimeter
    hrs2days: float = 1 / 24.0             # hours to days

    def __setattr__(self, name: str, value) -> None:
        """
        Prevents reassignment of constants.
        
        Parameters:
        - name (str): The name of the attribute attempting to be modified.
        - value: The value attempting to be set.
        
        Raises:
        - AttributeError: If an attempt is made to modify an attribute, indicating immutability.
        """
        raise AttributeError(f"Can't reassign constant '{name}'")
