import os
import json

# --- Paths (adjust if needed) ---
BASE_EDGES_DIR = "Correspondence_Edges/filtered_correspondence_edges"

IN_PATH = os.path.join(BASE_EDGES_DIR, "correspondence_pairs_undirected_filtered.json")
OUT_PATH = os.path.join("yearly_correspondence_links.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    folder = os.path.dirname(path)
    if folder:  # only create folder if it exists
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def main():
    data = load_json(IN_PATH)

    out = []
    skipped_keys = 0
    skipped_years = 0

    for key, payload in data.items():
        # key is "pA|pB"
        if "|" not in key:
            skipped_keys += 1
            continue

        a, b = key.split("|", 1)

        years = payload.get("years", {})
        if not isinstance(years, dict):
            skipped_years += 1
            continue

        for year_str, count in years.items():
            # year_str like "1532"
            try:
                year = int(year_str)
            except (ValueError, TypeError):
                skipped_years += 1
                continue

            # some safety: thickness must be int
            try:
                thickness = int(count)
            except (ValueError, TypeError):
                skipped_years += 1
                continue

            out.append({
                "source": a,
                "sourceId": a,
                "target": b,
                "targetId": b,
                "start": year,
                "end": year,
                "thickness": thickness
            })

    # Optional: sort for readability (by year then thickness desc)
    out.sort(key=lambda e: (e["start"], -e["thickness"], e["source"], e["target"]))

    save_json(out, OUT_PATH)

    print("Done.")
    print(f"Input pairs: {len(data)}")
    print(f"Output edges (pair-year rows): {len(out)}")
    if skipped_keys or skipped_years:
        print(f"Skipped: bad keys={skipped_keys}, bad years/counts={skipped_years}")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()