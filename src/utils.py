import io
import geopandas as gpd
from shapely.geometry import Point
import urllib.request
import zipfile
import requests
import time
import os
from datetime import datetime, timedelta
import json

class WRS2:
    _instance = None
    _gdf = None

    def __init__(self):
        shapefile = 'assets/landsat-path-row/WRS2_descending.shp'
        if self._is_data_old(): self._fetch_data()
        self._gdf = gpd.read_file(shapefile)

    def _fetch_data(self):
        url = "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/WRS2_descending_0.zip"
        print("Downloading Landsat Path files...")
        r = urllib.request.urlopen(url)
        print("Extracting Landsat Path files...")
        zip_file = zipfile.ZipFile(io.BytesIO(r.read()))
        zip_file.extractall("assets/landsat-path-row")
        zip_file.close()
        print("Acquiring Landsat Path files done.")

    def _is_data_old(self):
        shp_file_path = os.path.join('assets', 'landsat-path-row', 'WRS2_descending.shp')
        
        # Check if the file exists
        if not os.path.exists(shp_file_path):
            return True  # If the file doesn't exist, treat data as old
        
        # Get the last modified time of the file
        last_modified_time = os.path.getmtime(shp_file_path)
        last_modified_date = datetime.fromtimestamp(last_modified_time)

        print('Last downloaded Landsat Path:', last_modified_date)

        # Define the threshold for "old" data (e.g., 1 day)
        threshold = datetime.now() - timedelta(days=30)

        return last_modified_date < threshold

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)

        return cls._instance

    def get_path_row(self, longitude, latitude):
        point = Point(longitude, latitude)

        if self._gdf.crs != 'EPSG:4326':
            self._gdf = self._gdf.to_crs(epsg=4326)

        result = self._gdf[self._gdf.contains(point)]

        if not result.empty:
            return result['PATH'].values[0], result['ROW'].values[0]
        else:
            return None, None


class LandsatAcquisition:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
            cls._instance._landsat_cycles = {}
            cls._instance._time_last_acq_date_request = 0
            if cls._instance._is_data_old():
                cls._instance._fetch_url()
            else:
                cls._instance._fetch_file()
        return cls._instance

    def _is_data_old(self):
        json_file_path = os.path.join('assets', 'cycles_full.json')
        
        # Check if the file exists
        if not os.path.exists(json_file_path):
            return True  # If the file doesn't exist, treat data as old
        
        # Get the last modified time of the file
        last_modified_time = os.path.getmtime(json_file_path)
        last_modified_date = datetime.fromtimestamp(last_modified_time)

        print('Last downloaded Landsat Cycles:', last_modified_date)

        # Define the threshold for "old" data (e.g., 1 day)
        threshold = datetime.now() - timedelta(days=1)

        return last_modified_date < threshold

    def _fetch_file(self):
        json_file_path = os.path.join('assets', 'cycles_full.json')

        with open(json_file_path, 'r') as json_file:
            json_data = json.load(json_file)
        
        self._landsat_cycles = json_data

    def _fetch_url(self):
        url = "https://landsat.usgs.gov/sites/default/files/landsat_acq/assets/json/cycles_full.json"
        print("Requesting Landsat cycles...")
        response = requests.get(url)
        print("Landsat cycles request done.")
        self._landsat_cycles = response.json()
        
        # Save to json file
        json_file_path = os.path.join('assets', 'cycles_full.json')
        json_data = self._landsat_cycles

        # Save the JSON data to the specified file
        with open(json_file_path, 'w') as json_file:
            json.dump(json_data, json_file)
        print("Saved Landsat cycles.")

    def request_landsat_cycle(self, satellite):
        return self._landsat_cycles[satellite]

    def get_next_acquisition_dates(self, satellite, path):
        landsat_data = self.request_landsat_cycle(satellite)
        current_date = datetime.now()
        results = []

        for date_str, details in landsat_data.items():
            date = datetime.strptime(date_str, "%m/%d/%Y")

            # Check if the path matches and if the date is today or in the future
            if str(path) in details['path'] and date >= current_date:
                results.append(date_str)

        return results