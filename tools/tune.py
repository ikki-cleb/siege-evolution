"""Small helper for balance passes: tools/tune.py unit_id key=value ...
Sets stats in tools/content/immune_system.json (units, evolutions or invaders)."""
import json, sys
from pathlib import Path
path = Path(__file__).parent / "content" / "immune_system.json"
data = json.loads(path.read_text())
target, changes = sys.argv[1], sys.argv[2:]
rows = [i for i in data["invaders"]]
for pack in data["packs"]:
    for unit in pack["units"]:
        rows.append(unit)
        rows.extend(unit["evolutions"])
row = next(r for r in rows if r["id"] == target)
for change in changes:
    key, value = change.split("=")
    row[key] = json.loads(value)
text = json.dumps(data, indent=2)
path.write_text(text + "\n")
print(target, changes)
