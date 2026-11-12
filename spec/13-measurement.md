# 13. Measurement, experiment support and pre-registration

*Spec part 13 · owner cell C-018 · scope H of the brief · binding on vocabulary: `spec/00-conventions.md` (written `S0.*`). Written against Founding Document draft v0.1 (FD). Nothing here is legal advice and nothing has been verified against any provider's terms or any law. Every number is either derived by a formula shown next to it or labeled `initial configurable default`. Simulation output is never evidence about human behavior (prompt K).*

## 13.1 Purpose, scope and build split

**Purpose.** Produce, from the finished system, every Phase 1 measure of FD§9 and every Phase 0 measure of FD§9; record the thresholds and decision rules BEFORE launch and lock them; assign experiment arms by logged random assignment; give the founders a calibration tool that works with no members; and do all of it without building a tracking apparatus on volunteers. [D]

**Not defined here** (named so nobody re-specifies them): the ledger and the definition of v and the claim ratio (S6.*), the verification estimators for reliability, false-accept and false-reject (S8.*), screens (S11.*), operation ids (S15.*), retention numbers (S10.*, parameters `retention.*`), the launch-switch rule (S14.*), and the growth mechanics `V1`..`V6` (S12.*). This part states the data each of them must supply or consume. [D]

**Coverage map: every item of FD§9 Phase 1 and Phase 0 has one metric id.** Metric ids are `MET-nn` (a convention addition, see `## Issues raised`).

| FD§9 item | Metric id | Defined in | Computed by |
| --- | --- | --- | --- |
| Deposit-to-withdrawal ratio, weekly | `MET-01` | S13.6 | weekly rollup |
| Time to complete a large job vs quote | `MET-02` | S13.6 | on job completion plus daily |
| Rejection rate overall and by template | `MET-03` | S13.6 | daily |
| False-reject rate from gold cells | `MET-04` | S13.6 | daily |
| False-accept estimate from audits | `MET-05` | S13.6 | daily |
| Verification overhead v and implied eta | `MET-06` | S13.6 | daily (reads S6.*) |
| Week-2 and week-4 return | `MET-07` | S13.6 | daily, closes weekly |
| Median time per contribution, share under 60 s | `MET-08` | S13.6 | daily |
| Time to first verified cell for newcomers | `MET-09` | S13.6 | daily |
| Active capacity per member per day | `MET-10` | S13.6 | weekly |
| Concentration (top 10 percent share) | `MET-11` | S13.6 | weekly |
| Decline and opt-out rates by category | `MET-12` | S13.6 | daily |
| Incidents, typed | `MET-13` | S13.6 | hourly |
| Qualitative interviews (8-10) | `MET-14` | S13.6 | on record |
| Accelerated-expiry arm outcomes (FD§4.5 arm, FD§9 setup) | `MET-15` | S13.8 | weekly |
| Phase 0: cells per day per service, seconds per cell, refusal and failure, copy-paste error, automatic-check pass rate | `CAL-01`..`CAL-06` | S13.9 | on demand, frozen as evidence |

**Build split** (S0.12). `BM2` builds the `PreRegistration` lock, the `Experiment` and `ExperimentAssignment` engine and the Phase 0 calibration tool, so the founders can measure while the rest is built. `BM9` builds the event projector, the metric views, the rollups, the dashboards and the activation of the expiry arm. Domain events are written to the outbox from `BM0` on (S4.*); the projector MUST read the outbox from its first row, and an outbox row MUST NOT be purged before it has been projected. [D]

**Decisions of this part** [D]

1. Member-linked metrics (return, concentration, time to first verified cell, capacity) are computed by rollup SQL inside the database trust boundary from operational rows; only aggregates leave it. The analytics `events` table never holds a member id, a `vol_` handle, a device id or an IP hash.
2. Every published number is a `MetricSnapshot`: immutable, versioned by `definition_version`, carrying numerator, denominator and a suppression flag.
3. Thresholds and decision rules live in a `PreRegistration` that is canonicalized, hashed, timestamped and locked by two admins before `launch.members_may_join` may become true.
4. Experiment arms are data (`Experiment`): parameter and flag overrides per arm, assignment by permuted blocks within strata, every draw logged and reproducible from a salt that is published when the experiment concludes.
5. The calibration tool records numbers and sizes, never prompt or output text, never provider credentials, and never writes a parameter; it produces proposals that a human applies through the parameter editor.
6. Reports state what the data cannot support (S13.11). With 30 to 50 members most subgroup questions are unanswerable and the system says so instead of printing a number.

## 13.2 Analytics privacy rules

Safety principle: members in Iran may be endangered by what is stored (FD Principle 8, S0.6.4). Analytics therefore starts from "collect nothing that is not needed to compute a declared measure". [D]

| Rule | Statement | Enforced by |
| --- | --- | --- |
| `AN-01` | No third-party tracker, tag, pixel, session-replay tool or analytics SDK, in any surface. Parameter `analytics.third_party_trackers` = false is a constant. | CSP `connect-src` and `script-src` limited to the app's own origin (S10.*, S11.*); CI test that fails on any external host in the built bundle |
| `AN-02` | No cookies and no persistent client identifier for analytics. Parameter `analytics.cookies_enabled` = false is a constant. No fingerprinting beyond S10.*. | Client lint; the `events` schema has no identifier field |
| `AN-03` | Aggregate by default. Dashboards, exports and snapshots show counts, rates and percentiles, never rows about one member. There is no row-level export endpoint. | Admin API exposes only `GET /v1/admin/metric-snapshots` and report endpoints (S13.10) |
| `AN-04` | The `events` table holds no `mem_` id, no `vol_` handle, no `dev_` id, no IP hash, no e-mail, no free text. Allowed values are enum values, opaque ids of non-member entities, and integers. | JSON Schema per event with `additionalProperties: false`; DB check on column set |
| `AN-05` | Minimal retention. Raw `events` rows are deleted `retention.event_raw_days` (initial configurable default 30, S0.10.6 table B) after `occurred_at`. `MetricSnapshot` rows are `permanent` and aggregate-only. | Purge job `metrics.retention_purge` (S13.10) |
| `AN-06` | Small-cell suppression. A published value whose population has fewer than `analytics.min_cohort_k` distinct members (initial configurable default 10) is stored with `suppressed = true` and no value. Counts of events without a member population (for example incidents) are suppressed when the count is below k AND a dimension split was applied. | Snapshot writer (S13.5.4) |
| `AN-07` | Complementary suppression. If exactly one sibling cell of a published split is suppressed, the next-smallest sibling is suppressed too, so the hidden value cannot be recovered by subtracting from the parent total. | Snapshot writer (S13.5.4) |
| `AN-08` | No differencing through overlap. Public series use non-overlapping windows of at least one week. Internal rolling windows (for example v over `price.v_window_days`) are not public per member and never below k. | Snapshot writer; S12.* publishes only the series named there |
| `AN-09` | Small cells in the admin dashboard are hidden by default. The permission `perm.metrics.view_small_cells` shows them and every use writes an `AdminAction`. In a pilot of 30 to 50 members this will hide many splits; that is intended (S13.11). [A] | RBAC (S10.*) |
| `AN-10` | Client interaction events (S13.3) can be turned off per member in settings (`member.settings.client_events_enabled`, default true [A]) and globally by `analytics.client_events_enabled`. With them off, time per contribution falls back to server-side timestamps and `time_source` says so. | Event endpoint checks both switches |
| `AN-11` | Participants are told, in the pilot opt-in, what is measured and that interviews are voluntary. Copy key `copy.privacy.analytics_notice` (`fa` and `en`, marker `needs_human_and_legal_review`, S11.*). | S11.* |
| `AN-12` | Analytics privacy is not protection against compromise of the operational database or compelled disclosure of it: `leases`, `submissions` and `ledger_entries` carry `member_id`. The analytics design prevents casual exposure through dashboards, exports, third parties and public pages only. S10.* owns the statement of what the platform cannot promise. [D] | S10.* |

**Internal members.** Founders and testers who hold member accounts MUST be flagged `Member.is_internal` (bool, default false, set by an operator; a convention gap, see `## Issues raised`) so that every metric can be reported for `population = all` and `population = external`. Published and pre-registered values default to `external`. [A]

## 13.3 Event schema

### 13.3.1 Envelope

Table `events` (entity `Event`, prefix `evt_`, retention class `ops`, S0.7). One row per analytics event. Append-only; no update path. [D]

| Column | Type | Rule |
| --- | --- | --- |
| `id` | text | `evt_<ulid>` (S0.6.3) |
| `name` | text | Exactly one name from 13.3.4; lowercase dotted `<area>.<event>` (S0.5). Server-side names equal the domain event names of S0.9 |
| `event_version` | int | Version of the JSON Schema for this name; starts at 1; a change that removes or retypes a field is a new version |
| `source` | enum `server`, `client` | `client` events arrive through the event endpoint (13.3.5) |
| `occurred_at` | timestamptz | Server time only (S0.6.2). For client events it equals `received_at`; client clocks are never trusted |
| `received_at` | timestamptz | When the projector or the endpoint stored it |
| `actor_kind` | enum `member`, `admin`, `system`, `anonymous` | `principal_type` of S0.8.2 without the id |
| `refs` | json object | Opaque ids of non-member entities only. Allowed keys: `job_id`, `cell_id`, `lease_id`, `submission_id`, `template_id`, `template_version_id`, `service_id`, `policy_version_id`, `experiment_id`, `audit_id`, `incident_id`. A `lease_id` is a reference to a row that carries `member_id`; see `AN-12` |
| `dims` | json object | Keys and values drawn from the allowed dimension registry (13.3.3); every value is an enum value, a rule code, or a boolean |
| `measures` | json object | Integers only (counts, seconds, ucr, ppm) |
| `param_versions` | json object | `{ "policy_version_id": "plv_...", "parameters": { "<name>": <version> } }` for the parameters the event's metric depends on (S0.9.1 requires the versions in force) |
| `privacy_class` | enum `none`, `entity_ref` | 13.3.2 |
| `expires_at` | timestamptz | `occurred_at + retention.event_raw_days * 86,400 s` |

Indexes: `(name, occurred_at)`, `(refs->>'job_id', occurred_at)` partial, `(refs->>'lease_id', name)` partial, `(expires_at)`. Unique partial index `(refs->>'lease_id', name)` WHERE `name` IN (`ui.card_opened` first-fire guard is NOT applied; see 13.3.5). No foreign keys (events survive entity deletion by design). [D]

### 13.3.2 Privacy classes

| Class | Contains | Example | May appear in |
| --- | --- | --- | --- |
| `none` | No identifier of any entity; enums and integers only | `ledger.invariants_passed`, `ui.landing_viewed` | Everything |
| `entity_ref` | Opaque ids of jobs, cells, leases, templates, services (never members) | `cell.leased` | Admin aggregates; never exported row by row |

A third class that contains a member identifier does not exist; member-linked computation reads operational rows inside the database (decision 1 of 13.1). [D]

### 13.3.3 Allowed dimension registry

`dims` keys are limited to this list; an unknown key or a value outside the enum is rejected and counted in `hamyar_metrics_events_rejected_total`. [D]

| Key | Values |
| --- | --- |
| `job_type`, `purpose`, `license`, `sensitivity`, `service_requirement`, `cell_kind`, `deadline_class`, `size_class`, `locale`, `digits`, `calendar` | enums of S0.8 |
| `tier` | `new`, `established`, `trusted`, `restricted` |
| `is_internal`, `is_commons` | booleans |
| `reason` | one `reject.*` code (S0.8.4), one `policy.<rule>.<slug>` code, or one `decline_reason` value |
| `decline_reason` | `topic`, `too_long`, `service_unavailable`, `unclear`, `not_now`, `other` (convention addition; the decline button offers these, optional) |
| `optin_axis` | `purpose`, `sensitivity`, `license`, `service_requirement`, `topic` |
| `optin_value` | a value of the named axis, or a `top_` id |
| `direction` | `added`, `removed` |
| `device_class` | `phone`, `tablet`, `desktop` (derived by the client from viewport width buckets, never from a user-agent string) |
| `incident_type` | `policy_violation`, `injection_attempt`, `abuse_flag`, `provider_warning`, `provider_account_problem`, `safety_incident` |
| `severity` | `info`, `minor`, `major`, `critical` |
| `experiment_code`, `arm_key` | `EXP-nn`; the arm key of the experiment definition |
| `copy_paste_error_kind`, `result` | calibration enums (13.9) |

### 13.3.4 Event catalogue

"Retention" shows the raw row (`ev`: deleted after `retention.event_raw_days`) and where the information survives in aggregate or in an operational table.

**Server events (projected from the outbox; actor id removed).**

| Name | Trigger | Fields (refs / dims / measures) | Class | Retention |
| --- | --- | --- | --- | --- |
| `member.created` | Member row created | dims: `locale`, `is_internal`; none else | `none` | ev; survives in `members` |
| `member.tier_promoted`, `member.tier_demoted`, `member.restricted` | Tier change | dims: `tier` (new tier) | `none` | ev; `MET-07`, `MET-11` use `members` |
| `member.optin_changed` | Opt-in edited | dims: `optin_axis`, `optin_value`, `direction` | `none` | ev; `MET-12` |
| `member.suspended`, `member.banned`, `member.closed` | Status change | dims: none | `none` | ev |
| `job.created`, `job.submitted` | Job row created; wizard completed | refs: `job_id`; dims: `job_type`, `is_commons`, `purpose`, `sensitivity`, `license`, `service_requirement` | `entity_ref` | ev; `jobs` |
| `job.policy_rejected` | Screening rejects | refs: `job_id`, `policy_version_id`; dims: `reason` (each `policy.*` code, one event per code) | `entity_ref` | ev; `jobs` |
| `job.policy_passed`, `job.waitlisted`, `job.quote_expired` | Machine transition (S0.9.2) | refs: `job_id`; measures: `n_primary_cells`, `quoted_window_s` | `entity_ref` | ev; `jobs` |
| `job.escrow_confirmed` | Admission | refs: `job_id`; measures: `n_primary_cells`, `quoted_window_s`, `escrow_ucr` | `entity_ref` | ev; `jobs`; `MET-01`, `MET-02` |
| `job.started`, `job.all_cells_accepted`, `job.settled`, `job.settled_partial`, `job.stop_requested`, `job.cancel_requested`, `job.cancel_settled` | Transition | refs: `job_id`; measures: `elapsed_s` since `job.escrow_confirmed` | `entity_ref` | ev; `jobs`; `MET-02` |
| `cell.created` | Cell queued | refs: `cell_id`, `job_id`, `template_version_id`; dims: `cell_kind`, `job_type` | `entity_ref` | ev; `cells` |
| `cell.leased`, `lease.issued` | Lease created | refs: `cell_id`, `lease_id`, `template_version_id`, `service_id` (if known); dims: `cell_kind`, `tier`, `is_internal` | `entity_ref` | ev; `leases` |
| `cell.declined` | Member declines or releases | refs: `cell_id`, `lease_id`; dims: `decline_reason`, `purpose`, `sensitivity`, `license`, `service_requirement`, `job_type` | `entity_ref` | ev; `leases`; `MET-12` |
| `cell.lease_expired`, `lease.expired`, `lease.released`, `lease.revoked` | Reaper or member | refs: `cell_id`, `lease_id` | `entity_ref` | ev; `leases` |
| `submission.received`, `lease.submission_received` | Paste-back stored | refs: `lease_id`, `submission_id`; measures: `size_bytes` | `entity_ref` | ev; `submissions`; `MET-08` |
| `submission.schema_failed`, `submission.checks_failed`, `cell.checks_failed` | Automatic checks fail | refs: `lease_id`, `submission_id`, `template_version_id`; dims: `reason` (`reject.*`) | `entity_ref` | ev; `submissions`; `MET-03` |
| `submission.checks_passed`, `cell.checks_passed`, `submission.accepted` | Checks pass; accepted | refs: `lease_id`, `submission_id`, `template_version_id`, `service_id`; dims: `cell_kind`, `is_commons` | `entity_ref` | ev; `submissions`; `MET-01`, `MET-03`, `MET-09`, `MET-10`, `MET-11` |
| `submission.quarantined` | Output flagged (S0.9.3) | refs: `submission_id`, `template_version_id`; dims: `reason` | `entity_ref` | ev; creates an `Incident` of type `injection_attempt` or `abuse_flag` (13.4.3) |
| `cell.flagged_for_audit`, `cell.audit_passed`, `cell.audit_failed`, `cell.overturned`, `cell.requeued`, `cell.attempts_exhausted`, `cell.voided` | Transition | refs: `cell_id`, `template_version_id`; dims: `cell_kind`, `reason` | `entity_ref` | ev; `cells` |
| `audit.created`, `audit.matched`, `audit.mismatched`, `audit.third_requested`, `audit.resolved` | Audit machine (S0.9.8) | refs: `audit_id`, `cell_id`, `template_version_id`; measures: `sampling_prob_ppm` on `audit.created` | `entity_ref` | ev; `audits`; `MET-05` |
| `appeal.filed`, `appeal.upheld`, `appeal.overturned` | Appeal machine (S0.9.7) | dims: none | `none` | ev; `appeals` |
| `report.filed`, `report.actioned`, `report.dismissed` | Report machine | dims: `incident_type` where mapped (13.4.3) | `none` | ev; `reports` |
| `ledger.entry_committed` | Entry written | measures: `amount_ucr`; dims: entry type | `none` | ev; `ledger_entries` permanent |
| `ledger.invariants_passed`, `ledger.invariant_violated` | Checker run | measures: `invariant_no`; dims: none | `none` | ev; `invariant_checks` |
| `parameter.changed`, `policy.version_published`, `killswitch.engaged`, `killswitch.released`, `launch.members_may_join_changed` | Configuration | dims: parameter area or switch scope only | `none` | ev; `parameter_versions`, `change_log_entries`, `admin_actions` permanent |
| `service.suspended`, `service.revoked`, `template.paused` | Machine transition | refs: `service_id` or `template_id` | `entity_ref` | ev; registries permanent |
| `incident.recorded`, `incident.resolved` | Incident machine (13.4.3) | refs: `incident_id`; dims: `incident_type`, `severity` | `entity_ref` | ev; `incidents` permanent |
| `interview.recorded` | Interview row created | dims: none | `none` | ev; `interviews` permanent |
| `prereg.created`, `prereg.lock_requested`, `prereg.locked`, `prereg.amended`, `prereg.abandoned`, `prereg.evaluated` | Pre-registration machine (13.7) | dims: none; measures: `version` | `none` | ev; `pre_registrations` permanent |
| `experiment.created`, `experiment.registered`, `experiment.started`, `experiment.stopped` | Experiment machine (13.8) | refs: `experiment_id`; dims: `experiment_code` | `entity_ref` | ev; `experiments` permanent |
| `experiment.member_assigned` | One assignment row written | refs: `experiment_id`; dims: `experiment_code`, `arm_key`; measures: `block_index` | `entity_ref` | ev; `experiment_assignments` permanent |
| `calibration.recorded` | Calibration row written | dims: `result`, `copy_paste_error_kind`; refs: `service_id` | `entity_ref` | ev; `calibration_records` permanent |
| `metric.snapshot_created` | Rollup wrote a snapshot | dims: none; measures: `metric_no` | `none` | ev; `metric_snapshots` permanent |

**Client events (UI interaction; sent in batches; see 13.3.5).**

| Name | Trigger | Fields | Class | Retention |
| --- | --- | --- | --- | --- |
| `ui.card_opened` | The cell card is brought to the foreground (first open and each return) | refs: `lease_id`; dims: `device_class`, `locale` | `entity_ref` | ev; feeds `mv_attempt.card_opened_at` (latest value, then the event expires) |
| `ui.prompt_expanded` | Member expands the full prompt (mandatory on first use, `ui.card.expand_required_first_use`) | refs: `lease_id` | `entity_ref` | ev |
| `ui.prompt_copied` | Copy button pressed | refs: `lease_id`; dims: `device_class` | `entity_ref` | ev |
| `ui.service_opened` | Open-in-service button pressed (prefill or copy-only link) | refs: `lease_id`, `service_id` | `entity_ref` | ev |
| `ui.paste_started` | Paste-back field first receives input | refs: `lease_id` | `entity_ref` | ev |
| `ui.variant_exposed` | A growth or experiment variant is first rendered to the member (S12.*) | dims: `experiment_code`, `arm_key` | `none` | ev; exposure counts in `MetricSnapshot` |
| `ui.landing_viewed` | Public landing page loaded (count only; never deduplicated by visitor) | dims: `locale`, `device_class` | `none` | ev |

No client event can carry free text, a prompt, an output, a URL, a clipboard content or a timestamp from the device. Events `ui.prompt_copied` and `ui.service_opened` record that a button was pressed; they do not read the clipboard, the provider page or any provider session (ground rule 2 of the brief). [D]

### 13.3.5 Ingestion

- **Server events.** Background job `metrics.projector` reads the outbox in order, strips the actor id, maps fields per 13.3.4, validates against the JSON Schema of `(name, event_version)`, and inserts into `events`. A row that fails validation is not inserted; it increments `hamyar_metrics_events_rejected_total` and writes a log line (no payload). The projector is idempotent: `(outbox_id)` is stored in a side table `metrics_projector_offsets`, so replay inserts nothing twice. [D]
- **Client events.** A member-scheme batch endpoint accepts at most `api.max_body_bytes` of JSON containing up to 50 events [A] (limit stated here because S15.* has no parameter for it; see `## Issues raised`). The server stamps `occurred_at`; it drops any event whose `lease_id` does not belong to the authenticated member (drop, not error, so the endpoint reveals nothing); it applies `ratelimit.member_api_rpm`; it ignores the batch silently when `analytics.client_events_enabled` or the member's `client_events_enabled` is false. `Idempotency-Key` is optional here (S0.11.5). Loss of client events never blocks the UI and never changes a ledger or cell state. [D]
- **Deduplication.** `ui.card_opened` may repeat per lease (each return is informative); all other `ui.*` events keep only the first row per `(lease_id, name)` within the lease lifetime. [D]
