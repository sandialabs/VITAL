import numpy as np
import sys
import os
import matplotlib.pyplot as plt
plt.style.use('tableau-colorblind10')

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from module_battery_charging import BatteryCharging

# Test the module
def test_battery_charging():
    BatteryCapacity_kWh = 2.5  # Example battery capacity in kWh
    number_of_turbines = 2  # Example number of turbines
    turbulence_intensity = 0.1  # Example turbulence intensity

    # Generate time array from 0 to 24*7*3600 with a step of 10 seconds
    t = np.arange(0, 24 * 7 * 3600 + 1, 10)

    # Generate random Pelec values based on a sinusoidal function
    Pelec = np.sin(2 * np.pi * t / (24 * 3600)) * 10 + 100 + np.sin(2 * np.pi * t / (2 * 24 * 3600)) * 5 + np.sin(3 * np.pi * t / (2 * 24 * 3600)) * 5

    plt.plot(t, Pelec)
    plt.title('Electrical Power Profile')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (W)')
    plt.grid(True)
    plt.show()

    # Instantiate the BatteryCharging class with the required parameters
    battery_charging = BatteryCharging(BatteryCapacity_kWh, number_of_turbines, turbulence_intensity)

    # Charge the battery continuously
    num_batteries_charged, charge_times_hr = battery_charging.chargeBattery_continuous(Pelec, t)
    print(f"Number of batteries charged: {num_batteries_charged}")
    print(f"Charge times (hours): {charge_times_hr}")

    # Uncomment the following lines to test daily charging results
    # daily_charging_results = battery_charging.chargeBattery_perDay(Pelec, t)
    # print(f"Daily charging results: {daily_charging_results}")

if __name__ == "__main__":
    test_battery_charging()
