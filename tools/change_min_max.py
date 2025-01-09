#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import argparse
import fnmatch
import sys
from pathlib import Path
import re

# Extend ElementTree to preserve comments
class CommentedTreeBuilder(ET.TreeBuilder):
    def comment(self, data):
        self.start(ET.Comment, {})
        self.data(data)
        self.end(ET.Comment)

def read_xml_with_comments(filename):
    """Read XML file preserving comments"""
    parser = ET.XMLParser(target=CommentedTreeBuilder())
    return ET.parse(filename, parser)

def write_xml_with_comments(tree, filename):
    """Write XML file preserving comments and formatting"""
    # Convert tree to string
    xml_str = ET.tostring(tree.getroot(), encoding='unicode')
    
    # Preserve XML declaration
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
    
    # Fix comment formatting
    xml_str = re.sub(r'<Comment>', '<!--', xml_str)
    xml_str = re.sub(r'</Comment>', '-->', xml_str)
    
    # Write to file
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(xml_str)

def update_quantities(xml_file, pattern, quantmin, quantmax, dry_run=False):
    """
    Update quantmin and quantmax values for types matching the pattern,
    except where values are -1
    
    Args:
        xml_file (str): Path to types.xml
        pattern (str): Wildcard pattern to match type names
        quantmin (int): New quantmin value
        quantmax (int): New quantmax value
        dry_run (bool): If True, only show what would be changed
    
    Returns:
        list: Modified type names and their old/new values
    """
    tree = read_xml_with_comments(xml_file)
    root = tree.getroot()
    
    changes = []
    skipped = []
    
    for type_elem in root.findall('type'):
        type_name = type_elem.get('name')
        if fnmatch.fnmatch(type_name, pattern):
            min_elem = type_elem.find('quantmin')
            max_elem = type_elem.find('quantmax')
            old_min = min_elem.text
            old_max = max_elem.text
            
            # Skip if either value is -1
            if old_min == '-1' or old_max == '-1':
                skipped.append({
                    'name': type_name,
                    'min': old_min,
                    'max': old_max
                })
                continue
                
            if not dry_run:
                min_elem.text = str(quantmin)
                max_elem.text = str(quantmax)
            
            changes.append({
                'name': type_name,
                'old_min': old_min,
                'old_max': old_max,
                'new_min': quantmin,
                'new_max': quantmax
            })
    
    if not dry_run and changes:
        # Create backup of original file
        backup_file = f"{xml_file}.backup"
        Path(xml_file).rename(backup_file)
        
        # Write updated XML with comments
        write_xml_with_comments(tree, xml_file)
        
    return changes, skipped

def main():
    parser = argparse.ArgumentParser(
        description='Update quantmin and quantmax values in types.xml (except where -1)'
    )
    parser.add_argument('pattern', 
        help='Wildcard pattern to match type names (e.g., "Ammo*")'
    )
    parser.add_argument('quantmin', type=int,
        help='New quantmin value'
    )
    parser.add_argument('quantmax', type=int,
        help='New quantmax value'
    )
    parser.add_argument('--xml', default='types.xml',
        help='Path to types.xml file (default: types.xml)'
    )
    parser.add_argument('--dry-run', action='store_true',
        help='Show what would be changed without making changes'
    )
    
    args = parser.parse_args()
    
    # Validate input values
    if args.quantmin > args.quantmax:
        print("Error: quantmin cannot be greater than quantmax")
        sys.exit(1)
        
    try:
        changes, skipped = update_quantities(
            args.xml, 
            args.pattern, 
            args.quantmin, 
            args.quantmax, 
            args.dry_run
        )
        
        if not changes and not skipped:
            print(f"\nNo types found matching pattern: {args.pattern}")
            return
            
        if changes:
            print(f"\nTypes to be updated ({len(changes)}):")
            for change in changes:
                print(f"\n- {change['name']}:")
                print(f"  quantmin: {change['old_min']} → {change['new_min']}")
                print(f"  quantmax: {change['old_max']} → {change['new_max']}")
        
        if skipped:
            print(f"\nSkipped types with -1 values ({len(skipped)}):")
            for skip in skipped:
                print(f"\n- {skip['name']}:")
                print(f"  quantmin: {skip['min']}")
                print(f"  quantmax: {skip['max']}")
            
        if args.dry_run:
            print("\nDRY RUN - No changes were made")
        elif changes:
            print(f"\nUpdated {len(changes)} types")
            print(f"Skipped {len(skipped)} types")
            print(f"Backup saved as: {args.xml}.backup")
            
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.xml}'")
    except ET.ParseError:
        print(f"Error: Could not parse XML file '{args.xml}'")
    except AttributeError as e:
        print(f"Error: Some types are missing quantmin or quantmax elements")
        
if __name__ == '__main__':
    main()