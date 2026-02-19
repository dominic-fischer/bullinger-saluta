import os
import json
import xml.etree.ElementTree as ET
from collections import defaultdict

# --- TEI namespace ---
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

# --- Input / Output ---
LETTER_FOLDER = '/Users/Dominic-Asus/bullinger-korpus-tei/data/letters'
OUT_FOLDER = 'Correspondence_Edges/all_correspondence_edges'
os.makedirs(OUT_FOLDER, exist_ok=True)

# --- Helpers ---
def get_year(root):
    """Try to extract year from the sent date (notBefore/when)."""
    date_elem = root.find('.//tei:correspAction[@type="sent"]/tei:date', NS)
    if date_elem is None:
        return None
    date = date_elem.attrib.get('notBefore') or date_elem.attrib.get('when')
    return date[:4] if date else None

def get_person_refs(action_elem):
    """Return set of @ref values from persName elements inside a correspAction."""
    if action_elem is None:
        return set()
    refs = set()
    for p in action_elem.findall('tei:persName', NS):
        r = p.attrib.get('ref')
        if r:
            refs.add(r)
    return refs

def canonical_pair(a, b):
    """Unordered pair key (A|B) with stable ordering."""
    return "|".join(sorted([a, b]))

# --- Data structures ---
# Undirected pair counts
pair_counts = defaultdict(int)
pair_year_counts = defaultdict(lambda: defaultdict(int))

# Optional: directed counts
directed_counts = defaultdict(int)
directed_year_counts = defaultdict(lambda: defaultdict(int))

# Optional: keep a list of files contributing to each edge (can be big)
# pair_files = defaultdict(list)

# --- Main loop ---
for filename in os.listdir(LETTER_FOLDER):
    if not filename.endswith('.xml'):
        continue

    path = os.path.join(LETTER_FOLDER, filename)
    try:
        tree = ET.parse(path)
    except ET.ParseError:
        # skip broken xml
        continue

    root = tree.getroot()
    year = get_year(root)

    sent_action = root.find('.//tei:correspAction[@type="sent"]', NS)
    recv_action = root.find('.//tei:correspAction[@type="received"]', NS)

    senders = get_person_refs(sent_action)
    receivers = get_person_refs(recv_action)

    # If either side missing, we can't form a pair
    if not senders or not receivers:
        continue

    # Build all pairs for this letter, but count each pair only once per file
    seen_undirected_pairs_this_letter = set()
    seen_directed_pairs_this_letter = set()

    for s in senders:
        for r in receivers:
            if s == r:
                continue

            # Undirected (exchanged)
            ukey = canonical_pair(s, r)
            seen_undirected_pairs_this_letter.add(ukey)

            # Directed (sent -> received)
            dkey = f"{s}->{r}"
            seen_directed_pairs_this_letter.add(dkey)

    # Apply counts once per pair per letter
    for ukey in seen_undirected_pairs_this_letter:
        pair_counts[ukey] += 1
        if year:
            pair_year_counts[ukey][year] += 1
        # pair_files[ukey].append(filename)

    for dkey in seen_directed_pairs_this_letter:
        directed_counts[dkey] += 1
        if year:
            directed_year_counts[dkey][year] += 1

# --- Build output objects ---
edges_undirected = {
    pair: {
        "count": cnt,
        "years": dict(sorted(pair_year_counts[pair].items()))
    }
    for pair, cnt in pair_counts.items()
}

edges_directed = {
    pair: {
        "count": cnt,
        "years": dict(sorted(directed_year_counts[pair].items()))
    }
    for pair, cnt in directed_counts.items()
}

# --- Save JSON ---
with open(os.path.join(OUT_FOLDER, "correspondence_pairs_undirected.json"), "w", encoding="utf-8") as f:
    json.dump(edges_undirected, f, indent=2, ensure_ascii=False)

with open(os.path.join(OUT_FOLDER, "correspondence_pairs_directed.json"), "w", encoding="utf-8") as f:
    json.dump(edges_directed, f, indent=2, ensure_ascii=False)

print(f"Saved {len(edges_undirected)} undirected pairs and {len(edges_directed)} directed pairs.")
# also print the counts
total_undirected = sum(e["count"] for e in edges_undirected.values())
total_directed = sum(e["count"] for e in edges_directed.values())
print(f"Total undirected edges (exchanges): {total_undirected}")
print(f"Total directed edges (sent->received): {total_directed}")