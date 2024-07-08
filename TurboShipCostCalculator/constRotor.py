class ConstantsRotor:
    """
    Constants for rotor properties.
    """
    
    density: float = 3000.0  # Density of aluminium used for the rotor (kg/m^3)

    def __setattr__(self, name: str, value) -> None:
        """
        Prevents modification of class attributes to ensure the integrity of constants.
        
        Parameters:
        - name (str): The name of the attribute attempting to be modified.
        - value: The value attempting to be set.
        
        Raises:
        - AttributeError: If an attempt is made to modify an attribute, indicating immutability.
        """
        raise AttributeError(f"Can't reassign constant '{name}'")
