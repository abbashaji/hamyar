# FIX-24: open-decision ids and S3 rows

Cell C-095. Task: `docs/audit/A13.md` findings 2 and 22. Files edited: `spec/19-risks.md`, `spec/03-assumptions.md`. Sources: `spec/02e-issues-summary.md` 2.E.3 (the rows marked `no` and the "Rows to add to S3.2" table), `docs/audit/FINAL.md` section 4 (defaults D-01..D-22), the Founding Document 8.3. No id was renumbered or renamed. New S3 ids `OD-15`..`OD-31` continue the S3 series and exist only in S3. Line numbers are counted by hand from the files after the edits and may be off by a few lines. Nothing was run here; acceptance is run by CI.

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E1 cross-reference table S19 OD-nn / S3 OD-nn / meaning / same decision | spec/19-risks.md:308-327 | Only a prose paragraph (line 306) pairing six ids; no table; S19 ids and S3 ids not mapped one by one | Lead-in with the prefix rule (`S19 OD-nn`, `S3 OD-nn`), a 14-row table (nn, S19 meaning, S3 meaning, same decision and counterpart) and a closing line; the old paragraph is kept and a sentence says it predates `S3 OD-27` | applied |
| E2 same table in S3 | spec/03-assumptions.md:125-146 | no section 3.6; no mapping to S19.9 | new `## 3.6 Cross-reference to S19.9` with the same 14 rows in S3 order | applied |
| E3 prefix rule in S3.1 | spec/03-assumptions.md:7 | "...written `S3.OD-nn` or `S19.OD-nn`. [D]" | same sentence plus: from FIX-24 on prose writes `S3 OD-nn` or `S19 OD-nn`, key in 3.6, no renumbering | applied |
| E4 New 1 (`ISS-44`, `ISS-102` e-mail half) | spec/03-assumptions.md:30 | absent from S3.2 | `OD-15` e-mail purpose; default: in-app notices, e-mail opt-in and never login or recovery; default applied, owner decision open (D-14) | applied |
| E5 New 2 (`ISS-85` (a), (b), (e), `ISS-16` item 2) | spec/03-assumptions.md:31 | absent | `OD-16` quote basis of the verification pool; default max(measured v, `price.v_prior`, v_floor) [A]; default applied, owner decision open (D-04) | applied |
| E6 New 3 (`ISS-71`, `ISS-72`) | spec/03-assumptions.md:32 | absent | `OD-17` approval guard and regional `no`; default: stricter S7 7.10.3 guard, region never blocks; default applied, owner decision open (D-16) | applied |
| E7 New 4 (`ISS-73`) | spec/03-assumptions.md:33 | absent | `OD-18` license pairing for `P2` and `P3`; default: pairing of 02e A9, no such rows in Phases 1 and 2; default applied, owner decision open (D-16) | applied |
| E8 New 5 (`ISS-49`) | spec/03-assumptions.md:34 | absent | `OD-19` human review of the panel repository for G4; default: G4 stays open; default applied, owner decision open (D-16) | applied |
| E9 New 6 (`ISS-66`) | spec/03-assumptions.md:35 | absent | `OD-20` reservation penalty; default: no money, cooldown, one live reservation; default applied, owner decision open (D-09) | applied |
| E10 New 7 (`ISS-105`, `ISS-16107`) | spec/03-assumptions.md:36 | absent | `OD-21` `lease.max_job_share_ratio` value, rounding, visibility; default 0.34, max(1, floor(x x N)), hidden; default applied, owner decision open (D-16) | applied |
| E11 New 8 (`ISS-113`) | spec/03-assumptions.md:37 | absent | `OD-22` when the recovery key is shown; default: after the first accepted cell [H]; default applied, owner decision open (D-18) | applied |
| E12 New 9 (`ISS-115`) | spec/03-assumptions.md:38 | absent | `OD-23` cancelled or failed job accounting; default as in 2.E.3; default applied, owner decision open (D-11) | applied |
| E13 New 10 (`ISS-119`, 11d) | spec/03-assumptions.md:39 | absent | `OD-24` minimum member age [V: counsel]; default `identity.min_age_years` = 0; default applied, owner decision open (D-14) | applied |
| E14 New 11 (`ISS-124`, `ISS-127`) | spec/03-assumptions.md:40 | absent | `OD-25` V3 token and money-moving rewards [V: counsel]; default: V3 descriptive, no reward; default applied, owner decision open (D-15) | applied |
| E15 New 12 (`ISS-179`, `ISS-141`) | spec/03-assumptions.md:41 | absent | `OD-26` pilot size cap and minimum G5 interviews; default: invite supply, no minimum; default applied, owner decision open (D-17) | applied |
| E16 New 13, part (b) alarm owners and reachability test (`ISS-194`, `ISS-197`) | spec/03-assumptions.md:42 | absent | `OD-27` who acts on each alarm, method of the reachability test [V]; default: every tripwire names who acts, test repeated before exposure, join switch `false`; default applied, owner decision open (D-17, D-16) | applied |
| E17 New 13, part (a) the exit rule governs launch, not building (`ISS-171`, `ISS-192`) | spec/03-assumptions.md (no row added) | no S3.2 row | not added: the default of 02e New 13 and FINAL D-17 ("the rule governs launch; the build proceeds") departs from the exit rule of FD 8.3 as written ("Building beyond a throwaway prototype starts only when G0 yields at least one approved service (or a documented fallback) and G1 is complete"); the cell forbids applying an edit that conflicts with the Founding Document | skipped-needs-owner |
| E18 New 14 (`ISS-43`) | spec/03-assumptions.md:43 | absent | `OD-28` ledger store under one serialization point; default: one ledger, one chain, capacity formula and load test; default applied, owner decision open (D-10) | applied |
| E19 New 15 (`ISS-52`) | spec/03-assumptions.md:44 | absent | `OD-29` S5 file names and heading numbers; default: cell path authoritative; default applied, owner decision open (D-22) | applied |
| E20 New 16 (`ISS-16009`, `ISS-16020`) | spec/03-assumptions.md:45 | absent | `OD-30` split of `invite.strike_window_days`, floor on `report.decision_sample_rate`; default: one parameter, no floor; default applied, owner decision open (D-22) | applied |
| E21 New 17 (`ISS-16015`, `ISS-16017`) | spec/03-assumptions.md:46 | absent | `OD-31` value of `abuse.admin_lookup_rate`, name of the two-person approval lifetime; default: no value invented; default applied, owner decision open (D-22) | applied |
| E22 `ISS-56`, `ISS-76` (marked `no` in 2.E.3; 02e prescribes "Extend `OD-09`") | spec/03-assumptions.md:24 | `OD-09` named three costs and ended "the Reserve bears none" | decision cell adds restitution for an overturned rejection or ban and goodwill for a policy change; default cell adds no `appeal_restitution`, donor bears it, `ISS-27` over `ISS-76`; default applied, owner decision open (D-03) | applied |
| E23 rows of 3.5 for the new ids | spec/03-assumptions.md:98-123 | 3.5 lists `OD-01`..`OD-14` only | `OD-17`, `OD-25`, `OD-24`, `OD-27`, `OD-16`, `OD-23`, `OD-26` added to existing rows; 13 rows added for the other needed-before values | applied |

## Notes

- E17 is the only skip. The existing text of the spec already carries the other reading (`ISS-31`, applied; `ASM-26`), so nothing there was changed. `S19 OD-01` therefore has no S3.2 row, and the cross-reference says so. The owner decides whether to record the exit-rule decision in S3.2 and with which default.
- 02e also lists rows "Extend `OD-12`", "Extend `OD-02`" and "Extend `OD-08`". Those decisions are `yes` or `partly` in 2.E.3, not `no`, so they are outside this cell and were not applied. `OD-09` was extended only for `ISS-56` and `ISS-76`, which are `no`.
- `S19 OD-06`, `S19 OD-07` and `S19 OD-09` still have no S3.2 row (A13 finding 22). 2.E.3 lists no row for them, and no default for such a row is in FINAL section 4, so none was added.
- The "Why only the owner" cells of the new rows are the spec author's judgments [A]; where the source marks a legal or provider question they carry [V].
- The `S19.9` statement at line 306 that `S19.OD-01`, `OD-03`, `OD-06`, `OD-07` and `OD-09` have no S3.2 row is kept; E1 adds a sentence saying it is out of date for `OD-03`.

## Read-back

Read after all edits, from the branch.

- E1: `spec/19-risks.md` now shows after the 19.9 table and the old "S3.* by reference" paragraph a paragraph starting "Cross-reference S19 OD-nn and S3 OD-nn", a table with 14 rows (01 to 14; rows 13 and 14 say "none" for S19), and a closing line that `S3 OD-15` to `OD-31` were added. Rows 02, 11 and 12 read "Yes"; 03, 04, 08 and 10 point to `S3 OD-27`, `S3 OD-03` or `S3 OD-05`. The old paragraph is unchanged.
- E2: `spec/03-assumptions.md` has a heading "3.6 Cross-reference to S19.9" before "Issues raised", and the same 14 rows with the S3 meaning first.
- E3: 3.1 first bullet now ends with the sentence "no id is renumbered" and still contains the old `S3.OD-nn` sentence.
- E4 to E16, E18 to E21: 3.2 now has `OD-15` to `OD-31` in the five-column format, one row per id, each ending with a "Needed before" cell. `OD-27` names `S19 OD-03` and `S19 OD-04` and carries no exit-rule text. Every default cell is the default of 2.E.3 or FINAL section 4.
- E17: no row mentions the exit rule of FD 8.3 as an open decision; the table row 01 in 3.6 says "stays with `ISS-31`".
- E22: the `OD-09` row now reads "also whether the Reserve may pay restitution" in the decision cell and "`appeal_restitution`" in the default cell, and still ends "`BM7` acceptance".
- E23: 3.5 now shows `OD-17` in the `G0` row, `OD-25` in the `G1` row, `OD-27` in the "Launch sign-off" row, `OD-16` and `OD-23` in the `BM7` row, `OD-26` in the "Pilot invitations" row, and 13 new rows ending with "Assembly".
- Line counts seen: `spec/19-risks.md` 352 lines (acceptance asks 314), `spec/03-assumptions.md` 161 lines (acceptance asks 102). The acceptance scripts were not run by me.

Result: DONE WITH SKIPS
