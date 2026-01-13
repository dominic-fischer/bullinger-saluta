import os
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
import json

# Namespace
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}
XMLID = '{http://www.w3.org/XML/1998/namespace}id'

all_person_nodes = []

# --- Process letters --- #
letter_folder = '/Users/Dominic-Asus/bullinger-korpus-tei/data/letters'
person_data = defaultdict(lambda: {"count": 0, "locations": defaultdict(list)})

for filename in os.listdir(letter_folder):
    if not filename.endswith('.xml'):
        continue
    path = os.path.join(letter_folder, filename)
    tree = ET.parse(path)
    root = tree.getroot()

    # Try to extract the main date once from the sent block
    date_elem = root.find('.//tei:correspAction[@type="sent"]/tei:date', NS)
    date = date_elem.attrib.get('notBefore') or date_elem.attrib.get('when') if date_elem is not None else None
    year = date[:4] if date else None

    for action in root.findall('.//tei:correspAction', NS):
        person_elems = action.findall('tei:persName', NS)
        place_elem = action.find('tei:placeName', NS)

        location_ref = place_elem.attrib.get('ref') if place_elem is not None else None
        location_name = location_ref  # optional renaming

        for person_elem in person_elems:
            person_ref = person_elem.attrib.get('ref')
            if person_ref:
                person = person_ref
                person_data[person]["count"] += 1
                if location_name and year:
                    person_data[person]["locations"][year].append(location_name)
                all_person_nodes.append(person_ref)


# --- Sort years --- #
person_data_sorted = {
    person: {
        "count": data["count"],
        "locations": dict(sorted(data["locations"].items()))
    }
    for person, data in person_data.items()
}

# --- Most frequent location per year --- #
most_frequent_by_year = {}

for person, data in person_data_sorted.items():
    year_summary = {}

    # 1. Build global count across all years for fallback
    global_loc_counts = defaultdict(int)
    for locs in data["locations"].values():
        for loc in locs:
            global_loc_counts[loc] += 1

    # 2. Choose per-year most frequent location
    for year, loc_list in data["locations"].items():
        counts = defaultdict(int)
        for loc in loc_list:
            counts[loc] += 1

        max_count = max(counts.values())
        tied_locs = [loc for loc, c in counts.items() if c == max_count]

        if len(tied_locs) == 1:
            chosen = tied_locs[0]
        else:
            # Tie → pick one with highest global count
            chosen = max(tied_locs, key=lambda l: global_loc_counts[l])

        year_summary[year] = chosen

    most_frequent_by_year[person] = {
        "count": data["count"],
        "locations": year_summary
    }


# --- Save to JSON --- #
with open("person_locations_by_year.json", "w", encoding="utf-8") as f:
    json.dump(person_data_sorted, f, indent=2, ensure_ascii=False)

with open("person_main_location_by_year.json", "w", encoding="utf-8") as f:
    json.dump(most_frequent_by_year, f, indent=2, ensure_ascii=False)

with open("all_person_nodes.json", "w", encoding="utf-8") as f:
    json.dump(all_person_nodes, f, indent=2, ensure_ascii=False)
    



