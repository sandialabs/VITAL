# import unittest
# import sys
# import os
# import json
# import datetime
# import numpy as np
# from unittest.mock import patch, mock_open

# # Add the src directory to the Python path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# from module_tidal import TidalData

# class TestTidalData(unittest.TestCase):
#     def setUp(self):
#         self.station = "SEA0202"
#         self.startdate = 20200201
#         self.rangeHr = 2 * 7 * 24  # Two weeks
#         self.timestep = 5.0
#         self.city_data_file = "AlaskaCityLatLong.txt"
#         self.tidal_data = TidalData(self.station, self.startdate, self.rangeHr, self.timestep)

#     @patch('module_tidal.requests.get')
#     @patch('builtins.open', new_callable=mock_open, read_data="City,Lat,Lon\nCityA,58.3019,-134.4197\nCityB,61.2181,-149.9003")
#     def test_load_tidal_data(self, mock_open, mock_get):
#         # Mock the API responses
#         mock_get.side_effect = [
#             # Mock response for get_station_name
#             unittest.mock.Mock(status_code=200, content=json.dumps({
#                 "count": 1,
#                 "units": None,
#                 "stations": [
#                         {
#                         "count": 1,
#                         "units": None,
#                         "stations": [
#                             {
#                             "project": "Southeast Alaska 2002 Current Survey",
#                             "deployed": "2002-04-01 22:29:00",
#                             "retrieved": "2002-05-07 16:15:00",
#                             "timezone_offset": "-9",
#                             "observedst": True,
#                             "project_type": "Survey",
#                             "noaachart": None,
#                             "deployments": {
#                                 "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202/deployments.json"
#                             },
#                             "bins": {
#                                 "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202/bins.json"
#                             },
#                             "harmonicConstituents": {
#                                 "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202/harcon.json"
#                             },
#                             "height_from_bottom": 0.6,
#                             "center_bin_1_dist": 3.06,
#                             "id": "SEA0202",
#                             "name": "Sergius Narrows",
#                             "lat": 57.40702,
#                             "lng": -135.63115,
#                             "affiliations": "",
#                             "portscode": "",
#                             "products": {
#                                 "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202/products.json"
#                             },
#                             "disclaimers": None,
#                             "notices": None,
#                             "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202.json",
#                             "expand": "deployments,bins,harcon",
#                             "tideType": ""
#                             }
#                         ],
#                         "self": None
#                         }
#                 ],
#                 "self": None
#             }).encode('utf-8')),
#             # Mock response for get_station_info
#             unittest.mock.Mock(status_code=200, content=json.dumps({
#                 "count": 1,
#                 "units": None,
#                 "stations": [
#                     {
#                     "count": 1,
#                     "units": None,
#                     "stations": [
#                         {
#                         "project": "Southeast Alaska 2002 Current Survey",
#                         "deployed": "2002-04-01 22:29:00",
#                         "retrieved": "2002-05-07 16:15:00",
#                         "timezone_offset": "-9",
#                         "observedst": True,
#                         "project_type": "Survey",
#                         "noaachart": None,
#                         "deployments": {
#                             "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202/deployments.json"
#                         },
#                         "bins": {
#                             "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202/bins.json"
#                         },
#                         "harmonicConstituents": {
#                             "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202/harcon.json"
#                         },
#                         "height_from_bottom": 0.6,
#                         "center_bin_1_dist": 3.06,
#                         "id": "SEA0202",
#                         "name": "Sergius Narrows",
#                         "lat": 57.40702,
#                         "lng": -135.63115,
#                         "affiliations": "",
#                         "portscode": "",
#                         "products": {
#                             "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202/products.json"
#                         },
#                         "disclaimers": None,
#                         "notices": None,
#                         "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202.json",
#                         "expand": "deployments,bins,harcon",
#                         "tideType": ""
#                         }
#                     ],
#                     "self": None
#                     }
#                 ],
#                 "self": None
#             }).encode('utf-8')),
#             # Mock response for get_deployment_info
#             unittest.mock.Mock(status_code=200, content=json.dumps({
#                     "units": "meters",
#                     "flood_direction_degrees": 60.0,
#                     "orientation": "up",
#                     "sensor_depth": None,
#                     "depth": 16.5,
#                     "measured_depth": 25.18,
#                     "height_from_bottom": 0.6,
#                     "sample_interval": 360,
#                     "ping_int": None,
#                     "first_good_data": "2002-04-02 07:30:00",
#                     "last_good_data": "2002-05-07 16:12:00",
#                     "deployments": [
#                         {
#                         "id": "SEA0202",
#                         "deployed": "2002-04-01 22:29:00",
#                         "retrieved": "2002-05-07 16:15:00",
#                         "lat": 57.40702,
#                         "lng": -135.63115,
#                         "instrument_id": 16145,
#                         "instrument_desc": "Workhorse ADCP",
#                         "real_time_bin": None
#                         }
#                     ],
#                     "self": "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/SEA0202/deployments.json"
#                     }).encode('utf-8')),
#             # Mock response for get_tidal_data
#             unittest.mock.Mock(status_code=200, content=json.dumps({
#                 "current_predictions": {
#                     "units": "meters, cm/s",
#                     "cp": [
#                         {"Speed": "28.251", "Bin": "9", "Time": "2020-02-01 00:00", "Direction": 76, "Depth": "5.5"},
#                         {"Speed": "26.424", "Bin": "9", "Time": "2020-02-01 00:01", "Direction": 77, "Depth": "5.5"},
#                         {"Speed": "24.599", "Bin": "9", "Time": "2020-02-01 00:02", "Direction": 78, "Depth": "5.5"}
#                     ]
#                 }
#             }).encode('utf-8'))
#         ]

#         # Call the method to load tidal data
#         Uinf, t, dMoor, buoyLatitude, buoyLongitude, station_name, nearest_city, cable_length = self.tidal_data.load_tidal_data(self.city_data_file)

#         # Assert the results
#         self.assertEqual(station_name, "Sergius Narrows")
#         self.assertEqual(nearest_city, "CityA")
#         self.assertAlmostEqual(cable_length, 0.0, places=2)
#         # self.assertEqual(dMoor, 16.5)
#         self.assertAlmostEqual(buoyLatitude, np.radians(57.40702), places=5)
#         self.assertAlmostEqual(buoyLongitude, np.radians(-135.63115), places=5)
#         self.assertTrue(np.allclose(Uinf, [0.28251, 0.26424, 0.24599], atol=1e-4))
#         self.assertTrue(np.allclose(t, [0, 60, 120], atol=1e-4))

# if __name__ == '__main__':
#     unittest.main()


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

class TestTidalData(unittest.TestCase):

    def setUp(self):
        # Initialize TidalData with test parameters
        self.station = 'SEA0202'  
        self.startdate = '20200201'  
        self.range_hrs = 2 
        self.time_step_s = 5.0  
        self.tidal_data = TidalData(self.station, self.startdate, self.range_hrs, self.time_step_s)

    def test_get_station_name(self):
        station_name = self.tidal_data.get_station_name()
        self.assertIsNotNone(station_name)
        print(f"Station Name: {station_name}")

    def test_get_tidal_data(self):
        tidal_data = self.tidal_data.get_tidal_data()
        self.assertIn('current_predictions', tidal_data)
        print(f"Tidal Data: {tidal_data}")

    def test_load_tidal_data(self):
        city_data_file = "/Users/akeow/Desktop/VITAL/HDPS_TeamerClean/data/AlaskaCityLatLong.txt"
        flow_speeds, times, mooring_distance, buoy_latitude, buoy_longitude, station_name, nearest_city, cable_length = self.tidal_data.load_tidal_data(city_data_file)
        
        self.assertIsNotNone(flow_speeds)
        self.assertIsNotNone(times)
        self.assertIsNotNone(mooring_distance)
        self.assertIsNotNone(buoy_latitude)
        self.assertIsNotNone(buoy_longitude)
        self.assertIsNotNone(station_name)
        self.assertIsNotNone(nearest_city)
        self.assertIsNotNone(cable_length)

        # # Plotting the flow speeds
        # plt.figure(figsize=(10, 5))
        # plt.plot(times, flow_speeds, label='Flow Speeds (m/s)')
        # plt.title(f'Tidal Flow Speeds for Station {station_name}')
        # plt.xlabel('Time (s)')
        # plt.ylabel('Flow Speed (m/s)')
        # plt.legend()
        # plt.grid()
        # plt.show()

if __name__ == '__main__':
    unittest.main()
