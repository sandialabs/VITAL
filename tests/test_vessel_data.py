import numpy as np
import sys
import os
# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from module_vessel import VesselData
from constGlobal import ConstantsGlobal

def test_vessel_data():
    # Define turbine properties and flow profile
    Mturbine = 1000.0  # Example turbine weight (kg)
    Uinf = np.array([1.0, 1.5, 2.0, 2.5, 3.0])  # Example flow profile (m/s)
    Ft = np.array([100.0, 150.0, 200.0, 250.0, 300.0])  # Example thrust loads (N)

    # Test user-defined vessel properties
    user_vessel_properties = {
        'Xm': 5.77,
        'Zm': 1.65,
        'Kphi': 1.95e6,
        'theta': 45.0 * np.pi / 180.0,
        'phi': 10.0 * np.pi / 180.0,
        'area': 2.25,
        'Cd': 1.0
    }

    user_vessel = VesselData(
        user_defined=True,
        vessel_properties=user_vessel_properties
    )

    print("User-defined vessel properties:")
    print(f"Xm: {user_vessel.Xm:.2f} m")
    print(f"Zm: {user_vessel.Zm:.2f} m")
    print(f"Pitch Stiffness (Kphi): {user_vessel.Kphi:.2f} N*m/rad")
    print(f"Mooring Line Angle (theta): {user_vessel.theta_m:.2f} rad")
    print(f"Pitch Constraint (phi): {user_vessel.phi:.2f} rad")
    print(f"Reference Area: {user_vessel.area:.2f} m^2")
    print(f"Drag Coefficient (Cd): {user_vessel.Cd:.2f}")

    # Test rectangular vessel design
    rectangular_vessel = VesselData(
        height=0.5,
        density=500.0,
        theta_m=45 * np.pi / 180.0,
        alpha=4.0,
        Cd=0.25,
        phi=10 * np.pi / 180.0
    )

    rectangular_vessel.calculate_vessel_properties(Mturbine, Uinf, Ft)

    print("\nRectangular vessel properties:")
    print(f"Width: {rectangular_vessel.width:.2f} m")
    print(f"Mooring Force: {rectangular_vessel.Fmoor:.2f} N")
    print(f"Length: {rectangular_vessel.length:.2f} m")
    print(f"Hydrostatic Stiffness (Khs): {rectangular_vessel.Khs:.2f} N/m")
    print(f"Hydrostatic Stiffness in Roll (Kphi): {rectangular_vessel.Kphi:.2f} N*m/rad")
    print(f"Metacentric Height (GM): {rectangular_vessel.GM:.2f} m")
    print(f"Vessel Volume: {rectangular_vessel.VesselVolume:.2f} m^3")
    print(f"Submerged Height (h_s): {rectangular_vessel.h_s:.2f} m")


if __name__ == "__main__":
    test_vessel_data()
