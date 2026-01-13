
import sys
sys.stdout.reconfigure(encoding="utf-8")
import re
import json
from collections import defaultdict

with open("German_Files/DE_visualization_input_file.txt", "r", encoding="utf-8") as f:
    de_lines = f.readlines()
    de_lines = [l.split("\t") for l in de_lines]

with open("Latin_Files/LA_visualization_input_file.txt", "r", encoding="utf-8") as f:
    la_lines = f.readlines()
    la_lines = [l.split("\t") for l in la_lines]


lines = de_lines + la_lines

vis_data = {}


for l in lines:
    assert len(l) == 6, "something went wrong splitting the line by tabs"
    _, sender_raw, recipient_raw, year, _, letter_text = l

    senders = sender_raw.strip().split(",")
    recipients = recipient_raw.strip().split(",")

    pattern = r'<persName\b[^>]*\bsent="[^"]+"[^>]*>.*?</persName>'
    matches = re.findall(pattern, letter_text, re.DOTALL)

    for sender in senders:
        for recipient in recipients:
            # we only count actual greetings, not letters sent
            for match in matches:
                ref_match = re.search(r'\bref="([^"]+)"', match)
                ref_match = ref_match.group(1) if ref_match is not None else ""
                if ref_match == "":
                    continue

                if 'sent="to"' in match:
                    key = (sender, ref_match)
                elif 'sent="from"' in match:
                    key = (ref_match, recipient)
                
                if key in vis_data:
                    vis_data[key][year] = vis_data[key].get(year, 0) + 1
                else:
                    vis_data[key] = {year: 1}

    


total_count = sum(
    count for pair in vis_data.values()
    for count in pair.values()
)

print(total_count)
print(len(vis_data.keys()))





# normalize keys (sorted tuple) and merge year counts
merged = defaultdict(lambda: defaultdict(int))

for (a, b), years in vis_data.items():
    key = tuple(sorted([a, b]))
    for year, count in years.items():
        merged[key][year] += count

# convert nested defaultdicts to normal dicts
final_dict = {k: dict(v) for k, v in merged.items()}


total_count_final = sum(
    count for pair in final_dict.values()
    for count in pair.values()
)

print(total_count_final)
print(len(final_dict.keys()))



# convert tuple keys to strings (since JSON keys must be strings)
json_ready = {f"{k[0]}|{k[1]}": v for k, v in final_dict.items()}

# save to file
with open('all_links.json', 'w', encoding='utf-8') as f:
    json.dump(json_ready, f, indent=2, ensure_ascii=False)
