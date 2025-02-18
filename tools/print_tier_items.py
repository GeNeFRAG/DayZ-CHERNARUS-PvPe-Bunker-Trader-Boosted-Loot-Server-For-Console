import xml.etree.ElementTree as ET
import sys
import argparse
import csv
from collections import defaultdict

def print_tier_items(file_path, by_tier, by_usage, output_file):
    tree = ET.parse(file_path)
    root = tree.getroot()

    tier_items = defaultdict(list)
    usage_items = defaultdict(list)
    no_tier_with_usage_items = []
    no_usage_items = []

    # Special usage tags that should be treated as tiers
    special_usage_tags = {"ContaminatedArea", "Special", "Unique"}
    # Usage tags that should appear in both tier and usage output
    dual_usage_tags = {"Special"}

    for type_elem in root.findall('type'):
        type_name = type_elem.get('name')
        tier_values = [value_elem.get('name') for value_elem in type_elem.findall('value')]
        usage_values = [value_elem.get('name') for value_elem in type_elem.findall('usage')]
        
        # Add special usage tags to tier_values
        special_tiers = [usage for usage in usage_values if usage in special_usage_tags]
        combined_tier_values = tier_values + special_tiers

        # Handle tier categorization
        if not combined_tier_values and usage_values:  # No tier tags (including special usage tags) but has other usage tags
            no_tier_with_usage_items.append(type_name)
        elif combined_tier_values:  # Has tier tags or special usage tags
            tier_key = tuple(sorted(combined_tier_values))
            tier_items[tier_key].append(type_name)

        # Handle usage categorization
        # Include regular usage tags and dual_usage_tags
        relevant_usage_values = [usage for usage in usage_values 
                               if usage not in special_usage_tags or usage in dual_usage_tags]
        if not relevant_usage_values:
            no_usage_items.append(type_name)
        else:
            for usage in relevant_usage_values:
                usage_items[usage].append(type_name)

    # Sort all lists alphabetically
    no_tier_with_usage_items.sort()
    no_usage_items.sort()
    for key in tier_items:
        tier_items[key].sort()
    for key in usage_items:
        usage_items[key].sort()

    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        if by_tier:
            csvwriter.writerow(["Items categorized by tier:"])
            max_items = max(
                max((len(items) for items in tier_items.values()), default=0),
                len(no_tier_with_usage_items)
            )
            tier_keys = sorted(tier_items.keys(), key=lambda x: ', '.join(x))
            tier_keys_str = [', '.join(tier_key) for tier_key in tier_keys] + ["NoTier"]
            csvwriter.writerow(tier_keys_str)
            for i in range(max_items):
                row = []
                for tier_key in tier_keys:
                    if i < len(tier_items[tier_key]):
                        row.append(tier_items[tier_key][i])
                    else:
                        row.append("")
                if i < len(no_tier_with_usage_items):
                    row.append(no_tier_with_usage_items[i])
                else:
                    row.append("")
                csvwriter.writerow(row)

        if by_usage:
            max_items = max(
                max((len(items) for items in usage_items.values()), default=0),
                len(no_usage_items)
            )
            usage_keys = sorted(usage_items.keys()) + ["NoUsage"]
            csvwriter.writerow(usage_keys)
            for i in range(max_items):
                row = []
                for usage in usage_keys[:-1]:  # Exclude "NoUsage" from the loop
                    if i < len(usage_items[usage]):
                        row.append(usage_items[usage][i])
                    else:
                        row.append("")
                if i < len(no_usage_items):
                    row.append(no_usage_items[i])
                else:
                    row.append("")
                csvwriter.writerow(row)

    print(f"Results have been written to {output_file}")

def main():
    """
    Main function to parse arguments and print tier and usage categorized items.
    """
    parser = argparse.ArgumentParser(description='Print items categorized by tier and usage tags from an XML file.')
    parser.add_argument('file_path', help='Path to the XML file.')
    parser.add_argument('output_file', help='Path to the output CSV file.')
    parser.add_argument('--by_tier', action='store_true', help='Print items categorized by tier.')
    parser.add_argument('--by_usage', action='store_true', help='Print items categorized by usage.')
    
    args = parser.parse_args()

    print_tier_items(args.file_path, args.by_tier, args.by_usage, args.output_file)

if __name__ == "__main__":
    main()
