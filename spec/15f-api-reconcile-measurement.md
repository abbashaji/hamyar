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

## 15.E.5 Calibration reports (frozen evidence) [D]

Phase 0 numbers become evidence only when frozen (13.9.3). `getCalibrationSummary` (15.32.3) is a live computation that changes with every new record; a report is its immutable snapshot. `CalibrationReport` (`clr_`, permanent) = `{clr_id, created_at, service_ids: [id<svc>], record_count, first_cal_id, last_cal_id, statistics: [{cal_no, service_id, value, scale, n, ci_low_ppm, ci_high_ppm, sufficient, reason}], snapshot_ids: [id<mts>], report_hash, supersedes_id: id<clr>/null}`. `statistics` are computed over the `CalibrationRecord` rows of 15.32.3 with the formulas of 13.9.2; a statistic whose input field is not recorded is returned with `value: null` and `reason: "input_not_recorded"` and never estimated (Issues raised, item 1). The tool writes each statistic as an internal `MetricSnapshot` (`metric_no = CAL-nn`, `dims.service_id`, 13.5.4). `report_hash` is the SHA-256 of the RFC 8785 canonical JSON of the report without that field and without `clr_id` and `created_at`. A report is immutable; a later report names it in `supersedes_id`. The report is never attached to the launch gate by this operation: the operator attaches `clr_id` and `report_hash` with the launch evidence operation of 15.27 (`perm.launch.evidence`), so that this operation needs no launch permission and the evidence step stays a separate, logged act [D].

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `createCalibrationReport` | `POST /v1/admin/calibration-reports` | `admin` `perm.calibration.write` | `{service_ids?: [id<svc>] (1..20; default: every service with at least one record), supersedes_id?: id<clr>, reason}` | 201 `CalibrationReport`, `Location: /v1/admin/calibration-reports/{clr_id}`; event `+calibration.report_frozen` | `STATE_CONFLICT` (`details.reason`: `no_records`; `supersedes_not_latest`: the named report is already superseded), `ALREADY_EXISTS` (`report_exists`: same service set and same `last_cal_id`; `details.clr_id` names it), `NOT_FOUND` (unknown `service_id` or `supersedes_id`) | req | - | `A-W` |
| `listCalibrationReports` | `GET /v1/admin/calibration-reports` | `admin` `perm.calibration.read` | `?service_id`, `?from`, `?to` | list of `CalibrationReport` without `statistics`, newest first | - | n/a | cursor | `A-R` |
| `getCalibrationReport` | `GET /v1/admin/calibration-reports/{clr_id}` | `admin` `perm.calibration.read` | - | `CalibrationReport` | `NOT_FOUND` | n/a | - | `A-R` |

Idempotency: key required; the natural idempotency underneath is `(sorted service_ids, last_cal_id)`, so a double click or a key reused by mistake never writes two reports for the same data. Records contain sizes, counts and enums only (15.32.3); the report adds no prompt or output text and no account identifier. [D]

## 15.E.6 Decision reports [D]

The decision report of 13.7.7 is a generated document for the founders: locked hash and time, each threshold with observed value, interval, `n` and outcome, each rule outcome, every incident row (type, severity, resolution code), interview coverage, experiment arms and the balance table, `post_lock` and `post_launch_amendment` items under both versions, suppressed cells, and the limits statement of 13.11. It has no recommendation line. `DecisionReport` (`dcr_`, permanent) = `{dcr_id, prereg_id: id<prr>, created_at, source_watermark: ts, window_closed: bool, content_hash, formats: ["json", "markdown"]}`. The API is JSON only (S0 0.11.1), so the content is returned inside a JSON body as `{markdown: string, json: object, content_hash}` with `Content-Type: application/json` and `X-Content-Type-Options: nosniff`; the Operator tools offer it as a download. The report contains no member id and no volunteer identifier by construction (13.7.7); incident `note` text is never included.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `createDecisionReport` | `POST /v1/admin/decision-reports` | `admin` `perm.metrics.export` | `{prereg_id: id<prr>, reason}` | 201 `DecisionReport`, `Location`; event `+decision_report.created` | `NOT_FOUND` (draft or unknown `prereg_id`), `STATE_CONFLICT` (`prereg_not_locked`), `UNPROCESSABLE` (`no_evaluation_yet`: the evaluator of 13.7.7 has not run), `ALREADY_EXISTS` (`report_exists`: same `prereg_id` and same `source_watermark`; `details.dcr_id`) | req | - | `A-W` |
| `listDecisionReports` | `GET /v1/admin/decision-reports` | `admin` `perm.metrics.view` | `?prereg_id` | list of `DecisionReport`, newest first | - | n/a | cursor | `A-R` |
| `getDecisionReport` | `GET /v1/admin/decision-reports/{dcr_id}` | `admin` `perm.metrics.view` | - | `DecisionReport` | `NOT_FOUND` | n/a | - | `A-R` |
| `getDecisionReportContent` | `GET /v1/admin/decision-reports/{dcr_id}/content` | `admin` `perm.metrics.export` | - | 200 `{markdown, json, content_hash}` | `NOT_FOUND` | n/a | - | `A-W` |

An evaluation on a window that is not closed is reported as `inconclusive` (13.7.7 and the failure behavior of 13.10.1); `window_closed` says so. Reading the content is logged as an `AdminAction` of kind `read` because the document names every incident row. [D]

## 15.E.7 Experiment registration and balance [D]

**Registration.** Part 13 inserts a step `registered` between `draft` and `running` (13.8.2): it freezes arms, weights, the value of `fraction_source` and the stored `block_size`, and requires a locked pre-registration that lists the experiment. S15 has `draft`, `running`, `stopped` and freezes everything at `startExperiment`. The registration step is kept, because freezing only at start leaves arms, weights and the fraction editable between the lock and the first assignment, which is exactly the window a pre-registration exists to close [D]. `Experiment.status` gains the value `registered` (a new response enum value, additive in `v1`, 15.13); `startExperiment` then requires `registered` instead of `draft` and no longer re-reads `fraction_source`. Edits to 15.32.2 are listed in Issues raised, item 3.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `registerExperiment` | `POST /v1/admin/experiments/{exp_id}/registrations` | `admin` `SU` `perm.experiment.run` | `{reason}` | 200 `Experiment` (`status: registered`, arms and `fraction_source` value frozen, `block_size`, `warnings: [string]`); event `experiment.registered` | `NOT_FOUND`, `STATE_CONFLICT` (not `draft`), `UNPROCESSABLE` (`prereg_not_locked`: `prereg_id` must name a locked `PreRegistration` that lists this experiment), `VALIDATION_FAILED` (`details.reason`: `fractions_sum`, `block_size_over_limit`, `override_invalid`) | req | - | `A-W` |

`block_size = sum(fraction_ppm_i / g)` with `g` the greatest common divisor of the arm `fraction_ppm` values (13.8.3, where part 13 calls it `weight_ppm`; the S15 name wins); it is refused above 100 (hard cap [A]) and a `warnings` entry `block_size_exceeds_smallest_stratum` is returned when it exceeds the expected size of the smallest stratum. Every override is validated against the target parameter, including the cross-checks of S0 10.5 (for example C4); only parameters with `experiment_overridable = true` may be overridden. Idempotency: key required; registering a registered experiment with a new key is `409 STATE_CONFLICT` (`details.state = registered`); the stored response replays for the same key. No endpoint lists which member is in which arm (15.32.2). [D]

**Balance.** `getExperimentBalance` exposes the daily balance check of 13.8.4 step 6 as counts only.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `getExperimentBalance` | `GET /v1/admin/experiments/{exp_id}/balance` | `admin` `perm.metrics.view` (`perm.metrics.view_small_cells` for suppressed cells; each such use is logged as a read action) | - | 200 `{experiment_id, as_of, block_size, balanced: bool/null, strata: [{stratum, n_total: int/null, arms: [{arm_key, fraction_ppm, n: int/null}], balanced: bool/null, suppressed: bool}], covariates: [{dim (locale, pilot_week, invite_depth), by_arm: [{arm_key, buckets: [{value, n: int/null}]}]}]}` | `NOT_FOUND`, `STATE_CONFLICT` (`not_registered`: no assignments exist before `running`) | n/a | - | `A-R` |

`balanced` is computed from the unsuppressed counts inside the trust boundary and is true when, in every stratum, `abs(n_arm * 1,000,000 - n_total * fraction_ppm) < block_size * 1,000,000`; it is `null` only before the first assignment. A cell below `analytics.min_cohort_k` is `null` with `suppressed: true` (AN-06) and the next-smallest sibling is suppressed too (AN-07); `balanced` stays visible so that a defect is never hidden by suppression. With 30 to 50 members most strata fall under `k`; that is intended (13.11) [A]. No member id, no per-member arm and no covariate value of one member appears. [D]

## 15.E.8 Incidents [D]

S15 has `Alarm` (15.29.4, an operator notification) and `Report` (15.29.3, a member-filed record). Neither is the `Incident` of 13.4.3, which is a typed record that feeds decision rule (c) of FD§9 ("unresolved safety or provider incident"): it has an enumerated type, severity, status and resolution code and is reported row by row in the decision report. Mapping an incident onto an alarm would lose the typing; an `Alarm` is raised by the creation of a `critical` incident or of any `safety_incident` (13.6.13), with kind `incident.safety_or_critical` in category `ops` [A]. `Incident` (`inc_`, permanent) = `{inc_id, incident_type, severity, status, source, source_ref: {kind: "submission"/"report"/"service"/"job", id: string}/null, occurred_at, resolved_at, resolution_code, note, row_version, created_at}`; `ETag` = `row_version`. `incident_type`: `policy_violation`, `injection_attempt`, `abuse_flag`, `provider_warning`, `provider_account_problem`, `safety_incident`; `severity`: `info`, `minor`, `major`, `critical`; `status`: `open`, `investigating`, `resolved`; `resolution_code`: `no_action`, `parameter_changed`, `template_paused`, `service_suspended`, `member_actioned`, `provider_contacted`, `other`; `source`: `auto` or `manual`. This API only creates `manual` rows; `auto` rows are written by the system rules of 13.4.3. `source_ref` holds opaque non-member ids only (S0 0.7); a `mem_`, `vol_` or `dev_` id in it is `400 VALIDATION_FAILED`. `note` is at most 2,000 characters, reviewer-written, and the form says it must not hold names or text of a volunteer's page; the server cannot check that [H] and purges it `retention.moderation_days` after resolution (13.10.1).

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `createIncident` | `POST /v1/admin/incidents` | `admin` `perm.incident.record` | `{incident_type, severity, occurred_at: ts, source_ref?, note?}` | 201 `Incident` (`open`, `source: manual`), `Location`, `ETag`; event `incident.recorded`; a critical or `safety_incident` row also raises the alarm above | `VALIDATION_FAILED` (`occurred_at` in the future; `mem_`-like id in `source_ref`) | req | - | `A-W` |
| `listIncidents` | `GET /v1/admin/incidents` | `admin` `perm.metrics.view` | `?status`, `?incident_type`, `?severity`, `?unresolved_safety_or_provider=true` (the predicate of 13.4.3) | list of `Incident` without `note`, newest first by `occurred_at` | - | n/a | cursor | `A-R` |
| `getIncident` | `GET /v1/admin/incidents/{inc_id}` | `admin` `perm.metrics.view` | - | `Incident` with `note`, `ETag` | `NOT_FOUND` | n/a | - | `A-R` |
| `updateIncident` | `PATCH /v1/admin/incidents/{inc_id}` | `admin` `perm.incident.record` | Merge Patch `{severity?, note?}`; `If-Match` | 200 `Incident` | `STATE_CONFLICT` (`incident_resolved`), `PRECONDITION_FAILED` | req | - | `A-W` |
| `startIncidentInvestigation` | `POST /v1/admin/incidents/{inc_id}/investigations` | `admin` `perm.incident.record` | `{}` | 200 `Incident` (`investigating`); no domain event (13.4.3 names two), one `AdminAction` | `STATE_CONFLICT` (not `open`) | req | - | `A-W` |
| `resolveIncident` | `POST /v1/admin/incidents/{inc_id}/resolutions` | `admin` `perm.incident.record` | `{resolution_code, reason}` | 200 `Incident` (`resolved`, `resolved_at`); event `incident.resolved` | `STATE_CONFLICT` (already `resolved`) | req | - | `A-W` |

`PATCH` never changes `status`, `incident_type`, `source` or `resolution_code`; state changes are the two commands. A resolved row is immutable except that `note` becomes `null` at purge. Cited by part 13 as `PATCH /v1/admin/incidents`, a collection path that cannot carry a patch; the item path above replaces it. Idempotency: key required on every write; `resolveIncident` and `startIncidentInvestigation` are monotonic, so a replay with the same key returns the stored result and a repeat with a new key is `409`. Provider warnings and account problems enter only through this operation or a member report; the system never reads a provider page to create them (ground rule 2). [D]

## 15.E.9 Interviews and interview coverage [D]

FD§9 asks for 8 to 10 qualitative interviews including reasons for stopping. The platform tracks that they happened, not what was said (13.6.14): no name, no quote, no recording, no link to a `mem_` id. S15 has no such resource, and it is a real capability, so it is NEW. `Interview` (`ivw_`, permanent) = `{ivw_id, segment, held_on: date, stop_reason_codes: [enum], theme_codes: [text<40>], notes_ref: text<200>/null, corrects_id: id<ivw>/null, created_at}`; `segment`: `active_donor`, `stopped_donor`, `requester`, `never_started`, `reviewer_or_operator`; `stop_reason_codes`: `too_slow`, `too_many_rejections`, `unclear_task`, `service_limit_or_warning`, `safety_concern`, `no_work_available`, `credit_expired`, `lost_interest`, `other`; each `theme_codes` entry matches `^[a-z][a-z0-9_]{2,39}$`. Rows are immutable; a wrong row is corrected by a new row with `corrects_id` (the pattern of `CalibrationRecord`, 15.32.3 [A]) and coverage counts a corrected row once.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `createInterview` | `POST /v1/admin/interviews` | `admin` `perm.interview.record` | `{segment, held_on: date, consent_recorded: true, stop_reason_codes, theme_codes, notes_ref?, corrects_id?}` | 201 `Interview`, `Location`; event `interview.recorded` | `VALIDATION_FAILED` (`details.reason`: `consent_not_recorded` when `consent_recorded` is not `true`; `held_on` in the future; `stop_reason_codes` not empty for `active_donor`; any field naming a person or a member is `unknown_field`), `NOT_FOUND` (`corrects_id`) | req | - | `A-W` |
| `getInterviewCoverage` | `GET /v1/admin/interview-coverage` | `admin` `perm.metrics.view` (`perm.metrics.view_small_cells` for suppressed counts, logged) | - | 200 `{as_of, total: int, by_segment: [{segment, count: int/null, suppressed: bool}], stop_reasons: [{code, count: int/null, suppressed: bool}], has_stopped_donor: bool, target: {min: int, max: int}/null, within_target: bool/null}` | - | n/a | - | `A-R` |

`consent_recorded` is a required field that must be `true`, so a row cannot exist without the interviewee's consent to coded notes (`AN-11`); the API cannot verify the consent, only that the interviewer asserted it [H]. `total` is shown; a split below `analytics.min_cohort_k` is `null` with `suppressed: true`, so at the planned scale (8 to 10 interviews) the splits are hidden unless the caller holds `perm.metrics.view_small_cells`, which writes a read action (AN-09). `has_stopped_donor` is never suppressed: without a `stopped_donor` interview the reasons for stopping cannot be reported (13.6.14). `target` is read from the effective pre-registration when it carries a qualitative plan (8 to 10, FD§9) and is `null` otherwise [A]. Idempotency: key required; there is no natural key, so a replay is the only protection against a double row. [D]

## 15.E.10 Metric snapshots and pre-registration evaluations [D]

S15 publishes `getPublicMetrics` and `listPublicMetricSnapshots` (15.33.2) for the published bundle and `getCapacitySnapshot` (15.31) for live capacity; it has no admin read of the internal metric rows that part 13 writes (`MET-nn`, `CAL-nn`, `EXP-nn.<outcome>`, `PRR.<prr_id>.<id>`). Aggregates only: no operation here returns a row about one member (AN-03).

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listMetricSnapshots` | `GET /v1/admin/metric-snapshots` | `admin` `perm.metrics.view` (`perm.metrics.view_small_cells` to see values of `suppressed` rows; each such use is logged as a read action, AN-09) | `?kind` (`met`, `cal`, `exp`, `prr`: the family of `metric_no`, the `?kind=` of 11c:615), `?metric_no` (exact, or a prefix ending in `.` such as `PRR.prr_01j9...`), `?visibility` (`internal`, `public`), `?population` (`all`, `external`), `?from`, `?to` (bounds on `window_end`), `?latest=true` (newest row per `metric_no` and `dims_hash`) | list of `MetricSnapshot` as defined in 13.5.4, newest `window_end` first; `value` is `null` where `suppressed` or `no_data` | `VALIDATION_FAILED` (`kind` and `metric_no` family disagree; `from` after `to`) | n/a | cursor | `A-R` |
| `listPreRegistrationEvaluations` | `GET /v1/admin/pre-registrations/{prr_id}/evaluations` | `admin` `perm.metrics.view` | `?latest=true` | list of `Evaluation` = `{evaluated_at, source_watermark, window_closed: bool, thresholds: [{id, metric_no, outcome (pass, fail, inconclusive), observed_value, n_obs, ci_low_ppm, ci_high_ppm, locked_value, live_parameter_value/null}], rules: [{id, outcome (proceed, do_not_proceed, inconclusive)}], snapshot_ids: [id<mts>]}`, newest first | `NOT_FOUND` (draft or unknown `prr_id`) | n/a | cursor | `A-R` |

`Evaluation` is a decoded view of the `PRR.<prr_id>.<TH-id>` and `PRR.<prr_id>.<DR-id>` snapshot rows of 13.7.7 (value 0 `fail`, 1 `pass`, 2 `inconclusive`); it adds no data and no write path, because the evaluator is a scheduled job (`metrics.prereg_evaluator`, 13.10.1) and a person cannot trigger an evaluation or change its result. `live_parameter_value` is present only where the live value of a `parameter_ref` differs from the locked one (the drift printing of 13.7.7). The `MetricSnapshot` of 13.5.4 is one row per metric, window and dims; the `MetricSnapshot` of 15.33.4 is a published bundle for a period. The public bundle is a projection of the rows with `visibility = public` (Issues raised, item 5). [D][A]

## 15.E.11 Client interaction events [D][A]

Part 13 needs the moments between a card being opened and the result being pasted back to measure time per contribution (`MET-08`) and comprehension friction. It cites `POST /v1/events`. That path is not defined in S15, and the word "events" there already means the domain-event outbox of 15.34, so the path is changed and the operation id is kept.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `recordClientEvents` | `POST /v1/client-event-batches` | `member` | `{events: [ClientEvent]}`, 1 to 50 items, body at most `api.max_body_bytes` | 204, always, when the envelope is valid | `VALIDATION_FAILED` (an event does not match the schema of its `name`; unknown field; more than 50 events), `PAYLOAD_TOO_LARGE` | O | - | `RL-WRITE` |

```
ClientEvent { name: "ui.card_opened"/"ui.prompt_expanded"/"ui.prompt_copied"/"ui.service_opened"/"ui.paste_started"/"ui.variant_exposed",
              lease_id?: id<lse>, service_id?: id<svc>, experiment_code?: text<10>, arm_key?: text<40>,
              device_class?: "phone"/"tablet"/"desktop", locale?: "fa"/"en" }      required fields per name: 13.3.4
```

Rules [D]: (1) there is no client clock value in any field; the server stamps `occurred_at` (15.3 rule 3). (2) The server drops, without any error, an event whose `lease_id` is not a lease of the caller, whose `service_id` does not match the lease, a `ui.variant_exposed` whose `arm_key` is not the caller's logged assignment, a second row of any `ui.*` name except `ui.card_opened` for the same lease (13.3.5), and every event of a batch when `analytics.client_events_enabled` or the member's own setting is `false`; the always-`204` answer therefore confirms nothing about which events were kept or whether a lease exists. (3) It never changes a ledger entry, a lease, a cell or a verdict (loss of an event never blocks the UI). (4) Accepting `ui.card_opened` also writes `leases.last_card_opened_at` (13.10.1). (5) No event carries free text, a prompt, an output, a URL or clipboard content, and `ui.prompt_copied` and `ui.service_opened` record that a button was pressed, never what a provider page shows. (6) The anonymous page-load count `ui.landing_viewed` has no endpoint: a public write path would be a new unauthenticated surface that S15 does not have (15.33.1 makes public endpoints read-only apart from verification), so that count comes from aggregate counters at the front-end host, outside the API [A]. Idempotency: the key is optional; a replay with the same key returns the stored `204`, and without a key the deduplication of rule (2) makes a repeat harmless. Domain events: none; the analytics projector writes `events` rows from this input (13.3.5). Members who disabled client events send nothing, and the client reads that switch from the member setting proposed in Issues raised, item 4. The residual risk that a `lease_id` in a raw `events` row can be joined to a member inside the trust boundary for `retention.event_raw_days` is a trade-off, not a guarantee of unlinkability [V: privacy and legal review before launch].

## 15.E.12 Acceptance scenarios [D]

- `AC-api-rec-01` Given three `CalibrationRecord` rows exist for one service, When an operator calls `createCalibrationReport` and then calls it again with a new `Idempotency-Key` and no new records, Then the first answers `201` with a `report_hash` and the second `409 ALREADY_EXISTS` with `details.reason` = `report_exists` and `details.clr_id` equal to the first.
- `AC-api-rec-02` Given a locked `PreRegistration` whose evaluator has run once, When `createDecisionReport` is called, Then `201`, `content` contains every threshold outcome and no member id; and for a draft `prereg_id` the answer is `404 NOT_FOUND`.
- `AC-api-rec-03` Given an experiment in `draft` whose `prereg_id` names a locked pre-registration, When `registerExperiment` is called with a valid step-up, Then the status is `registered`, `block_size` is stored, and a later `PATCH` of its arms is `409 STATE_CONFLICT`.
- `AC-api-rec-04` Given a running experiment with 12 assigned members and `analytics.min_cohort_k` = 10 in three strata, When `getExperimentBalance` is called without `perm.metrics.view_small_cells`, Then every stratum cell below 10 is `null` with `suppressed: true` and `balanced` is still `true` or `false`.
- `AC-api-rec-05` Given an open `safety_incident` exists, When `listIncidents` is called with `unresolved_safety_or_provider=true`, Then it is listed without `note`; after `resolveIncident` it no longer is, and `incident.resolved` was emitted once.
- `AC-api-rec-06` Given `consent_recorded` is `false`, When `createInterview` is called, Then `400 VALIDATION_FAILED` with `details.reason` = `consent_not_recorded` and no row is written.
- `AC-api-rec-07` Given 2 interviews held and `analytics.min_cohort_k` = 10, When `getInterviewCoverage` is called by a caller without `perm.metrics.view_small_cells`, Then `total` is 2, every `count` of a split is `null` and `has_stopped_donor` is a boolean.
- `AC-api-rec-08` Given snapshot rows for `MET-06` and `CAL-01` exist, When `listMetricSnapshots` is called with `kind=cal`, Then only `CAL-nn` rows are returned and no row contains a `mem_` id.
- `AC-api-rec-09` Given the evaluator ran with `window_closed` false, When `listPreRegistrationEvaluations` is called with `latest=true`, Then every threshold outcome is `inconclusive` and `window_closed` is `false`.
- `AC-api-rec-10` Given a member holds lease A and another member holds lease B, When the first sends a batch with `ui.card_opened` for A and for B, Then the answer is `204` in both cases and only the event for A is projected.

## Issues raised

1. **`CalibrationRecord` shape.** 15.32.3 stores one aggregate row per observation day (`cells_attempted`, `cells_completed`, `seconds_per_cell` array, counts); part 13.9.1 stores one row per run (`kind`, `account_label`, `input_chars`, `output_chars`, `result`, `auto_check_passed`, `copy_paste_error_kind`, `probe_kind`, `canary_script`, nullable `service_id` for clipboard probes). `CAL-06` and the probe statistics cannot be computed from the S15 row. Needed: either S15 adds these as optional fields (additive) or part 13 reduces the tool. Not decided here. Also `createCalibrationRecords` (13:930) is `createCalibrationRecord` in S15 and its permission is `perm.calibration.write`; that row is outside this cell's list and is not edited below.
2. **`PreRegistration` shape and lock binding.** 15.32.1 and 13.7 define two different objects (S15: `scope`, `thresholds` with `measure_key`/`window_days`, `decision_rules` with `if`/`then`, `supersedes_id`, status `draft`/`locked`; part 13: `phase`, `content` with `study`, `measures`, `thresholds` with `TH-nn`, `min_sample`, `decision_rules` with a three-valued `expr`, `amends_id`, `version`, `chain_hash`, status with `lock_requested` and `abandoned`) and two different `content_hash` inputs. Proposed: S15 carries part 13's `content` document as one field, hashed once, with `scope` = `phase`. Separately, 15.32.1 does not bind the second approver to the content: add `content_hash` to the `lockPreRegistration` request and re-check it at execution, and refuse `updatePreRegistration` while an approval is pending.
3. **Experiment.** 15.32.2 needs the status value `registered`, `startExperiment` requiring it and no longer re-reading `fraction_source`, and a `block_size_over_limit` validation. Part 13.8.2 makes start a two-person action (`experiment.start` in `security.two_person_actions`); 15.32.2 makes it step-up only. Part 13 fields `unit`, `strata`, `eligibility`, `salt`, `weight_ppm`, `parameter_overrides` have no S15 counterpart (`fraction_ppm`, `config`); S15 names win and the mapping is for the cell that reconciles 13.8.
4. **Client events setting.** `Member` and `updateMe` (15.5) have no `client_events_enabled`, and `getFeatures` (15.8) carries no analytics switch, so a client cannot know whether to send. Proposed additive: `Member.client_events_enabled: bool` (initial configurable default `true` [A], to be reviewed for high-risk members [V]) and the global parameter reflected in `getFeatures`.
5. **`MetricSnapshot` is two objects** (13.5.4 row, 15.33.4 bundle) with one prefix `mts_`.
6. **Convention additions of this part:** id prefixes `clr_` and `dcr_`; permissions `perm.metrics.view`, `perm.metrics.view_small_cells`, `perm.metrics.export`, `perm.incident.record`, `perm.interview.record`; events `+calibration.report_frozen`, `+decision_report.created`; alarm kind `incident.safety_or_critical`; the event-name styles `prereg.locked` (13) and `preregistration.locked` (15.32.1) differ.
7. **Cited but outside this cell's path list, not reconciled here:** `GET /v1/admin/calibration-proposals` (13:931) and `GET /v1/admin/capacity-dashboard`, `GET /v1/admin/bottleneck` (11c:615; S15 has `GET /v1/admin/capacity`).

## Edits required in citing parts

Each edit gives the part and line (a `*` marks a line derived by counting from the nearest cited line; the old text is exact and is what to match), the old text and the new text. Rows of the table 13.10.2 are quoted with their pipe characters. No edit is needed at 13:51, 13:921, 13:925, 13:929 and 11c:615: the paths cited there are now defined (`/v1/admin/metric-snapshots` with `?kind`, 15.E.10; evaluations, 15.E.10; balance, 15.E.7).

```
E1  13:870
old: records the id range of the `calibration_records` used, and attaches the report id and a SHA-256 of its canonical JSON as evidence to the launch-gate item that S14.* designates for calibration data.
new: records the id range of the `calibration_records` used, and returns the report id and `report_hash` (a SHA-256 of its canonical JSON); the operator attaches them as evidence to the launch-gate item that S14.* designates for calibration data with the launch evidence operation of S15.27 (`perm.launch.evidence`).

E2  13:920
old: | `recordClientEvents` | `POST /v1/events` | member | none (own leases only; 13.3.5) |
new: | `recordClientEvents` | `POST /v1/client-event-batches` | member | none (own leases only; 13.3.5) |

E3  13:175*
old: A member-scheme batch endpoint accepts at most
new: The member-scheme batch endpoint `recordClientEvents` (`POST /v1/client-event-batches`, S15.E.11, which answers 204 in every valid case) accepts at most

E4  13:168*
old: Public landing page loaded (count only; never deduplicated by visitor)
new: Public landing page loaded (count only; never deduplicated by visitor); not sent through the API, S15.E.11 defines no public ingestion endpoint, so this count comes from aggregate counters at the front-end host

E5  13:923
old: | `approvePreRegistrationLock` | `POST /v1/admin/pre-registrations/{prr_id}/lock-approvals` | admin, step-up | `perm.prereg.lock` |
new: | `lockPreRegistration`, `approveApproval` | `POST /v1/admin/pre-registrations/{prr_id}/lock`, then `POST /v1/admin/approvals/{apv_id}/approvals` by a different admin | admin, step-up, two-person | `perm.prereg.lock`, `perm.approval.decide` |

E6  13:924
old: | `getPreRegistrationProof` | `GET /v1/public/pre-registrations/{prr_id}/proof` | none | Returns `content_hash`, `chain_hash`, `locked_at`, `phase`, `version` only |
new: | `getPublicPreRegistration` | `GET /v1/public/pre-registrations/{prr_id}` | none | Returns the locked `PreRegistration` of S15.33.2 with `content_hash`, `locked_at`, `post_launch` and the additive `chain_hash`; `phase` is `scope`, `version` is the depth of the `supersedes_id` chain |

E7  13:607*
old: | `status` | enum | `draft`, `lock_requested`, `locked`, `abandoned` |
new: | `status` | enum | `draft`, `locked`, `abandoned`; a pending lock is an `AdminApproval` (S15.E.3), not a row status. Rows `draft -> lock_requested`, `lock_requested -> draft` and `lock_requested -> locked` of 13.7.2 are re-read as: initiation of `lockPreRegistration`, withdrawal or expiry of that approval, and execution by `approveApproval` |

E8  13:623*
old: `ChangeLogEntry` published with `content_hash`, `chain_hash`, `locked_at`, `phase`, `version` (not the content)
new: `ChangeLogEntry` of kind `preregistration_lock` published with `content_hash`, `chain_hash`, `locked_at`, `scope` and the content (S15.32.1 publishes the content so that anyone can recompute the hash)

E9  13:926
old: | `createDecisionReport` | `POST /v1/admin/decision-reports` | admin | `perm.metrics.export` |
new: | `createDecisionReport`, `listDecisionReports`, `getDecisionReport`, `getDecisionReportContent` | `POST`, `GET /v1/admin/decision-reports`; `GET /v1/admin/decision-reports/{dcr_id}`; `GET /v1/admin/decision-reports/{dcr_id}/content` | admin | `perm.metrics.export` (create, content), `perm.metrics.view` (lists, get) |

E10 13:927
old: | `createExperiment`, `updateExperiment` | `POST`, `PATCH /v1/admin/experiments[/{exp_id}]` | admin | `perm.experiment.manage` |
new: | `createExperiment`, `updateExperiment` | `POST`, `PATCH /v1/admin/experiments[/{exp_id}]` | admin | `perm.experiment.edit` |

E11 13:928
old: | `registerExperiment`, `startExperiment`, `stopExperiment` | `POST /v1/admin/experiments/{exp_id}/registrations`, `/starts`, `/stops` | admin; `startExperiment` two-person | `perm.experiment.manage` |
new: | `registerExperiment`, `startExperiment`, `stopExperiment` | `POST /v1/admin/experiments/{exp_id}/registrations`, `/starts`, `/stops` | admin, step-up; two-person start is open (S15.E Issues raised, item 3) | `perm.experiment.run` |

E12 13:931
old: | `getCalibrationStatistics`, `getCalibrationProposals` | `GET /v1/admin/calibration-statistics`, `/calibration-proposals` | admin | `perm.calibration.record` |
new: | `getCalibrationSummary` (was `getCalibrationStatistics`), `getCalibrationProposals` | `GET /v1/admin/calibration/summary`, `GET /v1/admin/calibration-proposals` (path not reconciled here) | admin | `perm.calibration.read` |

E13 13:932
old: | `createCalibrationReport` | `POST /v1/admin/calibration-reports` | admin | `perm.calibration.record` |
new: | `createCalibrationReport`, `listCalibrationReports`, `getCalibrationReport` | `POST`, `GET /v1/admin/calibration-reports`; `GET /v1/admin/calibration-reports/{clr_id}` | admin | `perm.calibration.write` (create), `perm.calibration.read` (lists, get) |

E14 13:933
old: | `createIncident`, `updateIncident`, `listIncidents` | `POST`, `PATCH`, `GET /v1/admin/incidents` | admin | `perm.incident.record` |
new: | `createIncident`, `listIncidents`, `getIncident`, `updateIncident`, `startIncidentInvestigation`, `resolveIncident` | `POST`, `GET /v1/admin/incidents`; `GET`, `PATCH /v1/admin/incidents/{inc_id}`; `POST /v1/admin/incidents/{inc_id}/investigations`, `/resolutions` | admin | `perm.incident.record` (writes), `perm.metrics.view` (reads) |

E15 13:934
old: | `createInterview`, `getInterviewCoverage` | `POST /v1/admin/interviews`, `GET /v1/admin/interview-coverage` | admin | `perm.interview.record` |
new: | `createInterview`, `getInterviewCoverage` | `POST /v1/admin/interviews`, `GET /v1/admin/interview-coverage` | admin | `perm.interview.record` (create), `perm.metrics.view` (coverage) |
```
