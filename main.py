from azura.client import AzuraClient
from config import STATION_ID

client = AzuraClient()

station = client.get_station(STATION_ID)
print(f"Station: {station['name']}")
print(f"ID: {station['id']}")
print(f"Timezone: {station['timezone']}")
print(f"Website: {station['url']}")

print("\n--- Media Files ---")
media = client.get_media(STATION_ID)
print(f"Total files: {len(media)}")
for item in media[:5]:
    print(f"- {item['title']} by {item['artist']} ({item['length_text']})")

print("\n--- Playlists ---")
playlists = client.get_playlists(STATION_ID)
print(f"Total playlists: {len(playlists)}")
for pl in playlists:
    print(f"- {pl['name']} (ID: {pl['id']})")