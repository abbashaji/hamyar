# 10. Safety, secrets, hosting and abuse process

*Spec part 10, second file (`10b`) · owner cell C-012 · prompt scope I · binding on every part that stores data about members, handles a secret, chooses a host or moderates. Written against Founding Document draft v0.1 (FD) and `spec/00-conventions.md` (S0.*). Nothing here is legal advice and nothing here has been checked against any law, provider term or host: every legal point is [V] for counsel, and every statement about the existing panel repo is [V] because it rests on a static reading (`docs/source/panel-review.md`, cited as "panel-review §n") in which nothing was executed.*

## 10.11 Scope, boundaries and how to read this file

**What this file decides (prompt scope I)** [D]

| Topic | Where | Reason |
| --- | --- | --- |
| Threat model table (`THR-nn`) | S10.12 | FD§8.3 G1 requires a written threat model before any build beyond a throwaway prototype |
| Member safety design, exact disclosure inventory, what the platform cannot promise | S10.13 | FD Principle 8; `RISK-05` (FD§8.2) |
| Secrets inventory, storage, rotation, rotate-before-exposure rule, launch-gate items | S10.14 | FD§10 step 1; FD§8.3 G4 |
| Hosting interfaces, reachability, low bandwidth, no third-party resources | S10.15 | FD Principle 7; `RISK-14` (FD§8.2) |
| Abuse reporting, takedown, ban and appeals | S10.16 | FD§5.5, FD§5.7 items 1 and 10 |
| Acceptance criteria, added parameters and enums, register of unverified items | S10.17 to S10.19 | prompt K; ground rules 2 and 4 |

**What this file does not decide.** Identity mechanics (keys, recovery key, sessions, invites, device linking, the permission matrix, the exact logged fields) belong to the identity file of S10.*. Where this file states a constraint on them it says "constraint on S10.*", and the stricter reading applies until assembly records a decision (`ISS-104`). [D]

**Reading rules** [D]

- Tags follow S0.2. Every `[V]` in this file is collected in S10.19 with who verifies it and where the answer is stored; every `[A]` is collected there with the owner decision that could overturn it.
- Names (entities, enums, states, events, parameters, error codes, ID formats) are used exactly as in S0.*. Names this file adds are listed in S10.18 and reported under `## Issues raised`.
- User-facing promises say "declared" and "minimization", never "anonymous", "private", "secure" or "guaranteed" (FD Principle 8 and 11). A copy lint for these words is `AC-safety-14`.
- Every number is derived by a shown formula, taken from the parameter table in S0.10.6, or listed in S10.18 as an `initial configurable default`.

### 10.11.1 Assets [D]

| Asset | Why it matters | Defended mainly by |
| --- | --- | --- |
| Member safety (physical, legal, social) | Participation may carry personal risk in Iran (`RISK-05`); safety outranks growth (FD Principle 8) | S10.13 |
| Unlinkability of a pseudonym from a person | The only privacy property the design tries to protect, and only as minimization, never as anonymity | S10.13 |
| Ledger integrity | Trust is the asset (FD Principle 11); every credit traces to an accepted Commons cell (FD§4.2) | `THR-12`, S6.* |
| Volunteers' provider accounts | A suspended or exposed account harms the volunteer, not the project | `THR-09`, `THR-31`, S7.* |
| Requesters' S0 and S1 inputs | A stranger reads them by design (FD§5.3 S1) but they must not carry personal data of others | `R1`..`R3`, `THR-07` |
| Secrets and signing keys | Their compromise defeats other controls | S10.14 |
| Reviewer and admin authority | Capture changes rules, flags, bans and parameters | `THR-13`, `THR-23` |
| Availability and reachability | Members who cannot reach the host cannot join (`RISK-14`) | S10.15 |

### 10.11.2 Actors [D]

| Actor key | Capability assumed | Motive considered |
| --- | --- | --- |
| `network_observer` | Sees traffic between a member's device and the host (ISP, local network, state-level monitoring); may block or throttle | Identify or block participants |
| `host_provider` | Controls the machines, disks, snapshots and provider-level network logs the system runs on, and can be compelled | Commercial, or compelled |
| `external_attacker` | Internet reach, commodity tools, phishing | Theft, disruption, credit |
| `volunteer_malicious` | A valid member who runs cells | Free credit, harvesting inputs, attacking requesters or reviewers |
| `requester_malicious` | A valid member who submits jobs | Evade policy, inject, extract volunteers' data |
| `other_member` | Any member, sees only what the product shows | Curiosity, harassment, de-anonymization |
| `reviewer_insider` | `AdminUser` with the `reviewer` role | Error, bribery, coercion, capture |
| `operator_insider` | `AdminUser` with the `operator` role; deploy and database reach | Abuse of power, coercion |
| `authority` | Legal power in some jurisdiction over the operator, the host or a member | Obtain data, stop the project |
| `provider_service` | The AI service a volunteer uses (outside this system) | Account enforcement, data use |

### 10.11.3 Trust boundaries (text diagram) [D]

```
 member device (key pair, session token)
    |  TLS only, no third-party hosts                       <- network_observer sees this hop
    v
 edge / TLS terminator (optional adapter, S10.15)           <- sees plaintext requests and IPs if it terminates TLS
    |
    +--> app, member surface /v1/*        --> database (roles: app, ledger_append, readonly, migrate)
    +--> app, public surface /v1/public/*  --> cached aggregates only
    +--> admin origin /v1/admin/* (separate origin, WebAuthn, two-person actions)
 member device --human copy, Send, paste--> provider_service     <- OUTSIDE this system; never automated, never read
```

### 10.11.4 Priority order and residual-risk scale [D]

Priority when objectives conflict: (1) member safety, (2) ledger integrity, (3) integrity of verification, (4) confidentiality of S0 and S1 inputs, (5) availability. Reason: FD Principle 8 ("a growth tactic that endangers members loses"), FD§6.1 rank 5, FD Principle 11.

| Residual risk | Meaning | Required handling |
| --- | --- | --- |
| `low` | The control works unless there is a bug or an unrelated compromise; an `AC-safety-nn` case tests it | Monitor |
| `moderate` | A determined, resourced actor still partly succeeds; detection and a bounded loss exist | Alarm and a named owner |
| `high` | Cannot be reduced inside this design | Members are told in plain words (S10.13.7); the founders record acceptance (code `SEC`) as evidence on the G1 `LaunchGateItem`; without it G1 stays open |

## 10.12 Threat model

One row per threat. Columns follow prompt scope I: actor, goal, attack, impact, mitigation, residual risk (scale in S10.11.4). Parameters and events are named as in S0.*. Mitigations marked [A] are introduced by this file. [D]

| ID | Actor | Goal | Attack | Impact | Mitigation | Residual risk |
| --- | --- | --- | --- | --- | --- | --- |
| `THR-01` | `volunteer_malicious` | Credit without work | Forged results: fabricated paste-back, invented `cel_` or `lse_` ids, output not produced by a real run | Free credit, junk in deliverables, v rises | Server-issued ids; lease-bound 128-bit nonce stored as hash (S0.6.4); schema and size checks; automatic checks; hidden gold cells (`verify.gold_rate_g`) and audits with floor (`verify.audit_rate_floor`); duplicate and timing checks (`verify.duplicate_similarity_threshold`, `verify.timing_min_s`); blanket redundancy for the first `verify.new_donor_blanket_cells` cells | `moderate`: a human who really pastes a weaker model's answer passes any comparator that tolerates it; false-accept rate is an estimate [H] (S8.*) |
| `THR-02` | `volunteer_malicious`, `external_attacker` | Double credit or another member's cell | Replay of a submission, nonce reuse, lease race, submitting on another member's lease | Double mint or double transfer | One submission per (lease, nonce) with stored outcome; `Idempotency-Key` (S0.11.5); lease bound to `member_id`; `LEASE_CONFLICT`; natural idempotency in the ledger | `low`, if S5.* isolation is implemented and tested (`T-adv-nn`) |
| `THR-03` | `volunteer_malicious` | Maximum credit for minimum effort | Volume farming of low-effort accepted cells; repeated starter grants | Reserve drain; claims exceed capacity | `mint.per_member_daily_cap_credits`, `mint.monthly_cap_credits`, `ratelimit.member_leases_per_hour`, `ratelimit.member_submissions_per_hour`, trust-tier audit multipliers (`trust.audit_multiplier.*`), `grant.*` limits, expiry and cap K | `moderate`: a patient actor inside the caps earns credit that looks legitimate; loss is bounded by the caps, not removed |
| `THR-04` | `volunteer_malicious` (ring) | Pass audits and gold cells | Colluding donors share answers or audit each other | False accepts, inflated reputation | Audit and review assignment excludes members of the same invite tree and the same `Device` group [A]; random assignment; third execution on mismatch; hidden gold; sampling floor | `moderate`: collusion across unlinked sybils is not detectable by design |
| `THR-05` | `external_attacker` | Many accounts for starter grants or trust | Scripted identity creation (sybils) | Reserve drain, farmed trust | `grant.max_per_device`, `grant.max_per_invite_tree_per_day`, `grant.max_per_day`, `grant.required_verified_cells`, `ratelimit.device_new_members_per_day`, `ratelimit.ip_hash_new_members_per_day`, `ratelimit.invite_tree_new_members_per_day`; grants pause on an empty Reserve (FD§4.6); no fingerprinting beyond S10.* | `moderate`: IPs and devices are cheap to vary; `grant.max_per_day` times `grant.starter_credits` is the daily loss ceiling (formula, not a measurement) |
| `THR-06` | `volunteer_malicious` | Grow a tree of puppets | Mass invites, selling invites, vouching puppets | Farming at scale | `invite.max_active_per_member`, `invite.min_accepted_cells_to_issue`, `invite.tree_max_members`, `invite.tree_max_depth`, `invite.ttl_days`; a farming flag triggers tree review, never an automatic ban of the tree [D]; trees are never shown publicly | `moderate`: sold invites between real people look genuine |
| `THR-07` | `requester_malicious` | Get sensitive or prohibited work done | False declarations (`S2` or `S3` data declared `S1`; `P2` or `P3` declared `P0`); splitting a prohibited task across cells | Volunteers read others' personal data; policy breach | `R1`..`R10` as data; template-only prompts (`R4`); `screen.pii_action` = `reject`; `screen.max_urls_per_input` = 0; `screen.review_rate_new_requester` = 1.0; reports; bans; interface says "declared" | `high` for undetected lies: declarations cannot be disproved technically (FD§5.7 items 1 and 2) |
| `THR-08` | `requester_malicious` | Use volunteers to harm third parties | Inputs with prohibited content or text aimed at individuals (`R3`) | Harm to volunteers and third parties; legal exposure | `R3`; reviewer screening of inputs; report button on every card; takedown, job rejection and ban (S10.16); kill switches | `moderate`: screening is pattern-based, reviewers are fallible |
| `THR-09` | `requester_malicious` | Steer a volunteer's chat or reach its memory or connectors | Prompt injection in data slots; instructions to disclose memory, produce links or make the volunteer act | Exposure of volunteer account data; volunteer deceived | Template delimiters; screening for instruction patterns and links; volunteer advice (clean chat, memory off) via `adapter.clean_chat_hint_key`; a task may ask only copy, Send, return text (`R3`); outputs with links, code or requests of action become `submission.quarantined`; decline and report without penalty | `high`: reduces, does not remove (FD§5.5); depends on the volunteer's environment and on provider behavior [V] |
| `THR-10` | `volunteer_malicious` | Attack a requester or reviewer through output | Output with links, scripts, macros, spreadsheet formulas, phishing text | Requester or reviewer harm | Submitted content is never executed; quarantine (`screen.output_url_action` = `quarantine`); escaping on display; export neutralization (S10.12.1) | `moderate`: a requester who opens an export in a vulnerable external program is outside the platform |
| `THR-11` | any submitter | Execute code or spoof text inside our UIs | XSS, template injection, SQL injection, header or log injection, CSV formula injection, path traversal in `Upload` and `TermsCopy`, Unicode bidirectional and invisible-character spoofing in mixed Persian and English text | Reviewer or admin session theft; false display; data theft | Contextual escaping everywhere; untrusted text never inserted as markup; strict content security policy (S10.15.5); parameterized queries only; bearer tokens, no cookies, so no CSRF (S0.11.4); admin on a separate origin; bidirectional-control and invisible characters isolated or visibly marked on display; export cells starting with `=`, `+`, `-`, `@` are prefixed so they stay text; uploads by allowlisted type only, never served with a script-capable type | `low` to `moderate`: a browser or library zero-day defeats single layers; defense in depth only |
| `THR-12` | `operator_insider`, `external_attacker` with database reach | Change balances or history | Edit or delete ledger rows, forge entries, rewrite the hash chain, mutate lots | Unbacked credit; loss of trust | Append-only tables: the app role has no UPDATE or DELETE privilege on ledger tables; per-ledger hash chain (S0.6.4); continuous invariants (`ledger.invariant_check_interval_s`, `ledger.full_recompute_interval_s`); checkpoint every `ledger.checkpoint_interval_s`, signed with `secret.ledger_checkpoint_signing_key` and published on the public page and to at least one external mirror [V: where]; reversal needs `ledger.reversal_min_approvers`; separate database roles | `moderate`: whoever holds database superuser and the signing key can rewrite everything since the last mirrored checkpoint; detection window = `ledger.checkpoint_interval_s` |
| `THR-13` | `operator_insider` | Abuse power: mint, read members, favor friends, deanonymize | Direct database access; misuse of the admin tool; shipping modified code; disabling controls; editing logs | All of the other rows | `security.two_person_actions`; every action in `AdminAction`; passkeys; no admin screen shows IPs, e-mail or keys; parameter changes public (R10, FD Principle 5); secrets unreadable by humans (S10.14.3); deploys only from reviewed commits through CI; anyone can recompute invariants from the public page | `high` for a small team: whoever controls deployment controls the code and can ship a backdoor; two-person rules help only if the two are independent |
| `THR-14` | `external_attacker` | Take over a member account | Stolen or seized device, malware, malicious browser extension, stolen recovery key or session token, phishing | Impersonation, spending credit, reading history | Device-held key pair, private key not exported where the platform allows a non-extractable key [V: support on target phones]; hashed expiring sessions (`session.member_idle_ttl_s`); `identity.recovery_cooldown_s` (a recovered identity cannot start jobs or spend); `member.key_rotated` and `member.device_linked` shown to the member; no password exists | `high` if the device is compromised: device compromise is account compromise |
| `THR-15` | `external_attacker` | Take over an admin account | Phishing, session theft, XSS, compromised admin device | Control of rules, ledger tools, bans | WebAuthn passkeys (bound to the admin origin), separate origin and session store, `session.admin_idle_ttl_s`, `session.admin_abs_ttl_s`, `ratelimit.admin_api_rpm`, two-person actions, no shared password | `moderate`: stolen unlocked device with a passkey; coerced admin |
| `THR-16` | `external_attacker` | Hijack an identity through recovery | Guessing or stealing the recovery key; abusing recovery start; mass attempts | Takeover, harassment | `identity.recovery_key_bits` >= 128; `ratelimit.recovery_attempts_per_day`; `identity.recovery_max_per_90d`; `identity.recovery_cooldown_s`; no e-mail-only recovery [A] | `moderate`: a recovery key kept in a synced note is only as safe as that note |
| `THR-17` | `network_observer` | Learn who participates; block access | DNS, SNI, destination IP, timing and volume; deep packet inspection; blocking | Member identified as a participant; access cut | HTTPS only with HSTS [V: header set at the edge]; no third-party hosts so no extra names to observe; no tracking; encrypted client hello where the host supports it [V]; the platform is not a privacy network and offers no circumvention (S10.15.1) | `high`: an observer sees that a device talks to the host's addresses (S10.13.3) |
| `THR-18` | `host_provider`, `authority` acting through it | See everything the app handles | Access to machines, disks, snapshots, memory, TLS plaintext, provider network logs | Exposure of member keys, activity, in-flight cell text, IPs | Minimal data (S10.13.2); no raw IP stored by the app; daily-rolling `secret.ip_hash_key`; short retention; encryption at rest [V per host]; backups encrypted under `secret.backup_encryption_key` held off-host; host chosen and its logging settings decided as a G1 item [V]; ports so the system can move (S10.15.2) | `high`: a host that terminates TLS and logs sees IPs and timing whatever the app does |
| `THR-19` | `host_provider`, `network_observer`, `other_member`, analyst | Link a pseudonym to a person | Timing correlation between network time and ledger or accept times; stylometry; e-mail if supplied; small-cohort aggregates; public ledger patterns; team or place labels; shared provider accounts | Member exposed | Day-granular ledger timestamps for member legs (`ledger.member_timestamp_granularity_s`, `ISS-104`); `vol_` handles never shown to requesters; handle key rotated; `analytics.min_cohort_k`; `team.min_public_members`; `public.location_display` = `never`; e-mail optional and encrypted; share cards without personal data; no IP-derived place or time zone (S0.6.2) | `high` against an observer who sees both ends: timing correlation cannot be removed [H] |
| `THR-20` | `authority` | Compel data or assistance | Subpoena, order, seizure of servers or devices, pressure on operator or host | Disclosure of whatever exists; harm to members | Little exists (exact table in S10.13.5); retention limits; two-person `disclosure.release`; counsel review [V]; `AdminAction` log of every disclosure; closure deletes `member_bound` rows; no content in logs | `high`: what exists can be produced; refusal of a lawful order is not available to the platform [V] |
| `THR-21` | `authority`, thief | Read a member's device | Inspection or seizure of a phone or browser profile | Recent activity and key exposed | Minimal local data; "forget this device" action; neutral page titles; pasted text kept only until acknowledged; recovery key shown once (S10.13.4) | `high`: an unlocked device and the provider chat history are outside our control |
| `THR-22` | `external_attacker` | Make the service unavailable or waste capacity | Volumetric flood; slow clients; lease hoarding (lease cells and let them expire); job flooding; oversized uploads; expensive queries; report flooding | Missed windows, lost trust | `ratelimit.*` keyed by member id, admin id or IP hash; `lease.max_active_per_member`; `api.max_body_bytes`, `job.max_upload_bytes`, `api.request_timeout_s`; escrow cost; `admission.max_concurrent_jobs_per_member`; cursor pagination; kill switches; cacheable public surface; an optional DoS-absorbing front only as a replaceable adapter (S10.15.2) | `high` for volumetric attacks on a small host: a small host cannot absorb them |
| `THR-23` | `reviewer_insider` | Approve harm or block the legitimate | One reviewer approves a bad template or records a false `FlagAnswer`; favors a requester; account taken over | Volunteers exposed; terms violated | Second reviewer for new templates (`template.min_reviewers_new`, distinct from the author); `service.min_approvers` (raising it to 2 is an owner decision [A]); `AdminAction`; published criteria; `TermsCopy` bytes and hash so flags are checkable; conflict-of-interest declaration; re-review of a sample of approved items by a different reviewer at each rotation cycle (S10.16.8); appeals | `high` in Phase 1: the founders are the reviewers (FD§5.7 item 10) |
| `THR-24` | `reviewer_insider`, template author | Smuggle a malicious template | Links, exfiltration instructions, hidden text or bidirectional tricks in a prompt body | Volunteers harmed at scale | Diff review with detection of bidirectional and invisible characters; template lint: no URLs, nothing beyond copy, Send, return text (`R3`); `TemplateVersion` immutable once approved; `kill.template.<tpl_id>` | `moderate`: semantic traps in plain text |
| `THR-25` | `reviewer_insider` | Wrong service flags | `yes` recorded where the terms say no; stale `TermsCopy` | Volunteers' accounts at risk | Dated `FlagAnswer` pointing at a `TermsCopy`; `service.review_max_age_days`; `unknown` is `no`; flag changes in the public change log | `moderate`: our reading of terms can be wrong [V counsel] |
| `THR-26` | `external_attacker` | Run code in our build or runtime, steal secrets | Malicious or typosquatted dependency, compromised CI action, install scripts; the panel's cell acceptance commands run with `shell=True` and network access (panel-review §4.5 item 9) [V] | Secret theft, backdoor | Pinned dependencies with lockfile hashes; install scripts disabled; minimal dependency list; CI jobs that run untrusted code receive no secrets; CI cannot read runtime secrets | `moderate` |
| `THR-27` | any holder of a leaked secret | Use a leaked secret | Secrets in repo, logs, URLs, chat transcripts, browser storage (the panel's `bp_owner_key`, panel-review §4.5 item 5 [V]) | Takeover of panel, repository or infrastructure | Inventory and rotation (S10.14); secret scanning before commit and in CI; log redaction; no secret in a URL; rotation of all legacy secrets before exposure | `moderate`: human paste mistakes recur; rotation limits the window |
| `THR-28` | `external_attacker` | Steal recovery keys or sessions | Look-alike site, fake recovery or admin page | Takeover | One canonical domain set published on the parameter page [V]; the recovery key is requested on one route only; copy tells members to check the domain; passkeys are origin-bound; no message asks for a key | `high`: a member who types a recovery key where asked is exposed |
| `THR-29` | `other_member`, `volunteer_malicious` | Silence or harm others through moderation | Report brigading; false reports to trigger `template.autopause_report_count`; reports to get members banned | Template denial of service; unfair bans | Autopause counts only distinct reporters at or above `template.autopause_min_reporter_tier` (`ISS-106`); autopause is a pause, not a verdict; `report.max_per_member_per_day`; humans decide; appeals; repeated false reports lead to restriction | `moderate` |
| `THR-30` | `volunteer_malicious` | Harvest requesters' inputs | Lease many cells of one job and rebuild the input; keep copies | S1 data disclosed | S0 and S1 only, and the requester accepts a stranger reads it (FD§5.3); small envelope (`cell.envelope.max_input_chars`); proposed cap on one member's share of a job (`ISS-105`) | `moderate`: accepted by FD§5.3 for `S1` |
| `THR-31` | `provider_service` | Enforce terms, observe content | Ties prompt text to the volunteer's account; may suspend it; may train on chats; may share with an authority | Volunteer account loss or exposure | Service Registry review before use (S7.*); `info.provider_trains_on_chats` and `info.memory_or_connectors_risk` shown as advice; S0 and S1 only; "declared" wording | `high`: outside our control; the volunteer carries it, and the notice says so (S10.13.7) |
| `THR-32` | `external_attacker`, `operator_insider` | Destroy or hold data hostage | Ransom, destructive access, deletion of backups | Loss of the ledger | Backups encrypted, versioned, deletable only through a two-person action; restore drill (`BM9`); hash-chain verification after restore (S10.15.3) | `moderate` |

### 10.12.1 Controls that several rows depend on [D]

1. **Output handling.** Submitted text is data in every context: it is stored as bytes plus hash, never interpreted, never `eval`ed, never rendered as markup. Display escaping is applied at render time for the target context (HTML text, attribute, URL, CSV cell, log line). Text containing bidirectional controls or invisible characters is shown with explicit isolation and a visible marker (needed for correct Persian and for spoof resistance).
2. **Export neutralization.** Exports to CSV or spreadsheets prefix any cell that starts with `=`, `+`, `-` or `@` with a single quote; exports of manifests carry no `vol_` handle.
3. **Admin surface.** `/v1/admin/*` is served only from the admin origin; the member origin does not route it; a member token on it is `AUTH_INVALID` and counted (S0.11.4).
4. **Alarm path.** `ledger.invariant_violated`, `member.restricted` bursts and secret-scan hits raise an `Alarm`; the alarm destination token is itself an inventoried secret (S10.14.2).

### 10.12.2 Risk acceptance and upkeep [D]

- Each row with residual risk `high` is accepted, row by row, in a recorded founders' decision (code `SEC`) attached as evidence to the G1 `LaunchGateItem` `g1.threat_model_accepted` (item key proposed, S10.14.5).
- The table is re-read, and new rows are added, at every secret rotation cycle (`security.secret_rotation_days`), before any new public surface or `ff.*` flag is enabled, after any incident, and when a new data field is proposed (S10.13.8).
- A mitigation that names a parameter holds only while the parameter stays inside the range its row implies; a loosening change to such a parameter triggers a threat-model re-read (S10.13.8).

## 10.13 Member safety design

Context: some members may be in Iran, where participation may carry personal risk (`RISK-05`). The design promises minimization, never anonymity (FD Principle 8). [P]

### 10.13.1 Safety rules [D]

Numbered for reference as "S10.13.1 item n".

1. **Pseudonymity by default.** Identity is a key pair made on the device. No name, phone number, social login or government identity is requested anywhere. E-mail is optional (`identity.email_optional` = true) and never a condition of any feature (FD§3.2).
2. **Minimal collection.** Only the data in S10.13.2 exists. A new field, event or log line first passes S10.13.8.
3. **No location.** The server never derives or stores a place from an IP address, time zone, locale or any API (S0.6.2); the client never requests geolocation permission; `public.location_display` = `never` by default (FD§6.1 rank 5). With `opt_in`, only a free-text label the member typed is shown, unverified, with a warning, and never for a group below `team.min_public_members`.
4. **No fingerprinting.** A `Device` is a random client-generated token stored as a keyed hash (`secret.device_hash_key`, [A]). No canvas, audio, font-enumeration or hardware identifiers are read. The request log keeps no `User-Agent`. Constraint on S10.*.
5. **No third-party requests** from any page, script, font or image (S10.15.5).
6. **No raw IP stored** (`retention.raw_ip_stored` = false). Rate-limit counters use the daily-rolling `secret.ip_hash_key` (S10.14.4) and hold no member id.
7. **Retention is enforced by jobs, not by intent.** Every retention class in S0.7 has a sweep; a sweep that falls behind raises an alarm (`hamyar_retention_overdue_rows_total` > 0).
8. **Closure deletes.** On `member.closed` the sweep (interval `retention.sweep_interval_s`) deletes or opaques all `member_bound` rows; the ledger keeps only the opaque `mem_` id and day-granular times (`ISS-104`). Backups lose the data within `retention.backup_days`.
9. **No content in logs.** Logs and metrics never contain submitted text, cell input or output, or any free text. Allowed fields: UTC minute, method, route template, status, duration, `request_id`, `principal_type`.
10. **Admins see less than the database holds.** No admin screen shows IPs, e-mail, device hashes or public keys. The e-mail ciphertext is reachable only through the two-person disclosure path (S10.13.5).
11. **Public surfaces are aggregates** with small-cohort suppression (`analytics.min_cohort_k`); per-member rows are never public.
12. **Plain words.** Copy never says anonymous, untraceable, safe or guaranteed (Persian equivalents included, marked `needs_human_and_legal_review`).

### 10.13.2 Data inventory (everything that is collected) [D]

| Data item | Stored in | Why | Retention | Identifies a person by itself? | Who can read it |
| --- | --- | --- | --- | --- | --- |
| Member public key(s) | `member_keys` | Verify signatures | `member_bound` | No | System only |
| `mem_` id, `status`, `trust_tier`, creation day | `members` | Account | `member_bound` | No | Admins see id, status, tier only |
| Optional e-mail, only if the member supplies it | Ciphertext under `secret.email_encryption_key` [A] | Recovery notices if the identity file uses them | Deleted at `member.closed` | Yes, strongly, if supplied | System; decrypted only via S10.13.5 |
| `Device` keyed hash | `devices` | Limits, `grant.max_per_device`, linking | `short` | No | System only |
| Session token hash | `sessions` | Authentication | `retention.session_days` | No | System only |
| IP-hash counters (key hash, window, count) | Rate-limit store | Abuse limits | `retention.ip_hash_ttl_days`, key destroyed after | No once the key is destroyed; within the window a key holder can test a candidate IP | System only |
| Cell input and output text, uploads | `cells`, `submissions`, `uploads` | The work | Payload purged `retention.job_payload_days` after the job is terminal | Not by policy (S0 and S1), but a requester may have typed personal text | Leasing volunteer; reviewers when flagged or reviewed; the requester (own job) |
| Hashes and manifests (with `vol_` handle) | `manifests`, `submissions` | Provenance (FD§5.6) | `job_bound`, hashes stay | No; handle maps to a member only with its key version | Requester sees the manifest without handle; admins see the handle |
| Ledger entries and lots | `ledger_entries`, `credit_lots` | Credit | `permanent` | A pseudonymous activity trace per `mem_` account | Admins; public page shows aggregates only (S10.13.6) |
| Reports and appeals | `reports`, `appeals` | Moderation | `retention.moderation_days` after resolution, then counts | Pseudonymous ids only | Reviewers |
| Admin action log | `admin_actions` | Accountability | `permanent` | Contains `mem_` and `adm_` ids, no free personal text (reason codes only) | Operators and reviewers |
| Request and ops logs | Log sink | Debugging | `retention.request_log_days`, `retention.ops_log_days` | No (fields in item 9) | Operators |
| Analytics events | `events` | FD§9 measures | `retention.event_raw_days` | Member reference is `HMAC-SHA-256(secret.analytics_key[version], member_id)` [A] | Operators; aggregates only for publication |
| Backups | Blob store | Recovery | `retention.backup_days` | Contains all of the above | Key custodians (S10.14.3) |
| `TermsCopy` bytes, `GoldCell` answers | Blob store, `gold_cells` | Evidence, verification | `permanent` | No | Reviewers |

**Never held by the platform** [D]: raw IPs, names, phone numbers, locations, hardware or browser fingerprints, plaintext e-mail, any provider credential or session, any chat page or its text (ground rule 3), message bodies in logs, private keys, recovery keys (the server keeps only a verifier, identity file).

### 10.13.3 What each observer can see [D]

| Observer | Can see | Cannot see | What the platform controls | What it cannot change |
| --- | --- | --- | --- | --- |
| `network_observer` (passive) | Member's IP and the host's IP; DNS lookups unless encrypted; the host name in the TLS handshake unless encrypted client hello is used [V]; timing and volume, from which screens may be inferred | Paths, headers, tokens, bodies, cell text (TLS), unless a device or certificate authority is compromised | HTTPS only, HSTS [V], no third-party hosts, neutral content, no tracking | That a device contacts the host at all |
| `network_observer` (active) | The above, plus blocking, throttling, resetting, injection against users who click through certificate warnings | Same | Copy tells members never to bypass a certificate warning | Blocking. No circumvention is offered (S10.15.1) |
| `host_provider` | Whatever the layout gives it: at least disks, snapshots, memory, the secrets handed to the process, and provider-level network logs; at a TLS-terminating edge, plaintext requests and IPs [V per host] | Member private keys and recovery keys (never sent); backups' contents without `secret.backup_encryption_key` | Collects nothing beyond S10.13.2; chooses a host and logging settings by G1 decision | Provider-level logs and legal duties of the provider |
| Operators (`operator_insider`) | Admin-tool views, `AdminAction`, database through role-separated access | IPs and e-mail through the tool; secret values (S10.14.3) | Two-person actions; public change log | What a deployer can do by changing code (`THR-13`) |
| `other_member` | Own data; public aggregates; a team's total if the team is public | Any other member's id, handle, activity or place | `vol_` handle never shown to requesters or members | Writing style and what members say about themselves |
| `requester_malicious` and honest requesters | Own jobs, results, manifest without handle | Which member did a cell | Handle withheld; key rotated | Stylometry of outputs |
| Public visitor | Counter, public ledger aggregates, parameters, change log, milestones | Per-member rows; trees; places | Suppression below `analytics.min_cohort_k`; `public.ledger_lag_s` | Inference from small or timed aggregates beyond the suppression |
| `provider_service` | The prompt and the volunteer's reply, tied to the volunteer's own account | Nothing is sent to it by us; no automation exists | Template and registry review | Everything the volunteer's own account exposes (`THR-31`) |

### 10.13.4 Device-side data and device seizure [D]

| On the device | Where | Rule |
| --- | --- | --- |
| Private key | Non-extractable key handle where the platform supports it [V: target phones]; otherwise the weakest case is stated to the member | Never sent, never logged, never copied to the clipboard by the app |
| Session token | Browser storage, expires by `session.member_idle_ttl_s` | Revocable server-side by deleting its hash |
| Recovery key | Shown once at creation; not stored by the app afterwards | No automatic clipboard write; the member is told to store it offline |
| Pasted result before acknowledgment | Memory only; if the network drops, kept until the retry succeeds, then cleared | Cleared by "forget this device" |
| Preferences (locale, digits, calendar) | Browser storage | Harmless; no identifiers |
| History, balances | Not cached beyond the open screen | Fetched from the server |

**"Forget this device"** is a visible action: it deletes all local data above, revokes the session (`sessions` hash removed) and removes the `Device` record. The page title, icon and any notification text are neutral and carry no political or sensitive words. The design cannot protect an unlocked or already-inspected device or the volunteer's chat history at the provider (`THR-21`).

### 10.13.5 Subpoena, seizure and compelled disclosure [D]

All legal points here are [V] for counsel in the operator's jurisdiction (measurement code `CNS`); this section says only what technically exists and what the process is.

**What exists to disclose, by what the requesting party already holds**

| The party holds | What exists | What does not exist |
| --- | --- | --- |
| A real name | Nothing maps a name to a member | Any name field |
| An e-mail address | Only if that member supplied one: ciphertext, decryptable by the operators, giving a `mem_` id | Plaintext e-mail anywhere |
| An IP address and time | The app stores none. IP-hash counters exist for at most `retention.ip_hash_ttl_days` day(s); a holder of that day's key can test whether an IP was seen, but counters carry no member id; after the key is destroyed they cannot be tested at all. Provider-level and network-layer logs are outside the app [V per host] | Raw IPs in the app, an IP-to-member join |
| A `mem_` id (learned from a seized device) | `members` row; public keys; status and tier history; ledger activity at day granularity; accepted-cell counts; reports and appeals inside retention; `AdminAction` rows about it; submission hashes; cell text only inside `retention.job_payload_days` of the job's terminal state | Locations, device hardware, anything about the volunteer's provider account |
| A piece of output text ("who produced this?") | A `vol_` handle in the manifest; it maps to a `mem_` id only while the key version `secret.volunteer_handle_key[version]` still exists | The mapping after that key version is destroyed |
| A requester | Job records, declared metadata, uploads and results inside `retention.job_payload_days` | Provider-side data |
| A device | Keyed device hash, useless without the device's token | Hardware ids |
| Backups | The same as above for up to `retention.backup_days`, encrypted | Plaintext backups |

**Handling procedure** (no one discloses on their own initiative)

```
on legal_request(r):
  record AdminAction{kind: disclosure.received, ref: r.request_id, scope: category only}   # no content
  route r to counsel [V]                       # validity, jurisdiction, scope, gag terms
  scope := narrowest set of rows the order names (by 10.13.5 table)
  if scope is empty: respond that nothing exists, per counsel
  require two distinct admins approve action disclosure.release   # security.two_person_actions
  produce export(scope) with no extra fields; hash and store the export bytes' hash in AdminAction
  notify the affected member only if counsel confirms it is lawful and safe [V]
  count it in the aggregate disclosure total published each rotation cycle if lawful [V]
```

The platform adds no backdoor, no unlogged access path, no identity collection in response to a request without an owner decision, and promises no gag-order behavior. It specifies no warrant canary; whether one is lawful or wise is [V].

**Seizure of a server or host.** Assume disk and possibly memory are taken. Obtainable: the database, secrets in the process, and the logs of S10.13.2 (no IPs, no content). Not obtainable without a separate key held off-host: backups. Response: engage `kill.all_new_jobs` and `kill.all_minting`, revoke sessions, rotate every secret (S10.14.6). Data already taken cannot be recalled.

### 10.13.6 Identity, location and public-surface rules [D]

| Surface | Rule | Source |
| --- | --- | --- |
| Identity | No mandatory identity field anywhere; display name optional, generated by default | FD Principle 8 |
| Public ledger page | Aggregates by entry type and day; never `lac_` or `mem_` ids; trails the ledger by `public.ledger_lag_s`; checkpoints published (`THR-12`) | `ISS-104` |
| Live counter | Verified cells and members active today, suppressed when a cohort is below `analytics.min_cohort_k` | FD§6.2 V2 |
| Share card | Cell count and badge only; no handle, no timestamp finer than a week, no place | FD§6.2 V3 |
| Teams | Public only at `team.min_public_members` or more; totals only, no member rows; leaving is always possible | FD§6.2 V4 |
| Place or affiliation | Never collected; `opt_in` shows a typed, unverified label with a warning | FD§6.1 rank 5 |
| Invite trees | Never public; visible only to reviewers during farming review | `THR-06` |

### 10.13.7 What the platform cannot promise [D]

Each item has a copy key (`copy.privacy.cannot_promise.nn`) written in `fa` and `en` by S11.* and marked `needs_human_and_legal_review`; items 1 to 14 appear together in the first-run notice.

1. Anonymity. The design minimizes data; it does not make anyone anonymous (FD Principle 8).
2. That a network provider, employer or government cannot see that a device connects to this service.
3. That the host or the operators cannot see what the system handles; the ways they can are listed in S10.13.3.
4. That data cannot be compelled from the operator, the host or the member; what exists in S10.13.5 could be handed over.
5. The safety of the member's device: a lost, seized or infected device exposes the identity on it.
6. Deletion from other places: the volunteer's chat history at the provider, a requester's downloaded copies, openly licensed outputs ("downstream use uncontrolled"), and backups for up to `retention.backup_days`.
7. That a service's terms allow the member's use, or that the member's account will not be limited or suspended. Reviews are recorded; their result is [V].
8. That requesters follow what they declared about purpose, license and sensitivity ("declared", FD§5.7 item 2).
9. That cell text is harmless: prompt injection can still affect the volunteer's chat (FD§5.5).
10. That participation is lawful where the member lives; sanctions, terms and local law differ and this is not advice [V].
11. Availability: reachability from the member's location, uptime, or completion within a quoted window (FD Principle 10).
12. That timing patterns cannot link activity to a person.
13. That credit is money, property or an entitlement (FD§4.1).
14. That the code and the people running it are free of mistakes or pressure.

The member-facing notice (FD§8.3 G1) is drafted with someone qualified to advise, and that review is G1 evidence (`g1.member_notice_reviewed`) [V].

### 10.13.8 Safety review for new data, features and parameters [D]

Before any new field, event, log line, `ff.*` flag turning on, or change to a `retention.*`, `public.*`, `analytics.*` or `security.*` parameter takes effect, a reviewer answers the table. One "yes" in the fail column rejects the change (FD Principle 8).

| Question | Fail if |
| --- | --- |
| Does it collect, infer or display location, identity or contacts? | Yes |
| Does it add a request to a host the project does not run? | Yes |
| Does it lengthen retention or add a copy of data outside the sweep? | Yes |
| Can a small cohort or a time pattern identify a member? | Yes, unsuppressed |
| Does it show one pseudonym's activity to another member? | Yes |
| If it fails or leaks, could a member come to harm? | Yes, without a stated mitigation |

The outcome is an `AdminAction` (`safety_review`: `passed` or `rejected`). A change that loosens privacy (a larger `retention.*` value, a wider `public.*` setting) is a `loosen` change: public change-log entry, `change.notice_days_default` notice, second `operator` approval (S0.10.3). A tightening change takes effect at once (R10 applies by analogy).

## 10.14 Secrets management

### 10.14.1 Principles [D]

1. A secret exists only in the host secret store behind `SecretsPort` (S10.15.2) and in the memory of the process that needs it. Never in the repository, the database, the `Parameter` table, a log, a URL, a client bundle or a chat transcript (S0.10.1 reserves `secret.<name>` for this).
2. No human reads a secret value after creation. Access to a value is an `AdminAction` of kind `secret.emergency_access`, a two-person action with expiry `security.emergency_access_ttl_s`.
3. Every secret has an owner role, a version, a rotation cadence and a compromise procedure. A secret without all four is not allowed to exist.
4. Secrets are scoped to the smallest component that needs them (S10.14.3).
5. Statements about the four existing secrets come from panel-review §4 (static reading, nothing executed) and stay [V].

### 10.14.2 Inventory [D]

**A. Existing secrets of the panel repo** (names are the panel's environment variable names; spec names are `secret.legacy_*`). None of them authenticates a Hamyar member or admin: members use key pairs and admins use WebAuthn (S0.6.4). They stay only while the panel remains in use as build tooling [V].

| Spec name (env name) | What it protects, per panel-review | Known weaknesses seen in code (all [V]) | Cadence | On compromise |
| --- | --- | --- | --- | --- |
| `secret.legacy_panel_token` (`PANEL_TOKEN`) | Panel login password and the HMAC key of the stateless 12-hour cookie (§4.1) | Shared by all users; cookie not revocable except by changing the token; login limit read-then-write on KV (§4.5 items 1 to 3) | `security.secret_rotation_days`; rotating revokes every cookie at once | Rotate now |
| `secret.legacy_admin_token` (`ADMIN_TOKEN`) | Owner key for release, takeover, publish-plan and steward actions (§4.2) | May persist in browser storage as `bp_owner_key`; legacy steward prompt asks it be pasted into a chat; no failure counter (§4.5 items 4 to 6) | As above; also rotated if it was ever pasted into a transcript, URL or browser storage | Rotate now; clear stored copies |
| `secret.legacy_github_token` (`GITHUB_TOKEN`) | Every GitHub call of the Worker (§4.3) | Scope not determinable; one token, owner-wide `ALLOWED_REPOS` (§4.5 item 8); the Worker pushes to `main` (§2.1) | As above | Revoke at GitHub, issue a narrower replacement, review GitHub's audit log for use [V] |
| `secret.legacy_mcp_auth_token` (`MCP_AUTH_TOKEN`) | Password of the connector consent page; every consenting client becomes one `owner` principal (§4.4, §4.5 item 7) | Dynamic client registration is on; limiter on `/authorize` not seen; issued grants outlive the token (§9) | As above | Rotate and invalidate all issued grants (S10.14.5) |
| `secret.legacy_ext_token` (`EXT_TOKEN`) | Retired browser-extension endpoints; off when unset (§4, overview) | A fifth secret the README does not list | Unset it | Unset it |

**B. Hamyar runtime secrets** (new)

| Spec name | Purpose | Form and length | Held by | Cadence and overlap |
| --- | --- | --- | --- | --- |
| `secret.volunteer_handle_key[version]` | `vol_` handle HMAC (S0.6.4) | 256-bit random | App, ledger and provenance code | `security.secret_rotation_days`; no overlap needed (new handles use the new version); a retired version is destroyed `retention.job_payload_days` days after retirement, which unlinks old handles by design |
| `secret.ip_hash_key[version]` | Rate-limit counters (S0.6.4) | 256-bit random | Edge or app rate limiter | One version per UTC day; a version is destroyed `retention.ip_hash_ttl_days` x 86,400 s after its day ends |
| `secret.device_hash_key[version]` | `Device` keyed hash [A] | 256-bit random | Identity code | `security.secret_rotation_days`; old version kept until its devices age out (`short`) |
| `secret.analytics_key[version]` | Member reference in `events` [A] | 256-bit random | Metrics pipeline | Rotated per phase (week-2 and week-4 return need stable references); destroyed `retention.event_raw_days` after its last event |
| `secret.cursor_mac_key[version]` | Pagination cursor MAC (S0.11.6) | 256-bit random | App | `security.secret_rotation_days`; overlap `api.cursor_ttl_s` |
| `secret.ledger_checkpoint_signing_key` | Signs the daily checkpoint hash (S6.*) | Ed25519 key pair [A] | Checkpoint job only | `security.secret_rotation_days`; the new public key is announced in a `ChangeLogEntry` signed by the old key; old public keys stay published |
| `secret.backup_encryption_key` | Encrypts backups | 256-bit random data key, wrapped by a key split between two custodians | Backup job (data key); custodians (wrapping) | `security.secret_rotation_days` for new backups; an old key lives until the last backup it protects expires (`retention.backup_days`) |
| `secret.email_encryption_key` | Optional e-mail ciphertext [A] | 256-bit random | Identity code | `security.secret_rotation_days` with re-encryption of rows |
| `secret.db_credentials.<role>` | Roles `app`, `ledger_append`, `readonly`, `migrate`, `backup` | Random, per role | Only the component using the role | `security.secret_rotation_days` |
| `secret.blob_credentials` | Blob store access | Provider-specific | Blob adapter | `security.secret_rotation_days` |
| `secret.mail_credentials` | Optional mail sending | Provider-specific | Mail adapter (off if unused) | `security.secret_rotation_days` |
| `secret.alert_destination_token` | Alarm delivery | Provider-specific | Alerting job | `security.secret_rotation_days` |
| `secret.deploy_credentials` | CI deploy; never readable by runtime | Provider-specific | CI deploy job only | `security.secret_rotation_days` |
| `secret.tls_private_key` | TLS at the terminator | Provider-specific | TLS terminator | At each certificate renewal [V: CA and host rules] |

**C. Deliberately no key** [D]: session tokens, lease nonces and idempotency keys are CSPRNG values stored as SHA-256 hashes (S0.6.4), so there is no nonce key or pepper; the question is recorded here so it is not reopened without a threat-model change. WebAuthn gives the server public keys only.

**D. Never held by the platform** [D]: member private keys, member recovery keys, any provider credential or session (ground rule 3).

### 10.14.3 Storage and access [D]

| Rule | Detail |
| --- | --- |
| Store | `SecretsPort` backed by the chosen host's secret facility, or by an operator-run store that meets the port contract; secrets injected at process start or fetched on demand with a short cache |
| Component scope | A component receives only the secrets in the "Held by" column of S10.14.2. The checkpoint job cannot read database credentials of other roles; CI cannot read runtime secrets; the member origin never holds admin-only material |
| Database roles | `app` (no UPDATE or DELETE on ledger tables), `ledger_append` (INSERT only on ledger tables), `readonly` (analytics, aggregates), `migrate` (schema, used only by deploys), `backup` (read, no write) |
| Humans | No role reads values. The only path is `secret.emergency_access`, expiring after `security.emergency_access_ttl_s`, with an `AdminAction` entry and an `Alarm` |
| Backup key custodians | Two named people each hold half of the wrapping key; neither alone can decrypt a backup |
| Admin tool | Shows secret names, versions, created and rotated times, never values |

### 10.14.4 Rotation [D]

**Cadence.** Every secret rotates at most `security.secret_rotation_days` (initial configurable default 90) after creation, except where S10.14.2 gives a shorter rule (`secret.ip_hash_key` daily). Rotation is a calendar item owned by the `operator` role; a missed rotation raises an `Alarm` (`hamyar_secret_rotation_overdue_total`). Each rotation cycle also includes an access review of `AdminUser` accounts and the threat-model re-read (S10.12.2).

**Procedure** (generic; each secret's "overlap" is in S10.14.2)

```
rotate(secret):
  assert no incident open that needs a different order
  v_new := create version n+1 in SecretsPort (CSPRNG, length per table)
  mark v_new as "write"; keep v_old as "verify only" for the overlap window
  deploy; run the rotation canary (a request signed or hashed under v_new succeeds, one under a wrong key fails)
  after the overlap window: mark v_old "retired"; destroy it when its destroy rule (S10.14.2) allows
  write AdminAction{kind: secret.rotated, secret: name, from: n, to: n+1}   # never the value
  if the secret has a public part (signing key): publish the new public key in a ChangeLogEntry
```

**Legacy secrets: exact steps** (all [V]; the panel has not been run by the author of this spec)

| Secret | Steps | Verification |
| --- | --- | --- |
| `PANEL_TOKEN` | Generate a new random value; set it in the Worker's secret store; redeploy | An old cookie and the old password are refused; the new password works (every cookie ends, because the cookie is signed with this token) |
| `ADMIN_TOKEN` | Generate; set; redeploy; clear every `bp_owner_key` in browsers that used the panel; treat any copy that reached a chat transcript, a URL or a log as exposed | The old value is refused by release, takeover and publish-plan; the new value works |
| `GITHUB_TOKEN` | Create a replacement with the narrowest scope that works [V: scope is not determinable from code]; set it; redeploy; revoke the old token at GitHub; narrow `ALLOWED_REPOS` to the needed repositories; confirm whether `main` is branch-protected | Old token returns an authentication error; Worker calls succeed; GitHub's audit log shows no unexpected use [V] |
| `MCP_AUTH_TOKEN` | Generate; set; redeploy; invalidate every issued OAuth grant and registered client, by replacing the KV namespace the connector library uses (its key layout was not read [V]); re-consent from the owner's own client only | Old password refused; an old grant is refused; the owner's new consent works |
| `EXT_TOKEN` | Unset the secret so the legacy endpoints answer 404 | Endpoint returns 404 |

### 10.14.5 Rotate before any public exposure, and the launch-gate items [D]

**Rule.** All existing secrets (`secret.legacy_*`) are rotated before any public exposure. `security.rotate_before_public_exposure` = true is a constant (S0.10.6). "Public exposure" is the earliest of: (a) `launch.members_may_join` becomes true; (b) `/v1/public/*` or the panel's `/panel/*` is reachable by anyone outside the founders; (c) the repository holding the panel or this spec becomes public; (d) any non-founder receives any credential. The rotation must be dated after the last moment the old value could have been seen by anyone else (a transcript, a URL, browser storage, a screen share) and recorded by `AdminAction` (`secret.rotated`).

**Launch-gate items** contributed by this file. Item keys and the gate assignment are proposed [A] for S14.*, which owns `LaunchGateItem`. Evidence never contains a secret value. Sign-off needs `launch.min_signoffs` distinct admins.

| Proposed item key | Gate | Evidence required | Test |
| --- | --- | --- | --- |
| `g1.secrets_rotated` | G1 (always required, S0.10.6 `launch.required_gate_ids`) | One `secret.rotated` record per `secret.legacy_*`, each dated before the exposure event, plus the verification result of S10.14.4 | `AC-safety-05` |
| `g1.secrets_inventory_complete` | G1 | S10.14.2 matches the deployed `SecretsPort` listing, no extra names | `AC-safety-06` |
| `g1.no_raw_ip_audit` | G1 | Audit of storage and logs finding no raw IP in the app; statement of host-level logging [V] | `AC-safety-01` |
| `g1.retention_jobs_verified` | G1 | Each sweep ran on synthetic data and removed what S10.13.2 states | `AC-safety-03` |
| `g1.disclosure_runbook_reviewed` | G1 | S10.13.5 reviewed by counsel [V] | review record |
| `g1.member_notice_reviewed` | G1 | The notice of S10.13.7 reviewed by someone qualified to advise [V] | review record |
| `g1.threat_model_accepted` | G1 | Founders' acceptance of every `high` row (S10.12.2) | review record |
| `g1.abuse_contact_published` | G1 | `report.external_contact` set and shown on the public pages | `AC-safety-12` |
| `g4.secret_handling_audited` | G4 | The audit FD§8.3 G4 asks for, covering panel-review §4.5 items 1 to 15 | review record |
| `g2.reachability_recorded` | G2 | Reachability evidence of S10.15.4 | S10.15.4 |

While `g1.secrets_rotated` is open, `launch.members_may_join` refuses to turn on (`LAUNCH_GATE_CLOSED`).

### 10.14.6 Compromise response [D]

```
on suspected_compromise(secret or class):
  open an incident; engage kill.all_new_jobs (and kill.all_minting if the ledger path is involved)
  revoke sessions that the secret could have forged or read (member, admin, or panel cookies)
  rotate(secret) immediately; for a class (host seizure) rotate every secret in S10.14.2
  for secret.ledger_checkpoint_signing_key: publish a signed ChangeLogEntry naming the last trusted checkpoint
  record AdminAction entries; release kill switches only by two-person killswitch.release
  publish what members need to know in the change log, if safe and lawful [V]
  threat-model re-read (S10.12.2)
```

### 10.14.7 Hygiene [D]

- **Scanning.** A secret scanner runs before each commit and in CI over the whole history of any branch before it is made public. Patterns include the GitHub token forms the panel already redacts (`ghp_`, `github_pat_` and the like, panel-review §4.3) [V].
- **Redaction.** Error and log text passes a redactor that masks token-shaped strings; a user-supplied string is never concatenated into a log format.
- **No secrets in URLs.** Query strings carry none (S0.11.1); one-time codes are never placed in a URL.
- **CI separation.** Jobs that run untrusted code get no secrets and a read-only token (the panel's own design comment, panel-review §4.5 item 13 [V]).
- **Drill.** A rotation drill and a compromise drill run in `BM9`; both are logged and reviewed.

## 10.15 Hosting and reachability

### 10.15.1 Principles [D]

1. **Provider-neutral** (FD Principle 7): storage, hosting, mail, secrets and edge sit behind ports, so the system can move without a rewrite.
2. **Reachability is unverified** [V]: whether members in Iran can reach any chosen host is a measurement (G2), not an assumption (`RISK-14`).
3. **No circumvention** (FD Principle 9, ground rule 3): the platform bundles, recommends and implements no VPN, proxy, relay, bridge, domain fronting or mirror-hunting feature, and its copy gives no instruction to bypass a block. If the host is unreachable from a place, that is a recorded finding and an owner decision (change host through the ports, or accept). Whether any reachability measure is lawful is [V] for counsel.
4. **No mandatory third-party dependency** at runtime in any page: no CDN, font host, analytics, tag manager, captcha, embedded map or social widget (`analytics.third_party_trackers` = false, constant).
5. **Low bandwidth** is a design input, not a polish step (S10.15.6).

### 10.15.2 Ports [A]

Port names are proposed here; S4.* may rename them and assembly reconciles. Each port has a contract, a forbidden list, and a conformance test run against every adapter.

| Port | Contract | Forbidden | Conformance test |
| --- | --- | --- | --- |
| `StoragePort` | Relational store with serializable transactions for ledger postings, role separation (S10.14.3), append-only ledger tables, point-in-time restore | Eventually consistent stores for the ledger or leases (the panel's KV is advisory only, panel-review §2.2) | Ledger property and race suite (`T-prop-nn`, `T-adv-nn`) passes on the adapter |
| `BlobPort` | Immutable objects by hash: `TermsCopy` bytes, uploads, backups | Public-read buckets | Round trip by hash; access denied without credentials |
| `SecretsPort` | Versioned secrets, per-component scope, no value listing | Reading values into logs or the database | Scope test: a component reads only its own secrets |
| `SchedulerPort` | Reliable timers for lease reaping, expiry sweeps, retention sweeps, checkpoints, rotation reminders, invariant checks | Timers that run only when a request arrives (the panel evaluates expiry lazily, panel-review §3.3, which is not enough here) | Missed-tick test |
| `EdgePort` (optional) | TLS termination, routing, coarse rate limiting, HSTS | Logging full IPs beyond `retention.ip_hash_ttl_days`; injecting third-party scripts | Header and log audit |
| `MailPort` (optional, off by default) | Send a notice to a member-supplied address | Any message that asks for a recovery key or contains a login link | Template audit |
| `ClockPort` | Server time from a trusted source (S0.6.2) | Client time | Skew alarm |
| `LogSink` | Accepts only the fields of S10.13.1 item 9 | Free text, IPs, bodies | Schema test rejects extra fields |

An optional DoS-absorbing front is permitted only as an `EdgePort` adapter chosen by the owner after G1; such a front is an additional `host_provider` in S10.13.3 and must be named there before use.

### 10.15.3 Portability and the move drill [D]

```
move(host_old -> host_new):
  freeze: engage kill.all_new_jobs and kill.all_minting
  take a backup (encrypted); verify the ledger hash chain and checkpoints on the old host
  provision host_new from the same artifacts through the same ports; restore the backup
  verify: hash chain equals the last published checkpoint; invariants pass; counts of members, lots, escrows match
  rotate secrets that the old host could read (S10.14.6 list for a host change)
  switch DNS (TTL lowered in advance); keep host_old read-only until traffic has moved
  release kill switches by two-person killswitch.release; publish a ChangeLogEntry
```

The drill runs in `BM9` on a second host with synthetic data before launch (`AC-safety-10`).

### 10.15.4 Reachability from Iran [V] [D]

- **What is verified:** from networks inside Iran, can the first page load, the member API answer, and a cell round trip (lease, paste-back, submit) complete, within `ui.first_load_budget_bytes` and time budgets recorded as results, not promised? Also from outside Iran for the control.
- **Who:** the founders, with testers who opt in knowing the risk of the test and who are asked for no identity; remote measurement services where available [V]. No provider account is used in the test.
- **Measures:** DNS resolution, TCP connect, TLS handshake, first byte, full load on a throttled link, repeated at different times of day.
- **Where stored:** evidence on `g2.reachability_recorded` and `CalibrationRecord`-style rows by the `TEC` code; repeated every `security.reachability_check_interval_days` after launch, because blocking changes.
- **If unreachable:** the options in S10.15.1 item 3 only. The record states the finding; it is a [V] for counsel whether any further step is lawful.

### 10.15.5 No third-party resources [D]

| Control | Detail |
| --- | --- |
| Content security policy | `default-src 'self'`; no `unsafe-inline` or `unsafe-eval`; `frame-ancestors 'none'`; `connect-src` limited to the app's own origins. The panel today sets no such headers and loads fonts from third-party hosts (panel-review §4.5 item 12) [V], so none of its page code is reused unreviewed |
| Fonts | Persian and Latin fonts are self-hosted subsets; their licenses are checked [V: license of each font, reviewer, stored with the asset] |
| Build check | CI fails if any built asset or page contains an absolute `http` or `https` URL to a host outside the project's own set (`AC-safety-09`) |
| Preconnect, prefetch, embeds | None to third parties |
| Reports | No third-party error reporting; errors go to `LogSink` only |

### 10.15.6 Low-bandwidth rules [D]

- First load stays within `ui.first_load_budget_bytes` compressed (initial configurable default in S10.18; replaced by `TEC` measurement on real phones and links).
- Text first: no images on the first-contribution path; system fonts until the subset font arrives; no web socket requirement, polling with `ETag`, `Retry-After` and backoff (S0.11.7).
- A cell response body is at most `cell.envelope.max_input_chars` x 3 bytes of UTF-8 plus metadata; a submission is at most `cell.envelope.max_submission_bytes` (S0.10.6). Paste-back retries use the same `Idempotency-Key`, so a dropped connection never costs a second submission.
- Public pages are cacheable (`Cache-Control: max-age` no larger than the refresh parameter, S0.11.7), so a weak link can reuse them.

### 10.15.7 Environments [D]

Production, staging and development are separate hosts and secret scopes. No production data, member record or secret enters a non-production environment; tests use synthetic data (S18.*). The admin origin is separate in every environment (S0.11.4). Monitoring and alerting follow S10.13.1 item 9.

## 10.16 Abuse reporting, takedown, ban and appeals

Process spec. Entities `Report` and `Appeal`, their states and events are in S0.9.7 and S0.9.8 and are used unchanged. Everything legal is [V] for counsel.

### 10.16.1 Roles and permissions [D]

Permission names follow `perm.<area>.<action>` (S0.8.2); the matrix itself is in the identity file of S10.*, and the names below are proposed [A].

| Role in the process | Held by | May | May not |
| --- | --- | --- | --- |
| Reporter | Any member or requester (`perm.report.file`) | File a report; see its outcome; appeal a dismissal once | See who the subject is beyond the reported object; see other reports |
| Triager | `AdminUser` with `reviewer` (`perm.report.triage`) | Triage, request more evidence, dismiss, escalate | Ban; release a kill switch |
| Decider | `AdminUser` with `reviewer` (`perm.report.decide`) | Warn, restrict, suspend, reject a job, pause a template, void cells | Decide a report about themselves, or an appeal of their own decision |
| Second approver | A different `AdminUser` (`perm.member.ban_approve`) | Approve a ban, a legal-hold clear, a disclosure | Be the decider of the same action |
| Operator | `AdminUser` with `operator` | Engage kill switches with a logged reason; execute approved actions technically | Decide content questions alone |
| Appeals reviewer | `AdminUser` with `reviewer` who was not the decider and has no declared conflict (`perm.appeal.review`) | Uphold or overturn | Handle an appeal about a decision they took |
| Counsel (external) | Outside the system | Advise on legal notices and disclosure [V] | Hold any system credential |
| Subject | The reported member or requester | See the decision, its reason code and the object; appeal | See the reporter's identity |

### 10.16.2 Intake [D]

- **In product:** a report button on every cell card (FD§5.5), on public team and milestone surfaces, and on a requester's result view. A filing creates `Report` in state `open` and the event `report.filed`.
- **Categories** (`report_category`, new enum, S10.18): `unsafe_prompt`, `injection_attempt`, `suspected_sensitive_data`, `prohibited_content`, `harassment`, `forged_or_junk_result`, `fraud_or_farming`, `impersonation`, `safety_of_person`, `legal_notice`, `other`.
- **Automatic evidence** attached at filing, by identifier only: object id (`cel_`, `tpv_`, `job_`), `policy_version`, rule results (`policy.<rule>.<slug>`), submission hash, verification outcomes. Never a volunteer's chat page (never read) and never plaintext of a payload that is about to be purged for `suspected_sensitive_data` (S10.16.7).
- **Free text** is limited to `report.max_text_chars` and is stored with the report; it is written for reviewers, never shown to the subject.
- **Automatic flags** (screening, gold failures, anomaly detectors) create reports with `principal_type` = `system`. A flag never bans anyone by itself [D].
- **Outside the product:** people who are not members (a copyright holder, a person named in content, a legal authority) use the contact `report.external_contact` (string, set by the operator, published on the public pages; empty means launch gate `g1.abuse_contact_published` is open). Legal notices go to counsel without any member data being checked or produced first [V].
- **Rate limit:** `report.max_per_member_per_day` per member.

### 10.16.3 Triage and service levels [D]

```
report.filed  -> state open
triager picks within SLA -> report.triaged (category confirmed or changed, severity set)
decider chooses an action (10.16.4)  -> report.actioned   or   report.dismissed (reason code recorded)
SLA clock: filed_at -> triaged_at
  normal categories : report.triage_sla_days        (initial configurable default 3)
  urgent categories : report.urgent_triage_sla_s     (initial configurable default 14400)
  urgent = safety_of_person, injection_attempt, suspected_sensitive_data, legal_notice
on breach: Alarm, metric hamyar_report_triage_overdue_total increments; the oldest overdue report is shown first on the queue
```

SLAs are published defaults, configurable parameters, and targets, not promises ("declared"). A report in an urgent category lets any reviewer escalate to an operator at once, who may engage `kill.template.<tpl_id>` or pause cells (`cell.paused`) before a decision, with a logged reason. Template autopause: when `template.autopause_report_count` reports from at least `template.autopause_min_distinct_reporters` distinct reporters, each at or above `template.autopause_min_reporter_tier`, arrive within `template.autopause_window_s` for the categories `unsafe_prompt`, `injection_attempt`, `suspected_sensitive_data`, `prohibited_content`, the template is paused (`template.paused`); the pause is not a verdict, and release needs the usual `killswitch.release` two-person action (`ISS-106`).

### 10.16.4 Action ladder [D]

`moderation_action` (new enum, S10.18) with the existing event that records each effect:

| Action | Effect and event | Decider and approval | Notes |
| --- | --- | --- | --- |
| `no_action` | `report.dismissed` | Triager | Reason code recorded |
| `warn` | Note on the member; `report.actioned` | Decider | No other effect |
| `restrict` | `member.restricted`; caps fall, sampling rises (`trust.*`) for `trust.restriction_days` | Decider | Lifts by `member.restriction_lifted` |
| `suspend` | `member.suspended`; leases revoked (`lease.revoked`) | Decider | Reversible by `member.reinstated` |
| `ban` | `member.banned`; leases revoked | Decider plus second approver (`member.ban` is in `security.two_person_actions`) | Appealable; see below |
| `reject_job` | `job.stop_requested` with `closure_reason` `operator_killed`; refunds follow S6.* | Decider | Unstarted cells refunded as usual |
| `pause_template` | `template.paused` through `kill.template.<tpl_id>` | Operator on a decider's request | Release is two-person |
| `suspend_service` | `service.suspended` through `kill.service.<svc_id>` | Operator | Release is two-person |
| `void_cells` | `cell.voided` for in-flight cells | Decider | |
| `takedown_output` | Hosted copy withdrawn (S10.16.5) | Decider; legal notices via counsel [V] | |
| `refer_to_counsel` | Note on the report; no member data produced | Operator | [V] |

**Rules** [D]

1. Proportionality: the lowest action that stops the harm; escalation needs a recorded reason code.
2. A ban is never automatic, never produced by a classifier alone, and never propagates to an invite tree; tree members are reviewed individually (`THR-06`).
3. A ban or suspension never edits the ledger and never confiscates credit: the member's lots expire normally into the Reserve (FD§4.5), escrow refunds proceed under S6.*, accepted cells stand unless a fraud finding leads to `cell.overturned` and a two-approver `reversal`. Involuntary forfeiture is not specified (`ISS-104` records why: no entry type exists for it and it would reward false reports).
4. A suspended or banned member can still authenticate to a restricted scope: read history, export own data, file an appeal, close the account (constraint on S10.*).
5. A ban does not trigger tracking of the person elsewhere: evasion is limited by `grant.max_per_device` and the sybil limits only; no extra fingerprinting is added to detect it (S10.13.1 item 4). Residual evasion is accepted.
6. The platform does not report members to any authority on its own initiative unless counsel determines the law compels it [V].

