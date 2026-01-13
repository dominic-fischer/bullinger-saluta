import json


with open("all_persons_in_filtered_links.json", "r", encoding="utf-8") as f:
    all_actors = json.load(f)
with open("lookups/person_lookup.json", "r", encoding="utf-8") as f:
    person_lookup = json.load(f)
with open("person_nodes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for actor in all_actors:
    if any(actor in d['id'] for d in data):
        print(f"Actor {actor} not found in person nodes.")