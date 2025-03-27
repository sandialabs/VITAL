import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from module_lcoe import LCOE
import numpy as np

# Example code to test the calculate_total_capex and LCOE calculation
if __name__ == "__main__":
    # Parameters
    turbine_radius = 1  # meters
    turbine_rated_power = 1 * 10000  # kW to W
    number_of_turbines = 1
    dCable_m = 100  # meters
    dMoor_m = 50  # meters
    dHub_m = 10
    F_turbine_thrust = 1000  # N
    F_vessel_thrust = 1000  # N
    vessel_volume_m3 = 100  # m^3
    BatteryCapacity_kWh = 10  # kWh

    # Create an instance of the LCOE class
    lcoe_calculator = LCOE(turbine_radius, 
                           turbine_rated_power, 
                           number_of_turbines, 
                           hub_depth=dHub_m, 
                           customer='customer_B', 
                           application='battery_charging')
    
    # lcoe_calculator = LCOE(turbine_radius, 
    #                     turbine_rated_power, 
    #                     number_of_turbines, 
    #                     hub_depth=dHub_m, 
    #                     customer='customer_A', 
    #                     application='grid_connection')

    # Calculate total CAPEX
    total_capex = lcoe_calculator.calculate_total_capex(dCable_m, 
                                                        dMoor_m, 
                                                        F_vessel_thrust, 
                                                        F_turbine_thrust, 
                                                        vessel_volume_m3, 
                                                        BatteryCapacity_kWh)
    print(f"Total CAPEX: {total_capex[0]:.2f} USD")

    # Arbitrary Pelec(t) for instantaneous power data
    power_data = np.random.rand(8760) * turbine_rated_power  # Random power data for one year in watts
    time_data = np.linspace(0, 8760 * 3600, len(power_data))  # Time data in seconds for one year

    # Set instantaneous power data
    lcoe_calculator.set_instantaneous_power(power_data, time_data)

    # Calculate annual energy generation
    annual_energy = lcoe_calculator.calculate_annual_energy()
    print(f"Annual Energy: {annual_energy:.2f} kWh")

    # Calculate capacity factor
    capacity_factor = lcoe_calculator.calculate_capacity_factor()
    print(f"Capacity Factor: {capacity_factor:.2%}")

    # Calculate LCOE
    lcoe = lcoe_calculator.calculate_lcoe(dCable_m, 
                              dMoor_m,
                              F_vessel_thrust,
                              F_turbine_thrust,
                              vessel_volume_m3,
                              BatteryCapacity_kWh)
    print(f"LCOE: {lcoe:.2f} USD/kWh")
