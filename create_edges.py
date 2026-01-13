import json
import re

# --- Load data --- #
with open("filtered_links.json", "r", encoding="utf-8") as f:
    edges_files = json.load(f)

with open("lookups/person_lookup.json", "r", encoding="utf-8") as f:
    person_lookup = json.load(f)

# --- Generate per-year links --- #
links = []

for pair, years in edges_files.items():
    source_id, target_id = pair.split("|")
    source_name = person_lookup.get(source_id, source_id)
    target_name = person_lookup.get(target_id, target_id)

    for year_str, value in years.items():
        year = int(year_str)
        links.append({
            "source": source_id,
            "sourceId": source_id,
            "target": target_id,
            "targetId": target_id,
            "start": year,
            "end": year,
            "thickness": value
        })

# --- Save to file --- #
with open("yearly_links.json", "w", encoding="utf-8") as f:
    json.dump(links, f, ensure_ascii=False, indent=2)
