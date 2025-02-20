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
            'nominal': int(nominal.text) if nominal is not None and nominal.text else None,
            'min': int(min_val.text) if min_val is not None and min_val.text else None
        }
    return nom_min_values

def read_csv_counts(csv_file):
    counts = {}
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            counts[row['item']] = int(row['count'])
    return counts

def compare_and_subtract(xml_values, csv_counts):
    differences = []
    for item, values in xml_values.items():
        if item in csv_counts:
            count = csv_counts[item]
            new_nominal = values['nominal'] - count if values['nominal'] is not None else None
            new_min = values['min'] - count if values['min'] is not None else None
            differences.append({
                'item': item,
                'original_nominal': values['nominal'],
                'original_min': values['min'],
                'count': count,
                'new_nominal': new_nominal,
                'new_min': new_min
            })
    return differences

def write_differences_to_csv(differences, output_csv_file):
    with open(output_csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['item', 'original_nominal', 'original_min', 'count', 'new_nominal', 'new_min'])
        writer.writeheader()
        for diff in differences:
            writer.writerow(diff)

def main():
    parser = argparse.ArgumentParser(description='Compare XML file with CSV file and subtract the nominal and min values by the item count. Output the result to a CSV file.')
    parser.add_argument('xml_file', help='Path to the XML file')
    parser.add_argument('csv_file', help='Path to the CSV file')
    parser.add_argument('output_csv', help='Path to the output CSV file')

    args = parser.parse_args()

    xml_values = extract_nom_min(args.xml_file)
    csv_counts = read_csv_counts(args.csv_file)
    differences = compare_and_subtract(xml_values, csv_counts)
    write_differences_to_csv(differences, args.output_csv)

    print(f"Differences written to {args.output_csv}")

if __name__ == "__main__":
    main()
