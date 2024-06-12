import os
import json
import requests
import math
import datetime
import calendar
import numpy as np
import scipy.interpolate as sp_interpolate
import pandas as pd

import constGlobal
import constUnitConvert

# Initialize constants from modules
GLOBAL = constGlobal.ConstantsGlobal()
CONVERT = constUnitConvert.ConstantsUnitConversion()

def loadTidal(station, startdate, rangeHR, timestep):
    """
    Loads tidal data from NOAA for a given station and time range, and interpolates it to a specified timestep.
    
    Parameters:
    - station: NOAA station ID.
    - startdate: Start date for data retrieval.
    - rangeHR: Range in hours for data retrieval.
    - timestep: Timestep in seconds for data interpolation.
    
    Returns:
    - FlowSpeed_data: Interpolated flow speed data in m/s.
    - t_data: Time data corresponding to the flow speed data.
    - dmoor_m: Depth of the mooring in meters.
    - lat_rad: Latitude of the station in radians.
    - lon_rad: Longitude of the station in radians.
    """
    # Construct URL and fetch deployment data
    url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station}/deployments.json"
    req_data = requests.get(url, verify=False)  # Note: verify=False may pose a security risk in a production environment
    input_data = json.loads(req_data.content)

    # Convert depth to meters if necessary
    dmoor_m = float(input_data['depth'])
    if input_data['units'] == 'feet':
        dmoor_m *= CONVERT.ft2m

    # Convert latitude and longitude to radians
    lat_rad = math.radians(float(input_data['deployments'][0]['lat']))
    lon_rad = math.radians(float(input_data['deployments'][0]['lng']))

    # Construct URL for tidal data
    base = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?'
    url = (base + f'station={station}&begin_date={startdate}&range={rangeHR}&product=currents_predictions'
           f'&units=metric&time_zone=gmt&interval=1&vel_type=speed_dir&format=json')

    # Fetch tidal data
    req_data = requests.get(url, verify=False)  # Note: verify=False may pose a security risk in a production environment
    input_data = json.loads(req_data.content)

    # Extract and convert tidal speed and time data
    tidal_speed_cms = [x['Speed'] for x in input_data['current_predictions']['cp']]
    tidal_time_string = [x['Time'] for x in input_data['current_predictions']['cp']]
    date_obj = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M') for x in tidal_time_string]
    date_obj = [calendar.timegm(x.timetuple()) for x in date_obj]

    # Interpolate tidal data to specified timestep
    date_obj = np.array(date_obj)
    tidal_speed_cms = np.array([float(x) for x in tidal_speed_cms])
    tidal_speed_ms = tidal_speed_cms * CONVERT.cms2ms
    tidal_time_s = date_obj - date_obj[0]
    t_data = np.arange(tidal_time_s[0], tidal_time_s[-1], timestep)
    tidal_CubicSpline = sp_interpolate.CubicSpline(tidal_time_s, tidal_speed_ms)
    FlowSpeed_data = np.abs(tidal_CubicSpline(t_data))

    return FlowSpeed_data, t_data, dmoor_m, lat_rad, lon_rad

def distance(lat1, lat2, lon1, lon2):
    """
    Calculates the great-circle distance between two points on the Earth.
    
    Parameters:
    - lat1, lat2: Latitudes of the two points in radians.
    - lon1, lon2: Longitudes of the two points in radians.
    
    Returns:
    - Distance between the two points in meters.
    """
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000  # Radius of Earth in meters
    return c * r

def calCableLen(buoylat, buoylon, citytextfile):
    """
    Calculates the cable length from a buoy to the closest city listed in a text file.
    
    Parameters:
    - buoylat, buoylon: Latitude and longitude of the buoy in radians.
    - citytextfile: Path to a text file containing city data.
    
    Returns:
    - cableLen_m: Length of the cable to the closest city in meters.
    - closestCity: Name of the closest city.
    """
    # Load city data
    datafile = pd.read_table(citytextfile, delimiter=",", comment='#')
    d_cable_len = np.zeros(len(datafile))
    
    # Calculate distance to each city
    for ind in datafile.index:
        city_lat = math.radians(datafile[datafile.columns[1]][ind])
        city_lon = math.radians(datafile[datafile.columns[2]][ind])
        d_cable_len[ind] = distance(buoylat, city_lat, buoylon, city_lon)

    # Find the closest city
    closestCity = datafile[datafile.columns[0]][np.argmin(d_cable_len)]
    cableLen_m = round(d_cable_len[np.argmin(d_cable_len)], 2)
    return cableLen_m, closestCity

def flowAtDepth(FlowSpeed, Radius, dHub, dMoor):
    """
    Adjusts flow speed at a turbine's hub depth based on the mooring depth and the flow speed at the surface.
    
    Parameters:
    - FlowSpeed: Flow speed at the surface in m/s.
    - Radius: Radius of the turbine in meters.
    - dHub: Depth of the turbine hub in meters.
    - dMoor: Depth of the mooring in meters.
    
    Returns:
    - Uout: Adjusted flow speed at the hub depth in m/s.
    """
    # Calculate average flow speed based on depth
    Area = np.pi * Radius ** 2.0
    Uavg = FlowSpeed / 1.07
    dz = dMoor - dHub
    if (dz - Radius) < 0.5 * dMoor and (dz + Radius) <= 0.5 * dMoor:
        Za = dz - Radius
        Zb = dz + Radius
        Zc = Zd = 0.0
    elif (dz - Radius) >= 0.5 * dMoor and (dz + Radius) > 0.5 * dMoor:
        Za = Zb = 0.0
        Zc = dz - Radius
        Zd = dz + Radius
    else:
        Za = dz - Radius
        Zb = Zc = 0.5 * dMoor
        Zd = dz + Radius

    # Calculate average power and adjust flow speed
    tempvalA = (1.1407 * (1 / dMoor) ** (3 / 7) * Uavg ** 3.0 * (Zb ** (10 / 7) - Za ** (10 / 7)))
    tempvalB = (1.07 * Uavg) ** 3.0 * (Zd - Zc)
    PfluidAvg = 1 / (4.0 * Radius) * GLOBAL.rho * Area * (tempvalA + tempvalB)
    Uout = ((2.0 * PfluidAvg) / (GLOBAL.rho * Area)) ** (1 / 3.0)

    return Uout
