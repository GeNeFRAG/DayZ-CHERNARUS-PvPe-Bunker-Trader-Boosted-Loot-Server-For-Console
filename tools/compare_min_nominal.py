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

def update_min_values(types_file):
    types, root = parse_xml(types_file)
    
    for type_name, values in types.items():
        nominal = values['nominal']
        if nominal != 0:
            new_min_value = max(1, int(nominal * 0.4))  # Ensure no comma numbers and min is at least 1
            values['element'].find('min').text = str(new_min_value)
            print(f"{type_name}: updated min to {new_min_value}")

    #tree = ET.ElementTree(root)
    #tree.write(types_file)

if __name__ == "__main__":
    types_file = '/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZ/tools/types.xml'
    update_min_values(types_file)
