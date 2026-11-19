# Sweep candidates for old heading numbers (generated 2026-11-19)

Heading renumbering by FIX-21 (docs/fix/FIX-21.md): 10b: old 10.11..10.19 -> new 10.21..10.29; 11c: old 11.41..11.59 -> new 11.51..11.69; 11d: old 11.40..11.57 -> new 11.70..11.87. 10a keeps 10.1..10.19 and 11b keeps 11.31..11.49, 11a keeps 11.1..11.29. Because old and new ranges overlap, a number is stale ONLY if the sentence points into the 10b safety file, the 11c admin-tools file or the 11d copy file under its OLD number; a pointer into the file the line itself is in (10a's own 10.11..10.19, 11b's own 11.41..11.49) is correct. Decide by the words around the pointer (10b, safety, threat model, secrets, 11c, admin tool, 11d, copy). Line numbers drift: search about 40 lines either way using the snippet.

| file:line | matched number | snippet |
| --- | --- | --- |
| spec/05a-entities.md:107 | `10.14.2` | / A raw IP address / FD Principle 8; `retention.raw_ip_stored` = false (constant) / A keyed hash with a TTL, held only in the volatile rate- |
| spec/05a-entities.md:124 | `10.13.1` | / Stored in / `submissions.volunteer_handle` with `handle_key_version`, and in the internal manifest (S5.8.8). Never computed for a public p |
| spec/05a-entities.md:124 | `10.13.3` | / Stored in / `submissions.volunteer_handle` with `handle_key_version`, and in the internal manifest (S5.8.8). Never computed for a public p |
| spec/05a-entities.md:141 | `10.14.2` | The creation-time IP hash is not a column of any table of this model (FIX-17, audit A04 finding 15). Rate-limit counters (per member, per IP |
| spec/05a-entities.md:141 | `10.14.2` | The creation-time IP hash is not a column of any table of this model (FIX-17, audit A04 finding 15). Rate-limit counters (per member, per IP |
| spec/05a-entities.md:141 | `10.13.2` | The creation-time IP hash is not a column of any table of this model (FIX-17, audit A04 finding 15). Rate-limit counters (per member, per IP |
| spec/05a-entities.md:431 | `10.15.2` | **Edge clearing** [A] (default-pending D-12; 10a 10.10, `invite.accountability_days`). That many days after the invitee's `Member.created_at |
| spec/07-policy.md:293 | `11.43.1` | **Single owner of requester rejection copy.** This table is the only owner of the requester-facing rejection and warning copy. S11.* (spec/1 |
| spec/10a-identity.md:8 | `10.18` | - **Covered elsewhere in `S10.*`** [A]: the threat-model table (`THR-nn`), the secrets inventory and rotation procedure, hosting and reachab |
| spec/10a-identity.md:9 | `S10.19` | - **Numbering** [A]: this file owns `S10.1`..`S10.19`; any other S10 file starts at `S10.20` (`ISS-101`). |
| spec/10a-identity.md:10 | `10.18` | - **Reading rules** [D]: parameters are named exactly as in `S0.10`; the few this file adds are in 10.18 and reported as convention gaps. Fi |
| spec/10a-identity.md:12 | `10.17` | **Design commitments**, binding on every later part and tested in 10.17: [D] |
| spec/10a-identity.md:19 | `10.14` | / IC4 / Every stored identity item has a row in the 10.14 table; anything not in that table is not collected / FD Principle 8 / |
| spec/10a-identity.md:27 | `10.12` | A `Member` is a pseudonym: one row plus public keys. One person may hold several members; Hamyar neither forbids nor links them, except thro |
| spec/10a-identity.md:27 | `10.11` | A `Member` is a pseudonym: one row plus public keys. One person may hold several members; Hamyar neither forbids nor links them, except thro |
| spec/10a-identity.md:31 | `10.14.1` | / `Member` (`mem_`) / `status`, `trust_tier`, `tier_before_restriction`, `created_at`, `last_active_on` (UTC date only), `registration_devic |
| spec/10a-identity.md:34 | `10.13` | / `Session` (`ses_`) / `principal_type`, `member_id` or `admin_user_id`, `key_id` (member) or `credential_id` (admin), `token_hash`, `create |
| spec/10a-identity.md:40 | `10.11` | / `AdminUser` (`adm_`) / `label` (pseudonym), `roles` (subset of `reviewer`, `operator`), `status` (`invited`, `active`, `disabled`), `decla |
| spec/10a-identity.md:41 | `10.12` | / `AdminCredential` (`acr_`) / `admin_user_id`, `credential_id`, `public_key`, `sign_count`, `transports`, `label`, `status` (`pending`, `ac |
| spec/10a-identity.md:99 | `10.13` | / 8 / Issue a session (10.13) and return `{member_id, key_id, session}` / / |
| spec/10a-identity.md:156 | `10.15` | **Risks, stated plainly** [D]: (1) the mail provider and any relay see the address and the fact that Hamyar wrote to it; (2) an operator, or |
| spec/10a-identity.md:165 | `10.13` | planned rotation of device key K_old -> K_new            # step-up required (10.13) |
| spec/10a-identity.md:209 | `10.13` | B: next step is an ordinary session by challenge (10.13); B inherits nothing |
| spec/10a-identity.md:245 | `10.14` | Status is never changed by recovery: a `suspended` or `banned` member stays so, `trust_tier` and `restricted` carry over, and a `closed` mem |
| spec/10a-identity.md:262 | `10.11` | / 10 / Operator social engineering / Someone asks support to restore access / No operator or reviewer permission can restore or reassign a k |
| spec/10a-identity.md:275 | `10.14.2` | / IP hash (10.14.2) / Daily and per-minute counters / Daily-rotating keyed hash, kept at most `retention.ip_hash_ttl_days` / New network or  |
| spec/10a-identity.md:332 | `10.12` | The invite is a 128-bit random code carried in a link fragment, `https://<member-origin>/join#<code>`; a fragment is not sent in the request |
| spec/10a-identity.md:334 | `10.15.2` | **Visibility and the social-graph risk** [D]: a vouching graph shows who knows whom, which can expose people if one pseudonym is unmasked. S |
| spec/10a-identity.md:359 | `10.11` | ## 10.11 Roles and permission matrix |
| spec/10a-identity.md:370 | `10.13` | / `perm.identity.start_session` / Y / - / - / - / - / - / signature (10.13) / |
| spec/10a-identity.md:402 | `S10.16.4` | / `perm.report.decide` / - / - / - / Y / - / - / X8, X11 [A]; the actions of 10b S10.16.4 except `ban` (`perm.member.ban`) / |
| spec/10a-identity.md:428 | `10.15` | / `perm.identity.purge_optional_pii` / - / - / - / - / Y / - / X8; engages `kill.optional_pii` (10.15) / |
| spec/10a-identity.md:443 | `10.12` | / X9 / Two-person approval by a different `AdminUser` (10.12) / |
| spec/10a-identity.md:455 | `10.12` | ## 10.12 Admin authentication |
| spec/10a-identity.md:504 | `10.13` | ## 10.13 Session handling |
| spec/10a-identity.md:510 | `10.12` | / Issued by / A signed challenge with an active `MemberKey` (purpose `session`) or by registration or recovery / WebAuthn assertion (10.12)  |
| spec/10a-identity.md:525 | `10.11` | reject FORBIDDEN     if the permission or a condition X3..X8 fails (10.11) |
| spec/10a-identity.md:533 | `10.14` | ## 10.14 Logging, IP handling and retention |
| spec/10a-identity.md:535 | `10.14.1` | ### 10.14.1 What is and is not collected [D] |
| spec/10a-identity.md:542 | `10.14.2` | / IP hash / Short-lived / Rate-limit counter keys in a volatile store (10.14.2) / At most `retention.ip_hash_ttl_days` (1); each counter die |
| spec/10a-identity.md:548 | `10.13` | / Session / Yes / SHA-256 of the token, state, expiry (10.13) / `short`, at most `retention.session_days` (90) / Authentication / |
| spec/10a-identity.md:569 | `10.15` | / DNS, TLS and connection metadata at the host or CDN / Outside this system / Whatever the host keeps / Unknown [V] / Stated in 10.15 and th |
| spec/10a-identity.md:571 | `10.14.2` | ### 10.14.2 Exact IP handling [D] |
| spec/10a-identity.md:578 | `S10.14.2` | k_day = secret.ip_hash_key[day]   # a separate random 256-bit key per UTC day (10b S10.14.2), NOT derived from a longer-lived key, so destro |
| spec/10a-identity.md:585 | `10.15.4` | 3. **`retention.ip_hash_ttl_days`** is the ceiling on any IP-hash-bearing record. Setting it to 0 turns off the daily IP limits (only per-mi |
| spec/10a-identity.md:586 | `S10.14.2` | 4. **Residual risk, stated plainly:** the IPv4 space has only 2^32 addresses, so anyone who holds both the hashes and `secret.ip_hash_key` c |
| spec/10a-identity.md:587 | `10.15.1` | 5. **Deployment requirement** [V]: the reverse proxy, CDN or platform MUST NOT write client IPs to access logs, and the trusted header that  |
| spec/10a-identity.md:590 | `10.14.3` | ### 10.14.3 Closure, export, deletion [D] |
| spec/10a-identity.md:594 | `10.15` | ## 10.15 Member safety in a high-risk context |
| spec/10a-identity.md:598 | `10.15.1` | ### 10.15.1 What each party can see |
| spec/10a-identity.md:605 | `10.11` | / Operator or admin (insider) / Pseudonymous rows within their permissions (10.11); invite edges (operators only) / E-mail (not exposed), ke |
| spec/10a-identity.md:609 | `10.15.4` | / Browser or phone vendor, extensions, cloud sync / Whatever is on the device, including the key store and clipboard / n/a / Warnings at key |
| spec/10a-identity.md:611 | `10.15.2` | ### 10.15.2 Seizure and compelled disclosure |
| spec/10a-identity.md:616 | `10.15.4` | / Database plus secrets store seized / The above plus decryptable e-mail addresses; `vol_` handles of every key version not yet destroyed, l |
| spec/10a-identity.md:625 | `10.15.3` | ### 10.15.3 No location, no mandatory identity [D] |
| spec/10a-identity.md:627 | `10.14.1` | No location is collected, inferred or displayed by default (`public.location_display` = `never`); no GeoIP is used (10.14.1); teams are opt- |
| spec/10a-identity.md:629 | `10.15.4` | ### 10.15.4 Safety features [D] |
| spec/10a-identity.md:647 | `10.16` | ## 10.16 What the platform can NOT promise |
| spec/10a-identity.md:657 | `10.14.2` | 7. IP hashes are irreversible. They are keyed and short-lived, but enumerable by whoever holds the key and the hashes (10.14.2). |
| spec/10a-identity.md:661 | `10.14.3` | 11. Backups, deleted e-mail and closed accounts vanish at once. Backups expire on their schedule (10.5, 10.14.3). |
| spec/10a-identity.md:664 | `10.17` | ## 10.17 Acceptance criteria |
| spec/10a-identity.md:704 | `10.18` | ## 10.18 Events, interfaces, parameters, hooks |
| spec/10a-identity.md:706 | `10.18.1` | ### 10.18.1 Operations required by this part |
| spec/10a-identity.md:728 | `10.11` | / `approveApproval` / `POST /v1/admin/approvals/{apv_id}/approvals` / admin / by action (10.11); a two-person action is started by the concr |
| spec/10a-identity.md:730 | `10.18.2` | ### 10.18.2 Events and metrics [A] |
| spec/10a-identity.md:736 | `10.18.3` | ### 10.18.3 Parameters this part adds [A] |
| spec/10a-identity.md:761 | `10.18.4` | ### 10.18.4 Hooks this part needs from other S10 files [A] |
| spec/10a-identity.md:764 | `10.15` | 2. Threat model: rows for account takeover, de-anonymization, compelled disclosure, fake accounts and invite-tree abuse, insider and operato |
| spec/10a-identity.md:764 | `10.16` | 2. Threat model: rows for account takeover, de-anonymization, compelled disclosure, fake accounts and invite-tree abuse, insider and operato |
| spec/10a-identity.md:765 | `10.13` | 3. Ban process: define the `reason class` values `credit_farming`, `forgery`, `sybil` used in 10.10, the two-person ban, the appeal path and |
| spec/10a-identity.md:766 | `10.14.2` | 4. Hosting: the requirements of 10.14.2 item 5 (no client IP in host logs; trusted client-address header) and the reachability checks marked |
| spec/10a-identity.md:772 | `S10.19` | / `ISS-101` / minor / prompt / `S10` is split over several files, so `S10.<m>` numbers can collide, and this file lists identity-relevant co |
| spec/10a-identity.md:773 | `10.12` | / `ISS-102` / major / FD§3.2, FD§8.3 / The FD makes e-mail optional without saying what it is for, names no account recovery besides the key |
| spec/10a-identity.md:776 | `10.18.2` | Convention additions made by this part (not issues, listed so `S0.*` can fold them back): entities `AuthChallenge` (`chl_`), `DeviceLinkOffe |
| spec/10a-identity.md:776 | `10.18.3` | Convention additions made by this part (not issues, listed so `S0.*` can fold them back): entities `AuthChallenge` (`chl_`), `DeviceLinkOffe |
| spec/10a-identity.md:776 | `10.11` | Convention additions made by this part (not issues, listed so `S0.*` can fold them back): entities `AuthChallenge` (`chl_`), `DeviceLinkOffe |
| spec/10a-identity.md:776 | `10.15.4` | Convention additions made by this part (not issues, listed so `S0.*` can fold them back): entities `AuthChallenge` (`chl_`), `DeviceLinkOffe |
| spec/11a-volunteer-ux.md:162 | `S11.49` | / Paste-back draft / Device storage keyed by lease id (memory only if storage is unavailable), as specified in S11.49 / Until acknowledged,  |
| spec/11a-volunteer-ux.md:200 | `S11.55` | / `ui.first_load_budget_bytes` / int / 204,096 (the same budget as `ui.budget.first_load_bytes` of S11.55: 100,000 + 20,000 + 80,000 + 4,096 |
| spec/11a-volunteer-ux.md:206 | `S11.55` | / `ui.lease_warning_ratio` / ratio / 0.25 (warn when this share of `lease.timeout_s` remains; with the defaults it equals `ui.lease.warn_rem |
| spec/11a-volunteer-ux.md:638 | `S11.49` | key = draft.idempotency_key                      # new key per Submit press, reused only by retries of the same body (S0.11.5, S11.49) |
| spec/11a-volunteer-ux.md:1327 | `S11.51` | All text below is draft copy, marked `needs_human_and_legal_review`; none is a legal conclusion and each depends on facts that are [V]. Any  |
| spec/11a-volunteer-ux.md:1327 | `S11.51` | All text below is draft copy, marked `needs_human_and_legal_review`; none is a legal conclusion and each depends on facts that are [V]. Any  |
| spec/11a-volunteer-ux.md:1327 | `S11.50` | All text below is draft copy, marked `needs_human_and_legal_review`; none is a legal conclusion and each depends on facts that are [V]. Any  |
| spec/11b-requester-ux.md:15 | `11.44` | / Metadata declarations with plain-language P/L/S/M explanations / 11.36, 11.44 / `SCR-req-05` / |
| spec/11b-requester-ux.md:16 | `11.43` | / Policy result with reason codes / 11.36, 11.43 / `SCR-req-06` / |
| spec/11b-requester-ux.md:18 | `11.45` | / Escrow confirmation and the 'downstream use uncontrolled' notice for open licenses / 11.36, 11.45 / `SCR-req-08` / |
| spec/11b-requester-ux.md:19 | `11.48` | / Job progress with a per-cell status map (panel status-graph and bottleneck ideas, [V]) / 11.39, 11.48 / `SCR-req-12`, `SCR-req-13` / |
| spec/11b-requester-ux.md:20 | `11.40` | / Cancellation and refund display / 11.40 / `SCR-req-14`, `SCR-req-15` / |
| spec/11b-requester-ux.md:22 | `11.41` | / Results download with provenance manifest, including the manifest JSON schema / 11.41, 11.42 / `SCR-req-16` / |
| spec/11b-requester-ux.md:22 | `11.42` | / Results download with provenance manifest, including the manifest JSON schema / 11.41, 11.42 / `SCR-req-16` / |
| spec/11b-requester-ux.md:23 | `11.41` | / Rating of the outcome / 11.41 / `SCR-req-17` / |
| spec/11b-requester-ux.md:24 | `11.43` | / Requester-visible rejection reasons in EN and FA / 11.43 / `SCR-req-06`, `SCR-req-18` / |
| spec/11b-requester-ux.md:25 | `11.45` | / Copy for policy, privacy and risk notices in FA and EN / 11.45 / all / |
| spec/11b-requester-ux.md:26 | `11.46` | / Persian first: RTL, numerals, Jalali and Gregorian, mixed direction, accessibility, low bandwidth / 11.33, 11.46 / all / |
| spec/11b-requester-ux.md:53 | `11.42` | / `RD-08` / A requester never sees a volunteer identity, a `vol_` handle, a gold cell, or any timing finer than the granularity in 11.42. [D |
| spec/11b-requester-ux.md:59 | `11.46` | / `RD-14` / Everything that originates from volunteers or uploads (outputs, file names, glossary terms, reported model names) is untrusted t |
| spec/11b-requester-ux.md:66 | `11.43` | Every screen below uses these rows: **Purpose**, **Entry conditions**, **Blocks** (top to bottom), **States**, **Actions** (with the API ope |
| spec/11b-requester-ux.md:66 | `11.45` | Every screen below uses these rows: **Purpose**, **Entry conditions**, **Blocks** (top to bottom), **States**, **Actions** (with the API ope |
| spec/11b-requester-ux.md:111 | `11.49` | Operation ids (lowerCamelCase, S0.5) are the contract between the screens and S15.*; the paths are proposals in the shapes of S0.11 [A]. Eve |
| spec/11b-requester-ux.md:209 | `11.43` | **Which codes the requester screens must handle** (messages in 11.43): `400 VALIDATION_FAILED` (with `details.fields`), `401` family, `403 F |
| spec/11b-requester-ux.md:209 | `11.43.2` | **Which codes the requester screens must handle** (messages in 11.43): `400 VALIDATION_FAILED` (with `details.fields`), `401` family, `403 F |
| spec/11b-requester-ux.md:220 | `11.49` | / 2 Data / `SCR-req-03` / `draft` / `upload.accepted`+ or `upload.screen_failed`+ (11.49) / |
| spec/11b-requester-ux.md:306 | `11.46` | / Accessibility / File input and paste area both labelled; drag-and-drop is never the only route; progress is text plus `role="progressbar"` |
| spec/11b-requester-ux.md:349 | `11.44` | / Blocks / Four option groups in this order: Purpose `P0`..`P3`, License `L0`..`L3`, Sensitivity `S0`..`S3`, Service `M0`..`M2`. Each option |
| spec/11b-requester-ux.md:349 | `11.45` | / Blocks / Four option groups in this order: Purpose `P0`..`P3`, License `L0`..`L3`, Sensitivity `S0`..`S3`, Service `M0`..`M2`. Each option |
| spec/11b-requester-ux.md:349 | `11.45` | / Blocks / Four option groups in this order: Purpose `P0`..`P3`, License `L0`..`L3`, Sensitivity `S0`..`S3`, Service `M0`..`M2`. Each option |
| spec/11b-requester-ux.md:350 | `11.43.1` | / States / `incomplete` (groups missing; the button is disabled and names them, which is the client form of `R1`), `submit_refused` (`submit |
| spec/11b-requester-ux.md:367 | `11.43.1` | / Blocks / `waiting`: text that the check may include a reviewer for sampled or flagged inputs (`screen.review_rate_new_requester`, `screen. |
| spec/11b-requester-ux.md:482 | `11.43.1` | / States / `no_availability` (no day offered; says so), `policy_rejected` (reasons as in 11.43.1), `insufficient_credit`, `at_reservation_ca |
| spec/11b-requester-ux.md:596 | `11.48` | The linear baseline is crude because volunteer supply arrives in daily batches; whether `behind` predicts a missed quote is measured in Phas |
| spec/11b-requester-ux.md:633 | `11.40` | ## 11.40 Cancellation and refund screens |
| spec/11b-requester-ux.md:667 | `11.41` | ## 11.41 Results and rating screens |
| spec/11b-requester-ux.md:675 | `11.45` | / Blocks / (1) Completeness banner; for a partial result the missing cell indices. (2) For licenses `L1` and `L2` the notice "downstream use |
| spec/11b-requester-ux.md:717 | `11.42` | ## 11.42 Provenance manifest (requester profile) |
| spec/11b-requester-ux.md:721 | `11.42.1` | ### 11.42.1 Field decisions [D][A] |
| spec/11b-requester-ux.md:738 | `11.42.2` | ### 11.42.2 JSON Schema (draft 2020-12), version 1 |
| spec/11b-requester-ux.md:851 | `11.42.3` | ### 11.42.3 Verification on the device [D] |
| spec/11b-requester-ux.md:874 | `11.43` | ## 11.43 Rejection reasons, errors and appeal |
| spec/11b-requester-ux.md:876 | `11.43` | All rows of 11.43 to 11.45 carry the marker `needs_human_and_legal_review` (S0.5). Placeholders in braces are filled from parameters or serv |
| spec/11b-requester-ux.md:876 | `11.45` | All rows of 11.43 to 11.45 carry the marker `needs_human_and_legal_review` (S0.5). Placeholders in braces are filled from parameters or serv |
| spec/11b-requester-ux.md:878 | `11.43.1` | ### 11.43.1 Requester-visible policy rejection reasons [D] |
| spec/11b-requester-ux.md:894 | `11.43.2` | `policy.R9.policy_version_stale` is shown as this row only when the policy changed before confirmation (nothing was charged). When a rule ch |
| spec/11b-requester-ux.md:898 | `11.43.2` | ### 11.43.2 Errors and conditions [D] |
| spec/11b-requester-ux.md:900 | `11.49` | `details.reason` and `details.cap` values are convention additions [A] (11.49). |
| spec/11b-requester-ux.md:946 | `11.44` | ## 11.44 Plain-language explanations of P, L, S and M (declarations copy) |
| spec/11b-requester-ux.md:968 | `11.45` | ## 11.45 Notices: policy, privacy and risk copy |
| spec/11b-requester-ux.md:999 | `11.46` | ## 11.46 Persian-first, accessibility and low-bandwidth rules |
| spec/11b-requester-ux.md:1008 | `11.48` | / Fonts / System font stack with Persian-capable families and a guaranteed generic fallback; an optional self-hosted subset font served from |
| spec/11b-requester-ux.md:1019 | `11.47` | ## 11.47 Cross-cutting acceptance criteria |
| spec/11b-requester-ux.md:1027 | `11.46` | - **AC-req-73** Given any requester route loads, When network requests are listed, Then every request goes to the application's own origin ( |
| spec/11b-requester-ux.md:1029 | `11.43.1` | - **AC-req-75** Given a draft whose declarations pass the client checks but fail `R1` on the server (for example `R1` `not_allowlisted`), Wh |
| spec/11b-requester-ux.md:1032 | `11.48` | ## 11.48 Reuse from the existing panel [V] |
| spec/11b-requester-ux.md:1044 | `11.46` | / Third-party web font loaded from a font host / Rejected: requester screens load no third-party resource (11.46) / The font host / |
| spec/11b-requester-ux.md:1047 | `11.49` | ## 11.49 Convention additions made by this part |
| spec/11b-requester-ux.md:1057 | `11.41` | / Enum / `outcome_rating`: `good`, `mixed`, `poor`; `rating_tag`: `accuracy`, `format`, `completeness`, `speed_vs_quote`, `other` / 11.41 / |
| spec/11b-requester-ux.md:1059 | `11.42` | / Enum / `manifest_profile`: `requester`, `internal` / 11.42 / |
| spec/11b-requester-ux.md:1060 | `11.43.2` | / Error detail / `details.reason`: `quote_changed`, `policy_version_changed`, `no_approved_service`, `job_not_in_state`; `details.cap`: `con |
| spec/11b-requester-ux.md:1085 | `11.49` | / `ISS-114` / minor / prompt / S11 is split over several files but S0 fixes no rule for heading numbers or top headings of sibling files, an |
| spec/11b-requester-ux.md:1086 | `11.40` | / `ISS-115` / major / FD§4.8 / The FD says only that unstarted cells are refundable on cancellation; it does not say what happens to cells i |
| spec/11b-requester-ux.md:1086 | `11.41` | / `ISS-115` / major / FD§4.8 / The FD says only that unstarted cells are refundable on cancellation; it does not say what happens to cells i |
| spec/11b-requester-ux.md:1087 | `11.42` | / `ISS-116` / major / FD§5.6 / FD§5.6 says requesters never see the salted-hash volunteer id yet also that exports carry the manifest; a man |
| spec/16b-parameters-a.md:31 | `10.18.3` | / `used in` / Part and line of the passage that reads it, as given by the cell; `10a:744` style lines for the 10.18.3 table rows are counted |
| spec/16b-parameters-a.md:88 | `10.16.3` | Notes [D][A]: (1) `report.urgent_triage_sla_s` is the second SLA of 10.16.3; the first is `report.triage_sla_days` (3 days, S16 16.12), and  |
| spec/16b-parameters-a.md:158 | `10.13.1` | **Public exposure** [A]: S10a states that all its parameters are public, and every row here is public except two proposals. `growth.referral |
| spec/16b-parameters-a.md:170 | `10.18.3` | The names below are used in S10a (10.18.3), S10b (10.18), S12 (12.13.3), S13 (13.13), S14 (14.13), S15a (convention list and 15.12) and S15b |
| spec/16b-parameters-a.md:170 | `10.18` | The names below are used in S10a (10.18.3), S10b (10.18), S12 (12.13.3), S13 (13.13), S14 (14.13), S15a (convention list and 15.12) and S15b |
| spec/16b-parameters-a.md:209 | `10.15.4` | / `security.reachability_check_interval_days` / days / days between two reachability checks of the service from the target network (10b 10.1 |
| spec/16b-parameters-a.md:253 | `10.13.1` | / `ISS-16006` / minor / none / `retention.sweep_interval_s` (10a, 10b) and `ops.purge_interval_s` (16.16) have the same default 3600 and ran |
| spec/16b-parameters-a.md:254 | `10.18.3` | / `ISS-16007` / minor / none / S10a 10.18.3 names a constraint `C9` (`session.member_abs_ttl_s <= retention.session_days x 86,400`), but S16 |
| spec/16b-parameters-a.md:267 | `10.16.8` | / `ISS-16020` / minor / none / `report.decision_sample_rate` may be 0 (10b range 0..1), which removes the second look that 10.16.8 uses agai |
| spec/16c-parameters-b.md:21 | `10.15.4` | Owner `operator` (area `ui`, S0 0.10.5). The budgets are read by the CI build check (`AC-i18n-27`) and by nothing at runtime; a deployed bui |
| spec/16c-parameters-b.md:69 | `11.42.1` | / `job.manifest_time_granularity_s` / duration_s / seconds / 60..86,400; must divide 86,400 (`S16C-C14`) [A] / 3,600 (initial configurable d |
| spec/16c-parameters-b.md:122 | `11.41` | / `S16C-C13` / `ui.requester.rating_window_days <= retention.job_payload_days` / warning (flags raised after the payload is purged cannot le |
| spec/16c-parameters-b.md:171 | `10.15.4` | / `ISS-16101` / minor / none / The first-load budget has two names and three definitions: `ui.first_load_budget_bytes` (10b parameter table, |
| spec/16c-parameters-b.md:171 | `10.15.6` | / `ISS-16101` / minor / none / The first-load budget has two names and three definitions: `ui.first_load_budget_bytes` (10b parameter table, |
