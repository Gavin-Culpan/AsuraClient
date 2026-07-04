"""
Dry-run planner for the FULL exact-time weekly schedule.

Builds the complete list of timeslot playlists that would be created for
every matched entry across the whole week - one playlist per time slot,
each containing that slot's episode + its matched ads, scheduled to
interrupt at the exact clock time.

Makes ZERO API calls that write anything. Preview only.
"""

import re
from parse_schedule import extract_text, split_by_day, process_all_days, PDF_PATH
from azura.client import AzuraClient
from config import STATION_ID

WEEKDAY_NUMBERS = {
    "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
    "Friday": 5, "Saturday": 6, "Sunday": 7
}


def get_weekday_name(day_label):
    return day_label.split()[0]


def time_to_hhmm(time_str):
    """'9:00 AM' -> 900, '12:35 AM' -> 35, '11:45 PM' -> 2345"""
    match = re.match(r'(\d{1,2}):(\d{2})\s?([AP]M)', time_str.strip())
    hour, minute, meridiem = int(match.group(1)), int(match.group(2)), match.group(3)

    if meridiem == "AM" and hour == 12:
        hour = 0
    elif meridiem == "PM" and hour != 12:
        hour += 12

    return hour * 100 + minute


def add_minutes_hhmm(hhmm, minutes_to_add):
    """Properly add minutes to an HHMM-style time, rolling hours/minutes over correctly."""
    hour = hhmm // 100
    minute = hhmm % 100
    total_minutes = hour * 60 + minute + minutes_to_add
    total_minutes %= (24 * 60)  # wrap past midnight
    new_hour = total_minutes // 60
    new_minute = total_minutes % 60
    return new_hour * 100 + new_minute


def hhmm_label(hhmm):
    """900 -> '0900', 35 -> '0035' - for naming playlists consistently"""
    return f"{hhmm:04d}"


def build_timeslot_plan(all_results):
    """
    Returns a list of timeslot actions, one per matched entry, across the
    whole week (only the FIRST occurrence of each weekday name, since the
    PDF spans 8 calendar days but playlists are recurring by weekday).
    """
    plan = []
    seen_weekdays = set()

    for day_label, entries in all_results.items():
        weekday_name = get_weekday_name(day_label)
        if weekday_name in seen_weekdays:
            continue
        seen_weekdays.add(weekday_name)

        weekday_num = WEEKDAY_NUMBERS[weekday_name]
        weekday_short = weekday_name[:3]

        for e in entries:
            if not e["matched_file_id"]:
                continue  # skip episodes with no matched audio - nothing to schedule

            start_hhmm = time_to_hhmm(e["time"])
            end_hhmm = add_minutes_hhmm(start_hhmm, 5)

            file_ids = [e["matched_file_id"]]
            for ad in e["ads"]:
                if ad["matched_file_id"]:
                    file_ids.append(ad["matched_file_id"])

            name = f"AUTO_{weekday_short}_{hhmm_label(start_hhmm)}"

            plan.append({
                "name": name,
                "weekday_name": weekday_name,
                "weekday_num": weekday_num,
                "start_hhmm": start_hhmm,
                "end_hhmm": end_hhmm,
                "show": e["show"],
                "episode_title": e["episode_title"],
                "file_ids": file_ids
            })

    return plan


if __name__ == "__main__":
    text = extract_text(PDF_PATH)
    days = split_by_day(text)

    client = AzuraClient()
    media = client.get_media(STATION_ID)
    all_results, unmatched = process_all_days(days, media)

    plan = build_timeslot_plan(all_results)

    print(f"Total timeslot playlists that would be created: {len(plan)}\n")

    print("--- First 10 slots (sanity check) ---")
    for item in plan[:10]:
        print(f"{item['name']}  |  {item['weekday_name']} {item['start_hhmm']:04d}-{item['end_hhmm']:04d}  |  "
              f"{item['episode_title'][:50]}  |  {len(item['file_ids'])} files")

    # Count per weekday for a quick sanity check
    from collections import Counter
    counts = Counter(item["weekday_name"] for item in plan)
    print("\n--- Slots per weekday ---")
    for day, count in counts.items():
        print(f"  {day}: {count}")

    print("\nDRY RUN ONLY - no playlists were created.")