"""
This script processes multiple JSON files containing objects with "name" attributes,
aggregates the counts of each unique name (excluding those starting with "StaticObj_" or "Land_"),
and writes the results to a specified CSV file.

Usage:
    python sum_items_json.py <output_csv> <json1> <json2> ...

Arguments:
    output_csv: The path to the output CSV file.
    filename1, filename2, ...: Paths to the input JSON files.

Example:
    python sum_items_json.py output.csv file1.json file2.json
"""

import json
import sys
import csv
from collections import Counter

# Check if at least one filename is provided as a command-line argument
if len(sys.argv) < 3:
    print("Usage: python sum_names.py <output_csv> <json1> <json2> ...")
    sys.exit(1)

# Output CSV file
output_csv = sys.argv[1]

# Initialize a Counter to aggregate counts
name_counts = Counter()

# Process each file provided as a command-line argument
for filename in sys.argv[2:]:
    # Open the JSON file
    with open(filename, 'r') as file:
        data = json.load(file)
        # Extract the "name" values, excluding those starting with "StaticObj_" or "Land_"
        names = [obj['name'] for obj in data['Objects'] if not (obj['name'].startswith('StaticObj_') or obj['name'].startswith('Land_'))]
        # Update the aggregate counts
        name_counts.update(names)

# Write the results to the output CSV file
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(["item", "count"])
    # Write the item counts
    for name, count in name_counts.items():
        writer.writerow([name, count])
