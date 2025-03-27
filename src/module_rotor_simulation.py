import numpy as np
from constGlobal import ConstantsGlobal
import scipy as sp

class RotorSimulation:
    def __init__(self, config):
        self.Radius = config['Radius']
        self.Prated = config['Prated']
        self.dCable = config['dCable']
        self.dMoor = config['dMoor']
        self.Uinf = config['Uinf']
        self.t = config['t']
        self.CpFunc = config['CpFunc']
        self.CqFunc = config['CqFunc']
        self.CtFunc = config['CtFunc']
        self.CpOpt = config['CpOpt']
        self.TSROpt = config['TSROpt']
        self.TSRmax = config['TSRmax']
        self.Umin = config['Umin']
        self.withBrake = config['withBrake']
        self.control_strategy = config['control_strategy']
        self.attachment_method = config['attachment_method']
        self.turbine_efficiency = config['efficiency']

        self.GLOBAL = ConstantsGlobal()
        self.Jr = 1000000
        self.M_turbine = self.UnitWeight(self.Radius, self.Prated)
        self.Wturbine = self.M_turbine * self.GLOBAL.g
        self.Kopt = self.calculate_Kopt()

        self.initialize_results()

        if self.control_strategy == 'constant_speed':
            self.optimal_speed = self.find_optimal_constant_speed()

        if self.attachment_method == 'solid_bar':
            self.theta_turbine = np.zeros(np.shape(self.t))
            self.dHub = np.ones(np.shape(self.t)) * self.dCable
            self.Uinf_adjusted = self.flowAtDepth(self.Uinf, self.Radius, self.dHub, self.dMoor)

    def initialize_results(self):
        self.w = np.zeros(np.shape(self.t))
        self.wd = np.zeros(np.shape(self.t))
        self.TSR = np.zeros(np.shape(self.t))
        self.Tc = np.zeros(np.shape(self.t))
        self.Th = np.zeros(np.shape(self.t))
        self.Tbrake = np.zeros(np.shape(self.t))
        self.Ft = np.zeros(np.shape(self.t))
        self.Uinf_adjusted = np.zeros(np.shape(self.t))
        self.dHub = np.zeros(np.shape(self.t))
        self.theta_turbine = np.zeros(np.shape(self.t))

    def simulate(self):
        dt = np.mean(np.diff(self.t))

        for kk in range(len(self.t)):
            if self.attachment_method == 'cable':
                self.adjust_hub_depth(kk)

            if self.control_strategy == 'optimal':
                self.simulate_optimal_control(kk, dt)
            elif self.control_strategy == 'constant_speed':
                self.simulate_constant_speed(kk, dt)
                # print('This is constant speed')

        self.calculate_power()

    def adjust_hub_depth(self, kk):
        if kk == 0:
            self.dHub[kk] = self.dCable
            self.theta_turbine[kk] = 0
        else:
            self.theta_turbine[kk] = np.atan(self.Ft[kk-1] / self.Wturbine)
            self.dHub[kk] = self.dCable * np.cos(self.theta_turbine[kk])

        self.Uinf_adjusted[kk] = self.flowAtDepth(self.Uinf[kk], self.Radius, self.dHub[kk], self.dMoor)

    def simulate_optimal_control(self, kk, dt):
        if kk == 0:
            self.w[kk] = self.TSROpt * self.Uinf_adjusted[kk] / self.Radius
        else:
            self.w[kk] = self.w[kk-1] + self.wd[kk-1] * dt

        if self.Uinf_adjusted[kk] != 0:
            self.TSR[kk] = min(self.w[kk] * self.Radius / self.Uinf_adjusted[kk], self.TSRmax)
        else:
            self.TSR[kk] = 0

        self.Th[kk] = self.calculate_hydro_torque(self.Radius, self.Uinf_adjusted[kk], self.CqFunc(self.TSR[kk]))
        self.Tc[kk] = self.Kopt * self.w[kk]**2

        if self.Tc[kk] * self.w[kk] * self.turbine_efficiency > self.Prated:
            self.Tc[kk] = (self.Prated / self.turbine_efficiency) / self.w[kk]

        if self.Uinf_adjusted[kk] < self.Umin:
            self.Tc[kk] = 0

        if self.withBrake:
            self.Tbrake[kk] = (self.w[kk]**2 * self.Kopt) - self.Tc[kk]

        self.Ft[kk] = self.calculate_thrust_force(self.Radius, self.Uinf_adjusted[kk], self.CtFunc(self.TSR[kk]))

        self.wd[kk] = 1 / self.Jr * (self.Th[kk] - self.Tc[kk] - self.Tbrake[kk])

    def simulate_constant_speed(self, kk, dt):
        if kk == 0:
            self.w[kk] = self.optimal_speed
            print(f'Optimal Speed is {self.optimal_speed}')
        else:
            self.w[kk] = self.w[kk-1] + self.wd[kk-1] * dt

        if self.Uinf_adjusted[kk] != 0:
            self.TSR[kk] = min(self.w[kk] * self.Radius / self.Uinf_adjusted[kk], self.TSRmax)
        else:
            self.TSR[kk] = 0

        self.Th[kk] = self.calculate_hydro_torque(self.Radius, self.Uinf_adjusted[kk], self.CqFunc(self.TSR[kk]))
        self.Tc[kk] = self.Th[kk]  # Required to keep speed constant

        if self.Tc[kk] * self.w[kk] * self.turbine_efficiency > self.Prated:
            self.Tc[kk] = (self.Prated / self.turbine_efficiency) / self.w[kk]

        if self.Uinf_adjusted[kk] < self.Umin:
            self.Tc[kk] = 0

        if self.withBrake:
            self.Tbrake[kk] = self.Th[kk] - self.Tc[kk]

        self.Ft[kk] = self.calculate_thrust_force(self.Radius, self.Uinf_adjusted[kk], self.CtFunc(self.TSR[kk]))

        self.wd[kk] = 1 / self.Jr * (self.Th[kk] - self.Tc[kk] - self.Tbrake[kk])

    def calculate_Kopt(self):
        return 0.5 * self.GLOBAL.rho * (np.pi * self.Radius**2) * self.Radius**3 * self.CpOpt / self.TSROpt**3

    def calculate_hydro_torque(self, Radius, Uinf, Cq):
        return 0.5 * self.GLOBAL.rho * (np.pi * Radius**2) * Radius * Uinf**2 * Cq

    def calculate_thrust_force(self, Radius, Uinf, Ct):
        return 0.5 * self.GLOBAL.rho * (np.pi * Radius**2) * Uinf**2 * Ct

    def calculate_phydro(self, Uinf, Cp):
        return 0.5 * self.GLOBAL.rho * (np.pi * self.Radius**2) * Uinf**3 * Cp

    def calculate_pfluid(self):
        return 0.5 * self.GLOBAL.rho * (np.pi * self.Radius**2) * self.Uinf_adjusted**3

    def calculate_punc(self):
        return self.Kopt * (self.Uinf_adjusted * self.TSROpt / self.Radius)**3

    def calculate_pmech(self):
        return self.w * self.Tc

    def calculate_pelec(self):
        return self.w * self.Tc * self.turbine_efficiency

    def calculate_power(self):
        self.Phydro = self.calculate_phydro(self.Uinf_adjusted, self.CpFunc(self.TSR))
        self.Pfluid = self.calculate_pfluid()
        self.Punc = self.calculate_punc()
        self.Pmech = self.calculate_pmech()
        self.Pelec = self.calculate_pelec()

    def get_results(self):
        return {
            't': self.t,
            'w': self.w,
            'Tc': self.Tc,
            'Pmech': self.Pmech,
            'Pelec': self.Pelec,
            'Phydro': self.Phydro,
            'Pfluid': self.Pfluid,
            'Punc': self.Punc,
            'TSR': self.TSR,
            'Ft': self.Ft,
            'Th': self.Th,
            'Tbrake': self.Tbrake,
            'theta_turbine': self.theta_turbine,
            'dHub': self.dHub,
            'Wturbine': self.Wturbine,
            'Uinf_adjusted': self.Uinf_adjusted
        }

    def flowAtDepth(self, FlowSpeed, Radius, dHub, dMoor):
        """
        Adjusts flow speed at a turbine's hub depth based on the mooring depth and the flow speed at the surface.
        
        Parameters:
        - FlowSpeed: Flow speed at the surface in m/s.
        - Radius: Radius of the turbine in meters.
        - dHub: Depth of the turbine hub in meters.
        - dMoor: Depth of the mooring in meters.
        
        Returns:
        - Uout: Adjusted flow speed at the hub depth in m/s.
        """
        if np.isscalar(FlowSpeed):
            FlowSpeed = np.array([FlowSpeed])
            dHub = np.array([dHub])

        Uout = np.zeros_like(FlowSpeed)
        Area = np.pi * Radius ** 2.0
        Uavg = FlowSpeed / 1.07
        dz = dMoor - dHub

        for i in range(len(FlowSpeed)):
            if (dz[i] - Radius) < 0.5 * dMoor and (dz[i] + Radius) <= 0.5 * dMoor:
                Za = dz[i] - Radius
                Zb = dz[i] + Radius
                Zc = Zd = 0.0
            elif (dz[i] - Radius) >= 0.5 * dMoor and (dz[i] + Radius) > 0.5 * dMoor:
                Za = Zb = 0.0
                Zc = dz[i] - Radius
                Zd = dz[i] + Radius
            else:
                Za = dz[i] - Radius
                Zb = Zc = 0.5 * dMoor
                Zd = dz[i] + Radius

            tempvalA = (1.1407 * (1 / dMoor) ** (3 / 7) * Uavg[i] ** 3.0 * (Zb ** (10 / 7) - Za ** (10 / 7)))
            tempvalB = (1.07 * Uavg[i]) ** 3.0 * (Zd - Zc)
            PfluidAvg = 1 / (4.0 * Radius) * self.GLOBAL.rho * Area * (tempvalA + tempvalB)
            Uout[i] = ((2.0 * PfluidAvg) / (self.GLOBAL.rho * Area)) ** (1 / 3.0)

        return Uout if len(Uout) > 1 else Uout[0]

    def objectiveFunction_findOptimalConstantSpeed(self, x, radius, Uinf, t, CpFunc):
        speed = x
        TSR = np.divide(speed * radius, Uinf, out=np.zeros_like(Uinf), where=Uinf!=0)  # Avoid division by zero
        TSR = np.minimum(TSR, self.TSRmax)  # Cap TSR at TSRmax
        power = self.calculate_phydro(Uinf, CpFunc(TSR))
        avg_power = np.trapezoid(power, t) / (len(t) * np.mean(np.diff(t)))  # Calculate average power
        return -1 * avg_power  # Negative because we are maximizing power

    def find_optimal_constant_speed(self):
        possibleSpeed = self.TSROpt * self.Uinf / self.Radius  # Assuming optimal TSR condition, what is the speed range
        possibleSpeedRange = np.linspace(np.min(possibleSpeed), np.max(possibleSpeed), 50)  # Initial guess range

        # If we kept the constant speed candidate in possibleSpeedRange, what is the potential average power
        avePowerRange = -1 * np.array([self.objectiveFunction_findOptimalConstantSpeed(ii, self.Radius, self.Uinf, self.t, self.CpFunc) for ii in possibleSpeedRange])
        
        # What is the range of constant speed where we can get positive average power
        # This is for defining the bounds of the optimization
        positive_indices = np.where(avePowerRange > 0)[0]
        min_Speed = possibleSpeedRange[positive_indices[0]]
        max_Speed = possibleSpeedRange[positive_indices[-1]]

        # Solve for the optimal value (exact)
        result = sp.optimize.minimize_scalar(self.objectiveFunction_findOptimalConstantSpeed, bounds=(min_Speed, max_Speed), method='bounded', args=(self.Radius, self.Uinf, self.t, self.CpFunc))

        optimal_speed = result.x
        return optimal_speed

    def RotorWeight(self, Radius):
        Weight = 11.19999928 * Radius**2 + 16.37714233 * Radius - 7.44
        return Weight

    def PTOWeight(self, Prated):
        Weight = 0.01501693 * Prated + 1.51674108
        return Weight

    def UnitWeight(self, Radius, Prated):
        Weight = self.RotorWeight(Radius) + self.PTOWeight(Prated)
        return Weight
