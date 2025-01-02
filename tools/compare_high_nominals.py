import xml.etree.ElementTree as ET

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    types = {}
    for type_elem in root.findall('type'):
        name = type_elem.get('name')
        nominal = int(type_elem.find('nominal').text)
        min_value = int(type_elem.find('min').text)
        usage = [usage_elem.get('name') for usage_elem in type_elem.findall('usage')]
        category_elem = type_elem.find('category')
        category = category_elem.get('name') if category_elem is not None else None
        types[name] = {'nominal': nominal, 'min': min_value, 'usage': usage, 'category': category, 'element': type_elem}
    return types, root

def compare_and_update_high_nominals(vanilla_file, types_file):
    vanilla_types, _ = parse_xml(vanilla_file)
    types_20, root = parse_xml(types_file)
    
    for type_name, values in types_20.items():
        if type_name in vanilla_types:
            vanilla_nominal = vanilla_types[type_name]['nominal']
            types_20_nominal = values['nominal']
            if vanilla_nominal > 0 and types_20_nominal > 4 * vanilla_nominal and 'Military' not in values['usage'] and values['category'] not in ['weapons', 'explosives']:
                print(f"{type_name}: Types 20 nominal ({types_20_nominal}) > 4 * Vanilla nominal ({vanilla_nominal})")
                values['element'].find('nominal').text = str(vanilla_nominal)
    #tree = ET.ElementTree(root)
    #tree.write(types_file)

if __name__ == "__main__":
    vanilla_file = '/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZ/tools/types_vanilla.xml'
    types_file = '/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZ/tools/types.xml'
    compare_and_update_high_nominals(vanilla_file, types_file)
