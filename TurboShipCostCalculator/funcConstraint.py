# import autograd.numpy as np  # Thinly-wrapped numpy
import numpy as np
import matplotlib.pyplot as plt

import funcTidal  # Module for tidal flow calculations
import funcSimRotor  # Module for simulating rotor dynamics

import constGlobal
GLOBAL = constGlobal.ConstantsGlobal()  # Global constants (e.g., fluid density, gravity)

import matplotlib.pyplot as plt
plt.style.use('tableau-colorblind10')

import constUnitConvert
CONVERT = constUnitConvert.ConstantsUnitConversion()



# Function to calculate the force exerted by mooring on the vessel
# Parameters:
#   Uinf: Free stream velocity (m/s)
#   vessel: Dictionary containing vessel properties ('Cd' for drag coefficient, 'area' for cross-sectional area)
# Returns:
#   The force exerted by the mooring on the vessel (N)
calForceMoorThrustFunc = lambda Uinf, vessel: 0.5 * GLOBAL.rho * vessel['Cd'] * vessel['area'] * Uinf**2

# Function to calculate the pitch constraint for a tidal turbine system
# Parameters:
#   Radius: Radius of the turbine rotor (m)
#   dHub: Depth of the turbine hub (m)
#   dMoor: Mooring depth (m)
#   Uinf: Free stream velocity (m/s)
#   CtFunc: Function to calculate the thrust coefficient given TSR
#   TSR: Tip-speed ratio
#   vessel: Dictionary containing vessel properties
#   NumTurbine: Number of turbines in the system
# Returns:
#   ConstraintOut: The calculated pitch constraint. Must be >= 0 for a feasible design
def PitchCon(Radius, dHub, dMoor, Uinf, CtFunc, TSR, vessel, NumTurbine): 
    Uinf = funcTidal.flowAtDepth(Uinf, Radius, dHub, dMoor)  # Adjust flow speed for hub depth

    F_vessel_thrust = calForceMoorThrustFunc(Uinf, vessel)  # Calculate vessel thrust force
    F_turbine_thrust = funcSimRotor.calForceThrustFunc(Radius, Uinf, CtFunc(TSR))  # Calculate turbine thrust force
    F_total = F_vessel_thrust + round(NumTurbine) * F_turbine_thrust  # Total force

    # Calculate the pitch constraint
    ConstraintOut = vessel['K_m'] * vessel['phi'] - round(NumTurbine) * F_turbine_thrust * dHub - F_total * vessel['X_m'] * np.cos(vessel['theta']) - F_total * vessel['Z_m'] * np.sin(vessel['theta'])

    return ConstraintOut

# Function to calculate the cavitation constraint for a tidal turbine system
# Parameters:
#   Radius: Radius of the turbine rotor (m)
#   dHub: Depth of the turbine hub (m)
#   dMoor: Mooring depth (m)
#   Uinf: Free stream velocity (m/s)
#   w: Angular velocity of the rotor (rad/s)
#   TSR: Tip-speed ratio
#   CpminFunc: Function to calculate the minimum pressure coefficient given TSR
#   spanRatio: Ratio of the segment position to the rotor radius
# Returns:
#   ConstraintOut: The calculated cavitation constraint. Must be >= 0 for a feasible design
def CavitationCon(Radius, dHub, dMoor, Uinf, w, TSR, CpminFunc, spanRatio): 
    Uinf = funcTidal.flowAtDepth(Uinf, Radius, dHub, dMoor)  # Adjust flow speed for hub depth

    Vel = np.sqrt(Uinf**2 + (spanRatio * Radius)**2 * w**2)  # Calculate resultant velocity at blade

    # Calculate the cavitation constraint
    cavitation_num = GLOBAL.Patm + GLOBAL.rho * GLOBAL.g * (dHub - (spanRatio * Radius)) - GLOBAL.Pvap
    cavitation_den = 0.5 * GLOBAL.rho * Vel**2

    ConstraintOut = cavitation_num / cavitation_den + CpminFunc(TSR)

    return ConstraintOut



def plotCavitationCon(Radius, dHub, dMoor, Uinf, w, TSR, CpminFunc, spanRatio, t, ylim):
    # Create a figure with three subplots
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))

    # Iterate over each span ratio
    for i, ratio in enumerate(spanRatio):
        # Plot the cavitation constraint over time for the current span ratio
        axs[i].plot(t * CONVERT.sec2days, CavitationCon(Radius, dHub, dMoor, Uinf, w, TSR, CpminFunc[i], ratio))
        
        # Set the y-axis limits if provided, else use default limits
        if ylim is not None:
            axs[i].set_ylim(ylim)
        else:
            axs[i].set_ylim([-0.1, 1.0])
        
        # Add gridlines to the plot
        axs[i].grid()
        
        # Set the x-axis label
        axs[i].set_xlabel('Time [days]')
        
        # Set the y-axis label
        axs[i].set_ylabel('Cavitation Constraint (<0 means violation)')
        
        # Set the title for the subplot
        axs[i].set_title(f'Subplot for span ratio {round(ratio, 3)}')

    # Adjust the spacing between subplots
    plt.tight_layout()
    
    # Display the plot
    plt.show()



def plotPitchCon(Radius, dHub, dMoor, Uinf, CtFunc, TSR, VESSEL, NumTurbine, t, ylim):
    # Plot the pitch constraint over time
    plt.plot(t * CONVERT.sec2days, PitchCon(Radius, dHub, dMoor, Uinf, CtFunc, TSR, VESSEL, NumTurbine))
    
    # Set the y-axis limits if provided, else use default limits
    if ylim is not None:
        plt.ylim(ylim)
    else:
        plt.ylim([-0.1, 10.0])
    
    # Add gridlines to the plot
    plt.grid()
    
    # Set the x-axis label
    plt.xlabel('Time [days]')
    
    # Set the y-axis label
    plt.ylabel('Pitch Constraint (<0 means violation)')
    
    # Display the plot
    plt.show()

