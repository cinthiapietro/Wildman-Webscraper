import requests
import csv
import time
import xml.etree.ElementTree as ET
from typing import Dict, List

# -----------------------------
# Config
# -----------------------------
def load_config(path="config.txt") -> dict:
    cfg = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg

config = load_config("config.txt")

URL = config.get("URL", "https://batsqld.org.au/WildMan/AnimalExportMultipleForm.php")
USER_AGENT = config.get(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
OUTPUT_CSV = config.get("OUTPUT_CSV", "NQWC_data_test.csv")
INPUT_IDS_CSV = config.get("INPUT_IDS_CSV", "numbers.csv")

cookie_parts = []
for key in ["PHPSESSID", "WildManUserid", "WildManPassword", "WildManRemember"]:
    if key in config and config[key]:
        cookie_parts.append(f"{key}={config[key]}")
COOKIE = "; ".join(cookie_parts)

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": URL,
    "User-Agent": USER_AGENT,
    "Cookie": COOKIE,
}

# -----------------------------
# Helpers
# -----------------------------
def txt(node):
    return (node.text or "").strip() if node is not None else ""

def find_text(parent, path: str) -> str:
    return txt(parent.find(path))

def find_all_text(parent, path: str) -> List[str]:
    return [txt(n) for n in parent.findall(path) if txt(n) != ""]

def join(vals: List[str], sep=";"):
    return sep.join([v for v in vals if v])

# -----------------------------
# XML → single row per <Animal>
# -----------------------------
def animal_to_row(animal) -> Dict[str, str]:
    row: Dict[str, str] = {
        "Animal_Number":          find_text(animal, "Animal_Number"),
        "Animal_Scientific_Name": find_text(animal, "Animal_Scientific_Name"),
        "Animal_Birth_Date":      find_text(animal, "Animal_Birth_Date"),
        "Animal_Sex":             find_text(animal, "Animal_Sex"),
        "Animal_Status":          find_text(animal, "Animal_Status"),
        "Animal_Growth_Stage":    find_text(animal, "Animal_Growth_Stage"),
        "Animal_Vet_Number":      find_text(animal, "Animal_Vet_Number"),
        "Animal_Care_Group":      find_text(animal, "Animal_Care_Group"),
        "Animal_Place_Of_Origin": find_text(animal, "Animal_Place_Of_Origin"),
        "Animal_Care_Reason":     find_text(animal, "Animal_Care_Reason"),
        "Animal_Arrival_Notes":   find_text(animal, "Animal_Arrival_Notes"),
    }

    row["Measure_Date"] = join(find_all_text(animal, ".//Record_Date"))
    row["Weight"]       = join(find_all_text(animal, ".//Weight"))
    row["Arm_Length"]   = join(find_all_text(animal, ".//Arm_Length"))

    return row

def parse_response_xml(xml_text: str) -> List[Dict[str, str]]:
    xml_text = xml_text.strip()
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        root = ET.fromstring(f"<Root>{xml_text}</Root>")

    animals_blocks = [root] if root.tag == "Animals" else root.findall(".//Animals")
    rows: List[Dict[str, str]] = []
    for blk in animals_blocks:
        for animal in blk.findall("Animal"):
            rows.append(animal_to_row(animal))
    return rows

# -----------------------------
# Request body template
# -----------------------------
BASE_BODY = {
    "Action": "Export",
    "ID": "",
    "Mode": "",
    "page": "",
    "SortCol": "ID",
    "SortDxn": "DESC",
    "SortOrder": "ID",
    "scrollX": "",
    "scrollY": "",
    "FilterGroup": "All",
    "FilterCarer": "All",
    "FilterSpeciesType": "Flying Foxes",
    "FilterSpecies": "All",
    "FilterStatus": "All",
    "selectAll": "Y",
}

# -----------------------------
# Main
# -----------------------------
def main():

    with open(INPUT_IDS_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        ids = [row[0].strip() for row in reader if row and row[0].strip()]

    all_rows: List[Dict[str, str]] = []

    for num in ids:
        body = dict(BASE_BODY)
        body[f"select{num}"] = "Y"

        while True:
            try:
                resp = requests.post(URL, headers=HEADERS, data=body, timeout=30)
                if resp.status_code == 200:
                    print(f"Processing select{num}…")
                    all_rows.extend(parse_response_xml(resp.text))
                    break
                else:
                    print(f"HTTP {resp.status_code} for select{num}. Retrying in 60s…")
                    time.sleep(60)
            except requests.exceptions.RequestException as e:
                print(f"Error for select{num}: {e}. Retrying in 60s…")
                time.sleep(60)

    if not all_rows:
        print("No rows parsed; nothing to write.")
        return

    fieldnames = [
        "Animal_Number",
        "Animal_Scientific_Name",
        "Animal_Birth_Date",
        "Animal_Sex",
        "Animal_Status",
        "Animal_Growth_Stage",
        "Animal_Vet_Number",
        "Animal_Care_Group",
        "Animal_Place_Of_Origin",
        "Animal_Care_Reason",
        "Animal_Arrival_Notes",
        "Measure_Date",
        "Weight",
        "Arm_Length",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"Wrote {len(all_rows)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
