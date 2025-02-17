import argparse
import sys
import os
import xml.etree.ElementTree as ET

def parse_lootmax(file_path):
    """
    Parses the lootmax values from the given XML file.

    Args:
        file_path (str): Path to the XML file.

    Returns:
        dict: A dictionary containing lootmax data for groups and containers.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    lootmax_data = {}

    for group in root.findall('group'):
        group_name = group.get('name')
        group_lootmax = int(group.get('lootmax', 0))
        containers = []

        for container in group.findall('container'):
            container_name = container.get('name')
            container_lootmax = int(container.get('lootmax', 0))
            containers.append((container_name, container_lootmax))

        lootmax_data[group_name] = {
            'group_lootmax': group_lootmax,
            'containers': containers
        }

    return lootmax_data

def compare_lootmax(file1, file2, output_file="comparison_results.txt"):
    """
    Compares lootmax values between two XML files and writes the comparison results to an output file.

    Args:
        file1 (str): Path to the first XML file.
        file2 (str): Path to the second XML file.
        output_file (str): Path to the output file for comparison results.
    """
    lootmax1 = parse_lootmax(file1)
    lootmax2 = parse_lootmax(file2)

    common_groups = set(lootmax1.keys()).intersection(set(lootmax2.keys()))
    unique_to_file1 = set(lootmax1.keys()) - set(lootmax2.keys())
    unique_to_file2 = set(lootmax2.keys()) - set(lootmax1.keys())
    
    file1_name = os.path.basename(file1)
    file2_name = os.path.basename(file2)
    
    GROUP_COL_WIDTH = 40
    VALUE_COL_WIDTH = max(20, len(file1_name), len(file2_name))  # Adjust column width based on filename length

    with open(output_file, 'w') as f:
        # Write header
        f.write(f"{'Group/Container':<{GROUP_COL_WIDTH}} {file1_name:^{VALUE_COL_WIDTH}} {file2_name:^{VALUE_COL_WIDTH}}\n")
        total_width = GROUP_COL_WIDTH + VALUE_COL_WIDTH * 2 + 1  # +1 for the space between columns
        f.write("-" * total_width + "\n")

        for group in sorted(common_groups):
            lootmax1_data = lootmax1[group]
            lootmax2_data = lootmax2[group]

            # Write group name and its lootmax
            f.write(f"{group:<{GROUP_COL_WIDTH}} {lootmax1_data['group_lootmax']:^{VALUE_COL_WIDTH}} {lootmax2_data['group_lootmax']:^{VALUE_COL_WIDTH}}\n")
            
            # Get all containers
            containers1 = {name: lootmax for name, lootmax in lootmax1_data['containers']}
            containers2 = {name: lootmax for name, lootmax in lootmax2_data['containers']}
            all_containers = set(containers1.keys()).union(set(containers2.keys()))

            # Write container information
            for container in sorted(all_containers):
                lootmax1_value = containers1.get(container, 'N/A')
                lootmax2_value = containers2.get(container, 'N/A')
                diff_marker = ' *' if lootmax1_value != lootmax2_value else ''
                container_name = f"  {container}"  # Indent container names
                f.write(f"{container_name:<{GROUP_COL_WIDTH}} {str(lootmax1_value):^{VALUE_COL_WIDTH}} {str(lootmax2_value):^{VALUE_COL_WIDTH}}{diff_marker}\n")

            # Write total
            total_lootmax1 = sum(value for value in containers1.values() if isinstance(value, (int, float)))
            total_lootmax2 = sum(value for value in containers2.values() if isinstance(value, (int, float)))
            f.write(f"{'  Total':<{GROUP_COL_WIDTH}} {total_lootmax1:^{VALUE_COL_WIDTH}} {total_lootmax2:^{VALUE_COL_WIDTH}}\n")
            f.write("\n")  # Add blank line between groups

        # Write groups unique to file1
        if unique_to_file1:
            f.write("\n" + "-" * total_width + "\n")
            f.write(f"Groups only in {file1_name}:\n")
            for group in sorted(unique_to_file1):
                group_data = lootmax1[group]
                f.write(f"{group:<{GROUP_COL_WIDTH}} {group_data['group_lootmax']:^{VALUE_COL_WIDTH}}\n")
                
                # Write container information for unique groups
                for container_name, container_lootmax in sorted(group_data['containers']):
                    container_line = f"  {container_name}"
                    f.write(f"{container_line:<{GROUP_COL_WIDTH}} {container_lootmax:^{VALUE_COL_WIDTH}}\n")
                
                # Write total for this group
                total_lootmax = sum(lootmax for _, lootmax in group_data['containers'])
                f.write(f"{'  Total':<{GROUP_COL_WIDTH}} {total_lootmax:^{VALUE_COL_WIDTH}}\n")
                f.write("\n")

        # Write groups unique to file2
        if unique_to_file2:
            f.write("\n" + "-" * total_width + "\n")
            f.write(f"Groups only in {file2_name}:\n")
            for group in sorted(unique_to_file2):
                group_data = lootmax2[group]
                f.write(f"{group:<{GROUP_COL_WIDTH}} {' ':^{VALUE_COL_WIDTH}} {group_data['group_lootmax']:^{VALUE_COL_WIDTH}}\n")
                
                # Write container information for unique groups
                for container_name, container_lootmax in sorted(group_data['containers']):
                    container_line = f"  {container_name}"
                    f.write(f"{container_line:<{GROUP_COL_WIDTH}} {' ':^{VALUE_COL_WIDTH}} {container_lootmax:^{VALUE_COL_WIDTH}}\n")
                
                # Write total for this group
                total_lootmax = sum(lootmax for _, lootmax in group_data['containers'])
                f.write(f"{'  Total':<{GROUP_COL_WIDTH}} {' ':^{VALUE_COL_WIDTH}} {total_lootmax:^{VALUE_COL_WIDTH}}\n")
                f.write("\n")

    print(f"Comparison results have been written to {output_file}")

def merge_lootmax_files(file1, file2, output_file="merged_mapgroupproto.xml"):
    """
    Merges two lootmax files:
    - Preserves complete structure of file2 including comments and all tags
    - Updates lootmax values from file1 only for groups that exist in file1
    - Keeps original lootmax values from file2 for groups not in file1
    - Keeps all other tags, attributes and comments unchanged
    - Ensures lootmax attribute appears right after name attribute

    Args:
        file1 (str): Path to the first XML file.
        file2 (str): Path to the second XML file.
        output_file (str): Path to the output file for the merged XML.
    """
    class CommentedTreeBuilder(ET.TreeBuilder):
        def comment(self, data):
            self.start(ET.Comment, {})
            self.data(data)
            self.end(ET.Comment)

    # Parse both files
    tree1 = ET.parse(file1)
    root1 = tree1.getroot()

    parser = ET.XMLParser(target=CommentedTreeBuilder())
    tree2 = ET.parse(file2, parser=parser)
    root2 = tree2.getroot()

    # Create dictionaries for quick lookup from file1
    groups1 = {}
    for group in root1.findall('group'):
        group_name = group.get('name')
        containers = {cont.get('name'): cont.get('lootmax') 
                     for cont in group.findall('container')}
        groups1[group_name] = {
            'lootmax': group.get('lootmax'),
            'containers': containers
        }

    def create_ordered_attributes(elem, is_in_file1=False, file1_lootmax=None):
        """Create ordered attributes with name first, then lootmax, then others"""
        attrs = {}
        
        # First add name if it exists
        if 'name' in elem.attrib:
            attrs['name'] = elem.get('name')
        
        # Then add lootmax if it should exist
        if is_in_file1 and file1_lootmax:
            attrs['lootmax'] = file1_lootmax
        elif not is_in_file1 and 'lootmax' in elem.attrib:
            attrs['lootmax'] = elem.get('lootmax')
            
        # Then add all other attributes except name and lootmax
        for key, value in elem.attrib.items():
            if key not in ['name', 'lootmax']:
                attrs[key] = value
                
        return attrs

    def copy_element_with_children(elem, parent):
        """Helper function to copy an element and all its children"""
        if isinstance(elem.tag, str):
            # Handle groups and containers specially
            if elem.tag == 'group':
                group_name = elem.get('name')
                is_in_file1 = group_name in groups1
                file1_lootmax = groups1[group_name]['lootmax'] if is_in_file1 else None
                
                # Create new element with ordered attributes
                attrs = create_ordered_attributes(elem, is_in_file1, file1_lootmax)
                new_elem = ET.SubElement(parent, elem.tag, attrs)
                
            elif elem.tag == 'container':
                group_name = parent.get('name')
                cont_name = elem.get('name')
                is_in_file1 = (group_name in groups1 and 
                              cont_name in groups1[group_name]['containers'])
                file1_lootmax = (groups1[group_name]['containers'][cont_name] 
                                if is_in_file1 else None)
                
                # Create new element with ordered attributes
                attrs = create_ordered_attributes(elem, is_in_file1, file1_lootmax)
                new_elem = ET.SubElement(parent, elem.tag, attrs)
                
            else:
                # For all other elements, copy as is
                new_elem = ET.SubElement(parent, elem.tag, elem.attrib)
            
            # Copy text content if any
            if elem.text and elem.text.strip():
                new_elem.text = elem.text
            
            # Recursively copy all child elements
            for child in elem:
                copy_element_with_children(child, new_elem)
        else:  # Comment
            comment = ET.Comment(elem.text)
            parent.append(comment)
            if elem.tail and elem.tail.strip():
                comment.tail = elem.tail

    # Create new root and copy everything from file2
    new_root = ET.Element(root2.tag)
    new_root.attrib = root2.attrib

    # Copy all elements from file2
    for elem in root2:
        copy_element_with_children(elem, new_root)

    # Format the XML with proper indentation
    def indent(elem, level=0):
        i = "\n" + level*"    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                indent(subelem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    # Apply indentation
    indent(new_root)

    # Write the merged file
    tree = ET.ElementTree(new_root)
    with open(output_file, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        tree.write(f, encoding='utf-8', xml_declaration=False)

    print(f"Merged file has been written to {output_file}")

def main():
    """
    Main function to parse arguments and perform comparison and optional merging of lootmax values.
    """
    parser = argparse.ArgumentParser(description='Compare and optionally merge lootmax values between two XML files')
    parser.add_argument('file1', help='First XML file (base file)')
    parser.add_argument('file2', help='Second XML file (file to compare with)')
    parser.add_argument('-c', '--comparison', 
                      help='Output file for comparison results (default: comparison_results.txt)',
                      default='comparison_results.txt')
    parser.add_argument('-m', '--merge',
                      help='Create merged output file with updated lootmax values',
                      action='store_true')
    parser.add_argument('-o', '--output',
                      help='Output file for merged XML (default: merged_mapgroupproto.xml)',
                      default='merged_mapgroupproto.xml')

    args = parser.parse_args()

    # Always generate comparison
    compare_lootmax(args.file1, args.file2, args.comparison)
    
    # Only merge if requested
    if args.merge:
        merge_lootmax_files(args.file1, args.file2, args.output)
        print(f"Merged file has been written to {args.output}")

if __name__ == "__main__":
    main()
