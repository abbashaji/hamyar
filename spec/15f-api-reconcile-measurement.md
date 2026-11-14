# 15.E API reconciliation (measurement and remaining parts)

*Spec part 15f · owner cell C-040 · reconciles the `/v1` paths cited by part 13 (measurement) and part 11c (reviewer and operator tools) that S15 (`spec/15a-api-core.md`, `spec/15b-api-admin.md`) does not define. S15 is canonical: no existing S15 id, endpoint, parameter name or state is renamed here. Written against `docs/decisions.md` and Founding Document draft v0.1 (FD). Nothing here is legal advice or has been checked against any provider's terms or any law; every provider-dependent statement stays [V].*

## 15.E.1 Method, verdict codes and sources

For each cited path the surrounding lines of the citing part were read to learn what the screen or process needs, and the endpoint tables of S15 were searched for the nearest existing operation. Verdicts: **(a) ALIAS** (the cited path means an existing S15 operation), **(b) NEW** (defined here in the table format of 15.21.1), **(c) REMOVE** (the cited use must not exist). Five paths came with no line citation in the cell text; they were matched to their rows in the operation table of part 13 (13.10.2, lines 920 to 934), which is where the paths occur. [D]

Ground rules applied to every verdict [D]: member and admin authentication stay separate (`member` under `/v1/*`, `admin` under `/v1/admin/*`, 15.22); no endpoint reads a volunteer's provider page or stores a provider credential, cookie, session or chat content (FD Principle 3; S0 0.7); every write is idempotent (key required, plus the natural idempotency stated per operation); data is minimal (counts, ids, enums, hashes; no member id, no free text about a volunteer); promises say "declared", never "guaranteed"; every number is a formula or a labeled `initial configurable default`.

## 15.E.2 Verdict table

| # | Cited path | Cited at | Verdict | S15 operation or new operation | Section |
| --- | --- | --- | --- | --- | --- |
| 1 | `/v1/admin/calibration-reports` | 13:870, 13:932 | NEW | `createCalibrationReport`, `listCalibrationReports`, `getCalibrationReport` | 15.E.5 |
| 2 | `/v1/admin/calibration-statistics` | 13:931 | ALIAS | `getCalibrationSummary` (`GET /v1/admin/calibration/summary`) | 15.E.3 |
| 3 | `/v1/admin/decision-reports` | 13:926 | NEW | `createDecisionReport`, `listDecisionReports`, `getDecisionReport`, `getDecisionReportContent` | 15.E.6 |
| 4 | `/v1/admin/experiments/{}/balance` | 13:929 | NEW | `getExperimentBalance` | 15.E.7 |
| 5 | `/v1/admin/experiments/{}/registrations` | 13:928 | NEW | `registerExperiment` | 15.E.7 |
| 6 | `/v1/admin/incidents` | 13:933 | NEW | `createIncident`, `listIncidents`, `getIncident`, `updateIncident`, `startIncidentInvestigation`, `resolveIncident` | 15.E.8 |
| 7 | `/v1/admin/interview-coverage` | 13:934 | NEW | `getInterviewCoverage` | 15.E.9 |
| 8 | `/v1/admin/interviews` | 13:934 | NEW | `createInterview` | 15.E.9 |
| 9 | `/v1/admin/metric-snapshots` | 11c:615, 13:51, 13:921 | NEW | `listMetricSnapshots` | 15.E.10 |
| 10 | `/v1/admin/pre-registrations/{}/evaluations` | 13:925 | NEW | `listPreRegistrationEvaluations` | 15.E.10 |
| 11 | `/v1/admin/pre-registrations/{}/lock-approvals` | 13:923 | ALIAS | `lockPreRegistration` then `approveApproval` | 15.E.3 |
| 12 | `/v1/events` | 13:920 | NEW (path changed to `/v1/client-event-batches`) | `recordClientEvents` | 15.E.11 |
| 13 | `/v1/public/pre-registrations/{}/proof` | 13:924 | ALIAS | `getPublicPreRegistration` | 15.E.3 |

No path is verdict (c) as a whole. Two parts of a path are removed inside a (b) or (a) verdict: the public landing-page counter that part 13 routes through `/v1/events` (`ui.landing_viewed`, 15.E.11) and the separate `lock_requested` row state of 13.7.2 (15.E.3 row 11). [D]

## 15.E.3 ALIAS rows

| Cited path | S15 endpoint | Difference, if any |
| --- | --- | --- |
| `GET /v1/admin/calibration-statistics` (13:931) | `getCalibrationSummary`, `GET /v1/admin/calibration/summary` (15.32.3), `perm.calibration.read`, `A-R` | Path and permission name follow S15 (`perm.calibration.read`, not `perm.calibration.record`). Part 13 additionally wants a Wilson interval beside every rate (13.9.2 "the tool displays these widths"), the metric number `CAL-nn` per statistic and a per-service `sufficient` flag. S15 returns percentiles, ppm rates, `meets_min_samples` and `informs`. The S15 object gains the additive optional fields `cal_no`, `ci_low_ppm`, `ci_high_ppm` per statistic (additive in `v1`, 15.13); until it does, the widths are computed by the client from `n_cells` with the 13.5.3 formula [A]. `CAL-06` (input-size fit) needs `input_chars`, which S15's `CalibrationRecord` does not carry: see Issues raised, item 1. |
| `POST /v1/admin/pre-registrations/{prr_id}/lock-approvals` (13:923) | Two calls of S15: `lockPreRegistration` (`POST .../lock`, `2P` `preregistration.lock`, step-up, 15.32.1) by the first admin answers `202` with an `AdminApproval`; `approveApproval` (`POST /v1/admin/approvals/{apv_id}/approvals`, `SU`, `perm.approval.decide`, 15.22.4) by a different admin executes the lock | Part 13 models the pending state as a row status `lock_requested` with `lock_approvals[]` on the pre-registration; S15 keeps the pending state in `AdminApproval` and the row stays `draft` until execution. The S15 model is adopted and `lock_requested` is dropped. S15 does not bind the approvers to the content they approve, which part 13 does with `approved_hash`; this is a gap in 15.32.1, not a feature (Issues raised, item 2): the lock request must carry `content_hash`, the stored approval payload binds it, the execution guards re-check it, and `updatePreRegistration` is refused (`STATE_CONFLICT`, reason `lock_pending`) while an approval is pending. The nine lock guards of 13.7.3 run when the first admin initiates (a failure is `422 VALIDATION_FAILED` with `details.guards`, fail fast per 15.22.4) and again at execution (a failure is `409 STATE_CONFLICT`, reason `guard_failed`, with the same `details.guards`). `chain_hash` (13.7.1) is computed at execution and returned in the `result`. |
| `GET /v1/public/pre-registrations/{prr_id}/proof` (13:924) | `getPublicPreRegistration`, `GET /v1/public/pre-registrations/{prr_id}` (15.33.2), `PUB` | Part 13 wants only `content_hash`, `chain_hash`, `locked_at`, `phase`, `version` and says the change-log entry omits the content (13.7.2). S15 publishes the whole locked `PreRegistration` with its content and `content_hash`, so that anyone can recompute the hash (15.32.1). S15 wins: a separate proof endpoint would be a strict subset of a public record that already exists. Mapping: `phase` is S15 `scope`; `version` is the depth of the `supersedes_id` chain [A]; `chain_hash` is an additive response field of `getPublicPreRegistration` and of `listPublicPreRegistrations`. The recompute rule for `chain_hash` is unchanged from 13.7.1. |

The `content_hash` of S15 is the SHA-256 of the canonical JSON of `{scope, title, thresholds, decision_rules, linked_experiment_ids}` while part 13 hashes its own `content` document (13.7.5). These are two different `PreRegistration` shapes; the reconciliation is Issues raised, item 2, and it blocks the lock and evaluation operations of this part from being implemented as written. [D]

## 15.E.4 Rules for every new operation of this part [D]

Every operation below is under `/v1/admin/*` (scheme `admin`) except `recordClientEvents` (scheme `member`, 15.E.11). They inherit 15.21.1 to 15.21.3 and the pipeline of 15.4 without restating them. In particular: one `AdminAction` row per admin write in the same transaction; `reason` on every write that changes non-draft state; reads that expose member-scoped data are logged as `AdminAction` kind `read`; no response carries a raw IP address, an e-mail address, a `vol_` handle or a provider credential; `Cache-Control: no-store`; universal errors are not repeated in the tables. Rate-limit classes are `A-R` and `A-W` (15.21.2). Permission names follow 15.21.4; the names this part needs that 15.21.4 does not list (`perm.metrics.view`, `perm.metrics.view_small_cells`, `perm.metrics.export`, `perm.incident.record`, `perm.interview.record`) are the names part 13 already uses and are proposed as additions to 15.21.4 (default holders: operator; reviewer for `perm.metrics.view` and `perm.incident.record`) [A]; S10.* owns the matrix. New id prefixes are proposed in Issues raised, item 6.
