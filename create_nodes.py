import json

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

# --- Load files --- #
with open("grid_assignment.json", "r", encoding="utf-8") as f:
    cities_grid = json.load(f)

with open("person_main_location_by_year.json", "r", encoding="utf-8") as f:
    person_data = json.load(f)

with open("all_persons_in_filtered_links.json", "r", encoding="utf-8") as f:
    all_actors_in_filtered_links = json.load(f)

with open("lookups/place_colours_lookup.json", "r", encoding="utf-8") as f:
    place_colours = json.load(f)

with open("lookups/place_coord_lookup.json", "r", encoding="utf-8") as f:
    place_coords= json.load(f)

with open("lookups/person_lookup.json", "r", encoding="utf-8") as f:
    person_lookup = json.load(f)

with open("lookups/place_name_lookup.json", "r", encoding="utf-8") as f:
    place_names = json.load(f)

# --- Find global min and max for clamping radius --- #
counts = [person["count"] for person in person_data.values()]
min_count = min(counts)
max_count = max(counts)

unique_counts = sorted(set(counts), reverse=True)

if len(unique_counts) >= 2:
    second_highest = unique_counts[1]
else:
    second_highest = unique_counts[0]  # fallback if only one unique value

max_count = second_highest #disregarding bullinger


def normalize_radius(count):
    # Normalize to range 1–100
    if max_count == min_count:
        return 50  # fallback if all values are the same
    return round(10 + 99 * (count - min_count) / (max_count - min_count))

# --- Process each person --- #
nodes = []
locations = set()

for person_id, entry in person_data.items():
    if person_id not in all_actors_in_filtered_links:
        continue

    count = entry["count"]
    radius = normalize_radius(count)
    years_locations = entry.get("locations", {})

    # Convert years to integers and sort
    year_loc_pairs = sorted([(int(year), loc) for year, loc in years_locations.items()])
    #print(year_loc_pairs)

    # Determine start and end years
    if not year_loc_pairs:
        continue
    start_year = year_loc_pairs[0][0]
    end_year = year_loc_pairs[-1][0]

    # Build colorSchedule as (color, start, end) ranges
    colorSchedule = []
    current_color = None
    range_start = None
    prev_year = None
    current_loc_id = None

    for year, loc_id in year_loc_pairs:
        color = place_colours.get(loc_id, {}).get("hex", "#cccccc")
        
        if current_color is None:
            current_color = color
            current_loc_id = loc_id
            range_start = year
        elif color != current_color or loc_id != current_loc_id:
            # Check for gap
            if prev_year is not None and year > prev_year + 1:
                colorSchedule.append([current_color, range_start, prev_year, place_names.get(current_loc_id)])
                colorSchedule.append([current_color, prev_year + 1, year - 1, place_names.get(current_loc_id)])
            else:
                colorSchedule.append([current_color, range_start, prev_year, place_names.get(current_loc_id)])
            
            current_color = color
            current_loc_id = loc_id
            range_start = year

        prev_year = year

    # Close final range
    if current_color is not None and range_start is not None and prev_year is not None:
        colorSchedule.append([current_color, range_start, prev_year, place_names.get(current_loc_id)])

    # Track location usage
    locations.add(year_loc_pairs[0][1])


    # Add node entry
    nodes.append({
        "id": person_id,
        "name": person_lookup.get(person_id, person_id),
        "radius": min(radius, 100),
        "start": start_year,
        "end": end_year,
        "location": year_loc_pairs[0][1],
        "starting_loc_x": cities_grid.get(year_loc_pairs[0][1]).get("grid_cell").get("row"),
        "starting_loc_y": cities_grid.get(year_loc_pairs[0][1]).get("grid_cell").get("col"),
        "colorSchedule": colorSchedule
    })

with open("all_persons_in_filtered_links.json", "r", encoding="utf-8") as f:
    all_actors = json.load(f)
with open("lookups/person_lookup.json", "r", encoding="utf-8") as f:
    person_lookup = json.load(f)
with open("all_person_nodes.json", "r", encoding="utf-8") as f:
    all_person_nodes = json.load(f)

import json

with open("filtered_links.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for actor in all_actors:
    min_year = float("inf")
    max_year = float("-inf")
    year_loc_pairs = []

    # Collect all years and optionally link partner/location info
    for key, year_dict in data.items():
        participants = key.split("|")
        if actor in participants:
            other = [p for p in participants if p != actor]
            for year_str, count in year_dict.items():
                year = int(year_str)
                if year < min_year:
                    min_year = year
                if year > max_year:
                    max_year = year
                year_loc_pairs.append((year, other[0] if other else actor))  # fallback in case of malformed key

    if min_year != float("inf") and max_year != float("-inf") and year_loc_pairs:
        year_loc_pairs.sort()  # sort by year

        loc_id = year_loc_pairs[0][1]
        grid_info = cities_grid.get(loc_id, {}).get("grid_cell", {"row": None, "col": None})

        if actor not in all_person_nodes:
            nodes.append({
                "id": actor,
                "name": person_lookup.get(actor, actor),
                "radius": normalize_radius(1),
                "start": min_year,
                "end": max_year,
            })
            #print(f"Added new node for {person_lookup.get(actor, actor)} with start year {min_year} and end year {max_year}")
        elif actor in all_person_nodes:
            # check the start year
            existing_node = next((n for n in nodes if n["id"] == actor), None)
            if existing_node and existing_node["start"] > min_year:
                keep_original_start = existing_node["start"]
                existing_node["start"] = min(existing_node["start"], min_year)
                print(f"Updated start year for {person_lookup.get(actor)} from {keep_original_start} to {existing_node['start']}")

locations = list(locations)
print(len(locations))

loc_coords = [[l, place_coords.get(l)] for l in locations]

# --- Save result --- #
with open("person_nodes.json", "w", encoding="utf-8") as f:
    json.dump(nodes, f, ensure_ascii=False, indent=2)

with open("all_involved_cities.json", "w", encoding="utf-8") as f:
    json.dump(loc_coords, f, ensure_ascii=False, indent=2)
