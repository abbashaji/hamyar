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

