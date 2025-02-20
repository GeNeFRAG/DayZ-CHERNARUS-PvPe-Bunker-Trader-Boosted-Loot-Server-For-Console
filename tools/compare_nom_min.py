import xml.etree.ElementTree as ET
import csv
import argparse

def extract_nom_min(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    nom_min_values = {}
    for type_elem in root.findall('type'):
        name = type_elem.get('name')
        nominal = type_elem.find('nominal')
        min_val = type_elem.find('min')
        nom_min_values[name] = {
            'nominal': int(nominal.text),
            'min': int(min_val.text)
        }
    return nom_min_values

def compare_nom_min(file1_values, file2_values):
    differences = []
    all_items = {**file1_values, **file2_values}
    for item in all_items:
        file1_nom = file1_values.get(item, {}).get('nominal')
        file1_min = file1_values.get(item, {}).get('min')
        file2_nom = file2_values.get(item, {}).get('nominal')
        file2_min = file2_values.get(item, {}).get('min')
        if file1_nom != file2_nom or file1_min != file2_min:
            differences.append({
                'item': item,
                'file1_nominal': file1_nom,
                'file1_min': file1_min,
                'file2_nominal': file2_nom,
                'file2_min': file2_min,
                'nominal_diff': (file1_nom - file2_nom) if file1_nom is not None and file2_nom is not None else None,
                'min_diff': (file1_min - file2_min) if file1_min is not None and file2_min is not None else None
            })
    return differences

def write_differences_to_csv(differences, output_csv_file):
    with open(output_csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['item', 'file1_nominal', 'file1_min', 'file2_nominal', 'file2_min', 'nominal_diff', 'min_diff'])
        writer.writeheader()
        for diff in differences:
            writer.writerow(diff)

def main():
    parser = argparse.ArgumentParser(description='Compare nominal and min values between two types.xml files and output differences to a CSV file.')
    parser.add_argument('file1', help='Path to the first XML file')
    parser.add_argument('file2', help='Path to the second XML file')
    parser.add_argument('output_csv', help='Path to the output CSV file')

    args = parser.parse_args()

    file1_values = extract_nom_min(args.file1)
    file2_values = extract_nom_min(args.file2)
    differences = compare_nom_min(file1_values, file2_values)
    write_differences_to_csv(differences, args.output_csv)

    print(f"Differences written to {args.output_csv}")

if __name__ == "__main__":
    main()
