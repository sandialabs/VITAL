# import autograd.numpy as np  # Thinly-wrapped numpy
import math
# import autograd.numpy as np  # Thinly-wrapped numpy
import numpy as np

# # 36 ft fishing vessel
# FISH = {
#     'X_m' : 5.77,			# Horizontal distance from CG to mooring line [meter]
#     'Z_m' : 1.65,			# Vertical distance from CG to mooring line [meter]
#     'K_m' : 1.95e6,			# Pitch stiffness [N/rad]
#     'theta' : 45.0*np.pi/180, # Mooring line angle [radian]
#     'phi' : 10.0*np.pi/180,
#     'area' : 2.25,
#     'Cd' : 1.0,
# }

# # 100 ft barge 
# BARGE = {
#     'X_m' : 15.0,				# Horizontal distance from CG to mooring line [meter]
#     'Z_m' : 1.85,			# Vertical distance from CG to mooring line [meter]
#     'K_m' : 134.45e6,		# Pitch stiffness [N/rad]
#     'theta' : 45.0*np.pi/180,	# Mooring line angle [radian]
#     'phi' : 10.0*np.pi/180,
#     'area' : 15.03,
#     'Cd' : 1.0,
# }


# Convert degrees to radians for better readability
def degrees_to_radians(degrees):
    return degrees * np.pi / 180

# Updated dictionary template for vessels to include a name
def create_vessel(name, X_m, Z_m, K_m, theta_deg, phi_deg, area, Cd):
    return {
        'name': name,  # Name of the vessel
        'X_m': X_m,  # Horizontal distance from CG to mooring line [meter]
        'Z_m': Z_m,  # Vertical distance from CG to mooring line [meter]
        'K_m': K_m,  # Pitch stiffness [N/rad]
        'theta': degrees_to_radians(theta_deg),  # Mooring line angle [radian]
        'phi': degrees_to_radians(phi_deg),  # Vessel pitch constraint [radian]
        'area': area,  # Reference area for drag calculation [square meter]
        'Cd': Cd,  # Drag coefficient
    }

def print_vessel_details(dictionary):
    for key, value in dictionary.items():
        if key == 'phi' or key == 'theta':
            value = math.degrees(value)
        print(f"{key}: {value}")

# Define vessels using the updated template
FISH = create_vessel("Fish", 5.77, 1.65, 1.95e6, 45.0, 10.0, 2.25, 1.0)
BARGE = create_vessel("Barge", 15.0, 1.85, 134.45e6, 45.0, 10.0, 15.03, 1.0)

