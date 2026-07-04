import json
from azura.client import AzuraClient
from config import STATION_ID

client = AzuraClient()

playlists = client.get_playlists(STATION_ID)
auto_mon = [p for p in playlists if p["name"].startswith("AUTO_Mon")]

print(f"Found {len(auto_mon)} AUTO_Mon playlists\n")
for p in auto_mon[:3]:
    detail = client.get_playlist(STATION_ID, p["id"])
    print(f"{detail['name']}: {detail['num_songs']} songs, schedule: {detail['schedule_items']}")
    