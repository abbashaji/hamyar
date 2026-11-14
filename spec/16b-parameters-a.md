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
| RB-5 What was read | For each name the passage cited by the cell was read with about 15 lines around it, and S0 0.10 and S16 were read in full. The part S11 operator console (`11c:67`, `11c:126`, `11c:729`) could not be opened: the file name is not given in the cell, in S0 0.13 or in the sibling parts, and 40 guessed paths returned NOT_FOUND. The two rows that rest on it are marked [V] and recorded as `ISS-16015`. [A][V] |
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
