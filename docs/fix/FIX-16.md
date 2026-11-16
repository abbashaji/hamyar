# FIX-16: 05a entities: columns and keys that 05b and 09 use

Cell C-087. Source: `docs/audit/A05.md` findings 15 to 18, 20, 21, 23 to 27; usage lines in `spec/05b-state-machines.md` (5.21.3, 5.22, 5.23.2, 5.23.3, 5.29.3, 5.29.5, 5.29.6, 5.29.8). Only `spec/05a-entities.md` was edited. Line numbers are those after the edits (the file grew from 1917 to 2017 lines); nothing was executed. Defaults used from `docs/audit/FINAL.md` section 4: none of D-01 to D-22 was needed for an applied edit. Where a name differs between parts, the 05b name is canonical (as the cell says for the ledger keys) and the 05a name is kept as a documented alias; no id, parameter, endpoint or state was renamed.

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E1 catalogue intro counts the additions (A05 #18) | spec/05a-entities.md:150 | "One row per entity of S0.7 (57 rows)" | same sentence plus the two additions of S5.4.1, flagged [A] | applied |
| E2 entity `StateTransition`, table `state_transitions`, prefix `stt_` (A05 #18) | spec/05a-entities.md:213 | no such entity or table in 05a or S0.7 | new S5.4.1 with field table, unique `(entity_type, entity_id, entity_seq)`, indexes, retention by parent class, DDL, needed-by 05b 5.21.3 | applied |
| E3 store `mint_headroom` (alias `mint_budget`) (A05 #18) | spec/05a-entities.md:213 | no table for monthly mint-cap accounting | new S5.4.1 entry: scope month or member_day, `cap_ucr`, `reserved_ucr`, `minted_ucr`, CHECK, two partial unique indexes, retention, DDL, needed-by 05b 5.29.3 and 5.29.6 | applied |
| E4 polymorphic-reference rule lists `StateTransition` (A05 #18) | spec/05a-entities.md:343 | list ends at `ChangeLogEntry` | `StateTransition` added with its two columns | applied |
| E5 Job `closure_reason` gains `cells_exhausted` (A05 #16) | spec/05a-entities.md:594 | five values | six values, note that S0.9.2 lacks it (05b convention addition 4) | applied |
| E6 Job columns `pause_causes`, `state_before_pause`, `pause_started_at`, `paused_total_s`, `held_ucr`, `levy_reserved_ucr`, `quote_id` (A05 #16) | spec/05a-entities.md:619 | none of the seven | seven rows with type, constraint and the 05b transition that needs each; no DDL because `jobs` has none (see E19) | applied |
| E7 Cell `acceptance_deferred_until` (A05 #16), field row, DDL column, CHECK, index `cells_deferred` | spec/05a-entities.md:694 | no column | timestamptz, only in `submitted` or `flagged_for_audit`, partial index for the re-enqueue sweep; DDL near line 1514 | applied |
| E8 Lease `hard_expires_at` (A05 #15), field row and DDL column and CHECK | spec/05a-entities.md:712 | only `expires_at` | NN, `>= expires_at`, alias `grace_until` of S9.* | applied |
| E9 Lease `extensions` canonical, `extensions_used` alias (A05 #15) | spec/05a-entities.md:714 | `extensions_used` | `extensions` with bound `lease.max_extensions`, alias documented; DDL column renamed with an alias comment | applied |
| E10 Lease `release_reason` (A05 #15), field row, DDL column and CHECK | spec/05a-entities.md:718 | only `end_reason` | `declined` or `reported`, only when `released` | applied |
| E11 reaper index on `hard_expires_at` (A05 #15), text and DDL `leases_reaper` | spec/05a-entities.md:720 | index on `expires_at` | index on `hard_expires_at`; DDL at line 1557 | applied |
| E12 ledger transaction key `idempotency_key` canonical, `natural_key` alias (A05 #17), field row, DDL, reference rule 1 | spec/05a-entities.md:894 | `natural_key` | `idempotency_key` (alias `natural_key`); rule 1 at line 341 and DDL near line 1626 follow | applied |
| E13 `ledger_entries.entry_key` UNIQUE (A05 #17), field row and DDL | spec/05a-entities.md:881 | no such column | `<idempotency_key>#<leg>`, NN, unique; separator is a flagged [A] choice | applied |
| E14 closed-member credit uses `reserve_donation` and key `closedonate:<mem_id>` (A05 #23) | spec/05a-entities.md:374 | "through `expire` entries" | one `reserve_donation` transaction; `expire` only for expired lots | applied |
| E15 submission name drift (A05 #21): `elapsed_s` and `output_hash` | spec/05a-entities.md:740 | no mention of 05b names | rows say 05b calls them `time_to_submit_s` and `content_hash`, documented aliases (line 733 for `output_hash`); no rename | applied |
| E16 approvals of a reversal have no database enforcement (A05 #27) | spec/05a-entities.md:899 | "two distinct admins" only | deferred constraint trigger `ledger_transactions_two_admins` described in the field row and as a DDL comment (near line 1637) | applied |
| E17 Cell creation key for primary cells (A05 #20, primary part) | spec/05a-entities.md:698 | silent on the 05b L2 key | text says the partial index is the enforcing form of `UNIQUE (job_id, ordinal, cell_kind)` and why a plain composite key is ineffective | applied |
| E18 creation key for gold, audit, third, review and rework cells (A05 #20, non-primary part) | spec/05a-entities.md:698 | no key | only flagged as an open owner decision; choosing a key shape is a design decision with no default in D-01 to D-22 | skipped-needs-owner |
| E19 DDL for `jobs`, `reservations`, `waitlist_entries`, `audits`, `deliverables` (A05 #25) | spec/05a-entities.md:1380 (S5.14) | prose only | not written: five new tables are not a minimal edit, and the enum lists (`job_type`, `deliverable_format`) are in S0.8 and were not copied here; needs its own cell | skipped-needs-owner |
| E20 boolean columns not starting `is_` or `has_` (A05 #24) | spec/05a-entities.md:S5.7.2 and others | `enabled`, `grants_paused`, `adapter_supports_prefill`, `adapter_copy_only`, `no_training_flag`, `downstream_use_uncontrolled` | unchanged: a rename is not authorized by this cell and the audit says other parts may use the names | skipped-needs-owner |
| E21 `ChangeLogEntry.summary_fa` review marker on an IMM table (A05 #26) | spec/05a-entities.md:S5.12.5 | marker has no column | unchanged: a review column or a sibling table is a design decision with no default | skipped-needs-owner |
| E22 `leases` key `UNIQUE (cell_id, attempt)` against 05b 5.29.5 (found while reading, not in the audit list) | spec/05a-entities.md:1555 | `UNIQUE (cell_id, attempt)` for every lease | unchanged: 05b says a declined, released or revoked lease does not consume an attempt, so one attempt may have several leases and 05b's key is `UNIQUE (cell_id, attempt) WHERE state = 'submitted'`; the 05a key would refuse the second lease after a decline. Not in the authorized list, so only logged | skipped-needs-owner |

## Read-back

Every edited place was read again after the commit.

- E1 (line 150): the intro now says it adds the two entities of S5.4.1, flagged [A].
- E2 (lines 216 to 262): S5.4.1 shows a `StateTransition` field table, "Unique `(entity_type, entity_id, entity_seq)`", two indexes, a retention rule and a DDL block ending in a trigger comment.
- E3 (lines 264 to 285): `mint_headroom` is given with scope, period, member id and three amounts; the DDL shows the CHECK on minted plus reserved against the cap (its two partial unique indexes follow at the end of the block and were not on the lines re-read).
- E4 (line 343): rule 3 now ends with `StateTransition` and its two columns.
- E5 (line 594): the closure_reason row lists `cells_exhausted` and says S0.9.2 lacks it.
- E6 (lines 619 to 625): seven rows are present; for example `held_ucr` reads "`= escrow_ucr` for a member job".
- E7 (line 694, 698): the Cell row reads "non-null only in `submitted` or `flagged_for_audit`"; the index list ends with the deferred-acceptance index; DDL lines 1514 to 1523 show the CHECK and `cells_deferred`.
- E8 (line 712): `hard_expires_at` row present; DDL has the column and `CHECK (hard_expires_at >= expires_at)` (lines 1535 to 1552).
- E9 (line 714): the row is named `extensions` and says `extensions_used` is a documented alias; DDL column carries the comment "alias: extensions_used".
- E10 (line 718): `release_reason` row present; DDL line has the IN list and the CHECK at line 1552.
- E11 (lines 720 and 1557): both say `hard_expires_at`.
- E12 (lines 341, 894): rule 1 and the field row say `idempotency_key` with alias `natural_key`; the DDL line reads "alias: natural_key".
- E13 (lines 881 and 1664): the field row and the DDL line for `entry_key` are present.
- E14 (line 374): the closure sentence now names `reserve_donation` and `closedonate:<mem_id>`.
- E15 (lines 733, 740): both rows name the 05b alias.
- E16 (line 899): the row names the trigger `ledger_transactions_two_admins`; the DDL has the two comment lines before the closing parenthesis.
- E17 (line 698): the Unique sentence now explains the partial index as the form of the 05b key.
- Not re-read after the edit because they were not edited: E18 to E22. The `Not verified` items: `check_fixlog.py` and `check_spec.py` were not run; the DDL is unproven SQL; other uses of `natural_key` or `extensions_used` elsewhere in the file (for example the `ledger_post()` pseudocode of S5.14.6) were not searched and are covered only by the alias notes; S0.7 and the catalogue count in tests were not edited.

Result: DONE WITH SKIPS
