import xml.etree.ElementTree as ET
import json
import os
import argparse
import fnmatch

def parse_xml(file_path, category_filter=None, type_name_filter=None):
    tree = ET.parse(file_path)
    root = tree.getroot()
    types = {}
    for type_elem in root.findall('type'):
        name = type_elem.get('name')
        if category_filter:
            category_elem = type_elem.find('category')
            if category_elem is None or category_elem.get('name') != category_filter:
                continue
        if type_name_filter and not fnmatch.fnmatch(name, type_name_filter):
            continue
        types[name] = type_elem
    return types

def compare_xml_types(file1, file2, output_file, category_filter=None, type_name_filter=None):
    types1 = parse_xml(file1, category_filter, type_name_filter)
    types2 = parse_xml(file2, category_filter, type_name_filter)
    
    all_keys = set(types1.keys()).union(set(types2.keys()))
    differences = []

    file1_name = os.path.basename(file1)
    file2_name = os.path.basename(file2)

    for key in all_keys:
        type_diff = {}
        if key not in types1:
            type_diff[key] = f"only in {file2_name}"
        elif key not in types2:
            type_diff[key] = f"only in {file1_name}"
        else:
            elem1 = types1[key]
            elem2 = types2[key]
            for child in elem1:
                child_name = child.tag
                value1 = child.text
                value2 = elem2.find(child_name).text if elem2.find(child_name) is not None else None
                if value1 != value2:
                    if key not in type_diff:
                        type_diff[key] = {}
                    type_diff[key][child_name] = {file1_name: value1, file2_name: value2}
        if type_diff:
            differences.append(type_diff)

    with open(output_file, 'w') as f:
        json.dump(differences, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare XML types.')
    parser.add_argument('file1', help='First XML file')
    parser.add_argument('file2', help='Second XML file')
    parser.add_argument('output_file', help='Output JSON file')
    parser.add_argument('--category', help='Filter by category', default=None)
    parser.add_argument('--typename', help='Filter by type name (supports wildcards)', default=None)
    args = parser.parse_args()

    compare_xml_types(args.file1, args.file2, args.output_file, args.category, args.typename)
