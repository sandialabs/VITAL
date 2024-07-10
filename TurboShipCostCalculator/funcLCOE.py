import numpy as np
import scipy as sp
import funcTidal
import funcSimRotor
import funcConstraint
import constGlobal
import constLCOE
import constUnitConvert

# Initialize global constants from modules
GLOBAL = constGlobal.ConstantsGlobal()
COST = constLCOE.ConstantsLCOE()
CONVERT = constUnitConvert.ConstantsUnitConversion()

def calculate_cost(Radius, Prated, NumTurbine, dCable_m, dMoor_m, F_vessel_thrust, F_turbine_thrust, Pelec, t):
    """
    Calculates the Levelized Cost of Energy (LCOE) and provides a breakdown cost.
    
    Parameters:
    - Radius (float): Radius of the turbine rotor (meters).
    - Prated (float): Rated power of a single turbine (Watts).
    - NumTurbine (int): Number of turbines in the system.
    - dCable_m (float): Length of the cable (meters).
    - dMoor_m (float): Depth of the mooring system (meters).
    - F_vessel_thrust (float): Mooring force exerted on the vessel (Newtons).
    - F_turbine_thrust (float): Thrust force exerted by the turbine (Newtons).
    - Pelec (array): Electrical power output of the turbine system over time (Watts).
    - t (array): Time series associated with the electrical power output (seconds).
    
    Returns:
    - LCOE (float): The Levelized Cost of Energy in USD per kWh.
    - CostBreakdown (dict): A dictionary containing a breakdown of costs including CAPEX, OPEX, and individual component costs.
    """ 
    
    # Convert units upfront for clarity and efficiency
    Prated_MW = NumTurbine * Prated * CONVERT.W2MW
    dCable_km = dCable_m * CONVERT.m2km
    F_pull_mTon = np.max(np.abs(F_vessel_thrust + NumTurbine * F_turbine_thrust)) * CONVERT.N2mTon
    F_blade_kN = np.max(np.abs(F_turbine_thrust)) * CONVERT.N2kN
    Prated_kW = Prated * CONVERT.W2kW
    dCable_mile = dCable_m * CONVERT.m2mile
    
    # Calculate individual cost components
    Cost_kE_cable = COST.A_cable * dCable_km * Prated_MW**COST.E_cable # table 7
    Cost_kE_gridCon = COST.A_gridCon * Prated_MW # table 7
    Cost_kE_moor = 2 * dMoor_m * (COST.A_moor + COST.B_moor * F_pull_mTon) * 10**-3 # table 6
    Cost_kE_blade = NumTurbine * COST.A_blade * F_blade_kN * (2 * Radius)   # table 14
    Cost_kE_generator = NumTurbine * COST.A_generator * Prated_kW**COST.E_generator  # table 14
    Cost_kE_misc = (COST.switchgearCable + COST.controlRectifier) * Prated_MW  # table 14
    Cost_kE_hub = (COST.hub_SwitchGearCable + COST.hub_Converter + COST.hub_OffshoreSubstation + COST.hub_OtherSystems) * Prated_MW
    Cost_kE_cableInstall = COST.A_cableInstall * (dCable_mile / COST.B1_cableInstall + dCable_mile / COST.B2_cableInstall + dCable_mile / COST.B3_cableInstall) * CONVERT.hrs2days
    
    # Summarize CAPEX
    CAPEX_kE = (1 + COST.A_dev) * sum([Cost_kE_cable, Cost_kE_gridCon, Cost_kE_moor, Cost_kE_blade, Cost_kE_generator, Cost_kE_misc, Cost_kE_hub, Cost_kE_cableInstall])
    CAPEX_USD = CAPEX_kE * CONVERT.kE2E * CONVERT.euro2dollar
    OPEX_USD = COST.A_opex * CAPEX_USD

    # Calculate discounted OPEX over system life
    C_opex_sum = sum(OPEX_USD * ((1 + COST.interest_rate) ** (-tt)) for tt in range(1, int(COST.sys_life + 1)))

    # Calculate total energy production
    TotalDuration_seconds = np.mean(np.diff(t)) * len(t)
    Et = NumTurbine * sp.integrate.simpson(Pelec)*np.mean(np.diff(t)) / (TotalDuration_seconds) * (365 * 24 * 3600) / 3600 / 1000  # Convert to kWh

    # Calculate discounted energy production
    C_et_sum = sum(Et * ((1 + COST.interest_rate) ** (-tt)) for tt in range(1, int(COST.sys_life + 1)))

    # Calculate LCOE
    LCOE = (CAPEX_USD + C_opex_sum) / C_et_sum

    # Prepare cost breakdown for output
    CostBreakdown = {
        "LCOE": LCOE,
        "CAPEX": CAPEX_USD,
        "Et": Et,
        "cable": Cost_kE_cable * CONVERT.kE2E * CONVERT.euro2dollar,
        "grid connect": Cost_kE_gridCon * CONVERT.kE2E * CONVERT.euro2dollar,
        "moor": Cost_kE_moor * CONVERT.kE2E * CONVERT.euro2dollar,
        "blade": Cost_kE_blade * CONVERT.kE2E * CONVERT.euro2dollar,
        "generator": Cost_kE_generator * CONVERT.kE2E * CONVERT.euro2dollar,
        "misc": Cost_kE_misc * CONVERT.kE2E * CONVERT.euro2dollar,
        "hub": Cost_kE_hub * CONVERT.kE2E * CONVERT.euro2dollar,
        "cable install": Cost_kE_cableInstall * CONVERT.kE2E * CONVERT.euro2dollar,
    }

    return LCOE, CostBreakdown



def printCostBreakdown(CostBreakdown):
    # Print cost breakdown
    print("="*60)  # Print a line of "=" characters at the beginning
    print("Cost Breakdown:")
    for cost_item, cost_value in CostBreakdown.items():
        print(f"{cost_item}: ${cost_value:.2f}")
