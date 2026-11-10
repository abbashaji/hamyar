#!/usr/bin/env python3
"""Structural check for a spec part. Usage:
 check_spec.py FILE [--min-lines N] [--require TEXT]... [--min-tags N]
Fails on missing file, too short, missing required strings, too few evidence tags, or leftover placeholders.
Necessary, not sufficient: it cannot judge content quality."""
import argparse, re, sys
ap = argparse.ArgumentParser()
ap.add_argument("file")
ap.add_argument("--min-lines", type=int, default=120)
ap.add_argument("--require", action="append", default=[])
ap.add_argument("--min-tags", type=int, default=5)
a = ap.parse_args()
try:
    t = open(a.file, encoding="utf-8").read()
except OSError as e:
    print("ERROR cannot read", a.file, e); sys.exit(1)
errs = []
n = len(t.splitlines())
if n < a.min_lines: errs.append(f"{n} lines < {a.min_lines}")
for r in a.require:
    if r not in t: errs.append(f"missing required text: {r!r}")
tags = len(re.findall(r"\[(?:D|H|V|P|A)\]", t))
if tags < a.min_tags: errs.append(f"{tags} evidence tags < {a.min_tags}")
if re.search(r"\b(TODO|FIXME|lorem ipsum|to be written|\.\.\.\s*$)", t, re.I | re.M): errs.append("placeholder text found (TODO/FIXME/lorem/'...' at line end)")
if not re.match(r"#\s+\d+\.|#\s+\S", t): errs.append("file must start with a '# <n>. title' heading")
if re.search(r"\bguarantee[sd]?\b", re.sub(r"never[^.\n]*guarantee[sd]?|not[^.\n]*guarantee[sd]?|no[^.\n]*guarantee[sd]?|NOT[^.\n]*guarantee[sd]?|\"guaranteed\"|`guaranteed`", "", t), re.I):
    errs.append("'guarantee' used outside a prohibition context; user-facing promises must say 'declared' (rephrase, or state it as a banned word)")
if errs:
    print("FAIL", a.file); [print(" -", e) for e in errs]; sys.exit(1)
print("OK", a.file, n, "lines", tags, "tags")
