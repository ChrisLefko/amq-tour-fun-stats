import json
import os
import re
from collections import defaultdict

# --- CONFIGURATION ---
INPUT_FOLDER = "json"  # Folder containing JSON files
CATEGORY_RANGES = [
    ("1924–1969", 1924, 1969),
    ("1970–1979", 1970, 1979),
    ("1980–1989", 1980, 1989),
    ("1990–1999", 1990, 1999),
    ("2000–2009", 2000, 2009),
    ("2010–2019", 2010, 2019),
    ("2020–2029", 2020, 2029)
]

TYPE_LABELS = {1: "Opening", 2: "Ending", 3: "Insert"}


def extract_year(vintage_str):
    """Extract a 4-digit year from a string like 'Winter 2025' or 'Fall 1981'."""
    if not vintage_str:
        return None
    match = re.search(r"(19|20)\d{2}", vintage_str)
    return int(match.group()) if match else None


def categorize_year(year):
    """Categorize a year into one of the defined ranges."""
    if not year:
        return None
    for label, start, end in CATEGORY_RANGES:
        if start <= year <= end:
            return label
    return None


def process_json_file(filepath):
    """Extract anime titles, airing years, and song types from a single JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []
    for song in data.get("songs", []):
        info = song.get("songInfo", {})
        title = info.get("animeNames", {}).get("english") or info.get("animeNames", {}).get("romaji")
        vintage = info.get("vintage")
        year = extract_year(vintage)
        song_type = info.get("type")  # 1 = OP, 2 = ED, 3 = IN
        result.append((title, year, song_type))
    return result


def summarize_all_results(folder):
    """Aggregate anime airing data and song type statistics from multiple JSON files."""
    summary = defaultdict(lambda: {"count": 0, "titles": set()})
    type_counts = defaultdict(int)
    total_files = 0
    total_songs = 0

    for filename in os.listdir(folder):
        if filename.lower().endswith(".json"):
            total_files += 1
            filepath = os.path.join(folder, filename)
            anime_data = process_json_file(filepath)
            total_songs += len(anime_data)

            for title, year, song_type in anime_data:
                # Categorize year
                category = categorize_year(year)
                if category:
                    summary[category]["count"] += 1
                    summary[category]["titles"].add(title)

                # Count song types
                if song_type in TYPE_LABELS:
                    type_counts[TYPE_LABELS[song_type]] += 1
                else:
                    type_counts["Other"] += 1

    # Convert sets to sorted lists
    for cat in summary:
        summary[cat]["titles"] = sorted(summary[cat]["titles"])

    return summary, total_files, total_songs, type_counts


def main():
    summary, total_files, total_songs, type_counts = summarize_all_results(INPUT_FOLDER)

    print(f"📁 Processed {total_files} JSON files from '{INPUT_FOLDER}'\n")
    print(f"🎵 Total songs processed: {total_songs}\n")
    print("📊 Anime Airing Year Summary:\n")

    for label, _, _ in CATEGORY_RANGES:
        info = summary.get(label, {"count": 0, "titles": []})
        count = info["count"]
        percentage = (count / total_songs * 100) if total_songs > 0 else 0
        print(f"🕰 {label}: {count} anime(s) [{percentage:.2f}%]")
        if info["titles"]:
            print("   Examples:", ", ".join(info["titles"][:5]))
        print()

    print("🎶 Song Type Breakdown:\n")
    for tlabel in ["Opening", "Ending", "Insert"]:
        count = type_counts.get(tlabel, 0)
        percentage = (count / total_songs * 100) if total_songs > 0 else 0
        print(f"   {tlabel}: {count} song(s) [{percentage:.2f}%]")

    print()


if __name__ == "__main__":
    main()
