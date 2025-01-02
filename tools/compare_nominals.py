import xml.etree.ElementTree as ET

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    types = {}
    for type_elem in root.findall('type'):
        name = type_elem.get('name')
        nominal = int(type_elem.find('nominal').text)
        min_value = int(type_elem.find('min').text)
        types[name] = {'nominal': nominal, 'min': min_value, 'element': type_elem}
    return types, root

def compare_and_update_nominals(vanilla_file, types_file):
    vanilla_types, _ = parse_xml(vanilla_file)
    types_20, root = parse_xml(types_file)
    
    for type_name, values in types_20.items():
        if type_name in vanilla_types:
            vanilla_nominal = vanilla_types[type_name]['nominal']
            types_20_nominal = values['nominal']
            vanilla_min = vanilla_types[type_name]['min']
            types_20_min = values['min']
            if vanilla_nominal > types_20_nominal:
                print(f"{type_name}: Vanilla nominal ({vanilla_nominal}) > Types 20 nominal ({types_20_nominal})")
                values['element'].find('nominal').text = str(vanilla_nominal)
            if vanilla_min > types_20_min:
                print(f"{type_name}: Vanilla min ({vanilla_min}) > Types 20 min ({types_20_min})")
                values['element'].find('min').text = str(vanilla_min)
    
    tree = ET.ElementTree(root)
    tree.write(types_file)

if __name__ == "__main__":
    vanilla_file = '/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZ/tools/types_vanilla.xml'
    types_file = '/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZ/tools/types.xml'
    compare_and_update_nominals(vanilla_file, types_file)
