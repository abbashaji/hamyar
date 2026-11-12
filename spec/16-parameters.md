# 16. Configuration parameter table

*Spec part 16 · owner cell C-022 · completes `spec/00-conventions.md` (S0) 0.10.6 without renaming any parameter. Written against Founding Document draft v0.1 (FD) and the spec files that were on main when this part was written (S0, S4, S5.*, S6.*, S7, S9; see 16.1). Nothing here is legal advice and nothing here has been verified against any provider's terms or any law.*

## 16.1 Scope, sources and the rules of this table

This part is the single complete list of configuration parameters. Every number that any spec part states as a threshold, rate, limit, lifetime, interval or size is either a row below, a constant of S0 (marked `constant`), or derived by a formula shown next to it. [D]

| Rule | Decision |
| --- | --- |
| R16-1 Names | Exactly S0 0.10.1 (`area.name` or `area.group.name`, regex `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){1,2}$`). No name is renamed here; a name that another part introduced is accepted as written and reported in `## Issues raised`. [D] |
| R16-2 Defaults | The column `Initial configurable default` holds the value stored in `ParameterVersion` 1. It is a safe starting value, never a finding. A value written `= formula` is derived by that formula from the FD's own illustrative inputs (FD§3.3), which are not measurements. `constant` means immutable (measurement code `CON`). [D] |
| R16-3 No invented statistics | Where a default has no derivation it says so, and the `Cal` column names the measurement that replaces it (S0 0.10.4). Simulation output never replaces a default (prompt K). [D] |
| R16-4 Unknown names | The parameter store refuses a write, a read in a policy or job path, and a seed for any name not in this table (`AC-param-01`). [D] |
| R16-5 Not parameters | Feature flags `ff.*`, kill switches `kill.*` (S0 0.10.6 end) and secrets `secret.*` (S10.*). Bootstrap settings `HAMYAR_*` (S4.13.2) are process settings, not parameters. [D] |

**Sources scanned for this table** [A] (parameters and thresholds were collected from the parameter sections and convention-addition lists of these files, and from the FD; text elsewhere in them was not re-read):

| Source | What was taken |
| --- | --- |
| FD§4.9, FD§3.3, FD§4.3-4.8, FD§5.4, FD§6.2, FD§8.3, FD§9 | The ten FD§4.9 parameters, illustrative inputs, thresholds named by the FD, Phase 1 measures and decision rules |
| S0 0.10.6 (tables A, B, C), 0.10.3 constraints C1..C8 | 217 names with defaults, validation and measurement codes |
| S4 4.19.1 | 21 new `ops.*` names and `admission.forecast_refresh_s` |
| S6.* ledger file (6.11, 6.12) | Binding of parameters to entities, tighten directions required from this part, `phi` and mint-cap relation (`ISS-63`) |
| S6.* admission file (6.23 B and C) | 14 new `admission.*` and `reservation.*` names, constraints `C9`..`C12` |
| S7 (7.15.1) | 13 new `policy.*`, `screen.*`, `service.*` names |
| S9 (9.18) | 17 new `cell.*`, `lease.*`, `screen.*`, `verify.*` names, constraints `S9-C1`..`S9-C3` |
| Not yet on main when this was written | S8 (templates and verification), S10 (identity), S11..S15, S1..S3: parameters they add are folded in by C-001 at assembly (`ISS-169`) [V] |

## 16.2 Column legend and uniform rules

### 16.2.1 Columns [D]

| Column | Meaning |
| --- | --- |
| `Name` | Primary key of `Parameter` (S0 0.10.3) |
| `Type · unit` | S0 0.10.2 type plus the unit suffix of the name. `ratio` is stored as integer ppm and written as a decimal here for readability (S0 0.6.1); `credits` is stored in `ucr` |
| `Validation` | Range, enum or constraint id from 16.3, evaluated at write time. A violation is `VALIDATION_FAILED` |
| `Initial configurable default` | See R16-2 |
| `Chg` | Change-policy code, 16.2.2 |
| `Cal` | Measurement code (S0 0.10.4) and the measurement that replaces the default |
| `Used` | Spec part or section that reads it (`S6.*` is the credit and admission part, `S5.*` the domain model, and so on) |

The owner role, the binding rule and the public flag of a row are stated once in the header of its group table; a row that differs says so in its `Chg` or `Cal` cell. [D]

### 16.2.2 Change-policy codes [D][A]

Every mutable parameter is **prospective-only** (FD Principle 5; S0 0.10.3): a change never alters an object that was created under an earlier version where the group header names a binding, and never rewrites history. A tightening applies at once; every other change needs notice and a public change-log entry (R10).

| Code | Meaning | Class of a change | Timing |
| --- | --- | --- | --- |
| `T↓` | Lowering the value is the tightening | lower = `tighten`; raise = `loosen` | `tighten`: `effective_from` may be now, log published within `change.tighten_publish_within_s`. `loosen`: `effective_from >= now + notice_days` and a second operator |
| `T↑` | Raising the value is the tightening | raise = `tighten`; lower = `loosen` | as above |
| `T→x` | Boolean or ordered enum: moving to `x` (or toward `x`) is the tightening | toward `x` = `tighten` | as above |
| `N` | No tightening direction (changes what members hold or pay, or has no safe direction) | always `neutral` | always `notice_days` (`change.notice_days_price` = 14 for `price.*`, `credit.*`, `admission.*`, `reservation.*`; otherwise `change.notice_days_default` = 7) |
| `C` | Constant | not editable | a spec change and, if stored data depends on it, a migration |

The directions for rows whose defining part states one (S0 for `verify.audit_rate_s` and `admission.phi`; S6.* ledger file for the `grant.*`, `mint.*`, price, lifetime, K and Reserve-ceiling rows; S6.* admission file for its 14 rows) are copied. Every other direction is assigned here by one rule [A]: **tightening is the change that lowers risk to members, to credit integrity or to the platform without taking anything away from an object that already exists**; where that cannot be decided the row is `N`. An owner who disagrees changes the cell, not the rule (`ISS-164`).

### 16.2.3 Uniform rules for every row [D]

| Topic | Rule |
| --- | --- |
| Versioning | Every accepted change creates an immutable `ParameterVersion` (`version` + 1) with `effective_from`, `change_class`, reason, approvers. The `default` column of `Parameter` is never edited. The value in force at time `t` is the version with the greatest `effective_from <= t` |
| Owner roles | By area, S0 0.10.5: `operator` for `credit`, `price`, `grant`, `reserve`, `mint`, `inflation`, `ledger`, `job`, `admission`, `reservation`, `verify`, `lease`, `cell`, `trust`, `identity`, `session`, `invite`, `ratelimit`, `retention`, `security`, `launch`, `change`, `api`, `ui`, `i18n`, `ops`; `reviewer` for `policy`, `screen`, `service`, `template`, `optin`, `appeal`, `report` (exceptions named in 16.12); `founders` for thresholds, `operator` otherwise in `analytics`, `experiment`, `growth`, `team`, `public`, `metrics`, `calibration` |
| Approvers | The owner role edits. A `loosen` or `neutral` change also needs a second distinct `operator` (`security.two_person_actions` contains `parameter.loosen`); `launch.*` needs `launch.min_signoffs` distinct admins |
| Public exposure | `public` is true for every row except `security.*` and `ops.*` rows marked `public: no`; see 16.17.5 |
| Calibration gate | A `CAL` or `P1M` value may replace a default only with at least `calibration.min_samples_per_service` cells per service behind it (16.19) |
| Stamping | Objects stamp the version they were created under where the group header says `Binding`; every event carries `config_epoch` (S4.9.2) |

## 16.3 Cross-parameter constraints

Evaluated on every write against the configuration as it will be at `effective_from` (all pending versions applied), so two individually valid edits cannot combine into an invalid state (16.17.2). `C1`..`C8` are S0 0.10.3; `C9`..`C12` are proposed by the admission part and `S9-C1`..`S9-C3` by the result-return part; `C13`..`C20` are added here [A].

| Id | Constraint | Kind |
| --- | --- | --- |
| `C1` | `0 < admission.phi < 1` | error |
| `C2` | `verify.audit_rate_floor <= verify.audit_rate_s <= verify.audit_rate_max` and `verify.gold_rate_floor <= verify.gold_rate_g <= verify.gold_rate_max`; `verify.audit_rate_floor > 0` | error |
| `C3` | `lease.timeout_s >= cell.envelope.expected_time_s` | error |
| `C4` | `credit.lifetime_days_accelerated <= credit.lifetime_days`; `grant.starter_lifetime_days <= credit.lifetime_days` | error |
| `C5` | `reserve.ceiling_credits >= grant.starter_credits` | error |
| `C6` | `0 <= price.levy_lambda < 1`; `price.v_prior <= price.v_cap` | error |
| `C7` | `admission.min_window_s <= admission.max_window_days * 86400` | error |
| `C8` | `credit.member_cap_credits >= admission.max_job_cells * (1 + price.v_prior + price.levy_lambda)` | warning (a member who cannot hold the price of a maximum job can never request one) |
| `C9` | `admission.min_window_s` and `admission.max_window_days * 86400` are multiples of `admission.window_step_s` | error |
| `C10` | `admission.min_history_days <= admission.forecast_window_days`; `admission.active_donor_window_days <= admission.forecast_window_days` | error |
| `C11` | `reservation.min_lead_s <= reservation.max_horizon_days * 86400` | error |
| `C12` | `admission.waitlist_quote_ttl_s >= price.quote_ttl_s` | error |
| `S9-C1` | `cell.envelope.max_submission_bytes >= 3 * cell.envelope.max_output_chars` (a character is at most 3 bytes in the accepted UTF-8 range) | error |
| `S9-C2` | `verify.duplicate_minhash_perms` is a multiple of 4 | error |
| `S9-C3` | `lease.max_validations >= 0` and `lease.max_gate_failures >= 1` | error |
| `C13` | `mint.monthly_cap_credits * 10^6 <= floor(admission.phi_ppm * accepted_cells_in_window * 30 / inflation.throughput_window_days) * 10^6` once throughput data exists (skipped in Phase 0) | warning plus a second approver on the edit (S6.* ledger file 6.11.5; `ISS-166`) |
| `C14` | `lease.extend_s <= lease.timeout_s`; `lease.submit_grace_s <= lease.timeout_s` | error |
| `C15` | `session.member_idle_ttl_s <= session.member_abs_ttl_s`; `session.admin_idle_ttl_s <= session.admin_abs_ttl_s` | error |
| `C16` | `trust.demote_below_reliability <= trust.established_min_reliability <= trust.trusted_min_reliability` | error |
| `C17` | `reserve.retire_min_credits <= reserve.ceiling_credits`; `credit.expiry_notice_days <= credit.lifetime_days_accelerated` | error |
| `C18` | `admission.donor_daily_clamp_cells >= 1`; `mint.per_member_daily_cap_credits >= 1` | error |
| `C19` | `launch.required_gate_ids` contains `G0` and `G1`; `launch.min_signoffs <= count of active AdminUser` | error on the first, warning on the second (`ISS-168`) |
| `C20` | `policy.loosen_min_approvers >= policy.tighten_min_approvers`; `policy.loosen_min_notice_days >= change.notice_days_default` | error |

Worked check of the initial defaults against every constraint [D]: `C1` 0.5; `C2` 0.01 <= 0.05 <= 0.20 and 0.02 <= 0.10 <= 0.50; `C3` 1200 >= 120; `C4` 14 <= 60 twice; `C5` 1000 >= 3; `C6` 0.05 and 0.10 <= 0.50; `C7` 43,200 <= 1,209,600; `C8` 350 >= 300 x 1.15 = 345; `C9` 43,200 and 1,209,600 are multiples of 43,200; `C10` 3 <= 14 and 7 <= 14; `C11` 86,400 <= 2,592,000; `C12` 86,400 >= 1800; `S9-C1` 32,768 >= 18,000; `S9-C2` 128 = 4 x 32; `C13` skipped (Phase 0); `C14` 600 <= 1200, 120 <= 1200; `C15` 2,592,000 <= 7,776,000 and 1800 <= 28,800; `C16` 0.70 <= 0.80 <= 0.95; `C17` 10 <= 1000, 7 <= 14; `C18` 30 >= 1; `C19` `["G0","G1"]`; `C20` 2 >= 1, 7 >= 7. All pass (`AC-param-02`).

## 16.4 Cell envelope

Owner `operator`. Binding: the envelope in force is stamped on a `Cell` when it is created and on its `TemplateVersion` check at approval [A]; lowering a limit never invalidates a leased or submitted cell. The envelope is one parameter group, not a per-template field, in Phase 1 (one size class, S0 0.8.6). [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `cell.envelope.max_input_chars` | int · chars | 200..100000 | 4000 | `T↓` | `CAL`: largest input that completes in one Send, per service and device class | S8.*, S9.6 |
| `cell.envelope.max_output_chars` | int · chars | 200..100000 | 6000 | `T↓` | `CAL`: longest output a service returns inside one Send | S8.*, S9.6, S9.7.3 |
| `cell.envelope.max_submission_bytes` | int · bytes | 1024..1048576; `S9-C1` | 32,768 (6000 chars x up to 3 UTF-8 bytes = 18,000, plus margin) | `T↓` | `CAL`: size of real paste-backs | S9.6, S4.* |
| `cell.envelope.expected_time_s` | duration_s | 10..3600; `C3` | 120 (the FD§3.2 first-contribution estimate [H]) | `N` | `CAL`: median seconds per cell | S11.*, S6.*, S9.12 |
| `cell.envelope.max_json_depth` | int | 2..64 | 16 | `T↓` | `TEC`: parser limits on real phones | S9.7 |
| `cell.envelope.max_model_label_chars` | int · chars | 1..200 | 80 | `N` | `CAL`: labels donors actually type | S9.7 |
| `cell.max_attempts` | int | 1..20 | 5 | `N` | `P1M`: attempts to acceptance by template | S5.*, S9.14.2 |

## 16.5 Credit, expiry, caps, grant, Reserve, mint, inflation

Owner `operator`. Binding (S6.* ledger file 6.12.2): `credit.lifetime_days*` to the `CreditLot` (`lifetime_param_version`); `credit.member_cap_credits` and `trust.cap_multiplier.*` to the `Lease` (`ledger_versions`); `mint.*` to the lease; `grant.*` to the evaluation run; `reserve.*` to the next retirement run; `inflation.*` and `ledger.*_interval_s` to the next rollup or run. Every price, lifetime, K and Reserve-ceiling parameter is `N`: always notice, because it changes what members hold or pay. [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `credit.scale_ucr_per_credit` | int | constant | 1,000,000 | `C` | `CON` | S0 0.6.1, S6.* |
| `credit.lifetime_days` (E) | days | 1..365; `C4`, `C17` | 60 (FD§4.5 proposal, from the brief) | `N` | `P1M`: arm comparison, return and share of credit expiring | S6.*, S5.* |
| `credit.lifetime_days_accelerated` | days | 1..365; `C4`, `C17` | 14 (FD§4.5 example arm) | `N` | `P1M`: arm comparison | S6.*, S13.* |
| `credit.member_cap_credits` (K) | credits | 1..100000; `C8` | 350 = round to 50 of 1.25 x 240 x 1.15 (the FD§3.3 reference job with a 25% margin) | `N` | `DEM`: p90 large-job size; then `P1M` | S6.* |
| `credit.expiry_notice_days` | days | 0..60; `C17` | 7 | `N` | `OPS`: member feedback on expiry notices | S6.*, S11.* |
| `credit.expiry_sweep_interval_s` | duration_s | 60..86400 | 3600 | `N` | `OPS` | S6.*, S4.* |
| `grant.starter_credits` (G) | credits | 0..1000; `C5` | 3 (FD§4.6 "a few cells") | `T↓` | `P1M`: first-job completion and Reserve flow | S6.* |
| `grant.starter_lifetime_days` | days | 1..365; `C4` | 14 (FD§4.6 "expires quickly") | `N` | `P1M` | S6.* |
| `grant.required_verified_cells` | int | 1..50 | 1 (FD§4.6: after one verified contribution) | `T↑` | `FND` | S6.* |
| `grant.max_per_device` | int | 0..10 | 1 (lifetime) | `T↓` | `OPS`: farming flags | S6.*, S10.* |
| `grant.max_per_invite_tree_per_day` | int | 0..100 | 2 | `T↓` | `OPS` | S6.*, S10.* |
| `grant.max_per_day` | int | 0..10000 | 20 | `T↓` | `OPS` | S6.* |
| `grant.reserve_floor_credits` | credits | >= 0 | 0 (grants pause rather than overdraw, FD§4.6) | `T↑` | `FND` | S6.*, S5.27 |
| `grant.non_transferable` | bool | constant | true | `C` | `CON` | S6.* |
| `reserve.ceiling_credits` | credits | >= `grant.starter_credits`; `C5`, `C17` | 1000 | `N` (retirement is irreversible) | `P1M`: grant demand and expiry inflow | S6.* |
| `reserve.retire_interval_s` | duration_s | 3600..604800 | 86,400 | `N` | `OPS` | S6.* |
| `reserve.retire_min_credits` | credits | >= 0; `C17` | 10 (avoids noise entries) | `N` | `OPS` | S6.* |
| `mint.monthly_cap_credits` | credits | >= 0; `C13` | 4800 = 40 donors x 8 cells x 30 days x phi 0.5 (FD§3.3 illustrative inputs); never above forecast redeemable capacity | `T↓` | `CAL`, then `P1M`: measured throughput | S6.*, S6.24.3 |
| `mint.cap_period` | enum | constant | `utc_month` | `C` | `CON` | S0 0.6.2, S6.* |
| `mint.per_member_daily_cap_credits` | credits | >= 1; `C18` | 30 = 3 x the FD§3.2 habit of about 10 cells a day | `T↓` | `P1M` | S6.* |
| `mint.requires_launch_gate` | bool | constant | true | `C` | `CON` | S6.*, S14.* |
| `inflation.claim_ratio_threshold_weeks` | ratio · weeks | > 0 | 6.0 | `T↓` | `FND` (pre-registered), `P1M` | S6.*, S6.27.2 |
| `inflation.mint_cap_cut_ratio` | ratio | 0 < x <= 1 | 0.25 (cut applied when the threshold is passed) | `T↑` | `FND` | S6.* |
| `inflation.mint_utilization_alarm` | ratio | 0..1 | 0.90 | `N` | `OPS` | S6.*, S4.* |
| `inflation.throughput_window_days` | days | 7..90 | 28 | `N` | `P1M` | S6.*, `C13` |

## 16.6 Price

Owner `operator`. Binding: the quote stores the snapshot ids and the values it used; the `Escrow` stores `quote_p_ucr`, `quote_v_ppm`, `quote_lambda_ppm` at the hold and never changes them; a reservation fixes the price at booking. `price.*` changes take `change.notice_days_price` = 14 days and are announced in the change log with old and new `p_ucr` and eta; a quote lives `price.quote_ttl_s`, far shorter than the notice, so a price change never falls inside a quote. v itself is not a parameter: it is measured and published as a `MetricSnapshot` (S0 0.10.1). [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `price.levy_lambda` (λ) | ratio | 0 <= x < 1; `C6` | 0.05 (FD§3.3 illustrative) | `N` | `P1M`: Reserve inflow against grant demand; then `FND` | S6.*, S6.27 |
| `price.v_prior` | ratio | 0..`price.v_cap`; `C6` | 0.10 (FD§3.3 illustrative); used while fewer than `price.v_min_sample_cells` primary cells are in the window | `N` | `P1M`: measured v | S6.* |
| `price.v_cap` | ratio | 0..1; `C6` | 0.50 | `N` | `FND` | S6.* |
| `price.v_window_days` | days | 7..90 | 28 | `N` | `P1M`: stability of v | S6.* |
| `price.v_min_sample_cells` | int | 1..100000 | 100 | `N` | `P1M`: variance of v | S6.* |
| `price.publish_period_days` | days | 1..90 | 30 (FD§4.3 "monthly") | `N` | `FND` | S6.*, S12.* |
| `price.eta_alarm_threshold` | ratio | 0..1 | 0.80 (FD§4.3 suggested starting point, arbitrary) | `N` | `FND` (pre-registered, 16.15) | S6.*, S13.* |
| `price.quote_ttl_s` | duration_s | 60..86400; `C12` | 1800 | `N` | `OPS`: share of quotes confirmed after expiry | S6.*, S6.27 |
| `price.v_rounding` | enum | constant | `ceil` | `C` | `CON` | S0 0.6.1, S6.* |

## 16.7 Admission and reservation

Owner `operator`. Binding: a quote, hold or reservation keeps the parameter versions it was created under (recorded in the quote); a change never alters an existing hold or an admitted job's declared window. Lowering `admission.phi` is a tightening, so it can never invalidate an admitted job; it only affects later quotes (S6.* admission file 6.23 D, `AC-admission-23`). Notice for `admission.*` and `reservation.*` is `change.notice_days_price`. Directions for the rows added by the admission part are copied from its table. [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `admission.phi` (φ) | ratio | 0 < x < 1; `C1` | 0.50 (FD§3.3 illustrative) | `T↓` | `P1M`: throughput and deposit-to-withdrawal ratio | S6.26, S6.27 |
| `admission.forecast_window_days` | days | 3..60; `C10` | 14 | `N` | `P1M`: forecast error by window | S6.24 |
| `admission.active_donor_window_days` | days | 1..30; `C10` | 7 | `N` | `P1M` | S6.24, S7.* |
| `admission.forecast_haircut` | ratio | 0 <= x < 1 | 0.00 (so FD§3.3 reproduces exactly; expected to become greater than 0 [H]) | `T↑` | `P1M`: median and spread of signed forecast error | S6.24 |
| `admission.active_donor_min_cells` | int | 1..1000 | 1 | `T↑` | `P1M` | S6.24 |
| `admission.donor_daily_clamp_cells` | int | 1..1000; `C18` | 30 (equal to `mint.per_member_daily_cap_credits`) | `T↓` | `P1M`: capacity concentration (FD§9) | S6.24 |
| `admission.min_forecast_donors` | int | 1..1000 | 10 (the cohort size below which a mean is noise [H]) | `T↑` | `P1M`: forecast error; owner decision for a pilot of 30 to 50 (S6.39) | S6.24, S6.28 |
| `admission.min_history_days` | int | 1..`admission.forecast_window_days`; `C10` | 3 | `T↑` | `P1M` | S6.24 |
| `admission.horizon_discount_per_day` | ratio | 0 <= x < 1 | 0.00 (FD§3.3 exact; expected to become greater than 0 [H]) | `T↑` | `P1M`: forecast error by horizon | S6.24 |
| `admission.min_window_s` | duration_s | `C7`, `C9` | 43,200 | `N` | `DEM`: accepted windows | S6.27 |
| `admission.max_window_days` | days | 1..60; `C7`, `C9` | 14 | `T↓` | `DEM` | S6.27 |
| `admission.window_step_s` | duration_s | divides 86,400; `C9` | 43,200 (equal to `admission.min_window_s`) | `N` | `DEM` | S6.27 |
| `admission.max_job_cells` | int | 1..100000 | 300 = floor(350 / 1.15) rounded down to a multiple of 100 | `T↓` | `DEM`, then `P1M` | S6.*, S11.* |
| `admission.max_concurrent_jobs_per_member` | int | 1..20 | 2 | `T↓` | `FND` | S6.29, S5.* |
| `admission.waitlist_ttl_days` | days | 1..60 | 7 | `N` | `OPS` | S6.29 |
| `admission.waitlist_max_per_member` | int | 0..10 | 1 | `T↓` | `OPS` | S6.29 |
| `admission.waitlist_recheck_interval_s` | duration_s | 30..3600 | 300 | `N` | `OPS` | S6.29 |
| `admission.waitlist_quote_ttl_s` | duration_s | 60..604800; `C12` | 86,400 (a released requester checks a few times a day [H]) | `N` | `OPS`: share of released quotes confirmed | S6.29 |
| `admission.deadline_multiplier_standard` | ratio | constant 1.0 in Phase 1 | 1.0 (FD§4.8) | `C` | `CON` | S6.27.3 |
| `admission.reforecast_interval_s` | duration_s | 60..86400 | 3600 (equal to `metrics.rollup_interval_s`) | `N` | `OPS` | S6.25, S6.33 |
| `admission.forecast_refresh_s` | duration_s | 60..86400 | 3600; **alias of `admission.reforecast_interval_s`**, not seeded (`ISS-162`) | `N` | `P1M` | S4.19.1 |
| `admission.overrun_tolerance_ratio` | ratio | 0..1 | 0.10 | `T↓` | `OPS`: share of windows missed | S6.33 |
| `admission.claim_stretch_max` | ratio | >= 1 | 2.0 | `T↑` | `FND` | S6.27.2 |
| `admission.share_window_s` | duration_s | 3600..604800 | 86,400 | `N` | `OPS` | S6.26.2 |
| `job.max_overrun_ratio` | ratio | >= 1 | 2.0 (a job stops with partial settlement at 2 x its quoted window) | `T↓` (bound to the quote that stamped it) | `P1M`: actual against quoted completion | S6.33, S5.* |
| `reservation.max_horizon_days` | days | 1..180; `C11` | 30 | `T↓` | `P1M` | S6.30 |
| `reservation.max_active_per_member` | int | 0..10 | 1 | `T↓` | `FND` | S6.30 |
| `reservation.free_cancel_notice_s` | duration_s | 0..2592000 | 86,400 | `T↑` | `OPS` | S6.30.3 |
| `reservation.capacity_share_cap` | ratio | 0..1 | 0.25 of the phi capacity of any day or slot | `T↓` | `P1M`: burstiness | S6.26.2, S6.30 |
| `reservation.min_lead_s` | duration_s | 0..`reservation.max_horizon_days` x 86,400; `C11` | 86,400 (equal to `reservation.free_cancel_notice_s`, so a free cancel exists) | `T↑` | `OPS` | S6.30 |
| `reservation.activation_grace_s` | duration_s | 0..604800 | 43,200 | `T↓` | `OPS` | S6.30 |
| `reservation.late_cancel_cooldown_days` | days | 0..90 | 7 | `T↑` | `OPS`: no-show rate | S6.30.3 |

`job.max_overrun_ratio` is listed here because the admission part reads it (hard stop, 6.33); its S0 area is `job` and its owner `operator`. The default 4,800 of `mint.monthly_cap_credits` derives from phi, not from (1 - phi); the two coincide only at 0.5 (`ISS-166`). [D]
