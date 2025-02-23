import xml.etree.ElementTree as ET
import csv
import argparse

def extract_values(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    values = {}
    for type_elem in root.findall('type'):
        name = type_elem.get('name')
        nominal = type_elem.find('nominal')
        min_val = type_elem.find('min')
        restock = type_elem.find('restock')
        lifetime = type_elem.find('lifetime')
        values[name] = {
            'nominal': int(nominal.text) if nominal is not None else None,
            'min': int(min_val.text) if min_val is not None else None,
            'restock': int(restock.text) if restock is not None else None,
            'lifetime': int(lifetime.text) if lifetime is not None else None
        }
    return values

def compare_values(file1_values, file2_values):
    differences = []
    all_items = {**file1_values, **file2_values}
    for item in all_items:
        file1_vals = file1_values.get(item, {})
        file2_vals = file2_values.get(item, {})
        if file1_vals != file2_vals:
            differences.append({
                'item': item,
                'file1_nominal': file1_vals.get('nominal'),
                'file1_min': file1_vals.get('min'),
                'file1_lifetime': file1_vals.get('lifetime'),
                'file1_restock': file1_vals.get('restock'),
                'file2_nominal': file2_vals.get('nominal'),
                'file2_min': file2_vals.get('min'),
                'file2_lifetime': file2_vals.get('lifetime'),
                'file2_restock': file2_vals.get('restock'),
                'nominal_diff': (file1_vals.get('nominal') - file2_vals.get('nominal')) if file1_vals.get('nominal') is not None and file2_vals.get('nominal') is not None else None,
                'min_diff': (file1_vals.get('min') - file2_vals.get('min')) if file1_vals.get('min') is not None and file2_vals.get('min') is not None else None,
                'lifetime_diff': (file1_vals.get('lifetime') - file2_vals.get('lifetime')) if file1_vals.get('lifetime') is not None and file2_vals.get('lifetime') is not None else None,
                'restock_diff': (file1_vals.get('restock') - file2_vals.get('restock')) if file1_vals.get('restock') is not None and file2_vals.get('restock') is not None else None
            })
    return differences

def write_differences_to_csv(differences, output_csv_file):
    with open(output_csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['item', 'file1_nominal', 'file1_min', 'file1_restock', 'file1_lifetime', 'file2_nominal', 'file2_min', 'file2_restock', 'file2_lifetime', 'nominal_diff', 'min_diff', 'restock_diff', 'lifetime_diff'])
        writer.writeheader()
        for diff in differences:
            writer.writerow(diff)

def main():
    parser = argparse.ArgumentParser(description='Compare values between two types.xml files and output differences to a CSV file.')
    parser.add_argument('file1', help='Path to the first XML file')
    parser.add_argument('file2', help='Path to the second XML file')
    parser.add_argument('output_csv', help='Path to the output CSV file')

    args = parser.parse_args()

    file1_values = extract_values(args.file1)
    file2_values = extract_values(args.file2)
    differences = compare_values(file1_values, file2_values)
    write_differences_to_csv(differences, args.output_csv)

    print(f"Differences written to {args.output_csv}")

if __name__ == "__main__":
    main()
