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
