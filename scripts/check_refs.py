#!/usr/bin/env python3
"""Cross-part reference checks. Usage: check_refs.py api|events|all
api: every /v1/... path cited in any part is defined in spec/15a-api-core.md or spec/15b-api-admin.md (path params normalized)."""
import re, glob, sys
T = {f: open(f, encoding="utf-8").read() for f in sorted(glob.glob("spec/*.md"))}
norm = lambda p: re.sub(r"\{[^}]*\}|:[a-z_]+", "{}", p.rstrip("/.,;)`|"))
def paths(t): return set(norm(x) for x in re.findall(r"/v1/[A-Za-z0-9_\-/{}:]+", t))
defined = set()
for f, x in T.items():
    if re.match(r"spec/15", f): defined |= paths(x)
only = [a for a in sys.argv[2:]]
bad = {}
for f, t in T.items():
    if re.match(r"spec/15", f): continue
    if only and f[5:8] not in only and f[5:7] not in only: continue
    for p in paths(t):
        if p.count("{") != p.count("}"): continue
        if p not in defined and not any(d.startswith(p + "/") for d in defined): bad.setdefault(p, []).append(f[5:8])
if bad:
    print(f"FAIL: {len(bad)} API path(s) cited but not defined in S15")
    for p, fs in sorted(bad.items()): print(" -", p, sorted(set(fs)))
    sys.exit(1)
print("OK: all cited API paths are defined in S15 (", len(defined), "paths )")
