import xml.etree.ElementTree as ET

# Parse cfgspawnabletypes.xml
cfgspawnabletypes_tree = ET.parse('/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZ/tools/cfgspawnabletypes.xml')
cfgspawnabletypes_root = cfgspawnabletypes_tree.getroot()

# Parse types.xml
types_tree = ET.parse('/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZ/tools/types.xml')
types_root = types_tree.getroot()

# Extract item names from cfgspawnabletypes.xml
cfgspawnabletypes_items = set()
for type_elem in cfgspawnabletypes_root.findall('type'):
    cfgspawnabletypes_items.add(type_elem.get('name'))
    for item_elem in type_elem.findall('.//item'):
        cfgspawnabletypes_items.add(item_elem.get('name'))

# Extract item names from types.xml
types_items = set()
for type_elem in types_root.findall('type'):
    types_items.add(type_elem.get('name'))

# Find items in cfgspawnabletypes.xml that are not in types.xml
missing_items = cfgspawnabletypes_items - types_items

# Print missing items
print("Items in cfgspawnabletypes.xml but not in types.xml:")
for item in missing_items:
    print(item)