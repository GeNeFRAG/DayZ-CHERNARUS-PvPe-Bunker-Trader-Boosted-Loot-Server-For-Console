import xml.etree.ElementTree as ET
import argparse
import fnmatch

def sum_values(xml_file, pattern, field='nominal'):
    """
    Sum up the specified field values for types matching the pattern
    
    Args:
        xml_file (str): Path to types.xml
        pattern (str): Wildcard pattern to match type names
        field (str): Field to sum up ('nominal' or 'min')
    
    Returns:
        tuple: (sum of values, list of matched types)
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    total = 0
    matched_types = []
    
    for type_elem in root.findall('type'):
        type_name = type_elem.get('name')
        if fnmatch.fnmatch(type_name, pattern):
            try:
                value = int(type_elem.find(field).text)
                total += value
                matched_types.append(f"{type_name} ({value})")
            except (AttributeError, ValueError):
                print(f"Warning: Could not get {field} value for {type_name}")
                
    return total, matched_types

def main():
    parser = argparse.ArgumentParser(description='Sum up nominal or min values from types.xml')
    parser.add_argument('pattern', help='Wildcard pattern to match type names (e.g., "Mag_*")')
    parser.add_argument('--field', choices=['nominal', 'min'], default='nominal',
                      help='Field to sum up (nominal or min)')
    parser.add_argument('--xml', default='types.xml',
                      help='Path to types.xml file (default: types.xml)')
    
    args = parser.parse_args()
    
    try:
        total, matched = sum_values(args.xml, args.pattern, args.field)
        
        print(f"\nMatched types ({len(matched)}):")
        for item in matched:
            print(f"- {item}")
            
        print(f"\nTotal {args.field}: {total}")
        
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.xml}'")
    except ET.ParseError:
        print(f"Error: Could not parse XML file '{args.xml}'")

if __name__ == '__main__':
    main()
