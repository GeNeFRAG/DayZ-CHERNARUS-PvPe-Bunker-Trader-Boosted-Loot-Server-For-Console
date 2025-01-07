import re
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Find unique items causing search overtime.')
parser.add_argument('--log_file', type=str, required=True, help='Path to the log file')
args = parser.parse_args()

log_file_path = args.log_file

with open(log_file_path, 'r') as file:
    log_data = file.readlines()

overtime_items = set()

for line in log_data:
    match = re.search(r'Item \[\d+\] causing search overtime: "(.*?)"', line)
    if match:
        overtime_items.add(match.group(1))

print("Unique items causing search overtime:")
for item in overtime_items:
    print(item)