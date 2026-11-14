#!/usr/bin/env python3
"""Every issue id in the 'Issues raised' tables of the given part files must appear in the register files spec/02*.md
(other than the part itself). Usage: check_issues.py PART.md ...   (no args: all parts)"""
import re, glob, sys
parts = sys.argv[1:] or [f for f in sorted(glob.glob("spec/*.md")) if not re.search(r"spec/02", f)]
reg = "\n".join(open(f, encoding="utf-8").read() for f in glob.glob("spec/02*.md"))
regids = set(re.findall(r"ISS-\d+", reg)); bad = {}
for p in parts:
    if re.search(r"spec/02", p): continue
    for i in re.findall(r"^\|\s*`?(ISS-\d+)`?\s*\|", open(p, encoding="utf-8").read(), re.M):
        if i not in regids: bad.setdefault(p, []).append(i)
if bad:
    print("FAIL: issue ids raised in a part but missing from the register (spec/02*.md)")
    for p, ids in bad.items(): print(" -", p, len(ids), "e.g.", ", ".join(ids[:8]))
    sys.exit(1)
print("OK: register covers", len(parts), "part(s)")
