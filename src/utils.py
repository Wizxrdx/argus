import io
from osgeo import ogr
import shapely.wkt
import shapely.geometry
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
        wrs = ogr.Open(shapefile)
        self._layer = wrs.GetLayer(0)

    def get_path_row(self, longitude, latitude):
        point = shapely.geometry.Point(longitude, latitude)
        mode = 'D'

        i = 0
        while not self._checkpoint(self._layer.GetFeature(i), point, mode):
            i += 1
            feature = layer.GetFeature(i)
            path = feature['PATH']
            row = feature['ROW']
        return path, row

    def _checkpoint(self, feature, point, mode):
        geom = feature.GetGeometryRef() #Get geometry from feature
        shape = shapely.wkt.loads(geom.ExportToWkt()) #Import geometry into shapely to easily work with our point
        if point.within(shape) and feature['MODE']==mode:
            return True
