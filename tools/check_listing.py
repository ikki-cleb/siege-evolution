"""Checks store/listing.md against the stores' character limits.

    python3 tools/check_listing.py

Each limited field has a "<!-- limit:N -->" line above it, and the long
description sits between "<!-- description -->" markers (4,000 characters).
"""
import re
import sys
from pathlib import Path

text = (Path(__file__).resolve().parent.parent / "store" / "listing.md").read_text()
problems = 0
for limit, line in re.findall(r"<!-- limit:(\d+) -->\n(.+)", text):
    value = line.split(":**", 1)[1].strip() if ":**" in line else line.strip()
    status = "ok" if len(value) <= int(limit) else "TOO LONG"
    problems += status != "ok"
    print(f"{status:8} {len(value):4}/{limit:<4} {value[:60]}")
desc = re.search(r"<!-- description -->\n(.*?)<!-- /description -->", text, re.S).group(1).strip()
status = "ok" if len(desc) <= 4000 else "TOO LONG"
problems += status != "ok"
print(f"{status:8} {len(desc):4}/4000 description")
sys.exit(1 if problems else 0)
