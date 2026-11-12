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

Indexes: `(name, occurred_at)`, `(refs->>'job_id', occurred_at)` partial, `(refs->>'lease_id', name)` partial, `(expires_at)`. Deduplication of repeated client events is done by the endpoint (13.3.5), not by a unique index. No foreign keys (events survive entity deletion by design). [D]

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

## 13.4 Metric source views and data model additions

### 13.4.1 Metric source views

All metric SQL reads the views below, never the base tables, so that a change in S5.* column names touches one view definition and not fifteen queries. View columns follow the naming rules of S0.7; S5.* is authoritative for the base columns and the view definitions are updated with it [A]. SQL is PostgreSQL-flavored; the semantics are normative and the syntax illustrative (S4.* fixes the stack). Views are owned by a read-only database role used by the rollup jobs; no application role and no admin API reads them row by row (`AN-03`). [D]

| View | One row per | Columns (all derived; times are UTC `timestamptz`) |
| --- | --- | --- |
| `mv_member` | member (not `closed`, or opaque id after closure) | `member_ref` (= `member_id`, internal), `created_at`, `status`, `trust_tier`, `is_internal`, `locale`, `first_submission_at`, `first_accepted_at` |
| `mv_attempt` | lease (one attempt on one cell) | `lease_id`, `cell_id`, `job_id`, `member_ref`, `is_internal`, `cell_kind`, `job_type`, `template_id`, `template_version_id`, `service_id` (nullable), `is_commons`, `purpose`, `sensitivity`, `license`, `service_requirement`, `topic_category_id` (nullable), `issued_at`, `card_opened_at` (latest `ui.card_opened`, nullable), `submitted_at` (nullable), `decided_at` (acceptance, rejection, expiry, decline or release time; null while open), `outcome` (`open`, `declined`, `released`, `expired`, `revoked`, `rejected`, `accepted`), `reject_reason` (`reject.*`, nullable), `decline_reason` (nullable), `auto_check_passed` (bool, nullable) |
| `mv_job` | job | `job_id`, `is_commons`, `job_type`, `n_primary_cells`, `quoted_window_s`, `committed_cells` (primary plus verification pool, S0.6.1), `submitted_at`, `escrow_confirmed_at`, `all_accepted_at`, `settled_at`, `final_state` (`completed`, `failed`, `cancelled`, `rejected`, `running`, ...), `requester_is_internal` |
| `mv_gold` | gold-cell execution | `submission_id`, `template_id`, `outcome` (`pass`, `fail`, `inconclusive`), `insertion_prob_ppm` (the effective `g` at insertion), `adjudicated` (bool), `adjudicated_correct` (bool, nullable), `adjudication_prob_ppm` |
| `mv_audit` | audit | `audit_id`, `cell_id`, `template_id`, `sampling_prob_ppm` (the effective `s` at selection), `second_matches` (bool), `third_requested` (bool), `original_judged_wrong` (bool, nullable until resolved) |
| `mv_lot` | credit lot | `lot_id`, `member_ref`, `earned_at`, `earned_ucr`, `expires_at`, `expired_ucr`, `spent_ucr`, `lifetime_days_applied`, `assignment_id` (nullable) |
| `mv_optin` | member opt-in axis value | `member_ref`, `axis`, `value`, `is_default` (member holds exactly the default set of `optin.default_*` for the axis) |
| `mv_incident` | incident | `incident_id`, `incident_type`, `severity`, `status`, `occurred_at`, `resolved_at` |

The views contain `member_ref` and therefore live inside the trust boundary; `MetricSnapshot` never does (`AN-04`). [D]

### 13.4.2 Entities added by this part [A]

Each is reported as a convention addition (see `## Issues raised`). Retention classes are those of S0.7.

| Entity | Table | Prefix | Retention | Role |
| --- | --- | --- | --- | --- |
| `Incident` | `incidents` | `inc_` | `permanent` (typed core), free-text `note` is `moderation` | A typed record of one incident (13.4.3) |
| `Interview` | `interviews` | `ivw_` | `permanent` | One coded qualitative interview (13.6, `MET-14`); no name, no quote, no member link |
| `ExperimentBlock` | `experiment_blocks` | `blk_` | `permanent` | One permuted block of arm labels per experiment and stratum (13.8) |

Existing entities used with their S0.7 prefixes: `Event` (`evt_`), `MetricSnapshot` (`mts_`), `CalibrationRecord` (`cal_`), `Experiment` (`exp_`), `ExperimentAssignment` (`asg_`), `PreRegistration` (`prr_`), `LaunchGateItem` (`lgi_`), `Alarm` (`alm_`). New ID schemes: `MET-nn` (metrics), `CAL-nn` (calibration statistics), `TH-nn` (pre-registered threshold), `DR-nn` (decision rule), `AN-nn` (analytics privacy rule).

### 13.4.3 Incidents (typed)

Enum `incident_type` (stored values): `policy_violation`, `injection_attempt`, `abuse_flag`, `provider_warning`, `provider_account_problem`, `safety_incident`. These are exactly the FD§9 list (policy violations, injection attempts, abuse flags, any provider warning or account problem), plus `safety_incident` because decision rule (c) of FD§9 speaks of "unresolved safety" incidents. Enum `incident_severity`: `info`, `minor`, `major`, `critical`. Incident status: `open`, `investigating`, `resolved` (T). [D]

| Field | Type | Rule |
| --- | --- | --- |
| `id`, `created_at`, `row_version` | S0.7 | |
| `incident_type`, `severity`, `status` | enum | As above |
| `source` | enum `auto`, `manual` | `auto` rows are created by the rules below; `manual` by an operator (`perm.incident.record`) |
| `source_ref` | json | Opaque ids only (`submission_id`, `report_id`, `service_id`, `job_id`); no member id |
| `occurred_at`, `resolved_at` | timestamptz | `resolved_at` set only with status `resolved` |
| `resolution_code` | enum | `no_action`, `parameter_changed`, `template_paused`, `service_suspended`, `member_actioned`, `provider_contacted`, `other` |
| `note` | text, 0..2000 chars | Reviewer-written; no names, no quotes of volunteers' pages; purged to null `retention.moderation_days` after `resolved_at` |

Automatic creation rules [D]: `submission.quarantined` with a pattern reason creates `injection_attempt` (severity `minor`); `job.policy_rejected` with `policy.R3.prohibited_content` creates `policy_violation` (`minor`); `report.actioned` creates `abuse_flag` (severity set by the actioning reviewer); `killswitch.engaged` with scope `service` creates nothing (it is a response, not an incident). `provider_warning`, `provider_account_problem` and `safety_incident` are `manual` only, because no part of the system may read a volunteer's provider page (ground rule 2); they arrive by a member report or a founder's own account. A member-facing way to report a provider warning is a `Report` kind handled in S10.* and S11.*. Events: `incident.recorded` (none to `open`), `incident.resolved`.

**Unresolved safety or provider incident** (input to decision rule (c) of FD§9) means: a row with `status != 'resolved'` and `incident_type IN ('safety_incident','provider_warning','provider_account_problem')`. [D]

## 13.5 Metric conventions

### 13.5.1 Time windows

- `day0` is `PreRegistration.content.study.cohort_start_at` (UTC), set in the pre-registration before launch (13.7). Pilot week `k` is `[day0 + (k-1)*7 d, day0 + k*7 d)`. `wk(ts) = floor((ts - day0) / 7 d) + 1`. Days are UTC calendar days (S0.6.2). Seven days is the definition of a week; it is not a parameter. [D]
- Trailing windows (v, capacity forecasts) use their own parameters (`price.v_window_days`, `admission.throughput_window_days` where S6.* defines it). [D]
- `as_of` is the rollup's `source_watermark`: the latest `received_at` of any source row included. A window is `closed` when `as_of >= window_end + metrics.rollup_interval_s`; open windows are published with `is_partial = true`. [D]

### 13.5.2 Population

Every metric has a `population` dimension: `all` or `external` (`NOT is_internal`). Donor-side metrics filter on the executing member; demand-side metrics (`MET-01` requested cells, `MET-02`) include jobs posted by internal requesters, because the FD's own trial large jobs are founder-run, and report `requester_is_internal` as a dimension. In SQL below, `pop_ok` stands for `(:population = 'all' OR NOT is_internal)`. [D]

### 13.5.3 Numbers

- Ratios are integer ppm (S0.6.1). A measured ratio is `round_half_up(num * 1,000,000 / den)` computed as `(2 * num * 1000000 + den) / (2 * den)` with integer division, so every implementation agrees. `den = 0` gives `NULL` and status `no_data`. [D]
- Percentiles use the lower empirical percentile (`percentile_disc`): the median of an even count is the lower middle value. Seconds are integers (S0.6.2). [D]
- Intervals: 95 percent Wilson score interval for a proportion `x/n`, `z = 1.96` (the two-sided 95 percent standard normal quantile): `center = (p + z^2/(2n)) / (1 + z^2/n)`, `half = z / (1 + z^2/n) * sqrt(p(1-p)/n + z^2/(4n^2))`, `p = x/n`. The 95 percent level is a reporting convention, not a decision threshold. Intervals are stored as `ci_low_ppm`, `ci_high_ppm`. [D]

### 13.5.4 `MetricSnapshot` and the snapshot writer

Table `metric_snapshots` (prefix `mts_`, `permanent`, append-only). [D]

| Column | Type | Rule |
| --- | --- | --- |
| `id`, `created_at` | S0.7 | |
| `metric_no` | text | `MET-nn`, `CAL-nn` or `EXP-nn.<outcome>` |
| `metric_name` | text | `hamyar_<area>_<name>_<unit>` (S0.5) |
| `definition_version` | int | Per metric, starts at 1; bumped when the definition in this part changes; a pre-registration pins it (13.7) |
| `dims` | json | Allowed keys of 13.3.3 plus `population`, `window` |
| `dims_hash` | text | SHA-256 of canonical `dims` (S0.6.4) |
| `window_start`, `window_end` | timestamptz | `[start, end)` |
| `scale` | enum `count`, `ppm`, `seconds`, `ucr` | `ppm` is also used for fixed-point reals (1.0 = 1,000,000) |
| `value` | bigint | Null when `suppressed` or `no_data` |
| `numerator`, `denominator` | bigint | Where applicable |
| `ci_low_ppm`, `ci_high_ppm` | bigint | Where applicable |
| `n_members` | int | Distinct members in the population; the suppression basis (`AN-06`) |
| `n_obs` | int | Observations (cells, attempts, jobs) |
| `status` | enum `ok`, `no_data`, `suppressed`, `insufficient_sample` | |
| `is_partial` | bool | Window not closed (13.5.1) |
| `visibility` | enum `internal`, `public` | `public` only for series that S6.* and S12.* name (v, eta, claim ratio, counters) |
| `param_versions` | json | As in 13.3.1 |
| `source_watermark` | timestamptz | 13.5.1 |
| `supersedes_id` | text, nullable | A recomputation never edits; it inserts a row pointing at the one it replaces |

Unique key: `(metric_no, dims_hash, window_start, window_end, definition_version, supersedes_id)` so the rollup is idempotent. Writer algorithm [D]:

```
for each (metric, dims, window) produced by a rollup query:
    row.n_members = distinct members behind it (0 when the metric has no member population)
    if metric.has_member_population and row.n_members < analytics.min_cohort_k and dims has any split other than population/window:
        row.status = 'suppressed'; row.value = NULL; row.numerator = NULL; row.denominator = NULL
    elif row.denominator == 0: row.status = 'no_data'
    elif row.n_obs < metric.min_obs_for_value (pinned in the pre-registration, or 1): row.status = 'insufficient_sample'
    else row.status = 'ok'
for each split (siblings sharing every dim except one):
    if count(siblings with status 'suppressed') == 1 and parent total is published:
        suppress the sibling with the smallest n_members among the 'ok' ones      # AN-07
insert rows; emit metric.snapshot_created per row
```

For metrics whose population is not members (`MET-02` per job, `MET-13` incidents) the suppression test uses `n_obs < analytics.min_cohort_k` only when a split is applied, and the unsplit total is always stored. [D]

## 13.6 Phase 1 metrics: definitions, queries, cadence, known biases

Each metric lists: exact definition, reference query over the views of 13.4.1 (`:population`, `:day0` and the other `:name` values are bind parameters), rollup cadence, and the known biases. "Hourly" means every `metrics.rollup_interval_s` (initial configurable default 3,600 s); "daily" means once per UTC day at `metrics.daily_rollup_offset_s` after 00:00 UTC (new parameter, initial configurable default 1,800 s); "weekly" means when a pilot week closes (13.5.1); "on event" means in the transaction-after hook of the named event. [D]

### 13.6.1 `MET-01` Deposit-to-withdrawal ratio (weekly)

| Field | Value |
| --- | --- |
| Name | `hamyar_credit_deposit_withdrawal_ratio_ppm` |
| Definition (FD§9: cells contributed / cells requested) | `contributed(w)` = accepted cells of every `cell_kind`, Commons and member jobs, decided in week `w`. `requested(w)` = sum of `n_primary_cells` of jobs whose `job.escrow_confirmed` falls in week `w`. Ratio = `contributed / requested` in ppm (values above 1,000,000 mean more supply than admitted demand). Reported with the split `contributed_commons` and `contributed_member_jobs`, and a cumulative value over weeks `1..w` |
| Variant `B` | Same numerator; denominator `committed_cells` (primary plus verification pool) of the same jobs. It matches the admission arithmetic of S0.6.1 (committed 264 against capacity 320 in the FD§3.3 example) |
| Cadence | Weekly; daily partial |
| Known biases | Commons cells inflate the numerator: a member who only does Commons work raises the ratio without funding anyone's job, so the split is mandatory. The planned large-job event in weeks 3 and 4 makes the weekly series lumpy; read the cumulative value. Gold, audit and review cells count as contributed (they mint, `ISS-03`) but are not demand. Internal trial jobs count as demand by design (13.5.2). A ratio over a week with `requested = 0` is `no_data`, not infinity |

```sql
WITH c AS (
  SELECT wk(decided_at) AS wk,
         count(*) FILTER (WHERE is_commons)     AS commons,
         count(*) FILTER (WHERE NOT is_commons) AS member_jobs
  FROM mv_attempt WHERE outcome = 'accepted' AND pop_ok GROUP BY 1),
r AS (
  SELECT wk(escrow_confirmed_at) AS wk, sum(n_primary_cells) AS requested, sum(committed_cells) AS committed
  FROM mv_job WHERE NOT is_commons AND escrow_confirmed_at IS NOT NULL GROUP BY 1)
SELECT g.wk, c.commons + c.member_jobs AS contributed, r.requested, r.committed
FROM generate_series(1, :n_weeks) g(wk) LEFT JOIN c USING (wk) LEFT JOIN r USING (wk);
-- value = round_half_up(contributed * 1e6 / requested); variant B divides by committed
```

### 13.6.2 `MET-02` Time to complete a large job versus its quote

| Field | Value |
| --- | --- |
| Names | `hamyar_job_completion_vs_quote_ppm` (per large job), `hamyar_job_large_within_quote_total` |
| Large job | `n_primary_cells >= metrics.large_job_min_cells` (new parameter, initial configurable default 240, the size of the FD§3.3 reference job; validation `1..admission.max_job_cells`) |
| Definition | Two intervals per large job. `t_submit_to_done_s = all_accepted_at - submitted_at` (FD§9 wording: submission to all cells accepted). `t_admit_to_done_s = all_accepted_at - escrow_confirmed_at`, compared with `quoted_window_s`: `completion_vs_quote_ppm = round_half_up(t_admit_to_done_s * 1e6 / quoted_window_s)`. **Within quote** means `t_admit_to_done_s <= quoted_window_s`, that is ppm <= 1,000,000 (`ISS-136`). The quote window runs from admission, so waitlist and quote time are excluded from the comparison and reported separately as `t_submit_to_admit_s` |
| Job states | `completed` with `all_accepted_at` set: measured. `running` / `suspended`: reported as `open` with `elapsed_ratio_ppm = elapsed / quoted_window_s` (right-censored, never counted as within quote until done). `failed`, `cancelled` after admission: counted as not within quote, with `final_state` shown |
| The first three | `first_m_large(m)`: the first `m` large jobs ordered by `escrow_confirmed_at` after `day0`; FD§9 rule (a) uses `m = 3` ("two of three trial large jobs") |
| Cadence | On `job.all_cells_accepted`, `job.settled_partial`, `job.stop_requested`; daily for open jobs |
| Known biases | With three jobs the result is a count from 0 to 3, not an estimate (S13.11). Founder-run trial jobs may be unrepresentative. A quote that is padded makes "within quote" easy; always show `quoted_window_s` next to the measured time and the `committed_cells / capacity` at admission. Overrun stop at `job.max_overrun_ratio` truncates the worst cases at 2.0 |

```sql
SELECT job_id, n_primary_cells, quoted_window_s,
       extract(epoch FROM all_accepted_at - submitted_at)::bigint          AS t_submit_to_done_s,
       extract(epoch FROM all_accepted_at - escrow_confirmed_at)::bigint   AS t_admit_to_done_s,
       extract(epoch FROM escrow_confirmed_at - submitted_at)::bigint      AS t_submit_to_admit_s,
       CASE WHEN all_accepted_at IS NULL THEN NULL
            ELSE all_accepted_at <= escrow_confirmed_at + quoted_window_s * interval '1 second' END AS within_quote,
       row_number() OVER (ORDER BY escrow_confirmed_at) AS large_rank, final_state
FROM mv_job
WHERE NOT is_commons AND escrow_confirmed_at >= :day0 AND n_primary_cells >= :large_job_min_cells;
-- large_within_quote_total = count(*) FILTER (WHERE within_quote AND large_rank <= :m)
```

### 13.6.3 `MET-03` Rejection rate, overall and by template

| Field | Value |
| --- | --- |
| Name | `hamyar_verify_rejection_rate_ppm` (dims `template_id`, `reason`, `cell_kind`) |
| Definition | Over attempts with a submission: `rejected / submitted`. `rejected` = outcome `rejected` (automatic checks failed, audit failed, gold mismatch, forbidden content, nonce invalid). Lease expiries and declines are not submissions and are excluded; they are reported as `expiry_rate` and `decline_rate` beside it. Also the automatic-check pass rate `auto_check_passed / submitted` (FD§9 Phase 0 measure, also useful in Phase 1). `by reason` splits `rejected` by `reject.*` code |
| Cadence | Daily |
| Known biases | A rejection is not an error: a correct output can be rejected (`MET-04`) and a wrong one accepted (`MET-05`); the rate mixes donor quality, template strictness and verification design. Templates with fewer than `analytics.min_cohort_k` distinct donors are suppressed (`AN-06`), so in a pilot most per-template cells show only the pooled rate. Rejections raised by a changed policy (`reject.policy_changed`) are excluded from quality views and shown separately. An overturned acceptance (`cell.overturned`) moves the attempt to `rejected` retroactively; recomputation therefore supersedes earlier snapshots |

```sql
SELECT template_id, reject_reason,
       count(*) FILTER (WHERE outcome = 'rejected')                              AS rejected,
       count(*) FILTER (WHERE submitted_at IS NOT NULL)                          AS submitted,
       count(*) FILTER (WHERE auto_check_passed)                                 AS auto_pass,
       count(DISTINCT member_ref)                                                AS n_members
FROM mv_attempt
WHERE decided_at >= :ws AND decided_at < :we AND pop_ok
  AND (reject_reason IS NULL OR reject_reason <> 'reject.policy_changed')
GROUP BY GROUPING SETS ((), (template_id), (template_id, reject_reason), (reject_reason));
```

### 13.6.4 `MET-04` False-reject rate from gold cells

| Field | Value |
| --- | --- |
| Name | `hamyar_verify_false_reject_rate_ppm` |
| Problem (`ISS-133`) | A gold pass or fail only says whether the output matched the key. A failed gold submission can still be a correct output that the comparator or the key did not accept (for example a valid alternative translation). FD§9 asks for the false-reject rate "from gold cells"; without a ground-truth label for the failures it cannot be computed |
| Resolution | Reviewer adjudication of gold failures. Every failed gold submission is eligible; a reviewer labels it `correct` or `incorrect` (stored as a `VerificationRecord` with `verification_method` = `human_review` and `is_adjudication` = true, a convention addition). When adjudication is sampled, each failure carries `adjudication_prob_ppm`. A donor is never penalised for a failure that adjudication labels correct (S8.*) |
| Definition | `judged_correct` = gold passes + failures adjudicated correct (weighted by `1e6 / adjudication_prob_ppm`). `false_reject_rate = adjudicated_correct_failures_weighted / judged_correct`. The Wilson interval of 13.5.3 is applied to the unweighted counts when `adjudication_prob_ppm = 1,000,000` for all rows (the default); a weighted estimate carries `ci = NULL` and the status `insufficient_sample` unless S8.* supplies its variance formula |
| Alarm | `verify.false_reject_alarm` (initial configurable default 0.10, pre-registered by `FND`, S0.10.6): `Alarm` when the lower interval bound exceeds it |
| Cadence | Daily |
| Known biases | Gold cells may be recognisable to donors, so behavior on gold cells may differ from behavior on ordinary cells [H]. The key, not the output, can be wrong. Gold coverage per template is thin: the expected number of gold executions is `g * cells` (`verify.gold_rate_g`, initial configurable default 0.05), so a half-width of 0.10 at `p = 0.5` needs about `1.96^2 * 0.25 / 0.10^2 = 96.04` gold executions, that is about `96.04 / 0.05 = 1,921` cells through that template. Adjudicators are fallible and are not blinded to the comparator's verdict unless S8.* blinds them |

```sql
SELECT count(*) FILTER (WHERE outcome = 'pass')                              AS passes,
       count(*) FILTER (WHERE outcome = 'fail')                              AS fails,
       count(*) FILTER (WHERE outcome = 'fail' AND adjudicated)              AS fails_adjudicated,
       sum(1e6 / adjudication_prob_ppm) FILTER (WHERE outcome = 'fail' AND adjudicated_correct) AS fr_weighted,
       count(*) FILTER (WHERE outcome = 'fail' AND adjudicated_correct)      AS fr_n
FROM mv_gold WHERE template_id = COALESCE(:template_id, template_id);
-- false_reject = fr_weighted / (passes + fr_weighted)
```

### 13.6.5 `MET-05` False-accept estimate from audits

| Field | Value |
| --- | --- |
| Name | `hamyar_verify_false_accept_estimate_ppm` |
| Definition | Among audited cells (second execution of a cell that passed automatic checks; third execution on mismatch, S0.9.8, `verify.third_exec_on_mismatch`), `original_judged_wrong` is true when the audit resolution (S8.*) finds the first output wrong. The estimate is the inverse-probability weighted share: `sum(1e6 / sampling_prob_ppm over original_judged_wrong) / sum(1e6 / sampling_prob_ppm over resolved audits)`. Weights are needed because sampling is adaptive: tiers multiply `s` (`trust.audit_multiplier.*`) and `verify.adapt.*` steps it (`ISS-134`; `Audit` and `GoldCell` insertion must store the effective probability, a convention addition) |
| Alarm | `verify.false_accept_alarm` (initial configurable default 0.05, `FND`): `Alarm` when the lower Wilson bound of the unweighted share exceeds it |
| Cadence | Daily |
| Known biases | It is a **lower bound**: when the audit executor makes the same mistake as the original (same service, same model, same ambiguity) the two agree and the error is not seen [H]. Audited cells are only those that passed automatic checks. Cells that are never audited have no estimate; no claim is made about them. With zero observed false accepts in `n` resolved audits the 95 percent upper bound is about `3 / n` (rule of three; for example `3 / 30 = 0.10`), so a small audit count cannot show that the rate is below 0.05 |

```sql
SELECT count(*) FILTER (WHERE original_judged_wrong IS NOT NULL)                       AS resolved,
       count(*) FILTER (WHERE original_judged_wrong)                                   AS wrong,
       sum(1e6 / sampling_prob_ppm) FILTER (WHERE original_judged_wrong)               AS wrong_w,
       sum(1e6 / sampling_prob_ppm) FILTER (WHERE original_judged_wrong IS NOT NULL)   AS resolved_w
FROM mv_audit WHERE template_id = COALESCE(:template_id, template_id);
```
