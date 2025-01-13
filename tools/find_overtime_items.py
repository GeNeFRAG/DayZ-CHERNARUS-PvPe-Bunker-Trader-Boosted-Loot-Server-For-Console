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
performance_drop_items = set()

for line in log_data:
    overtime_match = re.search(r'Item \[\d+\] causing search overtime: "(.*?)"', line)
    performance_match = re.search(r'LootRespawner\] \(PRIDummy\) :: Item \[\d+\] is hard to place, performance drops: "(.*?)"', line)
    if overtime_match:
        overtime_items.add(overtime_match.group(1))
    if performance_match:
        performance_drop_items.add(performance_match.group(1))

print(f"Number of unique items causing search overtime: {len(overtime_items)}")
print("Unique items causing search overtime:")
for item in overtime_items:
    print(item)

print(f"\nNumber of unique items causing performance drops: {len(performance_drop_items)}")
print("Unique items causing performance drops:")
for item in performance_drop_items:
    print(item)