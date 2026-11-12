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
