# FIX-21: heading and id collisions across S10 and S11

Sources: `docs/audit/A04.md` finding 18, `docs/audit/A10.md` finding 10, `spec/02e-issues-summary.md` B4. Cell C-092. Line numbers below are approximate (about 3 lines either way) because the files drifted; every place was located by its heading text.

## Numbering plan

| File | Old heading range | New heading range | Change |
| --- | --- | --- | --- |
| `spec/10a-*` (identity file) | 10.1..10.19 | 10.1..10.19 | none (not renumbered, as instructed) |
| `spec/10b-safety.md` | 10.11..10.19 | 10.21..10.29 | +10 |
| `spec/11a-volunteer-ux.md` | 11.1..11.29 | unchanged | outside allowed paths |
| `spec/11b-requester-ux.md` | 11.31..11.49 | 11.31..11.49 | none; already inside 11.30..11.49 |
| `spec/11c-admin-tools.md` | 11.41..11.59 | 11.51..11.69 | +10 |
| `spec/11d-i18n-copy.md` | 11.40..11.57 | 11.70..11.87 | +30 |

Result of the plan: no two of the four files share a heading number, and none overlaps 10a (10.1..10.19) or 11a.

## Edits

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E01 10b headings, scope section | spec/10b-safety.md:5 | `## 10.11 Scope, boundaries and how to read this file` | `## 10.21 ...` | applied |
| E02 10b headings 10.12..10.16 and sub-headings 10.11.1..10.11.4 | spec/10b-safety.md:20-600 | 10.11.1..10.11.4, 10.12..10.16 (and their sub-numbers) | 10.21.1..10.21.4, 10.22..10.26 (and their sub-numbers) | applied |
| E03 10b heading, acceptance criteria | spec/10b-safety.md:604 | `## 10.17 Acceptance criteria (Given / When / Then)` | `## 10.27 ...` | applied |
| E04 10b heading, parameters | spec/10b-safety.md:629 | `## 10.18 Parameters, enums and permissions added by this part` | `## 10.28 ...` | applied |
| E05 10b heading, register | spec/10b-safety.md:663 | `## 10.19 Register of unverified items and assumptions` | `## 10.29 ...` | applied |
| E06 10b in-text references to its own sections (`S10.1x`) | spec/10b-safety.md:1-704 | `S10.11`..`S10.19` and their sub-numbers | `S10.21`..`S10.29` | applied |
| E07 10b Issues raised note on heading numbers | spec/10b-safety.md:~700 | heading numbers `10.11`..`10.19` | `10.21`..`10.29` (renumbered by FIX-21 from `10.11`..`10.19`, which collided with the identity file) | applied |
| E08 11c headings, scope through dependencies | spec/11c-admin-tools.md:5-840 | `11.41`..`11.49` and `11.50`..`11.59` with sub-numbers | `11.51`..`11.69` with sub-numbers (11.52.2, 11.54.2, 11.54.3, 11.58.3, 11.62.3, 11.64.2, 11.66.2, 11.66.3 and so on) | applied |
| E09 11c in-text references to its own sections, tool table and notes | spec/11c-admin-tools.md:5-60 and body | `11.4x`/`11.5x` self-references | `11.5x`/`11.6x` self-references | applied |
| E10 11c scope note and ISS-117 item (h) | spec/11c-admin-tools.md:~9, ~850 | sub-headings numbered from `11.41` | sub-headings `11.51` upward (renumbered by FIX-21 from `11.41`) | applied |
| E11 11d headings 11.70..11.87 | spec/11d-i18n-copy.md:5-812 | `11.40`..`11.57` and subheads `11.51.A`..`G` | `11.70`..`11.87` and subheads `11.81.A`..`G` | applied |
| E12 11d self-references in text, tables and acceptance rows | spec/11d-i18n-copy.md:3-828 | `S11.40`..`S11.57` | `S11.70`..`S11.87` | applied |
| E13 11d stale self-reference in `ISS-118` resolution (b), found at read-back | spec/11d-i18n-copy.md:837 | `copy_review_status` (S11.50) | `copy_review_status` (S11.80) | applied |
| E14 11b headings and self-references | spec/11b-requester-ux.md:7-1071 | 11.31..11.49 | 11.31..11.49 | already-applied (already inside its planned range; no reference in 11b points into the renumbered ranges) |
| E15 duplicate `ISS-117`..`ISS-119` block in 11c and 11d | spec/11c-admin-tools.md:~850, spec/11d-i18n-copy.md:836-838 | two different blocks that use the same three ids | unchanged | skipped-needs-owner: the two blocks have different content, so they are not verbatim duplicates and may not be removed; renaming ids is not authorized in this cell. A follow-up cell or C-001 must assign distinct ids (for example by the sub-block rule of S0.4) and re-point references such as `ISS-119` in 11c `AD9` and in 11d S11.71/S11.85. |
| E16 `ISS-117`..`ISS-119` block in `spec/02e-issues-summary.md` (B4) | spec/02e-issues-summary.md | not searched in this cell | not changed | skipped-needs-owner: outside allowed_paths; the follow-up cell must check whether it duplicates one of the blocks above verbatim before removing anything |
| E17 references to the old numbers (`S10.11`..`S10.19` meaning 10b, `S11.41`..`S11.59` meaning 11c, `S11.40`..`S11.57` meaning 11d) in other spec files | files outside allowed_paths | not enumerated in this cell (the only outside reference I saw, `spec/11a-volunteer-ux.md` 11.18 / `ISS-113` cited from 11d, points to 11a and needs no change) | old -> new map: 10.11..10.19 -> 10.21..10.29 (10b only); 11.41..11.59 -> 11.51..11.69 (11c only); 11.40..11.57 -> 11.70..11.87 (11d only) | skipped-needs-owner: a follow-up cell must read the reference sections of the other spec files and apply this map; the same section number can belong to two files in the old numbering, so each hit has to be matched to the file it cites |

Cited text such as `S10.13`, `11.41` quoted as a historical number, and `AC-` ids were left unchanged where they are ids or quotations rather than section pointers.

## Read-back

| edit | what I now see |
| --- | --- |
| E01 | 10b opens with `## 10.21 Scope, boundaries and how to read this file` and its tables point to `S10.22`..`S10.29` |
| E02 | 10b sections run `10.21` to `10.29` in order, with sub-sections `10.21.1`..`10.21.4` |
| E03, E04, E05 | `10.27` acceptance criteria, `10.28` parameters, `10.29` register of unverified items, each in sequence |
| E06 | The 10b scope table and acceptance rows cite `S10.22` to `S10.29`; I saw no `S10.1x` pointer to its own sections |
| E07 | The 10b note says the numbers were `renumbered by FIX-21 from 10.11..10.19` |
| E08 | 11c tool table lists sections `11.55` to `11.66`; the shell and tier sections are `11.52`, with `11.52.1` for roles; the last sections are `11.67` copy keys, `11.68` parameters, `11.69` dependencies |
| E09 | 11c rows cite `11.52.2`, `11.54.3`, `11.54.2`, `11.58.3`, `11.62.3`, `11.64.2`, `11.66.3`; none points into 11.41..11.49 |
| E10 | 11c scope bullet and `ISS-117` item (h) both say `renumbered by FIX-21 from 11.41` |
| E11 | 11d headings read `11.70` through `11.87` with no gap, and `11.81.A` to `11.81.G` under the notices table; the last one is `## 11.87 Requirements on other parts` |
| E12 | Read all 840 lines of 11d in three reads plus the tail: the scope table, decision table, assumptions table and acceptance rows cite only `S11.71`..`S11.87`; no `S11.40`..`S11.57` or `11.40`..`11.57` remains |
| E13 | After the edit the `ISS-118` row reads `copy_review_status` followed by `(S11.80)`, which is the copy system section |
| E14 | 11b starts at `11.31`, ends the numbered sections at `11.49`, and its references point to its own 11.33..11.49 sections and to `ISS-114`..`ISS-116` only |
| E15 | 11c `ISS-117`..`ISS-119` concern admin-tool convention gaps; 11d `ISS-117`..`ISS-119` concern heading numbers, consent records and a minimum age; the two sets are different, so both stay |
| E16, E17 | not read; listed for the follow-up cell |

Result: DONE WITH SKIPS
