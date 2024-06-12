import autograd.numpy as np  # Thinly-wrapped numpy
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('tableau-colorblind10')
import seaborn as sns
import itertools
import matplotlib.ticker as ticker

from datetime import datetime

import funcTidal
import funcSimRotor
import funcConstraint
import funcLCOE
import constGlobal
import constLCOE
import constUnitConvert

GLOBAL = constGlobal.ConstantsGlobal()
COST = constLCOE.ConstantsLCOE()
CONVERT = constUnitConvert.ConstantsUnitConversion() 

cacheSimResult = {}

"""
Code Below Print Out the Optimization Condition
"""
def printSimulationDetails(Umin, withBrake, scalePrated, VESSEL, station, startdate, rangeHr, timestep, Uinf, dMoor, cable_length_miles, CityName):
    print("="*60)  # Print a line of "=" characters at the beginning
    print("Simulation Conditions:")
    print(f"Minimum Flow Speed (Umin): {'None' if Umin is None else Umin}")
    print(f"Brake Enabled: {'Yes' if withBrake else 'No'}")
    print(f"Scale of Prated: {scalePrated} W")
    print(f"Vessel Type: {VESSEL['name']}")

    print(f"\nTidal Simulation Details:")
    print(f"Station: {station}")
    # Convert startdate to a more readable format
    startdate_readable = datetime.strptime(str(startdate), '%Y%m%d').strftime('%B %d, %Y')
    print(f"Start Date: {startdate_readable}")
    print(f"Simulation Range: {rangeHr} hours")
    print(f"Timestep: {timestep} seconds")

    min_flow = np.min(Uinf)
    max_flow = np.max(Uinf)
    mean_flow = np.mean(Uinf)
    print(f"Minimum Flow from Uinf: {min_flow:.2f} m/s") 
    print(f"Maximum Flow from Uinf: {max_flow:.2f} m/s")
    print(f"Mean Flow from Uinf: {mean_flow:.2f} m/s") 
    print(f"Mooring Depth: {dMoor} meters")
    print(f"Cable Length: {cable_length_miles:.2f} miles")
    print(f"Closest City: {CityName}")
    print("="*60)  # Print a line of "=" characters at the end


"""
Below are functions for sp.optimize.brute
"""

def objectiveFuncBrute(x, dMoor, Uinf, t, CpFunc, CtFunc, CpminFunc, spanRatio, CpOpt, TSROpt, baseRadius, baseMass, Umin, VESSEL, dCable, withBrake):
    Radius, Prated, dHub, NumTurbine = x

    # Initialize default values
    LCOE = 1e5
    PitchCon_flag = True
    CavCon_flag = True

    # Check if the conditions for a valid simulation are met
    if not (Radius < dHub) or not ((Radius + dHub) < dMoor):
        return calculate_cost_proxy(LCOE, PitchCon_flag, CavCon_flag, x)

    # Check if result is already in cache
    cache_key = tuple(list(x[:3]) + [Umin, withBrake])
    if cache_key in cacheSimResult:
        w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th = cacheSimResult[cache_key]
    else:
        w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th = funcSimRotor.simRotor(
            Radius, Prated, dHub, dMoor, Uinf, t, CpFunc, CtFunc, CpOpt, TSROpt, baseRadius, baseMass, Umin, withBrake)

        # Find indices where w is NaN
        nan_indices = np.isnan(w)
        w[nan_indices] = 0
        Tc[nan_indices] = 0
        Pmech[nan_indices] = 0
        Pelec[nan_indices] = 0
        Phydro[nan_indices] = 0
        TSR[nan_indices] = 0
        Ft[nan_indices] = 0
        Th[nan_indices] = 0

        # Cache the result
        cacheSimResult[cache_key] = (w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th)

    # Proceed with calculations if simulation results are valid
    Uinf_update = funcTidal.flowAtDepth(Uinf, Radius, dHub, dMoor)
    F_vessel_thrust = funcConstraint.calForceMoorThrustFunc(Uinf_update, VESSEL)
    F_turbine_thrust = funcSimRotor.calForceThrustFunc(Radius, Uinf_update, CtFunc(TSR))

    # Calculate LCOE and cost breakdown
    LCOE, CostBreakdown = funcLCOE.calculate_cost(
        Radius, Prated, NumTurbine, dCable, dMoor, F_vessel_thrust, F_turbine_thrust, Pelec, t)

    # Check pitch and cavitation constraints
    PitchCon_flag = any(val < 0 for val in funcConstraint.PitchCon(Radius, dHub, dMoor, Uinf, CtFunc, TSR, VESSEL, NumTurbine))

    CavCon_flag = any(any(val < 0 for val in funcConstraint.CavitationCon(Radius, dHub, dMoor, Uinf, w, TSR, Cpmin, span)) for Cpmin, span in zip(CpminFunc, spanRatio))


    return calculate_cost_proxy(LCOE, PitchCon_flag, CavCon_flag, x)


def calculate_cost_proxy(LCOE, PitchCon_flag, CavCon_flag, x):
    scale = 1e5
    myCost = LCOE + scale * (PitchCon_flag + CavCon_flag)

    outputString = f"Radius [m]: {x[0]}; Power Rating [W]: {x[1]}; hub depth [m]: {x[2]}; # Turbine: {x[3]}; fval: {round(myCost, 3)}; LCOE [$/kWh]: {round(LCOE, 3)}; CavCon: {CavCon_flag}; PitchCon: {PitchCon_flag}"
    print(outputString)

    return myCost

# Calculate number of simulation cases (given brute grid)
def calculateTotalCases(rranges):
    total_cases = 1
    for rrange in rranges:
        # Calculate the number of steps for each parameter
        num_steps = ((rrange.stop - rrange.start) / rrange.step) + 1
        # Multiply the number of steps to get the total number of cases
        total_cases *= num_steps
    return int(total_cases)


# Plot and save brute force result
def processBruteOutput(xopt, fval, grid, Jout, station, startdate, VESSEL, Umin, withBrake):
    # Replace values in Jout greater than 1e5 with -1 for consistency or error handling
    Jout[Jout > 1e5] = -1

    grid = np.round(grid, 4)
    Jout = np.round(Jout, 4)
    xopt = np.round(xopt, 4)
    fval = np.round(fval, 4)

    # Use f-string for more readable and Pythonic string formatting
    print(f"Optimal LCOE is [$/kWh]: {fval:5.4f} \n"
          f" - Radius [m]: {xopt[0]:5.2f} \n"
          f" - Turbine Power Rating [W]: {xopt[1]:5.2f} \n"
          f" - Hub depth [m]: {xopt[2]:5.2f} \n"
          f" - Number of turbine: {xopt[3]:5.2f}")

    # Create a DataFrame from the optimization results
    LCOEOUT = pd.DataFrame({
        'LCOE': Jout.ravel(),
        'Rr [m]': grid[0].ravel(),
        'Prated [W]': grid[1].ravel(),
        'dhub [m]': grid[2].ravel(),
        '#Turbine': grid[3].ravel()
    })

    # Generate filename with today's date
    now = datetime.now()
    formatted_date = now.strftime("%Y%m%d%H%M")
    filename = f"{station}_{startdate}_{VESSEL['name']}_Brake{withBrake}_Umin{Umin}_LCOE_{formatted_date}.txt"

    # Export DataFrame to text file
    LCOEOUT.to_csv(filename, sep='\t', index=False)

    plotGrid(xopt,LCOEOUT, station, startdate, VESSEL, Umin, withBrake)



def plotGrid(xopt,LCOEOUT, station, startdate, VESSEL, Umin, withBrake):
    fig, axes = plt.subplots(nrows=6, ncols=1, figsize=(6.4*1.5, 4.8*5))

    vmax = np.max(LCOEOUT['LCOE'])
    vmin = np.min(LCOEOUT['LCOE'][LCOEOUT['LCOE'] > 0])

    for ax, myidx in zip(axes, itertools.combinations(range(1, 5), 2)):
        valid_idx = [val for val in range(1, 5) if val not in myidx]
        table = pd.pivot_table(LCOEOUT.loc[(LCOEOUT[LCOEOUT.columns[myidx[0]]] == xopt[myidx[0]-1]) & (LCOEOUT[LCOEOUT.columns[myidx[1]]] == xopt[myidx[1]-1])], 
                            values='LCOE', 
                            index=LCOEOUT.columns[valid_idx[0]], 
                            columns=LCOEOUT.columns[valid_idx[1]])
        
        C_vals = table.columns.values
        g_vals = table.index.values

        tick = ticker.ScalarFormatter(useOffset=False)
        tick.set_powerlimits((0, 0))

        tc = C_vals
        tg = g_vals

        if table.columns.name == 'Prated [W]':
            tc = [u"${}$".format(tick.format_data(x)) for x in C_vals] 

        if table.index.name == 'Prated [W]':
            tg = [u"${}$".format(tick.format_data(x)) for x in g_vals]
        
        sns.heatmap(table.mask(table < 0), annot=True, fmt=".4f", linewidth=0.1, ax=ax, xticklabels=tc, yticklabels=tg, cmap="cividis", vmin=vmin, vmax=vmax)

        mytitle = 'LCOE [$/kWhr] at ' + LCOEOUT.columns[myidx[0]] + ': ' + str(xopt[myidx[0]-1]) + ' and ' + LCOEOUT.columns[myidx[1]] + ': ' + str(xopt[myidx[1]-1])
        ax.set_title(mytitle)

    fig.tight_layout()

    # Generate filename with today's date
    now = datetime.now()
    formatted_date = now.strftime("%Y%m%d%H%M")

    # save figure
    figurename = f"{station}_{startdate}_{VESSEL['name']}_brake{withBrake}_Umin{Umin}_grid_{formatted_date}.pdf"
    fig.savefig(figurename, format="pdf", bbox_inches="tight")

"""
Below are functions for sp.optimize.minimize
"""

def objectiveFuncMinimize(x, dCable, dMoor, Uinf, t, CpFunc, CtFunc, CpOpt, TSROpt, baseRadius, baseMass, VESSEL, Umin, withBrake, scalePrated): 
    Radius = x[0]
    Prated = x[1] * scalePrated
    dHub = x[2]
    NumTurbine = np.round(x[3])

    # Check if result is already in cache 
    cache_key = tuple(list(x[:3]) + [Umin, withBrake])
    if cache_key in cacheSimResult:
        w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th = cacheSimResult[cache_key]
    else:
        w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th = funcSimRotor.simRotor(
            Radius, Prated, dHub, dMoor, Uinf, t, CpFunc, CtFunc, CpOpt, TSROpt, baseRadius, baseMass, Umin, withBrake)

        # Find indices where w is NaN
        nan_indices = np.isnan(w)
        w[nan_indices] = 0
        Tc[nan_indices] = 0
        Pmech[nan_indices] = 0
        Pelec[nan_indices] = 0
        Phydro[nan_indices] = 0
        TSR[nan_indices] = 0
        Ft[nan_indices] = 0
        Th[nan_indices] = 0

        # Cache the result
        cacheSimResult[cache_key] = (w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th)

    Uinf_update = funcTidal.flowAtDepth(Uinf, Radius, dHub, dMoor)
    F_vessel_thrust = funcConstraint.calForceMoorThrustFunc(Uinf_update, VESSEL)
    F_turbine_thrust = funcSimRotor.calForceThrustFunc(Radius, Uinf_update, CtFunc(TSR))
   
    LCOE, CostBreakdown = funcLCOE.calculate_cost(Radius, Prated, NumTurbine, dCable, dMoor, F_vessel_thrust, F_turbine_thrust, Pelec, t)

    print(f'LCOE is {LCOE:0.4f} for Rr: {Radius:0.4f}, Prated: {Prated:0.4f}, dHub: {dHub:0.4f}, and #turbine: {NumTurbine:0.4f}')

    return LCOE

def constraintFuncMinimize1Pitch(x, dMoor, Uinf, t, CpFunc, CtFunc, CpOpt, TSROpt, baseRadius, baseMass, VESSEL, Umin, withBrake, scalePrated):
    Radius = x[0]
    Prated = x[1] * scalePrated
    dHub = x[2]
    NumTurbine = np.round(x[3])
    
    # Check if result is already in cache
    cache_key = tuple(list(x[:3]) + [Umin, withBrake])
    if cache_key in cacheSimResult:
        w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th = cacheSimResult[cache_key]
    else:
        w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th = funcSimRotor.simRotor(
            Radius, Prated, dHub, dMoor, Uinf, t, CpFunc, CtFunc, CpOpt, TSROpt, baseRadius, baseMass, Umin, withBrake)

        # Find indices where w is NaN
        nan_indices = np.isnan(w)
        w[nan_indices] = 0
        Tc[nan_indices] = 0
        Pmech[nan_indices] = 0
        Pelec[nan_indices] = 0
        Phydro[nan_indices] = 0
        TSR[nan_indices] = 0
        Ft[nan_indices] = 0
        Th[nan_indices] = 0

        # Cache the result
        cacheSimResult[cache_key] = (w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th)

    ConstraintOut = funcConstraint.PitchCon(Radius, dHub, dMoor, Uinf, CtFunc, TSR, VESSEL, NumTurbine)
    return ConstraintOut

def constraintFuncMinimizeCavitation(x, dMoor, Uinf, t, CpFunc, CtFunc, CpOpt, TSROpt, baseRadius, baseMass, CpminFunc, spanRatio, Umin, withBrake, scalePrated):
    Radius = x[0]
    Prated = x[1] * scalePrated
    dHub = x[2]
    NumTurbine = np.round(x[3])
        
    # Check if result is already in cache
    cache_key = tuple(list(x[:3]) + [Umin, withBrake])
    if cache_key in cacheSimResult:
        w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th = cacheSimResult[cache_key]
    else:
        w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th = funcSimRotor.simRotor(
            Radius, Prated, dHub, dMoor, Uinf, t, CpFunc, CtFunc, CpOpt, TSROpt, baseRadius, baseMass, Umin, withBrake)

        # Find indices where w is NaN
        nan_indices = np.isnan(w)
        w[nan_indices] = 0
        Tc[nan_indices] = 0
        Pmech[nan_indices] = 0
        Pelec[nan_indices] = 0
        Phydro[nan_indices] = 0
        TSR[nan_indices] = 0
        Ft[nan_indices] = 0
        Th[nan_indices] = 0

        # Cache the result
        cacheSimResult[cache_key] = (w, Tc, Pmech, Pelec, Phydro, Pfluid, Punc, TSR, Ft, Th)

    ConstraintOut = funcConstraint.CavitationCon(Radius, dHub, dMoor, Uinf, w, TSR, CpminFunc, spanRatio)
    return ConstraintOut

