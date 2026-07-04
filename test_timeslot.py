import requests
from azura.client import AzuraClient
from config import STATION_ID, API_KEY, BASE_URL

client = AzuraClient()
response = requests.delete(f"{BASE_URL}/station/{STATION_ID}/playlist/7782", headers=client.headers)
print("Delete status:", response.status_code)