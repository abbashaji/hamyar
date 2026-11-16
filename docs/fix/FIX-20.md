# FIX-20: S0 housekeeping: ranges, retention classes, file table

Cell C-091, base 90003ca. Source: `docs/audit/A15.md` findings 29, 46, 47, 49, 50 and `docs/audit/FINAL.md` section 5.1 (FIX-20). Only `spec/00-conventions.md` was edited. Every file:line below is a line of that file on this cell's branch after the edits (the audit lines were before them and had drifted). Nothing was run.

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| A15 #29: cap `template.min_reviewers_new` | spec/00-conventions.md:771 | validation `1..5` | validation `1..2; 0.9.5`; default 2 unchanged | applied |
| A15 #29: cap `service.min_approvers` | spec/00-conventions.md:769 | validation `1..5` | validation `1..2; 0.9.6`; default 1 unchanged, 2 stays an owner decision | applied |
| A15 #29: cap `appeal.ban_min_reviewers` | spec/00-conventions.md:783 | validation `1..5` | validation `1..2; 0.9.7`; default 2 unchanged | applied |
| A15 #29: counting rule for service approvals (0.9.6 has no second-approval state) | spec/00-conventions.md:495 | guard ended `reviewer recorded` | guard says `service.min_approvers` distinct reviewers have each recorded approval, a count and not a state, service stays `in_review` until reached | applied |
| A15 #50: retention class for request logs | spec/00-conventions.md:176 | `retention.request_log_days` mapped to no class | new class `request_log` mapped to `retention.request_log_days`; contents left to S4.* and S10.* | applied |
| A15 #50: retention class for events | spec/00-conventions.md:177 and :238 | `Event` had class `ops` (`retention.ops_log_days`) | new class `event_raw` mapped to `retention.event_raw_days`; `Event` row now uses it; `spec/05a-entities.md` must follow (not read here, cross-part) | applied |
| A15 #46: S11 file row | spec/00-conventions.md:954 | `spec/11-experiences.md` (does not exist) | `spec/11a-volunteer-ux.md`, `spec/11b-requester-ux.md`, `spec/11c-admin-tools.md`, `spec/11d-i18n-copy.md` | applied |
| A15 #46: added files 02b..02e, 15c..15g, 16b..16d | spec/00-conventions.md:943, :958, :959 | S2 row already `02b-*`..`02f-*` (covers 02e), S15 row `15c-*`..`15g-*`, S16 row `16b-*`..`16d-*` | unchanged | already-applied |
| A15 #46: list `docs/audit` and `docs/fix` | spec/00-conventions.md:970 | not listed anywhere in 0.13 | note bullet naming both folders, no part number, no issue block, no normative text, tagged [A] | applied |
| A15 #47: sub-block rule for parts with more than three files | spec/00-conventions.md:52 and :969 | rule gives three files three ids each; S2, S11, S15, S16 have four to seven files | unchanged: the rule for the fourth and later files is an allocation choice with no default in FINAL section 4 and other parts already use ids their own way (not read here); options for the owner: later files take no ids and cite existing ones, or the block is re-split | skipped-needs-owner |
| A15 #49: `BM2` and the service count | spec/00-conventions.md:924 | `BM2` end state silent on `launch.min_approved_services` before the registry exists | sentence added: before `BM3` the approved-service count is 0, so the S14.* rule cannot pass in `BM2` (fails closed), tagged [A]; S14.* and S17.* still have to say the same | applied |

## Read-back

- Row 1: line 771 now shows the validation cell `1..2; 0.9.5` and default `2 (FD§5.7 failure mode 10)`.
- Row 2: line 769 now shows `1..2; 0.9.6` with the default text `2 is an owner decision [A]` still there.
- Row 3: line 783 now shows `1..2; 0.9.7` and default 2.
- Row 4: line 495, the `service.approved` guard, now ends with the phrase `a count, not a state`, after `TermsCopy saved`.
- Row 5: line 176 is a table row of class `request_log` naming `retention.request_log_days` and S4.* and S10.*.
- Row 6: line 177 is class `event_raw` naming `retention.event_raw_days`; line 238, the `Event` row, now reads `event_raw` in the retention column.
- Row 7: line 954, the S11 row, lists the four files 11a, 11b, 11c, 11d and no `11-experiences`.
- Row 8: lines 943, 958, 959 still show the three globs and are unchanged by this cell.
- Row 9: line 970 is a bullet that names `docs/audit/` and `docs/fix/`, ending `[A]`.
- Row 10: lines 52 and 969 are unchanged; the S15 row at 958 still shows `ISS-151`..`ISS-159`.
- Row 11: line 924, the `BM2` end-state cell, now ends `cannot pass in BM2 [A]`.

Not edited, noticed while reading: `template.min_reviewers_edit` (line 772) is still `1..5` against the same one-step machine; it is not in the authorized list. `spec/16-parameters.md` was not read or edited (outside this cell's paths), so its ranges for the three capped parameters may still say `1..5`.

Result: DONE WITH SKIPS
