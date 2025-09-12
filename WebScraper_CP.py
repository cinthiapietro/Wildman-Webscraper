import requests
import csv
import time
from config import load_config

# Base URL and headers
cfg = load_config()

url = cfg.get("URL")
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer":  url,
    "User-Agent": cfg.get("USER_AGENT", "Mozilla/5.0"),
}
cookies = {
    "PHPSESSID": cfg.get("PHPSESSID", ""),
    "WildManUserid": cfg.get("WildManUserid", ""),
    "WildManPassword": cfg.get("WildManPassword", ""),
    "WildManRemember": cfg.get("WildManRemember", "Y"),
}

# Create session
session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies)

# Base body
base_body = {
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
    "selectAll": "Y"
}

# Input CSV file
csv_filename = "numbers.csv"

# Output file
output_filename = "Consolidated_WildManExport.xml"

# Start consolidated XML
with open(output_filename, "w", encoding="utf-8") as file:
    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write("<ConsolidatedData>\n")  # Root element for combined XML

# Read numbers from CSV
with open(csv_filename, "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    numbers = [row[0] for row in reader if row]  # Assuming numbers are in the first column

# Iterate through numbers
for num in numbers:
    body = base_body.copy()
    body[f"select{num}"] = "Y"

    success = False
    while not success:
        try:
            # Send POST request
            response = requests.post(url, headers=headers, data=body, timeout=30)  # 30 seconds timeout
            if response.status_code == 200:
                print(f"Processing select{num}...")
                with open(output_filename, "a", encoding="utf-8") as file:
                    # Append data, stripping the XML declaration if present
                    data = response.text.strip()
                    if data.startswith('<?xml'):
                        data = data[data.index('?>') + 2:].strip()
                    file.write(f"\n<!-- Data for select{num} -->\n")
                    file.write(data)
                success = True  # Exit loop on success
            else:
                print(f"Request for select{num} failed with status code {response.status_code}. Retrying...")
                time.sleep(60)  # Wait 1 minute before retrying
        except requests.exceptions.RequestException as e:
            print(f"Request for select{num} encountered an error: {e}. Retrying in 1 minute...")
            time.sleep(60)  # Wait 1 minute before retrying

# Close consolidated XML
with open(output_filename, "a", encoding="utf-8") as file:
    file.write("\n</ConsolidatedData>\n")

print(f"All responses consolidated into {output_filename}")
