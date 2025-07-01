import json

AOMid=1
value=93
with open('amp_frequencies.json', 'r') as f:
    current_data = json.load(f)
current_data[AOMid]=[value,AOMid]
with open('amp_frequencies.json', 'w') as f:
    json.dump(current_data, f, indent=3)