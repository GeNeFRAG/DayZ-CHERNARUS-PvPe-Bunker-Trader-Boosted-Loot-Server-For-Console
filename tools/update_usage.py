import xml.etree.ElementTree as ET
import sys

def update_usage(pos_file, proto_file, new_usage):
    # Parse the XML files
    pos_tree = ET.parse(pos_file)
    proto_tree = ET.parse(proto_file)
    
    pos_root = pos_tree.getroot()
    proto_root = proto_tree.getroot()
    
    # Extract group names from pos XML
    pos_groups = {group.attrib['name'] for group in pos_root.findall('group')}
    
    # Update usage in proto XML
    for group in proto_root.findall('group'):
        if group.attrib['name'] in pos_groups:
            usage = group.find('usage')
            if usage is not None:
                usage.attrib['name'] = new_usage
    
    # Write the updated proto XML back to file
    proto_tree.write(proto_file)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python update_usage.py <pos_file> <proto_file> <new_usage>")
        sys.exit(1)
    
    pos_file = sys.argv[1]
    proto_file = sys.argv[2]
    new_usage = sys.argv[3]
    
    update_usage(pos_file, proto_file, new_usage)
