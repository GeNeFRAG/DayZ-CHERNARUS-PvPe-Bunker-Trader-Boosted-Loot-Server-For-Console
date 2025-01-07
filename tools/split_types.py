import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Split types.xml into smaller files based on categories.')
parser.add_argument('--types_file', required=True, help='Path to the types.xml file')
parser.add_argument('--economy_core_file', required=True, help='Path to the cfgeconomycore.xml file')
args = parser.parse_args()

# Define the input file and output directory
input_file = args.types_file
db_dir = os.path.basename(os.path.dirname(input_file))
output_dir = os.path.join(os.path.dirname(input_file), 'split_types')
economy_core_file = args.economy_core_file

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Read the input file
with open(input_file, 'r') as file:
    lines = file.readlines()

# Initialize variables
current_category = None
category_files = {}

# Process each line
for line in lines:
    # Check for category comment
    match = re.match(r'^\s*<!--\s*####################\s*(.+?)\s*####################\s*-->', line)
    if match:
        current_category = re.sub(r'\W+', '', match.group(1).lower())
        category_files[current_category] = ['<?xml version="1.0" encoding="UTF-8"?>\n', '<types>\n']
        print(f"Matched category: {current_category}")
    if current_category:
        category_files[current_category].append(line)

# Write each category to a separate file
for category, content in category_files.items():
    content.append('</types>\n')
    output_file = os.path.join(output_dir, f'{category}_types.xml')
    with open(output_file, 'w') as file:
        file.writelines(content)

# Load and modify the cfgeconomycore.xml file
parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
tree = ET.parse(economy_core_file, parser=parser)
root = tree.getroot()

# Find or create the <ce> element
ce_element = root.find('ce')
if ce_element is None:
    ce_element = ET.SubElement(root, 'ce', folder=os.path.join(db_dir, 'split_types'))

# Add new files to the <ce> element
for category in category_files.keys():
    file_element = ET.SubElement(ce_element, 'file', name=f'{category}_types.xml', type='types')

# Format the XML for readability without extra new lines
xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])

# Save the modified cfgeconomycore.xml file
with open(economy_core_file, 'w') as file:
    file.write(xml_str)
