#!/usr/bin/env python3
"""check_text.py FILE [--absent REGEX]... [--present REGEX]...  : regex assertions on a file (multiline, case-sensitive)."""
import re, sys
f = sys.argv[1]; t = open(f, encoding="utf-8").read(); e = []; mode = None
for a in sys.argv[2:]:
    if a in ("--absent", "--present"): mode = a; continue
    hit = re.search(a, t, re.M)
    if mode == "--absent" and hit: e.append(f"must be absent: {a!r}  (found: {hit.group(0)[:80]!r})")
    if mode == "--present" and not hit: e.append(f"must be present: {a!r}")
if e: print("FAIL", f); [print(" -", x) for x in e]; sys.exit(1)
print("OK", f)
