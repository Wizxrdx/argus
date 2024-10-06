from abc import ABC, abstractmethod

class Satellite(ABC):
    def __init__(self, location, notification_lead_time, cloud_threshold):
        """
        Abstract Satellite class constructor.
        
        :param location: The target location (latitude, longitude, or place name).
        :param notification_lead_time: The lead time for notification before a satellite passes over the target location.
        :param cloud_threshold: The maximum acceptable cloud coverage percentage for data retrieval.
        """
        self.location = location
        self.notification_lead_time = notification_lead_time
        self.cloud_threshold = cloud_threshold
    
    @abstractmethod
    def set_target_location(self):
        """Allow the user to define the target location."""
        pass

    @abstractmethod
    def determine_overpass_time(self):
        """Determine when the satellite will pass over the target location."""
        pass

    @abstractmethod
    def set_notification_preferences(self, method):
        """Allow users to select the notification method and time lead."""
        pass

    @abstractmethod
    def get_landsat_grid(self):
        """Display a 3x3 grid of Landsat pixels centered on the target location."""
        pass

    @abstractmethod
    def get_scene_extent(self):
        """Determine and display the Landsat scene extent based on the target pixel."""
        pass

    @abstractmethod
    def set_cloud_threshold(self, threshold):
        """Allow users to set a threshold for cloud coverage."""
        pass

    @abstractmethod
    def filter_acquisitions(self, time_span=None):
        """Filter data to only show the most recent or a specific time span of acquisitions."""
        pass

    @abstractmethod
    def acquire_scene_metadata(self):
        """Acquire scene metadata such as satellite, date, time, cloud cover, etc."""
        pass

    @abstractmethod
    def get_surface_reflectance_data(self):
        """Access and display Landsat Surface Reflectance (SR) data for the target pixel."""
        pass

    @abstractmethod
    def display_spectral_signature(self):
        """Display a graph of the spectral signature for the target pixel."""
        pass

    @abstractmethod
    def download_data(self, format="csv"):
        """Allow users to download or share data in a useful format."""
        pass
