import numpy as np
from constGlobal import ConstantsGlobal
GLOBAL = ConstantsGlobal()

class VesselData:
    """
    A class to represent the data and properties of a vessel.

    Attributes
    ----------
    height : float
        Height of the vessel.
    density : float
        Density of the vessel material.
    theta_m : float
        Mooring line angle in radians.
    alpha : float
        Aspect ratio for the vessel.
    Cd : float
        Drag coefficient.
    phi : float
        Pitch constraint in radians.
    user_defined : bool
        Flag indicating if the vessel properties are user-defined.
    vessel_properties : dict
        Dictionary containing user-defined vessel properties.
    width : float
        Width of the vessel.
    Fmoor : float
        Mooring force.
    length : float
        Length of the vessel.
    Khs : float
        Hydrostatic stiffness.
    Kphi : float
        Pitch hydrostatic stiffness.
    GM : float
        Metacentric height.
    VesselVolume : float
        Volume of the vessel.
    h_s : float
        Submerged height; Half of the vessel height.
    """

    def __init__(self, height=None, density=None, theta_m=None, alpha=None, Cd=None, phi=None, user_defined=False, vessel_properties=None):
        """
        Constructs all the necessary attributes for the VesselData object.

        Parameters
        ----------
        height : float, optional
            Height of the vessel (default is None).
        density : float, optional
            Density of the vessel material (default is None).
        theta_m : float, optional
            Mooring line angle in radians (default is None).
        alpha : float, optional
            Aspect ratio for the vessel (default is None).
        Cd : float, optional
            Drag coefficient (default is None).
        phi : float, optional
            Pitch constraint in radians (default is None).
        user_defined : bool, optional
            Flag indicating if the vessel properties are user-defined (default is False).
        vessel_properties : dict, optional
            Dictionary containing user-defined vessel properties (default is None).
        """
        self.height = height
        self.density = density
        self.theta_m = theta_m
        self.alpha = alpha
        self.Cd = Cd
        self.phi = phi
        self.user_defined = user_defined
        self.vessel_properties = vessel_properties or {}

        self.width = None
        self.Fmoor = None
        self.length = None
        self.Khs = None
        self.Kphi = None
        self.GM = None
        self.VesselVolume = None
        self.h_s = None

        if self.user_defined and self.vessel_properties:
            self.set_vessel_properties()
        else:
            self.set_default_properties()

    def set_vessel_properties(self):
        """
        Set vessel properties from user-defined vessel geometry.
        """
        try:
            self.Xm = self.vessel_properties['Xm']
            self.Zm = self.vessel_properties['Zm']
            self.Kphi = self.vessel_properties['Kphi']
            self.theta_m = self.vessel_properties['theta']
            self.phi = self.vessel_properties['phi']
            self.area = self.vessel_properties['area']
            self.Cd = self.vessel_properties['Cd']
        except KeyError as e:
            raise ValueError(f"Missing key in vessel_properties: {e}")

    def set_default_properties(self):
        """
        Set default properties for the vessel.
        """
        if self.height is None:
            self.height = 0.5  # Default height
        if self.density is None:
            self.density = 500.0  # Default density (kg/m^3)
        if self.theta_m is None:
            self.theta_m = 45.0 * np.pi / 180.0  # Default mooring line angle (radians)
        if self.alpha is None:
            self.alpha = 4.0  # Default alpha
        if self.Cd is None:
            self.Cd = 0.25  # Default drag coefficient
        if self.phi is None:
            self.phi = 10.0 * np.pi / 180.0  # Default pitch constraint (radians)
        self.h_s = self.height / 2

    def calculate_vessel_properties(self, mass_of_turbines, Uinf, Ft, number_of_turbines):
        """
        Calculate the vessel properties based on the given parameters.

        Parameters
        ----------
        mass_of_turbines : float
            Mass of the turbine.
        Uinf : array
            Array of flow speeds.
        Ft : array
            Array of thrust forces.
        number_of_turbines : int
            Number of turbines.
        """
        if self.user_defined:
            return  # Skip calculation if vessel properties are user-defined

        theta_m = self.theta_m
        alpha = self.alpha
        height = self.height
        rho_b = self.density
        Cd = self.Cd

        rho = GLOBAL.rho
        g = GLOBAL.g

        U = np.max(Uinf)
        total_mass_of_turbines = mass_of_turbines * number_of_turbines
        total_turbine_thrust_force = Ft[np.argmax(Uinf)] * number_of_turbines
        width_temp = height * (height * Cd**2 * U**4 * rho**2 * np.cos(theta_m)**2 + 
                               32 * total_mass_of_turbines * alpha * g**2 * rho * np.sin(theta_m)**2 - 
                               64 * total_mass_of_turbines * alpha * rho_b * g**2 * np.sin(theta_m)**2 + 
                               16 * total_turbine_thrust_force * alpha * np.sin(2 * theta_m) * g * rho - 
                               32 * total_turbine_thrust_force * alpha * rho_b * np.sin(2 * theta_m) * g)
        self.width = 0.25 * (np.sqrt(width_temp) + Cd * U**2 * height * rho * np.cos(theta_m)) / (np.sin(theta_m) * (alpha * g * height * rho - 2 * alpha * g * height * rho_b))
        self.Fmoor = (0.25 * Cd * height * rho * self.width * U**2 + total_turbine_thrust_force) / np.sin(theta_m)
        self.length = self.alpha * self.width
        self.Khs = rho * g * self.width * self.length
        self.VesselVolume = self.width * self.length * height

        V_submerged = self.width * self.length * self.h_s
        BM = ((self.length * self.width**3) / 12) / V_submerged
        zCOG = height / 2 - self.h_s
        zCOB = -self.h_s / 2
        self.GM = BM + zCOB - zCOG
        self.Kphi = rho * V_submerged * g * self.GM  # Pitch hydrostatic stiffness
        self.area = self.h_s * self.width

    def calculate_vessel_drag_force(self, Uinf):
        """
        Calculate the drag force exerted on the vessel.

        Parameters
        ----------
        Uinf : float
            Free stream velocity (m/s)

        Returns
        -------
        float
            The drag force exerted on the vessel (N)
        """
        rho = GLOBAL.rho

        return 0.5 * rho * self.Cd * self.area * Uinf**2

    def print_all_attributes(self):
        """
        Print all attributes of the VesselData object.
        """
        for attribute, value in vars(self).items():
            print(f"{attribute}: {value}")


    # def calculate_mooring_force(self, Uinf, Ft):
    #     """
    #     Calculate the time-domain mooring force.
        
    #     Parameters
    #     ----------
    #     Uinf : array
    #         Array of flow speeds.
    #     Ft : array
    #         Array of thrust forces.
        
    #     Returns
    #     -------
    #     array
    #         Mooring force values.
    #     """
    #     theta_m = self.theta_m
    #     height = self.height
    #     Cd = self.Cd
    #     width = self.width

    #     Fmoor = (0.25 * Cd * height * self.rho * width * Uinf**2 + Ft) / np.sin(theta_m)
    #     return Fmoor
