"""
Live execution script for exact-time slot playlists.
Run for ONE weekday at a time to test safely before running the full week.

Usage:
    python execute_timeslots.py Monday
"""

import sys
from dry_run_timeslots import build_timeslot_plan
from parse_schedule import extract_text, split_by_day, process_all_days, PDF_PATH
from azura.client import AzuraClient
from config import STATION_ID


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python execute_timeslots.py <WeekdayName>")
        print("Example: python execute_timeslots.py Monday")
        sys.exit(1)

    target_weekday = sys.argv[1]

    text = extract_text(PDF_PATH)
    days = split_by_day(text)

    client = AzuraClient()
    media = client.get_media(STATION_ID)
    all_results, unmatched = process_all_days(days, media)

    full_plan = build_timeslot_plan(all_results)
    day_plan = [item for item in full_plan if item["weekday_name"] == target_weekday]

    if not day_plan:
        print(f"No slots found for '{target_weekday}'. Check spelling/capitalization.")
        sys.exit(1)

    print(f"About to create {len(day_plan)} timeslot playlists for {target_weekday}:")
    for item in day_plan[:5]:
        print(f"  {item['name']}  {item['start_hhmm']:04d}-{item['end_hhmm']:04d}  "
              f"{item['episode_title'][:50]}  ({len(item['file_ids'])} files)")
    if len(day_plan) > 5:
        print(f"  ... and {len(day_plan) - 5} more")

    confirm = input(f"\nType 'yes' to create these {len(day_plan)} playlists live: ")
    if confirm.strip().lower() != "yes":
        print("Cancelled.")
        sys.exit(0)

    created = 0
    failed = []

    for item in day_plan:
        try:
            client.create_timeslot_playlist(
                STATION_ID,
                name=item["name"],
                weekday_number=item["weekday_num"],
                start_hhmm=item["start_hhmm"],
                end_hhmm=item["end_hhmm"],
                file_ids=item["file_ids"]
            )
            created += 1
            print(f"  [{created}/{len(day_plan)}] Created {item['name']}")
        except Exception as ex:
            failed.append((item["name"], str(ex)))
            print(f"  FAILED: {item['name']} - {ex}")

    print(f"\nDone. Created {created}/{len(day_plan)} playlists.")
    if failed:
        print(f"\n{len(failed)} FAILURES:")
        for name, err in failed:
            print(f"  {name}: {err}")