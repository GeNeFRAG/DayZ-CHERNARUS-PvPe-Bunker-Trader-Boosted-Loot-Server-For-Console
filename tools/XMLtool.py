from lxml import etree
import sys
from typing import List, Dict, Callable

class XMLProcessor:
    def __init__(self, xml_file: str):
        """
        Initialize the XML processor with a file path
        
        Args:
            xml_file (str): Path to the XML file
        """
        self.xml_file = xml_file
        self.tree = None
        self.root = None
        self._load_file()
    
    def _load_file(self) -> None:
        """Load the XML file using iterparse to handle large files efficiently"""
        try:
            # Use iterparse for memory efficiency with large files
            context = etree.iterparse(self.xml_file, events=('end',), huge_tree=True)
            self.root = None
            
            for event, elem in context:
                if self.root is None:
                    self.root = elem
            
            self.tree = elem.getroottree()
        except Exception as e:
            print(f"Error loading XML file: {str(e)}")
            sys.exit(1)
    
    def find_elements(self, xpath_query: str) -> List[etree._Element]:
        """
        Find elements using XPath
        
        Args:
            xpath_query (str): XPath query string
            
        Returns:
            List[etree._Element]: List of matching elements
        """
        return self.root.xpath(xpath_query)
    
    def bulk_update(self, xpath_query: str, updates: Dict[str, str]) -> int:
        """
        Update multiple elements matching an XPath query
        
        Args:
            xpath_query (str): XPath query to find elements
            updates (Dict[str, str]): Dictionary of attribute/value pairs to update
            
        Returns:
            int: Number of elements updated
        """
        elements = self.find_elements(xpath_query)
        count = 0
        
        for element in elements:
            for attr, value in updates.items():
                element.set(attr, value)
            count += 1
            
        return count
    
    def conditional_update(self, xpath_query: str, condition: Callable[[etree._Element], bool], 
                         updates: Dict[str, str]) -> int:
        """
        Update elements that match both XPath and a custom condition
        
        Args:
            xpath_query (str): XPath query to find elements
            condition (Callable): Function that takes an element and returns bool
            updates (Dict[str, str]): Dictionary of attribute/value pairs to update
            
        Returns:
            int: Number of elements updated
        """
        elements = self.find_elements(xpath_query)
        count = 0
        
        for element in elements:
            if condition(element):
                for attr, value in updates.items():
                    element.set(attr, value)
                count += 1
                
        return count
    
    def save(self, output_file: str) -> None:
        """
        Save the modified XML to a new file
        
        Args:
            output_file (str): Path to save the modified XML
        """
        self.tree.write(output_file, pretty_print=True, encoding='utf-8', xml_declaration=True)


# Initialize the XMLProcessor with the XML file path
xml_processor = XMLProcessor('/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZModding/dayzOffline.chernarusplus/db/types.xml')

# Find all type elements with usage name 'ContaminatedArea'
elements = xml_processor.find_elements('//type[@name="FAL"]')

# Extract and print the  attribute of each type element
for type_elem in elements:
    # Find all usage elements
    usages = type_elem.findall('usage')
    if usages:
        print("Usage locations:")
        for usage in usages:
            print(f"- {usage.get('name')}")
    else:
        print("No usage locations specified")

    values = type_elem.findall('value')
    if values:
        print("Value locations:")
        for value in values:
            print(f"- {value.get('name')}")
    else:
        print("No usage locations specified")
    
    print("-" * 20)