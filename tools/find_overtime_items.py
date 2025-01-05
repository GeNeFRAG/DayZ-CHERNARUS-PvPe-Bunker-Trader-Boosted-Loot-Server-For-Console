import re

log_file_path = '/Users/gerhard.froehlich/Library/CloudStorage/OneDrive-RaiffeisenBankInternationalGroup/Code/DayZ/tools/DayZServer_X1_x64_2025-01-05_13-40-35.RPT'

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