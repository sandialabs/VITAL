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
    # Generate time array from 0 to 24*7*3600 with a step of 1 second
    t = np.arange(0, 24*7*3600 + 1, 10)

    # Generate random Pelec values between 0 and 1 with the same length as t
    Pelec = np.sin(2*np.pi*t/(24*3600))*10 + 100 + np.sin(2*np.pi*t/(2*24*3600))*5 + np.sin(3*np.pi*t/(2*24*3600))*5

    plt.plot(t,Pelec)

    battery_charging = BatteryCharging(BatteryCapacity_kWh)

    num_batteries_charged, charge_times_hr = battery_charging.chargeBattery_continuous(Pelec, t)
    print(f"Number of batteries charged: {num_batteries_charged}")
    print(f"Charge times (hours): {charge_times_hr}")

    daily_charging_results = battery_charging.chargeBattery_perDay(Pelec, t)
    print(f"Daily charging results: {daily_charging_results}")

if __name__ == "__main__":
    test_battery_charging()