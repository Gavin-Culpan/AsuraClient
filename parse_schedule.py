import re
import csv
import pdfplumber
from thefuzz import fuzz
from azura.client import AzuraClient
from config import STATION_ID

PDF_PATH = "schedule.pdf"

KNOWN_SHOWS = [
    "The Lease-Up - MHN Top Marketers",
    "The Lease-Up - MHN Management Diaries",
    "The Lease-Up - MHN Mission Success",
    "The Lease-Up - MHN NAA Insights",
    "The Lease-Up - MHN Student Housing Unlocked",
    "The Lease-Up - MHN Quarterly with NMHC",
    "The apartment department",
    "The NAA Apartmentcast",
    "Multifamily Matters",
    "ChangeMakers with Katie Goar",
    "Multifamily - From The Ground Up",
    "Filed & Deranged: Property Management's Classified Circus!",
]


def extract_text(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text


def split_by_day(text):
    day_pattern = r'((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) \w+ \d{1,2})'
    parts = re.split(day_pattern, text)
    days = {}
    for i in range(1, len(parts) - 1, 2):
        day_label = parts[i]
        content = parts[i + 1]
        days[day_label] = content
    return days


def split_into_entries(day_text):
    time_pattern = r'\d{1,2}:\d{2}\s?[AP]M'
    times = re.findall(time_pattern, day_text)
    chunks = re.split(time_pattern, day_text)[1:]
    return list(zip(times, chunks))


def parse_entry(content):
    result = {
        "duration": None,
        "guests": None,
        "show": None,
        "episode_title": None,
        "ads": []
    }

    duration_match = re.match(r'^\s*((?:\d+h\s?)?(?:\d+m\s?)?(?:\d+s)?)', content)
    if duration_match:
        result["duration"] = duration_match.group(1).strip()
        content = content[duration_match.end():]

    show_found = None
    show_index = -1
    for show in KNOWN_SHOWS:
        idx = content.find(show)
        if idx != -1 and (show_index == -1 or idx < show_index):
            show_found = show
            show_index = idx

    if show_found:
        result["guests"] = content[:show_index].strip()
        result["show"] = show_found
        remainder = content[show_index + len(show_found):]

        ad_split = re.split(r'Commercial\s', remainder)
        result["episode_title"] = ad_split[0].strip()
        result["ads"] = ["Commercial " + a.strip() for a in ad_split[1:] if a.strip()]
    else:
        ad_split = re.split(r'Commercial\s', content)
        result["ads"] = ["Commercial " + a.strip() for a in ad_split[1:] if a.strip()]

    return result


def clean_title(title):
    """Strip season/episode number prefixes that often aren't in the actual media filename."""
    title = re.sub(r'^Season \d+ Episode \d+\s*', '', title)
    title = re.sub(r'^Episode\s*-\s*\d+\s*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'^EP\s*\d+:?\s*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'^\d+\s+', '', title)
    return title.strip()


def find_best_match(episode_title, media_list, threshold=70):
    cleaned = clean_title(episode_title)
    best_score = 0
    best_item = None
    for item in media_list:
        score = fuzz.token_sort_ratio(cleaned, item['title'])
        if score > best_score:
            best_score = score
            best_item = item
    if best_score >= threshold:
        return best_item, best_score
    return None, best_score


def get_top_matches(episode_title, media_list, n=3):
    cleaned = clean_title(episode_title)
    scored = []
    for item in media_list:
        score = fuzz.token_sort_ratio(cleaned, item['title'])
        scored.append((score, item['title'], item['id']))
    scored.sort(reverse=True)
    return scored[:n]


def process_all_days(days, media):
    """Parse and match every entry across every day. Returns (all_results, unmatched)."""
    all_results = {}
    unmatched = []

    for day_label, day_text in days.items():
        entries = split_into_entries(day_text)
        day_results = []

        for time, content in entries:
            parsed = parse_entry(content)
            if not parsed["show"]:
                continue  # skip ad-only slots with no show

            match, score = find_best_match(parsed["episode_title"], media)
            record = {
                "time": time,
                "show": parsed["show"],
                "episode_title": parsed["episode_title"],
                "matched_file_id": match["id"] if match else None,
                "matched_title": match["title"] if match else None,
                "score": score
            }
            day_results.append(record)

            if not match:
                unmatched.append({"day": day_label, **record})

        all_results[day_label] = day_results

    return all_results, unmatched


def export_report(all_results, filename="schedule_report.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Day", "Time", "Show", "Episode Title", "Status", "Matched File ID", "Match Score"])
        for day_label, entries in all_results.items():
            for e in entries:
                status = "MATCHED" if e["matched_file_id"] else "NEEDS UPLOAD"
                writer.writerow([
                    day_label, e["time"], e["show"], e["episode_title"],
                    status, e["matched_file_id"], e["score"]
                ])
    print(f"\nReport saved to {filename}")


if __name__ == "__main__":
    text = extract_text(PDF_PATH)
    days = split_by_day(text)
    print(f"Found {len(days)} days: {list(days.keys())}")

    client = AzuraClient()
    media = client.get_media(STATION_ID)

    all_results, unmatched = process_all_days(days, media)

    total_entries = sum(len(v) for v in all_results.values())
    print(f"\nTotal episode entries across all days: {total_entries}")
    print(f"Unmatched entries: {len(unmatched)}")

    print("\n--- Unmatched Episodes (with top 3 candidates) ---")
    for u in unmatched[:15]:
        print(f"\n[{u['day']} {u['time']}] '{u['episode_title']}'")
        top = get_top_matches(u['episode_title'], media)
        for score, title, mid in top:
            print(f"    candidate: '{title}' (score: {score}, id: {mid})")

    export_report(all_results)