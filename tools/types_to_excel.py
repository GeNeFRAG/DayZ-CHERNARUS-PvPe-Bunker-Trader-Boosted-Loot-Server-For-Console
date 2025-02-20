#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict
import copy
import re
import argparse
import sys
import os
import openpyxl

def xml_to_excel(xml_file, excel_file):
    try:
        # Parse the actual XML
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Define flag columns
        flag_columns = [
            'count_in_cargo',
            'count_in_hoarder',
            'count_in_map',
            'count_in_player',
            'crafted',
            'deloot'
        ]
        
        # Define numeric fields
        numeric_fields = ['nominal', 'lifetime', 'restock', 'min', 'quantmin', 'quantmax', 'cost']
        
        # Collect all possible usage and tier values first
        usage_values = set()
        tier_values = set()
        for type_elem in root.findall('type'):
            for usage in type_elem.findall('usage'):
                usage_values.add(usage.get('name', ''))
            for value in type_elem.findall('value'):
                tier_values.add(value.get('name', ''))
        
        # Sort the sets for consistent column ordering
        usage_columns = sorted(usage_values)
        tier_columns = sorted(tier_values)
        
        # Prepare data for DataFrame
        data = []
        for type_elem in root.findall('type'):
            # Initialize item with name attribute
            item = {
                'name': type_elem.get('name', ''),
            }
            
            # Get numeric values from child elements
            for field in numeric_fields:
                field_elem = type_elem.find(field)
                # Convert to integer if possible, otherwise leave as empty string
                if field_elem is not None and field_elem.text:
                    try:
                        item[field] = int(field_elem.text)
                    except ValueError:
                        item[field] = field_elem.text
                else:
                    item[field] = ''
            
            # Handle flags attributes as separate columns
            flags_elem = type_elem.find('flags')
            if flags_elem is not None:
                for flag in flag_columns:
                    try:
                        item[flag] = int(flags_elem.get(flag, '0'))
                    except ValueError:
                        item[flag] = flags_elem.get(flag, '')
            else:
                for flag in flag_columns:
                    item[flag] = ''
            
            # Handle category
            category_elem = type_elem.find('category')
            item['category'] = category_elem.get('name', '') if category_elem is not None else ''
            
            # Handle usage tags as separate columns
            current_usage = {u.get('name', '') for u in type_elem.findall('usage')}
            for usage in usage_columns:
                item[f'usage_{usage}'] = 'X' if usage in current_usage else ''
            
            # Handle tier values as separate columns
            current_tiers = {v.get('name', '') for v in type_elem.findall('value')}
            for tier in tier_columns:
                item[f'tier_{tier}'] = 'X' if tier in current_tiers else ''
            
            data.append(item)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Convert empty strings to NaN for numeric columns
        numeric_columns = numeric_fields + flag_columns
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Save to Excel with appropriate formatting
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            
            # Format columns appropriately
            for idx, column in enumerate(df.columns, 1):
                letter = openpyxl.utils.get_column_letter(idx)
                if column in numeric_columns:
                    # Format numeric columns as numbers
                    for cell in worksheet[letter][1:]:  # Skip header row
                        if cell.value is not None:
                            cell.number_format = '0'
                else:
                    # Format other columns as text
                    for cell in worksheet[letter][1:]:  # Skip header row
                        cell.number_format = '@'
        
        print(f"Successfully exported to {excel_file}")
        return True
    except Exception as e:
        print(f"Error during XML to Excel conversion: {str(e)}", file=sys.stderr)
        return False

def excel_to_xml(excel_file, output_xml_file):
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file)
        
        # Create new XML structure
        new_root = ET.Element('types')
        
        # Define flag columns
        flag_columns = [
            'count_in_cargo',
            'count_in_hoarder',
            'count_in_map',
            'count_in_player',
            'crafted',
            'deloot'
        ]
        
        # Define numeric fields
        numeric_fields = ['nominal', 'lifetime', 'restock', 'min', 'quantmin', 'quantmax', 'cost']
        
        # Get usage and tier columns
        usage_columns = [col for col in df.columns if col.startswith('usage_')]
        tier_columns = [col for col in df.columns if col.startswith('tier_')]
        
        # Process each row in the DataFrame
        for _, row in df.iterrows():
            type_elem = ET.SubElement(new_root, 'type')
            
            # Set name attribute
            if pd.notna(row['name']) and str(row['name']).strip():
                type_elem.set('name', str(row['name']).strip())
            
            # Handle numeric fields as child elements
            for field in numeric_fields:
                if pd.notna(row[field]) and str(row[field]).strip():
                    field_elem = ET.SubElement(type_elem, field)
                    field_elem.text = str(int(float(row[field])))
            
            # Handle flags
            flags_present = False
            flags_attrs = {}
            for flag in flag_columns:
                if pd.notna(row[flag]):
                    flags_present = True
                    flags_attrs[flag] = str(int(float(row[flag])))
            
            if flags_present:
                flags_elem = ET.SubElement(type_elem, 'flags')
                for flag, value in flags_attrs.items():
                    flags_elem.set(flag, value)
            
            # Handle category
            if pd.notna(row['category']) and str(row['category']).strip():
                category_elem = ET.SubElement(type_elem, 'category')
                category_elem.set('name', str(row['category']).strip())
            
            # Handle usage tags
            for usage_col in usage_columns:
                if pd.notna(row[usage_col]) and row[usage_col] == 'X':
                    usage_name = usage_col.replace('usage_', '')
                    usage_elem = ET.SubElement(type_elem, 'usage')
                    usage_elem.set('name', usage_name)
            
            # Handle tier values
            for tier_col in tier_columns:
                if pd.notna(row[tier_col]) and row[tier_col] == 'X':
                    tier_name = tier_col.replace('tier_', '')
                    value_elem = ET.SubElement(type_elem, 'value')
                    value_elem.set('name', tier_name)
        
        # Custom XML formatting function
        def format_xml(elem, level=0):
            indent = "    "  # 4 spaces for indentation
            pieces = []
            pieces.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
            pieces.append('<types>\n')
            
            for type_elem in elem:
                pieces.append(f'{indent * (level + 1)}<type name="{type_elem.get("name")}">\n')
                
                # Add numeric fields
                for field in numeric_fields:
                    field_elem = type_elem.find(field)
                    if field_elem is not None:
                        pieces.append(f'{indent * (level + 2)}<{field}>{field_elem.text}</{field}>\n')
                
                # Add flags
                flags_elem = type_elem.find('flags')
                if flags_elem is not None:
                    flags_attrs = ' '.join(f'{k}="{v}"' for k, v in flags_elem.attrib.items())
                    pieces.append(f'{indent * (level + 2)}<flags {flags_attrs} />\n')
                
                # Add category
                category_elem = type_elem.find('category')
                if category_elem is not None:
                    pieces.append(f'{indent * (level + 2)}<category name="{category_elem.get("name")}" />\n')
                
                # Add usage tags
                for usage in type_elem.findall('usage'):
                    pieces.append(f'{indent * (level + 2)}<usage name="{usage.get("name")}" />\n')
                
                # Add value tags
                for value in type_elem.findall('value'):
                    pieces.append(f'{indent * (level + 2)}<value name="{value.get("name")}" />\n')
                
                pieces.append(f'{indent * (level + 1)}</type>\n')
            
            pieces.append('</types>\n')
            return ''.join(pieces)
        
        # Generate the formatted XML
        formatted_xml = format_xml(new_root)
        
        # Write the final XML
        with open(output_xml_file, 'w', encoding='utf-8') as f:
            f.write(formatted_xml)
        
        print(f"Successfully created new XML file: {output_xml_file}")
        return True
    except Exception as e:
        print(f"Error during Excel to XML conversion: {str(e)}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert between DayZ types.xml and Excel format')
    parser.add_argument('--to-excel', action='store_true', help='Convert XML to Excel')
    parser.add_argument('--to-xml', action='store_true', help='Convert Excel back to XML')
    parser.add_argument('input', help='Input file path')
    parser.add_argument('output', help='Output file path')

    args = parser.parse_args()

    if not args.to_excel and not args.to_xml:
        parser.error("Must specify either --to-excel or --to-xml")

    if args.to_excel and args.to_xml:
        parser.error("Cannot specify both --to-excel and --to-xml")

    if not os.path.exists(args.input):
        parser.error(f"Input file does not exist: {args.input}")

    if args.to_excel:
        if not xml_to_excel(args.input, args.output):
            sys.exit(1)
    else:  # to_xml
        if not excel_to_xml(args.input, args.output):
            sys.exit(1)

if __name__ == "__main__":
    main()

