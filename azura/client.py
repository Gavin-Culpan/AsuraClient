import requests
from config import API_KEY, BASE_URL


class AzuraClient:
    def __init__(self):
        self.headers = {
            "X-API-Key": API_KEY
        }

    def get_station(self, station_id):
        response = requests.get(
            f"{BASE_URL}/station/{station_id}",
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()
    
    def get_media(self, station_id):
        response = requests.get(
            f"{BASE_URL}/station/{station_id}/files",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_playlists(self, station_id):
        response = requests.get(
            f"{BASE_URL}/station/{station_id}/playlists",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()