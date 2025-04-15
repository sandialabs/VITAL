import numpy as np
import scipy as sp
from constGlobal import ConstantsGlobal
from constUnitConvert import ConstantsUnitConversion
from module_cost_config import COST_FUNCTIONS
from module_cost_calculations import operating_cost_SITKANA

# Initialize global constants from modules
GLOBAL = ConstantsGlobal()
CONVERT = ConstantsUnitConversion()

class LCOE: 

    # def __init__(self, turbine_radius, turbine_rated_power, number_of_turbines, hub_depth, 
    #              lifetime=20, discount_rate=0.01, turbulence_intensity=0, customer='customer_A', application='grid_connection'):
    def __init__(self, turbine_radius, turbine_rated_power, number_of_turbines, hub_depth, 
                 lifetime, discount_rate, turbulence_intensity, customer, application):
        self.turbine_radius = turbine_radius
        self.turbine_rated_power = turbine_rated_power
        self.number_of_turbines = number_of_turbines
        self.hub_depth = hub_depth
        self.lifetime = lifetime
        self.discount_rate = discount_rate
        self.turbulence_intensity = turbulence_intensity
        self.customer = customer
        self.application = application

        # Load cost functions based on customer and application configuration
        self.rotor_and_drivetrain_costs = COST_FUNCTIONS[self.customer]['rotor_and_drivetrain']
        self.application_costs = COST_FUNCTIONS[self.customer]['applications'][self.application]

        # Initialize CAPEX components
        self.capex = {}

        # Initialize OPEX components
        self.opex = {}

        self.instantaneous_power = None
        self.time_series = None

    def set_instantaneous_power(self, power_data, time_data):
        self.instantaneous_power = np.array(power_data) / (1 + self.turbulence_intensity) ** 3 * self.number_of_turbines
        self.time_series = np.array(time_data)

    def calculate_annual_energy(self):
        if self.instantaneous_power is None or self.time_series is None:
            raise ValueError("Instantaneous power data or time series not set.")
        
        dt = np.mean(np.diff(self.time_series))
        total_energy_generated = sp.integrate.simpson(self.instantaneous_power, dx=dt)  # Total energy in Joules
        average_power = total_energy_generated / (self.time_series[-1] - self.time_series[0])  # Average power in watts
        annual_energy = average_power * 8760  / 1000  # Convert to annual energy (kWh)
        return annual_energy

    def calculate_capacity_factor(self):
        annual_energy = self.calculate_annual_energy()
        max_annual_energy = self.turbine_rated_power * 8760 / 1000  # Maximum annual energy in kWh
        capacity_factor = annual_energy / max_annual_energy
        return capacity_factor

    def calculate_total_capex(self, 
                              dCable_m, 
                              dMoor_m,
                              F_vessel_thrust,
                              F_turbine_thrust,
                              vessel_volume_m3,
                              BatteryCapacity_kWh=None):
        
        # If the application is 'grid_connection', BatteryCapacity_kWh is set to 0 regardless of whether the user provided a value or not.
        # If the application is not 'grid_connection' and the user did not provide a value for BatteryCapacity_kWh (i.e., it is None), a ValueError will be raised.
        # If the application is not 'grid_connection' and the user provided a value for BatteryCapacity_kWh that is less than or equal to zero, a ValueError will be raised.

        
        # Check application type and set BatteryCapacity_kWh accordingly
        if self.application == 'grid_connection':
            BatteryCapacity_kWh = 0
        elif BatteryCapacity_kWh <= 0:
            raise ValueError("Battery capacity must be greater than zero for non-grid_connection applications.")


        # Common parameters
        common_params = {
            'turbine_radius_m': self.turbine_radius,
            'turbine_rated_power_W': self.turbine_rated_power,
            'number_of_turbines': self.number_of_turbines,
            'electrical_cable_length_m': dCable_m,
            'mooring_cable_length_m': dMoor_m,
            'force_vessel_drag_N': F_vessel_thrust,
            'force_turbine_thrust_N': F_turbine_thrust,
            'vessel_volume_m3': vessel_volume_m3,
            'BatteryCapacity_kWh': BatteryCapacity_kWh
        }

        # Calculate rotor and drivetrain costs
        for cost_name, cost_function in self.rotor_and_drivetrain_costs.items():
            self.capex[cost_name] = cost_function(**common_params)

        # Calculate application-specific costs
        for cost_name, cost_function in self.application_costs.items():
            self.capex[cost_name] = cost_function(**common_params)

        # # Print individual CAPEX components
        # print("Individual CAPEX components:")
        # for cost_name, cost_value in self.capex.items():
        #     print(f"{cost_name}: ${cost_value:.2f}")

        # Sum all CAPEX components
        total_capex_usd = sum(self.capex.values())
        
        # Add development cost (Only for HDPS)
        if self.customer == 'customer_A':  # HDPS
            total_capex_usd *= (1 + 0.05)
        
        return total_capex_usd, self.capex


    def calculate_total_opex(self, total_capex):
        # Calculate OPEX based on CAPEX
        if self.customer == 'customer_B': # SITKANA
            total_opex_usd = operating_cost_SITKANA(self.turbine_rated_power,self.number_of_turbines)
        else:
            total_opex_usd = 0.04 * total_capex

        return total_opex_usd

    def calculate_present_value_of_costs(self, total_capex, total_opex):
        # Calculate present value of costs
        pvc = total_capex + total_opex * np.sum([1 / (1 + self.discount_rate)**t for t in range(1, self.lifetime + 1)])
        return pvc

    def calculate_present_value_of_energy(self, annual_energy):
        # Calculate present value of electricity generation
        pve = annual_energy * np.sum([1 / (1 + self.discount_rate)**t for t in range(1, self.lifetime + 1)])
        return pve

    def calculate_lcoe(self, dCable_m, 
                              dMoor_m,
                              F_vessel_thrust,
                              F_turbine_thrust,
                              vessel_volume_m3,
                              BatteryCapacity_kWh=None):
        
        # If the application is 'grid_connection', BatteryCapacity_kWh is set to 0 regardless of whether the user provided a value or not.
        # If the application is not 'grid_connection' and the user did not provide a value for BatteryCapacity_kWh (i.e., it is None), a ValueError will be raised.
        # If the application is not 'grid_connection' and the user provided a value for BatteryCapacity_kWh that is less than or equal to zero, a ValueError will be raised.

        # Check application type and set BatteryCapacity_kWh accordingly
        if self.application == 'grid_connection':
            BatteryCapacity_kWh = 0
        elif BatteryCapacity_kWh <= 0:
            raise ValueError("Battery capacity must be greater than zero for non-grid_connection applications.")


        # Calculate total CAPEX
        total_capex, capex_components = self.calculate_total_capex(dCable_m, 
                              dMoor_m,
                              F_vessel_thrust,
                              F_turbine_thrust,
                              vessel_volume_m3,
                              BatteryCapacity_kWh=None)
        
        # Output individual CAPEX components to user
        print("Individual CAPEX components:")
        for cost_name, cost_value in capex_components.items():
            print(f"{cost_name}: ${cost_value:.2f}")
        
        # Calculate total OPEX
        total_opex = self.calculate_total_opex(total_capex)
        
        # Calculate annual energy generation
        annual_energy = self.calculate_annual_energy()
        
        # Calculate present value of costs and energy
        pvc = self.calculate_present_value_of_costs(total_capex, total_opex)
        pve = self.calculate_present_value_of_energy(annual_energy)
        
        # Calculate LCOE
        if pve == 0:
            raise ValueError("Present value of energy is zero, cannot calculate LCOE.")
        
        lcoe = pvc / pve
        return lcoe
