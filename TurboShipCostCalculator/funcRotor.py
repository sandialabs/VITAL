import glob
import autograd.numpy as np  # Used for operations that support automatic differentiation
import pandas as pd
import scipy as sp
from natsort import natsorted, ns  # Natural sorting
from scipy.spatial.transform import Rotation  # For rotating geometries
from scipy.spatial import ConvexHull  # For calculating convex hulls, useful in volume calculations

import constRotor  # Module containing rotor-specific constants
ROTOR = constRotor.ConstantsRotor()  # Instance of rotor constants

def loadRotorSurfaces(folderlocation, myTSRmax, myTSRmin):
    """
    Loads rotor surface data from output files, calculates spline functions for Cp, Ct, and Cpmin, and returns optimal TSR and Cp values.
    
    Parameters:
    - folderlocation (str): Path to the folder containing rotor surface data files.
    - myTSRmax (float): Maximum TSR value to consider.
    - myTSRmin (float): Minimum TSR value to consider.
    
    Returns:
    - spline_Cp, spline_Ct (function): Spline functions for Cp and Ct over TSR.
    - Cpmin_functions (list of functions): List of spline functions for minimum pressure coefficient Cpmin values at different span ratios.
    - spanRatio (list of floats): List of span ratios used in the analysis.
    - Cp_opt (float): Optimal Cp value found.
    - TSR_opt (float): TSR corresponding to the optimal Cp value.
    """

    outFileList = glob.glob1(folderlocation, "*.out")
    outFileList = natsorted(outFileList, key=lambda x: int(x.split('.')[1]))

    if not outFileList:
        raise Exception("Sorry list is empty. Folder does not contain any *.dot files")

    FileListLen = len(outFileList)
    rotordata_TSR = np.zeros(FileListLen)
    rotordata_pitch = np.zeros(FileListLen)
    rotordata_Cp = np.zeros(FileListLen)
    rotordata_Cq = np.zeros(FileListLen)
    rotordata_Ct = np.zeros(FileListLen)
    rotordata_Cpmin20 = np.zeros(FileListLen)
    rotordata_Cpmin19 = np.zeros(FileListLen)
    rotordata_Cpmin18 = np.zeros(FileListLen)

    for x in range(FileListLen):
        fullfile_withpath = folderlocation + outFileList[x]
        data = pd.read_table(fullfile_withpath, header=0, skiprows=[0, 1, 2, 3, 4, 5, 7], sep='\s+')

        rotordata_TSR[x] = data['RtTSR'][0]
        rotordata_pitch[x] = data['BldPitch1'][0]
        rotordata_Cp[x] = data['RtAeroCp'][0]
        rotordata_Cq[x] = data['RtAeroCq'][0]
        rotordata_Ct[x] = data['RtAeroCt'][0]
        rotordata_Cpmin20[x] = data['AB1N020CpMin'][0]
        rotordata_Cpmin19[x] = data['AB1N019CpMin'][0]
        rotordata_Cpmin18[x] = data['AB1N018CpMin'][0]

    pitchidx = rotordata_pitch == 0
    Cp_data_val = np.insert(rotordata_Cp[pitchidx], 0, 0.0)
    Cp_data_val = np.append(Cp_data_val, 0.0)

    Ct_data_val = np.insert(rotordata_Ct[pitchidx], 0, 0.0)
    Ct_data_val = np.append(Ct_data_val, Ct_data_val[-1])

    Cpmin20_data_val = np.insert(rotordata_Cpmin20[pitchidx], 0, np.ceil(rotordata_Cpmin20[pitchidx][0]))
    Cpmin20_data_val = np.append(Cpmin20_data_val, Cpmin20_data_val[-1])

    Cpmin19_data_val = np.insert(rotordata_Cpmin19[pitchidx], 0, -9.0)
    Cpmin19_data_val = np.append(Cpmin19_data_val, Cpmin19_data_val[-1])

    Cpmin18_data_val = np.insert(rotordata_Cpmin18[pitchidx], 0, -9.0)
    Cpmin18_data_val = np.append(Cpmin18_data_val, Cpmin18_data_val[-1])

    TSR_data_val = np.insert(rotordata_TSR[pitchidx], 0, myTSRmin)
    TSR_data_val = np.append(TSR_data_val, myTSRmax)

    spline_Cp = sp.interpolate.CubicSpline(TSR_data_val, Cp_data_val, bc_type='natural')
    spline_Ct = sp.interpolate.CubicSpline(TSR_data_val, Ct_data_val, bc_type='natural')
    spline_Cpmin20 = sp.interpolate.CubicSpline(TSR_data_val, Cpmin20_data_val, bc_type='natural')
    spline_Cpmin19 = sp.interpolate.CubicSpline(TSR_data_val, Cpmin19_data_val, bc_type='natural')
    spline_Cpmin18 = sp.interpolate.CubicSpline(TSR_data_val, Cpmin18_data_val, bc_type='natural')

    add_boundary_knots(spline_Cp)
    add_boundary_knots(spline_Ct)
    add_boundary_knots(spline_Cpmin20)
    add_boundary_knots(spline_Cpmin19)
    add_boundary_knots(spline_Cpmin18)

    Cp_opt = np.max(rotordata_Cp)
    TSR_opt = rotordata_TSR[np.argmax(rotordata_Cp)]

    datFileList = glob.glob1(folderlocation, "*blade.dat")
    fullfile_withpath = folderlocation + datFileList[0]

    data = pd.read_table(fullfile_withpath, header=0, skiprows=[0, 1, 2, 3, 5], sep='\s+')

    spanRatio = [data['BlSpn'][19], data['BlSpn'][18], data['BlSpn'][17]] / data['BlSpn'][19]
    Cpmin_functions = [spline_Cpmin20, spline_Cpmin19, spline_Cpmin18]

    return spline_Cp, spline_Ct, Cpmin_functions, spanRatio, Cp_opt, TSR_opt

def estimateRotorMass(folderlocation):
    """
    Estimates the rotor mass based on blade geometry data from a given folder.
    
    Parameters:
    - folderlocation (str): Path to the folder containing blade geometry data files.
    
    Returns:
    - blade_Volume_base (float): Base volume of the blade.
    - blade_MassBase (float): Base mass of the blade.
    - blade_RadiusBase (float): Base radius of the blade.
    - coor_geom (np.array): Array of blade geometry coordinates.
    """

    datFileList = glob.glob1(folderlocation, "*blade.dat")
    fullfile_withpath = folderlocation + datFileList[0]
    data = pd.read_table(fullfile_withpath, header=0, skiprows=[0, 1, 2, 3, 5], sep='\s+')

    BladeSpan = data['BlSpn']
    BladeChord = data['BlChord']
    BladeTwist = data['BlTwist'] * np.pi / 180

    fileList = glob.glob(folderlocation + '//**/*CM.dat', recursive=True)
    fileList = natsorted(fileList, key=lambda y: y.lower())
    fileListLen = len(fileList)

    file = open(fileList[1], "r")
    content = file.readlines()
    myrows = int(content[8].split()[0])
    colnames = ['X', 'Y']
    coor_geom = np.zeros((len(BladeSpan) * (myrows - 1), 3))
    twist_store = np.zeros((len(BladeSpan) * (myrows - 1), 1))
    idxA = np.arange(len(BladeSpan)) * (myrows - 1)
    idxB = np.arange(len(BladeSpan)) * (myrows - 1) + (myrows - 1)

    for idx in np.arange(len(BladeSpan)):
        data = pd.read_table(fileList[idx], skiprows=15, nrows=myrows - 1, names=colnames, sep='\s+')
        coor_geom[idxA[idx]:idxB[idx], 0] = data['X'] * BladeChord[idx]
        coor_geom[idxA[idx]:idxB[idx], 1] = data['Y'] * BladeChord[idx]
        coor_geom[idxA[idx]:idxB[idx], 2] = BladeSpan[idx]
        twist_store[idxA[idx]:idxB[idx]] = BladeTwist[idx]

    for idx in np.arange(len(BladeSpan) * (myrows - 1)):
        rot = Rotation.from_euler('Z', twist_store[idx])
        coor_geom[idx, :] = np.matmul(rot.as_matrix(), coor_geom[idx, :])

    hull = ConvexHull(coor_geom)
    blade_Volume_base = hull.volume
    blade_MassBase = blade_Volume_base * ROTOR.density
    blade_RadiusBase = max(coor_geom[:, 2]) - min(coor_geom[:, 2])

    return blade_Volume_base, blade_MassBase, blade_RadiusBase, coor_geom

def calInertia(Radius, RadiusBase, MassBase, nargout):
    """
    Calculates rotor inertia and optionally scaled mass based on scaling from a base configuration.
    
    Parameters:
    - Radius (float): Target rotor radius.
    - RadiusBase (float): Reference radius for scaling.
    - MassBase (float): Reference mass for scaling.
    - nargout (int): Number of return values (1 for inertia only, 2 for inertia and mass).
    
    Returns:
    - Jr (float): Calculated rotor inertia.
    - Mass (float, optional): Scaled rotor mass, returned if nargout is 2.
    
    Raises:
    - ValueError: If 'nargout' is not 1 or 2.
    """
    # Scale factor and mass based on volume scaling assumption
    scaleK = Radius / RadiusBase
    Mass = MassBase * scaleK ** 3
    
    # Inertia calculation assuming cylindrical mass distribution
    Jr = Mass * Radius ** 2

    # Return based on requested output
    if nargout == 1:
        return Jr
    elif nargout == 2:
        return Jr, Mass
    else:
        raise ValueError("Invalid nargout!")



def add_boundary_knots(spline):
    """
    Modifies a spline by adding boundary knots to maintain natural behavior at its edges.
    
    Parameters:
    - spline (scipy.interpolate.CubicSpline): Spline to be modified.
    """

    # Process left boundary
    leftx = spline.x[0]  # First knot x-value
    lefty = spline(leftx)  # Spline value at first knot
    leftslope = spline(leftx, nu=1)  # Slope at first knot
    leftxnext = np.nextafter(leftx, leftx - 1)  # Small step left from first knot
    leftynext = lefty + leftslope * (leftxnext - leftx)  # Extrapolate y-value left
    leftcoeffs = np.array([0, 0, leftslope, leftynext])  # Coefficients for new left knot
    spline.extend(leftcoeffs[..., None], np.r_[leftxnext])  # Add new left knot

    # Process right boundary
    rightx = spline.x[-1]  # Last knot x-value
    righty = spline(rightx)  # Spline value at last knot
    rightslope = spline(rightx, nu=1)  # Slope at last knot
    rightxnext = np.nextafter(rightx, rightx + 1)  # Small step right from last knot
    rightynext = righty + rightslope * (rightxnext - rightx)  # Extrapolate y-value right
    rightcoeffs = np.array([0, 0, rightslope, rightynext])  # Coefficients for new right knot
    spline.extend(rightcoeffs[..., None], np.r_[rightxnext])  # Add new right knot
