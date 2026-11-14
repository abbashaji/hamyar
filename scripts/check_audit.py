#!/usr/bin/env python3
"""Audit log structure: check_audit.py LOG.md. Needs: a 'Checked' section, a findings table, and a final 'Verdict:' line."""
import re, sys
t = open(sys.argv[1], encoding="utf-8").read(); e = []
if len(t.splitlines()) < 30: e.append("log shorter than 30 lines")
if not re.search(r"^##\s+Checked", t, re.M | re.I): e.append("missing '## Checked' section (what was examined and found fine)")
if not re.search(r"^\|.*severity.*\|.*file.*\|.*action.*\|", t, re.M | re.I): e.append("missing findings table with columns severity, file:line, action")
if not re.search(r"^Verdict:\s*(READY|READY WITH LOGGED ITEMS|NOT READY)\b", t, re.M): e.append("missing final 'Verdict: READY | READY WITH LOGGED ITEMS | NOT READY'")
if re.search(r"\b(TODO|FIXME)\b", t): e.append("placeholder text")
if e: print("FAIL", sys.argv[1]); [print(" -", x) for x in e]; sys.exit(1)
print("OK", sys.argv[1])
