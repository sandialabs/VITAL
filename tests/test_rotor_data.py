import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import argparse

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from module_rotor import RotorData

plt.style.use('tableau-colorblind10')

def test_rotor_data(rotor_filename, cpmin_filename=None):
    # Initialize RotorData class with Cpmin data if provided
    rotor_data = RotorData(rotor_filename, cpmin_filename)

    # Test find_max_cp functionality
    CpOpt, TSROpt = rotor_data.find_max_cp()
    print(f"Maximum Cp (CpOpt): {CpOpt}")
    print(f"Corresponding TSR (TSROpt): {TSROpt}")

    # Define TSR test range
    TSR_test = np.linspace(0.001, rotor_data.TSRmax + 1, 1000)
    print(rotor_data.get_cq(0.001))

    # Get interpolated values
    Cp_test = rotor_data.get_cp(TSR_test)
    Ct_test = rotor_data.get_ct(TSR_test)
    Cq_test = rotor_data.get_cq(TSR_test)
    Cpmin_test = rotor_data.get_cpmin(TSR_test)

    # Plot Cp, Ct, Cq, and Cpmin vs TSR
    plt.figure(figsize=(10, 8))

    plt.subplot(4, 1, 1)
    plt.plot(rotor_data.tsr, rotor_data.cp, 'o', label='Original Cp')
    plt.plot(TSR_test, Cp_test, '-', label='Interpolated Cp')
    plt.xlabel('TSR')
    plt.ylabel('Cp')
    plt.title('Cp vs TSR')
    plt.legend()
    plt.grid(True)

    plt.subplot(4, 1, 2)
    plt.plot(rotor_data.tsr, rotor_data.ct, 'o', label='Original Ct')
    plt.plot(TSR_test, Ct_test, '-', label='Interpolated Ct')
    plt.xlabel('TSR')
    plt.ylabel('Ct')
    plt.title('Ct vs TSR')
    plt.legend()
    plt.grid(True)

    plt.subplot(4, 1, 3)
    plt.plot(rotor_data.tsr, rotor_data.get_cq(rotor_data.tsr), 'o', label='Original Cq')
    plt.plot(TSR_test, Cq_test, '-', label='Interpolated Cq')
    plt.xlabel('TSR')
    plt.ylabel('Cq')
    plt.title('Cq vs TSR')
    plt.legend()
    plt.grid(True)

    plt.subplot(4, 1, 4)
    plt.plot(rotor_data.tsr, rotor_data.cpmin, 'o', label='Original Cpmin')
    plt.plot(TSR_test, Cpmin_test, '-', label='Interpolated Cpmin')
    plt.xlabel('TSR')
    plt.ylabel('Cpmin')
    plt.title('Cpmin vs TSR')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    cpmin_filename = "/Users/akeow/Desktop/VITAL/HDPS_TeamerClean/data/Cpmin_data.json"
    rotor_filename = "/Users/akeow/Desktop/VITAL/HDPS_TeamerClean/data/Sandia_rotor_data.txt"

    test_rotor_data(rotor_filename, cpmin_filename)

    # rotor_filename = "Sitkana_rotor_data_blade_1.txt"

    # test_rotor_data(rotor_filename)
