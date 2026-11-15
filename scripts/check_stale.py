#!/usr/bin/env python3
"""Paths that a reconcile file (spec/15c..15f verdict tables) marks ALIAS or REMOVE must no longer appear in any part file.
Usage: check_stale.py [PART.md ...]  (no args: every spec file except spec/15c..15g)"""
import re, glob, sys
def verdict_rows(text):
    for line in text.splitlines():
        if not line.startswith("|"): continue
        cells = [c.strip().strip("*") for c in line.strip().strip("|").split("|")]
        v = next((c for c in cells if c in ("NEW", "ALIAS", "REMOVE")), None)
        m = re.search(r"`(/v1/[^`\s]+)`", line)
        if v and m: yield m.group(1), v
norm = lambda p: re.sub(r"\{[^}]*\}|:[a-z_]+", "{}", p.rstrip("/.,;)`|"))
stale = {}
for f in sorted(glob.glob("spec/15[c-f]*.md")):
    for pth, v in verdict_rows(open(f, encoding="utf-8").read()):
        if v in ("ALIAS", "REMOVE"): stale[norm(pth)] = (v, f[5:8])
files = sys.argv[1:] or [f for f in sorted(glob.glob("spec/*.md")) if not re.match(r"spec/15[c-g]", f)]
bad = []
for f in files:
    for n, line in enumerate(open(f, encoding="utf-8").read().splitlines(), 1):
        for p in set(norm(x) for x in re.findall(r"/v1/[A-Za-z0-9_\-/{}:]+", line)):
            if p in stale: bad.append((f, n, p, stale[p][0]))
if bad:
    print(f"FAIL: {len(bad)} citation(s) of paths the reconciliation replaced or removed")
    for f, n, p, v in bad[:40]: print(f" - {f}:{n} {p} ({v})")
    sys.exit(1)
print("OK: no stale API path in", len(files), "file(s)")
