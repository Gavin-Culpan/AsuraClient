import json
from azura.client import AzuraClient
from config import STATION_ID

client = AzuraClient()

test_playlist = client.get_playlist(STATION_ID, 7782)
print(json.dumps(test_playlist, indent=2))