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

print("\n--- Monday Playlist Contents ---")
media = client.get_media(STATION_ID)

monday_items = [
    item for item in media
    if any(pl['id'] == 4805 for pl in item['playlists'])
]

print(f"Total items in Monday: {len(monday_items)}")
for item in monday_items[:10]:
    print(f"- {item['title']} by {item['artist']} ({item['length_text']})")