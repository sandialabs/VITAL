class ConstantsLCOE:
    """
    A class to hold constants related to the Levelized Cost of Energy (LCOE) calculations.
    
    Attributes are immutable to prevent accidental modification outside of class definition.
    """
    
    eff: float = 0.9            # Generator efficiency
    sys_life: float = 20.0      # Life of the system in years
    interest_rate: float = 0.1  # Discount rate
    
    # Cabling cost parameters (based on Lopez table 7)
    A_cable: float = 50.0   
    E_cable: float = 0.5    
    
    # Grid connection cost (based on Lopez table 7)
    A_gridCon: float = 20.0 
    
    # Mooring cost (based on Lopez table 6)
    A_moor: float = 60.0    
    B_moor: float = 0.25    
    
    # Blade cost (based on Lopez table 14)
    A_blade: float = 0.004  
    
    # Generator cost (based on Lopez table 14)
    A_generator: float = 0.39   
    E_generator: float = 0.8    
    
    # Additional electrical components cost (based on Lopez table 6)
    switchgearCable: float = 8.0    
    controlRectifier: float = 25.0  
    
    # Farm hub platform costs (based on Lopez table 7)
    hub_SwitchGearCable: float = 10.0
    hub_Converter: float = 50.0
    hub_OffshoreSubstation: float = 80.0
    hub_OtherSystems: float = 8.0
    
    # Jacket structure cost (based on Lopez table 7)
    A_JacketStructure: float = 170.0    
    E_JacketStructure: float = 0.8  
    
    # Cable installation cost (based on Lopez table 7)
    A_cableInstall: float = 120.0   
    B1_cableInstall: float = 4.1 / 24   # knots
    B2_cableInstall: float = 2.3    # knots
    B3_cableInstall: float = 8.6    # knots
    
    # TEC Installation & Commissioning costs (based on Lopez table 16)
    A_dev: float = 0.05  # Development cost
    A_opex: float = 0.04  # Operational expenditure

    def __setattr__(self, name: str, value) -> None:
        """
        Prevents modification of class attributes to ensure constants remain unchanged.
        
        Parameters:
        - name (str): The name of the attribute.
        - value: The value attempting to be set.
        
        Raises:
        - AttributeError: If an attempt is made to set an attribute.
        """
        raise AttributeError(f"Can't reassign constant '{name}'")
