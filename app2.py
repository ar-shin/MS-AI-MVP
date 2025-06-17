import json

with open("data/sample_projects.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

with open("data/sample_projects_lines.json", "w", encoding="utf-8") as outfile:
    for item in data:
        json.dump(item, outfile, ensure_ascii=False)
        outfile.write("\n")