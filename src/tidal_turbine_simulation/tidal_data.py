import os
import json
import requests
import math
import datetime
import calendar
import numpy as np
from scipy.interpolate import PchipInterpolator
import pandas as pd

from constGlobal import ConstantsGlobal
from constUnitConvert import ConstantsUnitConversion

GLOBAL = ConstantsGlobal()
CONVERT = ConstantsUnitConversion()

class TidalData:
    def __init__(self, station, startdate, rangeHR, timestep):
        self.station = station
        self.startdate = startdate
        self.rangeHR = rangeHR
        self.timestep = timestep
        self.flow_speeds = None
        self.times = None
        self.dmoor_m = None
        self.lat_rad = None
        self.lon_rad = None
        self.station_name = None
        self.nearest_city = None
        self.cable_length = None

    def get_station_name(self):
        url = f'https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{self.station}.json'
        req_data = requests.get(url, verify=False)  # Note: verify=False may pose a security risk in a production environment
        input_data = json.loads(req_data.content)
        print(url)
        return input_data['stations'][0]['name']

    def get_station_info(self):
        url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{self.station}.json"
        req_data = requests.get(url, verify=False)  # Note: verify=False may pose a security risk in a production environment
        input_data = json.loads(req_data.content)
        print(url)
        return input_data

    def get_deployment_info(self):
        url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{self.station}/deployments.json"
        req_data = requests.get(url, verify=False)  # Note: verify=False may pose a security risk in a production environment
        input_data = json.loads(req_data.content)
        print(url)
        return input_data

    def get_tidal_data(self):
        rangeHR_extended = self.rangeHR + 2  # make sure we are not extrapolating later
        base = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?'
        url = (base + f'station={self.station}&begin_date={self.startdate}&range={rangeHR_extended}&product=currents_predictions'
               f'&units=metric&time_zone=gmt&interval=1&vel_type=speed_dir&format=json')
        req_data = requests.get(url, verify=False)  # Note: verify=False may pose a security risk in a production environment
        input_data = json.loads(req_data.content)
        print(url)
        return input_data

    def extract_tidal_speed(self, input_data):
        if self.station.lower().startswith('pct'):
            return [x['Velocity_Major'] for x in input_data['current_predictions']['cp']]
        else:
            return [x['Speed'] for x in input_data['current_predictions']['cp']]

    def extract_tidal_time(self, input_data):
        tidal_time_string = [x['Time'] for x in input_data['current_predictions']['cp']]
        date_obj = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M') for x in tidal_time_string]
        return [calendar.timegm(x.timetuple()) for x in date_obj]

    def distance(self, lat1, lat2, lon1, lon2):
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

    def calCableLen(self, buoylat, buoylon, citytextfile):
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
            d_cable_len[ind] = self.distance(buoylat, city_lat, buoylon, city_lon)

        # Find the closest city
        closestCity = datafile[datafile.columns[0]][np.argmin(d_cable_len)]
        cableLen_m = round(d_cable_len[np.argmin(d_cable_len)], 2)
        return cableLen_m, closestCity

    def flowAtDepth(self, FlowSpeed, Radius, dHub, dMoor):
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

    def load_tidal_data(self, city_data_file):
        self.station_name = self.get_station_name()

        if self.station.lower().startswith('pct'):
            input_data = self.get_station_info()
            self.lat_rad = math.radians(input_data['stations'][0]['lat'])
            self.lon_rad = math.radians(input_data['stations'][0]['lng'])
            self.dmoor_m = 50.0  # PCT stations do not provide depth estimates. We assume 50 meters
        else:
            input_data = self.get_deployment_info()
            self.dmoor_m = float(input_data['depth'])
            if input_data['units'] == 'feet':
                self.dmoor_m *= CONVERT.ft2m
            self.lat_rad = math.radians(float(input_data['deployments'][0]['lat']))
            self.lon_rad = math.radians(float(input_data['deployments'][0]['lng']))

        tidal_data = self.get_tidal_data()
        tidal_speed_cms = self.extract_tidal_speed(tidal_data)
        tidal_time_s = np.array(self.extract_tidal_time(tidal_data))
        tidal_speed_ms = np.array([float(x) for x in tidal_speed_cms]) * CONVERT.cms2ms

        # Create the PchipInterpolator
        tidal_CubicSpline = PchipInterpolator(tidal_time_s - tidal_time_s[0], tidal_speed_ms)
        end_time = self.rangeHR * 3600.0  # Convert hours to seconds
        self.times = np.arange(0, end_time, self.timestep)
        self.flow_speeds = tidal_CubicSpline(self.times)
        self.flow_speeds = np.abs(self.flow_speeds)
        # Ensure the minimum value of flow_speeds is at least 1e-4; avoid divide by zero
        self.flow_speeds = np.maximum(self.flow_speeds, 1e-4)

        # Find the nearest city and calculate the cable length
        self.cable_length, self.nearest_city = self.calCableLen(self.lat_rad, self.lon_rad, city_data_file)

        return self.flow_speeds, self.times, self.dmoor_m, self.lat_rad, self.lon_rad, self.station_name, self.nearest_city, self.cable_length
