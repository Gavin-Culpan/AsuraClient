import json
from azura.client import AzuraClient
from config import STATION_ID

client = AzuraClient()
monday = client.get_playlist(STATION_ID, 4805)
print(json.dumps(monday, indent=2))