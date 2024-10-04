import io
import geopandas as gpd
from shapely.geometry import Point
import urllib.request
import zipfile

class WRS2:
    def __init__(self):
        url = "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/WRS2_descending_0.zip"
        r = urllib.request.urlopen(url)
        zip_file = zipfile.ZipFile(io.BytesIO(r.read()))
        zip_file.extractall("landsat-path-row")
        zip_file.close()

        shapefile = 'landsat-path-row/WRS2_descending.shp'
        self._gdf = gpd.read_file(shapefile)

    def get_path_row(self, longitude, latitude):
        point = Point(longitude, latitude)

        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs(epsg=4326)

        result = gdf[gdf.contains(point)]

        if not result.empty:
            return result['PATH'].values[0], result['ROW'].values[0]
        else:
            return None, None
