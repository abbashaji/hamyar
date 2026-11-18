# FINAL-2b: re-audit round 2, slice B (FIX-10 to FIX-18)

## Checked

Logs read completely: 10 of 10 (FIX-10, FIX-11, FIX-11a, FIX-12, FIX-13, FIX-14, FIX-15, FIX-16, FIX-17, FIX-18). Guessed names FIX-10a, FIX-11b, FIX-12a to FIX-18a do not exist, so no other log numbered 10 to 18 was found. `docs/fix` cannot be listed with the tools of this cell.

Applied edits confirmed in the part files, counted per log row: 183 in total over 8 part files (FIX-10 18, FIX-11 24, FIX-11a 1, FIX-12 24, FIX-13 34, FIX-14 14, FIX-15 16, FIX-16 17, FIX-17 11, FIX-18 24). Each confirmed edit was read in its final text at the place the log names (or within a few lines of it).

- FIX-17, all 11 applied edits (the whole log): E1 `spec/05a-entities.md:107`; E7 `:124`; E2 and E3 `:136-142` (keyed-hash table has no IP row; the counter paragraph says volatile `CounterStore` only); E8 `:359`; E4, E5, E6 `:396-408` (Device table without `creation_ip_hash`; index `(last_seen_day)` only; Not stored lists any IP hash); E9 and E10 `:424`, `:428`; E11 `:432` (edge clearing paragraph).
- FIX-10, `spec/11c-admin-tools.md`: E1 `:618`; E2 `:626`; E3 to E8 `:650-655` (launch paths, evidence without `If-Match`, `signOffGateItem`, `changeLaunchSwitch`, `/launch/status`); E9, E10 `:703-704`; E11 and E12 `:748-752` (only `getMemberAdmin` under the heading 11.65.3); E15 to E17 `:799-801`; E21, E22 `:756-757`.
- FIX-11, `spec/13-measurement.md`: E1 `:997`; E2, E3 `:179`; E4 `:172`; E5 to E15 `:1047-1061` (all operation rows); E7 `:723`; E8 `:739`; V1 to V6 `MET-16` to `MET-21` at `:600-700` with SQL for `MET-16` to `MET-18`; coverage map row `:30`; the four `thr.*` seeds `:820-834`.
- FIX-11a: section 15.E.13 exists at the end of `spec/15f-api-reconcile-measurement.md:233-243` with 8 path rows, none renamed. The 15.E.2 verdict table (13 rows, `:12-30`) already covers the other paths part 13 cites.
- FIX-12, `spec/15a-api-core.md`: CR-04a `:92`; CR-04b `:93`; step 7 lines `:124-126`; rule 1 with `secret_pattern` and the query-parameter rule `:78`; gate matrix rows `:145-146`; `listOfferedCells` drop line `:334`; `createLease` gates `:345-346`; `createReport` subjects `:367,372`; payment bullet `:394`; error catalogue rows ER-01 to ER-08 `:605-635`; paragraph for ER-09 to ER-11 and copy keys; `AC-api-02` `:851`; `AC-auth-01` to `AC-auth-03` `:868-870`.
- FIX-13, `spec/15b-api-admin.md`: wrong-scheme and bootstrap paragraph `:26`; legend `X` `:15`; rule 4 `:49`; `:87` precedence bullet; `X` rows `:94,95,108,171`; `:127` secret handling; `:152` replay rules; `:260-273` four flags and `g0.svc.*`; evidence, sign-off, chunked upload `:409-433`; guard and cascade `:455-464`; `launch_integrity_check` `:517`; `startExperiment` from `registered` `:735`; lock row with `content_hash` `:718`.
- FIX-14: `member.recovery_confirmed` `:1016`; `referral.paid` note `:1022`; `experiment.registered|assigned|exposed` `:986-988`; `service.review_due` cause `:950`; `lockTeam`, `unlockTeam` `:610-611` and events `:963`; `prev_hash`, `entry_hash` `:46`; `blocking_finding` `:296`; `job.cancelled` `:906` and the `closeMember` paragraph below the 15.34.2 table; `job_svc` consumer `:955`; `template_rejection` sentence `:549`; section 15.29.7 with `AC-api-C01`, `AC-api-C02` `:617-690`; `perm.claim.takeover` `:77`.
- FIX-15, `spec/14-launch-gates.md`: `reason_code` enum `:231`; three clauses in `evaluate_switch` `:461-466` and 14.7.2 paragraph `:486`; error mapping `:544` and failure column rows `:549-553`; Commons authoring bullet and seeds bullet `:588-589`; "Admit a member" row `:579`; `AC-launch-03` `:624`; `AC-launch-52` `:634`; Issues raised table `:665-674` (four ids).
- FIX-16, `spec/05a-entities.md`: E1 `:150`; E2 and E3 `:216-285` with DDL; E4 `:343`; E5 `:594`; E6 `:619-625`; E7 `:694` and DDL `:1514-1521`; E8 to E11 `:712-720`, DDL `:1543,1548,1552,1557`; E12 `:894` and DDL; E13 `:881` and DDL `entry_key`; E14 `:373`; E15 `:733,740`; E16 `:899` and the DDL comment; E17 `:698`.
- FIX-18: `spec/10a-identity.md` rows `:32,34,40-42`; `:53`, `:139`, `:162-173`, `:207`, `:234`, `:492`, `:522-524`, `:763`, `:776`; `spec/10b-safety.md:318-319` and `:685`. All 10a text names `secret.email_encryption_key` and `secret.email_lookup_key`, matching 05a `:135-137`.

Risky edits specifically opened: the renamed ids and statuses of FIX-18 (`rotated`, `purpose`, `subject_hash`), the renumbered and moved material of FIX-14 (new 15.29.7 and 11.65.3 reduction), the ids and tables of FIX-16 (`StateTransition`, `mint_headroom`, `entry_key`), the content moved out of 11c by FIX-10 (handle resolution, hand over, `requeue_at_front`), and the 13.7.2 status rewrite of FIX-11.

## Findings

| # | severity | file:line | defect | action |
| --- | --- | --- | --- | --- |
| 1 | minor | n/a | no defect found yet; work in progress | none |

## Not checked

- `spec/05b-state-machines.md`, `spec/09-result-return.md`, `spec/15d`, `spec/15e` and `spec/12-*` were not opened (outside the scope of this slice), so claims about them in the logs (for example FIX-16 E22 on lease keys, the 15e verdict rows, the part 12 team lock) were not re-checked against the source.
- FIX-10 E14 (11.56.3 sentence), FIX-11 closing paragraph of `## Issues raised`, FIX-12 CR-19a/b and CR-31, CR-36a, CR-37 in 15a were seen only in part (CR-19b, CR-36a/b, CR-37 seen; CR-19a and CR-31 not opened), FIX-13 CR-06j, CR-11a to d, CR-11f and CR-32, FIX-14 CR-09 EV-01/EV-03/EV-09/EV-11, CR-38, CR-39, FIX-15 A03 findings 29 and 30 (logged as skipped), FIX-18 edit 14 (`:139` seen, other lines of that sentence not).
- Every row a log marks skipped-needs-owner or skipped-not-found (FIX-10 E18, E23; FIX-11 `AN-09`; FIX-12 CR-15b, CR-29d, CR-01 to CR-03; FIX-13 CR-05c, CR-11g, CR-20e; FIX-14 EV-06, A12 27, CR-42; FIX-15 A03 29 and 30; FIX-16 E18 to E22; FIX-17 S1 to S4; FIX-18 rows 25 to 30) was not worked; only the ones that leave a visible contradiction are in the findings.
- The S15b 15.28.2 kill-switch enum, the full 15.21.4 permission table of `spec/15b-api-admin.md`, the S0 and S16 files and `docs/decisions.md` were not opened (nothing in them was edited by these fixes). The acceptance scripts were not run; CI runs them.
- The rest of each part file outside the cited places was not read, so a leftover use of a renamed id elsewhere in those files (for example `natural_key`, `extensions_used`, `creation_ip_hash`, `secret.email_enc_key`) was not searched for.

Verdict: NOT READY
