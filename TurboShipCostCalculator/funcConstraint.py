import numpy as np
import matplotlib.pyplot as plt
import funcTidal  # Module for tidal flow calculations
import funcSimRotor  # Module for simulating rotor dynamics
import constGlobal
import constUnitConvert

# Initialize global constants and unit conversion constants
GLOBAL = constGlobal.ConstantsGlobal()
CONVERT = constUnitConvert.ConstantsUnitConversion()

# Set the plotting style
plt.style.use('tableau-colorblind10')

# Function to calculate the force exerted by mooring on the vessel
def calForceMoorThrust(Uinf, vessel):
    """
    Calculate the force exerted by mooring on the vessel.

    Parameters:
    Uinf (float): Free stream velocity (m/s)
    vessel (dict): Dictionary containing vessel properties ('Cd' for drag coefficient, 'area' for cross-sectional area)

    Returns:
    float: The force exerted by the mooring on the vessel (N)
    """
    return 0.5 * GLOBAL.rho * vessel['Cd'] * vessel['area'] * Uinf**2

# Function to calculate the pitch constraint for a tidal turbine system
def PitchCon(Radius, dHub, dMoor, Uinf, CtFunc, TSR, vessel, NumTurbine):
    """
    Calculate the pitch constraint for a tidal turbine system.

    Parameters:
    Radius (float): Radius of the turbine rotor (m)
    dHub (float): Depth of the turbine hub (m)
    dMoor (float): Mooring depth (m)
    Uinf (float): Free stream velocity (m/s)
    CtFunc (function): Function to calculate the thrust coefficient given TSR
    TSR (float): Tip-speed ratio
    vessel (dict): Dictionary containing vessel properties
    NumTurbine (int): Number of turbines in the system

    Returns:
    float: The calculated pitch constraint. Must be >= 0 for a feasible design
    """
    Uinf = funcTidal.flowAtDepth(Uinf, Radius, dHub, dMoor)  # Adjust flow speed given hub depth
    F_vessel_thrust = calForceMoorThrust(Uinf, vessel)  # Calculate vessel thrust force
    F_turbine_thrust = funcSimRotor.calForceThrustFunc(Radius, Uinf, CtFunc(TSR))  # Calculate turbine thrust force
    F_total = F_vessel_thrust + round(NumTurbine) * F_turbine_thrust  # Total force

    # Calculate the pitch constraint
    ConstraintOut = (vessel['K_m'] * vessel['phi'] - round(NumTurbine) * F_turbine_thrust * dHub
                     - F_total * vessel['X_m'] * np.cos(vessel['theta'])
                     - F_total * vessel['Z_m'] * np.sin(vessel['theta']))

    return ConstraintOut

# Function to calculate the cavitation constraint for a tidal turbine system
def CavitationCon(Radius, dHub, dMoor, Uinf, w, TSR, CpminFunc, spanRatio):
    """
    Calculate the cavitation constraint for a tidal turbine system.

    Parameters:
    Radius (float): Radius of the turbine rotor (m)
    dHub (float): Depth of the turbine hub (m)
    dMoor (float): Mooring depth (m)
    Uinf (float): Free stream velocity (m/s)
    w (float): Angular velocity of the rotor (rad/s)
    TSR (float): Tip-speed ratio
    CpminFunc (function): Function to calculate the minimum pressure coefficient given TSR
    spanRatio (float): Ratio of the segment position to the rotor radius

    Returns:
    float: The calculated cavitation constraint. Must be >= 0 for a feasible design
    """
    Uinf = funcTidal.flowAtDepth(Uinf, Radius, dHub, dMoor)  # Adjust flow speed for hub depth
    Vel = np.sqrt(Uinf**2 + (spanRatio * Radius)**2 * w**2)  # Calculate resultant velocity at blade

    # Calculate the cavitation constraint
    cavitation_num = GLOBAL.Patm + GLOBAL.rho * GLOBAL.g * (dHub - (spanRatio * Radius)) - GLOBAL.Pvap
    cavitation_den = 0.5 * GLOBAL.rho * Vel**2

    ConstraintOut = cavitation_num / cavitation_den + CpminFunc(TSR)

    return ConstraintOut

# Function to plot the cavitation constraint over time
def plotCavitationCon(Radius, dHub, dMoor, Uinf, w, TSR, CpminFunc, spanRatio, t, ylim=None):
    """
    Plot the cavitation constraint over time.

    Parameters:
    Radius (float): Radius of the turbine rotor (m)
    dHub (float): Depth of the turbine hub (m)
    dMoor (float): Mooring depth (m)
    Uinf (float): Free stream velocity (m/s)
    w (float): Angular velocity of the rotor (rad/s)
    TSR (float): Tip-speed ratio
    CpminFunc (list of functions): List of functions to calculate the minimum pressure coefficient given TSR
    spanRatio (list of floats): List of span ratios
    t (array-like): Time array
    ylim (tuple, optional): Y-axis limits for the plot
    """
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))

    for i, ratio in enumerate(spanRatio):
        axs[i].plot(t * CONVERT.sec2days, CavitationCon(Radius, dHub, dMoor, Uinf, w, TSR, CpminFunc[i], ratio))
        axs[i].set_ylim(ylim if ylim is not None else [-0.1, 1.0])
        axs[i].grid()
        axs[i].set_xlabel('Time [days]')
        axs[i].set_ylabel('Cavitation Constraint (<0 means violation)')
        axs[i].set_title(f'Subplot for span ratio {round(ratio, 3)}')

    plt.tight_layout()
    plt.show()

# Function to plot the pitch constraint over time
def plotPitchCon(Radius, dHub, dMoor, Uinf, CtFunc, TSR, VESSEL, NumTurbine, t, ylim=None):
    """
    Plot the pitch constraint over time.

    Parameters:
    Radius (float): Radius of the turbine rotor (m)
    dHub (float): Depth of the turbine hub (m)
    dMoor (float): Mooring depth (m)
    Uinf (float): Free stream velocity (m/s)
    CtFunc (function): Function to calculate the thrust coefficient given TSR
    TSR (float): Tip-speed ratio
    VESSEL (dict): Dictionary containing vessel properties
    NumTurbine (int): Number of turbines in the system
    t (array-like): Time array
    ylim (tuple, optional): Y-axis limits for the plot
    """
    plt.plot(t * CONVERT.sec2days, PitchCon(Radius, dHub, dMoor, Uinf, CtFunc, TSR, VESSEL, NumTurbine))
    plt.ylim(ylim if ylim is not None else [-0.1, 10.0])
    plt.grid()
    plt.xlabel('Time [days]')
    plt.ylabel('Pitch Constraint (<0 means violation)')
    plt.show()
