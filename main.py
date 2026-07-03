from azura.client import AzuraClient
from config import STATION_ID

client = AzuraClient()

station = client.get_station(STATION_ID)

print(f"Station: {station['name']}")
print(f"ID: {station['id']}")
print(f"Timezone: {station['timezone']}")
print(f"Website: {station['url']}")