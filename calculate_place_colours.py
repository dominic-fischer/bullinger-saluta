import json
import math
import colorsys
from geopy.distance import geodesic

# --- Config ---
INPUT_JSON = "lookups/place_coord_lookup.json"
OUTPUT_JSON = "lookups/place_colours_lookup.json"
REFERENCE_PLACE = "l587"

# --- Load coordinate data ---
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    coord_data = json.load(f)

if REFERENCE_PLACE not in coord_data:
    raise ValueError(f"{REFERENCE_PLACE} not found in input data.")
zurich_lat, zurich_lon = map(float, coord_data[REFERENCE_PLACE].split())
reference_coords = (zurich_lat, zurich_lon)

# --- Compute max geodesic distance (in km) ---
max_dist = max(
    geodesic(reference_coords, tuple(map(float, coord.split()))).km
    for coord in coord_data.values()
)

# --- Compute color for each place ---
results = {}

for place, coord_str in coord_data.items():
    lat, lon = map(float, coord_str.split())
    delta_y = lat - zurich_lat
    delta_x = lon - zurich_lon

    angle_rad = math.atan2(delta_y, delta_x)
    angle_deg = (math.degrees(angle_rad) + 360) % 360  # 0° = East, counter-clockwise

    hue = angle_deg / 360.0  # [0.0–1.0]
    
    distance_km = geodesic(reference_coords, (lat, lon)).km
    normalized_dist = min(distance_km / max_dist, 1.0)

    saturation = normalized_dist ** 0.4  # try values from 0.3 to 0.6
  #  center = white, edge = full color
    value = 1.0  # max brightness

    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    rgb = tuple(int(round(c * 255)) for c in (r, g, b))
    hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)

    results[place] = {
        "lat": lat,
        "lon": lon,
        "angle_deg": round(angle_deg, 2),
        "distance_km": round(distance_km, 2),
        "hue": round(hue, 4),
        "saturation": round(saturation, 4),
        "rgb": rgb,
        "hex": hex_color
    }

# --- Save results ---
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    #order by keys
    json.dump(results, f, ensure_ascii=False, indent=2, sort_keys=True)

print(f"Saved {len(results)} places with color mapping to:")
print(f"- JSON: {OUTPUT_JSON}")
