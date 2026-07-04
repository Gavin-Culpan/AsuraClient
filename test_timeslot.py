from azura.client import AzuraClient
from config import STATION_ID

client = AzuraClient()

# Monday June 29, 12:35 AM - "Supporting a Prospect First Experience with Technology"
test_file_ids = [2370829]

print("Creating test time-slot playlist...")
playlist = client.create_timeslot_playlist(
    STATION_ID,
    name="AUTO_Mon_0035",
    weekday_number=1,
    start_hhmm=35,
    end_hhmm=40,
    file_ids=test_file_ids
)
print(f"Created playlist id {playlist['id']} with {len(test_file_ids)} files")