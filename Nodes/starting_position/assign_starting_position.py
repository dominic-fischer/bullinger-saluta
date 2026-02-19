from typing import List, Tuple

def assign_grid(coords: List[str]) -> List[Tuple[str, Tuple[int, int]]]:
    coords_float = [tuple(map(float, c.split())) for c in coords]

    # Extract latitudes and longitudes
    lats = [lat for lat, _ in coords_float]
    lons = [lon for _, lon in coords_float]

    # Compute bounding box
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)

    lat_step = (lat_max - lat_min) / 3
    lon_step = (lon_max - lon_min) / 3

    def get_row(lat):
        if lat < lat_min + lat_step:
            return 2  # bottom
        elif lat < lat_min + 2 * lat_step:
            return 1  # middle
        else:
            return 0  # top

    def get_col(lon):
        if lon < lon_min + lon_step:
            return 0  # left
        elif lon < lon_min + 2 * lon_step:
            return 1  # middle
        else:
            return 2  # right

    return [
        (original, (get_row(lat), get_col(lon)))
        for original, (lat, lon) in zip(coords, coords_float)
    ]



from typing import List, Tuple

from typing import List, Tuple
import numpy as np

def assign_quantile_grid(coords: List[str]) -> List[Tuple[str, Tuple[int, int]]]:
    coords_float = [tuple(map(float, c.split())) for c in coords]
    lats = np.array([lat for lat, _ in coords_float])
    lons = np.array([lon for _, lon in coords_float])

    # Compute quantile thresholds (33.3% and 66.6%)
    lat_q1, lat_q2 = np.quantile(lats, [1/3, 2/3])
    lon_q1, lon_q2 = np.quantile(lons, [1/3, 2/3])

    def get_row(lat):
        if lat > lat_q2:
            return 0  # top
        elif lat > lat_q1:
            return 1  # middle
        else:
            return 2  # bottom

    def get_col(lon):
        if lon < lon_q1:
            return 0  # left
        elif lon < lon_q2:
            return 1  # middle
        else:
            return 2  # right

    return [
        (original, (get_row(lat), get_col(lon)))
        for original, (lat, lon) in zip(coords, coords_float)
    ]


# -----------------------------------------------------------------------


# Example usage
import json
with open("Nodes/starting_position/all_involved_cities.json", "r",encoding="utf-8") as f:
    cities = json.load(f)

with open("lookups/place_name_lookup.json", "r", encoding="utf-8") as f:
    place_names= json.load(f)

coords = [t[1] for t in cities]
coords_reverse_mapping = {t[1]:t[0] for t in cities}


result = assign_quantile_grid(coords)

# Print result
# Initialize empty 3x3 grid
grid = [[[] for _ in range(3)] for _ in range(3)]

# Fill the grid with place names or coordinates
for coord_str, (row, col) in result:
    place_id = coords_reverse_mapping.get(coord_str)
    name = place_names.get(place_id, coord_str)
    grid[row][col].append(name)

# Print the grid (row 0 is top)
def print_grid(result, coords_reverse_mapping, place_names):
    # Initialize empty 3x3 grid
    grid = [[[] for _ in range(3)] for _ in range(3)]

    # Fill grid with resolved names (or fall back to coordinates)
    for coord_str, (row, col) in result:
        place_id = coords_reverse_mapping.get(coord_str)
        name = place_names.get(place_id, coord_str)
        grid[row][col].append(name)

    # Compute max height per cell for alignment
    max_rows = max(len(cell) for row in grid for cell in row)

    # Create formatted rows
    def format_cell(lines, height):
        lines = lines + [''] * (height - len(lines))  # pad
        return lines

    print("\nGrid Visualization (3×3):\n")

    horizontal_line = "+--------------------------" * 3 + "+"

    for row in grid:
        # Prepare each column's content as vertical stacks
        col_contents = [format_cell(cell, max_rows) for cell in row]

        for i in range(max_rows):
            line = "|"
            for cell in col_contents:
                line += f" {cell[i]:<24} |"
            print(line)
        print(horizontal_line)


print_grid(result, coords_reverse_mapping, place_names)



# Convert to a dictionary for JSON saving
json_result = {
    coords_reverse_mapping.get(coord_str) : {
        "coordinates": coord_str,
        "name": place_names.get(coords_reverse_mapping.get(coord_str)),
        "grid_cell": {"row": row, "col": col}
    }
    for coord_str, (row, col) in result
    }


# Save to file
with open("Nodes/starting_position/grid_assignment.json", "w", encoding="utf-8") as f:
    json.dump(json_result, f, indent=2)

print("Saved to Nodes/starting_position/grid_assignment.json")
