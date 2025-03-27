import numpy as np
from constUnitConvert import ConstantsUnitConversion
from unit_weight import UnitWeight  # Import the function from the new file

CONVERT = ConstantsUnitConversion()
 
# mooring_cable_length_m, 
# force_vessel_drag_N, 
# turbine_radius_m, 
# force_turbine_thrust_N
# turbine_rated_power_W, 
# number_of_turbines
# electrical_cable_length_m
# vessel_volume_m3
# BatteryCapacity_kWh


def calculate_electrical_cable_cost(turbine_radius_m, 
                                    turbine_rated_power_W, 
                                    number_of_turbines, 
                                    electrical_cable_length_m, 
                                    mooring_cable_length_m, 
                                    force_vessel_drag_N, 
                                    force_turbine_thrust_N, 
                                    vessel_volume_m3=None, 
                                    BatteryCapacity_kWh=None):
    # Lopez table 7
    electrical_cable_length_km = electrical_cable_length_m * CONVERT.m2km
    system_total_power_MW = number_of_turbines * turbine_rated_power_W * CONVERT.W2MW
    electrical_cable_cost_kE = 50.0 * electrical_cable_length_km * system_total_power_MW**0.5
    electrical_cable_cost_USD = electrical_cable_cost_kE * CONVERT.kE2E * CONVERT.euro2dollar
    return electrical_cable_cost_USD

def calculate_mooring_cost(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    # Lopez table 6
    mooring_force_mTon = np.max(np.abs(force_vessel_drag_N + number_of_turbines * force_turbine_thrust_N)) * CONVERT.N2mTon
    mooring_cost_kE = 2 * mooring_cable_length_m * (60.0   + 0.25 * mooring_force_mTon) * 10**-3 
    mooring_cost_USD = mooring_cost_kE * CONVERT.kE2E * CONVERT.euro2dollar
    return mooring_cost_USD

def calculate_grid_connection_cost(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    # Lopez table 7
    turbine_rated_power_MW = turbine_rated_power_W * number_of_turbines * CONVERT.W2MW
    grid_connection_cost_kE = 20.0 * turbine_rated_power_MW 
    grid_connection_cost_USD = grid_connection_cost_kE * CONVERT.kE2E * CONVERT.euro2dollar
    return grid_connection_cost_USD

def calculate_blade_cost(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    # Lopez table 14
    force_turbine_thrust_kN = np.max(np.abs(force_turbine_thrust_N)) * CONVERT.N2kN
    blade_cost_kE = number_of_turbines * 0.004 * force_turbine_thrust_kN * (2 * turbine_radius_m)
    blade_cost_USD = blade_cost_kE * CONVERT.kE2E * CONVERT.euro2dollar
    return blade_cost_USD

def calculate_generator_cost(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    # Lopez table 14
    turbine_rated_power_kW = turbine_rated_power_W * CONVERT.W2kW
    generator_cost_kE = number_of_turbines * 0.39 * turbine_rated_power_kW**0.8
    generator_cost_USD = generator_cost_kE * CONVERT.kE2E * CONVERT.euro2dollar
    return generator_cost_USD

def calculate_misc_cost(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    # Additional electrical components cost (based on Lopez table 6)
    turbine_rated_power_MW = turbine_rated_power_W * number_of_turbines * CONVERT.W2MW
    switchgear_cable_cost_kE = 8.0 * turbine_rated_power_MW
    control_rectifier_cost_kE = 25.0 * turbine_rated_power_MW
    misc_cost_USD = (control_rectifier_cost_kE + switchgear_cable_cost_kE) * CONVERT.kE2E * CONVERT.euro2dollar
    return misc_cost_USD

def calculate_hub_cost(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    # Farm hub platform costs (based on Lopez table 7)
    turbine_rated_power_MW = turbine_rated_power_W * number_of_turbines * CONVERT.W2MW
    hub_switchgear_cable_cost_kE  = 10.0 * turbine_rated_power_MW
    hub_converter_cost_kE  = 50.0 * turbine_rated_power_MW
    hub_offshore_substation_cost_kE  = 80.0 * turbine_rated_power_MW
    hub_other_systems_cost_kE  = 8.0 * turbine_rated_power_MW
    hub_cost_USD = (hub_switchgear_cable_cost_kE + hub_converter_cost_kE + hub_offshore_substation_cost_kE + hub_other_systems_cost_kE) * CONVERT.kE2E * CONVERT.euro2dollar
    return hub_cost_USD

def calculate_cable_installation_cost(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    # Cable installation cost (based on Lopez table 7)
    electrical_cable_length_mile = electrical_cable_length_m * CONVERT.m2mile
    cable_installation_cost_kE = 120.0 * (electrical_cable_length_mile / (4.1 / 24) + electrical_cable_length_mile / 2.3 + electrical_cable_length_mile / 8.6) * CONVERT.hrs2days
    cable_installation_cost_USD = cable_installation_cost_kE * CONVERT.kE2E * CONVERT.euro2dollar
    return cable_installation_cost_USD

# Sitkana Cost
# Unit cost
def calculate_rotor_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    # Small Scale
    # rotor_cost_USD_perUnit = 280*turbine_radius_m**2 + 409.43*turbine_radius_m - 186.00

    # Large Scale
    rotor_cost_USD_perUnit = 5.58*turbine_radius_m**2 + 8.26*turbine_radius_m -3.75
    rotor_cost_USD = rotor_cost_USD_perUnit*number_of_turbines
    return rotor_cost_USD 

def calculate_rotor_construction_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    # Small Scale
    # rotor_construction_cost_USD_perUnit = -7.81*turbine_radius_m**2 + 391.41*turbine_radius_m - 168.75

    # Large Scale
    rotor_construction_cost_USD_perUnit = 6.53*turbine_radius_m + 0.03
    rotor_construction_cost_USD = rotor_construction_cost_USD_perUnit*number_of_turbines
    return rotor_construction_cost_USD 

def calculate_steel_component_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    steel_component_cost_USD_perUnit = 42.86*turbine_radius_m**2 + 261.43*turbine_radius_m - 31.25
    steel_component_cost_USD = steel_component_cost_USD_perUnit*number_of_turbines
    return steel_component_cost_USD 

def calculate_generator_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    generator_cost_USD_perUnit = -2.20e-06*turbine_rated_power_W**2 + 2.12e-01*turbine_rated_power_W + 1.42e+02
    generator_cost_USD = generator_cost_USD_perUnit*number_of_turbines
    return generator_cost_USD 

def calculate_assembly_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    assembly_cost_USD_perUnit = -4.40e-07*turbine_rated_power_W**2 + 4.23e-02*turbine_rated_power_W + 1.28e+02
    assembly_cost_USD = assembly_cost_USD_perUnit*number_of_turbines
    return assembly_cost_USD 

def calculate_concrete_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    concrete_cost_USD_perUnit = 6.65e-09*turbine_rated_power_W**2 + 5.15e-03*turbine_rated_power_W + 8.46e-01
    concrete_cost_USD = concrete_cost_USD_perUnit*number_of_turbines
    return concrete_cost_USD 

def calculate_gearbox_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    a = -645.31
    b = 120.38
    gearbox_cost_USD_perUnit = a + b * np.log(turbine_rated_power_W) 
    gearbox_cost_USD = gearbox_cost_USD_perUnit*number_of_turbines
    return gearbox_cost_USD  

def calculate_charge_controller_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None): 
    # a = -2553.9455502056103 
    # b = 398.4982065789759
    # charge_controller_USD_perUnit = a + b * np.log(turbine_rated_power_W) 
    a = 12.71
    b = -222.70
    charge_controller_USD_perUnit = a*np.sqrt(turbine_rated_power_W) + b
    charge_controller_cost_USD = charge_controller_USD_perUnit*number_of_turbines

    return charge_controller_cost_USD  



# System level cost
# def calculate_platform_cost_SITKANA(turbine_radius_m, 
#                             turbine_rated_power_W, 
#                             number_of_turbines, 
#                             electrical_cable_length_m, 
#                             mooring_cable_length_m, 
#                             force_vessel_drag_N, 
#                             force_turbine_thrust_N, 
#                             vessel_volume_m3=None, 
#                             BatteryCapacity_kWh=None):
#     if vessel_volume_m3 is None:
#         raise ValueError("vessel_volume_m3 parameter is required for platform cost calculation.")
#     PlasticDensity = 1000
#     return vessel_volume_m3 * PlasticDensity * 10.0

def calculate_platform_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):

    total_weight = UnitWeight(turbine_radius_m, turbine_rated_power_W)
    platformVolume = total_weight/1020 # for neutral buoyancy
    # density of platform given by Lance is 1020 (?)
    new_min = 0.049019608 # np.min(df['Platform Volume (m3)'])
    new_max = 3.921568627 # np.max(df['Platform Volume (m3)'])
    old_min = 0.012327232416666669 # np.min(total_weight_vector/1020)
    old_max = 0.36467610084313723 # np.max(total_weight_vector/1020)
    platformVolume_adjusted = new_min + ((platformVolume - old_min) / (old_max - old_min)) * (new_max - new_min)

    a = 3426.95
    b = 0.43
    cost = a * platformVolume_adjusted**b
    return cost

def calculate_anchor_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    anchor_cost_USD_perUnit = 1.27542203e+02 + 1.57545238e-02 *(turbine_rated_power_W *number_of_turbines)
    anchor_cost_USD = anchor_cost_USD_perUnit

    return anchor_cost_USD  



# def calculate_electrical_cable_cost_SITKANA(turbine_radius_m, 
#                             turbine_rated_power_W, 
#                             number_of_turbines, 
#                             electrical_cable_length_m, 
#                             mooring_cable_length_m, 
#                             force_vessel_drag_N, 
#                             force_turbine_thrust_N, 
#                             vessel_volume_m3=None, 
#                             BatteryCapacity_kWh=None):
#     CostLand_Mile = 150000
#     CostWater_Mile = 50000
#     mile2meter = 1609.34

#     electrical_cable_cost_USD = CostWater_Mile*0.75*electrical_cable_length_m/mile2meter + CostLand_Mile*0.25*electrical_cable_length_m/mile2meter

#     return electrical_cable_cost_USD 

def calculate_battery_cost_SITKANA(turbine_radius_m, 
                            turbine_rated_power_W, 
                            number_of_turbines, 
                            electrical_cable_length_m, 
                            mooring_cable_length_m, 
                            force_vessel_drag_N, 
                            force_turbine_thrust_N, 
                            vessel_volume_m3=None, 
                            BatteryCapacity_kWh=None):
    if BatteryCapacity_kWh is None:
        raise ValueError("BatteryCapacity_kWh parameter is required for battery cost calculation.")

    battery_cost_USD = 150*BatteryCapacity_kWh

    return battery_cost_USD



def operating_cost_SITKANA(turbine_rated_power,number_of_turbines):
    System_Rated_Power = number_of_turbines*turbine_rated_power
    a = 4.71130313e+05
    b = 2.74814600e-04
    c = 6.59375848e+04
    return a * np.exp(-b * System_Rated_Power) + c
