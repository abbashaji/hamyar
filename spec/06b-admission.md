# 6. Admission control and capacity

*Spec part 6, file 6b (admission control) · owner cell C-006 · binding on every other spec file. Written against Founding Document draft v0.1 (FD) and `spec/00-conventions.md` (S0). Nothing here is legal advice and nothing here has been verified against any provider's terms or any law.*

## 6.20 Scope, numbering and how to read this part

This file specifies how the platform decides whether, when and at which quoted window a member job is admitted (prompt scope C, admission control; FD§4.8): capacity forecasting, φ, quoting, the accept / later quote / waitlist decision, capacity reservations for future dates, fairness, cancellation and refunds, behaviour when the forecast drops after acceptance, and preservation of the Commons share (1 − φ). [D]

| Topic | Owner | Relation to this part |
| --- | --- | --- |
| Price `p = 1 + v + λ`, measurement of v, η, claim ratio, lots, expiry, escrow and settlement postings | `S6.*` (credit and ledger file of part 6) | Used by name: `escrow_hold`, `escrow_release`, `transfer`, `levy`, `refund` (S0 0.8.5). This part states only the admission-side quantities and one arithmetic check (6.32) |
| State-machine guards in general, concurrency of leasing and settlement | `S5.*` | This part adds guards and side effects only for the edges named in 6.28, 6.29, 6.30, 6.33 |
| Lease scheduling, verification, anti-forgery | `S8.*`, `S9.*` | This part fixes the scheduler contract it needs (6.26, 6.31) |
| Screens and copy | `S11.*` | This part names `copy.admission.*` keys and their intent only (6.35) |
| API operations | `S15.*` | This part proposes operation ids and errors (6.35) |
| Parameter table, test ids | `S16.*`, `S18.*` | This part lists the parameters it adds (6.23) and acceptance ids `AC-admission-nn` (6.37) |

**Numbering.** Headings of this file are `6.20`..`6.39` so they cannot collide with the headings of the credit and ledger file of part 6; cross-reference them as `S6.20`..`S6.39` (`ISS-64`). [D]

**Rules for every number here.** A default is an `initial configurable default` that exists in 6.23 or in S0 0.10.6. An example number is an illustrative input (the FD§3.3 inputs, or an input invented in 6.36 for arithmetic only), never a measurement and never evidence about human behavior. User-facing promises say "declared", never "guaranteed" (FD Principle 11). Simulation output about admission is not evidence about real members (prompt K). [D]

## 6.21 Decisions at a glance

| Topic | Decision | Basis |
| --- | --- | --- |
| Unit of capacity | Cells executed and accepted, of every `cell_kind`. A member job commits `N + V` cells (N primary, V verification and rework cells, `V = floor(N × v_ppm / 10^6)`, ISS-04) | FD§3.3, FD§4.3 [D] |
| Forecast | Retrospective-cohort trailing mean of verified throughput of today's active donors, `B = min(W-day mean, A-day mean)`, with a per-donor daily clamp, a haircut and a per-day horizon discount | prompt C [D][H] |
| Admission test | A first-come fluid-queue test: backlog ahead plus the new cells must fit in `φ × forecast capacity − reserved cells` over the window, both globally and for the job's category | FD§4.8; `ISS-65` [D] |
| Quote | The smallest feasible window on the grid `admission.window_step_s`, never below `admission.min_window_s`; shown as a declared window | FD§4.8, Principle 10 [D] |
| Decisions | `accept`, `counter_offer` (later quote), `waitlist` | FD§4.8 [D] |
| Capacity hold | A funded quote holds capacity for `price.quote_ttl_s`; a waitlisted job holds none | [D][A] |
| Waitlist | First come, per category, no overtaking, expires after `admission.waitlist_ttl_days` | FD§4.8 [D] |
| Reservations | Absolute-grid slot plans, share-capped, escrow at booking, price locked, no monetary penalty, a cooldown after a late cancel or no-show | FD§4.8; `ISS-66` [D][A][H] |
| Fairness | Concurrent-job cap, first come within deadline class, no queue jumping by credit amount, class multiplier read from a parameter and fixed at 1.0 | FD§4.8 [D] |
| Cancellation | Unstarted cells are refunded; in-flight cells drain and are paid if accepted; capacity returns at once | FD§4.8 [D] |
| Forecast drop | Admitted jobs are never re-priced or silently cancelled; they become `at_risk`, the requester is told, a job stops only at `job.max_overrun_ratio` | FD Principle 10 [D] |
| Commons share | Preserved by three layers: the admission bound, a scheduler offer guard, a share cap on reservations | FD§4.8 [D] |
| Concurrency | One admission lock; every command is idempotent | prompt B [D] |

## 6.22 Vocabulary and derived data

| Term | Definition |
| --- | --- |
| `W`, `A` | `admission.forecast_window_days`, `admission.active_donor_window_days` |
| complete day | A UTC calendar day that has ended (S0 0.6.2); the current partial day is never used in a forecast |
| active donor | A `Member` with `status` = `active`, no engaged `kill.member.<mem_id>`, and at least `admission.active_donor_min_cells` accepted cells (any `cell_kind`) in the last `A` complete days. Trust tier is irrelevant |
| `category_key` | `<purpose>/<license>/<sensitivity>/<service_requirement>/<service_id or ->/<topic_id or ->`, for example `P1/L2/S0/M0/-/-`. It is the tuple R8 uses to decide who may see a cell. The set of keys is bounded by the `PolicyVersion` allowlist (S7.*); Phase 1 has two active profiles, FD§5.7(5) [D][A: a job carries an optional `topic_category_id`; S7.* confirms] |
| eligible donor for `category_key` c | An active donor for whom `optin_covers(member, c)` is true (R8; the evaluator is S7.*). For a pinned service (M1) or `M2`, the donor must also have the accepted-cell count above counted only on cells whose volunteer-reported service is that service (self-reported, FD§5.7(7); used for a forecast, never as proof) [D] |
| `step` | `admission.window_step_s`; every quoted window is `n × step`, `n` an integer |
| `committed_cells` | `R = ceil(( N + V ) × m_class)`, with `m_class = admission.deadline_multiplier_standard` (fixed at 1.0, so `R = N + V`) |
| `remaining(job)` | `max(0, committed_cells − accepted cells of the job so far)`; cancelled and voided cells leave `committed_cells` |
| `hold_seq` | A global, strictly increasing integer taken under the admission lock when a capacity hold is created; it is the first-come key (ledger-style ordering by sequence, never by timestamp, S0 0.6.2) |
| capacity hold | The state of a job in `quoted` with `quote.has_hold` = true, or in `admitted`, `running`, `suspended`; its `remaining` cells count in the backlog |
| `window_status` | Derived, not stored as a Job state: `on_track`, `at_risk`, `overdue`, `not_applicable` (6.33) |

**Derived data** (not entities; recomputable from cell events; no personal data beyond the opaque `mem_` id) [D][A]

| Name | Content | Retention |
| --- | --- | --- |
| `donor_day_counts` | `(member_id, day_utc, service_id or none, cells_accepted)` | `member_bound`; rows older than `W + 1` days are deleted by the rollup job |
| forecast snapshots | One `MetricSnapshot` per scope and run (`admission.forecast.all`, `admission.forecast.<category_key>`): `B`, cohort size, history days, inputs hash. Aggregates only | `permanent` |
| capacity view | The sum of `remaining` per category and the held reservations, computed on demand under the admission lock | none |

## 6.23 Parameters

**A. Parameters used (defined in S0 0.10.6; not redefined)**

| Name | Use here |
| --- | --- |
| `admission.phi`, `admission.forecast_window_days`, `admission.active_donor_window_days`, `admission.forecast_haircut` | φ, `W`, `A`, `h` (6.24) |
| `admission.min_window_s`, `admission.max_window_days` | Bounds of a quoted window (6.27) |
| `admission.max_job_cells` | Upper bound of N, validated at submission |
| `admission.max_concurrent_jobs_per_member`, `admission.waitlist_max_per_member`, `admission.waitlist_ttl_days` | Fairness and waitlist (6.29, 6.31) |
| `admission.deadline_multiplier_standard` | `m_class`; validated equal to 1.0 in Phase 1 |
| `reservation.max_horizon_days`, `reservation.max_active_per_member`, `reservation.free_cancel_notice_s`, `reservation.capacity_share_cap` | Reservations (6.30) |
| `price.quote_ttl_s`, `price.v_prior`, `price.levy_lambda`, `price.v_cap` | Quote validity; v and λ stamped into a quote come from S6.* |
| `credit.member_cap_credits`, `job.max_overrun_ratio`, `lease.timeout_s`, `lease.submit_grace_s` | Balance check, hard stop (6.33), drain time on cancel (6.32) |
| `mint.monthly_cap_credits`, `mint.per_member_daily_cap_credits`, `inflation.claim_ratio_threshold_weeks` | Commons capacity bound (6.26), donor clamp default, claim stretch (6.27) |
| `analytics.min_cohort_k`, `public.counter_refresh_s` | Suppression and refresh of the public supply gauge (6.25) |
| `launch.member_jobs_enabled`, `ff.job.reservations`, `kill.all_new_jobs`, `kill.template.<tpl_id>`, `kill.service.<svc_id>`, `kill.member.<mem_id>` | Guards (6.28) |
| `api.idempotency_ttl_s`, `change.notice_days_price` | Idempotency; notice for `admission.*` changes |

**B. Parameters added by this part** (convention gaps, report in `## Issues raised`; names follow S0 0.10.1; `S16.*` completes them without renaming)

| Name | Type | Initial configurable default | Validation | Tighten direction | Replaced by |
| --- | --- | --- | --- | --- | --- |
| `admission.active_donor_min_cells` | int | 1 | 1..1000 | up | `P1M` |
| `admission.donor_daily_clamp_cells` | int | 30 (equal to `mint.per_member_daily_cap_credits`, three times the FD§3.2 habit of about 10 cells a day) | 1..1000 | down | `P1M` capacity concentration |
| `admission.min_forecast_donors` | int | 10 (the cohort size below which a mean is noise) | 1..1000 | up | `P1M` forecast error |
| `admission.min_history_days` | int | 3 | 1..`admission.forecast_window_days` | up | `P1M` |
| `admission.horizon_discount_per_day` | ratio | 0.00 (so FD§3.3 reproduces exactly; expected to become greater than 0 [H]) | 0 <= x < 1 | up | `P1M` forecast error by horizon |
| `admission.window_step_s` | duration_s | 43,200 (equal to `admission.min_window_s`) | divides 86,400; C9 | none | `DEM` |
| `admission.reforecast_interval_s` | duration_s | 3600 (equal to `metrics.rollup_interval_s`) | 60..86400 | none | `OPS` |
| `admission.overrun_tolerance_ratio` | ratio | 0.10 | 0..1 | down | `OPS` share of windows missed |
| `admission.claim_stretch_max` | ratio | 2.0 | >= 1 | up | `FND` |
| `admission.share_window_s` | duration_s | 86,400 | 3600..604800 | none | `OPS` |
| `admission.waitlist_recheck_interval_s` | duration_s | 300 | 30..3600 | none | `OPS` |
| `admission.waitlist_quote_ttl_s` | duration_s | 86,400 (a released requester checks a few times a day [H]); C12 | 60..604800 | none | `OPS` share of released quotes confirmed |
| `reservation.min_lead_s` | duration_s | 86,400 (equal to `reservation.free_cancel_notice_s`, so a free cancel exists) | 0..`reservation.max_horizon_days` × 86,400 | up | `OPS` |
| `reservation.activation_grace_s` | duration_s | 43,200 | 0..604800 | down | `OPS` |
| `reservation.late_cancel_cooldown_days` | days | 7 | 0..90 | up | `OPS` no-show rate |

**C. Cross-parameter constraints proposed** (numbering is `S16.*`'s) [A]: `C9` `admission.min_window_s` and `admission.max_window_days × 86,400` are multiples of `admission.window_step_s`; `C10` `admission.min_history_days <= admission.forecast_window_days` and `admission.active_donor_window_days <= admission.forecast_window_days`; `C11` `reservation.min_lead_s <= reservation.max_horizon_days × 86,400`; `C12` `admission.waitlist_quote_ttl_s >= price.quote_ttl_s`.

**D. Change rules.** `admission.*` and `reservation.*` follow S0 0.10.3 and the notice `change.notice_days_price`. Tightening applies at once; loosening needs a change-log entry and notice (R10). A quote, hold or reservation keeps the parameter versions it was created under (recorded in the quote); a change never alters an existing hold or an admitted job's declared window. Lowering `admission.phi` is a tightening, so it can never invalidate an admitted job; it only affects later quotes. [D]
