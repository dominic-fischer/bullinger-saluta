
import xml.etree.ElementTree as ET

# Namespace
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}
XMLID = '{http://www.w3.org/XML/1998/namespace}id'

# --- Load person index --- #
def load_person_lookup(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    lookup = {}

    for pers_name in root.findall('.//tei:persName', NS):
        pers_id = pers_name.attrib.get(XMLID)
        if not pers_id:
            continue

        forename = pers_name.find('tei:forename', NS)
        surname = pers_name.find('tei:surname', NS)

        forename_text = forename.text.strip() if forename is not None and forename.text else ""
        surname_text = surname.text.strip() if surname is not None and surname.text else ""
        full_name = (forename_text + " " + surname_text).strip()

        if full_name:
            lookup[pers_id] = full_name

    return lookup

# --- Load place index --- #
def load_place_lookup(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    name_lookup = {}
    coord_lookup = {}

    for place in root.findall('.//tei:place', NS):
        place_id = place.attrib.get(XMLID)

        settlement = place.find('tei:settlement', NS)
        district = place.find('tei:district', NS)
        country = place.find('tei:country', NS)

        name = None
        for candidate in [settlement, district, country]:
            if candidate is not None and candidate.text:
                name = candidate.text.strip()
                break

        geo = place.find('tei:location/tei:geo', NS)
        coords = geo.text.strip() if geo is not None and geo.text else None

        if place_id and name:
            name_lookup[place_id] = name
            if coords:
                coord_lookup[place_id] = coords

    return name_lookup, coord_lookup



import json
if __name__ == "__main__":
    # Load data
    person_lookup = load_person_lookup("/Users/Dominic-Asus/bullinger-korpus-tei/data/index/persons.xml")
    place_lookup, coord_lookup = load_place_lookup("/Users/Dominic-Asus/bullinger-korpus-tei/data/index/localities.xml")

    # --- Save person lookup to JSON --- #
    with open("person_lookup.json", "w", encoding="utf-8") as f:
        json.dump(person_lookup, f, ensure_ascii=False, indent=2)

    # --- Save place lookup to JSON --- #
    with open("place_name_lookup.json", "w", encoding="utf-8") as f:
        json.dump(place_lookup, f, ensure_ascii=False, indent=2)

    with open("place_coord_lookup.json", "w", encoding="utf-8") as f:
        json.dump(coord_lookup, f, ensure_ascii=False, indent=2)