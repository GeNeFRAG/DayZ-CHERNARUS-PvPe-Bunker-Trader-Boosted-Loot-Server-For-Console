import xml.etree.ElementTree as ET
import sys
import os

def get_valid_usages(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        valid_usages = {usage.get('name') for usage in root.findall('.//usage')}
        return valid_usages
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {xml_file}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def check_invalid_usages_proto(xml_file, valid_usages):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Track if any invalid usages were found
        found_invalid = False
        
        # Check all groups
        for group in root.findall('.//group'):
            group_name = group.get('name', 'Unknown Group')
            
            # Check each usage tag within the group
            for usage in group.findall('.//usage'):
                usage_name = usage.get('name')
                if usage_name not in valid_usages:
                    found_invalid = True
                    print(f"Invalid usage '{usage_name}' found in group '{group_name}'")
        
        if not found_invalid:
            print("No invalid usage tags found.")
            
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
    except FileNotFoundError:
        print(f"File not found: {xml_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def check_invalid_usages_types(xml_file, valid_usages):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        undefined_usages = set()

        for type_elem in root.findall('type'):
            for usage_elem in type_elem.findall('usage'):
                usage_name = usage_elem.get('name')
                if usage_name not in valid_usages:
                    undefined_usages.add(usage_name)

        if undefined_usages:
            print("The following usages are not defined:")
            for usage in undefined_usages:
                print(usage)
        else:
            print("No invalid usage tags found.")
            
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
    except FileNotFoundError:
        print(f"File not found: {xml_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python check_usage_tags.py <cfglimitsdefinition.xml> <xml_file>")
        sys.exit(1)

    cfglimits_file = sys.argv[1]
    xml_file = sys.argv[2]
    
    valid_usages = get_valid_usages(cfglimits_file)
    
    if 'mapgroupproto' in xml_file:
        check_invalid_usages_proto(xml_file, valid_usages)
    elif 'types' in xml_file:
        check_invalid_usages_types(xml_file, valid_usages)
    else:
        print("Unsupported XML file type. Please provide either a mapgroupproto.xml or types.xml file.")
        sys.exit(1)

if __name__ == "__main__":
    main()
