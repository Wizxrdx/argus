from abc import ABC, abstractmethod

class Satellite(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_landsat_grid(self, longitude, latitude, cloud_threshold):
        """Display a 3x3 grid of Landsat pixels centered on the target location."""
        pass

    @abstractmethod
    def get_scene_extent(self):
        """Determine and display the Landsat scene extent based on the target pixel."""
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
