import xml.etree.ElementTree as ET
import argparse
import fnmatch

def sum_values(xml_file, pattern, field='nominal', usages=None, category=None, tiers=None, debug=False):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    total = 0
    matched_types = []
    
    if debug:
        print(f"\nDebug: Looking for pattern '{pattern}'")
        if usages:
            print(f"Debug: Looking for usages: {', '.join(usages)}")
        if tiers:
            print(f"Debug: Looking for tiers: {', '.join(tiers)}")
    
    for type_elem in root.findall('type'):
        type_name = type_elem.get('name')
        
        # Check if type matches pattern
        if not fnmatch.fnmatch(type_name, pattern):
            continue
            
        # Check usage filter - match if ANY of the specified usages match
        if usages:
            usage_elem = type_elem.find('usage')
            if usage_elem is not None:
                if debug:
                    print(f"\nDebug: Found matching pattern: {type_name}")
                    print(f"  - Usage attribute: {usage_elem.get('name')}")
                
                if usage_elem.get('name') not in usages:
                    if debug:
                        print(f"  - Filtered out: Usage mismatch (found '{usage_elem.get('name')}', wanted one of {usages})")
                    continue
                elif debug:
                    print(f"  - Usage match found!")
            else:
                if debug:
                    print(f"  - Filtered out: No usage element")
                continue
                
        # Check category filter
        if category:
            category_elem = type_elem.find('category')
            if not category_elem or category_elem.get('name') != category:
                continue
                
        # Check tier filter - match if ANY of the specified tiers exist among item's tiers
        if tiers:
            item_tiers = [v.get('name') for v in type_elem.findall('value') if v.get('name').startswith('Tier')]
            if not any(tier in item_tiers for tier in tiers):
                if debug:
                    print(f"  - Filtered out: None of required tiers {tiers} found in {item_tiers}")
                continue
            elif debug:
                matching_tiers = [tier for tier in tiers if tier in item_tiers]
                print(f"  - Found matching tiers: {matching_tiers}")
        
        # If we got here, all filters passed
        try:
            value = int(type_elem.find(field).text)
            total += value
            
            # Collect additional info for display
            info = [f"{type_name} ({value})"]
            if usages or category or tiers:
                extra = []
                if usages:
                    usage_text = type_elem.find('usage').get('name') if type_elem.find('usage') is not None else 'N/A'
                    extra.append(f"usage={usage_text}")
                if category:
                    category_text = type_elem.find('category').get('name') if type_elem.find('category') is not None else 'N/A'
                    extra.append(f"category={category_text}")
                if tiers:
                    item_tiers = [v.get('name') for v in type_elem.findall('value') if v.get('name').startswith('Tier')]
                    extra.append(f"tiers=[{', '.join(item_tiers)}]")
                info.append(f"[{', '.join(extra)}]")
            
            matched_types.append(" ".join(info))
            if debug:
                print(f"  - Added to matches with {field}={value}")
            
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
    parser.add_argument('--usage', action='append', help='Filter by usage (e.g., Military). Can be specified multiple times')
    parser.add_argument('--category', help='Filter by category (e.g., weapons)')
    parser.add_argument('--tier', action='append', help='Filter by tier (e.g., Tier1). Can be specified multiple times')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    try:
        total, matched = sum_values(
            args.xml, 
            args.pattern, 
            args.field,
            args.usage,
            args.category,
            args.tier,
            args.debug
        )
        
        # Print applied filters
        filters = []
        if args.usage:
            filters.append(f"usages=[{', '.join(args.usage)}]")
        if args.category:
            filters.append(f"category={args.category}")
        if args.tier:
            filters.append(f"tiers=[{', '.join(args.tier)}]")
            
        if filters:
            print("\nApplied filters:", ", ".join(filters))
        
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
