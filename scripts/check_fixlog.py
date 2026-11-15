#!/usr/bin/env python3
"""Fix log structure: check_fixlog.py LOG.md. Needs a table with columns edit | file:line | before | after | status
where status is one of applied / already-applied / skipped-needs-owner / skipped-not-found (with a reason); no 'pending'/'todo'; a '## Read-back' section; a final 'Result:' line."""
import re, sys
t = open(sys.argv[1], encoding="utf-8").read(); e = []
if not re.search(r"^\|.*edit.*\|.*file.*\|.*before.*\|.*after.*\|.*status.*\|", t, re.M | re.I): e.append("missing table with columns edit | file:line | before | after | status")
rows = [l for l in t.splitlines() if l.startswith("|") and not re.match(r"^\|\s*(-|edit|#)", l, re.I) and not set(l) <= set("|- :")]
ok = [l for l in rows if re.search(r"\b(applied|already-applied|skipped-needs-owner|skipped-not-found)\b", l)]
if len(ok) < 3: e.append(f"fewer than 3 rows with a valid status ({len(ok)})")
if re.search(r"\b(pending|todo|tbd)\b", t, re.I): e.append("pending/todo/tbd found")
if not re.search(r"^##\s+Read-back", t, re.M | re.I): e.append("missing '## Read-back' section (what you saw when you re-read the edited lines)")
if not re.search(r"^Result:\s*(DONE|DONE WITH SKIPS)\b", t, re.M): e.append("missing final 'Result: DONE' or 'Result: DONE WITH SKIPS'")
if e: print("FAIL", sys.argv[1]); [print(" -", x) for x in e]; sys.exit(1)
print("OK", sys.argv[1], len(ok), "edits")
