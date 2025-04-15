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

# Constants
NOAA_API_BASE_URL = 'https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations'
NOAA_TIDAL_DATA_URL = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'
EARTH_RADIUS_M = 6378137.0
MIN_FLOW_SPEED = 1e-4
DEFAULT_MOORING_DISTANCE_M = 50.0

class TidalData:
    """
    A class to represent tidal data.
    ...
    """

    def __init__(self, station: str, startdate: str, range_hrs: int, time_step_s: float):
        """
        Constructs all the necessary attributes for the TidalData object.
        ...
        """
        self.station: str = station
        self.startdate: str = startdate
        self.range_hrs: int = range_hrs
        self.time_step_s: float = time_step_s
        self.flow_speeds_m_s: np.ndarray = None
        self.time_s: np.ndarray = None
        self.mooring_distance_m: float = None
        self.buoy_latitude_rad: float = None
        self.buoy_longitude_rad: float = None
        self.station_name: str = None
        self.nearest_city: str = None
        self.electrical_cable_length_m: float = None
        self.session = requests.Session()  # Use a session for requests

    def __del__(self):
        """Ensure the session is closed when the object is deleted."""
        self.session.close()

    def get_station_name(self) -> str:
        """
        Retrieves the name of the station.
        ...
        """
        url = f'{NOAA_API_BASE_URL}/{self.station}.json'
        try:
            req_data = self.session.get(url, verify=False)
            req_data.raise_for_status()  # Raise an error for bad responses
            input_data = req_data.json()
            return input_data['stations'][0]['name']
        except (requests.RequestException, KeyError) as e:
            print(f"Error retrieving station name: {e}")
            return None

    def get_station_info(self) -> dict:
        """
        Retrieves information about the station.
        ...
        """
        url = f"{NOAA_API_BASE_URL}/{self.station}.json"
        try:
            req_data = self.session.get(url, verify=False)
            req_data.raise_for_status()
            return req_data.json()
        except (requests.RequestException, KeyError) as e:
            print(f"Error retrieving station info: {e}")
            return {}

    def get_deployment_info(self) -> dict:
        """
        Retrieves deployment information for the station.
        ...
        """
        url = f"{NOAA_API_BASE_URL}/{self.station}/deployments.json"
        try:
            req_data = self.session.get(url, verify=False)
            req_data.raise_for_status()
            return req_data.json()
        except (requests.RequestException, KeyError) as e:
            print(f"Error retrieving deployment info: {e}")
            return {}

    def get_tidal_data(self) -> dict:
        """
        Retrieves tidal data for the station.
        ...
        """
        range_hrs_extended = self.range_hrs + 2
        url = (f'{NOAA_TIDAL_DATA_URL}?station={self.station}&begin_date={self.startdate}&range={range_hrs_extended}'
               f'&product=currents_predictions&units=metric&time_zone=gmt&interval=1&vel_type=speed_dir&format=json')
        try:
            req_data = self.session.get(url, verify=False)
            req_data.raise_for_status()
            return req_data.json()
        except (requests.RequestException, KeyError) as e:
            print(f"Error retrieving tidal data: {e}")
            return {}

    def extract_tidal_speed(self, input_data: dict) -> list:
        """
        Extracts tidal speed data from the input data.
        ...
        """
        if self.station.lower().startswith('pct'):
            return [x['Velocity_Major'] for x in input_data['current_predictions']['cp']]
        else:
            return [x['Speed'] for x in input_data['current_predictions']['cp']]

    def extract_tidal_time(self, input_data: dict) -> list:
        """
        Extracts tidal time data from the input data.
        ...
        """
        tidal_time_string = [x['Time'] for x in input_data['current_predictions']['cp']]
        date_obj = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M') for x in tidal_time_string]
        return [calendar.timegm(x.timetuple()) for x in date_obj]

    def distance(self, lat1: float, lat2: float, lon1: float, lon2: float) -> float:
        """
        Calculates the great-circle distance between two points on the Earth.
        ...
        """
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        return c * EARTH_RADIUS_M

    def calCableLen(self, buoylat: float, buoylon: float, citytextfile: str) -> tuple:
        """
        Calculates the cable length from a buoy to the closest city listed in a text file.
        ...
        """
        datafile = pd.read_table(citytextfile, delimiter=",", comment='#')
        d_cable_len = np.zeros(len(datafile))
        
        for ind in datafile.index:
            city_lat = math.radians(datafile[datafile.columns[1]][ind])
            city_lon = math.radians(datafile[datafile.columns[2]][ind])

            d_cable_len[ind] = self.distance(buoylat, city_lat, buoylon, city_lon)

        closestCity = datafile[datafile.columns[0]][np.argmin(d_cable_len)]
        cableLen_m = round(d_cable_len[np.argmin(d_cable_len)], 2)
        # print(f'City lat:{datafile[datafile.columns[1]][np.argmin(d_cable_len)]} degree')
        # print(f'City lon:{datafile[datafile.columns[2]][np.argmin(d_cable_len)]} degree')
        # print(f'City lat:{math.radians(datafile[datafile.columns[1]][np.argmin(d_cable_len)])} radian')
        # print(f'City lon:{math.radians(datafile[datafile.columns[2]][np.argmin(d_cable_len)])} radian')
        # print(f'Buoy lat:{buoylat} radian')
        # print(f'Buoy lon:{buoylon} radian')
        return cableLen_m, closestCity

    def load_tidal_data(self, city_data_file: str) -> tuple:
        """
        Loads tidal data and calculates the necessary attributes.
        ...
        """
        self.station_name = self.get_station_name()

        if self.station.lower().startswith('pct'):
            input_data = self.get_station_info()
            self.buoy_latitude_rad = math.radians(input_data['stations'][0]['lat'])
            self.buoy_longitude_rad = math.radians(input_data['stations'][0]['lng'])
            # print(f'Buoy lat:{float(input_data['stations'][0]['lat'])} degree')
            # print(f'Buoy lon:{float(input_data['stations'][0]['lng'])} degree')
            self.mooring_distance_m = DEFAULT_MOORING_DISTANCE_M
        else:
            input_data = self.get_deployment_info()
            self.mooring_distance_m = float(input_data['depth'])
            if input_data['units'] == 'feet':
                self.mooring_distance_m *= CONVERT.ft2m
            self.buoy_latitude_rad = math.radians(float(input_data['deployments'][0]['lat']))
            self.buoy_longitude_rad = math.radians(float(input_data['deployments'][0]['lng']))
            # print(f'Buoy lat:{float(input_data['deployments'][0]['lat'])} degree')
            # print(f'Buoy lon:{float(input_data['deployments'][0]['lng'])} degree')


        tidal_data = self.get_tidal_data()
        tidal_speed_cms = self.extract_tidal_speed(tidal_data)
        tidal_time_s = np.array(self.extract_tidal_time(tidal_data))
        tidal_speed_ms = np.array([float(x) for x in tidal_speed_cms]) * CONVERT.cms2ms

        tidal_CubicSpline = PchipInterpolator(tidal_time_s - tidal_time_s[0], tidal_speed_ms)
        end_time = self.range_hrs * 3600.0
        self.time_s = np.arange(0, end_time, self.time_step_s)
        self.flow_speeds_m_s = tidal_CubicSpline(self.time_s)
        self.flow_speeds_m_s = np.abs(self.flow_speeds_m_s)
        self.flow_speeds_m_s = np.maximum(self.flow_speeds_m_s, MIN_FLOW_SPEED)

        self.electrical_cable_length_m, self.nearest_city = self.calCableLen(self.buoy_latitude_rad, self.buoy_longitude_rad, city_data_file)

        return self.flow_speeds_m_s, self.time_s, self.mooring_distance_m, self.buoy_latitude_rad, self.buoy_longitude_rad, self.station_name, self.nearest_city, self.electrical_cable_length_m
