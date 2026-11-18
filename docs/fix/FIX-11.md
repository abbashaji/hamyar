# FIX-11: apply API reconciliation to part 13 (measurement)

Cell C-082. Edited file: `spec/13-measurement.md` (1031 lines before, 1157 after; nothing deleted). Sources: `spec/15f-api-reconcile-measurement.md` (section "Edits required in citing parts", E1 to E15), `docs/audit/A11.md` finding 4, `docs/audit/A13.md` finding 6, `docs/audit/FINAL.md` sections 3, 4 and 5.1. Lines are as of the branch after the edits; where the pre-edit line differs it is given in brackets. Nothing was executed by this cell.

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E1 | spec/13-measurement.md:997 [873] | report id and SHA-256 attached "as evidence" by the tool | tool returns `report_hash`; operator attaches with S15.27 `perm.launch.evidence` | applied |
| E2 | spec/13-measurement.md:1047 [923] | `POST /v1/events` | `POST /v1/client-event-batches` | applied |
| E3 | spec/13-measurement.md:179 [178] | "A member-scheme batch endpoint accepts" | names `recordClientEvents`, the new path and the 204 rule | applied |
| E4 (REMOVE part: landing counter through the API) | spec/13-measurement.md:172 [171] | landing-page row with no note | row says it is not sent through the API; counted at the front-end host | applied |
| E5 (ALIAS 11) | spec/13-measurement.md:1050 [926] | `approvePreRegistrationLock` on `.../lock-approvals` | `lockPreRegistration`, then `approveApproval`; two-person; `perm.prereg.lock`, `perm.approval.decide` | applied |
| E6 (ALIAS 13) | spec/13-measurement.md:1051 [927] | `getPreRegistrationProof` on `.../proof` | `getPublicPreRegistration` on `/v1/public/pre-registrations/{prr_id}` | applied |
| E7 (REMOVE part: `lock_requested` row status) | spec/13-measurement.md:723 [609] | status enum with `lock_requested` | enum `draft`, `locked`, `abandoned`; a lock in progress is an `AdminApproval`; 13.7.2 rows re-read | applied |
| E8 | spec/13-measurement.md:739 [625] | change-log entry without content, with `phase`, `version` | entry of kind `preregistration_lock` with `scope` and the content | applied |
| E9 | spec/13-measurement.md:1053 [929] | `createDecisionReport` only | four decision-report operations with `perm.metrics.export` or `perm.metrics.view` | applied |
| E10 | spec/13-measurement.md:1054 [930] | `perm.experiment.manage` | `perm.experiment.edit` | applied |
| E11 | spec/13-measurement.md:1055 [931] | start two-person, `perm.experiment.manage` | step-up, two-person start marked open, `perm.experiment.run` | applied |
| E12 (ALIAS 2) | spec/13-measurement.md:1058 [934] | `getCalibrationStatistics`, `perm.calibration.record` | `getCalibrationSummary`, `perm.calibration.read`; proposals path not reconciled | applied |
| E13 | spec/13-measurement.md:1059 [935] | `createCalibrationReport`, `perm.calibration.record` | three report operations, `perm.calibration.write` and `perm.calibration.read` | applied |
| E14 | spec/13-measurement.md:1060 [936] | `PATCH`, `GET /v1/admin/incidents` | six incident operations on collection and item paths | applied |
| E15 | spec/13-measurement.md:1061 [937] | `perm.interview.record` for both | create keeps it, coverage reads with `perm.metrics.view` | applied |
| remove `perm.metrics.view_small_cells` (table row) | spec/13-measurement.md:1048 [924] | `perm.metrics.view`; `perm.metrics.view_small_cells` for `suppressed` values | `perm.metrics.view`; `value` of a `suppressed` row always `null` for every caller (default applied, owner undecided: 15e decision, 15g CR-12) | applied |
| remove `perm.metrics.view_small_cells` (rule `AN-09`) | spec/13-measurement.md:~96 (13.2 table) | rule says the permission shows small cells | unchanged | skipped-needs-owner: not in the authorized list; whether suppressed cells may ever be shown to anyone is not decided with a default in FINAL section 4 (nearest: D-13, D-20); left so that no rule is deleted |
| `listMetricSnapshots` / `?kind=` (13:51, 13:921, 13:925, 13:929, 11c:615) | spec/13-measurement.md | cited paths | now defined by 15.E.10 and 15.E.7 | no edit needed (as 15f says) |
| V1 (A11 #4) | spec/13-measurement.md:~616 (13.6.16) | key `hamyar_growth_v1_*` named in S12, undefined in S13 | `MET-16`: definition, query, cadence, bias note | applied (default applied, owner undecided: window `analysis_window_s` has no default) |
| V2 `day7_return` (A11 #4) | spec/13-measurement.md:~13.6.17 | `hamyar_growth_v2_day7_return_ratio` undefined | `MET-17`: calendar days 1 to 7 after anchor day, ITT, companion exact-day | applied (reading chosen [A], default applied, owner undecided) |
| V3 (A11 #4) | spec/13-measurement.md:~13.6.18 | share-tap ratio and card arrivals undefined | `MET-18` | applied (default applied, owner undecided) |
| V4 (A11 #4, same finding) | spec/13-measurement.md:~13.6.19 | `hamyar_growth_v4_week2_return_ratio` undefined | `MET-19`, ITT, not limited to week-1 contributors | applied (default applied, owner undecided) |
| V5 (A11 #4) | spec/13-measurement.md:~13.6.20 | activation ratio, blocked total, unrecovered credit undefined | `MET-20` | applied (default applied, owner undecided) |
| V6 (A11 #4) | spec/13-measurement.md:~13.6.21 | return after milestone undefined | `MET-21`: first published milestone after assignment per member, ITT | applied (default applied, owner undecided) |
| coverage map | spec/13-measurement.md:~29 | `MET-15` was the last FD row | row for `MET-16` to `MET-21` added | applied |
| seeds TRIP-10, TRIP-11, TRIP-15 (A13 #6) | spec/13-measurement.md:824-834 (13.7.5) | no `thr.*` key for them | keys `thr.exhausted_cell_share_max`, `thr.fast_contribution_share_min`, `thr.copy_paste_error_max`, `thr.active_donors_min`, no initial default; optional `thresholds[].key` | applied (default applied, owner undecided: lock refused while empty) |
| FIX-11 notes | spec/13-measurement.md:~1155 (Issues raised) | no record of these additions | paragraph listing seven additions and open points | applied |

## Read-back

Every edited place was re-read after the last commit. What is there now:

- 13.3.4 row `ui.landing_viewed` (line 172) says the count "comes from aggregate counters at the front-end host"; 13.3.5 (line 179) names `recordClientEvents` and `/v1/client-event-batches`.
- 13.7.1 status row (line 723) lists `draft`, `locked`, `abandoned` and says a lock in progress is an `AdminApproval`; the 13.7.2 table (lines 737 to 739) still has the `lock_requested` rows, which the status row re-reads; line 739 says the entry is of kind `preregistration_lock` and carries "the content".
- 13.7.5 (lines 824 to 834) shows the paragraph and the four-row table of `thr.*` keys with "no initial default".
- 13.9.3 (line 997) says the tool "returns the report id and `report_hash`" and that the operator attaches them.
- 13.10.2 (lines 1047 to 1061): `recordClientEvents` on `/v1/client-event-batches`; `listMetricSnapshots` without the small-cell permission; `lockPreRegistration`, `approveApproval`; `getPublicPreRegistration`; four decision-report operations; `perm.experiment.edit`; `perm.experiment.run`; `getCalibrationSummary`; three report operations; six incident operations; interview coverage under `perm.metrics.view`.
- 13.6.15 starts at line 596 with the shared conventions and the four added views; `MET-16` to `MET-21` follow it, each with a Field/Value table; the SQL blocks were written for `MET-16`, `MET-17`, `MET-18` only.
- `## Issues raised` ends with the FIX-11 paragraph; no `ISS` id was added.

## Notes for the owner and later cells

1. **Conflict inside the 15f contract.** 15f (not an allowed path) still uses `perm.metrics.view_small_cells` in 15.E.4, 15.E.7, 15.E.9 and 15.E.10, and `AN-09` in part 13 still names it. The cell told this edit to remove it from the part 13 table, following 15e and 15g CR-12, so part 13 is now inconsistent with 15f and with `AN-09` until FIX-09 or the owner settles it.
2. **Permissions taken from 15f.** `perm.experiment.edit`, `perm.experiment.run`, `perm.calibration.read`, `perm.calibration.write` and `perm.approval.decide` are quoted from 15f; whether 15.21.4 lists them was not checked here. The list in `ISS-138` was not rewritten.
3. **S16 16.15 needs the same seeds.** The four `thr.*` keys exist only in part 13. `spec/16-parameters.md` 16.15 still has no rows for them, and FIX-02 and FIX-04 do not cover them: a cell that edits S16 must add them.
4. **Not read here.** `docs/source/Hamyar - Founding Document.md`, `docs/source/prompt.md` and `docs/decisions.md` were not read in this cell; conflicts were judged against the ground rules as 15f 15.E.1 states them (no provider-page reading, no credentials, `declared` not `guaranteed`, aggregates only). E8 makes the locked pre-registration content public through the change log, as 15f decides; that was not checked against the Founding Document.
5. **Definitions I chose** (all [A], none an FD figure): the day-7 reading in `MET-17`, the ITT denominators of `MET-17` and `MET-19`, one observation per member in `MET-21`, and `analysis_window_s` as the only window without a default. D-13 and D-15 (default: V3 descriptive) are untouched.
6. **Open for S4.\* and S12.** Whether actor-bearing outbox rows survive until the closing rollup (`mv_share`); S12 guardrails without keys (V2 rendered-false share, V3 reports, V4 small-team share) are not defined; `rendered` is not an allowed dimension in 13.3.4.
7. **Checks.** Acceptance scripts were not run by this cell. `check_params.py` may or may not read the new `thr.*` names in part 13; `check_spec.py --min-lines 979` is met by line count (1157).

Result: DONE WITH SKIPS
