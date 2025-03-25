import numpy as np
from constGlobal import ConstantsGlobal

class ConstraintChecker:
    def __init__(self, Radius, CpminFunc):
        self.Radius = Radius
        self.CpminFunc = CpminFunc
        self.GLOBAL = ConstantsGlobal()
        self.rho = self.GLOBAL.rho
        self.g = self.GLOBAL.g
        self.Pvap = self.GLOBAL.Pvap
        self.Patm = self.GLOBAL.Patm

    def depth_constraint(self, dHub):
        """
        Check if the rotor is fully submerged.
        
        Parameters:
        - dHub: Array of hub depths.
        
        Returns:
        - Array: Depth constraint values (must be greater than 0 to be valid).
        """
        return dHub - self.Radius

    def check_depth_constraint(self, dHub):
        """
        Check if the depth constraint is satisfied.
        
        Parameters:
        - dHub: Array of hub depths.
        
        Returns:
        - bool: True if the depth constraint is satisfied, False otherwise.
        """
        return np.all(self.depth_constraint(dHub) > 0)

    def cavitation_constraint(self, TSR, Uinf_adjusted, RotorSpeed, dHub):
        """
        Check for cavitation constraints.
        
        Parameters:
        - TSR: Array of TSR values.
        - Uinf_adjusted: Array of adjusted flow speeds.
        - RotorSpeed: Array of rotor speeds.
        - dHub: Array of hub depths.
        
        Returns:
        - Array: Cavitation constraint values (must be greater than 0 to be valid).
        """
        Vinf = np.sqrt(Uinf_adjusted**2 + (self.Radius * RotorSpeed)**2)
        Pinf = self.Patm + self.rho * self.g * (dHub - self.Radius)
        Cpmin = self.CpminFunc(TSR)
        return 0.5 * self.rho * Vinf**2 * Cpmin - (self.Pvap - Pinf)

    def check_cavitation_constraint(self, TSR, Uinf_adjusted, RotorSpeed, dHub):
        """
        Check if the cavitation constraint is satisfied.
        
        Parameters:
        - TSR: Array of TSR values.
        - Uinf_adjusted: Array of adjusted flow speeds.
        - RotorSpeed: Array of rotor speeds.
        - dHub: Array of hub depths.
        
        Returns:
        - bool: True if the cavitation constraint is satisfied, False otherwise.
        """
        return np.all(self.cavitation_constraint(TSR, Uinf_adjusted, RotorSpeed, dHub) > 0)

    def check_pitch_stiffness_constraint(self, vessel):
        """
        Check if the pitch stiffness constraint is satisfied.
        
        Parameters:
        - vessel: VesselData object.
        
        Returns:
        - bool: True if the pitch stiffness constraint is satisfied, False otherwise.
        """
        if vessel.user_defined:
            return True  # Skip check if vessel is user-defined
        return vessel.GM > 0

    def pitch_constraint(self, vessel, Uinf, Ft, dHub):
        """
        Check for pitch constraints.
        
        Parameters:
        - vessel: VesselData object.
        - Uinf: Array of flow speeds.
        - Ft: Array of thrust forces.
        - dHub: Array of hub depths.
        
        Returns:
        - Array: Pitch constraint values (must be greater than 0 to be valid).
        """
        if vessel.user_defined:
            return self.user_defined_pitch_constraint(vessel, Uinf, Ft, dHub)
        else:
            return self.designed_pitch_constraint(vessel, Uinf, Ft)

    def designed_pitch_constraint(self, vessel, Uinf, Ft):
        """
        Check for pitch constraints for a designed vessel.
        
        Parameters:
        - vessel: VesselData object.
        - Uinf: Array of flow speeds.
        - Ft: Array of thrust forces.
        
        Returns:
        - Array: Pitch constraint values (must be greater than 0 to be valid).
        """
        theta_m = vessel.theta_m
        height = vessel.height
        Cd = vessel.Cd
        phi = vessel.phi
        width = vessel.width
        Kphi = vessel.Kphi

        Fmoor = (0.25 * Cd * height * self.rho * width * Uinf**2 + Ft) / np.sin(theta_m)

        h_s = vessel.h_s
        Fdrag = 0.5 * self.rho * Cd * Uinf**2 * width * h_s
        Fbuoy = self.rho * self.g * vessel.VesselVolume

        MomentEquation = (Fmoor * np.cos(theta_m) * vessel.length / 2 + Ft * height / 2 + Fdrag * (height / 2 - h_s / 2) - Fbuoy * (height / 2 - h_s / 2))

        return Kphi * phi - MomentEquation

    def user_defined_pitch_constraint(self, vessel, Uinf, Ft, dHub):
        """
        Check for pitch constraints for a user-defined vessel.
        
        Parameters:
        - vessel: VesselData object.
        - Uinf: Array of flow speeds.
        - Ft: Array of thrust forces.
        - dHub: Array of hub depths.
        
        Returns:
        - Array: Pitch constraint values (must be greater than 0 to be valid).
        """
        F_vessel_thrust = 0.5 * self.rho * vessel.Cd * vessel.area * Uinf**2
        F_turbine_thrust = Ft
        F_total = F_vessel_thrust + F_turbine_thrust

        ConstraintOut = (vessel.Kphi * vessel.phi - F_turbine_thrust * dHub
                         - F_total * vessel.X_m * np.cos(vessel.theta_m)
                         - F_total * vessel.Z_m * np.sin(vessel.theta_m))

        return ConstraintOut

    def check_pitch_constraint(self, vessel, Uinf, Ft, dHub):
        """
        Check if the pitch constraint is satisfied.
        
        Parameters:
        - vessel: VesselData object.
        - Uinf: Array of flow speeds.
        - Ft: Array of thrust forces.
        - dHub: Array of hub depths.
        
        Returns:
        - bool: True if the pitch constraint is satisfied, False otherwise.
        """
        return np.all(self.pitch_constraint(vessel, Uinf, Ft, dHub) > 0)

