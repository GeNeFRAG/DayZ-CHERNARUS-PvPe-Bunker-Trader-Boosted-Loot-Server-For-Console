from lxml import etree

# Load the XML file
tree = etree.parse('/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZModding/FriendZ Of DayZ/cfgspawnabletypes.xml')
root = tree.getroot()

# Find the comment <!-- VEHICLES -->
vehicles_comment = None
for comment in root.xpath("//comment()"):
    if "VEHICLES" in comment.text:
        vehicles_comment = comment
        break

if vehicles_comment is not None:
    # Find all type elements after the <!-- VEHICLES --> comment
    for type_elem in vehicles_comment.itersiblings(tag="type"):
        # Find all item elements within each type element and change their chance attribute to 1.0
        for item in type_elem.xpath(".//item"):
            item.set('chance', '1.0')

    # Save the modified XML back to the file
    tree.write('/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZModding/FriendZ Of DayZ/cfgspawnabletypes_modified.xml', pretty_print=True, encoding='utf-8', xml_declaration=True)
else:
    print("<!-- VEHICLES --> comment not found.")