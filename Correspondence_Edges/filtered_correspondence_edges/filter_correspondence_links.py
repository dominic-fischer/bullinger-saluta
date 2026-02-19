import os
import json

# --- Paths (adjust if your folder names differ) ---
BASE_EDGES_DIR = "Correspondence_Edges"

IN_EDGES_DIR = os.path.join(BASE_EDGES_DIR, "all_correspondence_edges")
OUT_EDGES_DIR = os.path.join(BASE_EDGES_DIR, "filtered_correspondence_edges")

WHITELIST_PATH = "Nodes/filtered_nodes/all_persons_in_filtered_links.json"

UNDIRECTED_IN = os.path.join(IN_EDGES_DIR, "correspondence_pairs_undirected.json")
DIRECTED_IN   = os.path.join(IN_EDGES_DIR, "correspondence_pairs_directed.json")

UNDIRECTED_OUT = os.path.join(OUT_EDGES_DIR, "correspondence_pairs_undirected_filtered.json")
DIRECTED_OUT   = os.path.join(OUT_EDGES_DIR, "correspondence_pairs_directed_filtered.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def filter_undirected(edges, allowed):
    """
    edges format:
      {
        "p1|p2": {"count": ..., "years": {...}},
        ...
      }
    keep only if p1 and p2 are both in allowed
    """
    out = {}
    for k, v in edges.items():
        if "|" not in k:
            continue
        a, b = k.split("|", 1)
        if a in allowed and b in allowed:
            out[k] = v
    return out


def filter_directed(edges, allowed):
    """
    edges format:
      {
        "p1->p2": {"count": ..., "years": {...}},
        ...
      }
    keep only if p1 and p2 are both in allowed
    """
    out = {}
    for k, v in edges.items():
        if "->" not in k:
            continue
        a, b = k.split("->", 1)
        if a in allowed and b in allowed:
            out[k] = v
    return out


def main():
    allowed_list = load_json(WHITELIST_PATH)
    allowed = set(allowed_list)

    undirected = load_json(UNDIRECTED_IN)
    directed = load_json(DIRECTED_IN)

    undirected_f = filter_undirected(undirected, allowed)
    directed_f = filter_directed(directed, allowed)

    save_json(undirected_f, UNDIRECTED_OUT)
    save_json(directed_f, DIRECTED_OUT)

    print("Done.")
    print(f"Allowed persons: {len(allowed)}")
    print(f"Undirected: {len(undirected)} -> {len(undirected_f)}")
    print(f"Directed:   {len(directed)} -> {len(directed_f)}")
    print(f"Saved:\n  {UNDIRECTED_OUT}\n  {DIRECTED_OUT}")


if __name__ == "__main__":
    main()