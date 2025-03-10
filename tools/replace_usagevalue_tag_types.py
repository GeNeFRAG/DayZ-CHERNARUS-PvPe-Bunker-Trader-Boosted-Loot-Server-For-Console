import xml.etree.ElementTree as ET
import argparse
from xml.dom import minidom

def extract_usages_and_values(src_file):
    tree = ET.parse(src_file)
    root = tree.getroot()
    usages_and_values = {}
    for type_elem in root.findall('type'):
        name = type_elem.get('name')
        usage_tags = [usage.get('name') for usage in type_elem.findall('usage')]
        value_tags = [value.get('name') for value in type_elem.findall('value')]
        usages_and_values[name] = {'usages': usage_tags, 'values': value_tags}
    return usages_and_values

def update_target_file(target_file, usages_and_values, output_file, cmd_usage_tag=None):
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(target_file, parser=parser)
    root = tree.getroot()
    not_found = []
    for type_elem in root.findall('type'):
        name = type_elem.get('name')
        if name in usages_and_values:
            # Remove existing category, usage, tag, and value tags
            for tag in type_elem.findall('category') + type_elem.findall('usage') + type_elem.findall('tag') + type_elem.findall('value'):
                type_elem.remove(tag)
            # Add usage tags from source file
            for usage_name in usages_and_values[name]['usages']:
                usage_elem = ET.Element('usage')
                usage_elem.set('name', usage_name)
                type_elem.append(usage_elem)
            # Add value tags from source file
            for value_name in usages_and_values[name]['values']:
                value_elem = ET.Element('value')
                value_elem.set('name', value_name)
                type_elem.append(value_elem)
        else:
            not_found.append(name)
        
        # Replace all usage and value tags with the usage_tag from cmd line if provided
        if cmd_usage_tag and (type_elem.findall('usage') or type_elem.findall('value') or type_elem.findall('category')):
            for tag in type_elem.findall('category') + type_elem.findall('usage') + type_elem.findall('tag') + type_elem.findall('value'):
                type_elem.remove(tag)
            usage_elem = ET.Element('usage')
            usage_elem.set('name', cmd_usage_tag)
            type_elem.append(usage_elem)
    
    # Pretty print the XML with comments and remove empty lines
    xml_str = ET.tostring(root, encoding='unicode')
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
    pretty_xml_str = "\n".join([line for line in pretty_xml_str.split('\n') if line.strip()])

    with open(output_file, 'w') as f:
        f.write(pretty_xml_str)
    
    return not_found

def main():
    parser = argparse.ArgumentParser(description='Update target XML file with usage and value tags from source XML file.')
    parser.add_argument('target_file', help='Path to the target XML file')
    parser.add_argument('output_file', help='Path to the output XML file')
    parser.add_argument('--src_file', help='Path to the source XML file', default=None)
    parser.add_argument('--usage_tag', help='Usage tag to be added to all types', default=None)
    
    args = parser.parse_args()
    
    usages_and_values = {}
    if args.src_file:
        usages_and_values = extract_usages_and_values(args.src_file)
    
    not_found = update_target_file(args.target_file, usages_and_values, args.output_file, args.usage_tag)
    
    if not_found:
        print("The following type names were not found in the source file:")
        for name in not_found:
            print(name)

if __name__ == "__main__":
    main()
