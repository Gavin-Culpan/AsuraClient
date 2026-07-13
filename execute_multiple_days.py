"""
Run timeslot playlist creation for MULTIPLE weekdays in one go.

Usage:
    python execute_multiple_days.py Thursday Friday Saturday Sunday
"""

import sys
from dry_run_timeslots import build_timeslot_plan
from parse_schedule import extract_text, split_by_day, process_all_days, PDF_PATH
from azura.client import AzuraClient
from config import STATION_ID


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python execute_multiple_days.py <Day1> <Day2> ...")
        print("Example: python execute_multiple_days.py Thursday Friday Saturday Sunday")
        sys.exit(1)

    target_weekdays = sys.argv[1:]

    text = extract_text(PDF_PATH)
    days = split_by_day(text)

    client = AzuraClient()
    media = client.get_media(STATION_ID)
    all_results, unmatched = process_all_days(days, media)

    full_plan = build_timeslot_plan(all_results)

    combined_plan = [item for item in full_plan if item["weekday_name"] in target_weekdays]

    if not combined_plan:
        print(f"No slots found for any of: {target_weekdays}. Check spelling/capitalization.")
        sys.exit(1)

    print(f"About to create timeslot playlists for: {', '.join(target_weekdays)}")
    print(f"Total playlists across all selected days: {len(combined_plan)}\n")

    for day in target_weekdays:
        count = len([item for item in combined_plan if item["weekday_name"] == day])
        print(f"  {day}: {count} slots")

    confirm = input(f"\nType 'yes' to create these {len(combined_plan)} playlists live: ")
    if confirm.strip().lower() != "yes":
        print("Cancelled.")
        sys.exit(0)

    created = 0
    failed = []

    for item in combined_plan:
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
            print(f"  [{created}/{len(combined_plan)}] Created {item['name']}")
        except Exception as ex:
            failed.append((item["name"], str(ex)))
            print(f"  FAILED: {item['name']} - {ex}")

    print(f"\nDone. Created {created}/{len(combined_plan)} playlists.")
    if failed:
        print(f"\n{len(failed)} FAILURES:")
        for name, err in failed:
            print(f"  {name}: {err}")