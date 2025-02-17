import xml.etree.ElementTree as ET
import sys
from collections import defaultdict

def print_tier_items(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    tier_items = defaultdict(list)
    unique_items = []

    for type_elem in root.findall('type'):
        type_name = type_elem.get('name')
        tier_values = [value_elem.get('name') for value_elem in type_elem.findall('value')]
        usage_values = [value_elem.get('name') for value_elem in type_elem.findall('usage')]

        if 'ContaminatedArea' in usage_values:
            tier_values.append('ContaminatedArea')

        if not tier_values:
            continue  # Skip items that don't have a tier

        if 'Unique' in tier_values:
            unique_items.append(type_name)

        tier_key = tuple(sorted(tier_values))
        tier_items[tier_key].append(type_name)

    for tier_key, items in tier_items.items():
        tier_key_str = ', '.join(tier_key)
        print(f"{tier_key_str}:")
        for item in items:
            print(item)
        print()

def main():
    if len(sys.argv) != 2:
        print("Usage: python print_tier_items.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    print_tier_items(file_path)

if __name__ == "__main__":
    main()
