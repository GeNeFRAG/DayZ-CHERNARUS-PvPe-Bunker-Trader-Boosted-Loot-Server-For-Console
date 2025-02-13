"""
This script updates the nominal and minimum values in a types.xml file based on counts from a CSV file.

Usage:
    python update_nom_min_types.py <csv_file> <input_xml_file> <output_xml_file>

Arguments:
    csv_file: Path to the input CSV file containing item counts.
    input_xml_file: Path to the input types.xml file.
    output_xml_file: Path to the output XML file where updates will be saved.

Example:
    python update_nom_min_types.py counts.csv types.xml updated_types.xml
"""

import csv
from lxml import etree as ET
import argparse

def read_csv_counts(csv_file):
    """
    Reads item counts from a CSV file.

    Args:
        csv_file (str): Path to the CSV file.

    Returns:
        dict: A dictionary with item names as keys and counts as values.
    """
    counts = {}
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        if 'item' not in reader.fieldnames or 'count' not in reader.fieldnames:
            raise KeyError(f"CSV file must contain 'item' and 'count' columns. Found columns: {reader.fieldnames}")
        for row in reader:
            counts[row['item']] = int(row['count'])
    return counts

def update_types_xml(input_xml_file, output_xml_file, counts):
    """
    Updates the nominal and minimum values in the types.xml file based on the counts.

    Args:
        input_xml_file (str): Path to the input types.xml file.
        output_xml_file (str): Path to the output XML file.
        counts (dict): A dictionary with item names as keys and counts as values.
    """
    parser = ET.XMLParser(remove_blank_text=False)
    tree = ET.parse(input_xml_file, parser)
    root = tree.getroot()

    for item in root.findall('.//type'):
        name = item.get('name')
        nominal = item.find('nominal')
        min_val = item.find('min')

        if name in counts and nominal is not None and int(nominal.text) != 0:
            nominal.text = str(int(nominal.text) + counts[name])
            if min_val is not None:
                min_val.text = str(int(min_val.text) + counts[name])

    tree.write(output_xml_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update types.xml with counts from a CSV file.')
    parser.add_argument('csv_file', help='Path to the input CSV file')
    parser.add_argument('input_xml_file', help='Path to the input types.xml file')
    parser.add_argument('output_xml_file', help='Path to the output XML file')

    args = parser.parse_args()

    counts = read_csv_counts(args.csv_file)
    update_types_xml(args.input_xml_file, args.output_xml_file, counts)
