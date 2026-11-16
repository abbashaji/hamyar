# FIX-02: parameter table corrections (S16), cell C-073

*Applies the corrections of `spec/16d-parameter-consistency.md` `## Corrections required` that target `spec/16-parameters.md`: CR-01, CR-03, CR-05, CR-09, CR-10, CR-12, CR-15, CR-16, CR-17, CR-18, CR-19, CR-21, CR-22, CR-23, CR-24. CR-02 is not applied (it waits for decision D-07). Method: each cited place was read in the file, the old text was found (no text had to be searched more than a few lines from its cited place), the minimal edit was made with `apply_changes` in two commits, then every edited place was re-read. File lines in the table are the lines in `spec/16-parameters.md` AFTER these edits (the file is now 650 lines; it had 626). Nothing was run. Rows of the launch, change, retention and eta ranges were not touched (FIX-01).*

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| CR-01 | spec/16-parameters.md:462 | `Minimum eta (Reserve inflow versus spend)` | `Minimum round-trip efficiency eta = 1/(1+v+lambda), cells requested per cell contributed` | applied |
| CR-02 | spec/16-parameters.md:92, spec/16-parameters.md:164 | `C13` multiplies `admission.phi_ppm`; `mint.monthly_cap_credits` row derives 4800 from phi | unchanged: default of D-07 is `4,800 unchanged`; no change to `C13`, to the mint-cap rows or to the closing note of 16.7 | skipped-needs-owner |
| CR-03 (min window) | spec/16-parameters.md:204 | `> 0; C7, C9` | `admission.window_step_s .. admission.max_window_days x 86400; C7, C9, S16D-C5` | applied |
| CR-03 (step) | spec/16-parameters.md:206 | `divides 86,400; C9` | `1..86,400, divides 86,400; C9` | applied |
| CR-05 | spec/16-parameters.md:78 | `C2` ends `verify.audit_rate_floor > 0` | `C2` ends `verify.audit_rate_floor > 0; verify.gold_rate_floor > 0` (the S0 0.10.3 `C2` part of CR-05 is outside allowed_paths: left to FIX-03) | applied |
| CR-09 | spec/16-parameters.md:169 | `0.25 (cut applied when the threshold is passed)` | same, then `; the cap after the cut = floor(cap x (1 - ratio))` | applied |
| CR-10 (envelope basis) | spec/16-parameters.md:576 | `FD§3.2 estimate [H]; replaced by CAL` for the four envelope defaults | `[A] initial safe default, no derivation (FD§4.1: measured in Phase 0), replaced by CAL` for 4000, 6000, 32,768; 120 keeps `FD§3.2 estimate [H]` | applied |
| CR-10 (not FD rows) | spec/16-parameters.md:584, spec/16-parameters.md:585 | Mint cap row `derived (16.5)`; Reserve ceiling row `P1M` | `mint.per_member_daily_cap_credits` and `reserve.ceiling_credits` each marked as not an FD§4.9 row | applied |
| CR-10 (last paragraph) | spec/16-parameters.md:588 | FD§4.9 table `not re-read line by line` | states the table (10 rows) was re-read in 16d 16.D.7 and that C-001 still re-checks at assembly | applied |
| CR-12 (public ops) | spec/16-parameters.md:477, spec/16-parameters.md:563 | public exceptions `ops.rpo_s`, `ops.rto_s`, `ops.backup_retention_days` | `ops.purge_interval_s` added in the 16.16 header and in the 16.17.5 list | applied |
| CR-12 (hidden `lease.max_job_share_ratio`) | spec/16-parameters.md:563 | hidden list without it | `lease.max_job_share_ratio` added to the hidden list; owner default D-16 applied (default: ratio 0.34, hidden) | applied |
| CR-12 (hide the three recommended rows) | spec/16-parameters.md:563 | `growth.referral.max_per_day`, `growth.referral.max_per_invite_tree_per_30d` and `grant.max_per_invite_tree_per_day` are not in the hidden list | unchanged: 16d 16.D.6 calls these a recommendation [A] and an owner decision under `SEC`; FINAL section 4 has no default for them (default: stay public as today) | skipped-needs-owner |
| CR-15 | spec/16-parameters.md:400 | `5 reports inside template.autopause_window_s` | `5 reports from distinct reporting members inside template.autopause_window_s [V S9.9.2]` | applied |
| CR-16 | spec/16-parameters.md:492 | `ops.rpo_s` default `300` | `300 [V]: no parameter bounds the log-archive interval; the S4 owner adds one or states 300 s as a target` | applied |
| CR-17 | spec/16-parameters.md:257 | `verify.duplicate_min_chars` validation `1..10000` | `1..10000; >= verify.duplicate_shingle_chars; S16D-C11` | applied |
| CR-18 (intro) | spec/16-parameters.md:73 | `C13`..`C20` are added here | adds that `S16D-C1`..`S16D-C24` are added from 16d 16.D.3 and evaluated like every other constraint | applied |
| CR-18 (relations) | spec/16-parameters.md:100 | 16.3 ends at `C20` | 24 rows `S16D-C1`..`S16D-C24` (lines 100 to 123) with relation and kind as in 16d 16.D.3 | applied |
| CR-18 (worked check) | spec/16-parameters.md:125 | worked check ends `All pass (AC-param-02).` | keeps that sentence and adds the result for `S16D-C1`..`S16D-C24` (22 pass; `S16D-C3` in the arm and `S16D-C21` fail as warnings) | applied |
| CR-18 (AC-param-02) | spec/16-parameters.md:611 | `every constraint of 16.3, and the derived defaults recompute` | counts `S16D-C1`..`S16D-C24` and says the two warning-kind failures are returned and recorded, not refused | applied |
| CR-19 (16.3) | spec/16-parameters.md:73 | no rule for the arm | a relation naming `credit.lifetime_days` is evaluated twice, with the standard and the accelerated lifetime, while `ff.experiment.expiry_arm` is on | applied |
| CR-19 (16.17.2) | spec/16-parameters.md:549 | `Warnings (C8, C13) are returned ...` | same sentence, then the same two-lifetime rule | applied |
| CR-21 | spec/16-parameters.md:185 | `(0,1]; fail-closed floor: 0 would make the alarm unreachable ...` | unchanged: FIX-01 already set the range (`(0,1]` equals `> 0 .. 1`); row not touched; `S16D-C1` is now a row of 16.3 (line 100) | already-applied |
| CR-22 | spec/16c-parameters-b.md 16.C.2 `ui.draft.ttl_s` (outside allowed_paths) | searched all 650 lines of `spec/16-parameters.md` for `ui.draft.ttl_s` and for draft-lifetime text: no such row (16.14 says UI budgets are added by S11 and 16c) | none: the cited row is in `spec/16c-parameters-b.md`, which this cell may not edit (FINAL 5.1 gives it to FIX-04) | skipped-not-found |
| CR-23 | spec/16-parameters.md:489 | `subset of the action names in S10.*` | same, then `; always contains parameter.loosen (S16D-C20)` | applied |
| CR-24 | spec/16-parameters.md:125 | no note on `S16D-C3` | note after the worked check: `S16D-C3` is a warning until S6 confirms whether escrowed credit keeps its lot expiry; owner decision before the PreRegistration lock; owner default D-05 applied (escrow counts toward K, `ff.job.reservations` off for the arm) | applied |

## Read-back

Every edited place was re-read after the second commit. What is there now:

- CR-01, line 462: first cell of the first row of 16.15 now reads as a round-trip efficiency defined as 1/(1+v+lambda); the other cells of the row (`price.eta_alarm_threshold`, FD§4.3, FD§9, 0.80) are unchanged.
- CR-02: line 92 (`C13`) still contains `admission.phi_ppm`; the mint-cap row (line 164) and the 16.7 closing note still derive 4800 from phi. Nothing was edited, as intended.
- CR-03, lines 204 and 206: the min-window validation now begins with the step parameter as its lower bound and ends with `S16D-C5`; the step validation now begins `1..86,400`. The default and other cells of both rows are unchanged.
- CR-05, line 78: `C2` now lists a positive floor for audit and for gold, kind still error.
- CR-09, line 169: the default cell of `inflation.mint_cap_cut_ratio` now carries the floor formula for the cap after the cut; `T↑` and the other cells are unchanged.
- CR-10, lines 576, 584, 585, 588: the envelope row shows the `[A]` basis for the three size defaults and keeps `[H]` for 120; the Mint cap and Reserve ceiling rows say they are not FD§4.9 rows; the closing paragraph now points to 16d 16.D.7 and still leaves assembly to C-001.
- CR-12, lines 477 and 563: the 16.16 header and the 16.17.5 list both name `ops.purge_interval_s` as a public exception; the 16.17.5 hidden list now has `lease.max_job_share_ratio` between `grant.max_per_device` and `growth.referral.max_per_referrer_per_30d`; the three recommended hides are absent.
- CR-15, line 400: the default cell of `template.autopause_report_count` names distinct reporting members and carries `[V S9.9.2]`.
- CR-16, line 492: the default cell of `ops.rpo_s` starts with 300 and then states the missing archive-interval bound as `[V]`.
- CR-17, line 257: the validation of `verify.duplicate_min_chars` now has the shingle lower bound and `S16D-C11`; default 80 unchanged.
- CR-18, lines 73, 100 to 125 and 611: the intro names the 24 new ids; the table has 24 rows from `S16D-C1` to `S16D-C24`, each with three cells; the worked check keeps `All pass` for `C1`..`C20` and adds a separate sentence for the new ids; `AC-param-02` counts them.
- CR-19, lines 73 and 549: both places state that a relation on `credit.lifetime_days` is evaluated for both lifetimes while the arm flag is on.
- CR-21, line 185: the row still shows the range `(0,1]` with the fail-closed note; not edited by this cell.
- CR-22: no edit; `spec/16-parameters.md` has no `ui.draft.ttl_s` row.
- CR-23, line 489: validation of `security.two_person_actions` now ends with the `parameter.loosen` rule and `S16D-C20`; default list unchanged.
- CR-24, line 125: the paragraph after the worked check carries the `S16D-C3` warning note with decision D-05 named as the owner default in use.

## Notes

- Kinds of `S16D-C2` (warning) and `C2` (error, after CR-05) now overlap for the gold floor: 16d gives both and they were copied as written. The owner of S16 may drop `S16D-C2` at assembly.
- `ISS-169` in `## Issues raised` still says the FD§4.9 cross-check was not re-read; it was not edited (history of the issue). CR-10 changes only the 16.18 paragraph.
- The S0 side of CR-05, CR-09 and the other S0 and S16 pairs belongs to FIX-03; the 16b and 16c side (CR-14, CR-22, CR-25) to FIX-04.
- `S16D-C3` and `S16D-C21` fail at the current defaults as warnings (see CR-24 and decision D-13 in FINAL section 4); no default was changed here.

Result: DONE WITH SKIPS
