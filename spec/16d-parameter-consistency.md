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

## 16.D.3 Relations added by this file

The cell's own examples (phi, audit floor, lease against envelope, credit lifetime against reservation horizon, K against a large job, levy and v against eta, referral draw against Reserve, rate-limit ordering) are rows below or in 16.D.2. A row that fails at the defaults is a finding in 16.D.4, not a change of the relation. [D]

| Id | kind | Relation | Arithmetic at the initial defaults | Result |
| --- | --- | --- | --- | --- |
| `S16D-C1` | err (first part), warn (second) | eta window: `price.eta_alarm_threshold <= 1 / (1 + price.v_prior + price.levy_lambda)` and `price.eta_alarm_threshold > 1 / (1 + price.v_cap + price.levy_lambda)`; also `price.eta_alarm_threshold > 0` | 1/1.15 = 0.8696 >= 0.80; 1/1.55 = 0.6452 < 0.80. Equivalent: eta >= 0.80 holds while v + lambda <= 1/0.80 - 1 = 0.25, i.e. v <= 0.20 at lambda 0.05; the alarm is reachable because `price.v_cap` 0.50 > 0.20 | pass (`F-01`) |
| `S16D-C2` | warn | gold floor positive: `verify.gold_rate_floor > 0` (extends `C2`) | 0.01 > 0 | pass |
| `S16D-C3` | warn [V] | held credit ages: `reservation.max_horizon_days + admission.max_window_days <= credit.lifetime_days` AND `<= credit.lifetime_days_accelerated`, applied only if credit held in escrow keeps its lot expiry (S6 must confirm) | 30 + 14 = 44 <= 60 passes; 44 <= 14 **fails** in the arm | fail in the arm (`F-03`) |
| `S16D-C4` | err | a free cancel exists: `reservation.min_lead_s >= reservation.free_cancel_notice_s` | 86,400 >= 86,400 | pass (equal) |
| `S16D-C5` | err | window floor: `admission.min_window_s >= admission.window_step_s` and `admission.window_step_s >= 1` | 43,200 >= 43,200; 43,200 >= 1 | pass (`F-05`) |
| `S16D-C6` | err | upload fits the largest job: `job.max_upload_bytes >= admission.max_job_cells * cell.envelope.max_input_chars * 3` | 4,194,304 >= 300 x 4,000 x 3 = 3,600,000 | pass |
| `S16D-C7` | err | submissions fit the JSON body: `api.max_body_bytes >= cell.envelope.max_submission_bytes` | 1,048,576 >= 32,768 | pass |
| `S16D-C8` | err | a price change never falls inside a quote: `price.quote_ttl_s <= change.notice_days_price * 86400` and `admission.waitlist_quote_ttl_s <= change.notice_days_price * 86400` | 1,800 and 86,400 <= 1,209,600 | pass (backs the claim in S16 16.6) |
| `S16D-C9` | err | notice is real: `change.notice_days_default >= 1` and `change.notice_days_price >= change.notice_days_default` | 7 >= 1; 14 >= 7 | pass; ranges currently allow 0 (`F-07`) |
| `S16D-C10` | err | tier ordering: `trust.cap_multiplier.restricted <= trust.cap_multiplier.new <= trust.cap_multiplier.established <= trust.cap_multiplier.trusted`; `trust.audit_multiplier.restricted >= trust.audit_multiplier.new >= trust.audit_multiplier.established >= trust.audit_multiplier.trusted`; `trust.established_min_cells <= trust.trusted_min_cells`; `verify.new_donor_blanket_cells <= trust.established_min_cells` (warn) | 0.25 <= 0.50 <= 1.00 <= 1.50; 3.0 >= 1.0 >= 1.0 >= 0.5; 10 <= 100; 5 <= 10 | pass |
| `S16D-C11` | err | a shingle fits the shortest compared text: `verify.duplicate_min_chars >= verify.duplicate_shingle_chars` | 80 >= 5 | pass; ranges allow 1 (`F-08`) |
| `S16D-C12` | err | a streak is observable: `verify.adapt.clean_streak <= verify.reliability_window_obs` | 20 <= 50 | pass |
| `S16D-C13` | err | the daily per-IP-hash limit needs a day of hash: `retention.ip_hash_ttl_days >= 1` | 1 >= 1 | pass; range allows 0 (`F-06`) |
| `S16D-C14` | warn [V] | windows stay inside retention of the data they read, if they read raw events: `price.v_window_days <= retention.event_raw_days` and `inflation.throughput_window_days <= retention.event_raw_days` | 28 <= 30; 28 <= 30 (2 days of margin) | pass; S13 and S6 confirm the data source |
| `S16D-C15` | warn | an appeal can be decided while the payload exists: `appeal.window_days + appeal.reviewer_sla_days <= retention.job_payload_days` and `appeal.window_days <= retention.moderation_days` | 14 + 7 = 21 <= 30; 14 <= 180 | pass |
| `S16D-C16` | warn | rate-limit ordering: `ratelimit.device_new_members_per_day <= ratelimit.invite_tree_new_members_per_day`; `ratelimit.device_new_members_per_day <= ratelimit.ip_hash_new_members_per_day`; `ratelimit.public_rpm <= ratelimit.member_api_rpm <= ratelimit.admin_api_rpm`; `ratelimit.member_leases_per_hour <= ratelimit.member_submissions_per_hour`; `lease.max_active_per_member <= ratelimit.member_leases_per_hour` | 3 <= 10; 3 <= 10; 60 <= 120 <= 300; 30 <= 60; 3 <= 30 | pass; the ordering device < tree < day holds, but there is no day-level cap on joins (`F-12`) |
| `S16D-C17` | err / warn | grant ordering: `grant.max_per_invite_tree_per_day <= grant.max_per_day` (err); `grant.max_per_invite_tree_per_day <= ratelimit.invite_tree_new_members_per_day` (warn); `growth.referral.min_newcomer_verified_cells >= grant.required_verified_cells` (warn, a bonus never pays before the grant gate) | 2 <= 20; 2 <= 10; 1 >= 1 | pass; `grant.max_per_device` is a lifetime count and is not in a per-day ordering |
| `S16D-C18` | warn | one member cannot take the whole month, and the Reserve holds a day of grants: `mint.per_member_daily_cap_credits * 30 <= mint.monthly_cap_credits`; `reserve.ceiling_credits >= grant.max_per_day * grant.starter_credits` | 900 <= 4,800; 1,000 >= 20 x 3 = 60 | pass |
| `S16D-C19` | warn | approvers can exist: count of active AdminUser >= max(`launch.min_signoffs`, `policy.loosen_min_approvers`, `ledger.reversal_min_approvers`, `appeal.ban_min_reviewers`, `template.min_reviewers_new`) (generalises `C19`) | max(2, 2, 2, 2, 2) = 2 | pass only with 2 or more admins (`F-14`) |
| `S16D-C20` | err | the two-person rule cannot be edited away: `security.two_person_actions` always contains `parameter.loosen` | contains it | pass |
| `S16D-C21` | warn | a team shown publicly is not a suppressed cohort: `team.min_public_members >= analytics.min_cohort_k` and `team.min_public_members <= team.max_members` | 5 >= 10 **fails**; 5 <= 50 | fail (`F-10`) |
| `S16D-C22` | err | UI caps never above server caps and polls ordered: `ui.requester.appeal_note_max_chars <= appeal.reason_max_chars`; `ui.requester.progress_poll_s <= ui.status_poll_max_s` | 1,000 <= 1,000; 30 <= 60 | pass; the UI range allows 0 to 5,000 (`F-11`) |
| `S16D-C23` | warn | check order: `ledger.invariant_check_interval_s <= ledger.full_recompute_interval_s <= ledger.checkpoint_interval_s`; `ops.job_lock_ttl_s <= ops.job_max_runtime_s`; `admission.reforecast_interval_s >= metrics.rollup_interval_s` | 60 <= 3,600 <= 86,400; 120 <= 300; 3,600 >= 3,600 | pass |
| `S16D-C24` | warn | an anomaly floor below the expected time: `verify.timing_min_s < cell.envelope.expected_time_s` | 5 < 120 | pass |

Result: 24 added relations; 22 pass at the defaults and in both arms; `S16D-C3` and `S16D-C21` fail and are `F-03` and `F-10`. [D]

**Equality-by-design pairs without a validator** [D]: `admission.donor_daily_clamp_cells` = `mint.per_member_daily_cap_credits` (30, left unlinked on purpose: the clamp counts all cells, the mint cap only Commons cells); `session.touch_min_interval_s` = `session.step_up_max_age_s` (300, bound by `S16B-C3` only); `grant.starter_lifetime_days` = `credit.lifetime_days_accelerated` (14, bound by `C4`); `ops.job_lock_ttl_s` = 4 x `lease.reap_interval_s` (120, a derivation of a default, not a relation).

**Lone tightening refused** [D]: R10 says a tightening applies at once, yet a relation can refuse it when the other side is not moved. Pairs where tightening one alone is refused and a batch is required (S16 16.17.2): `retention.session_days` with `session.member_abs_ttl_s` and `session.admin_abs_ttl_s` (`S16B-C1`); `session.member_abs_ttl_s` with `session.member_idle_ttl_s` (`C15`); `verify.audit_rate_floor` with `verify.audit_rate_s` (`C2`); `trust.established_min_reliability` with `trust.trusted_min_reliability` (`C16`); `growth.referral.qualify_window_days` with `growth.referral.hold_s` (`S16B-C5`); `admission.min_history_days` with `admission.forecast_window_days` (`C10`). The refusal message must name the partner and offer the batch (`F-16`).
