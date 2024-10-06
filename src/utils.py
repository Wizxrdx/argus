import io
import geopandas as gpd
from shapely.geometry import Point
import urllib.request
import zipfile

class WRS2:
    _instance = None
    _gdf = None

    def __init__(self):
        url = "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/WRS2_descending_0.zip"
        r = urllib.request.urlopen(url)
        zip_file = zipfile.ZipFile(io.BytesIO(r.read()))
        zip_file.extractall("landsat-path-row")
        zip_file.close()

        shapefile = 'landsat-path-row/WRS2_descending.shp'
        self._gdf = gpd.read_file(shapefile)

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
