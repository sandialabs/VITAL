class ConstantsGlobal:
    """
    A class to hold global constants related to the physical properties of the world.
    
    Attributes are immutable to prevent accidental modification outside of class definition.
    """
    
    rho: float = 1025.0         # Density of sea water (kg/m^3)
    Patm: float = 101325.0      # Atmospheric pressure at sea level (Pa)
    Pvap: float = 3063.7485     # Vapor pressure of sea water at 25 degrees Celsius (Pa)
    g: float = 9.8              # Acceleration due to gravity (m/s^2)
    
    def __setattr__(self, name: str, value) -> None:
        """
        Override the default __setattr__ method to prevent modification of class attributes.
        
        Parameters:
        - name (str): The name of the attribute.
        - value: The value attempting to be set.
        
        Raises:
        - AttributeError: If an attempt is made to set an attribute.
        """
        raise AttributeError(f"Can't reassign constant '{name}'")
