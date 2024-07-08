import math
import numpy as np

def degrees_to_radians(degrees: float) -> float:
    """
    Convert degrees to radians.
    
    Parameters:
    - degrees (float): Angle in degrees.
    
    Returns:
    - float: Angle in radians.
    """
    return degrees * np.pi / 180

def create_vessel(name: str, X_m: float, Z_m: float, K_m: float, theta_deg: float, phi_deg: float, area: float, Cd: float) -> dict:
    """
    Create a dictionary representing a vessel with given properties.
    
    Parameters:
    - name (str): Name of the vessel.
    - X_m (float): Horizontal distance from CG to mooring line [meter].
    - Z_m (float): Vertical distance from CG to mooring line [meter].
    - K_m (float): Pitch stiffness [N/rad].
    - theta_deg (float): Mooring line angle [degrees].
    - phi_deg (float): Vessel pitch constraint [degrees].
    - area (float): Reference area for drag calculation [square meter].
    - Cd (float): Drag coefficient.
    
    Returns:
    - dict: Dictionary containing vessel properties.
    """
    return {
        'name': name,  
        'X_m': X_m,  
        'Z_m': Z_m,  
        'K_m': K_m,  
        'theta': degrees_to_radians(theta_deg),  
        'phi': degrees_to_radians(phi_deg),  
        'area': area,  
        'Cd': Cd,  
    }

def print_vessel_details(vessel: dict) -> None:
    """
    Print the details of a vessel.
    
    Parameters:
    - vessel (dict): Dictionary containing vessel properties.
    """
    for key, value in vessel.items():
        if key in ['phi', 'theta']:
            value = math.degrees(value)
        print(f"{key}: {value}")

# Define vessels using the updated template
FISH = create_vessel("Fish", 5.77, 1.65, 1.95e6, 45.0, 10.0, 2.25, 1.0)
BARGE = create_vessel("Barge", 15.0, 1.85, 134.45e6, 45.0, 10.0, 15.03, 1.0)

# # 36 ft fishing vessel
# FISH = {
#     'X_m' : 5.77, # Horizontal distance from CG to mooring line [meter]
#     'Z_m' : 1.65, # Vertical distance from CG to mooring line [meter]
#     'K_m' : 1.95e6, # Pitch stiffness [N/rad]
#     'theta' : 45.0*np.pi/180, # Mooring line angle [radian]
#     'phi' : 10.0*np.pi/180,
#     'area' : 2.25,
#     'Cd' : 1.0,
# }

# # 100 ft barge 
# BARGE = {
#     'X_m' : 15.0, # Horizontal distance from CG to mooring line [meter]
#     'Z_m' : 1.85, # Vertical distance from CG to mooring line [meter]
#     'K_m' : 134.45e6, # Pitch stiffness [N/rad]
#     'theta' : 45.0*np.pi/180,	# Mooring line angle [radian]
#     'phi' : 10.0*np.pi/180,
#     'area' : 15.03,
#     'Cd' : 1.0,
# }
