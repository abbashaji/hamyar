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
| `report.urgent_triage_sla_s` | duration_s | seconds from `filed_at` to `triaged_at` for urgent categories (`safety_of_person`, `injection_attempt`, `suspected_sensitive_data`, `legal_notice`) | 600..86400; `S16B-C9` | 14,400 (4 hours, S10b; a declared target, not a promise) | reviewer | `T↓` | yes: read when the SLA clock is evaluated; after a tightening an open report may become overdue, which raises the alarm only | `OPS`: time to triage seen in Phase 1 | 10b:516, 10b:640 |
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

## 16.B.7 Alias rows

An alias is not seeded, is refused on write as an unknown name (`AC-param-14`), and is listed so that `check_params` and readers resolve it. The part that uses the alias is amended to the canonical name at assembly. [D]

| alias | canonical | value | seeded | used in | note |
| --- | --- | --- | --- | --- | --- |
| `identity.link_code_ttl_s` | `identity.device_link_code_ttl_s` | 300 s, 30..3600, `T↓` (S0 0.10.6, 16.11) | no | 18:746 (`AC-ident-05`) | Same quantity: the lifetime of a device-link offer (10.7). `ISS-16002` |
| `growth.referral.bonus_credits` | the pair `growth.referral.bonus_referrer_credits` and `growth.referral.bonus_newcomer_credits` | 1 and 1 (16.14) | no | 15a:582 | S15a says both parties receive one amount; S0, S12 and S16 define two parameters, which may differ. Read both. `ISS-16003` |
| `retention.backup_days` | `ops.backup_retention_days` | 35 days, 1..365, `T↓` (16.16) | no | 10b:146, 10b:169 | Same number, same range, same promise (data is gone from backups within this many days). `ISS-16005` |
| `retention.sweep_interval_s` | `ops.purge_interval_s` [V] | 3600 s, 60..86400, `T↓` (16.16) | no | 10a:529, 10a:757; 10b:146 | Same default and range; the sweep that deletes expired and closed rows is the purge job. `ISS-16006` |
| `session.admin_stepup_s` | `session.step_up_max_age_s` [V] | 300 s, 30..3600, `T↓` | no | 11c:67, 11c:126 | Assumed from the name and from S10a X8 (one step-up window for admin writes); the 11c text was not read. `ISS-16004`, `ISS-16015` |

## 16.B.8 Why the safety limits are safe

Only rows that limit abuse, exposure or spend are listed. None of these values is derived from measurement; each is safe because of the mechanism named, and each is replaced by the measurement in its calibration column. [D][H]

| Parameter | Why the default is safe | What makes it unsafe |
| --- | --- | --- |
| `identity.challenge_ttl_s` = 60 | An unused challenge is worthless alone: the signature covers purpose, audience, challenge id, nonce and the hash of the request body (10.3.2), and the nonce is single use. The TTL only bounds how many open challenges exist. | A value below the signing round trip on a slow phone link makes honest sign-ins retry; a very large value only grows the open-challenge table. |
| `identity.email_code_ttl_s` = 900 | Guessing is bounded by the attempt cap: P(success per code) <= `identity.code_max_attempts` / 32^8 = 5 / 2^40, about 4.5 x 10^-12, whatever the TTL. E-mail is never a login or a recovery factor (10.5), so a stolen code can at most bind an address. | Raising `identity.code_max_attempts` without lowering the TTL. |
| `identity.max_devices_per_member` = 5 | Rate limits are per member (10.9), so extra devices do not multiply throughput; the cap bounds parallel contributors per member. | Removing per-member limits while raising it. |
| `session.step_up_max_age_s` = 300 | After 5 minutes a sensitive action needs a fresh signature by a non-extractable device key (member) or a fresh WebAuthn assertion (admin), so an unlocked stolen session cannot reach it. [H] | A long window lets one hijacked session do several sensitive actions. |
| `session.admin_stepup_ttl_s` = 300 | The challenge is single use and WebAuthn binds it to the admin origin; an unanswered one simply expires. | None found; a value far below the time a hardware key takes to answer makes admin login fail. |
| `session.max_active_per_member` = 10 | A backstop: the oldest idle session is revoked, no login is refused; at the defaults at most 5 sessions can exist (`ISS-16008`). | A value below `identity.max_devices_per_member` logs out legitimate devices (`S16B-C2`). |
| `growth.referral.max_per_day` = 5, `growth.referral.reserve_draw_cap_ratio` = 0.10 | Worst-case draw per UTC day is 5 x (1 + 1) = 10 credits, 1% of `reserve.ceiling_credits` (1000), and at most 10% of the start-of-day balance, so starter grants are not starved (12.10.3). Payment also needs an accepted cell, a delay of `growth.referral.hold_s`, and a device that differs from the referrer's. | Raising the count without the ratio, or the bonuses without `S16B-C8` showing which cap binds. |
| `growth.referral.max_per_invite_tree_per_30d` = 5 | Bounds what one invite tree can draw in 30 days to 5 pairs, so one farmed tree cannot drain the daily budget alone. | A value below `growth.referral.max_per_referrer_per_30d` (`S16B-C7`). |
| `growth.referral.clawback_window_days` = 30 | Not above `credit.lifetime_days` (60), so a clawback can still reach the unspent part of the bonus lot (`S16B-C6`). | 0 switches clawback off; a value above the lot lifetime reaches nothing. |
| `launch.approval_window_s` = 86,400 | Approval re-runs `evaluate_switch` and is refused if the reasons or `relied_on` changed (14.8.1), so a long window cannot approve a stale state; it only bounds how long a proposal stays open. | None found; the safe direction is a shorter window. |
| `launch.generic_validity_days`, `launch.counsel_validity_days`, `launch.measurement_validity_days` | A shorter validity only reopens items sooner, and a reopened item closes the switches that rely on it in the same transaction (14.8.3); stale evidence is the unsafe direction, so lowering is the tightening. | Raising any of them keeps old counsel advice, old measurements or old sign-offs in force longer. |
| `launch.evidence_max_bytes` = 10 MiB | Evidence is attached only by admins, the media type is sniffed and the hash is computed by the server (14.3); the cap bounds storage per row. | A value above `api.max_body_bytes` with no chunked upload makes the default unreachable (`ISS-16016`). |

## 16.B.9 Cross-parameter constraints

Evaluated on every write against the configuration as it will be at `effective_from` (16.17.2). Errors refuse the write; warnings are returned and recorded in the change-log entry. [D]

| Id | Constraint | Kind |
| --- | --- | --- |
| `S16B-C1` | `session.member_abs_ttl_s <= retention.session_days x 86,400` and `session.admin_abs_ttl_s <= retention.session_days x 86,400` (the rule S10a called `C9`, `ISS-16007`) | error |
| `S16B-C2` | `session.max_active_per_member >= identity.max_devices_per_member` | error |
| `S16B-C3` | `session.touch_min_interval_s < min(session.member_idle_ttl_s, session.admin_idle_ttl_s)` | error |
| `S16B-C4` | `3 x max(report.max_text_chars, appeal.reason_max_chars, team.label_max_chars) <= api.max_body_bytes` (a character is at most 3 bytes, as `S9-C1`; JSON escapes are not counted, an oversize body is refused with 413 anyway) | warning |
| `S16B-C5` | `growth.referral.hold_s < growth.referral.qualify_window_days x 86,400` | error |
| `S16B-C6` | `growth.referral.clawback_window_days <= credit.lifetime_days` | warning |
| `S16B-C7` | `growth.referral.max_per_invite_tree_per_30d >= growth.referral.max_per_referrer_per_30d` | warning |
| `S16B-C8` | `growth.referral.max_per_day x (growth.referral.bonus_referrer_credits + growth.referral.bonus_newcomer_credits) <= reserve.ceiling_credits x growth.referral.reserve_draw_cap_ratio` (when false, the ratio and not the count is the daily limit at a full Reserve) | warning |
| `S16B-C9` | `report.urgent_triage_sla_s <= report.triage_sla_days x 86,400` | error |

Worked check of the initial defaults [D]: `S16B-C1` 7,776,000 <= 90 x 86,400 = 7,776,000 and 28,800 <= 7,776,000; `S16B-C2` 10 >= 5; `S16B-C3` 300 < min(2,592,000; 1800) = 1800; `S16B-C4` 3 x 1000 = 3000 <= 1,048,576; `S16B-C5` 86,400 < 30 x 86,400 = 2,592,000; `S16B-C6` 30 <= 60; `S16B-C7` 5 >= 5; `S16B-C8` 5 x (1 + 1) = 10 <= 1000 x 0.10 = 100; `S16B-C9` 14,400 <= 3 x 86,400 = 259,200. All pass. The row `abuse.admin_lookup_rate` has no default and is not in any check (`ISS-16015`).

## 16.B.10 Not parameters, public exposure, hypotheses, verifications

**Not parameters** [D]: none of the 31 names is an event or state name. Each is a bounded limit, duration, ratio or count read by a rule, which is what 16.1 R16-5 leaves in the table. One doubt remains: `abuse.admin_lookup_rate` could be the name of a metric or a rate-limit scope rather than a configurable value; the cell lists it as a parameter, and its passage was not read [V] (`ISS-16015`).

**Public exposure** [A]: S10a states that all its parameters are public, and every row here is public except two proposals. `growth.referral.max_per_day` and `growth.referral.max_per_invite_tree_per_30d` are anti-farming values like `growth.referral.max_per_referrer_per_30d`, which 16.17.5 hides, so they are proposed for the hidden list (`ISS-16011`). `abuse.admin_lookup_rate` is undecided until its passage is read. `ops.purge_interval_s`, the canonical row behind `retention.sweep_interval_s`, is proposed as public because it is the latency of the deletion promise of 10.13.1 item 8 (`ISS-16006`).

**Hypotheses [H]**: `identity.challenge_ttl_s` = 60 is long enough for a signing round trip on a phone link in Iran; `session.step_up_max_age_s` = 300 balances friction and exposure; `growth.referral.qualify_window_days` = 30 covers most newcomers' time to a first verified cell; 0.10 of closed reports is a useful second-look sample at pilot volume (it may select none).

**Verifications [V]** (what, by whom, where stored): the 11c passages for `session.admin_stepup_s` and `abuse.admin_lookup_rate` (cell C-036 or the S11 console owner; the value goes into this table); counting rule of `_chars` limits for Persian text (S9 text rules owner, recorded in S9); counsel's review period behind `launch.counsel_validity_days` (`CNS`, memo reference on the `ParameterVersion` reason); whether `ops.purge_interval_s` and `retention.sweep_interval_s` are one job (S4 owner).

**Assumptions [A]** (with the decision that could overturn each): canonical-versus-alias choices follow 'already defined in S0 or S16 wins'; `invite.accountability_days` is treated like retention for lowering; ranges not given by a source part (`session.max_active_per_member` 1..100, `session.admin_stepup_ttl_s` 10..600, `launch.*` ranges) are chosen here; owner `operator` for the area `abuse`.

**What this file cannot promise** [D]: a default is a guess until its replacing measurement exists; none of these values shows that a limit is safe for real members, legal in any jurisdiction or enough at a pilot of 30 to 50 members.

## Issues raised

Found while completing the table. Each resolution is already applied in this file; C-001 consolidates them into S2.* and C-036 checks them against the whole table. Ids use the block `ISS-16001`..`ISS-16099` of this file [D].

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-16001` | minor | none | `identity.challenge_ttl_s` has two defaults: 60 (10a:743, range 10..600) and 120 (15a:860); 15a:108 says S10 wins where it differs in detail | 60 is canonical, range 10..600; S15a 15.9 convention list is amended at assembly | proposed |
| `ISS-16002` | minor | none | `identity.link_code_ttl_s` (18:746) names the quantity S0 calls `identity.device_link_code_ttl_s` (300 s) | Alias row, not seeded; S18 `AC-ident-05` is amended to the canonical name | proposed |
| `ISS-16003` | minor | FD§6.2 | `growth.referral.bonus_credits` (15a:582) is one amount for both parties; S0, S12 and S16 define `growth.referral.bonus_referrer_credits` and `growth.referral.bonus_newcomer_credits`, which can differ, and `Referral.bonus_ucr` in S15a holds one value | Alias of the pair, not seeded; S15a 15.8 is amended to name both parameters and to show both amounts | proposed |
| `ISS-16004` | minor | none | Three names for step-up time: `session.step_up_max_age_s` (10a:439, how long a step-up counts), `session.admin_stepup_ttl_s` (15b:87, how long an admin challenge may be answered) and `session.admin_stepup_s` (11c) | Two canonical rows for the two quantities; `session.admin_stepup_s` is an alias of the first [V]; both defaults are 300 and the pair must not be merged because the quantities differ | proposed |
| `ISS-16005` | minor | none | `retention.backup_days` (10b) and `ops.backup_retention_days` (16.16) are one setting: 35 days, 1..365 | `ops.backup_retention_days` is canonical (already seeded and public); the other is an alias; S10b is amended at assembly | proposed |
| `ISS-16006` | minor | none | `retention.sweep_interval_s` (10a, 10b) and `ops.purge_interval_s` (16.16) have the same default 3600 and range 60..86400; 16.16 marks `ops.purge_interval_s` as not public although it is the latency of the deletion promise (10.13.1 item 8) | Alias [V: S4 owner confirms they are one job]; `ops.purge_interval_s` is proposed as public | proposed |
| `ISS-16007` | minor | none | S10a 10.18.3 names a constraint `C9` (`session.member_abs_ttl_s <= retention.session_days x 86,400`), but S16 16.3 already uses `C9` for admission windows | Renamed to `S16B-C1` here; S10a text keeps its wording until assembly | proposed |
| `ISS-16008` | minor | none | `session.max_active_per_member` = 10 (15a) can never be reached under S10a, which allows one active session per key and at most `identity.max_devices_per_member` = 5 keys | Keep 10 as a backstop, add `S16B-C2` so a legitimate device is never logged out, and say in 15a that eviction is a backstop | proposed |
| `ISS-16009` | minor | none | `invite.strike_window_days` has three roles at 10a:342-343: the window in which strikes count, the length of an issuing suspension, and the window in which tree bans are counted for a freeze | One parameter is kept because renaming or splitting is not allowed in this audit; `S10a` may add `invite.suspension_days` and a freeze window later | needs_owner |
| `ISS-16010` | minor | none | `growth.referral.qualify_window_days` runs two clocks, joined to qualified and qualified to paid (12.10.2) | One value, with `S16B-C5` keeping `growth.referral.hold_s` below it; the owner may split it later | proposed |
| `ISS-16011` | minor | none | 16.17.5 hides `growth.referral.max_per_referrer_per_30d` but not the two sibling anti-farming caps `growth.referral.max_per_day` and `growth.referral.max_per_invite_tree_per_30d` | Both proposed for the hidden list in 16.17.5 | proposed |
| `ISS-16012` | minor | none | `team.label_max_chars` is applied to `Team.name` in 12.9.1, but `Team.group_label`, a free text typed by the member (10b item 3), has no limit | The limit applies to both fields [A] | proposed |
| `ISS-16013` | minor | none | No part defines how a `_chars` limit counts Persian text (code points, grapheme clusters, normalization, zero-width non-joiner); it matters for `report.max_text_chars`, `appeal.reason_max_chars`, `team.label_max_chars` and the `cell.envelope.*_chars` rows | Proposed rule: count Unicode code points after NFC normalization [A][V]; S9 text rules confirm and state it once | proposed |
| `ISS-16014` | minor | none | `abuse` is a parameter area in S11 but is not in S0 0.10.5 or 16.2.3, so it has no owner role | Area `abuse` added with owner `operator` and defining part S11 [A]; S0 0.10.5 is regenerated at assembly | proposed |
| `ISS-16015` | major | none | The S11 console file holding `11c:67`, `11c:126` and `11c:729` could not be opened by this writer, so `abuse.admin_lookup_rate` has no unit, range or default and `session.admin_stepup_s` is an alias by inference | The row is recorded without an invented value; the owner of that file or C-036 supplies type, unit, range, default and public flag before the seed runs (`AC-param-02`) | needs_owner |
| `ISS-16016` | minor | FD§8.3 | `launch.evidence_max_bytes` (10 MiB) exceeds `api.max_body_bytes` (1 MiB), and S15b 15.23.2 defines chunked upload only for terms copies | Evidence uses the same sealed chunk mechanism [A]; S14 and S15b confirm | proposed |
| `ISS-16017` | minor | FD§8.3 | Three names hold the same default, 86,400 s, for the lifetime of a pending two-person approval: `launch.approval_window_s` (14), `security.approval_ttl_s` (15b `ISS-154`) and `security.two_person_ttl_s` (10a) | `launch.approval_window_s` stays a canonical row because the launch flow stores its own proposal (14.8.1); the two `security.*` names are left to the cell that owns `security.*` | needs_owner |
| `ISS-16018` | minor | none | Passages read for this cell disagree with S16 on names outside its list: `calibration.min_samples_per_service` is 20 in 14:603 and 30 in 16.16; `security.secret_rotation_max_age_days` (14:600) and `security.secret_rotation_days` (16.16) are both 90; `ui.first_load_budget_bytes` has range 20,000..5,000,000 in 11a:198 and 10240..5242880 in 10b | Reported for the cells that own `calibration.*`, `security.*` and `ui.*`; nothing is changed here | proposed |
| `ISS-16019` | minor | FD§4.6 | `growth.referral.clawback_window_days` (30) can exceed the life of the bonus lot for members in the accelerated-expiry arm (`credit.lifetime_days_accelerated` = 14), so the clawback reaches nothing after the lot expires | `S16B-C6` warns against `credit.lifetime_days`; the effective period is the shorter of the two and is stated in 16.B.4 | proposed |
| `ISS-16020` | minor | none | `report.decision_sample_rate` may be 0 (10b range 0..1), which removes the second look that 10.16.8 uses against moderator abuse, and 0.10 of a few reports can select none | Range kept as S10b states it; lowering is a loosening (`T↑`) and needs notice and a second operator; a floor count is an owner decision and is not added here | needs_owner |
| `ISS-16021` | minor | none | `invite.accountability_days` is a retention period outside the `retention` area, and shortening it trades member privacy against accountability of inviters | Treated like retention when lowered (applies to existing edges); the trade-off is an owner decision under `SEC` | needs_owner |
