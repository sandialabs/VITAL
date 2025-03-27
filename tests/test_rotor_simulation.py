import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import pickle

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from module_rotor_simulation import RotorSimulation
# from constGlobal import ConstantsGlobal
from module_rotor import RotorData
from module_tidal import TidalData

plt.style.use('tableau-colorblind10')

def test_rotor_simulation():
    # Define tidal data parameters
    station = "PCT3716"  # Site 2
    startdate = 20200201  # yyyyMMdd
    rangeHr = 2 * 7 * 24  # Two weeks
    timestep = 5.0  # Timestep in seconds

    # Initialize TidalData class
    tidal_data = TidalData(station, startdate, rangeHr, timestep)
    city_data_file = "/Users/akeow/Desktop/VITAL/HDPS_TeamerClean/data/AlaskaCityLatLong.txt"
    flow_speeds, times, dmoor_m, lat_rad, lon_rad, station_name, nearest_city, cable_length = tidal_data.load_tidal_data(city_data_file)

    # Define simulation parameters
    config = {
        'Radius': 1.0,
        'Prated': 1000.0,
        'dCable': 10.0,
        'dMoor': dmoor_m,
        'Uinf': flow_speeds,
        't': times,
        'CpFunc': None,  # Placeholder, will be set later
        'CqFunc': None,  # Placeholder, will be set later
        'CtFunc': None,  # Placeholder, will be set later
        'CpOpt': None,  # Placeholder, will be set later
        'TSROpt': None,  # Placeholder, will be set later
        'Umin': 0.1,
        'withBrake': True,
        'control_strategy': 'optimal',
        'attachment_method': 'solid_bar'
    }

    # Initialize RotorData class
    rotor_filename = "/Users/akeow/Desktop/VITAL/HDPS_TeamerClean/data/Sitkana_rotor_data_blade_1.txt"
    rotor_data = RotorData(rotor_filename)

    # Set Cp, Cq, and Ct functions from RotorData class
    config['CpFunc'] = rotor_data.get_cp
    config['CqFunc'] = rotor_data.get_cq
    config['CtFunc'] = rotor_data.get_ct

    # Set CpOpt and TSROpt from RotorData class
    config['CpOpt'] = rotor_data.CpOpt
    config['TSROpt'] = rotor_data.TSROpt
    config['TSRmax'] = rotor_data.TSRmax
    config['efficiency'] = 0.9

    # Define the four configurations
    configurations = [
        {'control_strategy': 'optimal', 'attachment_method': 'cable'},
        {'control_strategy': 'optimal', 'attachment_method': 'solid_bar'},
        {'control_strategy': 'constant_speed', 'attachment_method': 'cable'},
        {'control_strategy': 'constant_speed', 'attachment_method': 'solid_bar'}
    ]

    results = []

    # Run simulations for each configuration
    for i, config_update in enumerate(configurations):
        config.update(config_update)
        rotor_sim = RotorSimulation(config)
        rotor_sim.simulate()
        result = rotor_sim.get_results()
        results.append(result)

        # Save results to file
        output_filename = f"simulation_results_{i}.pkl"
        with open(output_filename, 'wb') as f:
            pickle.dump(result, f)

    labels = ['Optimal Cable', 'Optimal Solid Bar', 'Constant Speed Cable', 'Constant Speed Solid Bar']
    colors = ['b', 'g', 'r', 'c']
    linestyles = ['-', '--', '-.', ':']

    # Plot results for each signal type in separate figures
    signal_titles = [
        'Rotor Speed (w) vs Time',
        'TSR vs Time',
        'Control Torque (Tc) vs Time',
        'Hydrodynamic Torque (Th) vs Time',
        'Brake Torque (Tbrake) vs Time',
        'Thrust Force (Ft) vs Time',
        'Electrical Power (Pelec) vs Time',
        'Theta Turbine vs Time',
        'Hub Depth (dHub) vs Time',
        'Adjusted Flow Speed (Uinf_adjusted) vs Time'
    ]

    signal_keys = [
        'w', 'TSR', 'Tc', 'Th', 'Tbrake', 'Ft', 'Pelec', 'theta_turbine', 'dHub', 'Uinf_adjusted'
    ]

    for title, key in zip(signal_titles, signal_keys):
        plt.figure(figsize=(10, 6))
        for i, result in enumerate(results):
            if key == 'Uinf_adjusted':
                plt.plot(config['t'], config['Uinf'], label='Uinf', linestyle='--', color='k')
            plt.plot(config['t'], result[key], label=labels[i], color=colors[i], linestyle=linestyles[i])
        plt.title(title)
        plt.xlabel('Time [s]')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    test_rotor_simulation()
