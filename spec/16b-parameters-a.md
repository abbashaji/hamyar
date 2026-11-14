# 16.B Parameter additions (growth identity invite session retention report abuse launch team appeal)

*Spec part 16, file 16b (audit and reconcile; cell C-034) · extends `spec/16-parameters.md` (S16) and `spec/00-conventions.md` (S0) without renaming any parameter. Written against Founding Document draft v0.1 (FD) and the spec files on main when it was written (S10a, S10b, S11a, S12, S14, S15a, S15b, S18). Nothing here is legal advice and nothing has been verified against any provider's terms or any law.*

## 16.B.1 Scope, sources and rules

The 31 names below are used in other parts and are defined in neither S0 0.10.6 nor S16. This file defines 26 of them as canonical rows (16.B.2 to 16.B.6) and 5 as alias rows (16.B.7). No name is renamed; where two parts use two names for one thing, the name that is already seeded or defined in S0 or S16 is canonical and the other is an alias that is not seeded (the pattern of `admission.forecast_refresh_s`, `ISS-162`, `AC-param-14`). [D]

| Rule | Decision |
| --- | --- |
| RB-1 Rules | Every rule of S16 applies unchanged: R16-1 to R16-5, the change-policy codes of 16.2.2, the owner roles of 16.2.3, the write pipeline of 16.17.2 and the seeding rule of 16.17.6. This file adds rows and constraints, not rules. [D] |
| RB-2 Defaults | Every default is an `initial configurable default`, stored in `ParameterVersion` 1. A formula is shown where one exists; where the source part gives a value without a derivation, the row says so and the calibration column names what replaces it (R16-3). No default here is a finding. [D] |
| RB-3 Safety limits | A default that limits abuse, exposure or spend is a safety limit; 16.B.8 says why each such value is safe and what would make it unsafe. [D] |
| RB-4 Constraint ids | New cross-parameter constraints are `S16B-C1`..`S16B-C9` (16.B.9), written like `S9-C1` so they cannot collide with `C13`..`C20` of 16.3 or with the `C9` that S10a used for a different rule (`ISS-16007`). [D] |
| RB-5 What was read | For each name the passage cited by the cell was read with about 15 lines around it, and S0 0.10.1 to 0.10.5, Tables A and B and most of Table C of S0 0.10.6, and all of S16 were read. The part S11 console file that holds `11c:67`, `11c:126` and `11c:729` could not be opened: its file name is not given in the cell, in S0 0.13 or in the sibling parts, and every guessed path returned NOT_FOUND. The two rows that rest on it are marked [V] and recorded as `ISS-16015`. [A][V] |
| RB-6 Folding | Like every convention addition (`ISS-169`), these rows are folded into S0 0.10.6 and S16 by C-001 at assembly; until then this file is part of the table, so `AC-param-01` and `AC-param-15` apply to its names. [A] |

### 16.B.1.1 Columns

| Column | Meaning |
| --- | --- |
| `name` | Primary key of `Parameter` (S0 0.10.3), regex of S0 0.10.1 |
| `type` / `unit` | S0 0.10.2 type, and what one unit of the value counts (the S0 0.10.1 suffix where one exists) |
| `validation` | Range, enum and constraint ids, evaluated on write; a violation is `VALIDATION_FAILED` |
| `initial configurable default` | The value of `ParameterVersion` 1 |
| `owner role` | The role that edits, from the area table of S0 0.10.5 and 16.2.3 |
| `change policy` | The code of 16.2.2: `T↓` tighten-immediately when lowered, loosen-with-notice when raised; `T↑` the mirror; `N` always with notice (`change.notice_days_default` = 7). A loosening also needs a second `operator` (16.2.3) |
| `prospective-only` | `yes` with the object or run that keeps the value it was created under, or the stated exception. Every mutable parameter is prospective (S0 0.10.3) |
| `calibration` | Measurement code of S0 0.10.4 and the Phase 0 or Phase 1 measurement that replaces the default |
| `used in` | Part and line of the passage that reads it, as given by the cell; `10a:744` style lines for the 10.18.3 table rows are counted from the cited neighbours (`10a:743`, `10a:746`, `10a:754`, `10a:757`) |

## 16.B.2 Identity and invite

Owner `operator` (S0 0.10.5). Binding: a challenge and a code store their own expiry when they are issued, so a changed TTL applies to the next one; the invite settings are read at the event they govern. [D]

| name | type | unit | validation | initial configurable default | owner role | change policy | prospective-only | calibration | used in |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `identity.challenge_ttl_s` | duration_s | seconds a single-use auth challenge stays valid | 10..600 | 60 (S10a value; S15a lists 120, `ISS-16001`) | operator | `T↓` | yes: each challenge stores `expires_at` | `SEC`; then the signing round trip on real phones and links measured in `TEC` [H] | 10a:69, 10a:743; 15a:100-116, 15a:860 |
| `identity.email_code_ttl_s` | duration_s | seconds an e-mail verification code stays valid | 60..3600 | 900 (15 minutes, S10a) | operator | `T↓` | yes: the code row stores its expiry | `SEC` | 10a:149, 10a:746 |
| `identity.max_devices_per_member` | int | active or retiring device keys per member | 1..20; `S16B-C2` | 5 (S10a) | operator | `T↓` | yes: lowering never revokes an existing key, it only blocks new links [A] | `OPS`: Phase 1 devices per member and farming flags | 10a:182, 10a:218, 10a:744 |
| `invite.accountability_days` | days | days after `Member.created_at` until `invited_by_member_id` is cleared | 1..365 | 90 (S10a, no derivation) | operator | `T↓` | yes, except that lowering also applies to existing edges at the next sweep, as lowering `retention.*` does (16.11) [A] | `SEC`: the G1 decision on the social-graph risk | 10a:335, 10a:563, 10a:749 |
| `invite.strike_window_days` | days | days (strike counting window, issuing suspension, tree-freeze counting window: three roles, `ISS-16009`) | 1..365 | 90 (S10a, no derivation) | operator | `T↑` | yes: a suspension stores its end when imposed; counts are evaluated with the value in force at the time [A] | `OPS`: strikes and freezes in the Phase 1 abuse queue | 10a:342, 10a:343, 10a:750 |

Notes [D][A]: (1) `identity.max_devices_per_member` counts `MemberKey` rows of kind device in state `active` or `retiring` (10a:182), not `Device` rows. (2) A strike is recorded only while the invite edge exists, so a descendant banned more than `invite.accountability_days` after joining gives the inviter no strike; the effective strike look-back per descendant is `invite.accountability_days`, whatever `invite.strike_window_days` is. (3) `invite.strikes_to_revoke_issuing`, `invite.tree_freeze_ban_threshold`, `identity.code_max_attempts` and `identity.registration_mode` sit in the same S10a table and are outside this cell's list; they are for the cell that owns that completion.

## 16.B.3 Session

Owner `operator`. Binding: a session stores its own expiry when created; `session.step_up_max_age_s` and `session.touch_min_interval_s` are read on each request and rewrite nothing stored. [D]

| name | type | unit | validation | initial configurable default | owner role | change policy | prospective-only | calibration | used in |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `session.step_up_max_age_s` | duration_s | seconds a step-up (fresh device signature, or WebAuthn assertion for an admin) stays valid | 30..3600 | 300 (S10a; one value for member X5 and admin X8) | operator | `T↓` | yes: read at each check, nothing stored is rewritten | `SEC` | 10a:439, 10a:442, 10a:753 |
| `session.touch_min_interval_s` | duration_s | minimum seconds between two writes of `Session.last_used_at` | 10..86400; `S16B-C3` | 300 (S10a; equal to `session.step_up_max_age_s`) | operator | `N` (a longer interval saves writes and makes idle expiry coarser; neither is the safer end) | yes: read at the next touch | `OPS`: write load of the session table | 10a:516, 10a:754 |
| `session.max_active_per_member` | int | live sessions per member | 1..100; `S16B-C2` | 10 (S15a convention gap) | operator | `T↓` | yes: enforced when the next session is created, nothing is revoked at once; the oldest idle session is the one revoked | `OPS`: sessions per member seen in Phase 1 | 15a:108, 15a:860 |
| `session.admin_stepup_ttl_s` | duration_s | seconds an admin WebAuthn challenge (login or step-up) stays valid | 10..600 | 300 (S15b `ISS-154`) | operator | `T↓` | yes: each admin challenge stores `expires_at` | `SEC` | 15b:87, 15b:1101 |

Notes [D][A]: (1) `session.step_up_max_age_s` and `session.admin_stepup_ttl_s` are two different quantities that both default to 300: the first is how long a completed step-up counts, the second is how long an unused challenge may be answered; `identity.challenge_ttl_s` is the member counterpart of the second and is shorter (60) because a member's device signs without a human step (`ISS-16004`). (2) Under S10a a key has one active session and a member has at most `identity.max_devices_per_member` active or retiring keys, so more than 5 live sessions cannot occur at the defaults; 10 is a backstop for faulty clients and never refuses a login (`ISS-16008`). (3) `session.touch_min_interval_s` must stay below both idle TTLs, otherwise an active session could expire between two writes (`S16B-C3`).

## 16.B.4 Growth (referral) and team

Owner `operator`, except `growth.referral.reserve_draw_cap_ratio`, which is a Reserve budget threshold decided by `FND` and so owned by `founders` (S0 0.10.5, S12 12.12.6). Binding (16.14): the amounts and windows of a referral are stamped on it; the caps and the draw ratio are read at each payout sweep, so a tightening holds back referrals that are still waiting and never touches one that was paid [A]. The rolling 30 days in two names is a constant of the name, not a parameter: 30 x 86,400 s. [D]

| name | type | unit | validation | initial configurable default | owner role | change policy | prospective-only | calibration | used in |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `growth.referral.max_per_day` | int | referral pairs paid per UTC day | 0..1000; `S16B-C8` | 5 (S12; no derivation) | operator | `T↓` | yes: read at each sweep | `OPS`: farming flags and Reserve inflow in Phase 1 | 12:411, 12:661 |
| `growth.referral.max_per_invite_tree_per_30d` | int | paid or qualified referrals per invite tree in a rolling 30 days | 0..1000; `S16B-C7` | 5 (S12; no derivation) | operator | `T↓` | yes: read at creation and at each sweep | `OPS`: farming flags | 12:410, 12:662 |
| `growth.referral.reserve_draw_cap_ratio` | ratio | share of the Reserve balance at the start of the UTC day that referral bonuses may draw | 0 < x <= 1; `S16B-C8` | 0.10 (S12) | founders | `T↓` | yes: read at each sweep | `FND`, then `P1M`: starter-grant demand against Reserve inflow | 12:411, 12:614, 12:663 |
| `growth.referral.qualify_window_days` | days | days | 1..365; `S16B-C5` | 30 (S12 [H]; no derivation) | operator | `T↓` | yes: stamped on the referral at acceptance | `P1M`: distribution of days from joining to the first verified cell | 12:664, 12:758 |
| `growth.referral.clawback_window_days` | days | days after `Referral.paid_at` | 0..365; `S16B-C6` | 30 (S12) | operator | `T↑` (0 switches clawback off and is the loosest value) | yes: stamped on the referral at payment | `OPS`: delay between acceptance and a later overturn | 12:415, 12:665 |
| `team.label_max_chars` | int | chars of `Team.name`, and of `Team.group_label` when it exists [A] | 10..200; `S16B-C4` | 40 (S12) | operator | `T↓` | yes: applies to names and labels saved after the change; existing ones stay until edited [A] | `OPS`: lengths of real team names | 12:331, 12:667 |

Notes [D][A]: (1) `growth.referral.qualify_window_days` runs two clocks, joined to qualified and qualified to paid (12.10.2); one value serves both and `S16B-C5` keeps `growth.referral.hold_s` (86,400 s) far below it (`ISS-16010`). (2) The worst-case Reserve draw per UTC day is `growth.referral.max_per_day x (growth.referral.bonus_referrer_credits + growth.referral.bonus_newcomer_credits)` = 5 x 2 = 10 credits at the defaults, and never more than `growth.referral.reserve_draw_cap_ratio` of the start-of-day balance (12.10.3). (3) A bonus lot expires after `credit.lifetime_days` (`AC-referral-01`); a clawback recovers only the unspent remainder of that lot, so for a member in the accelerated-expiry arm (`credit.lifetime_days_accelerated` = 14) the effective clawback period is the shorter of the two.

## 16.B.5 Report, appeal and abuse

Owner `reviewer` for `report.*` and `appeal.*` (S0 0.10.5, 10b parameter table); `abuse` is an area that S0 0.10.5 does not list, given owner `operator` here [A] (`ISS-16014`). Binding: read when the filing, the sampling job, the publication job or the SLA clock runs; nothing is stamped on a `Report` or an `Appeal`. [D]

| name | type | unit | validation | initial configurable default | owner role | change policy | prospective-only | calibration | used in |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `report.max_text_chars` | int | chars of a report's free text | 100..10000; `S16B-C4` | 1000 (S10b) | reviewer | `N` (a lower cap can silence a safety report, a higher one stores more personal text) | yes: applies to filings after the change | `OPS`: lengths of real reports | 10b:503, 10b:641 |
| `report.decision_sample_rate` | ratio | share of closed reports given a second look by a reviewer who did not decide them | 0..1 (`ISS-16020`) | 0.10 (S10b `initial configurable default`, no derivation) | reviewer | `T↑` | yes: applies to reports closed after `effective_from` [A] | `OPS`: reversal rate found by the second look; at pilot volume a ratio may select no report at all [H] | 10b:594, 10b:642 |
| `report.transparency_publish_days` | days | days between two publications of aggregate counts of reports, actions, appeals and outcomes | 1..365 | 30 (S10b); publication may be delayed on counsel's advice [V] | reviewer | `T↓` | yes: read when the publication job runs | `FND`: founders' decision before day 1 | 10b:598, 10b:643 |
| `report.urgent_triage_sla_s` | duration_s | seconds from `filed_at` to `triaged_at` for urgent categories (`safety_of_person`, `injection_attempt`, `suspected_sensitive_data`, `legal_notice`) | 600..86400; `S16B-C9` | 14,400 (4 hours, S10b; a declared target, not a promise) | reviewer | `T↓` | yes: read when the SLA clock is evaluated; after a tightening an open report may become overdue, which raises the alarm only | `OPS`: time to triage seen in Phase 1 | 10b:510, 10b:640 |
| `appeal.reason_max_chars` | int | chars of the reason a member types when filing an appeal | 100..10000; `S16B-C4` | 1000 (S11a) | reviewer | `N` (a member's right to be heard has no safe lower end) | yes: applies to filings after the change | `OPS`: lengths of real appeals | 11a:203, 11a:1384 |
| `abuse.admin_lookup_rate` | int [V] | [V] lookups per admin per time unit; the name does not fix the unit | [V] | none stated: no value is invented here; the passage `11c:729` was not read (`ISS-16015`) | operator [A] | `T↓` [A] (fewer admin lookups of member data is the tightening) | yes [A] | `OPS` [A]: lookups per admin seen in Phase 1 | 11c:729 |

Notes [D][A]: (1) `report.urgent_triage_sla_s` is the second SLA of 10.16.3; the first is `report.triage_sla_days` (3 days, S16 16.12), and `S16B-C9` keeps the urgent one shorter. (2) Aggregate counts published every `report.transparency_publish_days` are subject to the small-cohort suppression of `analytics.min_cohort_k` (S10b item 11), so at a pilot of 30 to 50 members most counts will be suppressed; that is the intended trade [A][H]. (3) The three `_chars` limits count characters by one rule that no part states yet (`ISS-16013`).

## 16.B.6 Launch

Owner `operator`; an edit of any `launch.*` row needs `launch.min_signoffs` distinct admins (16.2.3). Binding: a validity row is read once, when an item is signed off, and `valid_until` is then fixed (14.6.3); a proposal stores the window it was proposed under (14.8.1). The validity formulas are in 14.6.3: generic `signed_off_at + launch.generic_validity_days x 86,400`; counsel and measurement likewise with their own parameter; terms-bound items take `min(generic, terms_copy.captured_at + service.review_max_age_days x 86,400)`, which at the defaults is 90 days, so `launch.generic_validity_days` does not bind a service item while `service.review_max_age_days` stays at 90. [D]

| name | type | unit | validation | initial configurable default | owner role | change policy | prospective-only | calibration | used in |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `launch.approval_window_s` | duration_s | seconds the second admin has to approve a proposed launch switch | 600..604800 [A: the range of `security.two_person_ttl_s`] | 86,400 (S14) | operator | `T↓` | yes: each proposal stores its `expires_at` when proposed [A] | `OPS`: time between proposal and approval seen in the pre-launch drill | 14:595; 14.8.1 step 2 |
| `launch.counsel_validity_days` | days | days a counsel-bound gate sign-off stays valid | 1..3650 [A] | 365 (S14; no derivation) | operator | `T↓` | yes: `valid_until` is fixed at sign-off | `CNS`: the review period counsel states in the memo [V] | 14:422, 14:597 |
| `launch.generic_validity_days` | days | days a sign-off with no more specific rule stays valid | 1..3650 [A] | 180 (S14; no derivation) | operator | `T↓` | yes: `valid_until` is fixed at sign-off | `FND` | 14:422, 14:596 |
| `launch.measurement_validity_days` | days | days after the newest evidence `occurred_at` that a measurement-based sign-off (`g2.*`, `g3.*`, `g5.*`) stays valid | 1..3650 [A] | 120 (S14; no derivation) | operator | `T↓` | yes: `valid_until` is fixed at sign-off | `FND`; how fast the device matrix and throughput drift, seen by repeating `CAL` and `TEC` [H] | 14:422, 14:598 |
| `launch.evidence_max_bytes` | int | bytes of one `GateEvidence` file | 1024..104857600 [A: the range of `job.max_upload_bytes`]; `ISS-16016` | 10,485,760 = 10 x 1,048,576 (S14; no derivation) | operator | `T↓` | yes: checked when evidence is attached; stored evidence is kept | `OPS`: sizes of real memos and reports | 14:157, 14:599 |
