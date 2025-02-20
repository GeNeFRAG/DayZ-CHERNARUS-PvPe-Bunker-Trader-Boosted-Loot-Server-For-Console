import xml.etree.ElementTree as ET
from collections import defaultdict
import argparse
import fnmatch
import csv
import sys
from statistics import mean, median

def parse_tags(tag_string):
    if not tag_string:
        return []
    return [tag.strip().lower() for tag in tag_string.split(',')]

def matches_any(name, filters):
    if not filters:
        return True
    name = name.lower()
    return any(filter_tag in name for filter_tag in filters)

def matches_pattern(name, pattern):
    if not pattern:
        return True
    return fnmatch.fnmatch(name.lower(), pattern.lower())

def analyze_types(xml_file, include_pattern=None, exclude_pattern=None, 
                 usage_filters=None, category_filters=None, value_filters=None):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Statistics containers
    stats = {
        'total': {'count': 0, 'nominal': 0, 'min': 0, 'nominal_values': [], 'min_values': []},
        'by_usage': defaultdict(lambda: {'count': 0, 'nominal': 0, 'min': 0, 'nominal_values': [], 'min_values': []}),
        'by_category': defaultdict(lambda: {'count': 0, 'nominal': 0, 'min': 0, 'nominal_values': [], 'min_values': []}),
        'by_value': defaultdict(lambda: {'count': 0, 'nominal': 0, 'min': 0, 'nominal_values': [], 'min_values': []})
    }
    
    for type_elem in root.findall('.//type'):
        type_name = type_elem.get('name', 'unnamed')
        
        # Skip if type matches exclude pattern or doesn't match include pattern
        if exclude_pattern and matches_pattern(type_name, exclude_pattern):
            continue
        if include_pattern and not matches_pattern(type_name, include_pattern):
            continue
            
        nominal = int(type_elem.find('nominal').text)
        min_val = int(type_elem.find('min').text)
        
        for usage in type_elem.findall('usage'):
            usage_name = usage.get('name', 'unnamed')
            
            if not matches_any(usage_name, usage_filters):
                continue
                
            has_matching_category = False
            has_matching_value = False
            
            # Process categories
            for category in usage.findall('category'):
                category_name = category.get('name', 'unnamed')
                if not category_filters or matches_any(category_name, category_filters):
                    has_matching_category = True
                    stats['by_category'][category_name]['count'] += 1
                    stats['by_category'][category_name]['nominal'] += nominal
                    stats['by_category'][category_name]['min'] += min_val
                    stats['by_category'][category_name]['nominal_values'].append(nominal)
                    stats['by_category'][category_name]['min_values'].append(min_val)
            
            # Process values
            for value in usage.findall('value'):
                value_name = value.get('name', 'unnamed')
                if not value_filters or matches_any(value_name, value_filters):
                    has_matching_value = True
                    stats['by_value'][value_name]['count'] += 1
                    stats['by_value'][value_name]['nominal'] += nominal
                    stats['by_value'][value_name]['min'] += min_val
                    stats['by_value'][value_name]['nominal_values'].append(nominal)
                    stats['by_value'][value_name]['min_values'].append(min_val)
            
            if (not category_filters or has_matching_category) and (not value_filters or has_matching_value):
                stats['total']['count'] += 1
                stats['total']['nominal'] += nominal
                stats['total']['min'] += min_val
                stats['total']['nominal_values'].append(nominal)
                stats['total']['min_values'].append(min_val)
                
                stats['by_usage'][usage_name]['count'] += 1
                stats['by_usage'][usage_name]['nominal'] += nominal
                stats['by_usage'][usage_name]['min'] += min_val
                stats['by_usage'][usage_name]['nominal_values'].append(nominal)
                stats['by_usage'][usage_name]['min_values'].append(min_val)
    
    return stats

def write_csv(stats, output_file=None):
    if output_file:
        f = open(output_file, 'w', newline='')
    else:
        f = sys.stdout
    
    writer = csv.writer(f)
    
    # Write headers
    writer.writerow(['Type', 'Count', 'Total Nominal', 'Total Min', 'Avg Nominal', 'Avg Min', 
                    'Median Nominal', 'Median Min', 'Max Nominal', 'Max Min'])
    
    # Write total stats
    total = stats['total']
    if total['count'] > 0:
        writer.writerow(['Total', total['count'], total['nominal'], total['min'],
                        round(mean(total['nominal_values']), 2), round(mean(total['min_values']), 2),
                        median(total['nominal_values']), median(total['min_values']),
                        max(total['nominal_values']), max(total['min_values'])])
    
    # Blank row
    writer.writerow([])
    writer.writerow(['--- By Usage ---'])
    
    # Write usage stats
    for usage, data in sorted(stats['by_usage'].items()):
        if data['count'] > 0:
            writer.writerow([usage, data['count'], data['nominal'], data['min'],
                           round(mean(data['nominal_values']), 2), round(mean(data['min_values']), 2),
                           median(data['nominal_values']), median(data['min_values']),
                           max(data['nominal_values']), max(data['min_values'])])
    
    # Write category stats
    if stats['by_category']:
        writer.writerow([])
        writer.writerow(['--- By Category ---'])
        for category, data in sorted(stats['by_category'].items()):
            if data['count'] > 0:
                writer.writerow([category, data['count'], data['nominal'], data['min'],
                               round(mean(data['nominal_values']), 2), round(mean(data['min_values']), 2),
                               median(data['nominal_values']), median(data['min_values']),
                               max(data['nominal_values']), max(data['min_values'])])
    
    # Write value stats
    if stats['by_value']:
        writer.writerow([])
        writer.writerow(['--- By Value ---'])
        for value, data in sorted(stats['by_value'].items()):
            if data['count'] > 0:
                writer.writerow([value, data['count'], data['nominal'], data['min'],
                               round(mean(data['nominal_values']), 2), round(mean(data['min_values']), 2),
                               median(data['nominal_values']), median(data['min_values']),
                               max(data['nominal_values']), max(data['min_values'])])
    
    if output_file:
        f.close()

def main():
    parser = argparse.ArgumentParser(description='Query types.xml file for DayZ')
    parser.add_argument('file', help='Path to the XML file')
    parser.add_argument('-i', '--include', help='Pattern for types to include (use * as wildcard)')
    parser.add_argument('-e', '--exclude', help='Pattern for types to exclude (use * as wildcard)')
    parser.add_argument('-u', '--usage', help='Filter by usage names (comma-separated)')
    parser.add_argument('-c', '--category', help='Filter by category names (comma-separated)')
    parser.add_argument('-v', '--value', help='Filter by value names (comma-separated)')
    parser.add_argument('-o', '--output', help='Output CSV file (if not specified, prints to stdout)')

    args = parser.parse_args()

    try:
        stats = analyze_types(
            args.file,
            include_pattern=args.include,
            exclude_pattern=args.exclude,
            usage_filters=parse_tags(args.usage),
            category_filters=parse_tags(args.category),
            value_filters=parse_tags(args.value)
        )
        
        if stats['total']['count'] == 0:
            print("No matches found")
            return
            
        write_csv(stats, args.output)
        
    except FileNotFoundError:
        print(f"Error: Could not find file {args.file}")
    except ET.ParseError:
        print("Error: Invalid XML format")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
