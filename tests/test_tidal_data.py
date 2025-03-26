import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import unittest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from module_tidal import TidalData
from constUnitConvert import ConstantsUnitConversion

CONVERT = ConstantsUnitConversion()

# Use color-blind friendly style
plt.style.use('tableau-colorblind10')

def test_tidal_data():
    # Define parameters for tidal data acquisition
    station = "SEA0202"  # Site 2
    startdate = 20200201  # yyyyMMdd
    rangeHr = 2 * 7 * 24  # Two weeks
    timestep = 5.0
    city_data_file = "/Users/akeow/Desktop/VITAL/HDPS_TeamerClean/data/AlaskaCityLatLong.txt"

    # Load tidal data using the TidalData class
    tidal_data = TidalData(station, startdate, rangeHr, timestep)
    Uinf, t, dMoor, buoyLatitude, buoyLongitude, station_name, nearest_city, cable_length = tidal_data.load_tidal_data(city_data_file)

    # Print the results to verify
    print(f'Station name: {station_name}')
    print(f'Mooring depth: {dMoor} [m]')
    print(f'Latitude: {buoyLatitude} [rad]')
    print(f'Longitude: {buoyLongitude} [rad]')
    print(f'Nearest city: {nearest_city}')
    print(f'Cable length: {cable_length * CONVERT.m2mile:.2f} miles')
    print(f'Flow speeds (first 10): {Uinf[:10]} [m/s]')
    print(f'Times (first 10): {t[:10]} [s]')


if __name__ == "__main__":
    test_tidal_data()
