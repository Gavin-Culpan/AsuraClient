import requests
import re

with open("openapi.yml", "r", encoding="utf-8") as f:
    text = f.read()

def print_section(anchor, lines_after=60):
    idx = text.find(anchor)
    if idx == -1:
        print(f"NOT FOUND: {anchor}")
        return
    snippet = text[idx:idx + 3000]
    print(f"\n=== {anchor} ===")
    print(snippet)

print_section("putStationFileBatchAction", lines_after=100)
print_section("/station/{station_id}/file/{id}':", lines_after=150)
print_section("StationMedia:", lines_after=200)

idx = text.find("playlists:\n                            type: array")
print(text[idx:idx+600])

idx = text.find("'/station/{station_id}/playlists':")
print(text[idx:idx+2500])

idx = text.find("StationPlaylist:")
print(text[idx:idx+2500])

idx = text.find("/station/{station_id}/playlist/{id}/queue")
print(text[idx:idx+2000])