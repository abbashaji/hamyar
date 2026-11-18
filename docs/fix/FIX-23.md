# FIX-23: one Experiment machine across S12 and S13

Source: `docs/audit/A11.md` finding 2 (and 14, 15); `docs/audit/FINAL.md` section 5.1 FIX-23. Canonical choice: `S13.8` (the measurement owner). Cell C-094. Nothing was executed; CI runs the acceptance scripts. Lines are those found after reading the cited area (they had drifted).

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E1 precedence paragraph | spec/12-public-growth.md:430 | rule saying S13.8 governs on differences | states S13.8 canonical, its four states, its event names, `ExperimentBlock` blocks; lazy-path and strata sentence kept | applied |
| E2 status states and events | spec/12-public-growth.md:442 | `draft`, `locked`, `running`, `stopped`; `experiment.locked` | `draft`, `registered`, `running`, `stopped`; `experiment.created`, `experiment.registered` | applied |
| E3 `assignment_mode` | spec/12-public-growth.md:448 | `hash_bucket` or `hash_blocked` | `hash_blocked` only (S13.8.4); `hash_bucket` reserved, `VALIDATION_FAILED` (default-pending, owner may re-add a stateless mode to S13.8) | applied |
| E4 `block_size` | spec/12-public-growth.md:450 | required, divisibility rule | derived at `registered` by the S13.8.3 gcd rule, at most 100 | applied |
| E5 `salt` | spec/12-public-growth.md:451 | 128 bits | 32 bytes (256 bits), generated at `draft` (S13.8.1) | applied |
| E6 `pre_registration_id` and immutability sentence | spec/12-public-growth.md:453, :457 | `running` requires lock; "After `locked`" | `registered` requires lock; "After `registered`" | applied |
| E7 evaluation pseudo-code | spec/12-public-growth.md:469 | emits `experiment.assigned` | emits `experiment.member_assigned` | applied |
| E8 assignment creation path | spec/12-public-growth.md:473 | `getFeatures` is the only place assignment is created | `member.created` transaction for new members; lazy at `getFeatures` for existing members (`include_existing`) | applied |
| E9 S12.11.3 mechanism | spec/12-public-growth.md:478-494 | `hash_bucket` and counter-based `hash_blocked`; `bucket_ppm`, `stratum_seq`, `stratum_key` | `ExperimentBlock` permuted blocks with row lock; assignment columns `stratum`, `block_id`, `position_in_block`, `source`; one `experiment.member_assigned` | applied |
| E10 exposure bullet | spec/12-public-growth.md:503 | `experiment.assigned`, `experiment.exposed` | `experiment.member_assigned`, `ui.variant_exposed` (server-side `source` `server`) | applied |
| E11 V1 to V6 event rows | spec/12-public-growth.md:544, :560, :568, :587, :601, :617 | `experiment.assigned`, `experiment.exposed` | `experiment.member_assigned`, `ui.variant_exposed` | applied |
| E12 V2, V3, V5, V6 assignment mode | spec/12-public-growth.md:558, :567, :600, :615 | `hash_bucket` (V2: or `hash_blocked`) | `hash_blocked` | applied |
| E13 12.13.1 event rows | spec/12-public-growth.md:630-632 | `experiment.assigned`, `experiment.exposed`, `experiment.locked`, `experiment.started`, `experiment.stopped` | `experiment.member_assigned`, `ui.variant_exposed`, `experiment.created`, `experiment.registered`, `experiment.started`, `experiment.stopped` | applied |
| E14 AC-exp-01..08 | spec/12-public-growth.md:764-771 | bucket tolerance test, counter blocks, `experiment.assigned`, `locked` | block recomputation, balance below `block_size`, `ExperimentBlock` permutation, `ui.variant_exposed`, `registered` refusals, flag off means `stopped` with salt published; AC-exp-08 unchanged | applied |
| E15 lazy path in 13.8.4 | spec/13-measurement.md:905 | existing members not assigned unless `include_existing` | same, plus lazy assignment at first `getFeatures` by the same block draw | applied |
| E16 stratifier name `cohort_week` (12.11.4, V2, V4, V6) vs `pilot_week` (13.8.1) | spec/12-public-growth.md:497 | `cohort_week` | unchanged: renaming a stratifier is not authorized and S13.8.1 lists no `cohort_week`; also `stratum_key` wording in 12.11.4 | skipped-needs-owner |
| E17 A11 #14 `TH-01` early fail | spec/13-measurement.md:~860 | `min_sample = 3` | unchanged; D-21 default "as written" (default-pending) | already-applied |
| E18 A11 #15 envelope proposal margin | spec/13-measurement.md (envelope proposal, 13.9.4) | `ceil(3 x max_output_chars / 1024) x 1024` | not located within 60 lines of 545-600 (searched 13.6.12 and neighbours); D-21 default "as written" so no change | skipped-not-found |

## Read-back

Re-read after the edits:

- 12:430 now says "`S13.8` (the measurement owner) is canonical" and lists the four states and the event names.
- 12:442 shows status `draft`, `registered`, `running`, `stopped`; 12:448 shows `hash_blocked` as the only mode; 12:450 block size "derived and stored at `registered`"; 12:451 salt "32 bytes (256 bits)"; 12:453 "`registered` requires a locked `PreRegistration`"; 12:457 "After `registered`".
- 12:469 comment reads `experiment.member_assigned once`; 12:473 gives both assignment paths.
- 12:478-494 shows "the open ExperimentBlock ... FOR UPDATE" and columns `block_id`, `position_in_block`; no counter and no bucket remain there.
- 12:503 first bullet names `experiment.member_assigned` and `ui.variant_exposed`.
- V1 to V6 rows (12:544, 560, 568, 587, 601, 617) show the new names; V2, V3, V5, V6 show `hash_blocked`; 12:630-632 table rows show the new events.
- AC-exp-01..08 (12:764-771) read as in the table above; AC-exp-08 reads "`VALIDATION_FAILED`".
- 13:905 item 1 reads "assigned lazily, by the same block draw". 13.8.1 to 13.8.3 were not edited.
- Not re-found: `cohort_week` still appears at 12:497 and in V2, V4, V6 rows (see E16); `stratum_key` still appears in the 12.11.4 text.

## Needed in S0 and S5

Not edited here.

- Experiment states (S0.9, S5): `draft`, `registered`, `running`, `stopped` (terminal). Transitions as 13.8.2: `draft -> registered` (locked PreRegistration lists the code; weights sum 1,000,000; block size at most 100), `registered -> running` (two admins), `running -> stopped` (admin, flag off, or kill switch). No `locked` state.
- Events (S0.9): `experiment.created`, `experiment.registered`, `experiment.started`, `experiment.stopped`, `experiment.member_assigned`, `ui.variant_exposed` (also server-side, `source` `server`), alarm kind `experiment.balance_violated`.
- Entities (S5): `Experiment` (`exp_`), `ExperimentAssignment` (`asg_`; `stratum`, `block_id`, `position_in_block`, `source`), `ExperimentBlock` (`blk_`; `permutation`, `next_position`); salt 32 bytes; `Experiment.unit` `member` or `invite_tree`; `eligibility.include_existing`.
- Decisions: strata name (`pilot_week` or `cohort_week`) and whether a stateless `hash_bucket` mode is wanted for large populations.

Result: DONE WITH SKIPS
