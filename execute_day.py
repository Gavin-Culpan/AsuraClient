"""
Live execution script — writes to AzuraCast.
Run with a single weekday name to test safely before running the full week.

Usage:
    python execute_day.py Wednesday
"""

import sys
from parse_schedule import extract_text, split_by_day, process_all_days, PDF_PATH
from dry_run import build_plan
from azura.client import AzuraClient
from config import STATION_ID

WEEKDAY_NUMBERS = {
    "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
    "Friday": 5, "Saturday": 6, "Sunday": 7
}


def execute_day(client, station_id, item):
    if item["needs_create"]:
        print(f"Creating playlist '{item['weekday_name']}'...")
        new_playlist = client.create_playlist(
            station_id,
            item["weekday_name"],
            weekday_number=WEEKDAY_NUMBERS[item["weekday_name"]]
        )
        playlist_id = new_playlist["id"]
        print(f"  Created playlist id {playlist_id}")
    else:
        playlist_id = item["playlist_id"]
        print(f"Emptying existing playlist id {playlist_id}...")
        client.empty_playlist(station_id, playlist_id)

    print(f"Assigning {item['file_count']} files...")
    for i, file_id in enumerate(item["file_ids"], 1):
        client.assign_file_to_playlist(station_id, file_id, playlist_id)
        if i % 10 == 0:
            print(f"  {i}/{item['file_count']} assigned...")

    print(f"Done. {item['file_count']} files assigned to '{item['weekday_name']}'.\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python execute_day.py <WeekdayName>")
        print("Example: python execute_day.py Wednesday")
        sys.exit(1)

    target_weekday = sys.argv[1]

    text = extract_text(PDF_PATH)
    days = split_by_day(text)

    client = AzuraClient()
    media = client.get_media(STATION_ID)
    all_results, unmatched = process_all_days(days, media)

    existing_playlists_list = client.get_playlists(STATION_ID)
    existing_playlists = {p["name"]: p for p in existing_playlists_list}

    plan = build_plan(all_results, existing_playlists)

    target_item = next((p for p in plan if p["weekday_name"] == target_weekday), None)
    if not target_item:
        print(f"No plan found for '{target_weekday}'. Check spelling/capitalization.")
        sys.exit(1)

    print(f"About to execute LIVE changes for: {target_weekday}")
    print(f"  Playlist action: {'CREATE new' if target_item['needs_create'] else 'USE existing id ' + str(target_item['playlist_id'])}")
    print(f"  Files to assign: {target_item['file_count']}")
    confirm = input("Type 'yes' to proceed: ")
    if confirm.strip().lower() != "yes":
        print("Cancelled.")
        sys.exit(0)

    execute_day(client, STATION_ID, target_item)