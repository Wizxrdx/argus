import datetime
import numpy as np
import matplotlib.pyplot as plt
from dateutil import parser
from dateutil.relativedelta import relativedelta
from shapely.geometry import Polygon
from sentinelhub import (
    SHConfig, CRS, BBox, DataCollection,
    SentinelHubRequest, MimeType, MosaickingOrder, SentinelHubCatalog, bbox_to_dimensions
)

class SentinelDataRetriever:
    def __init__(self, client_id, client_secret, token_url, base_url):
        """
        Initialize the SentinelDataRetriever with the necessary configuration.

        Parameters:
        client_id (str): Your Sentinel Hub client ID.
        client_secret (str): Your Sentinel Hub client secret.
        token_url (str): URL for token authentication.
        base_url (str): Base URL for the Sentinel Hub API.
        """
        self.config = self.initialize_sentinelhub_config(client_id, client_secret, token_url, base_url)
        self.catalog = SentinelHubCatalog(config=self.config)

    def initialize_sentinelhub_config(self, client_id, client_secret, token_url, base_url):
        """Initialize and configure the SentinelHub API."""
        config = SHConfig()
        config.sh_client_id = client_id
        config.sh_client_secret = client_secret
        config.sh_token_url = token_url
        config.sh_base_url = base_url
        config.save("cdse")
        return config

    def create_polygon(self, min_lon, max_lon, min_lat, max_lat):
        """Create a GeoJSON-style polygon."""
        return [
            [min_lon, min_lat],
            [min_lon, max_lat],
            [max_lon, max_lat],
            [max_lon, min_lat],
            [min_lon, min_lat]
        ]

    def get_bounding_box(self, lon, lat, delta=0.00015):
        """Create a bounding box around a location (lon, lat)."""
        min_lon = lon - delta
        max_lon = lon + delta
        min_lat = lat - delta
        max_lat = lat + delta

        coordinates = self.create_polygon(min_lon, max_lon, min_lat, max_lat)
        polygon = Polygon(coordinates)
        bounds = polygon.bounds  # (minx, miny, maxx, maxy)
        return BBox(bbox=bounds, crs=CRS.WGS84), bounds

    def search_catalog(self, aoi_bbox, time_interval):
        """Search SentinelHub catalog for available data."""
        search_iterator = self.catalog.search(
            DataCollection.SENTINEL2_L2A,
            bbox=aoi_bbox,
            time=time_interval,
            fields={"include": ["id", "properties.datetime"], "exclude": []}
        )
        results = list(search_iterator)
        print(f"Total number of results: {len(results)}")
        return results

    def create_sentinelhub_request(self, bbox, size, time_interval, evalscript):
        """Create a SentinelHub request for satellite data."""
        request = SentinelHubRequest(
            evalscript=evalscript,
            input_data=[SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                mosaicking_order=MosaickingOrder.LEAST_CC
            )],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=self.config,
        )
        return request

    def retrieve_band_data(self, lon, lat, resolution=10, time_interval=("2022-07-01", "2022-08-01")):
        """Retrieve Sentinel-2 band data for the specified longitude and latitude."""
        bbox, _ = self.get_bounding_box(lon, lat)
        size = bbox_to_dimensions(bbox, resolution=resolution)

        evalscript_all_bands = """
            //VERSION=3
            function setup() {
                return {
                    input: [{
                        bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"],
                        units: "DN"
                    }],
                    output: {
                        bands: 13,
                        sampleType: "INT16"
                    }
                };
            }

            function evaluatePixel(sample) {
                return [sample.B01, sample.B02, sample.B03, sample.B04, sample.B05, sample.B06, sample.B07,
                        sample.B08, sample.B8A, sample.B09, sample.B11, sample.B12];
            }
        """

        request = self.create_sentinelhub_request(bbox, size, time_interval, evalscript_all_bands)
        all_bands_response = request.get_data()

        image = np.array(all_bands_response)
        band_labels = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"]
        
        band_data = []
        for i, label in enumerate(band_labels):
            band_values = image[0, :, :, i]  # Get the corresponding band data
            band_data.append({"band": label, "values": band_values.tolist()})  # Store as dictionary

        return band_data

    def get_past_dates(self, orig_lon, orig_lat, num_months: int) -> list:
        """Get a list of past dates at 5-day intervals based on search results from the specified number of months back."""
        bbox, _ = self.get_bounding_box(orig_lon, orig_lat)
        today = datetime.datetime.now()
        start_date = today - relativedelta(months=num_months)
        time_interval = (start_date, today)

        search_results = self.search_catalog(bbox, time_interval)
        dates = [result['properties']['datetime'] for result in search_results]

        date_objects = [parser.isoparse(date) for date in dates]
        sorted_dates = sorted(date_objects)

        formatted_dates = [date.strftime('%Y-%m-%d %H:%M:%S') for date in sorted_dates]
        return formatted_dates

    def get_future_dates(self, orig_lon, orig_lat, num_months: int) -> list:
        """Get a list of future dates at 5-day intervals based on search results from the specified number of months ahead."""
        bbox, _ = self.get_bounding_box(orig_lon, orig_lat)
        today = datetime.datetime.now()
        one_month_ago = today - relativedelta(months=1)
        time_interval = (one_month_ago, today)

        search_results = self.search_catalog(bbox, time_interval)
        dates = [result['properties']['datetime'] for result in search_results]

        date_objects = [parser.isoparse(date) for date in dates]
        sorted_dates = sorted(date_objects)

        latest_date = sorted_dates[-1] if sorted_dates else None

        if latest_date:
            next_dates = [latest_date + datetime.timedelta(days=i * 5) for i in range(1, 6)]
            formatted_next_dates = [date.strftime('%Y-%m-%d %H:%M:%S') for date in next_dates]
            return formatted_next_dates
        else:
            return []

    @staticmethod
    def display_image_from_list(data_list, brightness_factor=3.5/255):
        """Convert a list to an image and display it."""
        image = np.array(data_list)
        scaled_image = image * brightness_factor
        clipped_image = np.clip(scaled_image, 0, 1)
        plt.imshow(clipped_image)
        plt.axis('off')
        plt.show()