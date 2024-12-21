import xml.etree.ElementTree as ET

def copy_default_values(source_file, target_file):
    # Parse the source and target XML files
    source_tree = ET.parse(source_file)
    target_tree = ET.parse(target_file)
    
    source_root = source_tree.getroot()
    target_root = target_tree.getroot()

    # Create a dictionary to store the default values from the source file
    default_values = {}
    for type_elem in source_root.findall('type'):
        name = type_elem.get('name')
        nominal = type_elem.find('nominal').text
        quantmin = type_elem.find('min').text
        default_values[name] = {'nominal': nominal, 'min': quantmin}

    # Update the target file with the default values from the source file
    for type_elem in target_root.findall('type'):
        name = type_elem.get('name')
        if name in default_values:
            type_elem.find('nominal').text = default_values[name]['nominal']
            type_elem.find('min').text = default_values[name]['min']

    # Write the updated target XML to a new file
    target_tree.write('updated_' + target_file)

# Example usage
source_file = 'types_src.xml'
target_file = 'types_target.xml'
copy_default_values(source_file, target_file)
