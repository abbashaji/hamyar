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

## 6.24 Capacity forecasting

### 6.24.1 Estimator [D][H]

The forecast answers one question: how many cells per day will today's active donors execute and have accepted? The estimator is a **retrospective-cohort trailing mean**: take the donors who are active now, replay their verified throughput over the last `W` complete days, and use the lower of the `W`-day and the `A`-day mean.

| Element | Rule | Reason |
| --- | --- | --- |
| Cohort | Active donors (6.22), restricted to eligible donors for a category scope | Donors who left are not counted; donors who joined recently count with zeros for days before they joined, which errs low |
| Daily throughput `X(d)` | `sum over cohort members m of min(admission.donor_daily_clamp_cells, cells_accepted(m, d))` | The clamp stops one heavy donor from dominating the forecast; capacity concentration is a Phase 1 measure (FD§9) |
| `M_W`, `M_A` | Mean of `X(d)` over the newest `min(W, hist)` and `min(A, hist)` complete days; `hist` = complete days since the first accepted cell of the platform | A rise shows up slowly (through `M_W`); a fall shows up quickly (through `M_A`) |
| Base rate | `B = min(M_W, M_A)` cells per day, an exact rational | Conservative in both directions |
| Safety margins | haircut `h = admission.forecast_haircut`; horizon weight `w(d) = max(0, 1 − admission.horizon_discount_per_day × d)` for the d-th day after the forecast time; φ itself; the clamp; the `min` | The first two are the explicit margins; φ is a share, not a margin, but also keeps a buffer |
| Insufficient data | `hist < admission.min_history_days` gives reason `insufficient_history`; cohort smaller than `admission.min_forecast_donors` gives `forecast_below_min_donors`. Either makes the forecast `ok = false` | A forecast that is not trusted never accepts a job; the decision is `waitlist` (6.28) |

All quantities are exact rationals (integer numerator and denominator, 128-bit or arbitrary precision). Nothing is rounded until a capacity is displayed, and then it is **rounded down**; a comparison `integer demand <= rational capacity` needs no rounding. The ppm parameters enter as integers over 10^6. [D]

The forecast is a function of its inputs only. Its `inputs_hash` is the SHA-256 (S0 0.6.4) of the canonical JSON of the cohort size, the daily `X(d)` vector, the parameter versions and the forecast time, so the same inputs give the same snapshot and an audit can replay a quote. [D]

### 6.24.2 Pseudocode

```text
type Q = exact rational

function compute_forecast(scope, now) -> Forecast          # scope = ALL or a category_key
  W, A = params.forecast_window_days, params.active_donor_window_days
  hist = min(W, complete_days_since(platform_first_accept_day, now))
  if hist < params.min_history_days: return Forecast(ok=false, reason="insufficient_history")
  use    = newest min(W, hist) complete days            # d(1) oldest .. d(k) newest
  recent = newest min(A, hist) complete days
  cohort = { m in Member :
               m.status == active and not killed(m)
             and sum(counts(m, recent, svc_filter(scope))) >= params.active_donor_min_cells
             and (scope == ALL or optin_covers(m, scope)) }
  if |cohort| < params.min_forecast_donors:
      return Forecast(ok=false, reason="forecast_below_min_donors", n=|cohort|)
  X(d)  = sum over m in cohort of min(params.donor_daily_clamp_cells, counts(m, d, svc_filter(scope)))
  M_W   = Q(sum over d in use of X(d), |use|)
  M_A   = Q(sum over d in recent of X(d), |recent|)
  return Forecast(ok=true, B=min(M_W, M_A), n=|cohort|, hist=hist, inputs_hash=...)
  # svc_filter(scope): rows of the pinned service only when scope pins one; otherwise no filter

function phi_capacity(fc, a, b, now) -> Q        # member-job share of forecast cells in [a, b)
  total = Q(0)
  for each day index d with day_d = [now + d*86400, now + (d+1)*86400) overlapping [a, b):
      overlap = seconds in [a, b) intersect day_d
      w       = max(0, 1e6 - params.horizon_discount_ppm * d)            # ppm
      total  += fc.B * (1e6 - params.haircut_ppm)/1e6 * w/1e6 * overlap/86400
  return Q(params.phi_ppm, 1e6) * total
```

Check against FD§3.3: `B = 320` (40 donors × 8 cells), `h = 0`, `w = 1`, a 2-day window gives `phi_capacity = 0.5 × 320 × 2 = 320`, the number in `AC-admission-01`. [D]

### 6.24.3 Commons capacity bound

The same snapshot publishes `commons_cells_per_day = (1 − φ) × B(ALL) × (1 − h)` as `MetricSnapshot` key `admission.commons_capacity_cells_per_day`. `S6.*` reads it as the "forecast redeemable capacity" that bounds `mint.monthly_cap_credits` (FD§4.2). With the FD§3.3 inputs, `(1 − 0.5) × 320 × 30 = 4,800`, the initial default of `mint.monthly_cap_credits`. [D]

## 6.25 Per-category supply gauge (FD§5.7(8))

Restrictive opt-ins can starve one category while the platform as a whole has capacity. The remedy named by the FD is a per-category supply gauge that feeds the quote. [D]

| Item | Decision |
| --- | --- |
| Gauge | For every `category_key` that has a live job, a waitlist entry, a reservation or a recent quote, and for `ALL`: the `Forecast` of 6.24 with `scope` = that key. The gauge is recomputed every `admission.reforecast_interval_s` and at every quote |
| Overlap | One donor can be eligible for several categories, so category capacities are not additive. The admission test therefore applies **two** constraints, the global one and the category one; a job must satisfy both (6.27). By construction `B(category) <= B(ALL)` |
| Feeding the quote | The quote record carries `supply` = `{category_key, limiting_factor}`; `limiting_factor` is one of `global_capacity`, `category_supply`, `backlog`, `claim_pressure`, `window_bounds`. The requester sees the factor, never donor counts |
| Public gauge | `GET /v1/public/capacity` returns per category: eligible-donor bucket, `forecast_cells_per_day` and the committed share, refreshed every `public.counter_refresh_s`. A category with fewer than `analytics.min_cohort_k` eligible donors shows `"<k"` for both counts, so a small category cannot reveal individual donors (S10.*). No member id, handle or location appears [D] |
| Operator view | The admin capacity dashboard (`SCR-ops-*`, S11.*) shows exact counts, the gauge history and the forecast error of 6.33 |
| Opt-out fragmentation signal | `hamyar_admission_category_supply_ratio` = `B(category) / B(ALL)` per category; a falling ratio is the early sign of FD§5.7(8) [H: that opt-out fragmentation matters in Phase 1; test: the ratio of the two most restrictive categories over the pilot; kill criterion: ratio stays above `0.9` for every live category] |

## 6.26 φ and preservation of the Commons share

### 6.26.1 φ

`admission.phi` (φ, `0 < φ < 1`, constraint C1) is the share of forecast capacity that may be committed to member jobs and reserved for them. It is a single global value in Phase 1 [D]; a per-category φ is not specified (open decision, 6.39). The initial default 0.5 is the FD§3.3 illustrative value. It is replaced by `P1M`: measured throughput and the deposit-to-withdrawal ratio. [D][H]

### 6.26.2 Three layers that keep (1 − φ) for Commons work [D]

| Layer | Mechanism | Guarantee it gives |
| --- | --- | --- |
| L1 admission bound | Every quote, hold and reservation is tested against `φ × capacity` (6.27, 6.30) | Committed member cells cannot exceed φ of forecast capacity at the moment of admission |
| L2 offer guard | The lease scheduler uses `offer_class` below whenever a donor could be offered either a Commons cell or a member-job cell | While both classes have eligible queued cells, the member share of leases never exceeds φ in any prefix of the offers, so Commons minting continues |
| L3 reservation share cap | Reserved cells in any slot never exceed `reservation.capacity_share_cap` of the φ capacity of that slot | Reservations cannot absorb the member share and then push it over φ |
| Monitoring | `hamyar_admission_commons_share_ratio` (Commons leases divided by all leases over `admission.share_window_s`). An alarm (`Alarm`, S4.*) is raised when it stays below `1 − φ` while eligible Commons cells exist | Detects a scheduler defect |

If no eligible Commons cell exists, member cells are offered; capacity is never left idle. If no eligible member cell exists, Commons cells are offered. [D]

```text
function offer_class(donor, now) -> COMMONS | MEMBER | NONE        # called by the lease scheduler (S8.*, S9.*)
  W        = params.share_window_s
  m        = count of leases issued for member-job cells in [now - W, now)
  a        = count of leases issued for all cells in [now - W, now)
  member_ok  = exists queued member-job cell eligible for donor (R8)
  commons_ok = exists queued Commons cell eligible for donor (R8)
  if not member_ok and not commons_ok: return NONE
  if not member_ok: return COMMONS
  if not commons_ok: return MEMBER
  # both available: offer a member cell only if the member share stays <= phi afterwards
  if (m + 1) * 1e6 <= params.phi_ppm * (a + 1): return MEMBER
  return COMMONS
```

With φ = 0.5 and empty counters the first offer is Commons, the second member, then alternating. The counters are global, not per donor; a donor may receive a different mix. [A]

### 6.26.3 Scheduler contract (consumed by S5.*, S8.*, S9.*) [D]

| Id | Requirement |
| --- | --- |
| SC-1 | Within one deadline class, member-job cells are offered in ascending `hold_seq` of their job (first come) |
| SC-2 | Deadline classes are served in ascending class rank; only `standard` (rank 0) exists in Phase 1 |
| SC-3 | A reserved job gets priority for up to `slot_plan[k]` cells in absolute slot `k`; the unserved remainder of a slot is not carried over and falls back to SC-1 |
| SC-4 | `offer_class` decides the Commons versus member mix |
| SC-5 | No cell of a job is offered before the job is `admitted`; cells of a `suspended` job are not offered |
