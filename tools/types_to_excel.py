#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import pandas as pd
from typing import TypedDict, Dict, Set, List
from io import StringIO
import argparse
import sys
import os
import openpyxl
from dataclasses import dataclass

@dataclass
class XMLConfig:
    flag_columns: List[str] = None
    numeric_fields: List[str] = None

    def __post_init__(self):
        self.flag_columns = [
            'count_in_cargo',
            'count_in_hoarder',
            'count_in_map',
            'count_in_player',
            'crafted',
            'deloot'
        ]
        self.numeric_fields = ['nominal', 'lifetime', 'restock', 'min', 'quantmin', 'quantmax', 'cost']

class ItemData(TypedDict, total=False):
    name: str
    nominal: int
    lifetime: int
    restock: int
    min: int
    quantmin: int
    quantmax: int
    cost: int
    category: str

def collect_values(root: ET.Element) -> tuple[Set[str], Set[str]]:
    usage_values = {usage.get('name', '') for type_elem in root.findall('type') 
                   for usage in type_elem.findall('usage')}
    tier_values = {value.get('name', '') for type_elem in root.findall('type') 
                   for value in type_elem.findall('value')}
    return usage_values, tier_values

def process_type_element(type_elem: ET.Element, config: XMLConfig, 
                        usage_columns: List[str], tier_columns: List[str]) -> Dict:
    flags_elem = type_elem.find('flags')
    category_elem = type_elem.find('category')
    current_usage = {u.get('name', '') for u in type_elem.findall('usage')}
    current_tiers = {v.get('name', '') for v in type_elem.findall('value')}

    item_data = {
        'name': type_elem.get('name', ''),
        **{field: int(type_elem.find(field).text) if type_elem.find(field) is not None 
           and type_elem.find(field).text else '' for field in config.numeric_fields},
        **{flag: int(flags_elem.get(flag, '0')) if flags_elem is not None else '' 
           for flag in config.flag_columns},
        'category': category_elem.get('name', '') if category_elem is not None else '',
        **{f'usage_{usage}': 'X' if usage in current_usage else '' for usage in usage_columns},
        **{f'tier_{tier}': 'X' if tier in current_tiers else '' for tier in tier_columns}
    }
    return item_data

def format_xml(elem: ET.Element, config: XMLConfig, level: int = 0) -> str:
    indent = "    "
    output = StringIO()
    output.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
    output.write('<types>\n')
    
    for type_elem in elem:
        output.write(f'{indent * (level + 1)}<type name="{type_elem.get("name")}">\n')
        
        # Write numeric fields
        for field in config.numeric_fields:
            if (field_elem := type_elem.find(field)) is not None:
                output.write(f'{indent * (level + 2)}<{field}>{field_elem.text}</{field}>\n')
        
        # Write flags
        if (flags_elem := type_elem.find('flags')) is not None:
            flags_attrs = ' '.join(f'{k}="{v}"' for k, v in flags_elem.attrib.items())
            output.write(f'{indent * (level + 2)}<flags {flags_attrs} />\n')
        
        # Write category
        if (category_elem := type_elem.find('category')) is not None:
            output.write(f'{indent * (level + 2)}<category name="{category_elem.get("name")}" />\n')
        
        # Write usage and value tags
        for tag_type in ['usage', 'value']:
            for elem in type_elem.findall(tag_type):
                output.write(f'{indent * (level + 2)}<{tag_type} name="{elem.get("name")}" />\n')
        
        output.write(f'{indent * (level + 1)}</type>\n')
    
    output.write('</types>\n')
    return output.getvalue()

def xml_to_excel(xml_file: str, excel_file: str) -> bool:
    try:
        config = XMLConfig()
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Collect values and prepare columns
        usage_values, tier_values = collect_values(root)
        usage_columns = sorted(usage_values)
        tier_columns = sorted(tier_values)
        
        # Process all type elements
        data = [process_type_element(type_elem, config, usage_columns, tier_columns) 
                for type_elem in root.findall('type')]
        
        # Create and process DataFrame
        df = pd.DataFrame(data).replace('', pd.NA)
        numeric_columns = config.numeric_fields + config.flag_columns
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
        
        # Save to Excel with formatting
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            
            for idx, column in enumerate(df.columns, 1):
                letter = openpyxl.utils.get_column_letter(idx)
                for cell in worksheet[letter][1:]:
                    cell.number_format = '0' if column in numeric_columns else '@'
        
        print(f"Successfully exported to {excel_file}")
        return True
        
    except Exception as e:
        print(f"Error during XML to Excel conversion: {str(e)}", file=sys.stderr)
        return False

def excel_to_xml(excel_file: str, output_xml_file: str, chunk_size: int = 1000) -> bool:
    try:
        config = XMLConfig()
        new_root = ET.Element('types')
        
        # Get column information
        df = pd.read_excel(excel_file)
        usage_columns = [col for col in df.columns if col.startswith('usage_')]
        tier_columns = [col for col in df.columns if col.startswith('tier_')]
        
        # Process DataFrame in chunks
        for chunk_start in range(0, len(df), chunk_size):
            chunk = df.iloc[chunk_start:chunk_start + chunk_size]
            
            for _, row in chunk.iterrows():
                type_elem = ET.SubElement(new_root, 'type')
                
                if pd.notna(row['name']) and str(row['name']).strip():
                    type_elem.set('name', str(row['name']).strip())
                
                # Process numeric fields
                for field in config.numeric_fields:
                    if pd.notna(row[field]) and str(row[field]).strip():
                        field_elem = ET.SubElement(type_elem, field)
                        field_elem.text = str(int(float(row[field])))
                
                # Process flags
                flags_attrs = {flag: str(int(float(row[flag]))) 
                             for flag in config.flag_columns 
                             if pd.notna(row[flag])}
                if flags_attrs:
                    flags_elem = ET.SubElement(type_elem, 'flags')
                    for flag, value in flags_attrs.items():
                        flags_elem.set(flag, value)
                
                # Process category
                if pd.notna(row['category']) and str(row['category']).strip():
                    category_elem = ET.SubElement(type_elem, 'category')
                    category_elem.set('name', str(row['category']).strip())
                
                # Process usage and tier tags
                for col_list, tag_type in [(usage_columns, 'usage'), (tier_columns, 'value')]:
                    for col in col_list:
                        if pd.notna(row[col]) and row[col] == 'X':
                            tag_name = col.replace(f'{tag_type}_', '')
                            tag_elem = ET.SubElement(type_elem, tag_type)
                            tag_elem.set('name', tag_name)
        
        # Generate and write formatted XML
        formatted_xml = format_xml(new_root, config)
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

    success = xml_to_excel(args.input, args.output) if args.to_excel else excel_to_xml(args.input, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
