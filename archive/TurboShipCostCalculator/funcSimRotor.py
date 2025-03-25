import numpy as np
from datetime import datetime

import funcRotor
import funcTidal
import constLCOE
import constGlobal
import constUnitConvert

import matplotlib.pyplot as plt
plt.style.use('tableau-colorblind10')

# Constants
GLOBAL = constGlobal.ConstantsGlobal()
COST = constLCOE.ConstantsLCOE()
CONVERT = constUnitConvert.ConstantsUnitConversion() 

# Lambda functions for various hydrodynamic and power calculations
calTorqueHydroFunc = lambda Radius, Uinf, Cq: 0.5 * GLOBAL.rho * (np.pi * Radius**2) * Radius * Uinf**2 * Cq  # Calculate hydrodynamic torque
calForceThrustFunc = lambda Radius, Uinf, Ct: 0.5 * GLOBAL.rho * (np.pi * Radius**2) * Uinf**2 * Ct  # Calculate thrust force
calPowerHydro = lambda Radius, Uinf, Cp: 0.5 * GLOBAL.rho * (np.pi * Radius**2) * Uinf**3 * Cp  # Calculate hydrodynamic power
calKoptFunc = lambda Radius, CpOpt, TSROpt: 0.5 * GLOBAL.rho * (np.pi * Radius**2) * Radius**3 * CpOpt / TSROpt**3  # Calculate optimal control gain
calPowerFluidFunc = lambda Radius, Uinf: 0.5 * GLOBAL.rho * (np.pi * Radius**2) * Uinf**3  # Calculate fluid power
calPowerUncFunc = lambda Radius, Kopt, TSROpt, Uinf: Kopt * (Uinf * TSROpt / Radius)**3  # Calculate unconstrained power

# Helper functions for input verification
def verify_scalar(value, name):
    if not np.isscalar(value):
        raise ValueError(f"{name} should be a scalar value.")

def verify_array(value, name):
    if not isinstance(value, (np.ndarray, list)):
        raise ValueError(f"{name} should be an array.")

def verify_callable(value, name):
    if not callable(value):
        raise ValueError(f"{name} should be a callable function.")

def simRotor(Radius, Prated, dHub, dMoor, Uinf, t, CpFunc, CtFunc, CpOpt, TSROpt, baseRadius, baseMass, Umin, withBrake):

    print(f"Running rotor simulation for Radius = {Radius}, Prated = {Prated}, dHub = {dHub}.")
    """
    Simulate rotor dynamics and calculate various power and force metrics.
    """
    # Verify inputs
    scalar_inputs = [Radius, Prated, dHub, dMoor, CpOpt, TSROpt, baseRadius, baseMass]
    scalar_names = ['Radius', 'Prated', 'dHub', 'dMoor', 'CpOpt', 'TSROpt', 'baseRadius', 'baseMass']
    for value, name in zip(scalar_inputs, scalar_names):
        verify_scalar(value, name)
    verify_array(Uinf, "Uinf")
    verify_array(t, "t")
    verify_callable(CpFunc, "CpFunc")
    verify_callable(CtFunc, "CtFunc")
    if Umin is not None:
        verify_scalar(Umin, "Umin")
    if not isinstance(withBrake, bool):
        raise ValueError("withBrake should be a boolean value.")

    # Initialize arrays for simulation results
    # w = np.zeros(np.shape(t), dtype=np.float64)  # Angular velocity
    w = np.zeros(np.shape(t))  # Angular velocity

    wd = np.zeros(np.shape(t))  # Angular acceleration
    TSR = np.zeros(np.shape(t))  # Tip-speed ratio
    Tc = np.zeros(np.shape(t))  # Control torque
    Th = np.zeros(np.shape(t))  # Hydrodynamic torque
    Ft = np.zeros(np.shape(t))  # Thrust force
    Pmech = np.zeros(np.shape(t))  # Mechanical power
    Pelec = np.zeros(np.shape(t))  # Electrical power
    Phydro = np.zeros(np.shape(t))  # Hydrodynamic power

    dt = np.mean(np.diff(t))  # Time step

    # Adjust flow speed given hub depth
    Uinf = funcTidal.flowAtDepth(Uinf, Radius, dHub, dMoor)

    # Scale moment of inertia
    Jr = funcRotor.calInertia(Radius, baseRadius, baseMass, 1)

    # Calculate optimal control gain
    Kopt = calKoptFunc(Radius, CpOpt, TSROpt)

    # Calculate power from fluid
    Pfluid = calPowerFluidFunc(Radius, Uinf)
    Punc = calPowerUncFunc(Radius, Kopt, TSROpt, Uinf)

    wmin = 1e-4  # Minimum angular velocity

    # Initial condition with cut-in speed consideration
    if Umin is not None and Uinf[0] < Umin:
        w[0] = wmin
        Tc[0] = 0
    else:
        w[0] = TSROpt * Uinf[0] / Radius
        Tc[0] = Kopt * w[0]**2

    Pmech[0] = Tc[0] * w[0]
    Pelec[0] = Pmech[0] * COST.eff

    # Check if Pelec > Prated. If yes, limit control torque
    if Pelec[0] > Prated:
        if withBrake:
            TSR[0] = TSROpt
            w[0] = TSR[0] * Uinf[0] / Radius
        Tc[0] = (Prated / COST.eff) / w[0]
        Pmech[0] = Tc[0] * w[0]
        Pelec[0] = Pmech[0] * COST.eff

    # Update TSR, hydrodynamic thrust, velocity, hydrodynamic power, thrust force
    TSR[0] = Radius * w[0] / Uinf[0]
    Th[0] = calTorqueHydroFunc(Radius, Uinf[0], CpFunc(TSR[0]) / TSR[0])
    wd[0] = 1 / Jr * (Th[0] - Tc[0])
    Phydro[0] = calPowerHydro(Radius, Uinf[0], CpFunc(TSR[0]))
    Ft[0] = calForceThrustFunc(Radius, Uinf[0], CtFunc(TSR[0]))

    # Simulate for remaining time
    for kk in range(1, len(t)):
        w[kk] = w[kk-1] + wd[kk-1] * dt
        Tc[kk] = Kopt * w[kk]**2
        Pmech[kk] = Tc[kk] * w[kk]
        Pelec[kk] = Pmech[kk] * COST.eff

        if Pelec[kk] > Prated:
            if withBrake:
                TSR[kk] = TSROpt
                w[kk] = TSR[kk] * Uinf[kk] / Radius
            Tc[kk] = (Prated / COST.eff) / w[kk]
            Pmech[kk] = Tc[kk] * w[kk]
            Pelec[kk] = Pmech[kk] * COST.eff

        if Umin is not None and Uinf[kk] < Umin:
            w[kk] = wmin
            Tc[kk] = 0
            Pmech[kk] = Tc[kk] * w[kk]
            Pelec[kk] = Pmech[kk] * COST.eff
        else:
            TSR[kk] = Radius * w[kk] / Uinf[kk]
            Th[kk] = calTorqueHydroFunc(Radius, Uinf[kk], CpFunc(TSR[kk]) / TSR[kk])
            wd[kk] = 1 / Jr * (Th[kk] - Tc[kk])
            Phydro[kk] = calPowerHydro(Radius, Uinf[kk], CpFunc(TSR[kk]))
            Ft[kk] = calForceThrustFunc(Radius, Uinf[kk], CtFunc(TSR[kk]))

    # print("Simulation completed")

    return w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th


def printSimRotorStatistic(w,Tc,Pmech,Pelec,Phydro,Pfluid,Punc,TSR,Ft,Th):
    # Calculate the mean of the output arrays
    mean_w = np.mean(w)
    mean_Tc = np.mean(Tc)
    mean_TSR = np.mean(TSR)
    mean_Pmech = np.mean(Pmech)
    mean_Pelec = np.mean(Pelec)
    mean_Phydro = np.mean(Phydro)
    mean_Pfluid = np.mean(Pfluid)
    mean_Punc = np.mean(Punc)
    mean_Ft = np.mean(Ft)
    mean_Th = np.mean(Th)

    # Calculate the max of the output arrays
    max_w = np.max(w)
    max_Tc = np.max(Tc)
    max_TSR = np.max(TSR)
    max_Pmech = np.max(Pmech)
    max_Pelec = np.max(Pelec)
    max_Phydro = np.max(Phydro)
    max_Pfluid = np.max(Pfluid)
    max_Punc = np.max(Punc)
    max_Ft = np.max(Ft)
    max_Th = np.max(Th)

    # Define a function to format the output
    def format_output(name, value):
        return f"{name}: {value:.2f}"

    # Print cost breakdown
    print("="*60)  # Print a line of "=" characters at the beginning
    print("Rotor Dynamics (Mean) [SI units are assumed]:")

    # Print the mean of the output arrays
    print(format_output("w", mean_w))
    print(format_output("Tc", mean_Tc))
    print(format_output("TSR", mean_TSR))
    print(format_output("Pmech", mean_Pmech))
    print(format_output("Pelec", mean_Pelec))
    print(format_output("Phydro", mean_Phydro))
    print(format_output("Pfluid", mean_Pfluid))
    print(format_output("Punc", mean_Punc))
    print(format_output("Ft", mean_Ft))
    print(format_output("Th", mean_Th))

    # Print cost breakdown
    print("="*60)  # Print a line of "=" characters at the beginning
    print("Rotor Dynamics (Max) [SI units are assumed]:")

    # Print the mean of the output arrays
    print(format_output("w", max_w))
    print(format_output("Tc", max_Tc))
    print(format_output("TSR", max_TSR))
    print(format_output("Pmech", max_Pmech))
    print(format_output("Pelec", max_Pelec))
    print(format_output("Phydro", max_Phydro))
    print(format_output("Pfluid", max_Pfluid))
    print(format_output("Punc", max_Punc))
    print(format_output("Ft", max_Ft))
    print(format_output("Th", max_Th))



def plotTimeDomainResult(Uinf,t, w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th, station, startdate, VESSEL, Umin, withBrake):
    plt.figure(figsize=(6.4,4.8*5))

    plt.subplot(7,1,1)
    plt.plot(t*CONVERT.sec2days,Uinf)
    plt.xlabel('Time [days]')
    plt.ylabel('Flow Speed [m/s]')

    plt.subplot(7,1,2)
    plt.plot(t*CONVERT.sec2days,w*CONVERT.rads2rpm)
    plt.xlabel('Time [days]')
    plt.ylabel('Rotor Speed [RPM]')

    plt.subplot(7,1,3)
    plt.plot(t*CONVERT.sec2days,Tc,label='Control')
    plt.plot(t*CONVERT.sec2days,Th,'--',label='Hydro')
    plt.xlabel('Time [days]')
    plt.ylabel('Torque [Nm]')
    plt.legend(loc='upper right')
    
    plt.subplot(7,1,4)
    plt.plot(t*CONVERT.sec2days,Phydro,label='Hydro')
    plt.plot(t*CONVERT.sec2days,Pmech,'--',label='Mech')
    plt.plot(t*CONVERT.sec2days,Pelec,':',label='Elec')
    plt.xlabel('Time [days]')
    plt.ylabel('Power [W]')
    plt.legend(loc='upper right')

    plt.subplot(7,1,5)
    plt.plot(t*CONVERT.sec2days,Pfluid,label='Fluid')
    plt.plot(t*CONVERT.sec2days,Punc,'--',label='Unc')
    plt.xlabel('Time [days]')
    plt.ylabel('Power [W]')
    plt.legend(loc='upper right')

    plt.subplot(7,1,6)
    plt.plot(t*CONVERT.sec2days,TSR,label='TSR')
    plt.xlabel('Time [days]')
    plt.ylabel('TSR')
    plt.legend(loc='upper right')

    plt.subplot(7,1,7)
    plt.plot(t*CONVERT.sec2days,Ft,label='Thrust')
    plt.xlabel('Time [days]')
    plt.ylabel('Force [N]')
    plt.legend(loc='upper right')

    if VESSEL is not None and isinstance(VESSEL, dict):
        vessel_name = VESSEL.get('name', None)
    else:
        vessel_name = None

    plt.tight_layout()

    now = datetime.now()
    formatted_date = now.strftime("%Y%m%d%H%M")

    figurename = f"{station}_{startdate}_{vessel_name}_brake{withBrake}_Umin{Umin}_dynamic_{formatted_date}.pdf"
    plt.savefig(figurename, format="pdf", bbox_inches="tight")