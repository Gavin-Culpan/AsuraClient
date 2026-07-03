import pdfplumber
import re

PDF_PATH = "schedule.pdf"

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
    entries = list(zip(times, chunks))
    return entries

if __name__ == "__main__":
    text = extract_text(PDF_PATH)
    days = split_by_day(text)

    print(f"Found {len(days)} days: {list(days.keys())}")

    monday_key = "Monday June 29"
    monday_entries = split_into_entries(days[monday_key])
    print(f"\nMonday has {len(monday_entries)} entries")
    for time, content in monday_entries[:5]:
        print(f"\n[{time}] {content[:100].strip()}...")

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
        # No known show matched — likely an ad-only slot
        ad_split = re.split(r'Commercial\s', content)
        result["ads"] = ["Commercial " + a.strip() for a in ad_split[1:] if a.strip()]

    return result

if __name__ == "__main__":
    text = extract_text(PDF_PATH)
    days = split_by_day(text)

    print(f"Found {len(days)} days: {list(days.keys())}")

    monday_key = "Monday June 29"
    monday_entries = split_into_entries(days[monday_key])
    print(f"\nMonday has {len(monday_entries)} entries")

    for time, content in monday_entries[:5]:
        parsed = parse_entry(content)
        print(f"\n[{time}]")
        print(f"  Duration: {parsed['duration']}")
        print(f"  Guests: {parsed['guests']}")
        print(f"  Show: {parsed['show']}")
        print(f"  Episode: {parsed['episode_title']}")
        print(f"  Ads: {parsed['ads']}")