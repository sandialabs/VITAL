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
        return 1025.0  # Density of sea water (kg/m^3)

    @property
    def Patm(self):
        return 101325.0  # Atmospheric pressure at sea level (Pa)

    @property
    def Pvap(self):
        return 3063.7485  # Vapor pressure of sea water at 25 degrees Celsius (Pa)

    @property
    def g(self):
        return 9.8  # Acceleration due to gravity (m/s^2)
    
    @property
    def eff(self):
        return 0.9  # Acceleration due to gravity (m/s^2)
