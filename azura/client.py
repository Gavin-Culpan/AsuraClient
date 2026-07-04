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

    def get_playlist(self, station_id, playlist_id):
        response = requests.get(
            f"{BASE_URL}/station/{station_id}/playlist/{playlist_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_playlist(self, station_id, name, weekday_number, weight=3):
        """
        Create a new day-scheduled playlist that plays all day on the given weekday.
        weekday_number: ISO weekday, 1=Monday ... 7=Sunday
        """
        payload = {
            "name": name,
            "type": "default",
            "source": "songs",
            "order": "sequential",
            "is_enabled": True,
            "weight": weight,
            "schedule_items": [
                {
                    "start_time": 0,
                    "end_time": 2359,
                    "days": [weekday_number]
                }
            ]
        }
        response = requests.post(
            f"{BASE_URL}/station/{station_id}/playlists",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def empty_playlist(self, station_id, playlist_id):
        """Remove all current contents from a playlist."""
        response = requests.delete(
            f"{BASE_URL}/station/{station_id}/playlist/{playlist_id}/empty",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_file(self, station_id, media_id):
        response = requests.get(
            f"{BASE_URL}/station/{station_id}/file/{media_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def assign_file_to_playlist(self, station_id, media_id, playlist_id):
        """
        Add a media file to a playlist WITHOUT removing its existing playlist
        memberships. Necessary because the same file (e.g. an ad) can belong
        to multiple day-playlists at once.
        """
        current = self.get_file(station_id, media_id)
        existing_playlist_ids = [p["id"] for p in current.get("playlists", [])]

        if playlist_id not in existing_playlist_ids:
            existing_playlist_ids.append(playlist_id)

        payload = {"playlists": existing_playlist_ids}
        response = requests.put(
            f"{BASE_URL}/station/{station_id}/file/{media_id}",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def remove_file_from_playlist(self, station_id, media_id, playlist_id):
        """Remove a file from one playlist without affecting its other memberships."""
        current = self.get_file(station_id, media_id)
        existing_playlist_ids = [p["id"] for p in current.get("playlists", []) if p["id"] != playlist_id]

        payload = {"playlists": existing_playlist_ids}
        response = requests.put(
            f"{BASE_URL}/station/{station_id}/file/{media_id}",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def delete_playlist(self, station_id, playlist_id):
        response = requests.delete(
            f"{BASE_URL}/station/{station_id}/playlist/{playlist_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_timeslot_playlist(self, station_id, name, weekday_number, start_hhmm, end_hhmm, file_ids):
        """
        Create a narrow-window playlist that interrupts to play specific files
        at an exact time. start_hhmm/end_hhmm are ints like 900 for 9:00, 2359 for 23:59.
        """
        payload = {
            "name": name,
            "type": "default",
            "source": "songs",
            "order": "sequential",
            "is_enabled": True,
            "weight": 10,
            "backend_options": ["interrupt"],
            "schedule_items": [
                {
                    "start_time": start_hhmm,
                    "end_time": end_hhmm,
                    "days": [weekday_number]
                }
            ]
        }
        response = requests.post(
            f"{BASE_URL}/station/{station_id}/playlists",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        playlist = response.json()

        for file_id in file_ids:
            self.assign_file_to_playlist(station_id, file_id, playlist["id"])

        return playlist