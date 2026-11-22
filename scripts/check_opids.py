#!/usr/bin/env python3
"""check_opids.py [--list]: every operation id cited in backticks by a part that is not S15 or a reconciliation file
must be defined as an operation: a table row of 15a/15b with a backticked id and a backticked METHOD /v1 path, or a NEW verdict row
of 15c..15g (id in any backticked cell). Alias table: docs/opid-aliases.txt (one 'cited_id defined_id' pair per line; a defined_id starting with OPEN means 'no S15 operation yet, logged as a known issue in docs/SPEC-STATUS.md') for ids
that a part may keep by decision (D-08)."""
import re, glob, sys, os
T = {f: open(f, encoding="utf-8").read() for f in sorted(glob.glob("spec/*.md"))}
VERBS = "get|list|create|update|delete|put|set|redeem|revoke|approve|reject|withdraw|confirm|close|start|stop|end|lock|unlock|register|replace|export|check|expand|rotate|resolve|release|take|submit|rate|cancel|pause|resume|engage|attach|sign|reopen|change|decide|issue|claim|acknowledge|publish|retire|enroll|link|deny|record|run|add|remove|assign|flag|mark|open|reserve|preview|quote|confirmQuote"
IDRE = re.compile(r"^(?:%s)[A-Z][A-Za-z0-9]+$" % VERBS)
defined = set()
for f, t in T.items():
    n = f[5:8]
    for line in t.splitlines():
        if not line.startswith("|"): continue
        ids = re.findall(r"`([a-z][A-Za-z0-9]+)`", line)
        if n in ("15a", "15b") and re.search(r"`(GET|POST|PUT|PATCH|DELETE) /v1/", line):
            first = line.strip().strip("|").split("|")[0]
            defined |= set(re.findall(r"`([a-z][A-Za-z0-9]+)`", first))
        if re.match(r"15[c-g]", n) and re.search(r"\|\s*\*{0,2}NEW\*{0,2}\s*\|", line): defined |= {i for i in ids if IDRE.match(i)}
alias = {}
if os.path.exists("docs/opid-aliases.txt"):
    for l in open("docs/opid-aliases.txt", encoding="utf-8"):
        p = l.split()
        if len(p) >= 2 and not l.startswith("#"): alias[p[0]] = p[1]
SKIP = re.compile(r"\b(was|renamed|formerly|retired|REMOVE|ALIAS|old id|not an operation|alias)\b", re.I)
bad = {}
for f, t in T.items():
    n = f[5:8]
    if n.startswith("15") or n.startswith("02") or n.startswith("20") or n in ("17 ", "18-"): continue
    for i, line in enumerate(t.splitlines(), 1):
        if SKIP.search(line): continue
        for tok in re.findall(r"`([a-z][A-Za-z0-9]+)`", line):
            if IDRE.match(tok) and tok not in defined and tok not in alias: bad.setdefault(tok, []).append(f"{n}:{i}")
openn = sorted(k for k, v in alias.items() if v.startswith("OPEN"))
if openn: print(f"note: {len(openn)} id(s) logged OPEN (known issues): {', '.join(openn)}")
if "--list" in sys.argv or bad:
    print(f"{'FAIL' if bad else 'OK'}: {len(bad)} operation id(s) cited but not defined ({len(defined)} defined)")
    for k, v in sorted(bad.items()): print(" -", k, v[:4])
    sys.exit(1 if bad else 0)
print(f"OK: every cited operation id is defined ({len(defined)} ids)")
