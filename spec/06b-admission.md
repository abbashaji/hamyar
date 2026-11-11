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

## 6.27 Quoting a completion window

### 6.27.1 The admission test [D]

Service is first come (SC-1), so the cells ahead of a new job must be done before it. A window of `n` steps, `[t0, t0 + n × step)`, is **feasible** for a job needing `R` cells in scope S (S = `ALL`, and S = the job's `category_key`) when

`R + backlog(S) <= phi_capacity(fc(S), t0, t0 + n × step) − reserved_in(t0, t0 + n × step, S)`

with `backlog(S)` the sum of `remaining` over capacity-holding jobs in S (all of it counts, because first come puts it ahead), and `reserved_in` the cells of **held** reservations in S that overlap the window (an activated reservation is an ordinary job and is counted in the backlog, never in both). The job is admissible in a window only if both scopes pass. This is the FD§4.8 rule "committed cells over its window <= φ × forecast active capacity", made precise for several jobs, several categories and reservations (`ISS-65`). [D]

### 6.27.2 Claim stretch (FD§4.7)

When the published claim ratio passes its threshold, quoted windows lengthen: `stretch_ppm = clamp(claim_ratio_ppm × 10^6 / threshold_ppm, 10^6, admission.claim_stretch_max × 10^6)`, where `claim_ratio_ppm` is the latest `MetricSnapshot` `inflation.claim_ratio` (weeks of capacity, from `S6.*`) and `threshold_ppm` is `inflation.claim_ratio_threshold_weeks`. At or below the threshold the stretch is 1.0. A missing snapshot counts as 1.0 and is logged. [D]

### 6.27.3 Pseudocode

```text
function quote_job(job, requested_window_s, now) -> Quote          # caller holds admission_lock
  N, v_ppm, lam_ppm = job.cells_n, quote_inputs.v_ppm, quote_inputs.lambda_ppm    # from S6.*
  V      = floor(N * v_ppm / 1e6)                                  # ISS-04
  R      = ceil((N + V) * params.deadline_multiplier_standard)
  p_ucr  = 1_000_000 + v_ppm + lam_ppm ;  escrow_ucr = N * p_ucr
  cat    = job.category_key
  fcA, fcC = latest_or_compute_forecast(ALL, now), latest_or_compute_forecast(cat, now)
  if not fcA.ok: return decide_waitlist(fcA.reason)
  if not fcC.ok: return decide_waitlist(fcC.reason)
  bA, bC = backlog(ALL), backlog(cat)
  n_min  = ceil(params.min_window_s / step)
  n_max  = params.max_window_days * 86400 / step
  feasible(n) = for S, fc, b in ((ALL, fcA, bA), (cat, fcC, bC)):
                   R + b <= phi_capacity(fc, now, now + n*step, now) - reserved_in(now, now + n*step, S)
  L_min  = smallest n in [n_min, n_max] with feasible(n)           # linear scan; never binary search
  if none: return decide_waitlist("exceeds_max_window")
  stretch = claim_stretch_ppm()
  n_need  = smallest n in [ceil(L_min * stretch / 1e6), n_max] with feasible(n)   # else n_need = L_min
  limiting = classify(L_min, n_need)    # global_capacity | category_supply | backlog | claim_pressure | window_bounds
  req = requested_window_s / step if requested_window_s else n_need   # validated: on the grid, in bounds
  if req < n_need: return Quote(decision=counter_offer, window_s=n_need*step, ...)
  return Quote(decision=accept, window_s=req*step, ...)
```

`requested_window_s` is optional (null means earliest). It must lie in `[admission.min_window_s, admission.max_window_days × 86,400]` and be a multiple of `step`, else `VALIDATION_FAILED`. The quote never promises less than `admission.min_window_s`, so "instant" completion is never quoted (Principle 10). A requester may choose a window longer than the earliest one. [D]

### 6.27.4 Quote record [D]

Stored on the `Job` as an immutable document `quote` (the column is `S5.*`'s); a re-quote increments `quote_seq` and never edits an earlier document.

| Field | Meaning |
| --- | --- |
| `quote_seq`, `issued_at`, `expires_at` | `expires_at = issued_at + price.quote_ttl_s` (`admission.waitlist_quote_ttl_s` after a waitlist release; the activation deadline for a reserved job, 6.30) |
| `decision` | `accept`, `counter_offer`, `waitlist` |
| `reason` | For `waitlist`: `insufficient_history`, `forecast_below_min_donors`, `exceeds_max_window`, `category_no_supply`, `forecast_dropped_before_confirm` |
| `requested_window_s`, `window_s` | Declared window in seconds, a multiple of `step` (null when waitlisted) |
| `cells_n`, `verification_cells_v`, `committed_cells_r`, `class_multiplier_ppm` | N, V, R |
| `v_ppm`, `lambda_ppm`, `p_ucr`, `escrow_ucr` | Price stamped from `S6.*`; `escrow_ucr = N × p_ucr` (S0 0.6.1) |
| `category_key`, `supply.limiting_factor`, `stretch_ppm` | 6.25, 6.27.2 |
| `has_hold`, `hold_seq`, `reservation_id` | 6.28 |
| `forecast_refs` | Snapshot ids and `inputs_hash` of `fcA`, `fcC`; backlog and reserved totals used |
| `param_versions` | Versions of `admission.*`, `reservation.*`, `price.*` in force |
| `policy_version_id` | The policy stamped at screening (R9) |

The copy shown to the requester says the window is *declared*, never guaranteed (`copy.admission.window_declared`). [D]

## 6.28 Decision: accept, later quote or waitlist

### 6.28.1 Guards before the test [D]

Checked in order; the first failure refuses with the error shown and changes no state.

| # | Guard | Error |
| --- | --- | --- |
| 1 | `launch.member_jobs_enabled` is true | `403 LAUNCH_GATE_CLOSED` |
| 2 | `kill.all_new_jobs`, `kill.template.<tpl_id>`, `kill.service.<svc_id>` and `kill.member.<mem_id>` are released | `503 KILL_SWITCH_ENGAGED` |
| 3 | `N <= admission.max_job_cells` | `400 VALIDATION_FAILED` (details point to splitting the job) |
| 4 | The member's jobs in `quoted`, `admitted`, `running`, `suspended`, `assembling`, `settling`, `cancelling` number fewer than `admission.max_concurrent_jobs_per_member` (checked at `job.submitted` and again under the lock) | `422 CAP_EXCEEDED` |
| 5 | At `job.submitted`, unexpired balance is at least `N × p_ucr` at the current published price | `422 INSUFFICIENT_CREDIT` |

### 6.28.2 Decision table

| Condition (evaluated top down) | Decision | Job transition (S0 0.9.2) | Capacity hold |
| --- | --- | --- | --- |
| A forecast is not `ok` for `ALL` or for the category | `waitlist` | `job.policy_passed` then `job.waitlisted` in one transaction | none |
| No feasible window within `n_max` | `waitlist` | same | none |
| `req < n_need` (the requested window is too short) | `counter_offer` with window `n_need × step` | `job.policy_passed` (stays `quoted`) | yes if funded |
| Otherwise | `accept` with the requested or earliest window | `job.policy_passed` (stays `quoted`) | yes if funded |
| `decision = waitlist` and the member already has `admission.waitlist_max_per_member` entries (0 disables the waitlist) | refused: `422 NO_CAPACITY`; the job ends `cancelled` with `cancel_reason` = `no_capacity` | `job.cancel_requested` by `system` | none |

`quoted` is therefore always passed through, even for a waitlist decision, because S0 0.9.2 reaches `waitlisted` only from `quoted`. [D]

### 6.28.3 Holds, confirmation and expiry [D]

- **Hold.** A hold is created only if the member's unexpired balance is at least `escrow_ucr` at quote time (`has_hold` = true). An unfunded member cannot reserve capacity by opening quotes. The hold takes the next `hold_seq` and counts in every later backlog.
- **Confirm** (`confirmJobQuote`, body `{quote_seq}`; `Idempotency-Key` required). Under the admission lock: the job is `quoted`, `now < quote.expires_at`, `quote_seq` is current. With a hold, the job's own position is re-tested on `[now, now + window_s)` with only holds of smaller `hold_seq` as backlog; without a hold, a fresh test is run as for a new quote. If the window can still be honored, the system posts `escrow_hold` (S6.*), creates and queues the cells, and the job becomes `admitted` (`job.escrow_confirmed`), all in one transaction; `window_end_at = admitted_at + window_s`. If it cannot, the confirm is refused with `422 NO_CAPACITY` and `details.requote = true`, no escrow is posted, and either a new quote (`quote_seq + 1`, still `quoted`) or a `waitlist` follows according to 6.28.2 (reason `forecast_dropped_before_confirm`). If escrow cannot be funded (balance spent or a lot expired meanwhile) the answer is `422 INSUFFICIENT_CREDIT` and the job stays `quoted` until expiry.
- **Expiry.** At `expires_at` the reaper (6.34) emits `job.quote_expired` and releases the hold. The job is terminal. A counter-offer is accepted only by confirming it.
- **Cancel** from `quoted` releases the hold at once (`job.cancel_requested` to `cancelled`).
- **Events.** Besides S0 events, `admission.quote_issued` is logged per quote (6.34).

## 6.29 Waitlist

### 6.29.1 `WaitlistEntry` fields required by admission [D][A]

(`S5.*` owns the DDL; prefix `wlt_`, retention `job_bound`.)

| Field | Type | Rule |
| --- | --- | --- |
| `id`, `job_id`, `member_id` | text | `job_id` unique among entries with `status` = `waiting` |
| `category_key`, `committed_cells_r`, `requested_window_s` | text, int, int | Copied from the quote |
| `waitlist_seq` | int | Strictly increasing under the admission lock; the first-come key |
| `reason` | enum | As in 6.27.4 |
| `status` | enum | `waiting`, `released`, `expired`, `cancelled` |
| `created_at`, `expires_at`, `last_evaluated_at` | timestamptz | `expires_at = created_at + admission.waitlist_ttl_days × 86,400 s` |

A waitlisted job holds no capacity and no escrow. The requester sees the position (`1 +` earlier `waiting` entries of the same category), the reason, and the expiry; no completion estimate is invented.

### 6.29.2 Release and expiry [D]

- **Triggers:** capacity freed (`job.settled`, `job.settled_partial`, `job.cancel_settled`, `job.quote_expired`, a reservation ending), a forecast that rises, and a timer every `admission.waitlist_recheck_interval_s`.
- **Order and no overtaking.** Entries are evaluated in ascending `waitlist_seq`. When an entry is still infeasible, its category is blocked for the rest of the sweep: later entries of the same category are skipped, so a small late job cannot starve a large early one. Entries of other categories are still evaluated; the global constraint keeps them honest. Utilization cost of this rule is measured (`hamyar_admission_waitlist_wait_s`, [H]).
- **Release.** A feasible entry becomes `released`; the job moves `waitlisted` to `quoted` (`job.waitlist_released`) with a fresh quote, a hold if funded, and `expires_at = now + admission.waitlist_quote_ttl_s`. The longer TTL stops a requester who is away from losing a place after one missed quote; a missed quote still ends the job (`job.quote_expired`).
- **Expiry.** At `expires_at` the entry is `expired` and the job `cancelled` (`job.waitlist_expired`); no refund is needed.
- **Cancel.** `job.cancel_requested` from `waitlisted` marks the entry `cancelled`.
- While `kill.all_new_jobs` is engaged or `launch.member_jobs_enabled` is false, no entry is released; entries still age and expire. [D]

```text
function release_waitlist(now)                                   # holds admission_lock
  blocked = {}
  for e in entries where status == waiting order by waitlist_seq:
      if e.expires_at <= now: expire(e); continue
      if e.category_key in blocked: continue
      q = quote_job(e.job, e.requested_window_s, now)
      if q.decision == waitlist: blocked.add(e.category_key); continue
      mark_released(e); transition(e.job, job.waitlist_released); issue(q, ttl=params.waitlist_quote_ttl_s)
```

## 6.30 Capacity reservations for future dates

A requester may book capacity for a future date (exam week, a deadline) with credit escrowed at booking (FD§4.8). Effectiveness in flattening bursts is [H]; test: share of peak-day committed cells coming from reservations and the no-show rate; kill criterion: no-show rate above 0.30 of reservations over the pilot, in which case `ff.job.reservations` is switched off. [H]

### 6.30.1 `Reservation` fields required by admission [D][A]

(`S5.*` owns the DDL; prefix `rsn_`, retention `job_bound`, states `held`, `activated` (T), `cancelled` (T), `expired` (T) and events `reservation.*` as in S0 0.9.8.)

| Field | Rule |
| --- | --- |
| `member_id`, `category_key`, `job_type` | Declared at booking; the job later created must have the same `category_key` and `job_type` |
| `cells_n`, `verification_cells_v`, `committed_cells_r` | As in 6.22; `R` is what is reserved |
| `v_ppm`, `lambda_ppm`, `p_ucr`, `escrow_ucr`, `escrow_id` | **Price lock**: stamped at booking, used at activation. A locked price is at most `reservation.max_horizon_days` old; a later published change of `price.*` does not apply to an existing reservation, and the booking screen shows the locked price and the lock date [D][A] |
| `target_start_at`, `window_s` | `target_start_at` on the absolute grid (a multiple of `step` since the UTC epoch); `window_s` a multiple of `step` in `[admission.min_window_s, admission.max_window_days × 86,400]` |
| `activation_deadline_at` | `target_start_at + reservation.activation_grace_s` |
| `slot_plan` | Integer cells per absolute slot, below |
| `degraded` | Boolean; true when a forecast drop removed its priority (6.33) |
| `job_id`, `cancel_reason`, `late_cancel` | Set at activation or end; `cancel_reason` in `member_requested`, `expired`, `operator`, `policy_stopped`, `degraded_release` |

### 6.30.2 Booking [D]

Guards, in order: 6.28.1 guards 1 to 3 and `ff.job.reservations` (else `403 FORBIDDEN`); the member has fewer than `reservation.max_active_per_member` `held` reservations (else `422 CAP_EXCEEDED`); no cooldown is running (`now` is at least `late_cancel_at + reservation.late_cancel_cooldown_days × 86,400 s` for the member's latest late cancel or expiry, else `422 CAP_EXCEEDED` with `details.copy_key` = `copy.admission.late_cancel_cooldown`); `now + reservation.min_lead_s <= target_start_at <= now + reservation.max_horizon_days × 86,400 s` (else `400 VALIDATION_FAILED`); unexpired balance at least `escrow_ucr` (else `422 INSUFFICIENT_CREDIT`).

**Slot plan.** The window covers `m = window_s / step` absolute slots `k0 .. k0+m-1`. Cells are spread by largest remainder: slot `k0+i` gets `floor(R / m) + (1 if i < R mod m else 0)`. The plan always sums to `R`.

**Share cap.** For every slot `k` and for both scopes (`ALL` and the category) the booking is accepted only if `held_plan(S, k) + plan[k] <= reservation.capacity_share_cap × phi_capacity(fc(S), slot_k) `, evaluated with the forecast at booking time (exact rational comparison). A forecast that is not `ok` refuses the booking with `422 NO_CAPACITY`. Reservations are not queued on a waitlist. [D]

**Escrow at booking.** In one transaction: `escrow_hold` of `escrow_ucr` from the member into a new `Escrow` bound to the reservation (S0 0.8.5), the `Reservation` row in `held`, event `reservation.held`. Lots are consumed oldest-first as for any `escrow_hold`.

### 6.30.3 Activation, release and expiry [D]

| Situation | Effect |
| --- | --- |
| The member creates a job with `reservation_id` (any time after booking) | The job goes through `draft`, `screening` and policy as usual (R1..R10, R9 stamp). It passes `job.policy_passed` into `quoted` with a quote of decision `accept`, no admission test, the locked price, `reservation_id` set and `expires_at = activation_deadline_at`. It must satisfy `cells_n <= reservation.cells_n`, the same `category_key` and `job_type`, else `422 UNPROCESSABLE`. Extra cells beyond the reservation are a separate job through normal admission |
| `now >= target_start_at` | The system re-checks policy (R9), then in one transaction posts `escrow_release` of `cells_n × p_ucr` from the reservation escrow to the job escrow, refunds the difference to the member (`refund`), emits `reservation.activated` and `job.escrow_confirmed`; the job becomes `admitted`; `window_end_at = target_start_at + window_s`. The reserved slot plan stops counting in `reserved_in` and the job's `remaining` joins the backlog; priority per slot is SC-3 |
| Policy now rejects the job | The system cancels the job (`cancel_reason` = `policy_stopped`) and the reservation (`cancel_reason` = `policy_stopped`) with a full refund and no cooldown |
| No admitted job by `activation_deadline_at` | Event `reservation.expired`; full refund; the cooldown applies (`late_cancel` = true); capacity returns at once |
| Member cancels (`cancelReservation`) at or before `target_start_at − reservation.free_cancel_notice_s` | `reservation.cancelled`; full refund; no cooldown |
| Member cancels after that moment | Same refund; `late_cancel` = true; the cooldown applies. There is **no monetary penalty**: a fee needs a new ledger entry type, and the FD says credit is never printed or created (FD§4.6); a fee is an open owner decision (`ISS-66`, 6.39) |
| Degraded by a forecast drop (6.33) | The holder is told and may cancel at once; such a cancel never sets `late_cancel` |

A refund restores the consumed lots with their original expiry (`ISS-07`). A reservation made far ahead can therefore be funded by lots that expire before a cancellation or expiry refund; a restored lot already past expiry moves to the Reserve at the next sweep. The booking confirmation must say so for every consumed lot that expires before `target_start_at + window_s` (`copy.admission.reservation_expiry_warning`), and the screen shows the expiry dates (`ISS-66`). Escrowed credit that is *spent* on activated cells is unaffected. [D]

## 6.31 Fairness rules

| Id | Rule | Enforced where |
| --- | --- | --- |
| FR-1 | At most `admission.max_concurrent_jobs_per_member` jobs in the capacity-holding states of 6.28.1 guard 4, per member | `job.submitted`, again under the lock |
| FR-2 | First come within a deadline class: order by `hold_seq` (and by `waitlist_seq` for waiting entries). A re-quote of a job takes a new `hold_seq` only if its earlier hold was released | 6.27, SC-1 |
| FR-3 | No overtaking within a category on the waitlist (6.29.2) | `release_waitlist` |
| FR-4 | No queue jumping by credit: price is not a bid, a larger balance or a higher escrow buys no position | by construction |
| FR-5 | Deadline classes: `R = ceil((N + V) × m_class)` and classes are served in rank order. In Phase 1 only `standard` exists and `admission.deadline_multiplier_standard` is validated equal to 1.0; the code path reads the parameter. A multiplier other than 1.0 affects capacity accounting only; its effect on price is not specified and needs a spec change [D] | 6.22, SC-2 |
| FR-6 | Job size is bounded by `admission.max_job_cells`; the size is part of the guard, not a priority input | 6.28.1 |
| FR-7 | A waitlist cap per member (`admission.waitlist_max_per_member`) and one live reservation (`reservation.max_active_per_member`) | 6.28.2, 6.30.2 |
| FR-8 | Reserved capacity of any slot is at most `reservation.capacity_share_cap` of its φ capacity | 6.30.2 |
| FR-9 | Only members with `status` = `active` can quote, book or confirm; `suspended`, `banned` and `closed` members cannot. `restricted` tier changes only the credit cap (`trust.cap_multiplier.restricted`), not queue position | guards |

## 6.32 Cancellation and refunds

Posting mechanics belong to `S6.*`; the table states what is refundable and when capacity returns. [D]

| State at `job.cancel_requested` | Effect | Refund |
| --- | --- | --- |
| `draft`, `waitlisted` | Job `cancelled`; a waiting entry is `cancelled` | none (no escrow) |
| `quoted` | Hold released; job `cancelled` | none |
| `admitted` (no cell leased) | `cancelling`; every cell `cancelled`; `job.cancel_settled` | the whole escrow |
| `running`, `suspended` | `cancelling`. Cells in `queued` or `suspended` are `cancelled` at once. Leased cells drain: each lease may still be submitted until `lease.timeout_s + lease.submit_grace_s` after the request; an accepted cell is paid, a rejected or expired one is `cancelled`. Then `job.cancel_settled` | the unspent part below |

Capacity returns when the cells are cancelled, not when settlement ends; the waitlist sweep (6.29.2) is triggered at that moment.

**Unspent part.** Let `a` be accepted primary cells, `b` accepted verification, audit and rework cells, `N`, `v_ppm`, `lambda_ppm` as stamped in the quote. Donors are paid `(a + b) × 1,000,000 ucr` by `transfer` at acceptance; the Reserve receives the levy `a × lambda_ppm`; the rest returns to the requester:

`refund_ucr = escrow_ucr − (a + b) × 1,000,000 − a × lambda_ppm`, with `escrow_ucr = N × (1,000,000 + v_ppm + lambda_ppm)`.

Since `b <= V = floor(N × v_ppm / 1,000,000)`, the unused verification pool `N × v_ppm − b × 1,000,000` is not negative. With the FD§3.3 inputs and `a = 240`, `b = 24` the refund is 0 and the identity closes (264,000,000 + 12,000,000 = 276,000,000); with `a = 100`, `b = 5` the refund is `276,000,000 − 105,000,000 − 5,000,000 = 166,000,000 ucr`, which equals the unaccepted primary share (140,000,000) plus the unused pool (19,000,000) plus the unused levy (7,000,000). The formula is the arithmetic check of `AC-admission-06`; if `S6.*` states the settlement rule differently, `S6.*` wins and this check is updated. [D][A]

## 6.33 Behaviour when the forecast drops after acceptance

### 6.33.1 Principles [D]

1. An admitted job is **never** re-priced, never silently cancelled and never moved behind later jobs because the forecast fell. Its declared window stays what it was quoted (Principle 10; the copy says "declared").
2. The requester is told early and plainly when the projection moves beyond the declared window.
3. New quotes become honest at once, because they are computed from the new forecast and the unchanged backlog (6.27); no separate intake freeze is needed. An intake freeze, an automatic increase of φ, a silent re-quote, and cancelling the newest jobs were considered and rejected: the first duplicates what the backlog already does, the second takes capacity from Commons work and breaks (1 − φ), the last two break principle 1.
4. A hard stop exists: at `job.max_overrun_ratio × window_s` after `admitted_at` the system emits `job.stop_requested` with `closure_reason` = `overrun_timeout`; accepted cells are paid, everything else is refunded (6.32 formula with the cells accepted so far). Any make-good for such a job is an owner decision (6.39).

### 6.33.2 `window_status` (derived, evaluated by the reforecast job) [D]

| Value | Condition |
| --- | --- |
| `not_applicable` | job not in `admitted`, `running`, `suspended` |
| `on_track` | `projected_finish_at <= window_end_at + admission.overrun_tolerance_ratio × window_s` |
| `at_risk` | `projected_finish_at` is later than that, and `now <= window_end_at` |
| `overdue` | `now > window_end_at` and the job is not complete |

`projected_finish_at` is the earliest `T` such that, in both scopes, the cells of all jobs placed before or at this job (reserved jobs with unspent slot budget first, then ascending `hold_seq`), counting this job's own `remaining`, are at most `phi_capacity(fc(S), now, T) − reserved_in(now, T, S)`; if no `T` within `job.max_overrun_ratio × window_s` exists the value is `null` and the status is `at_risk`. A `suspended` job's projection is shown but its status is `on_track` while the suspension is active (whether the window clock pauses is decided by `S5.*`; that dependency is flagged to `S5.*`).

### 6.33.3 Pseudocode

```text
function reforecast(now)                                           # job every admission.reforecast_interval_s
  with admission_lock:
    for scope in {ALL} + live category_keys: fc[scope] = compute_forecast(scope, now); store MetricSnapshot
    record forecast_error: for each complete day d not yet scored,
        error_ppm = (actual_accepted_cells(d) - predicted_cells(d)) * 1e6 / predicted_cells(d)   # signed
    degrade_reservations(now)
    for job in capacity-holding jobs (admitted, running, suspended) order by priority, hold_seq:
        old = job.window_status ; new = compute_window_status(job, now)
        if new != old: persist; emit admission.window_at_risk | window_recovered | window_missed; notify requester
        if now > job.admitted_at + params.max_overrun_ratio * job.window_s: request_stop(job, "overrun_timeout")
    release_waitlist(now)                                            # capacity may have risen
    run consistency checks (6.34.4)

function degrade_reservations(now)           # newest booking is degraded first (last in, first out)
  for scope in (ALL, categories): for slot k with held_plan(scope, k) > share_cap * phi_capacity(fc(scope), slot_k):
      for r in held reservations covering slot k in scope ordered by created_at desc until the slot fits:
          r.degraded = true ; emit admission.reservation_degraded ; notify holder
```

A degraded reservation keeps its escrow, loses SC-3 priority and stops counting in `reserved_in`; at activation its job joins the ordinary first-come queue behind existing jobs. The holder may cancel without cooldown. [D]

### 6.33.4 Forecast error and calibration [D][H]

The signed daily `error_ppm` is aggregated (never per member) and published as `hamyar_admission_forecast_error_ratio`. It is the measurement that replaces `admission.forecast_haircut`, `admission.horizon_discount_per_day` and, together with the deposit-to-withdrawal ratio, φ (`P1M`). [H: with a clean 14-day history the trailing mean overstates next-week capacity because of churn; test: the median signed error over the pilot; success: the median error is within the margin the haircut covers; kill criterion: error beyond 0.25 in magnitude on more than a quarter of days, in which case `admission.min_forecast_donors` is raised and the haircut set from the data.]

## 6.34 Concurrency, operations, events and metrics

### 6.34.1 Concurrency and idempotency [D]

- **One admission lock.** Quote, confirm, hold release, waitlist release, reservation booking, activation, cancellation and the reforecast run hold a single mutual-exclusion lock named `admission` (a serializable transaction or an advisory lock). Hold time is bounded by `api.request_timeout_s`. Phase 1 member-job volume is low, so a global lock is acceptable; per-scope sharding is not possible because the global test spans all categories [A].
- `hold_seq` and `waitlist_seq` come from database sequences read under the lock; they are never reused.
- **Idempotency.** Every command above takes `Idempotency-Key` (S0 0.11.5). Natural idempotency underneath: one quote document per `(job_id, quote_seq)`, one live hold per job, one `escrow_hold` per job, one reservation escrow per reservation, one `escrow_release` per activation. A retried confirm after success returns the stored result and posts nothing.
- **Race guarantee.** Two simultaneous quotes or confirms are serialized; the later one sees the earlier hold in its backlog. Joint admission beyond capacity is impossible.

### 6.34.2 Background jobs [D]

| Job | Cadence | Does |
| --- | --- | --- |
| `admission.reforecast` | `admission.reforecast_interval_s` | 6.33.3 |
| `admission.waitlist_sweep` | `admission.waitlist_recheck_interval_s` and the triggers of 6.29.2 | `release_waitlist` |
| `admission.hold_reaper` | every `lease.reap_interval_s` [A] | `job.quote_expired`, hold release; entry expiry (`job.waitlist_expired`) |
| `admission.reservation_watch` | same | activation at `target_start_at`, expiry at `activation_deadline_at` |
| `admission.rollup` | daily after the UTC boundary | fills `donor_day_counts`, deletes rows older than `W + 1` days |

Every job is idempotent: running twice on the same inputs produces the same state and no second event.

### 6.34.3 Events and metrics [D][A]

Domain events used: `job.*` and `reservation.*` of S0 0.9. Events added by this part (logged under the same names, no personal data): `admission.forecast_recomputed`, `admission.quote_issued`, `admission.hold_released`, `admission.window_at_risk`, `admission.window_recovered`, `admission.window_missed`, `admission.reservation_degraded`, `admission.consistency_violated`.

Metrics (S0 0.5 scheme): `hamyar_admission_decisions_total` (by decision), `hamyar_admission_forecast_capacity_cells` (by scope), `hamyar_admission_active_donors_count`, `hamyar_admission_committed_cells`, `hamyar_admission_utilization_ratio` (backlog of `ALL` divided by the φ capacity of a maximum-length window), `hamyar_admission_waitlist_length_count`, `hamyar_admission_waitlist_wait_s`, `hamyar_admission_window_at_risk_total`, `hamyar_admission_window_missed_total`, `hamyar_admission_completion_vs_quote_ratio` (actual time from `admitted_at` to completion divided by `window_s`; the FD§9 "time to complete a large job versus quote" measure), `hamyar_admission_forecast_error_ratio`, `hamyar_admission_commons_share_ratio`, `hamyar_admission_category_supply_ratio`, `hamyar_admission_reservation_noshow_ratio`.

### 6.34.4 Consistency checks (run by `admission.reforecast`; a failure raises an `Alarm` and `admission.consistency_violated`) [D]

| Check | Statement |
| --- | --- |
| Hold integrity | Every capacity-holding job has exactly one `hold_seq`; no `hold_seq` belongs to a terminal job |
| Entry integrity | A `waiting` entry exists exactly for each `waitlisted` job |
| Member caps | No member exceeds `admission.max_concurrent_jobs_per_member`, `admission.waitlist_max_per_member` or `reservation.max_active_per_member` |
| Reservation caps | For every slot, held non-degraded plans are at most `reservation.capacity_share_cap` of the φ capacity, or the reservation is flagged `degraded` |
| Escrow link | Every `held` reservation has an `Escrow` in `open` with `escrow_ucr`; every `activated` reservation has a closed reservation escrow |
| No orphan capacity | With no non-terminal job and no held reservation, backlog and reserved totals are zero |

## 6.35 API surface and copy keys

Operation ids and paths are proposals for `S15.*`; conventions of S0 0.11 apply (member scheme, `/v1`, `Idempotency-Key` on every write, ETag where the resource is mutable). [A]

| `op` | Method and path | Purpose | Errors beyond the common ones |
| --- | --- | --- | --- |
| `confirmJobQuote` | `POST /v1/jobs/{job_id}/confirmation` body `{quote_seq}` | 6.28.3 | `422 NO_CAPACITY` (`details.requote`), `422 INSUFFICIENT_CREDIT`, `409 STATE_CONFLICT` (also for an expired quote) |
| `requestJobQuote` | `POST /v1/jobs/{job_id}/quotes` body `{requested_window_s?}` | Re-quote while `quoted` or after a release | `422 CAP_EXCEEDED`, `403 LAUNCH_GATE_CLOSED`, `503 KILL_SWITCH_ENGAGED` |
| `cancelJob` | `POST /v1/jobs/{job_id}/cancellation` | 6.32 | `409 STATE_CONFLICT` |
| `createReservation` | `POST /v1/reservations` | 6.30.2 | `422 CAP_EXCEEDED`, `422 NO_CAPACITY`, `422 INSUFFICIENT_CREDIT` |
| `getReservation`, `listReservations` | `GET /v1/reservations/{id}`, `GET /v1/reservations` | Read | `404 NOT_FOUND` |
| `cancelReservation` | `POST /v1/reservations/{id}/cancellation` | 6.30.3 | `409 STATE_CONFLICT` |
| `getPublicCapacity` | `GET /v1/public/capacity` | Public gauge, 6.25 | none |
| `getAdminCapacity` | `GET /v1/admin/capacity` | Operator dashboard: exact counts, backlog, forecast history, error | `403 FORBIDDEN` |

Copy keys used (text in `fa` and `en`, marker `needs_human_and_legal_review`, owned by `S11.*`; intent only here): `copy.admission.window_declared` (the window is a declared estimate, not a promise of completion), `copy.admission.counter_offer` (a later window is available and why, by `limiting_factor`), `copy.admission.waitlisted` (position, reason, expiry; nothing is held or charged), `copy.admission.window_at_risk` (the projection moved; what happens next), `copy.admission.reservation_expiry_warning` (lots that expire before the reserved date), `copy.admission.late_cancel_cooldown`, `copy.admission.cancel_refund_summary`, `copy.admission.supply_gauge_suppressed`. [D]

## 6.36 Worked numeric examples

All inputs are illustrative: the FD§3.3 inputs (WE-1) or inputs chosen here only to exercise the arithmetic (WE-2 to WE-7). None is a measurement. Common settings: φ = 0.5, `h` = 0, `admission.horizon_discount_per_day` = 0, `step` = 43,200 s (12 h), `admission.min_window_s` = 43,200, `admission.max_window_days` = 14 (so `n_max` = 28), `v_ppm` = 100,000, `lambda_ppm` = 50,000, 40 active donors each with 8 accepted cells on each of the last 14 complete days. Then `X(d) = 320`, `B = 320` cells per day, and one 12-hour slot has φ capacity `0.5 × 320 × 0.5 = 80` cells.

| Case | Inputs and arithmetic | Result |
| --- | --- | --- |
| WE-1 (FD§3.3) | N = 240; `V = floor(240 × 100,000 / 10^6) = 24`; `R = 264`; `p_ucr = 1,150,000`; `escrow_ucr = 240 × 1,150,000 = 276,000,000`. Feasible window: `264 <= 80 n` gives `n >= 3.3`, so `n = 4` (n = 3 gives 240 < 264). Capacity over 2 days: `0.5 × 320 × 2 = 320 >= 264`. Requested window 2 days | `accept`, declared window 2 days (172,800 s); Sara (300 credits) keeps 24 credits after escrow |
| WE-1 boundary | Same job, 33 donors: `B = 264`, 2-day capacity `0.5 × 264 × 2 = 264 >= 264` (equality is admitted). 32 donors: `B = 256`, `n = 4` gives 256 < 264, `n = 5` gives `0.5 × 256 × 2.5 = 320` | 33 donors: `accept` 2 days. 32 donors: `counter_offer` 2.5 days |
| WE-2 counter-offer | A second member, N = 100, immediately after WE-1: `V = 10`, `R = 110`, backlog 264, total 374; `374 <= 80 n` gives `n = 5` (400); n = 4 gives 320 < 374. Requested 2 days | `counter_offer` 2.5 days (216,000 s), `limiting_factor` = `backlog` |
| WE-3 category supply | Category `P0/L0/S1/M1/svc_x/-` has 12 eligible donors, each 8 cells a day on that service: `B(category) = 96`, slot capacity `0.5 × 96 × 0.5 = 24`. Job R = 110, no other backlog. Global needs `n = 2` (160 >= 110); category needs `110 <= 24 n`, `n = 5` | `counter_offer` 2.5 days, `limiting_factor` = `category_supply` |
| WE-4 waitlist | Backlog of `ALL` is 2,000 cells; a job with N = 300 (`V = 30`, `R = 330`, `escrow_ucr = 345,000,000`, within `admission.max_job_cells` and under the initial K of 350 credits). Capacity at `n_max`: `80 × 28 = 2,240`; `2,000 + 330 = 2,330 > 2,240`. Also: 8 eligible donors (below `admission.min_forecast_donors`) | `waitlist`, reasons `exceeds_max_window` and `forecast_below_min_donors`; no hold, no escrow |
| WE-5 forecast drop | WE-1 job admitted; the cohort falls to 28 donors: `B = 224`, φ rate 112 per day. Remaining 264: `projected = 264 / 112 = 2.357` days. Threshold `2 + 0.10 × 2 = 2.2` days. A new job R = 110: `374 <= 56 n` gives `n = 7` | WE-1 job `at_risk`, requester notified, price and window unchanged; hard stop at `2.0 × 2 = 4` days; the new job gets a 3.5-day counter-offer |
| WE-6 reservation | R = 264 for a future start. Slot capacity 80, share cap `0.25 × 80 = 20` cells per slot. `20 m >= 264` gives `m >= 13.2`, so `m = 14` slots (7 days); 13 slots hold only 260. Plan: `floor(264 / 14) = 18`, remainder 12, so 12 slots of 19 and 2 of 18 (`12 × 19 + 2 × 18 = 264`). Escrow at booking 276,000,000 ucr | A 6.5-day window is refused (`NO_CAPACITY`); a 7-day window is held; a cancel at least 24 h before the start refunds everything with no cooldown |
| WE-7 claim stretch | Published claim ratio 9 weeks, threshold 6 weeks: `stretch_ppm = 9 × 10^6 / 6 = 1,500,000`. WE-1 with `L_min = 4` steps: `ceil(4 × 1.5) = 6` steps | The earliest quote is 3 days; requested 2 days gives `counter_offer` 3 days, `limiting_factor` = `claim_pressure` |

## 6.37 Acceptance criteria

Ids follow S0 0.5. The `T-*` ids are assigned by `S18.*`; each criterion names the layer it belongs to. `AC-admission-01` is the admission row of the FD§3.3 reproduction and must be implemented as the same fixture as `AC-ledger-01` / `T-unit-01` (S0 0.6.1). [D]

| Id | Layer | Given | When | Then |
| --- | --- | --- | --- | --- |
| `AC-admission-01` | unit | **The FD§3.3 admission example.** 40 active donors, 8 accepted cells each on each of 14 complete days; `admission.phi` = 500,000 ppm; haircut 0; discount 0; `v_ppm` = 100,000; `lambda_ppm` = 50,000; Sara holds 300 credits | Sara submits N = 240 with `requested_window_s` = 172,800 and the policy passes | `V` = 24; `R` = 264; `p_ucr` = 1,150,000; `escrow_ucr` = 276,000,000; `B` = 320; `phi_capacity` over 2 days = 320 and `320 >= 264`; `feasible(3)` is false (240 < 264) and `feasible(4)` is true; decision `accept`, `window_s` = 172,800; a hold exists; on confirm the escrow is posted and Sara's balance is 24,000,000 ucr; with `requested_window_s` = 129,600 the decision is `counter_offer` at 172,800 |
| `AC-admission-02` | unit | As 01 with 33 donors, then 32 donors | The same job is quoted | 33 donors: `accept` at 2 days (264 = 264). 32 donors: `counter_offer` at 216,000 s |
| `AC-admission-03` | unit | WE-1 job holds capacity; a second job N = 100 | It is quoted with a 2-day request | `counter_offer` at 216,000 s; `limiting_factor` = `backlog` |
| `AC-admission-04` | unit | WE-3 category with 12 eligible donors | A job R = 110 is quoted | `counter_offer` at 216,000 s; `limiting_factor` = `category_supply` |
| `AC-admission-05` | unit | WE-4 inputs; also a history of 2 complete days | A job is quoted | Decision `waitlist` with reasons `exceeds_max_window`, `forecast_below_min_donors`, `insufficient_history` respectively; the job ends in `waitlisted` through `quoted`; a `WaitlistEntry` with the next `waitlist_seq` exists; no hold, no `escrow_hold` |
| `AC-admission-06` | unit | A job N = 240 with 100 primary and 5 verification cells accepted | The job is cancelled | Donors received 105,000,000 ucr, the Reserve 5,000,000, the member 166,000,000; the three sum to 276,000,000; capacity returns when the unstarted cells are cancelled |
| `AC-admission-07` | fsm | A member with `admission.max_concurrent_jobs_per_member` jobs in capacity-holding states | The member submits another job | `422 CAP_EXCEEDED`; no state change, no hold |
| `AC-admission-08` | fsm | A funded quote with a hold | `price.quote_ttl_s` elapses | `job.quote_expired`; the hold is released; backlog falls by `R`; the waitlist sweep runs |
| `AC-admission-09` | fsm | Waiting entries A (seq 1, large, infeasible) and B (seq 2, small, feasible) in one category, and C in another category, feasible | A sweep runs | B is not released (no overtaking); C is released; after capacity rises A and then B are released in that order |
| `AC-admission-10` | fsm | The WE-6 reservation | A 6.5-day booking, a 7-day booking, a cancel 25 h before the start, a cancel 23 h before the start, a no-show | Refused with `NO_CAPACITY`; held with escrow and a slot plan summing to 264; free cancel with full refund; late cancel with full refund and a cooldown of `reservation.late_cancel_cooldown_days`; `reservation.expired`, full refund, cooldown |
| `AC-admission-11` | fsm | A reservation with a job at `target_start_at` | The system activates it | One `escrow_release` of `cells_n × p_ucr`, the excess refunded, `reservation.activated`, `job.escrow_confirmed`, the slot plan no longer counted in `reserved_in` |
| `AC-admission-12` | sim | WE-5 | The cohort falls to 28 donors | The job is `at_risk` within one `admission.reforecast_interval_s`, price and window unchanged, requester notified; at 4 days `job.stop_requested` with `overrun_timeout` and a partial refund |
| `AC-admission-13` | fsm | `launch.member_jobs_enabled` false, then `kill.all_new_jobs` engaged | A quote is requested | `403 LAUNCH_GATE_CLOSED`, then `503 KILL_SWITCH_ENGAGED`; no hold, no entry, no event beyond the refusal |
| `AC-admission-14` | adv | Capacity for exactly one of two simultaneous confirms | Both are sent | Exactly one job is `admitted`; the other gets `NO_CAPACITY` with `requote`; no double escrow |
| `AC-admission-15` | unit | A category with 9 eligible donors and `analytics.min_cohort_k` = 10 | The public gauge is read | The category shows `"<k"` for both counts; no member data |
| `AC-admission-16` | unit | φ = 0.5, both classes always available | 6 consecutive `offer_class` calls | COMMONS, MEMBER, COMMONS, MEMBER, COMMONS, MEMBER |
| `AC-admission-17` | adv | A confirm retried with the same `Idempotency-Key` | After a successful confirm | The stored response with `Idempotent-Replayed: true`; no second `escrow_hold`, hold or cell set |

## 6.38 Property-based test properties for admission control

Generators: random sequences of quote, confirm, expire, cancel, complete, reservation and forecast-change commands over random members, categories, N, requested windows and forecasts; parameters drawn inside their validation ranges; integer arithmetic checked against an exact-rational oracle. Each property is a criterion with layer `prop`. [D]

| Id | Property (for all generated inputs) |
| --- | --- |
| `AC-admission-20` | **Soundness at admission.** For every job admitted or quoted with a hold, at the moment of the decision `R + backlog(S) <= phi_capacity(...) − reserved_in(...)` holds in both scopes, evaluated by an independent oracle |
| `AC-admission-21` | **Monotone in capacity.** Raising `B`, raising φ, or lowering the haircut or the discount never lengthens the quoted window and never worsens the decision (`accept` before `counter_offer` before `waitlist`) |
| `AC-admission-22` | **Monotone in demand.** Raising N, `v_ppm`, the backlog or the reserved cells never shortens the quoted window |
| `AC-admission-23` | **Tightening cannot invalidate.** Lowering φ changes no admitted job's declared window and cancels nothing; it only changes later decisions |
| `AC-admission-24` | **Window bounds.** Every `accept` or `counter_offer` window is a multiple of `step` and lies in `[admission.min_window_s, admission.max_window_days × 86,400]`; a quote is never 0 |
| `AC-admission-25` | **Determinism.** The same snapshot, backlog, parameter versions and inputs give the same quote and `inputs_hash`; a replayed command creates no second hold |
| `AC-admission-26` | **First come.** Among capacity-holding jobs of one class, service order is ascending `hold_seq`; a waitlist release order is ascending `waitlist_seq` within a category; no entry is released while an earlier entry of its category is infeasible |
| `AC-admission-27` | **Member caps.** At no point does a member exceed the concurrent-job, waitlist or reservation caps, under any interleaving |
| `AC-admission-28` | **No leaked capacity.** After every job and reservation is terminal, backlog and reserved totals are 0; a terminal job's `hold_seq` is released |
| `AC-admission-29` | **Reservation soundness.** For every slot, held non-degraded plans are at most `reservation.capacity_share_cap` of the φ capacity in each scope; every plan sums to its `R`; the escrow released at activation plus the refund equals the reservation's `escrow_ucr` |
| `AC-admission-30` | **Conservation on cancel.** `payouts + levy + refund = escrow_ucr` exactly for every cancel point, with `refund >= 0` and `refund >=` the unaccepted primary share |
| `AC-admission-31` | **Commons share.** In any stationary run in which eligible Commons and member cells are both always queued, the member share of leases in every prefix is at most φ (`m <= phi × a`) |
| `AC-admission-32` | **Forecast is conservative.** Lowering any cohort member's daily counts, or removing a cohort member, never raises `B`; `B <= min(M_W, M_A)`; the clamp never lets one donor contribute more than `admission.donor_daily_clamp_cells` a day |
| `AC-admission-33` | **Exact arithmetic.** Capacities are never rounded up; every comparison is exact; no int64 overflow at the maximum values of the validation ranges |
| `AC-admission-34` | **Race safety.** Under concurrent quotes and confirms the admitted set always satisfies `AC-admission-20` at admission time; no two confirms jointly exceed capacity |
| `AC-admission-35` | **No clawback.** No command or reforecast ever re-prices, cancels or re-orders an admitted job except `job.stop_requested` at `job.max_overrun_ratio`, an operator action, or a policy or service stop |
| `AC-admission-36` | **Gauge privacy.** A public gauge row never exposes a count below `analytics.min_cohort_k` and never an id |

## 6.39 Hypotheses, calibration and open decisions

| Tag | Statement | Test, and what replaces the default |
| --- | --- | --- |
| [H] | The trailing cohort mean predicts next-week verified capacity well enough (6.33.4) | Median and spread of the signed daily forecast error over the pilot; replaces `admission.forecast_haircut`, `admission.horizon_discount_per_day`, `admission.min_forecast_donors` (`P1M`) |
| [H] | A single global φ suffices (6.26.1) | Per-category committed share and Commons share over the pilot (`P1M`); a per-category φ is the alternative |
| [H] | No-overtaking costs little utilization (6.29.2) | `hamyar_admission_waitlist_wait_s` and utilization with and without a skipped head, in simulation first and then in the pilot (`OPS`) |
| [H] | Reservations flatten bursts (6.30) | Share of peak-day cells from reservations; no-show ratio (`P1M`) |
| [H] | Opt-out fragmentation matters (6.25) | `hamyar_admission_category_supply_ratio` for the most restrictive categories (`P1M`) |

The numeric kill criteria quoted in 6.25, 6.30 and 6.33.4 are suggested starting points, arbitrary and not derived from data; the founders fix them in a `PreRegistration` before launch (`FND`, S13.*). [D]

**Open owner decisions and assumptions introduced** (for S3.*) [A]: (1) a per-category φ instead of one φ; (2) a late-cancel fee versus the cooldown of 6.30.3 (a fee needs a new ledger entry type); (3) a make-good for jobs stopped at `job.max_overrun_ratio`; (4) whether the window clock pauses while a job is `suspended` (`S5.*`); (5) whether the initial `admission.min_forecast_donors` of 10 suits a pilot of 30 to 50 members, since a narrow category with fewer eligible donors is waitlisted entirely; (6) the single global admission lock; (7) self-reported service attribution for M1 supply (6.22).

## Issues raised

Each resolution is already applied in this file; `C-001` consolidates and may record another. Convention additions made by this part (not issues, listed so `C-001` and `C-022` can fold them back): the parameters of 6.23 B and constraints `C9`..`C12`; the events and metric names of 6.34.3; the derived data of 6.22; the `quote` document, `WaitlistEntry` and `Reservation` field requirements of 6.27.4, 6.29.1, 6.30.1; `hold_seq`, `waitlist_seq`, `cancel_reason`; operation ids and copy keys of 6.35; the scheduler contract SC-1..SC-5 for `S5.*`, `S8.*`, `S9.*`.

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-64` | minor | prompt | Part 6 is split over two files (the credit and ledger file and this one) and S0 0.3 gives no rule for heading numbers, so two files could both contain `6.1`; S0 0.13 also proposes the file name `06b-admission-control.md` while the cell's `allowed_paths` name `06b-admission.md` | Headings of this file are `6.20`..`6.39`; the file name of the cell is authoritative (S0 0.13) | proposed |
| `ISS-65` | major | FD§4.8, FD§3.3 | "Committed cells over its window <= φ × forecast active capacity" is stated for one job only; it does not say how several concurrent jobs, categories with different supply, held reservations and the Commons share combine, nor what a quote is when the window is infeasible | The first-come fluid-queue test of 6.27 over two scopes (global and category), net of held reservations, with backlog ahead counted in full; the smallest feasible window on a grid is the quote; the decisions are `accept`, `counter_offer`, `waitlist` (6.28) | proposed |
| `ISS-66` | major | FD§4.8, FD§4.5, FD§4.6 | Reservations with escrow at booking are under-specified: escrowed credit can pass its expiry before a cancel or expiry refund (see `ISS-07`), a no-show has no consequence, there is no source for a penalty (credit is never printed), and the price can change between booking and use | Price is locked at booking; no monetary penalty, a cooldown after a late cancel or expiry instead; booking discloses lots that expire before the reserved date; one live reservation per member and a share cap per slot (6.30). Whether to charge a fee is an owner decision | needs_owner |
