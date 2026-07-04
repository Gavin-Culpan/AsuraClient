"""
Deletes all auto-generated timeslot playlists (name starts with 'AUTO_')
so a fresh week can be built without duplicates or stale schedules.

Safe by design: only touches playlists whose name starts with 'AUTO_'.
Your real playlists (Monday, Tuesday, Sunday, On Demand, etc.) are never
touched, since they don't match that prefix.

Run in DRY_RUN mode first to see what WOULD be deleted.
"""

from azura.client import AzuraClient
from config import STATION_ID

DRY_RUN = False
PREFIX = "AUTO_"

if __name__ == "__main__":
    client = AzuraClient()
    playlists = client.get_playlists(STATION_ID)

    auto_playlists = [p for p in playlists if p["name"].startswith(PREFIX)]

    print(f"Found {len(auto_playlists)} playlists starting with '{PREFIX}':")
    for p in auto_playlists:
        print(f"  - {p['name']} (id: {p['id']}, {p['num_songs']} songs)")

    if not auto_playlists:
        print("\nNothing to clean up.")
        exit(0)

    if DRY_RUN:
        print(f"\nDRY_RUN is True — no playlists were deleted. {len(auto_playlists)} would be removed.")
    else:
        confirm = input(f"\nType 'yes' to permanently delete these {len(auto_playlists)} playlists: ")
        if confirm.strip().lower() != "yes":
            print("Cancelled.")
            exit(0)

        for p in auto_playlists:
            client.delete_playlist(STATION_ID, p["id"])
            print(f"Deleted: {p['name']} (id: {p['id']})")

        print(f"\nDone. Deleted {len(auto_playlists)} playlists.")