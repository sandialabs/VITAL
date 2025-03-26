class ConstantsGlobal:
    """
    A class to hold global constants related to the physical properties of the world.
    
    Attributes are immutable to prevent accidental modification outside of class definition.
    """
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConstantsGlobal, cls).__new__(cls)
        return cls._instance

    @property
    def rho(self):
        """Density of sea water (kg/m^3)"""
        return 1025.0

    @property
    def Patm(self):
        """Atmospheric pressure at sea level (Pa)"""
        return 101325.0

    @property
    def Pvap(self):
        """Vapor pressure of sea water at 25 degrees Celsius (Pa)"""
        return 3063.7485

    @property
    def g(self):
        """Acceleration due to gravity (m/s^2)"""
        return 9.8
