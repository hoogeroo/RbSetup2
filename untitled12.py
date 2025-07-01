import json

with open("stages.json", "r") as f:
    stages = json.load(f)

for stage in stages[0][0]:
    print(stage)