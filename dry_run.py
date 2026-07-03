"""
Dry-run planner for weekly schedule assignment.

This script:
1. Parses the weekly PDF schedule
2. Matches episodes + ads to existing AzuraCast media (same as parse_schedule.py)
3. Figures out, per weekday, whether a playlist needs to be created
4. Builds the exact list of file IDs that would be assigned to each day's playlist
5. PRINTS the plan only — makes NO changes to AzuraCast

Once you've reviewed the plan and it looks right, we'll flip DRY_RUN to False
in a later step to actually execute it.
"""

from parse_schedule import extract_text, split_by_day, process_all_days, PDF_PATH
from azura.client import AzuraClient
from config import STATION_ID

DRY_RUN = True

WEEKDAY_NUMBERS = {
    "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
    "Friday": 5, "Saturday": 6, "Sunday": 7
}


def get_weekday_name(day_label):
    """'Monday June 29' -> 'Monday'"""
    return day_label.split()[0]


def build_plan(all_results, existing_playlists):
    """
    existing_playlists: dict of {weekday_name: playlist_dict} from AzuraCast
    Returns a list of per-weekday action plans.
    """
    plan = []
    seen_weekdays = set()

    for day_label, entries in all_results.items():
        weekday_name = get_weekday_name(day_label)

        # The PDF spans 8 calendar days (Mon June 29 -> Mon July 6), which means
        # "Monday" appears twice. We only want ONE plan per weekday name, using
        # the first occurrence, since playlists are recurring by weekday, not by date.
        if weekday_name in seen_weekdays:
            continue
        seen_weekdays.add(weekday_name)

        existing = existing_playlists.get(weekday_name)
        needs_create = existing is None

        file_ids_in_order = []
        for e in entries:
            if e["matched_file_id"]:
                file_ids_in_order.append(e["matched_file_id"])
            for ad in e["ads"]:
                if ad["matched_file_id"]:
                    file_ids_in_order.append(ad["matched_file_id"])

        plan.append({
            "weekday_name": weekday_name,
            "day_label": day_label,
            "playlist_id": existing["id"] if existing else None,
            "needs_create": needs_create,
            "file_count": len(file_ids_in_order),
            "file_ids": file_ids_in_order
        })

    return plan


if __name__ == "__main__":
    text = extract_text(PDF_PATH)
    days = split_by_day(text)

    client = AzuraClient()
    media = client.get_media(STATION_ID)
    all_results, unmatched = process_all_days(days, media)

    existing_playlists_list = client.get_playlists(STATION_ID)
    existing_playlists = {p["name"]: p for p in existing_playlists_list}

    plan = build_plan(all_results, existing_playlists)

    print("=== DRY RUN PLAN ===\n")
    for item in plan:
        if item["needs_create"]:
            action = f"CREATE new playlist '{item['weekday_name']}' (weekday {WEEKDAY_NUMBERS[item['weekday_name']]})"
        else:
            action = f"USE existing playlist (id {item['playlist_id']})"

        print(f"{item['weekday_name']}  [{action}]")
        print(f"  Would EMPTY the playlist, then ASSIGN {item['file_count']} matched files in order")
        print(f"  First 5 file IDs: {item['file_ids'][:5]}")
        print()

    print(f"Total unmatched episode entries across the week: {len(unmatched)}")
    print("(These won't be assigned anywhere since no matching file exists yet.)\n")

    if DRY_RUN:
        print("DRY_RUN is True — no changes were made to AzuraCast. This was a preview only.")
    else:
        print("LIVE MODE — this would now execute the actions above against AzuraCast.")