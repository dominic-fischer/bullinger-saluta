import json
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
from tqdm import tqdm

TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}
XML_NS_ID = "{http://www.w3.org/XML/1998/namespace}id"

HEADERS = {
    "User-Agent": "Bullinger-Person-Enricher/1.0 (contact: you@example.org)"
}


def parse_wikipedia_url(url: str):
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()

    if not host.endswith("wikipedia.org"):
        return None

    lang = host.split(".")[0]

    if parsed.path.startswith("/wiki/"):
        title = parsed.path[len("/wiki/"):]
    else:
        qs = urllib.parse.parse_qs(parsed.query)
        title = qs.get("title", [None])[0]

    if not title:
        return None

    return lang, urllib.parse.unquote(title)


def fetch_wiki_summary(lang: str, title: str, session: requests.Session):
    encoded_title = urllib.parse.quote(title, safe="")
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

    try:
        r = session.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return None

        data = r.json()

        return {
            "title": data.get("title"),
            "description": data.get("description"),
            "summary": data.get("extract"),
            "thumbnail": (data.get("thumbnail") or {}).get("source"),
        }

    except requests.RequestException:
        return None


def enrich(xml_path: str, output_json: str):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    session = requests.Session()

    persons = root.findall(".//tei:person", TEI_NS)

    output = {}

    for person in tqdm(persons, desc="Fetching Wikipedia summaries", unit="person"):
        pid = person.get(XML_NS_ID)
        if not pid:
            continue

        gnd = None
        wiki = None

        for idno in person.findall("./tei:idno", TEI_NS):
            subtype = idno.get("subtype")
            val = (idno.text or "").strip() or None
            if subtype == "gnd":
                gnd = val
            elif subtype == "wiki":
                wiki = val

        record = {"gnd": gnd, "wiki": wiki}

        if wiki:
            parsed = parse_wikipedia_url(wiki)

            # show current person in progress bar
            tqdm.write(f"{pid} → {parsed[1] if parsed else 'invalid wiki url'}")

            if parsed:
                lang, title = parsed
                record["wiki_summary"] = fetch_wiki_summary(lang, title, session)
                time.sleep(0.25)  # politeness delay
            else:
                record["wiki_summary"] = None

        output[pid] = record

    Path(output_json).write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\nSaved {len(output)} persons to {output_json}")


if __name__ == "__main__":
    enrich("persons.xml", "person_gnd_wiki.json")