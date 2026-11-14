# 16.D Parameter consistency

*Spec part 16, file 16d (audit and reconcile; cell C-036) · audits `spec/16-parameters.md` (S16), `spec/16b-parameters-a.md` (16.B), `spec/16c-parameters-b.md` (16.C) and the parameter sections of `spec/00-conventions.md` (S0 0.10) as ONE table. It renames nothing, edits no other file and changes no default silently: every change to another file is stated exactly under `## Corrections required`. Written against Founding Document draft v0.1 (FD). Nothing here is legal advice and nothing has been verified against any provider's terms or any law.*

## 16.D.1 Scope, method and limits

| Topic | Decision |
| --- | --- |
| Object | The three tables (S16, 16.B, 16.C) plus S0 0.10.6 tables A, B, C and the constraints of S0 0.10.3 `C1`..`C8`. Together they hold about 560 rows; the relations between them are the subject of this file. [D] |
| Method | Every relation of every table was re-computed from the initial defaults, and the defaults were also checked against their own range column. Every default of S16 16.4..16.16, 16.B and 16.C lies inside its own range (checked row by row); the failures found are in the relations and in ranges that are missing, and are listed in 16.D.4. [D] |
| New relation ids | `S16D-C1`..`S16D-C24`, in the pattern of `S9-C1`, `S16B-C1` and `S16C-C1`, so nothing collides with `C1`..`C20`. They are evaluated like every other constraint: on every write, against the configuration as it will be at `effective_from` with all pending versions (S16 16.17.2). An `error` refuses the write with `VALIDATION_FAILED` naming the id; a `warning` is accepted, returned in the response and recorded in the change-log entry. Until C-001 folds them into S16 16.3 at assembly (`ISS-169`), this file is part of the table, so `AC-param-01` and `AC-param-15` apply to its names. [D][A] |
| Defaults | No default is changed by this file. Where a default conflicts, 16.D.4 names the corrected default and the reason, and `## Corrections required` carries the exact edit. [D] |
| What was NOT read | S4, S6, S8, S9, S10, S11, S12, S13, S14 and S15 were not read (the cell names only the three tables, S0, the FD and the decisions file). A statement about their behaviour is taken from the quoted table text and marked [V] with the part that must confirm it. The S11 console file behind `abuse.admin_lookup_rate` and `session.admin_stepup_s` is one of them: this cell could not resolve `ISS-16015` (see 16.D.5). [A][V] |
| Arms | The accelerated-expiry arm (FD§4.5, FD§9) replaces `credit.lifetime_days` by `credit.lifetime_days_accelerated` for the members in it. A relation that mentions `credit.lifetime_days` must therefore hold for BOTH values; 16.D.2 and 16.D.3 say which do not. [D][A] |

## 16.D.2 Relations already defined, re-verified

Formula, defaults arithmetic and result for each of the 46 relations of S0, S16, 16.B and 16.C. `kind` is the kind its defining part gave (`err` refuses, `warn` returns and logs). [D]

| Id | kind | Relation | Arithmetic at the initial defaults | Result |
| --- | --- | --- | --- | --- |
| `C1` | err | `0 < admission.phi < 1` | 0 < 0.50 < 1 | pass |
| `C2` | err | `verify.audit_rate_floor <= verify.audit_rate_s <= verify.audit_rate_max`; same for gold; `verify.audit_rate_floor > 0` | 0.02 <= 0.10 <= 0.50; 0.01 <= 0.05 <= 0.20 | pass; gap: no `> 0` for the gold floor (`F-09`) |
| `C3` | err | `lease.timeout_s >= cell.envelope.expected_time_s` | 1,200 >= 120 | pass |
| `C4` | err | `credit.lifetime_days_accelerated <= credit.lifetime_days`; `grant.starter_lifetime_days <= credit.lifetime_days` | 14 <= 60; 14 <= 60 | pass |
| `C5` | err | `reserve.ceiling_credits >= grant.starter_credits` | 1,000 >= 3 | pass |
| `C6` | err | `0 <= price.levy_lambda < 1`; `price.v_prior <= price.v_cap` | 0 <= 0.05 < 1; 0.10 <= 0.50 | pass |
| `C7` | err | `admission.min_window_s <= admission.max_window_days * 86400` | 43,200 <= 1,209,600 | pass; no lower bound on the min window (`F-05`) |
| `C8` | warn | `credit.member_cap_credits >= admission.max_job_cells * (1 + price.v_prior + price.levy_lambda)` | 350 >= 300 x 1.15 = 345 (margin 5) | pass at the prior; fails at `price.v_cap` (`F-04`) |
| `C9` | err | `admission.min_window_s` and `admission.max_window_days * 86400` are multiples of `admission.window_step_s` | 43,200 / 43,200 = 1; 1,209,600 / 43,200 = 28 | pass; zero would pass too (`F-05`) |
| `C10` | err | `admission.min_history_days <= admission.forecast_window_days`; `admission.active_donor_window_days <= admission.forecast_window_days` | 3 <= 14; 7 <= 14 | pass |
| `C11` | err | `reservation.min_lead_s <= reservation.max_horizon_days * 86400` | 86,400 <= 2,592,000 | pass |
| `C12` | err | `admission.waitlist_quote_ttl_s >= price.quote_ttl_s` | 86,400 >= 1,800 | pass |
| `S9-C1` | err | `cell.envelope.max_submission_bytes >= 3 * cell.envelope.max_output_chars` | 32,768 >= 18,000 | pass |
| `S9-C2` | err | `verify.duplicate_minhash_perms` is a multiple of 4 | 128 = 4 x 32 | pass |
| `S9-C3` | err | `lease.max_validations >= 0`; `lease.max_gate_failures >= 1` | 10 >= 0; 5 >= 1 | pass |
| `C13` | warn + 2nd approver | `mint.monthly_cap_credits <= floor(phi x accepted_cells_in_window x 30 / inflation.throughput_window_days)` (phi as integer ppm, 10^6 scaled both sides) | skipped in Phase 0; at the FD§3.3 throughput (40 x 8 x 28 = 8,960 cells in 28 days): floor(0.5 x 8,960 x 30 / 28) = 4,800 >= 4,800 | pass with zero margin; the phi factor is wrong off 0.5 (`F-02`) |
| `C14` | err | `lease.extend_s <= lease.timeout_s`; `lease.submit_grace_s <= lease.timeout_s` | 600 <= 1,200; 120 <= 1,200 | pass |
| `C15` | err | `session.member_idle_ttl_s <= session.member_abs_ttl_s`; `session.admin_idle_ttl_s <= session.admin_abs_ttl_s` | 2,592,000 <= 7,776,000; 1,800 <= 28,800 | pass |
| `C16` | err | `trust.demote_below_reliability <= trust.established_min_reliability <= trust.trusted_min_reliability` | 0.70 <= 0.80 <= 0.95 | pass |
| `C17` | err | `reserve.retire_min_credits <= reserve.ceiling_credits`; `credit.expiry_notice_days <= credit.lifetime_days_accelerated` | 10 <= 1,000; 7 <= 14 | pass (both lifetimes: 7 <= 14 and 7 <= 60) |
| `C18` | err | `admission.donor_daily_clamp_cells >= 1`; `mint.per_member_daily_cap_credits >= 1` | 30 >= 1; 30 >= 1 | pass |
| `C19` | err / warn | `launch.required_gate_ids` contains `G0` and `G1` (err); `launch.min_signoffs <= count of active AdminUser` (warn) | `["G0","G1"]`; 2 <= number of admins [V] | pass on the list; the warn passes only with 2 or more admins (`F-14`) |
| `C20` | err | `policy.loosen_min_approvers >= policy.tighten_min_approvers`; `policy.loosen_min_notice_days >= change.notice_days_default` | 2 >= 1; 7 >= 7 | pass |
| `S16B-C1` | err | `session.member_abs_ttl_s <= retention.session_days * 86400` and the same for `session.admin_abs_ttl_s` | 7,776,000 <= 90 x 86,400 = 7,776,000; 28,800 <= 7,776,000 | pass with zero margin (`F-16`) |
| `S16B-C2` | err | `session.max_active_per_member >= identity.max_devices_per_member` | 10 >= 5 | pass |
| `S16B-C3` | err | `session.touch_min_interval_s < min(session.member_idle_ttl_s, session.admin_idle_ttl_s)` | 300 < min(2,592,000; 1,800) = 1,800 | pass |
| `S16B-C4` | warn | `3 * max(report.max_text_chars, appeal.reason_max_chars, team.label_max_chars) <= api.max_body_bytes` | 3 x 1,000 = 3,000 <= 1,048,576 | pass |
| `S16B-C5` | err | `growth.referral.hold_s < growth.referral.qualify_window_days * 86400` | 86,400 < 2,592,000 | pass |
| `S16B-C6` | warn | `growth.referral.clawback_window_days <= credit.lifetime_days` | 30 <= 60; **30 <= 14 fails in the arm** | pass for 60, fail for the arm (`F-03`, `ISS-16019`) |
| `S16B-C7` | warn | `growth.referral.max_per_invite_tree_per_30d >= growth.referral.max_per_referrer_per_30d` | 5 >= 5 | pass (equal) |
| `S16B-C8` | warn | `growth.referral.max_per_day * (growth.referral.bonus_referrer_credits + growth.referral.bonus_newcomer_credits) <= reserve.ceiling_credits * growth.referral.reserve_draw_cap_ratio` | 5 x (1 + 1) = 10 <= 1,000 x 0.10 = 100 | pass at a full Reserve; at a start-of-day balance of 50 the real cap is 5 credits (2 pairs), see `F-13` |
| `S16B-C9` | err | `report.urgent_triage_sla_s <= report.triage_sla_days * 86400` | 14,400 <= 259,200 | pass |
| `S16C-C1` | err | `ui.budget.first_load_bytes >= ui.budget.js_bytes + ui.budget.css_bytes + ui.budget.fonts_bytes` | 204,096 >= 200,000 | pass |
| `S16C-C2` | err | `ui.budget.cell_card_bytes >= cell.envelope.max_input_chars * 3` | 16,096 >= 12,000 | pass |
| `S16C-C3` | warn | `ui.budget.repeat_view_bytes >= ui.budget.cell_card_bytes + cell.envelope.max_submission_bytes` | 65,248 >= 16,096 + 32,768 = 48,864 | pass |
| `S16C-C4` | err | `lease.timeout_s + lease.max_extensions * lease.extend_s + lease.submit_grace_s <= ui.draft.ttl_s <= 86400` | 1,200 + 600 + 120 = 1,920 <= 3,600 <= 86,400 | pass; baseline wording `F-15` |
| `S16C-C5` | err | `ui.lease.warn_remaining_s <= lease.timeout_s` | 300 <= 1,200 | pass |
| `S16C-C6` | err | `ui.retry.base_delay_s <= ui.retry.max_delay_s <= 600` | 2 <= 60 <= 600 | pass |
| `S16C-C7` | err | `metrics.large_job_min_cells <= admission.max_job_cells` | 240 <= 300 | pass |
| `S16C-C8` | warn | `ceil(1 / lease.max_job_share_ratio) <= admission.min_forecast_donors` | ceil(2.94) = 3 <= 10 | pass |
| `S16C-C9` | warn | `verify.review_channel_daily_cap_cells <= mint.per_member_daily_cap_credits` | 20 <= 30 | pass |
| `S16C-C10` | warn | `ui.admin_claim_ttl_s <= session.admin_idle_ttl_s` | 1,800 <= 1,800 | pass (equal) |
| `S16C-C11` | warn | `ui.requester.rating_flag_cells_max <= admission.max_job_cells` | 20 <= 300 | pass |
| `S16C-C12` | warn | `metrics.daily_rollup_offset_s >= ops.outbox_lag_alarm_s` | 1,800 >= 60 | pass |
| `S16C-C13` | warn | `ui.requester.rating_window_days <= retention.job_payload_days` | 14 <= 30 | pass |
| `S16C-C14` | err | `ledger.member_timestamp_granularity_s` and `job.manifest_time_granularity_s` each divide 86,400 | 86,400 / 86,400 = 1; 86,400 / 3,600 = 24 | pass |

Result: 46 relations, 46 pass at the initial defaults when evaluated against the standard lifetime `credit.lifetime_days` = 60; `S16B-C6` fails when evaluated against the accelerated lifetime of 14 days. Four of the passes have zero or negligible margin (`C13`, `S16B-C1`, `S16B-C7`, `S16C-C10`, plus `C8` at 5 credits); a one-step edit of either side breaks them, which is the intended effect of an equality default and is why `16.D.4` `F-16` asks that a lone tightening be refused with a batch hint. [D]
