import xml.etree.ElementTree as ET
import sys

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

def modify_xml(src_file, target_file, output_file):
    src_tree = ET.parse(src_file)
    src_root = src_tree.getroot()

    target_tree = ET.parse(target_file)
    target_root = target_tree.getroot()

    remove_category_tags(target_root)
    replace_usage_tags(src_root, target_root)
    replace_usage_tags_de(target_root)

    indent(target_root)
    target_tree.write(output_file, encoding='UTF-8', xml_declaration=True)
    remove_empty_lines(output_file)

def main():
    if len(sys.argv) != 4:
        print("Usage: python modify_xml.py <src_file> <target_file> <output_file>")
        sys.exit(1)

    src_file = sys.argv[1]
    target_file = sys.argv[2]
    output_file = sys.argv[3]

    modify_xml(src_file, target_file, output_file)

if __name__ == "__main__":
    main()
