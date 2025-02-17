import xml.etree.ElementTree as ET
import argparse
from xml.dom import minidom

def extract_usages(src_file):
    tree = ET.parse(src_file)
    root = tree.getroot()
    usages = {}
    for type_elem in root.findall('type'):
        name = type_elem.get('name')
        usage_tags = type_elem.findall('usage')
        usages[name] = [usage.get('name') for usage in usage_tags]
    return usages

def update_target_file(target_file, usages, output_file):
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(target_file, parser=parser)
    root = tree.getroot()
    not_found = []
    for type_elem in root.findall('type'):
        name = type_elem.get('name')
        if name in usages:
            # Remove existing category, usage, tag, and value tags
            for tag in type_elem.findall('category') + type_elem.findall('usage') + type_elem.findall('tag') + type_elem.findall('value'):
                type_elem.remove(tag)
            # Add usage tags from source file
            for usage_name in usages[name]:
                usage_elem = ET.Element('usage')
                usage_elem.set('name', usage_name)
                type_elem.append(usage_elem)
        else:
            not_found.append(name)
    
    # Pretty print the XML with comments and remove empty lines
    xml_str = ET.tostring(root, encoding='unicode')
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
    pretty_xml_str = "\n".join([line for line in pretty_xml_str.split('\n') if line.strip()])

    with open(output_file, 'w') as f:
        f.write(pretty_xml_str)
    
    return not_found

def main():
    parser = argparse.ArgumentParser(description='Update target XML file with usage tags from source XML file.')
    parser.add_argument('src_file', help='Path to the source XML file')
    parser.add_argument('target_file', help='Path to the target XML file')
    parser.add_argument('output_file', help='Path to the output XML file')
    
    args = parser.parse_args()
    
    usages = extract_usages(args.src_file)
    not_found = update_target_file(args.target_file, usages, args.output_file)
    
    if not_found:
        print("The following type names were not found in the source file:")
        for name in not_found:
            print(name)

if __name__ == "__main__":
    main()
