#!/usr/bin/env python3
"""
This script sorts items in a types.xml file by usage categories and adds an index.

Usage:
    python sort_types_xml.py <input_xml_file> <output_xml_file>

Arguments:
    input_xml_file: Path to the input types.xml file.
    output_xml_file: Path to the output XML file where sorted content will be saved.

Example:
    python sort_types_xml.py types.xml sorted_types.xml
"""

from lxml import etree as ET
import argparse
from collections import OrderedDict

def sort_items_alphabetically(items):
    """
    Sorts items alphabetically by their 'name' attribute.

    Args:
        items (list): List of XML elements representing items.

    Returns:
        list: Sorted list of XML elements.
    """
    return sorted(items, key=lambda x: x.get('name'))

def sort_items_by_usage(items):
    """
    Sorts items by their 'usage' attribute. Items with multiple usages are grouped into combined sections.
    Items with no usage are grouped under 'NO USAGE' category.

    Args:
        items (list): List of XML elements representing items.

    Returns:
        dict: Dictionary with usages as keys and lists of items as values.
    """
    usages = {}
    no_usage_items = []

    for item in items:
        usage_elements = item.findall('usage')
        if not usage_elements:
            no_usage_items.append(item)
            continue
            
        usage_list = [usage.get('name') for usage in usage_elements]
        if usage_list:
            usage_key = ', '.join(sorted(usage_list))
            if usage_key not in usages:
                usages[usage_key] = []
            usages[usage_key].append(item)

    # Sort items within each usage category alphabetically
    for usage_key in usages:
        usages[usage_key] = sorted(usages[usage_key], key=lambda x: x.get('name'))

    # Add the "NO USAGE" category with sorted items
    if no_usage_items:
        usages["NO USAGE"] = sorted(no_usage_items, key=lambda x: x.get('name'))

    # Return OrderedDict with sorted keys
    return OrderedDict(sorted(usages.items()))

def organize_types_xml(input_xml_file, output_xml_file):
    """
    Organizes the types.xml file by sorting items into usage categories.

    Args:
        input_xml_file (str): Path to the input types.xml file.
        output_xml_file (str): Path to the output XML file.
    """
    parser = ET.XMLParser(remove_blank_text=False)
    tree = ET.parse(input_xml_file, parser)
    root = tree.getroot()

    items = root.findall('.//type')
    sorted_items = sort_items_alphabetically(items)
    usages = sort_items_by_usage(sorted_items)

    # Clear the root and add initial newline
    root.clear()
    root.text = '\n'  # This adds the newline after <types>
    
    # Create index comment
    index_text = "INDEX OF CATEGORIES:\n"
    index_text += "==================================================\n"
    for i, usage in enumerate(sorted(usages.keys()), 1):
        index_text += f" {i:2d}. {usage.upper()}\n"
    index_text += "=================================================="
    
    index_comment = ET.Comment(index_text)
    root.append(index_comment)
    index_comment.tail = '\n\n'

    # Add categories and their items
    for usage, items in usages.items():
        comment = ET.Comment(f" ################ [{usage.upper()}] ################")
        root.append(comment)
        comment.tail = '\n'
        
        for item in items:
            root.append(item)
            item.tail = '\n'
        
        # Add extra newline between categories
        if items:
            items[-1].tail = '\n\n'

    tree.write(output_xml_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')

def main():
    parser = argparse.ArgumentParser(description='Sort types.xml by usage categories.')
    parser.add_argument('input_xml_file', help='Path to the input types.xml file')
    parser.add_argument('output_xml_file', help='Path to the output XML file')

    args = parser.parse_args()
    organize_types_xml(args.input_xml_file, args.output_xml_file)

if __name__ == "__main__":
    main()
