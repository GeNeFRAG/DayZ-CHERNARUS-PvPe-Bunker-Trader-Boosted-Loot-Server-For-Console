import re

log_file_path = '/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZ/tools/log.txt'

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