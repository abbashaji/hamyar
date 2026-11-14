#!/usr/bin/env python3
"""Every config-looking parameter name used in spec/*.md must be defined in spec/00-conventions.md or spec/16*.md
(a backticked occurrence in those files counts: a defined name or an alias row).
Usage: check_params.py [--all | --prefix P ...]  (--prefix limits the check to names starting with P)"""
import re, glob, sys
PRE = "credit|price|admission|verify|lease|launch|rate|retention|ui|session|invite|team|referral|analytics|privacy|identity|abuse|appeal|report|calibration|metrics|growth|job|ledger|cell|policy|review|experiment|experiment"
SUF = r"(_s|_days|_ppm|_chars|_ratio|_ttl_s|_max|_min|_cap|_per_\w+|_bytes|_hours|_count|_window\w*|_rate|_pct|_credits|_ms|_cells)$"
files = sorted(glob.glob("spec/*.md")); T = {f: open(f, encoding="utf-8").read() for f in files}
defined = set()
for f in files:
    if f.endswith("00-conventions.md") or "/16" in f:
        defined |= set(re.findall(r"`([a-z_]+(?:\.[a-z0-9_]+)+)`", T[f]))
prefixes = [a for a in sys.argv[1:] if a not in ("--all", "--prefix")]
miss = {}
for f, t in T.items():
    if f.endswith("00-conventions.md") or "/16" in f: continue
    for n in set(re.findall(rf"`((?:{PRE})\.[a-z0-9_.]+)`", t)):
        if re.search(SUF, n) and n not in defined and (not prefixes or any(n.startswith(p) for p in prefixes)):
            miss.setdefault(n, set()).add(f)
if miss:
    print(f"FAIL: {len(miss)} parameter name(s) used but not defined in spec/00-conventions.md or spec/16*.md")
    for n, fs in sorted(miss.items()): print(" -", n, "(" + ", ".join(sorted(x[5:8] for x in fs)) + ")")
    sys.exit(1)
print("OK: all parameter names defined", "(prefixes: " + " ".join(prefixes) + ")" if prefixes else "")
