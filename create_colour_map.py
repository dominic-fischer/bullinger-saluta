import json
from pathlib import Path
import folium

# Input: your generated lookup (id -> lat/lon/hex/etc.)
DATA_PATH = Path("lookups/place_colours_lookup.json")

# Output: interactive map HTML
OUT_HTML = Path("place_colour_osm_map_nocluster.html")

# ---- Load data ----
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
points = [(k, v["lat"], v["lon"], v["hex"], v["distance_km"]) for k, v in data.items()]

# Reference point = closest to 0 km (your Zürich anchor)
ref_id, ref_lat, ref_lon, _, _ = min(points, key=lambda t: t[4])

# ---- Build map ----
m = folium.Map(
    location=[ref_lat, ref_lon],
    zoom_start=6,
    tiles="OpenStreetMap",
    control_scale=True,
)

# Add all points directly (NO clustering)
for pid, lat, lon, hx, dist in points:
    folium.CircleMarker(
        location=[lat, lon],
        radius=3,              # tweak size if needed
        color=hx,              # stroke uses your hex
        fill=True,
        fill_color=hx,         # fill uses your hex
        fill_opacity=0.95,
        opacity=0.95,
        weight=2 if pid == ref_id else 1,   # make reference stand out a bit
        popup=f"{pid}<br>dist: {dist:.1f} km<br>{lat:.5f}, {lon:.5f}",
    ).add_to(m)

# Reference marker (optional)
folium.Marker(
    [ref_lat, ref_lon],
    tooltip=f"Reference: {ref_id}",
    icon=folium.Icon(color="red", icon="star"),
).add_to(m)

# Fit view to all points
lats = [p[1] for p in points]
lons = [p[2] for p in points]
m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

# Save
m.save(str(OUT_HTML))
print(f"Saved: {OUT_HTML}")