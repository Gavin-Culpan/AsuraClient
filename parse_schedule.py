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