import json

def filter_links(links_file="all_links.json", outfile="filtered_links.json"):
    with open(links_file, "r", encoding="utf-8") as f:
        edges_files = json.load(f)

    threshold = 10
    filtered_edges = {}

    for k, v in edges_files.items():
        # filter out entries where the sum across all years is lower than the threshold
        if sum(v.values()) >= threshold:
            print(k, v)
            filtered_edges[k] = v

    all_actors = set()

    # find out how many unique actors are involved
    for k in filtered_edges:
        actors = k.split("|")
        for name in actors:
            all_actors.add(name)

    all_actors = list(all_actors)
    print(len(all_actors))

    with open("all_persons_in_filtered_links.json", "w", encoding="utf-8") as f:
        json.dump(all_actors, f, ensure_ascii=False, indent=2)

    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(filtered_edges, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    filter_links()


