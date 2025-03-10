import xml.etree.ElementTree as ET
import sys
import argparse

def remove_category_tags(root):
    for category in root.findall('.//category'):
        parent = root.find(f".//{category.tag}/..")
        if parent is not None:
            parent.remove(category)

def replace_usage_tags(src_root, target_root):
    src_groups = {group.get('name') for group in src_root.findall('.//group')}
    for group_name in src_groups:
        target_group = target_root.find(f".//group[@name='{group_name}']")
        if target_group is not None:
            for usage in target_group.findall('usage'):
                target_group.remove(usage)
            for usage in src_root.find(f".//group[@name='{group_name}']").findall('usage'):
                target_group.insert(0, usage)  # Insert usage tags directly below the group tag

def replace_usage_tags_de(root):
    for group in root.findall('.//group'):
        group_name = group.get('name')
        if group_name.endswith('_DE'):
            base_group_name = group_name[:-3]
            target_group = root.find(f".//group[@name='{base_group_name}']")
            if target_group is not None:
                for usage in target_group.findall('usage'):
                    target_group.remove(usage)
                for usage in group.findall('usage'):
                    target_group.insert(0, usage)  # Insert usage tags directly below the group tag

def remove_empty_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if line.strip():
                file.write(line)

def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def modify_xml(src_file, target_file, output_file, cmd_usage_tag=None):
    if src_file:
        src_tree = ET.parse(src_file)
        src_root = src_tree.getroot()
    else:
        src_root = None

    target_tree = ET.parse(target_file)
    target_root = target_tree.getroot()

    remove_category_tags(target_root)
    if src_root:
        replace_usage_tags(src_root, target_root)
    replace_usage_tags_de(target_root)

    if cmd_usage_tag:
        for group in target_root.findall('.//group'):
            for tag in group.findall('category') + group.findall('usage') + group.findall('tag') + group.findall('value'):
                group.remove(tag)
            usage_elem = ET.Element('usage')
            usage_elem.set('name', cmd_usage_tag)
            group.insert(0, usage_elem)  # Insert usage tag directly after the group tag

    indent(target_root)
    target_tree.write(output_file, encoding='UTF-8', xml_declaration=True)
    remove_empty_lines(output_file)

def main():
    parser = argparse.ArgumentParser(description='Modify XML files by replacing usage tags and removing category tags.')
    parser.add_argument('--src_file', help='Path to the source XML file', default=None)
    parser.add_argument('target_file', help='Path to the target XML file')
    parser.add_argument('output_file', help='Path to the output XML file')
    parser.add_argument('--usage_tag', help='Usage tag to be added to all groups', default=None)
    
    args = parser.parse_args()

    modify_xml(args.src_file, args.target_file, args.output_file, args.usage_tag)

if __name__ == "__main__":
    main()
