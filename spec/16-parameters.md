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
| S0 0.10.6 (tables A, B, C), 0.10.3 constraints C1..C8 | Every name of tables A, B and C with defaults, validation and measurement codes |
| S4 4.19.1 | 21 new `ops.*` names and `admission.forecast_refresh_s` (22 names) |
| S6.* ledger file (6.11, 6.12) | Binding of parameters to entities, tighten directions required from this part, `phi` and mint-cap relation (`ISS-63`) |
| S6.* admission file (6.23 B and C) | 15 new `admission.*` and `reservation.*` names, constraints `C9`..`C12` |
| S7 (7.15.1) | 14 new `policy.*`, `screen.*`, `service.*` names |
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
| Public exposure | `public` is true for every row except those listed in 16.17.5 |
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

## 16.8 Verification

Owner `operator`. Binding: the sampling rates and multipliers that decided whether a cell was gold-checked or audited are stamped on the `Lease` at issue (`ledger_versions`), so a later change never re-decides an old cell; reliability and duplicate thresholds are read when the next evaluation runs. The ratios g and s move by the adaptive rule (`verify.adapt.*`), never below their floors (FD§4.4). [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `verify.gold_rate_g` (g) | ratio | `C2` | 0.05 | `T↑` | `P1M`: reliability-estimate variance and false-accept estimate | S8.*, S9.* |
| `verify.gold_rate_floor` | ratio | `C2` | 0.01 | `T↑` | `FND` | S8.* |
| `verify.gold_rate_max` | ratio | `C2` | 0.20 | `N` | `FND` | S8.* |
| `verify.audit_rate_s` (s) | ratio | `C2` | 0.10 | `T↑` (S0) | `P1M`: false-accept estimate, v | S8.*, S6.* |
| `verify.audit_rate_floor` | ratio | `C2`; > 0 | 0.02 (FD§4.4: sampling never falls to zero) | `T↑` | `FND` | S8.* |
| `verify.audit_rate_max` | ratio | `C2` | 0.50 | `N` | `FND` | S8.* |
| `verify.blanket_redundancy_n` | int | 2..5 | 3 (FD§4.4 "triple") | `T↑` | `P1M` | S8.* |
| `verify.new_donor_blanket_cells` | int | 0..50 | 5 first cells of a new donor | `T↑` | `P1M` | S8.*, S5.* |
| `verify.adapt.clean_streak` | int | 1..1000 | 20 clean observations before a step down | `T↑` | `P1M` | S8.* |
| `verify.adapt.step_down_ratio` | ratio | 0 < x < 1 | 0.80 | `T↑` (a larger ratio lowers the rate more slowly) | `P1M` | S8.* |
| `verify.adapt.step_up_ratio` | ratio | > 1 | 2.00 | `T↑` | `P1M` | S8.* |
| `verify.reliability_prior_a` | int | >= 1 | 1 (Beta prior, successes) | `N` | `P1M` | S8.* |
| `verify.reliability_prior_b` | int | >= 1 | 1 (Beta prior, failures) | `N` | `P1M` | S8.* |
| `verify.reliability_window_obs` | int | 5..1000 | 50 most recent gold and audit observations | `N` | `P1M` | S8.* |
| `verify.human_review_rate` | ratio | 0..1 | 0.20 of subjective outputs | `T↑` | `P1M` | S8.*, S9.* |
| `verify.human_review_gold_rate` | ratio | 0..1 | 0.10 | `T↑` | `P1M` | S8.* |
| `verify.timing_min_s` | duration_s | >= 0 | 5 (below this a submission is a timing anomaly) | `T↑` | `CAL`: seconds-per-cell distribution | S9.12 |
| `verify.timing_soft_ratio` | ratio | 0..1 | 0.25 | `N` | `CAL` | S9.12 |
| `verify.timing_regular_window_obs` | int | 5..1000 | 20 | `N` | `P1M` | S9.12 |
| `verify.timing_regular_cv` | ratio | 0..1 | 0.05 [H] | `T↑` (a higher coefficient flags more) | `P1M` | S9.12 |
| `verify.duplicate_similarity_threshold` | ratio | 0..1 | 0.95 | `T↓` | `P1M` | S9.11 |
| `verify.duplicate_min_chars` | int | 1..10000 | 80 | `T↓` | `P1M`: rate of honest short agreement | S9.11 |
| `verify.duplicate_shingle_chars` | int | 2..20 | 5 | `N` | `P1M` | S9.11 |
| `verify.duplicate_minhash_perms` | int | multiple of 4; `S9-C2` | 128 (32 bands of 4 rows) | `N` | `OPS`: index cost | S9.11 |
| `verify.duplicate_window_days` | days | 1..90 | 14 | `T↑` | `P1M` | S9.11 |
| `verify.false_accept_alarm` | ratio | 0..1 | 0.05 | `T↓` (an earlier alarm) | `FND` (pre-registered, 16.15) | S8.*, S13.* |
| `verify.false_reject_alarm` | ratio | 0..1 | 0.10 | `T↓` | `FND` (pre-registered, 16.15) | S8.*, S13.* |
| `verify.third_exec_on_mismatch` | bool | constant | true (FD§4.4) | `C` | `CON` | S8.* |
| `verify.model_judge_mints_credit` | bool | constant in Phase 1 | false (FD§4.4) | `C` | `CON` | S8.* |

## 16.9 Lease

Owner `operator`. Binding: `timeout_s`, `extend_s` and `max_extensions` are stamped on the `Lease` at issue and decide its `expires_at`; the others are read at the event they govern. A lease already issued is never shortened. [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `lease.timeout_s` | duration_s | `C3`, `C14` | 1200 = 10 x 120 s, ten times the FD§3.2 first-contribution estimate | `N` | `CAL`: p95 of seconds per cell | S5.23.3, S9.4.4 |
| `lease.max_active_per_member` | int | 1..50 | 3 (a daily batch is one card or a few, FD§3.2) | `T↓` | `P1M` | S5.23, S9.6 |
| `lease.max_extensions` | int | 0..5 | 1 | `T↓` | `CAL` | S9.4.4 |
| `lease.extend_s` | duration_s | 60..3600; `C14` | 600 | `T↓` | `CAL` | S9.4.4 |
| `lease.submit_grace_s` | duration_s | 0..900; `C14` | 120 (a late paste-back is accepted if the cell is not yet re-leased) | `T↓` | `CAL`: copy-paste timing | S9.4.4 |
| `lease.reap_interval_s` | duration_s | 5..300 | 30 | `N` | `OPS` | S5.23, S4.19.1 |
| `lease.max_gate_failures` | int | 1..100; `S9-C3` | 5 | `T↓` | `OPS`: honest retry counts | S9.7 |
| `lease.max_validations` | int | 0..100; `S9-C3` | 10 | `T↓` | `CAL`: copy-paste error rate | S9.7 |
| `lease.max_nonce_rotations` | int | 0..10 | 2 | `T↓` | `OPS`: reload frequency on phones | S9.4 |
| `lease.nonce_bytes` | int | constant | 16 | `C` | `CON` | S9.4.1 |
| `lease.decline_cooldown_s` | duration_s | constant | 0 (a decline is never punished, FD§5.5) | `C` | `CON` | S9.* |

## 16.10 Trust, invite, rate limits

Owner `operator`. Binding: `trust.cap_multiplier.*` and `trust.audit_multiplier.*` are stamped on the `Lease`; tier thresholds are read at the next tier evaluation and never demote a member retroactively for cells already accepted. `trust.audit_multiplier.*` multiplies s, then the result is clamped to `[verify.audit_rate_floor, verify.audit_rate_max]`. A cap multiplier changes what a member may hold, so it is `N` like K. `ratelimit.*` is read per request (no stamp). [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `trust.established_min_cells` | int | 1..10000 | 10 accepted cells | `T↑` | `P1M` | S8.*, S10.* |
| `trust.established_min_reliability` | ratio | 0..1; `C16` | 0.80 | `T↑` | `P1M` | S8.* |
| `trust.trusted_min_cells` | int | 1..100000 | 100 | `T↑` | `P1M` | S8.* |
| `trust.trusted_min_reliability` | ratio | 0..1; `C16` | 0.95 | `T↑` | `P1M` | S8.* |
| `trust.demote_below_reliability` | ratio | 0..1; `C16` | 0.70 | `T↑` | `P1M` | S8.* |
| `trust.restrict_after_gold_fails` | int | 1..20 | 2 consecutive failed gold cells | `T↓` | `P1M` | S8.* |
| `trust.restriction_days` | days | 1..90 | 7 | `T↑` | `OPS` | S8.* |
| `trust.cap_multiplier.new` | ratio | 0..10 | 0.50 of K | `N` | `P1M` | S6.*, S8.* |
| `trust.cap_multiplier.established` | ratio | 0..10 | 1.00 of K | `N` | `P1M` | S6.*, S8.* |
| `trust.cap_multiplier.trusted` | ratio | 0..10 | 1.50 of K (FD§6.1: tiers raise caps) | `N` | `P1M` | S6.*, S8.* |
| `trust.cap_multiplier.restricted` | ratio | 0..10 | 0.25 of K | `N` | `P1M` | S6.*, S8.* |
| `trust.audit_multiplier.new` | ratio | 0..10 | 1.0 of s | `T↑` | `P1M` | S8.* |
| `trust.audit_multiplier.established` | ratio | 0..10 | 1.0 of s | `T↑` | `P1M` | S8.* |
| `trust.audit_multiplier.trusted` | ratio | 0..10 | 0.5 of s (FD§6.1: tiers lower sampling) | `T↑` | `P1M` | S8.* |
| `trust.audit_multiplier.restricted` | ratio | 0..10 | 3.0 of s | `T↑` | `P1M` | S8.* |
| `invite.max_active_per_member` | int | 0..100 | 3 | `T↓` | `OPS`: farming flags | S10.* |
| `invite.ttl_days` | days | 1..90 | 14 | `T↓` | `OPS` | S10.* |
| `invite.min_accepted_cells_to_issue` | int | 0..1000 | 3 | `T↑` | `OPS` | S10.* |
| `invite.tree_max_members` | int | 1..10000 | 50 | `T↓` | `OPS` | S10.* |
| `invite.tree_max_depth` | int | 1..20 | 4 | `T↓` | `OPS` | S10.* |
| `ratelimit.device_new_members_per_day` | int | 1..100 | 3 | `T↓` | `OPS` | S10.* |
| `ratelimit.ip_hash_new_members_per_day` | int | 1..1000 | 10 | `T↓` | `OPS`, `SEC` | S10.* |
| `ratelimit.invite_tree_new_members_per_day` | int | 1..1000 | 10 | `T↓` | `OPS` | S10.* |
| `ratelimit.member_leases_per_hour` | int | 1..1000 | 30 | `T↓` | `P1M` | S9.6 |
| `ratelimit.member_submissions_per_hour` | int | 1..1000 | 60 | `T↓` | `P1M` | S9.6 |
| `ratelimit.member_api_rpm` | int | 10..10000 | 120 | `T↓` | `OPS` | S9.6, S15.* |
| `ratelimit.admin_api_rpm` | int | 10..10000 | 300 | `T↓` | `OPS` | S15.* |
| `ratelimit.public_rpm` | int · per IP hash | 1..10000 | 60 | `T↓` | `OPS` | S9.6, S12.* |
| `ratelimit.recovery_attempts_per_day` | int | 1..100 | 5 | `T↓` | `SEC` | S10.* |

## 16.11 Identity, session, privacy and retention

Owner `operator`; measurement `SEC` (the G1 threat-model decision) unless stated. Binding: a session stores its own expiry at creation, so a TTL change applies to sessions created afterwards; `identity.*` is read at the event. **Retention is the one group with a stated exception to prospective-only [A]:** lowering a `retention.*` value (a tightening) is applied to existing rows by the next purge run, because data minimisation must not wait for old rows to age out; raising a value applies only to rows created after the change and never restores deleted rows. Every retention change is public (16.17.5). [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `identity.recovery_key_bits` | int | >= 128 | 128 | `T↑` | `SEC` | S10.* |
| `identity.key_rotation_grace_s` | duration_s | 0..2592000 | 604,800 | `T↓` | `SEC` | S10.* |
| `identity.device_link_code_ttl_s` | duration_s | 30..3600 | 300 | `T↓` | `SEC` | S10.* |
| `identity.recovery_cooldown_s` | duration_s | 0..2592000 | 86,400 (a recovered identity cannot start jobs or spend for this long) | `T↑` | `SEC` | S10.*, S6.* |
| `identity.recovery_max_per_90d` | int | 0..20 | 2 | `T↓` | `SEC` | S10.* |
| `identity.email_optional` | bool | constant | true (FD§3.2) | `C` | `CON` | S10.* |
| `session.member_idle_ttl_s` | duration_s | 600..31536000; `C15` | 2,592,000 | `T↓` | `SEC` | S10.* |
| `session.member_abs_ttl_s` | duration_s | 600..31536000; `C15` | 7,776,000 | `T↓` | `SEC` | S10.* |
| `session.admin_idle_ttl_s` | duration_s | 60..86400; `C15` | 1800 | `T↓` | `SEC` | S10.*, S15.* |
| `session.admin_abs_ttl_s` | duration_s | 600..86400; `C15` | 28,800 | `T↓` | `SEC` | S10.*, S15.* |
| `retention.raw_ip_stored` | bool | constant | false | `C` | `CON` | S10.*, S0 0.6.4 |
| `retention.ip_hash_ttl_days` | days | 0..30 | 1 | `T↓` | `SEC` | S10.* |
| `retention.session_days` | days | 1..365 | 90 | `T↓` | `SEC` | S10.* |
| `retention.request_log_days` | days | 0..90 | 7 | `T↓` | `SEC` | S4.*, S10.* |
| `retention.ops_log_days` | days | 0..365 | 30 | `T↓` | `SEC` | S4.* |
| `retention.event_raw_days` | days | 0..365 | 30 | `T↓` | `SEC` | S4.*, S9.* |
| `retention.job_payload_days` | days | 0..365 | 30 | `T↓` | `SEC`, `DEM` | S9.14.3, S10.* |
| `retention.moderation_days` | days | 0..1095 | 180 | `T↓` | `SEC`, `CNS` | S7.*, S10.* |
| `retention.member_inactive_days` | days | 30..3650 | 365 (then status `closed`) | `T↓` | `SEC` | S5.*, S10.* |

## 16.12 Policy, screening, service, template, opt-in, appeal, report

Owner `reviewer` for the first table, `operator` for the second (the owner column of S7 7.15.1 (b) is copied). Binding: a `PolicyVersion` stamps the parameter versions it was approved under; `optin.default_*` apply only to members created after the change and never alter an existing member's choices; `screen.*` is read at the stage that applies it; `service.*` and `template.*` are read at the next review or sweep. Tightening is immediate and loosening needs notice (R10, FD Principle 5). An enum moves toward its stricter end by the order `flag_for_review` < `quarantine` < `reject`. [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `policy.loosen_min_notice_days` | days | >= `change.notice_days_default`; `C20` | 7 (R10) | `T↑` | `FND` | S7.* |
| `policy.tighten_immediate` | bool | constant | true (R10) | `C` | `CON` | S7.* |
| `policy.recheck_on_accept` | bool | constant | true (R9) | `C` | `CON` | S7.*, S9.* |
| `policy.max_pinned_services` | int | 1..10 | 3 | `T↓` | `DEM`: how many services requesters actually pin | S7.* |
| `screen.url_action` | enum | `reject`, `flag_for_review` | `flag_for_review` | `T→reject` | `P1M`: incident log | S7.12, S9.9 |
| `screen.pii_action` | enum | `reject`, `flag_for_review` | `reject` | `T→reject` | `P1M` | S7.12 |
| `screen.output_url_action` | enum | `reject`, `flag_for_review`, `quarantine` | `quarantine` (FD§5.5: flagged, not shown as a result) | `T→reject` | `P1M` | S9.9 |
| `screen.output_code_action` | enum | same | `quarantine` | `T→reject` | `P1M`: release ratio | S9.9 |
| `screen.output_request_action` | enum | same union (`ISS-163`) | `quarantine` | `T→reject` | `P1M`: quarantine outcomes | S7.*, S9.9 |
| `screen.instruction_action` | enum | `flag_for_review`, `reject` | `flag_for_review` | `T→reject` | `P1M`: reviewer false positives | S7.12 |
| `screen.max_urls_per_input` | int | 0..100 | 0 | `T↓` | `P1M` | S7.12 |
| `screen.output_max_urls` | int | 0..100 | 0 | `T↓` | `P1M` | S9.9 |
| `screen.invisible_char_max` | int | 0..50 | 0 | `T↓` | `P1M`: real Persian inputs | S7.12 |
| `screen.max_combining_run` | int | 1..64 | 8 | `T↓` | `P1M`: reviewed Persian sample | S9.7 |
| `screen.review_rate_new_requester` | ratio | 0..1 | 1.0 (every input reviewed) | `T↑` | `OPS`: reviewer load | S7.12 |
| `screen.review_rate_established_requester` | ratio | 0..1 | 0.20 | `T↑` | `OPS` | S7.12 |
| `service.review_max_age_days` | days | 1..365 | 90 | `T↓` | `CNS` | S7.10 |
| `service.review_grace_days` | days | 0..90 | 14 | `T↓` | `CNS` | S7.10 |
| `service.min_approvers` | int | 1..5 | 1 (FD§5.3: a reviewer records the answers); 2 is an owner decision [A] | `T↑` | `FND` | S7.10 |
| `service.terms_copy_allowed_types` | json list | MIME types | `["text/html","application/pdf","text/plain"]` | `T↓` (shorter list) | `P1M`: reviewer practice | S7.10 |
| `template.min_reviewers_new` | int | 1..5 | 2 (FD§5.7 failure mode 10) | `T↑` | `FND` | S8.* |
| `template.min_reviewers_edit` | int | 1..5 | 1 | `T↑` | `FND` | S8.* |
| `optin.default_purposes` | json | subset of P0..P3 | `["P0","P1"]` (FD§5.4 R8) | `T↓` (shorter list) | `FND` | S7.*, S10.* |
| `optin.default_sensitivities` | json | subset of S0..S1 | `["S0","S1"]` (R8) | `T↓` | `FND` | S7.* |
| `optin.default_licenses` | json | subset of L0..L3 | `["L0","L1","L2"]` [A] | `T↓` | `FND` | S7.* |
| `optin.default_service_requirements` | json | subset of M0..M2 | `["M0","M1","M2"]` [A] | `T↓` | `FND` | S7.* |
| `optin.sensitive_topics_default` | bool | constant | false (each sensitive category is opt-in, R8) | `C` | `CON` | S7.* |
| `appeal.window_days` | days | 1..90 | 14 | `N` | `FND` | S7.*, S10.* |
| `appeal.max_per_decision` | int | 1..5 | 1 | `N` | `FND` | S10.* |
| `appeal.reviewer_sla_days` | days | 1..60 | 7 (target, published) | `T↓` | `OPS` | S10.* |
| `appeal.ban_min_reviewers` | int | 1..5 | 2 | `T↑` | `FND` | S10.* |
| `report.triage_sla_days` | days | 1..30 | 3 (target, published) | `T↓` | `OPS` | S10.* |
| `report.max_per_member_per_day` | int | 1..1000 | 20 | `T↓` | `OPS` | S10.* |

**Operator-owned rows in the same areas** (S7 7.15.1 (b); template rows below are `operator` too):

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `policy.tighten_min_approvers` | int · distinct admins | 1..3; `C20` | 1 | `T↑` | `OPS`: reviewer capacity | S7.8 |
| `policy.loosen_min_approvers` | int · distinct admins, author counted | 2..5; `C20` | 2 (`ISS-168`) | `T↑` | `OPS`: size of the reviewer pool | S7.8 |
| `policy.loosen_reason_min_chars` | int · chars | 0..2000 | 40 | `T↑` | `OPS` | S7.8 |
| `policy.revert_window_s` | duration_s | 0..604800 | 86,400 | `T↓` | `OPS`: incident review of mistaken tightenings | S7.8 |
| `policy.reconcile_interval_s` | duration_s | 30..86400 | 300 | `T↓` | `OPS`: sweep duration | S7.7.5 |
| `policy.invariant_check_interval_s` | duration_s | 5..3600 | 60 | `T↓` | `OPS`: check cost | S7.* |
| `screen.review_sla_s` | duration_s | 3600..2592000 | 172,800 | `T↓` | `OPS`: reviewer throughput | S7.12 |
| `screen.quarantine_max_age_days` | days | 1..60 | 7 | `T↓` | `OPS`: reviewer capacity | S9.9 |
| `service.required_regions` | json list | ISO 3166-1 alpha-2 codes | `["IR"]`; the operator's jurisdiction is added once chosen [V] | `T↑` (longer list) | `CNS` | S7.10 |
| `service.terms_copy_max_bytes` | int · bytes | 1024..52428800 | 5,242,880 (S0 value kept, `ISS-163`) | `T↓` | `OPS`: size of real terms documents | S7.10 |
| `template.autopause_report_count` | int | 1..1000 | 5 reports inside `template.autopause_window_s` | `T↓` | `OPS` | S9.9.2, S8.* |
| `template.autopause_window_s` | duration_s | 60..604800 | 3600 | `N` | `OPS` | S9.9.2, S8.* |

## 16.13 Launch, change control, ledger checks, job size

Owner `operator`; `launch.*` needs `launch.min_signoffs` distinct admins and the gate rule of S14.*. The three `launch.*_enabled` and `launch.members_may_join` switches are `T→false`: switching off is always immediate; switching on is possible only through gate sign-off and is never a plain edit. Binding: `ledger.*` is read by the next check run; `change.*` is read at the next change request. [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `launch.members_may_join` | bool | only settable when the gate rule in S14.* passes | false | `T→false` | `CON` default; flipped by sign-off | S14.*, S10.* |
| `launch.member_jobs_enabled` | bool | as above | false | `T→false` | flipped by sign-off | S14.*, S6.* |
| `launch.minting_enabled` | bool | as above | false | `T→false` | flipped by sign-off | S14.*, S6.* |
| `launch.required_gate_ids` | json | subset of G0..G5 containing G0 and G1; `C19` | `["G0","G1"]` (FD§8.3 exit rule) | `T↑` (more ids) | `FND` | S14.* |
| `launch.min_signoffs` | int | 1..5; `C19` | 2 distinct admins [A]; an owner decision if the team has one person (`ISS-168`) | `T↑` | `FND` | S14.* |
| `launch.min_approved_services` | int | 0..20 | 1 (FD§8.3 exit rule; or a documented fallback) | `T↑` | `FND` | S14.*, S7.* |
| `change.notice_days_default` | days | 0..90; `C20` | 7 (FD Principle 5) | `T↑` | `FND` | S0 R10, all parts |
| `change.notice_days_price` | days | 0..90 | 14 (for `price.*`, `admission.*`, `credit.*`) | `T↑` | `FND` | S6.* |
| `change.tighten_publish_within_s` | duration_s | 0..604800 | 86,400 (tightening is immediate, its public log entry follows within a day) | `T↓` | `FND` | S7.*, 16.17 |
| `ledger.invariant_check_interval_s` | duration_s | 5..3600 | 60 (sampled checks; the per-commit check is a constant) | `T↓` | `OPS` | S6.*, S4.* |
| `ledger.full_recompute_interval_s` | duration_s | 60..86400 | 3600 | `T↓` | `OPS` | S6.* |
| `ledger.checkpoint_interval_s` | duration_s | 3600..604800 | 86,400 | `T↓` | `OPS` | S6.* |
| `ledger.reversal_min_approvers` | int | constant | 2 | `C` | `CON` | S6.*, S10.* |
| `ledger.allow_negative_balance` | bool | constant | false | `C` | `CON` | S6.* |
| `job.max_upload_bytes` | int · bytes | 1..104857600 | 4,194,304 (300 cells x 4,000 chars x up to 3 bytes of UTF-8 is about 3.6 MB) | `T↓` | `TEC` | S9.*, S15.* |

## 16.14 Analytics, experiment, growth, team, public, UI, i18n

Owner `founders` for rows marked † (thresholds and the experiment design), `operator` for the rest. Binding: the experiment assignment writes its parameter versions with each logged assignment (`ExperimentAssignment`), so a member's arm never changes when a parameter changes (FD§5.6 pre-registration); `growth.referral.*` is stamped on the referral at acceptance. UI budgets such as page weight and first-load size are **not named by any merged part**; S11.* adds them (`ISS-169`). [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `analytics.third_party_trackers` | bool | constant | false | `C` | `CON` | S12.*, S13.* |
| `analytics.cookies_enabled` | bool | constant | false | `C` | `CON` | S12.*, S13.* |
| `analytics.min_cohort_k` | int | 1..1000 | 10 (cohorts smaller than this are suppressed in aggregates) | `T↑` | `SEC` | S13.*, S12.* |
| `experiment.expiry_arm.fraction` † | ratio | 0..1 | 0.50 of Phase 1 members (FD§9 "part of the group") | `N` | `FND` (pre-registered, 16.15) | S6.*, S13.* |
| `experiment.assignment_seed_version` | int | >= 1 | 1 | `N` | `OPS` | S13.* |
| `experiment.assignment_log_enabled` | bool | constant | true | `C` | `CON` | S13.* |
| `growth.referral.bonus_referrer_credits` † | credits | 0..100 | 1 | `N` | `FND`, `P1M` | S6.*, S12.* |
| `growth.referral.bonus_newcomer_credits` † | credits | 0..100 | 1 | `N` | `FND`, `P1M` | S6.*, S12.* |
| `growth.referral.min_newcomer_verified_cells` | int | 1..50 | 1 (FD§6.2 V5) | `T↑` | `FND` | S12.* |
| `growth.referral.max_per_referrer_per_30d` | int | 0..1000 | 5 | `T↓` | `OPS`: farming flags | S12.* |
| `growth.referral.hold_s` | duration_s | 0..2592000 | 86,400 (bonus paid after this delay) | `T↑` | `OPS` | S12.* |
| `team.max_members` | int | 2..10000 | 50 | `T↓` | `OPS` | S12.* |
| `team.min_public_members` | int | 1..1000 | 5 (a team is not shown publicly below this size) | `T↑` | `SEC` | S12.* |
| `team.create_min_tier` | enum | `new`, `established`, `trusted` | `established` | `T→trusted` | `OPS` | S12.* |
| `public.counter_refresh_s` | duration_s | 5..3600 | 60 | `N` | `OPS` | S12.* |
| `public.ledger_lag_s` | duration_s | 0..86400 | 300 (the public ledger page trails the ledger by this much) | `T↑` | `SEC` | S12.*, S6.* |
| `public.location_display` | enum | `never`, `opt_in` | `never` (FD§6.1 row 5) | `T→never` | `SEC` | S12.* |
| `ui.card.expand_required_first_use` | bool | constant | true (FD§5.5) | `C` | `CON` | S11.* |
| `ui.comprehension_check_rate` | ratio | 0..1 | 0.00 (FD§5.7 failure mode 6 is a hypothesis [H]) | `N` | `P1M` | S11.* |
| `ui.fast_contribution_threshold_s` | duration_s | 1..600 | 60 (FD§6.2 V1) | `N` | `FND` | S11.*, S12.* |
| `i18n.default_locale` | enum | `fa`, `en` | `fa` | `N` | `FND` | S11.* |
| `i18n.supported_locales` | json | subset of `locale` | `["fa","en"]` | `C` | `CON` | S11.* |
| `i18n.digits_default_fa` | enum | `latin`, `persian` | `persian` [A][H]; the member can switch to `latin` | `N` | `P1M`: interviews | S11.* |
| `i18n.dual_calendar_detail` | bool | | true (FD§10: Jalali and Gregorian) | `N` | `FND` | S11.* |

## 16.15 Thresholds for pre-registration

FD§9 requires that every measure and every stop/continue rule is recorded **before day 1** of Phase 1 (`PreRegistration`, S0 0.7, `FND`). A pre-registered value is not an editable parameter after the lock: the parameters below seed the form, and the lock copies their value into the record. Editing the parameter afterwards changes behaviour, but the pre-registered threshold used to judge the pilot stays as locked and the change is itself shown in the pilot report (FD Principle 11). [D]

| Pre-registered threshold | Seeded from parameter | FD source | Initial configurable default |
| --- | --- | --- | --- |
| Minimum eta (Reserve inflow versus spend) | `price.eta_alarm_threshold` | FD§4.3, FD§9 | 0.80 |
| Maximum false-accept rate | `verify.false_accept_alarm` | FD§4.4, FD§9 | 0.05 |
| Maximum false-reject rate | `verify.false_reject_alarm` | FD§4.4, FD§9 | 0.10 |
| Claim-to-capacity ratio that forces a mint cut | `inflation.claim_ratio_threshold_weeks` | FD§4.5, FD§9 | 6.0 weeks |
| Share of members in the accelerated-expiry arm | `experiment.expiry_arm.fraction` | FD§4.5, FD§9 | 0.50 |
| Fast-contribution threshold | `ui.fast_contribution_threshold_s` | FD§6.2 V1 | 60 s |
| Week-2 return bar | none: the form has no default | FD§9 ("a bar you set") | **no initial default**: the lock is refused while empty [A] |
| Large-job trial success rule (jobs finishing within the quoted window, of the trial jobs) | none | FD§9 decision rule (a) | **no initial default**; the FD proposes a starting rule that is "arbitrary until you set it" [A] |
| Unresolved incident rule (no open safety or provider incident at pilot end) | none | FD§9 | rule text only, no number |

The three rows without a default are keys of `PreRegistration.thresholds` (`thr.week2_return_min`, `thr.large_job_trial_rule`, `thr.open_incident_rule`), not parameters: they exist only inside a lock record, are never in the parameter store and cannot be loosened after locking (`ISS-167`). A pre-registered threshold also lists the decision it feeds (`continue`, `extend`, `stop`) and the data source; S13.* owns the form. [A]

## 16.16 API, security, calibration, metrics, operations

Owner `operator` (`calibration.min_samples_per_service` is `founders`). Binding: read at the next request, job run or cache refresh (`ops.config_cache_ttl_s`); none is stamped on a domain object. All `ops.*` rows are `public: no` except `ops.rpo_s`, `ops.rto_s` and `ops.backup_retention_days` (they are promises members can read) [A]. [D]

| Name | Type · unit | Validation | Initial configurable default | Chg | Cal | Used |
| --- | --- | --- | --- | --- | --- | --- |
| `api.idempotency_ttl_s` | duration_s | 3600..604800 | 86,400 | `N` | `OPS` | S0 0.11.5, S9.10 |
| `api.page_size_default` | int | 1..`api.page_size_max` | 50 | `N` | `OPS` | S15.* |
| `api.page_size_max` | int | 1..1000 | 200 | `T↓` | `OPS` | S15.* |
| `api.cursor_ttl_s` | duration_s | 60..86400 | 3600 | `T↓` | `OPS` | S15.* |
| `api.max_body_bytes` | int · bytes | 1024..104857600 | 1,048,576 (uploads use `job.max_upload_bytes`) | `T↓` | `TEC` | S15.*, S4.* |
| `api.request_timeout_s` | duration_s | 1..300 | 30 | `N` | `TEC` | S15.*, S4.* |
| `security.secret_rotation_days` | int | 1..365 | 90 | `T↓` | `SEC` | S10.* |
| `security.rotate_before_public_exposure` | bool | constant | true (FD§10) | `C` | `CON` | S10.*, S14.* |
| `security.two_person_actions` | json | subset of the action names in S10.* | `["ledger.reversal","launch.signoff","parameter.loosen","killswitch.release"]` [A] | `T↑` (more actions) | `SEC` | S10.*, 16.17 |
| `calibration.min_samples_per_service` | int · cells | 1..10000 | 30 | `T↑` | `FND` | S0 0.10.4, S9.12 |
| `metrics.rollup_interval_s` | duration_s | 60..86400 | 3600 | `N` | `OPS` | S13.*, S4.* |
| `ops.rpo_s` | duration_s | 0..86400 | 300 | `T↓` | `OPS`: restore drill | S4.* |
| `ops.rto_s` | duration_s | 60..604800 | 14,400 | `T↓` | `OPS`: restore drill duration | S4.* |
| `ops.txn_retry_max` | int | 0..20 | 5 | `N` | `OPS`: retry counters | S4.* |
| `ops.capacity_headroom_ratio` | ratio | >= 1 | 5.0 | `T↑` | `OPS`: load test (S4.6.2) | S4.* |
| `ops.clock_skew_alarm_s` | duration_s | 0..60 | 2 | `T↓` | `OPS` | S4.* |
| `ops.outbox_relay_interval_s` | duration_s | 1..60 | 2 | `N` | `OPS` | S4.* |
| `ops.outbox_max_attempts` | int | 1..100 | 10 | `N` | `OPS` | S4.* |
| `ops.outbox_retention_days` | days | 1..90 | 7 | `T↓` | `OPS` | S4.* |
| `ops.outbox_lag_alarm_s` | duration_s | 1..86400 | 60 | `T↓` | `OPS` | S4.* |
| `ops.job_lock_ttl_s` | duration_s | 10..3600 | 120 = 4 x `lease.reap_interval_s` | `N` | `OPS` | S4.* |
| `ops.job_max_runtime_s` | duration_s | 10..3600 (the lock is renewed below it) | 300 | `N` | `OPS` | S4.* |
| `ops.job_overdue_factor` | ratio | >= 1 | 3.0 | `T↓` | `OPS` | S4.* |
| `ops.ttl_sweep_interval_s` | duration_s | 5..3600 | 60 | `N` | `OPS` | S4.* |
| `ops.purge_interval_s` | duration_s | 60..86400 | 3600 | `T↓` | `OPS` | S4.*, S10.* |
| `ops.backup_interval_s` | duration_s | 3600..604800 | 86,400 (meets `ops.rpo_s` together with log archiving) | `T↓` | `OPS` | S4.* |
| `ops.backup_retention_days` | days | 1..365 | 35 | `T↓` | `CNS` (privacy duties), `OPS` | S4.*, S10.* |
| `ops.restore_drill_interval_days` | days | 7..365 | 90 | `T↓` | `OPS` | S4.* |
| `ops.config_cache_ttl_s` | duration_s | 1..600 | 30 | `T↓` | `OPS` | S4.9.2, 16.17 |
| `ops.migration_batch_size` | int | 1..100000 | 1000 | `N` | `OPS` | S4.* |
| `ops.alert_error_ratio` | ratio | 0..1 | 0.05 | `T↓` | `OPS` | S4.11 |
| `ops.alert_window_s` | duration_s | 30..86400 | 300 | `N` | `OPS` | S4.11 |

## 16.17 Configuration mechanics

### 16.17.1 Records [D]

| Record | Fields beyond S0 0.10.3 |
| --- | --- |
| `Parameter` | `name` (PK), `type`, `unit`, `owner_role`, `change_policy` (16.2.2), `tighten_direction` (`lower`, `higher`, `toward:<value>`, `none`), `validation` (json), `default_value`, `public` (bool), `calibration_code`, `constraint_ids`, `introduced_in` (spec part), `prospective_only` (always true except constants, which are immutable) |
| `ParameterVersion` | `parameter_name`, `version` (from 1), `value`, `effective_from`, `change_class` (`tighten`, `loosen`, `neutral`, `seed`), `reason`, `author_admin_id`, `approver_admin_ids`, `created_at`, `withdrawn_at` (null unless withdrawn before it took effect) |

### 16.17.2 Write pipeline [D]

```
function write_parameter(actor, name, new_value, effective_from, reason, batch):
  p = store.get(name)  or reject VALIDATION_FAILED("unknown parameter")      # R16-4
  if p.change_policy == C: reject FORBIDDEN                                  # constants
  if actor.role not in owner_roles(p.area): reject FORBIDDEN
  v = parse(p.type, new_value); check_range_and_enum(p, v)                   # 16.4-16.16 Validation column
  cur = value_at(name, now)
  if v == cur and no pending version differs: return ok(no-op)              # idempotent
  cls = classify(p, cur, v)          # tighten | loosen | neutral, by p.tighten_direction
  if cls == tighten:   effective_from = now                                  # immediate (R10)
  else:                effective_from = max(effective_from or 0, now + notice_days(p) * 86400)
  future = config_as_of(effective_from) with batch applied and (name -> v)   # all pending versions
  for c in constraints(p): if c.kind == error and not c.holds(future): reject VALIDATION_FAILED(c.id)
  need = 1
  if cls != tighten and "parameter.loosen" in value_at("security.two_person_actions"): need = 2
  if p.area == launch: need = max(need, value_at("launch.min_signoffs"))
  if c13_warning(future): need = max(need, 2)                                # mint cap above redeemable
  if cls != tighten and len(reason) < value_at("policy.loosen_reason_min_chars"): reject VALIDATION_FAILED
  require distinct approvers >= need
  transaction:
    insert ParameterVersion(version+1, effective_from, cls, reason, approvers)
    insert ChangeLogEntry(public per 16.17.5, old, new, effective_from, notice)   # S0 0.10.3
    insert AdminAction; emit parameter.changed via the outbox; bump config_epoch when it takes effect
```

A batch is atomic and validated as one future configuration, so an edit that is valid only together with another (for example `credit.lifetime_days` and `credit.lifetime_days_accelerated`) is accepted as a batch and refused as two single edits when the first alone breaks a constraint. Warnings (`C8`, `C13`) are returned in the response and recorded in the log entry. [D]

**Classification** [A]: numeric and duration values use the direction of 16.2.2; booleans and enums use the stated end; lists use set inclusion (a longer `service.required_regions` or `security.two_person_actions` is a tightening, a longer `optin.default_*` or `service.terms_copy_allowed_types` is a loosening); a parameter with several members changed at once is `loosen` if any member loosens.

### 16.17.3 Activation, lookup, caching [D]

`value_at(name, t)` returns the non-withdrawn version with the greatest `effective_from <= t` (higher `version` wins a tie). Time is the server's UTC clock only. A scheduled version takes effect through an idempotent activation job every `ops.ttl_sweep_interval_s`, which bumps `config_epoch`; every event and every stamped object carries the epoch or the version it used. Processes cache values for at most `ops.config_cache_ttl_s`; a `tighten` change also emits `parameter.changed`, so the longest a tightening stays unapplied in one process is that TTL (30 s by default). Kill switches and `launch.*` are read uncached. [D]

### 16.17.4 Rollback [D]

A rollback is a new version with the old value; it is classified by the same rule, so rolling back a tightening is a loosening and takes notice, and rolling back a loosening is a tightening and is immediate. A version that has not yet taken effect may be withdrawn by its author or by any admin of the owner role at any time (`withdrawn_at`), which is itself logged. There is no revert window for parameters; the revert window of S7 (`policy.revert_window_s`) applies to `PolicyVersion` only. [A]

### 16.17.5 Public exposure [D][A]

`GET /v1/public/parameters` (S0 0.11.2) lists, for every public parameter: name, unit, current value, owner role, change-policy code, calibration code, initial default, the next pending version with its `effective_from`, and a link to the change log. A member can therefore see what changes before it changes (FD Principle 5). These rows are `public: no` because publishing the exact value helps an attacker more than it helps a member: `security.*`; `ops.*` except `ops.rpo_s`, `ops.rto_s`, `ops.backup_retention_days`; `identity.recovery_*`; `ratelimit.recovery_attempts_per_day`, `ratelimit.*new_members_per_day`; `grant.max_per_device`; `growth.referral.max_per_referrer_per_30d`; `verify.timing_*`, `verify.duplicate_*`, `verify.audit_rate_*`, `verify.gold_rate_*`, `verify.adapt.*`, `trust.audit_multiplier.*`; the `screen.*` limits. A change to a hidden parameter still produces a public change-log entry that names the area and the change class and gives the notice period, but not the value; an owner may decide that is too little (`ISS-164`). Constants and the structure of the sampling method are public in S8.* and S9.*. [A]

### 16.17.6 Seeding and constants [D]

The first migration inserts every row of this table at `version` 1 with `change_class` `seed` and `effective_from` = migration time, except the alias row `admission.forecast_refresh_s` (`ISS-162`). The `default_value` of a `Parameter` is never updated. A constant is stored for reading and for the public list but refuses writes; changing one is a spec change with a migration note.

## 16.18 Cross-check against FD§4.9

The FD's parameter table is the list that must be configurable and justified. Each item maps to the rows below; the derived values are recomputed by `AC-param-13`. [D]

| FD§4.9 parameter | Row(s) here | Initial configurable default | Basis |
| --- | --- | --- | --- |
| Cell envelope | `cell.envelope.max_input_chars`, `.max_output_chars`, `.max_submission_bytes`, `.expected_time_s` | 4000, 6000, 32,768, 120 | FD§3.2 estimate [H]; replaced by `CAL` |
| E, credit expiry | `credit.lifetime_days`, `credit.lifetime_days_accelerated` | 60 and 14 | FD§4.5 proposal and example arm |
| K, member cap | `credit.member_cap_credits` | 350 | 1.25 x 240 x 1.15, rounded to 50 |
| v, verification overhead | `price.v_prior`, `price.v_cap`, `price.v_window_days`, `price.v_min_sample_cells` (v itself is measured) | 0.10, 0.50, 28 days, 100 cells | FD§3.3 illustrative input as prior only |
| λ, levy | `price.levy_lambda` | 0.05 | FD§3.3 illustrative |
| g, gold rate | `verify.gold_rate_g`, `_floor`, `_max` | 0.05, 0.01, 0.20 | `P1M` |
| s, audit rate | `verify.audit_rate_s`, `_floor`, `_max` | 0.10, 0.02, 0.50 | `P1M`; the floor keeps sampling above zero (FD§4.4) |
| φ, redeemable share | `admission.phi` (and `admission.forecast_haircut`, `admission.horizon_discount_per_day`) | 0.50, 0.00, 0.00 | FD§3.3 illustrative; `P1M` |
| G, starter grant | `grant.starter_credits`, `grant.starter_lifetime_days` | 3, 14 | FD§4.6 |
| Mint cap | `mint.monthly_cap_credits`, `mint.per_member_daily_cap_credits` | 4800, 30 | derived (16.5) |
| Reserve ceiling | `reserve.ceiling_credits` | 1000 | `P1M` |
| Lease timeout | `lease.timeout_s` | 1200 | 10 x 120 s, `CAL` |

Checked against the rows named in the cell and in the other parts; the FD§4.9 table itself was not re-read line by line for this cross-check [V]: C-001 re-checks it at assembly (`ISS-169`).

## 16.19 Calibration plan

A default is replaced only by the named evidence, recorded as a `CalibrationRecord` or a `PreRegistration`, with at least `calibration.min_samples_per_service` cells per service behind a `CAL` value. The pilot has 30 to 50 members (FD§9), too few for statistical claims: a `P1M` value is a descriptive estimate, published with its sample size and the range it was measured over, and no row is tuned inside that range without noting that. [D]

| Code | Evidence and gate | Who decides | Rows it replaces (groups) |
| --- | --- | --- | --- |
| `CAL` | Phase 0 on the founders' own accounts: cells per day per service, seconds per cell, failure and copy-paste error rates (FD§9 Phase 0) | operator, recorded | 16.4 envelope, 16.9 lease, `verify.timing_*`, `mint.monthly_cap_credits` |
| `P1M` | Phase 1 pilot measures (FD§9) | founders | credit and price group, 16.7 admission, 16.8 verification, 16.10 trust, 16.14 UI and i18n |
| `DEM` | Demand check: interviews about real job sizes, splittability, accepted window (FD§8.3 G5) | founders | `credit.member_cap_credits`, `admission.max_job_cells`, `admission.min_window_s`, `admission.max_window_days`, `policy.max_pinned_services` |
| `FND` | A founders' decision locked in a `PreRegistration` before day 1 | founders | floors, maxima, thresholds, `launch.*`, `change.*`, review counts |
| `CNS` | Counsel's answer in the operator's jurisdiction [V] | operator with counsel | `service.review_*`, `service.required_regions`, retention rows marked `CNS`, `ops.backup_retention_days` |
| `SEC` | The G1 threat-model decision | operator | identity, session, retention, security, `analytics.min_cohort_k`, public-exposure choices |
| `TEC` | Feasibility measurement on real phones and desktops (FD§8.3 G2) | operator | `cell.envelope.max_json_depth`, `api.max_body_bytes`, `api.request_timeout_s`, `job.max_upload_bytes` |
| `OPS` | Operating experience: alerts, incidents, capacity dashboard | operator | intervals, TTLs, `ops.*`, anti-farming limits |
| `CON` | None: constants, changed only by a spec change | spec | every `C` row |

## 16.20 Acceptance criteria

| Id | Given | When | Then |
| --- | --- | --- | --- |
| `AC-param-01` | a name not in this table | it is seeded, written or read in a policy or job path | the store refuses it with `VALIDATION_FAILED`; CI fails on a code reference to an unknown name |
| `AC-param-02` | the seeded defaults | the seed check runs | every row satisfies its range and every constraint of 16.3, and the derived defaults recompute to the stored values |
| `AC-param-03` | an operator lowers `admission.phi` | the write is accepted | `change_class` is `tighten`, `effective_from` is now, and the log entry is public within `change.tighten_publish_within_s` |
| `AC-param-04` | an operator raises `admission.phi` | the write is made without a second approver or with `effective_from` earlier than now + 14 days | it is refused; with a second approver and 14 days of notice it is accepted as `loosen` |
| `AC-param-05` | two pending versions that are each valid but together break `C7` | the second is written | it is refused naming `C7`; as one batch with a fix it is accepted |
| `AC-param-06` | a constant such as `lease.nonce_bytes` | any write is attempted | refused with `FORBIDDEN`, and nothing is logged as a change |
| `AC-param-07` | a lease issued under `lease.timeout_s` = 1200 | the value is changed to 600 and effective | the issued lease keeps its stamped expiry; the next lease uses 600 |
| `AC-param-08` | a tightening that is then rolled back | the rollback is written | it is classified `loosen` and takes notice; withdrawing a pending version before `effective_from` is immediate and logged |
| `AC-param-09` | `retention.job_payload_days` lowered from 30 to 14 | the next purge run executes | payloads older than 14 days are deleted; raising it later does not restore them |
| `AC-param-10` | a hidden parameter such as `verify.audit_rate_s` is changed | the public parameters list and the change log are read | the list omits the row; the log entry names the area, class and notice but not the value |
| `AC-param-11` | a write is repeated with the same `Idempotency-Key` and body | the second arrives | the first response is replayed and no second `ParameterVersion` exists |
| `AC-param-12` | the `PreRegistration` form for Phase 1 | it is locked with an empty week-2 return bar or large-job trial rule | the lock is refused; after locking, editing the seeding parameter does not change the locked threshold |
| `AC-param-13` | the derived defaults 350, 300, 4800, 1200, 32,768 | CI recomputes them from the FD§3.3 inputs | each equals its stored default or the build fails |
| `AC-param-14` | the alias row `admission.forecast_refresh_s` | the seed runs | it is not created and a write to it is refused as unknown |
| `AC-param-15` | code that compares a number with a literal threshold in a policy, ledger, admission, verification, lease or retention path | the config-literal lint runs | it fails unless the literal is a constant of S0 or is read through `value_at` |

## 16.21 Hypotheses, verifications, assumptions

**Hypotheses [H]** (each default above is one; the ones most likely to be wrong): `admission.forecast_haircut` and `admission.horizon_discount_per_day` at 0.00 are too optimistic; `admission.min_forecast_donors` = 10 is the right floor; `ui.comprehension_check_rate` 0.00 is acceptable; the FD§3.2 time estimates behind `cell.envelope.expected_time_s`; `verify.timing_regular_cv` = 0.05; `i18n.digits_default_fa` = `persian`.

**Verifications [V]** (what, by whom, where stored): counsel's answer on regions and retention (`CNS`, counsel memo reference on the `ParameterVersion` reason); the G1 threat-model decision on public exposure of anti-abuse values (`SEC`); a line-by-line check of the FD§4.9 table at assembly (C-001); the measurement for every `CAL` and `P1M` row, stored as `CalibrationRecord` or in the pilot report.

**Assumptions [A]** (with the decision that could overturn each): change directions not stated by a defining part are assigned by the rule in 16.2.2 (owner decision on any row); retention lowering is applied to existing rows (16.11); hidden-parameter list and value-less log entries (16.17.5); no revert window for parameters (16.17.4); the union enum for `screen.output_request_action`; thresholds in 16.15 without a default are `PreRegistration` keys.

**What this part cannot promise** [D]: a default is a guess until its replacing measurement exists; nothing here shows that any default is safe for real members, legal in any jurisdiction or sufficient for the pilot's 30 to 50 members; two-person approval is only as strong as the number of distinct admins (`ISS-168`).

## Issues raised

Convention additions and problems found while completing the table. None blocks this part; `needs_owner` marks a decision only the owner can make. [D]

| Id | Severity | Status | Finding | Proposed resolution |
| --- | --- | --- | --- | --- |
| `ISS-161` | major | proposed | Parts S4, S6 (admission), S7 and S9 added names that S0 0.10.6 does not list (22 `ops.*` and alias, 15 admission and reservation, 14 policy, screen and service, 17 cell, lease, screen and verify), and a new area `ops` (`ISS-45`). S0 says its list is the full set. | This table is the complete list; added names are accepted as written; S0 0.10.5 gains the `ops` area (owner `operator`, defining part S4) and the S0 list is regenerated from this table at assembly. |
| `ISS-162` | minor | proposed | One concept has two names: `admission.forecast_refresh_s` (S4 4.19.1) and `admission.reforecast_interval_s` (S6 admission file). | Keep `admission.reforecast_interval_s`; the other is listed as an alias that is not seeded; S4 4.19.1 is amended at assembly. |
| `ISS-163` | minor | proposed | Two value conflicts: `service.terms_copy_max_bytes` is 5,242,880 in S0 and 10,485,760 in S7 (S7 added it only "if absent from S0"); `screen.output_request_action` is defined in both S7 (`quarantine`, `reject`) and S9 (`reject`, `flag_for_review`, `quarantine`). | S0's 5,242,880 stands; one parameter with the union enum and the strictness order `flag_for_review` < `quarantine` < `reject`; S7 7.15.1 and S9 9.18 reference this table. |
| `ISS-164` | major | proposed | S0 0.10.3 requires `tighten_direction` on every parameter but defines it only for a few (`verify.audit_rate_s`, `admission.phi`, and the S6 rows); no part says which parameters are public. | Directions are assigned by the rule in 16.2.2 and the `Chg` column; public flags by 16.17.5; both are [A] and an owner may change any cell. The decision to publish names but not values of anti-abuse parameters is the owner's. |
| `ISS-165` | minor | proposed | Constraint ids: S0 has `C1`..`C8`, the admission part proposes `C9`..`C12`, S9 proposes `S9-C1`..`S9-C3`; several limits in S5 to S9 have no constraint id. | `C13`..`C20` are added in 16.3; `S9-C1`..`S9-C3` are kept as written; S0 0.10.3 is regenerated from 16.3 at assembly. |
| `ISS-166` | minor | proposed | S0 derives `mint.monthly_cap_credits` with (1 - phi) and S6 (ledger) with phi; both equal 0.5, so 4,800 is right either way, but the two diverge if phi changes. | The derivation is phi x forecast capacity (S6 ledger 6.11.5); `C13` warns when the cap exceeds forecast redeemable capacity; S0's wording is corrected at assembly. |
| `ISS-167` | minor | proposed | FD§9 decision rules (week-2 return bar, large-job trial rule, open-incident rule) have no parameter names and the FD gives no numbers for two of them. | They are `PreRegistration.thresholds` keys (`thr.week2_return_min`, `thr.large_job_trial_rule`, `thr.open_incident_rule`), not parameters, with no initial default; S13.* defines the form; S0 0.7 gains the keys. |
| `ISS-168` | major | needs_owner | Two-person rules (`service.min_approvers` 1 vs `policy.loosen_min_approvers` 2, `launch.min_signoffs` 2, `security.two_person_actions`) assume at least two distinct admins; with one admin every loosening and every sign-off is blocked. | Owner decision: the number of admins at launch. Until decided the defaults stand and `C19` warns; the fallback of FD§8.3 (documented single-person approval with a stated reason) needs the owner's explicit choice. |
| `ISS-169` | major | proposed | When this part was written S8, S10 to S15 and S1 to S3 were not on main, so parameters they add (for example UI budgets for S11, gate parameters for S14, template and verification details for S8) are missing, and the FD§4.9 cross-check was not re-read line by line. | C-001 assembly adds their names to the matching group table, re-checks FD§4.9 row by row and re-runs `AC-param-01` and `AC-param-15` over the assembled spec; any `area.name` found in a later part and absent here is a convention gap by R16-4. |
