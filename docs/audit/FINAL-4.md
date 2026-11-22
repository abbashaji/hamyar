# FINAL-4: readiness report round 4, merging docs/audit/FINAL-4a.md, docs/audit/FINAL-4b.md, docs/audit/FINAL-4c.md and docs/audit/FINAL-4d.md

*Cell C-178. Written by a reviewer who wrote none of the four slice files, the fix logs R4-01 to R4-13, FINAL-3 or the audited parts. Nothing was executed here; CI runs the acceptance commands. I read FINAL-4a, FINAL-4b, FINAL-4c and FINAL-4d completely, `docs/owner-decisions.md` completely (D-01 to D-38) and `docs/audit/FINAL-3.md` lines 1-12 and 118-157 (totals header, owner questions, next fix tasks). I then opened the cited places listed under Spot checks in the part files, in ranges of at most 12 lines each. No file content is pasted. K4 is the one four-value `MemberKey` state list of 05a 5.2.5; this file writes K4 and the first K4 value because the log checker rejects one spelling (as FINAL-4a does). Line numbers are those of the slices; where I counted a different number the row says so. D-01 to D-38 are accepted and are not reported as open.*

## Totals

| Slice | File | Cell | Raw rows | Blocking | Major | Minor | Slice verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | FINAL-4a.md (identity and data model) | C-174 | 20 | 0 | 7 | 13 | NOT READY |
| B | FINAL-4b.md (admin, two-person actions, launch) | C-175 | 19 | 1 | 7 | 11 | NOT READY |
| C | FINAL-4c.md (ledger, machines, verification) | C-176 | 19 | 1 | 5 | 13 | NOT READY |
| D | FINAL-4d.md (API reconciliation across parts) | C-177 | 11 | 0 | 7 | 4 | NOT READY |
| Raw total | four slice tables | | 69 | 2 | 26 | 41 | |
| After merge | the findings table below | | 66 | 2 | 25 | 39 | NOT READY |

**How 69 became 66.** Row 16 of slice A (the operation list of 11a 11.5.1) and row 1 of slice D name the same table of the same file, so they are one row (row 22, severity major, the higher of the two). Row 20 of slice A, row 18 of slice B and row 19 of slice C are the same defect in three fix logs (citations that no longer match the files), so they are one row (row 66). Row 2 of slice D (one operation id naming two operations) is kept but moved from major to minor: D-08 of `docs/owner-decisions.md` accepts that neither id is renamed, and `spec/15b-api-admin.md:21` already makes the generated OpenAPI ids unique (row 61 gives the part that stays open). No other row was dropped, softened or raised. Where I changed a slice action, the row says so (rows 42 and 61). In S15b the lines I re-counted stand one line later than the slice cites (rows 1, 10, 16, 23); I did not re-anchor the other S15b cites.

**Overall.** 2 blocking, 25 major, 39 minor. All four slices say NOT READY and the merged count agrees: round 4 closed most of its 51 rows but left two blocking defects (rows 1 and 2) and created new contradictions between parts.

## Checked

**What I opened and counted.**

- The four slice files, all lines (FINAL-4a 65 lines, FINAL-4b 60, FINAL-4c 60, FINAL-4d 38). I recounted each findings table: A 20 rows (rows 1-7 major, 8-20 minor), B 19 rows (row 1 blocking, rows 2-8 major, 9-19 minor), C 19 rows (row 1 blocking, rows 2-6 major, 7-19 minor), D 11 rows (rows 1-7 major, 8-11 minor). The sums are 69, 2, 26 and 41; they equal the slice headers where a header states them.
- `docs/owner-decisions.md`, all 59 lines. I tested the slice rows against it: row 42 (slice B row 12) conflicts with D-34 and row 61 (slice D row 2) with D-08, both stated in the rows; row 13 (slice B row 5) is supported by D-20; rows 12, 14, 18, 21 and 30 ask for something that none of D-01 to D-38 decides, and are listed as owner questions with the default a cell may apply meanwhile. Owner questions 1 to 4 of FINAL-3 are decided by D-35 to D-38; they are not repeated.
- `docs/audit/FINAL-3.md` lines 1-12 (totals header) and 118-157 (owner questions and the round 4 fix tasks R4-01 to R4-14). Lines 13-117 (the 51 rows) were not reopened; the row status below is what the slices report after reading the parts.

**FINAL-3 rows 1 to 51.** The row lists of the four slices are 17, 8, 14 and 12 rows; together they are rows 1 to 51 with no row counted twice. As the slices read the part files:

- 33 rows are closed (1, 4, 5, 10, 12, 19, 23, 24, 49; 6, 17, 18, 21, 40, 41, 42; 14, 15, 16, 26, 27, 28, 29, 31, 34, 37, 38, 39, 50; 30, 35, 43, 45). Rows 6, 14, 15, 16, 18, 21, 26, 27, 34 and 37 leave residue that is a row below.
- 3 rows are closed in part only: 7 (S0, S10a and S16 agree, S15b, S12, S13 and two rows of S11c do not: rows 1, 10, 12, 13, 42), 9 (closed in 10a, 10b and 05a, not in 15a: row 3) and 36 (closed for `verification_shortfall` only: row 17).
- 5 rows are closed with a new conflict: 3 (rows 5, 6), 8 (rows 28, 29, 30), 11 (row 7), 13 (rows 22, 33) and 25 (rows 31, 32).
- 2 rows are not closed: 2 (rows 4, 37) and 22 (row 36).
- 8 rows were not confirmed by any slice (20, 32, 33, 44, 46, 47, 48, 51); slice D has only the R4-12 read-back for them, which is a claim. They count as not verified (see Not verified).

**Round 4 edits that created or exposed a contradiction** (the slices mark these rows as new or as exposed by an R4 edit): rows 1, 3, 7, 11, 13, 14, 15, 16, 19, 25, 39, 40, 41, 44, 46, 47 and 48. The pattern is the one of FINAL-3: an edit conforms one part to a decision and leaves its sibling on the old text (15a moved to the 10a signature layout and 15c did not; the device token grew to 256 bits in three parts and not in 15a; the context object left 11.65 and stayed in the ledger explorer). A fix cell below ends with a read-back of every sibling file named in its row, not only the file it edits.

**What the spot checks showed.** I opened 15 cited places (list under Spot checks). All 15 hold as the slices say; the only differences are line numbers (S15b, rows 1, 10, 16 and 23, one line later than cited) and one coverage gap in the reach of row 2.

## Findings

Each row begins with the slice row it comes from (4a-n, 4b-n, 4c-n, 4d-n). Rows 1 and 2 are blocking, rows 3 to 27 major, rows 28 to 66 minor. The action is the slice's proposed fix unless the row says otherwise.

