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

## 16.D.4 Findings from the arithmetic

Each finding: what fails, the arithmetic, the corrected default or validation, and why. `no default change` means the relation or text is corrected, not the number. Severity is `major` where a safety control or a promise to members is affected. [D]

| Id | Sev | Finding and arithmetic | Correction and reason |
| --- | --- | --- | --- |
| `F-01` | major | S16 16.15 labels `price.eta_alarm_threshold` "Reserve inflow versus spend". FD§4.3 and FD§0.1 item 10 define eta = 1/(1+v+lambda), cells a member can request per cell contributed, with a suggested floor of 0.8. At the defaults eta = 1/1.15 = 0.8696; eta falls under 0.80 when v > 1/0.80 - 1 - 0.05 = 0.20; at `price.v_cap` eta = 1/1.55 = 0.6452. The range `0..1` also allows 0, which makes the alarm unreachable | no default change. Relabel (CR-01); validation `> 0 .. 1` and `S16D-C1` (CR-21). Reason: the pre-registered threshold (16.15) must be judged on the quantity the FD names |
| `F-02` | major | `mint.monthly_cap_credits` = 4,800 is derived in S0 as 40 x 8 x 30 x (1 - 0.5) and in S16 as x phi; ISS-166 and `ISS-16108` leave it open. FD§4.8 leaves (1 - phi) of capacity to Commons work, which is where credit is minted, so minting cannot exceed (1 - phi) of the cells; FD§4.2 bounds the cap by forecast redeemable capacity, which is phi of them. Both bounds hold at once, so the cap is bounded by min(phi, 1 - phi) x cells. At phi = 0.5 all three agree (4,800). At phi = 0.8 S16's `C13` would allow 7,680 although only 0.2 x 9,600 = 1,920 Commons cells exist to mint | no default change. `C13` and the S0 and S16 default text use min(phi, 1 - phi) (CR-02). Reason: a cap above the Commons cells that can exist is dead; a cap above redeemable capacity inflates claims (FD§4.7). Owner of S6.* confirms the meaning of "redeemable" [V] |
| `F-03` | major | A reservation escrows credit at booking (FD§4.8) for up to `reservation.max_horizon_days` = 30 and then runs a window of up to `admission.max_window_days` = 14: 44 days. In the accelerated arm lots live 14 days (`credit.lifetime_days_accelerated`), so if held credit keeps ageing, a reservation can outlive its own funding (30 > 14 even before the job starts). Standard arm: 44 <= 60 passes. `S16B-C6` fails the same way (30 > 14) | no default change (the arm is an FD§9 design, and the answer depends on S6 [V]). `S16D-C3` added as a warning evaluated against both lifetimes (CR-24). Decision for S6 and the founders before day 1: either escrowed credit is exempt from expiry until settlement (then `S16D-C3` is moot) or `ff.job.reservations` stays off for the arm. Never silently refund expired credit |
| `F-04` | major | `C8` uses `price.v_prior` (0.10) but v is measured and can reach `price.v_cap` (0.50). At v = 0.50: 300 x (1 + 0.50 + 0.05) = 465 > 350, so a maximum job is not holdable. The break-even v at K = 350 is 350/300 - 1 - 0.05 = 0.1167. Tier caps make it stricter: `trust.cap_multiplier.new` x K = 175 holds only 175/1.15 = 152 cells, `restricted` 87.5 holds 76 cells; only `established` (350) and `trusted` (525) reach the maximum job | no default change. Keep `C8` (prior) as the error-free warning; the quote path must return `CAP_EXCEEDED` with the largest holdable job for the member's tier, and the pilot report publishes v against 0.1167. Alternative if founders want the maximum job always holdable: K = 500 (465 rounded up to 50) or `admission.max_job_cells` = 200 (200 x 1.55 = 310 <= 350); a founders' decision [A] |
| `F-05` | minor | `admission.min_window_s` has no numeric range and `admission.window_step_s` only "divides 86,400". 0 is a multiple of the step, so `C7` and `C9` accept a zero-length minimum window | validation `admission.window_step_s .. admission.max_window_days x 86400` for the min window and `1 .. 86,400` for the step (CR-03), `S16D-C5`. Reason: a quote needs a positive window |
| `F-06` | major | `retention.ip_hash_ttl_days` has range `0..30` and is a tightening when lowered (applies at once, 16.11). The per-IP-hash daily join limit (`ratelimit.ip_hash_new_members_per_day`, 10 per day) cannot work with less than one day of hash. A value of 0 silently switches the limit off | validation `1..30` and `S16D-C13` (CR-04). Reason: a safety limit must not be disabled by a tightening of another row |
| `F-07` | major | `change.notice_days_default` and `change.notice_days_price` have range `0..90`. FD Principle 5 and R10 require advance notice of a loosening; 0 removes the notice for every row (and `C20` bounds `policy.loosen_min_notice_days` only from below) | validation `1..90` for both, `change.notice_days_price >= change.notice_days_default` (CR-06), `S16D-C9`. Defaults 7 and 14 unchanged |
| `F-08` | minor | `verify.duplicate_shingle_chars` (2..20) can exceed `verify.duplicate_min_chars` (1..10000); a text shorter than one shingle has no similarity | `S16D-C11` (CR-17) |
| `F-09` | major | `C2` requires `verify.audit_rate_floor > 0` (FD§4.4: sampling has a floor) but not the gold floor; `verify.gold_rate_floor` could be 0 and a patient bad actor could coast under gold checks | `verify.gold_rate_floor > 0` in `C2` and `S16D-C2` (CR-05) |
| `F-10` | major | `team.min_public_members` = 5 shows a team publicly from 5 members, while `analytics.min_cohort_k` = 10 suppresses aggregates for cohorts under 10. A team of 5 to 9 members would publish totals that the cohort rule suppresses | corrected default `team.min_public_members` = 10 (= `analytics.min_cohort_k`) and `S16D-C21` (CR-08) [A]. Reason: the privacy rule must not be bypassed by a team page. The owner may instead exempt team totals; that is a `SEC` decision. At a pilot of 30 to 50 few teams reach 10; that is the intended trade (16.B.5 note 2) |
| `F-11` | minor | `ui.requester.appeal_note_max_chars` has range `0..5,000` while the server limit `appeal.reason_max_chars` is 100..10,000 (default 1,000). 0 stops a requester from stating a reason; a value above the server limit is refused later by the API | range `100 .. appeal.reason_max_chars` and `S16D-C22` (CR-14). The field name (note or reason) is [V] for S15 (`ISS-16111`) |
| `F-12` | minor | The cell's ordering device < tree < day holds for joins (3 < 10) and for grants (1 lifetime, 2 per tree per day, 20 per day), but no `ratelimit.*` row limits joins per day for the whole platform, and the per-IP-hash and per-tree limits are both 10, so ten trees can join 100 members a day before `invite.*` caps bind | no default change. Owner decision (S10): a platform-wide join limit per day if the registration is open. Until then `launch.members_may_join` (default false) is the only global brake |
| `F-13` | major | Reserve funding: grants are paid from the Reserve and pause when it is empty (FD§4.6, `grant.reserve_floor_credits` = 0). The daily outflow cap is `grant.max_per_day` x `grant.starter_credits` = 20 x 3 = 60 credits plus referral draws of at most 10 = 70 credits a day; the ceiling 1,000 holds 14.3 days of that. At the FD§3.3 inputs the levy inflow is at most lambda x 160 = 8 credits a day (phi x 320 cells a day x 0.05), so the 60-credit grant cap is 7.5 times the inflow and the Reserve, not `grant.max_per_day`, is the binding limit [H]. A pilot of 50 members needs 50 x 3 = 150 credits of starter grant; FD§4.6 says the founders seed the Reserve by their own verified Commons work | no default change. Launch precondition [V]: Reserve seeded with at least 150 credits (= `grant.starter_credits` x pilot size) before `launch.members_may_join` is switched on; recorded as a G-gate evidence item (S14 owner). `S16D-C18` keeps the ceiling above one day of grants |
| `F-14` | major | Many approver counts default to 2 distinct people: `launch.min_signoffs`, `policy.loosen_min_approvers`, `ledger.reversal_min_approvers`, `appeal.ban_min_reviewers`, `template.min_reviewers_new`, and every action in `security.two_person_actions`. `C19` warns only for launch. With one admin no loosening, no ledger reversal, no ban and no new template can ever complete (`ISS-168`) | `S16D-C19` (warning, all counts together). Reason: one consistent check instead of one per count. Phase 1 needs at least 2 active admins before any switch is flipped |
| `F-15` | minor | `ui.draft.ttl_s` is "counted from the lease end" (16.C.2) but `S16C-C4` bounds it below by the whole lease path (1,920 s) counted from lease start; counted from the lease end only `lease.submit_grace_s` (120) is needed | no default change. State the baseline once: the draft lives from the last write on the device, not from the lease end; 3,600 s satisfies both readings (CR-22) |
| `F-16` | minor | Zero-margin pairs (`S16B-C1`, `C13`, `S16B-C7`, `S16C-C10`) and the lone-tightening pairs of 16.D.3 make a plain tightening fail with `VALIDATION_FAILED` and no hint | the refusal names the partner row and offers the batch (S15 owner) [A] |
| `F-17` | major | In the accelerated arm lots expire after 14 days. To hold the 276 credits of the FD§3.3 job (240 cells at 1.15) a member must earn 276 within one 14-day window: 276 / 14 = 19.7 cells a day, against the FD§3.2 habit of about 10 and the example's 8. K never binds in the arm (10 cells a day x 14 days = 140 < 350) | no default change. The pre-registered large-job trial (16.15) must take its jobs from the standard arm or from a funded grant; founders decide before the lock (FD§9) [H] |
| `F-18` | major | `ops.rpo_s` = 300 is a public promise (16.16) but the only mechanism cited is `ops.backup_interval_s` = 86,400 "together with log archiving"; no parameter bounds the archive interval, so nothing validates 300 s | no default change. S4 owner adds the archive interval or states that the promise is a target [V] (CR-16) |
| `F-19` | major | `template.autopause_report_count` = 5 reports in `template.autopause_window_s` = 3,600 s, while `report.max_per_member_per_day` = 20: one member could file 5 reports in an hour and pause a template alone, if reports are counted without distinct reporters | unit text becomes "distinct reporting members" (CR-15) [V S9.9.2] |
| `F-20` | major | `price.v_cap` = 0.50 caps the price at 1.55 per cell, but donors are paid 1 credit per executed cell of any kind (FD§4.3). If true overhead exceeds 0.50 the escrow cannot pay all verification cells and the ledger cannot create the difference (FD§4.2 invariant) | no default change [V]: S6 states that verification cells beyond the priced v are not run (or the job stops with partial settlement), never paid from the Reserve |
| `F-21` | minor | `inflation.mint_cap_cut_ratio` = 0.25 (range `0 < x <= 1`, `T↑`) does not say whether the new cap is cap x 0.25 or cap x 0.75; `T↑` only fits the second | the row states: new cap = floor(cap x (1 - ratio)) [A] (CR-09) |
| `F-22` | minor | S16 16.18 gives "FD§3.2 estimate [H]" as the basis of 4,000, 6,000 and 32,768. FD§3.2 holds only a time (about 2 minutes); FD§4.1 says the envelope numbers are measured in Phase 0, not guessed | the basis of the three size defaults is "[A] initial safe default without derivation, replaced by `CAL`" (CR-10) |

## 16.D.5 Duplicates and aliases, one canonical name each

No name is a canonical row in two of the three tables (checked: 16.B has 26 canonical rows, 16.C 30, S16 the rest of S0 0.10.6 plus its additions). Nine alias rows exist (1 in S16, 5 in 16.B, 3 in 16.C); an alias is never seeded and a write to it is refused as unknown (`AC-param-14`, `AC-paramc-01`). [D]

| Quantity | Names in use | Canonical | Status |
| --- | --- | --- | --- |
| forecast refresh | `admission.forecast_refresh_s`, `admission.reforecast_interval_s` | `admission.reforecast_interval_s` | alias confirmed (`ISS-162`) |
| device-link code lifetime | `identity.link_code_ttl_s`, `identity.device_link_code_ttl_s` | `identity.device_link_code_ttl_s` | alias confirmed (`ISS-16002`) |
| referral bonus | `growth.referral.bonus_credits`, the pair `growth.referral.bonus_referrer_credits` and `growth.referral.bonus_newcomer_credits` | the pair | alias confirmed; S15a must carry two amounts (`ISS-16003`) |
| backup retention | `retention.backup_days`, `ops.backup_retention_days` | `ops.backup_retention_days` | alias confirmed (`ISS-16005`) |
| purge sweep | `retention.sweep_interval_s`, `ops.purge_interval_s` | `ops.purge_interval_s` | alias kept [V]: S4 confirms one job. Public flag: `ops.purge_interval_s` is the latency of the deletion promise, so it joins `ops.rpo_s`, `ops.rto_s`, `ops.backup_retention_days` as public (CR-12) |
| admin step-up | `session.admin_stepup_s`, `session.step_up_max_age_s`, `session.admin_stepup_ttl_s` | the second and third are two different quantities (how long a completed step-up counts; how long an unused challenge may be answered); the first is an alias of the second | [V] unresolved: its source (S11 console file) is outside this cell's reading (`ISS-16004`, `ISS-16015`) |
| first-load budget | `ui.first_load_budget_bytes`, `ui.budget.first_load_bytes` | `ui.budget.first_load_bytes` (204,096, not the 204,800 printed in 10b and 11a) | alias confirmed (`ISS-16101`) |
| lease warning | `ui.lease_warning_ratio`, `ui.lease.warn_remaining_s` | `ui.lease.warn_remaining_s` | alias confirmed; range keeps 0 only as "warning off", which `F-23` below flags |
| waitlist quote lifetime | `admission.waitlist_claim_ttl_s`, `admission.waitlist_quote_ttl_s` | `admission.waitlist_quote_ttl_s`, calibration `OPS` | alias confirmed (`ISS-16103`) |
| two-person approval lifetime | a name in S10a, a name in S15b (`ISS-154`) and `launch.approval_window_s`, all 86,400 s | the S10a name is the generic canonical (first definer); the S15b name is its alias; `launch.approval_window_s` stays separate because the launch flow stores its own proposal (14.8.1) and must not exceed the generic value by default (both 86,400) | decided here (`ISS-16017`); the generic row is added by CR-13 [V S10, S14, S15b] |
| secret rotation age | a name in S14 (14:600) and `security.secret_rotation_days` | `security.secret_rotation_days` | decided here: the S14 name is an alias (both 90, `ISS-16018`) |
| calibration sample | 20 (S14 14:603) and 30 (`calibration.min_samples_per_service`) | 30, as S0 0.10.6 and S16 16.16 | decided: S14 text corrected (CR-20) |
| status wait and retry cap | `ui.status_poll_max_s`, `ui.retry.max_delay_s` (both 60) | both stay | confirmed separate (asked in `ISS-16105`): a poll repeats after success, a retry follows a failure; the equal default is a coincidence. `S16D-C22` orders the poll base below the poll cap |
| draft lifetime | `ui.draft.ttl_s` (device, seconds) and `job.draft_ttl_days` (server, days) | both stay | confirmed separate: different objects and units |
| appeal text | `ui.requester.appeal_note_max_chars`, `appeal.reason_max_chars` | the server limit is canonical; the UI cap is bounded by it | `S16D-C22`, `F-11` |

**Used but defined in no table** [V]: the four S10a names `identity.code_max_attempts`, `identity.registration_mode`, `invite.strikes_to_revoke_issuing`, `invite.tree_freeze_ban_threshold` (named as out of scope in 16.B.2 note 3) and the S14 and S15b names above; `ISS-16018` also lists `ui.*` names that 11d adds. `AC-param-01` makes each a failure of CI where code reads it. The value 5 of `identity.code_max_attempts` is implied by the 16.B.8 arithmetic (5 / 2^40) but is not confirmed here. The owner of S10.* supplies the rows; CR-13 lists them. `abuse.admin_lookup_rate` has no type, unit or default: until supplied it is treated like an alias, not seeded and refused on write, otherwise `AC-param-02` (every row satisfies its range) fails at seed time (CR-13). [A][V]

## 16.D.6 Defaults that conflict with an earlier part

Where two tables disagreed, the earlier source was read: the FD, then S0. [D]

| Item | Conflict | Resolution |
| --- | --- | --- |
| Mint cap derivation | S0: x (1 - 0.5); S16 and `ISS-166`: x phi; FD§4.8 and FD§4.2 give both bounds | `F-02`, CR-02: min(phi, 1 - phi); default 4,800 unchanged |
| eta label | S16 16.15: Reserve inflow versus spend; FD§4.3: 1/(1+v+lambda) | FD wins, `F-01`, CR-01 |
| Notice for `reservation.*` | S16 16.2.2 and 16.7: 14 days (`change.notice_days_price`); S16 16.13 and S0 Table A row: "for `price.*`, `admission.*`, `credit.*`" only | 16.2.2 and 16.7 stand; the rows add `reservation.*` (CR-07). `grant.*`, `reserve.*`, `mint.*`, `inflation.*` keep 7 days |
| `tighten_direction` | S0 0.10.3: enum `up`, `down`, `none`; S16 16.17.1: `lower`, `higher`, `toward:<value>`, `none`, and codes `T↓ T↑ T→x N C` | S16 stands (it needs enums and lists); S0 gains the same four values (CR-11) |
| `public` default | S0 0.10.3: true except `security.*`; S16 16.17.5 hides about 30 more rows; S10a says all its parameters are public (16.B.10) | S16 16.17.5 stands; S0 text refers to it; the 16.B and 16.C proposals are folded (CR-12) |
| Owner of exception rows | S0 0.10.5: area `policy`, `screen`, `service`, `template` are `reviewer`; S16 16.12 makes 12 rows `operator`; `abuse` has no area row (`ISS-16014`) | S16 16.12 stands; S0 0.10.5 regenerated at assembly with the exceptions and the `abuse` area (CR-11) |
| Envelope basis | S16 16.18: FD§3.2 estimate for 4,000, 6,000, 32,768 | FD§4.1: measured in Phase 0; `F-22`, CR-10 |
| `ui.first_load_budget_bytes` range | 10,240..5,242,880 (10b) against 20,000..5,000,000 (11a) | 16.C picked 5,000,000 as the upper bound; confirmed |
| `identity.challenge_ttl_s` | 60 (S10a) against 120 (S15a) | 60; S15a text corrected at assembly (`ISS-16001`) |
| `lease.max_job_share_ratio` public flag | 16.C hides it; 16.17.5 does not list it | add to the hidden list (CR-12) |
| Anti-farming rows with mixed flags | hidden: `grant.max_per_device`, `ratelimit.*new_members_per_day`, `growth.referral.max_per_referrer_per_30d`; public: `grant.max_per_invite_tree_per_day`, `grant.max_per_day`, `invite.tree_max_members`, `invite.tree_max_depth` | recommendation [A]: hide `grant.max_per_invite_tree_per_day`, `growth.referral.max_per_day`, `growth.referral.max_per_invite_tree_per_30d` (`ISS-16011`); leave `invite.max_active_per_member` and `invite.ttl_days` public because a member needs them; owner decision under `SEC` |
| `F-23` | `ui.lease.warn_remaining_s` may be 0, which switches off the warning that carries the extension offer (`ISS-16102`) | range `1 .. lease.timeout_s` (CR-14b); default 300 unchanged. Reason: the warning protects a volunteer's paste-back |

## 16.D.7 Cross-check against FD§4.9

The FD§4.9 table was read line by line for this cell (it has 10 rows: cell envelope, E, K, v, lambda, g and s, phi, G, mint cap, lease timeout). Each row maps to one canonical name, or to one group where the FD row is itself a group. [D]

| FD§4.9 row | FD initial value | Canonical name(s) | Check |
| --- | --- | --- | --- |
| Cell envelope: max input and output size | TBD from Phase 0 | the group `cell.envelope.*`; the FD sizes are `cell.envelope.max_input_chars` and `cell.envelope.max_output_chars`; `max_submission_bytes`, `expected_time_s`, `max_json_depth`, `max_model_label_chars` are additions, and `cell.max_attempts` is outside the group on purpose | one group prefix, no second; defaults 4,000 and 6,000 have no FD derivation (`F-22`) |
| E | 60 days; 14-day arm | `credit.lifetime_days`; the arm value `credit.lifetime_days_accelerated` is not a second E | 60 and 14 match FD§4.5; arm relations `F-03`, `F-17` |
| K | TBD from a typical large job | `credit.member_cap_credits` | 350 = round to 50 of 1.25 x 240 x 1.15 = 345 matches FD§3.3; tier scaling by `trust.cap_multiplier.*` is an addition (FD§6.1); `F-04` |
| v | measured in Phase 1 | measured value published as a `MetricSnapshot`; prior `price.v_prior`; estimator rows `price.v_window_days`, `price.v_min_sample_cells`; safety cap `price.v_cap` | the FD has no cap on v; `price.v_cap` is an addition with a conservation question (`F-20`) |
| lambda | TBD; 0.05 in the example | `price.levy_lambda` | 0.05; FD§3.3 settlement 12 = 0.05 x 240 recomputes |
| g, s | TBD; adaptive with a floor | `verify.gold_rate_g` and `verify.audit_rate_s`, each with `_floor` and `_max` | FD§4.4 floor needs both floors positive (`F-09`) |
| phi | TBD; 0.5 in the example | `admission.phi` (modifiers `admission.forecast_haircut`, `admission.horizon_discount_per_day`) | 0.5; FD§3.3: 40 x 8 x 2 x 0.5 = 320 >= 264 recomputes |
| G | a few cells; TBD | `grant.starter_credits` (lifetime in `grant.starter_lifetime_days`) | 3 credits buy floor(3 / 1.15) = 2 cells alone; with the 1 credit of the verified first cell (FD§4.6), floor(4 / 1.15) = 3 cells, so "a few cells" holds only after that first credit |
| Mint cap | TBD from measured throughput | `mint.monthly_cap_credits` (one canonical name; `mint.per_member_daily_cap_credits` is an addition, not an FD row) | 4,800 = 40 x 8 x 30 x 0.5 recomputes; `F-02` |
| Lease timeout | TBD from measured time per cell | `lease.timeout_s` (`lease.extend_s`, `lease.submit_grace_s` are additions) | 1,200 = 10 x 120 |

Two rows of S16 16.18 are not in FD§4.9: the Reserve ceiling (`reserve.ceiling_credits`, from FD§4.2: "a published ceiling") and the daily per-member mint cap; the table should say so (CR-10). Parameters that the FD body requires and FD§4.9 omits all have a canonical row: eta threshold (`price.eta_alarm_threshold`, FD§4.3), claim ratio threshold (`inflation.claim_ratio_threshold_weeks`) and mint-cap utilization (`inflation.mint_utilization_alarm`, FD§4.7), per-device, per-invite-tree and per-day grant limits (`grant.max_per_device`, `grant.max_per_invite_tree_per_day`, `grant.max_per_day`, FD§4.6), concurrent jobs (`admission.max_concurrent_jobs_per_member`, FD§4.8), deadline multiplier (`admission.deadline_multiplier_standard`, FD§4.8). No FD parameter maps to two canonical names. [D]

## 16.D.8 Safety-critical defaults

### 16.D.8.1 Defaults that are a safety-critical fail-closed value [D]

The default is the closed or strict end; the system is safe if nobody ever edits the row. A change in the open direction is impossible (constant), gate-only (`launch.*`) or a loosening (notice and a second operator, S16 16.2.3). [D]

| Class | Rows and default |
| --- | --- |
| Switches closed until sign-off | `launch.members_may_join` false; `launch.member_jobs_enabled` false; `launch.minting_enabled` false; `launch.required_gate_ids` `["G0","G1"]`; `launch.min_signoffs` 2; `launch.min_approved_services` 1. Kill switches default `released` and feature flags default off are not parameters (S0 0.10.6) |
| Constants (not editable) | `mint.requires_launch_gate` true; `ledger.allow_negative_balance` false; `ledger.reversal_min_approvers` 2; `grant.non_transferable` true; `verify.model_judge_mints_credit` false; `verify.third_exec_on_mismatch` true; `retention.raw_ip_stored` false; `analytics.third_party_trackers` false; `analytics.cookies_enabled` false; `policy.tighten_immediate` true; `policy.recheck_on_accept` true; `optin.sensitive_topics_default` false; `security.rotate_before_public_exposure` true; `ui.card.expand_required_first_use` true; `price.v_rounding` `ceil`; `mint.cap_period` `utc_month` |
| Credit creation and spend | `grant.reserve_floor_credits` 0 (grants pause, never overdraw); `grant.required_verified_cells` 1; `grant.max_per_device` 1; `admission.phi` 0.50 (below 1, `C1`); `mint.monthly_cap_credits` 4,800 behind the launch gate; `reserve.ceiling_credits` 1,000; `credit.member_cap_credits` 350 |
| Verification | `verify.audit_rate_floor` 0.02 and `verify.gold_rate_floor` 0.01 (must stay above 0, `S16D-C2`); `verify.blanket_redundancy_n` 3; `verify.new_donor_blanket_cells` 5; `trust.cap_multiplier.restricted` 0.25 |
| Content screening and policy | `screen.pii_action` `reject`; `screen.output_url_action`, `screen.output_code_action`, `screen.output_request_action` `quarantine`; `screen.max_urls_per_input` 0; `screen.output_max_urls` 0; `screen.invisible_char_max` 0; `screen.review_rate_new_requester` 1.0; `optin.default_purposes` `["P0","P1"]`; `optin.default_sensitivities` `["S0","S1"]`; `policy.loosen_min_approvers` 2; `policy.loosen_min_notice_days` 7 |
| Privacy and exposure | `analytics.min_cohort_k` 10; `team.min_public_members` (5 now, 10 after `F-10`); `public.location_display` `never`; `public.ledger_lag_s` 300; `ledger.member_timestamp_granularity_s` 86,400 (the coarsest value); `lease.max_job_share_ratio` 0.34; `identity.recovery_key_bits` 128; `identity.recovery_cooldown_s` 86,400 |
| Access and approval | `security.two_person_actions` (four actions, must keep `parameter.loosen`); `session.admin_idle_ttl_s` 1,800; `session.admin_abs_ttl_s` 28,800; `ratelimit.recovery_attempts_per_day` 5 |

### 16.D.8.2 Parameters that are not safe to loosen without notice [D]

Every loosening already takes notice (`change.notice_days_default` 7, `change.notice_days_price` 14) and a second operator; the rows below are those where the harm of an unannounced loosening cannot be undone or cannot be seen by a member before it happens, so the notice must not be shortened, waived or set to 0 (`F-07`, `S16D-C9`) and the change-log entry states the reason. [D][A]

| Group | Loosening direction | Why it cannot wait or be reversed |
| --- | --- | --- |
| `mint.monthly_cap_credits`, `credit.member_cap_credits`, `trust.cap_multiplier.*` | raise | credit created or held cannot be uncreated except by Reserve retirement (FD§4.2); claims exceed capacity (FD§4.7) |
| `admission.phi`, `reservation.capacity_share_cap`, `admission.max_job_cells` | raise | admitted jobs and held reservations are promises that cannot be withdrawn |
| `reserve.ceiling_credits` | either way | retirement is irreversible; the group is `N` |
| `price.*`, `credit.lifetime_days*`, `admission.*`, `reservation.*` | any | changes what members hold or pay; 14 days |
| `verify.*_floor`, `verify.audit_rate_s`, `verify.gold_rate_g`, `trust.*_min_*`, `verify.blanket_redundancy_n` | lower | weakens fraud controls; abuse during the gap is not recoverable |
| `analytics.min_cohort_k`, `team.min_public_members`, `public.ledger_lag_s`, `public.location_display`, `job.manifest_time_granularity_s`, `ledger.member_timestamp_granularity_s`, `identity.recovery_*` | lower or open | a disclosure cannot be taken back; a `SEC` reason is recorded |
| `retention.*` | raise | data is kept longer; applies to new rows only |
| `session.*_ttl_s`, `security.two_person_actions`, `security.secret_rotation_days` | longer or smaller set | a hijacked session or secret lives longer |
| `screen.*`, `policy.*`, `service.*`, `optin.default_*`, `template.min_reviewers_*` | loosen | content or terms exposure; 7 days minimum |
| `launch.*` | switch on | gate sign-off only; never a plain edit |

## 16.D.9 Acceptance criteria

| Id | Given | When | Then |
| --- | --- | --- | --- |
| `AC-paramd-01` | the seeded defaults | the seed check runs | every relation of 16.D.2 and 16.D.3 holds, except the two listed failures (`S16D-C3` in the arm, `S16D-C21` until CR-08), which return warnings |
| `AC-paramd-02` | `price.eta_alarm_threshold` = 0.90 with the defaults | the write is made | it is refused naming `S16D-C1` (0.90 > 0.8696) |
| `AC-paramd-03` | `retention.ip_hash_ttl_days` = 0 | the write is made | refused naming `S16D-C13`; nothing is changed |
| `AC-paramd-04` | `change.notice_days_default` = 0 | the write is made | refused naming `S16D-C9` |
| `AC-paramd-05` | `admission.min_window_s` = 0 | the write is made | refused naming `S16D-C5` |
| `AC-paramd-06` | `retention.session_days` lowered to 60 alone | the write is made | refused naming `S16B-C1` with the batch hint (`F-16`); as a batch with both session limits it is accepted as `tighten` |
| `AC-paramd-07` | `team.min_public_members` = 5 | the write is made | accepted with the warning `S16D-C21`, recorded in the log entry |
| `AC-paramd-08` | one active admin | any of the approver counts in `S16D-C19` is 2 | the warning is returned and recorded; no loosening completes |
| `AC-paramd-09` | a name from 16.D.5 marked alias, or `abuse.admin_lookup_rate` | it is seeded or written | not created and refused as unknown (`AC-param-14`) |
| `AC-paramd-10` | `security.two_person_actions` without `parameter.loosen` | the write is made | refused naming `S16D-C20` |

## 16.D.10 Hypotheses, verifications, assumptions

**Hypotheses [H]**: the Reserve, not `grant.max_per_day`, is the binding limit on starter grants at the FD§3.3 inputs (`F-13`); accelerated-arm members cannot fund a 240-cell job from earned credit alone (`F-17`); two weeks of margin is enough between `price.v_window_days` and `retention.event_raw_days` (2 days of margin today).

**Verifications [V]** (what, by whom, where stored): whether escrowed credit keeps ageing (S6 owner, S6.* text, `S16D-C3`); the meaning of redeemable capacity (S6 owner, `F-02`); what happens when verification need exceeds the priced v (S6 owner, `F-20`); archive interval behind `ops.rpo_s` (S4 owner, `F-18`); distinct reporters in the template autopause (S9 owner, `F-19`); data sources of the v and throughput windows (S13 and S6, `S16D-C14`); one job behind `ops.purge_interval_s` and the S10 retention sweep (S4 owner); the S11 console passages for `abuse.admin_lookup_rate` and `session.admin_stepup_s` (owner of S11, `ISS-16015`); the S10a, S14 and S15b names of 16.D.5.

**Assumptions [A]** (with the decision that could overturn each): the corrected default `team.min_public_members` = 10 (a `SEC` decision may exempt team totals); min(phi, 1 - phi) as the mint bound; the canonical choices of 16.D.5 where the two names have one value; ranges `1..90` for notice and `1..` for the IP-hash TTL; recommendations on the public flags.

**What this part cannot promise** [D]: every default stays a starting value until its measurement exists; passing every relation shows that the table is consistent, not that any value is safe for real members, legal anywhere or enough for a pilot of 30 to 50 members (FD§9).

## Corrections required

Exact edits to other files, none made by this cell. `S` = `spec/00-conventions.md`, `P` = `spec/16-parameters.md`, `B` = `spec/16b-parameters-a.md`, `C` = `spec/16c-parameters-b.md`. Each is minimal and renames nothing. [D]

| No | File and place | Exact change | Finding |
| --- | --- | --- | --- |
| CR-01 | P 16.15, row 1, first cell | replace `Minimum eta (Reserve inflow versus spend)` by `Minimum round-trip efficiency eta = 1/(1+v+lambda), cells requested per cell contributed` | `F-01` |
| CR-02 | P 16.3 `C13`; P 16.5 row `mint.monthly_cap_credits`; S Table A same row | `C13`: replace the factor phi by min(phi, 1 - phi) (as integer ppm: min(phi_ppm, 1,000,000 - phi_ppm)). Rows: replace `x (1 - 0.5)` and `x phi 0.5` by `x 0.5, where 0.5 = min(phi, 1 - phi)`; default 4,800 unchanged. P 16.7 closing note on `ISS-166` and 16.18 follow | `F-02` |
| CR-03 | P 16.7 `admission.min_window_s` and `admission.window_step_s`; S Table A | validation of the min window becomes `admission.window_step_s .. admission.max_window_days x 86400; C7, C9, S16D-C5`; of the step `1..86,400, divides 86,400; C9` | `F-05` |
| CR-04 | P 16.11 `retention.ip_hash_ttl_days`; S Table B | validation `0..30` becomes `1..30; S16D-C13` | `F-06` |
| CR-05 | P 16.3 `C2`; S 0.10.3 `C2` | append `; verify.gold_rate_floor > 0` | `F-09` |
| CR-06 | P 16.13 and S Table A rows `change.notice_days_default`, `change.notice_days_price` | validation `0..90` becomes `1..90` (price: `>= change.notice_days_default`; `S16D-C9`) | `F-07` |
| CR-07 | P 16.13 and S Table A row `change.notice_days_price` | `(for price.*, admission.*, credit.*)` becomes `(for price.*, credit.*, admission.*, reservation.*)` | 16.D.6 |
| CR-08 | P 16.14 and S Table C row `team.min_public_members` | default 5 becomes 10 (= `analytics.min_cohort_k`) with `S16D-C21`; the pilot report states that few teams reach it | `F-10` |
| CR-09 | P 16.5 and S Table A row `inflation.mint_cap_cut_ratio` | default cell appends `; the cap after the cut = floor(cap x (1 - ratio))` | `F-21` |
| CR-10 | P 16.18 | the basis of the three size defaults reads `[A] initial safe default, no derivation (FD§4.1: measured in Phase 0), replaced by CAL`; the Reserve ceiling and `mint.per_member_daily_cap_credits` are marked as not FD§4.9 rows; last paragraph states that FD§4.9 was re-read (this file) | `F-22`, 16.D.7 |
| CR-11 | S 0.10.3 and 0.10.5 | `tighten_direction` enum becomes `up`, `down`, `toward:<value>`, `none`; `public` default text becomes `true except the rows listed in S16 16.17.5`; 0.10.5 lists the operator exceptions of S16 16.12 and the area `abuse` (owner `operator`) | 16.D.6 |
| CR-12 | P 16.16 and 16.17.5 | public exceptions: add `ops.purge_interval_s`; hidden list: add `lease.max_job_share_ratio`, `growth.referral.max_per_day`, `growth.referral.max_per_invite_tree_per_30d`; recommended: `grant.max_per_invite_tree_per_day` | 16.D.6 |
| CR-13 | B (new rows, owner of S10 and S14 to supply values) | add rows for the generic two-person approval lifetime (S10a name; type duration_s, range 600..604,800 as 16.B.6, default 86,400, `T↓`, `SEC`; the S15b name an alias), `identity.code_max_attempts`, `identity.registration_mode`, `invite.strikes_to_revoke_issuing`, `invite.tree_freeze_ban_threshold`; `abuse.admin_lookup_rate` marked not seeded until type, unit and default are given | 16.D.5 |
| CR-14 | C 16.C.3 `ui.requester.appeal_note_max_chars`; C 16.C.2 `ui.lease.warn_remaining_s` | the note range `0..5,000` becomes `100 .. appeal.reason_max_chars` (field name [V]); the warning range becomes `1 .. lease.timeout_s`, so it cannot be switched off | `F-11`, `F-23` |
| CR-15 | P 16.12 `template.autopause_report_count` | `5 reports` becomes `5 reports from distinct reporting members` [V S9.9.2] | `F-19` |
| CR-16 | P 16.16 `ops.rpo_s` | add `[V]: no parameter bounds the log-archive interval; the S4 owner adds one or states 300 s as a target` | `F-18` |
| CR-17 | P 16.8 `verify.duplicate_min_chars` | validation appends `; >= verify.duplicate_shingle_chars` (`S16D-C11`) | `F-08` |
| CR-18 | P 16.3 | the list of 16.3 gains `S16D-C1`..`S16D-C24` of 16.D.3 and its worked check; `AC-param-02` counts them | 16.D.3 |
| CR-19 | P 16.3 intro and 16.17.2 | a relation that mentions `credit.lifetime_days` is evaluated twice, with `credit.lifetime_days` and with `credit.lifetime_days_accelerated`, while `ff.experiment.expiry_arm` is on | `F-03` |
| CR-20 | S14 text at 14:603 and 14:600 (owner of S14) | `calibration.min_samples_per_service` 20 becomes 30; the S14 secret-rotation name becomes `security.secret_rotation_days` | 16.D.5 |
| CR-21 | P 16.6 `price.eta_alarm_threshold` | validation `0..1` becomes `> 0 .. 1; S16D-C1` | `F-01` |
| CR-22 | C 16.C.2 `ui.draft.ttl_s` | append: `the draft lives from its last write on the device; 3,600 s satisfies S16C-C4 on either reading` | `F-15` |
| CR-23 | P 16.16 `security.two_person_actions` | validation appends `; always contains parameter.loosen (S16D-C20)` | `S16D-C20` |
| CR-24 | P 16.3 | `S16D-C3` is recorded as a warning until S6 confirms whether escrowed credit keeps its lot expiry; if it does, `reservation.max_horizon_days` and the arm are an owner decision before the `PreRegistration` lock | `F-03` |
