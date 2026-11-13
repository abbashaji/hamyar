# 14. Launch gates: building versus launching

*Spec part 14 · owner cell C-019 · binding on every part that creates members, jobs, cells or credit. Written against Founding Document draft v0.1 (FD) and `spec/00-conventions.md` (S0). This part controls software behavior. Nothing here is legal advice and nothing here was checked against any provider's terms or any law. A signed-off gate records that evidence was attached and that two people reviewed it; it does not make anything lawful, safe or permitted [V].*

## 14.1 Purpose: build everything, launch nothing until the gates say so

FD§8.3 lists six verification gates, G0 to G5, and FD§9 says G0 and G1 must be finished before Phase 0 ends. Today none is resolved. The product owner builds the full system before running any experiment, so the gates cannot be a paragraph that people remember to read. This part makes them a product feature: a data model, screens, a machine-checked exit rule, global switches that default to off, kill switches, enforcement points in server code, and tests. [D]

Four locks, each independent of the others:

| Lock | What it does | State on a fresh database | Specified in |
| --- | --- | --- | --- |
| Registry lock | Every service starts `unreviewed`, which counts as no; no job can be created for a service until a reviewer has recorded the flags against a saved terms copy | No service approved | S14.3 |
| Checklist lock | G0..G5 broken into items with evidence and two-person sign-off | Every item `open` | S14.4 to S14.6 |
| Switch lock | `launch.members_may_join`, `launch.member_jobs_enabled` and `launch.minting_enabled` stay `false` until the exit rule passes | All `false` | S14.7, S14.8 |
| Brake | Kill switches pause a template, a service, a member, all minting or all new jobs | All `released` | S14.8 |

Rules that apply to the whole part: [D]

1. **Fail-closed.** Any gate input that is missing, unreadable, malformed, expired or ambiguous is evaluated as closed. S14.9 lists every case.
2. **Server-side only.** A client, a hidden button or a cached page is never a control. Every enforcement point runs in the server transaction that changes state (S14.9).
3. **Defaults live in migrations.** Migrations and seed data never set a launch switch to `true`, never create a service in any state but `unreviewed`, and never create a signed-off item. A CI check fails the build if they do (`AC-launch-03`).
4. **Tighten at once, loosen with two people.** Closing a switch, engaging a kill switch or reopening an item needs one authorized admin. Opening a switch, releasing a kill switch or signing an item needs two distinct admins (R10 applied to launch; `security.two_person_actions`, 0.10.6).
5. **Evidence before assertion.** A sign-off binds to hashes of the evidence it relied on and to the values it watched; if either changes, the sign-off stops counting (S14.6).
6. **Brakes never trap value.** Closing a gate stops transitions that start new work or create credit. It never blocks refunds, cancellations, settlement, expiry sweeps, data export or account recovery (S14.9, `AC-launch-32`).
7. **No bypass.** There is no flag, environment variable, header, debug route or build option that skips a gate. Test suites open the gates through the same flow with seeded test admins (`AC-launch-03`).
8. **Honest limits.** The tool checks that evidence exists, was reviewed by two people and is current. It does not read, interpret or judge the evidence (S14.14).

Owned elsewhere: the service review machine and flag semantics (S7.*), admin authentication and the generic two-person mechanism (S10.*), the final operation list of the API (S15.*), final user-facing copy (S11.*), the values that replace defaults (S16.*).

## 14.2 Names and vocabulary used by this part

All names come from S0. Additions are listed in `ISS-147`.

| Brief or FD wording | Normative name | Type, default | Defined in |
| --- | --- | --- | --- |
| members may join | `launch.members_may_join` | `bool`, `false` | 0.10.6 table C |
| jobs may be created (member jobs) | `launch.member_jobs_enabled` | `bool`, `false` | 0.10.6 table C; scope in `ISS-144` |
| minting enabled | `launch.minting_enabled` | `bool`, `false` | 0.10.6 table C |
| gates that must be signed | `launch.required_gate_ids` | `json`, `["G0","G1"]` | 0.10.6 table C |
| sign-offs per item | `launch.min_signoffs` | `int`, 2 | 0.10.6 table C |
| approved services needed | `launch.min_approved_services` | `int`, 1 | 0.10.6 table C |
| pause a template, a service, a member, all minting, all new jobs | `kill.template.<tpl_id>`, `kill.service.<svc_id>`, `kill.member.<mem_id>`, `kill.all_minting`, `kill.all_new_jobs` | `KillSwitch`, `released` | 0.10.6 |
| a checklist line | `LaunchGateItem` (`lgi_`) | permanent | 0.7 |
| evidence, sign-off, launch authorization | `GateEvidence` (`gev_`), `GateSignoff` (`gso_`), `LaunchAuthorization` (`lau_`) | permanent | this part [A] |

UI labels (English; `fa` supplied by S11.*): 'Members may join', 'Member jobs may be created', 'Minting enabled'. [A]

Permissions [A] (names follow 0.8.2; the full matrix is S10.*):

| Permission | Meaning | Default holders |
| --- | --- | --- |
| `perm.launch.read` | View checklist, evaluation, switch panel | `reviewer`, `operator` |
| `perm.launch.read_restricted` | Open evidence marked `restricted` (counsel memos) | `operator` |
| `perm.launch.attach_evidence` | Attach evidence to an item | `reviewer` for items of scope `service`; `operator` for all items |
| `perm.launch.signoff` | Sign off an item | same split as attach |
| `perm.launch.reopen` | Reopen an item | `reviewer`, `operator` |
| `perm.launch.switch_propose`, `perm.launch.switch_approve`, `perm.launch.switch_close` | Open a launch switch (two admins), close one (one admin) | `operator` |
| `perm.killswitch.engage` | Engage a kill switch | `operator` for every key; `reviewer` for `kill.template.*` and `kill.service.*` only |
| `perm.killswitch.release_propose`, `perm.killswitch.release_approve` | Release a kill switch (two admins) | `operator` |

## 14.3 Registry lock: services ship `unreviewed`

**Decisions** [D]

- `RL-1` On a fresh database the registry is empty or holds only entries in state `unreviewed`. An operator may import a candidate list from a file; the importer ignores any state, flag or approval field in the file and creates `ServiceRegistryEntry` rows with `state = unreviewed`, no `FlagAnswer` and no `TermsCopy`. This spec names no provider; the candidate list is data entered by a human [V].
- `RL-2` The only transition into `approved` is `service.approved` (0.9.6). The database enforces its guard with a `CHECK` and a trigger, not only with application code: an `approved` row carries `approved_at`, `approved_by` (an `adm_` id holding `reviewer`) and `terms_copy_id`, and the trigger confirms the flag rows of `SG` below. A direct `UPDATE` to `approved` by the application role fails (`AC-launch-04`). Field names `approved_at`, `approved_by`, `reviewed_at`, `reviewed_by`, `terms_copy_id` are provisional; S7.* owns the entity (`ISS-147`). [A]
- `RL-3` `unreviewed` counts as no. An absent `FlagAnswer` is `unknown`, and `unknown` is evaluated as `no` (0.8.3, FD§5.3).
- `RL-4` 'Approved' means the service gate `SG` below holds. `SG` is evaluated again at every enforcement point that names a service (S14.9), not only when the service is approved.
- `RL-5` Saved terms are bytes plus hash (0.6.4). A `FlagAnswer` is valid only against the latest `TermsCopy` of its service. Saving a newer copy with a different hash makes every older answer stale (S14.6, `AC-launch-21`).
- `RL-6` A nightly job re-hashes every stored `TermsCopy`. A mismatch suspends the service (`service.suspended`) and raises an alarm. [A]
- `RL-7` `service.approved` has one more guard than 0.9.6 lists: every per-service `G0` item of that service is `signed_off` and valid (S14.5, S14.7). Gate reopening on a service moves it to `review_due` (`ISS-143`).

**Service gate `SG`** (pseudocode; reasons are returned in `details.reasons`):

```
function service_gate(svc_id, now) -> Pass | Fail(reasons)
    svc = registry.get(svc_id)                       # missing row -> Fail('service_unknown')
    reasons = []
    if svc.state != 'approved':    reasons += 'service_not_approved'     # unreviewed, in_review, review_due, ... all count as no
    tcp = terms_copies.latest(svc_id)
    if tcp is null:               reasons += 'terms_copy_missing'
    for key in ['third_party_task_use', 'prohibited_content_compatible']:
        fa = flag_answers.latest(svc_id, key, region = null)
        if fa is null or fa.answer != 'yes':   reasons += 'flag_not_yes:' + key     # null and 'unknown' are 'no'
        elif tcp is not null and fa.terms_copy_id != tcp.id:
                                               reasons += 'flag_answer_stale:' + key
    if svc.reviewed_by is null or svc.reviewed_at is null:  reasons += 'reviewer_not_recorded'
    if now >= svc.reviewed_at + param('service.review_max_age_days') * 86400:  reasons += 'review_expired'
    if not g0_items_valid(svc_id, now):                      reasons += 'g0_items_not_signed'
    if kill_switch_engaged('kill.service.' + svc_id):        reasons += 'kill_switch_engaged'
    return Pass if reasons is empty else Fail(reasons)
```

Per-purpose conditions (`R5`..`R7`) stay in the policy engine (S7.*). `SG` answers one question only: may any job be created or run for this service at all. [D]

**What a job needs at each point** [D]

| `service_requirement` | At job creation, submission and escrow confirmation | At lease and acceptance |
| --- | --- | --- |
| `M0` | At least one service passes `SG` | The service the volunteer attested passes `SG` at acceptance (R9) |
| `M1` | Every pinned service passes `SG` | Same, for the attested service |
| `M2` | At least one registry entry for an open-weight route passes `SG`; how local routes are represented is S7.* [V] | Same |
| `job_type` `human_review` under fallback (iii) | No provider service; requires fallback (iii) adopted (S14.7) and `ff.channel.human_review` on | Review cells only |

**Gate obligations by service state** (S7.* owns the machine and may refine the in-flight handling; the right-hand columns are what the gate requires of it) [A]

| Service state | New jobs | New leases needing it | In-flight cells | Submission attested to it |
| --- | --- | --- | --- | --- |
| `unreviewed`, `in_review`, `rejected` | Refused | Refused | None can exist | Rejected, `reject.policy_changed` |
| `approved` | Allowed if `SG` | Allowed | Continue | Accepted if checks pass |
| `review_due` | Refused at once | Allowed for `service.review_grace_days` | Continue for the grace period | Accepted within the grace period |
| `suspended` | Refused | Refused | `cell.paused`; pinned jobs `job.paused` | Lease revoked, so `reject.lease_expired` |
| `revoked` | Refused | Refused | `cell.voided`; pinned jobs `job.stop_requested` with closure_reason `service_revoked` | Rejected, `reject.policy_changed`; already accepted cells stay accepted and paid (R9: a change never legitimizes in-flight work retroactively and never claws back accepted work) |

## 14.4 Data model

Table and column naming follows 0.7. Entities marked [A] are convention additions (`ISS-147`). `GI-nn` ids name gate invariants local to this part. [A]

### 14.4.1 `LaunchGateItem` (`launch_gate_items`, prefix `lgi_`, retention `permanent`)

One row is one checklist line for one scope. The catalog of lines is data seeded by migration (S14.5); rows are created by `gate.item_created`.

| Column | Type | Constraint and meaning |
| --- | --- | --- |
| `id` | text | `lgi_` ULID (0.6.3) |
| `catalog_key` | text | Stable key from the catalog in S14.5, for example `g0.svc.a`, `g1.threat_model` |
| `catalog_version` | int | Version of the catalog row that created this item; a catalog change that alters meaning increments it and reopens the item (`catalog_changed`) |
| `gate_id` | text | `CHECK` in `G0`..`G5` |
| `scope_type` | text | `global`, `service`, `template` |
| `scope_id` | text null | `svc_` or `tpl_` id; null if and only if `global` |
| `kind` | text | `attestation`, `evidence`, `measurement`, `decision`, `machine_check` |
| `is_blocking` | bool | Counts in the predicates of S14.7. Advisory items (false) are shown and never block |
| `required_role` | text | `reviewer` or `operator`: at least one signer of the generation holds it (SO-3, S14.6) |
| `state` | text | `open`, `evidence_attached`, `signed_off`, `reopened` (0.9.8) |
| `generation` | int | Starts at 1; increases by 1 on every `gate.reopened` |
| `outcome` | text null | `satisfied`, `satisfied_with_conditions`, `not_satisfied`, `adopted`, `declined`; set only while `state = signed_off` |
| `conditions_text` | text null | At most 4,000 characters; required when `outcome = satisfied_with_conditions` |
| `signed_off_at`, `valid_until` | timestamptz null | Set with the outcome; `valid_until` by the formulas in S14.6.3 |
| `watch` | json | List of watch descriptors copied from the catalog (S14.6.4) |
| `watch_digest` | text null | `sha256:` over canonical JSON of the watched values at sign-off |
| `reopen_reason` | text null | `expired`, `watched_change`, `manual`, `evidence_superseded`, `catalog_changed`, `service_state` |
| `created_at`, `updated_at`, `row_version` | | Standard (0.7) |

Unique on `(catalog_key, scope_type, scope_id)` with null `scope_id` coalesced to the empty string. Indexes: `(gate_id, state)`, `(scope_type, scope_id)`, and `(valid_until)` partial where `state = 'signed_off'` for the expiry sweep. [D]

`outcome` meaning: `satisfied` means the recorded evidence supports the item; `satisfied_with_conditions` means it does, subject to `conditions_text`, which the signers also enter as the items or parameters it constrains; `not_satisfied` is a recorded finding that the answer is no (it is a sign-off, so it is immutable, and it never counts as valid); `adopted` and `declined` are used only by items of kind `decision` (fallbacks). A `not_satisfied` outcome is the honest way to record that counsel or a measurement said no. [D]

### 14.4.2 `GateEvidence` (`gate_evidences`, prefix `gev_`, retention `permanent`, append-only) [A]

| Column | Type | Rule |
| --- | --- | --- |
| `id` | text | `gev_` ULID |
| `item_id`, `item_generation` | text, int | The item and the generation the evidence belongs to |
| `kind` | text | `document`, `terms_copy_ref`, `flag_answer_ref`, `calibration_ref`, `measurement_report`, `counsel_memo`, `ci_artifact`, `rotation_record`, `secret_audit_note`, `history_scan_report`, `decision_record`, `interview_summary`, `attestation` |
| `content_hash` | text | `sha256:` over the raw bytes, computed by the server and never taken from the client (0.6.4) |
| `byte_length` | int | At most `launch.evidence_max_bytes` |
| `media_type` | text | `text/plain`, `text/markdown`, `application/pdf`, `application/json`, `image/png`; sniffed, not trusted from the header |
| `storage_ref` | text | Opaque key behind the storage interface (S4.*) |
| `visibility` | text | `internal` or `restricted`; `counsel_memo` is always `restricted` |
| `source_ref` | text null | For system-attached evidence: the `fla_`, `tcp_` or `cal_` ids, or a CI run reference |
| `occurred_at` | timestamptz null | When the described thing happened (rotation date, measurement date, memo date); used by the validity formulas |
| `note` | text | At most 2,000 characters, plain text, escaped on display |
| `attached_by` | text | `adm_` id or `system` |
| `supersedes_evidence_id` | text null | A correction is a new row pointing at the old one; nothing is edited or deleted |
| `created_at` | timestamptz | |

Upload rules [D]:

- `EV-1` The server hashes the bytes and stores them; a client-supplied hash is only compared, never trusted.
- `EV-2` Media type is sniffed from content; a mismatch with the declared type is `VALIDATION_FAILED`.
- `EV-3` Secret-pattern guard: content that matches credential patterns (provider token prefixes, private-key headers, long high-entropy strings) is refused with `UNPROCESSABLE` and `details.fields[].code = secret_pattern` and is not stored. The guard is a heuristic: it reduces accidental disclosure and does not prove absence (S14.14). Evidence about secrets records handling, dates and fingerprints of identifiers, never values (ground rule 2; FD§10).
- `EV-4` Evidence is never rendered inline. It is served with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`; the screen shows hash, size, type and note only.
- `EV-5` `restricted` evidence is readable only with `perm.launch.read_restricted`; every read writes an `AdminAction`.
- `EV-6` Evidence contains no personal data of members, no raw IP addresses and no provider credentials. Tester results for reachability or device tests are stored as summaries without identities (FD Principle 8).

### 14.4.3 `GateSignoff` (`gate_signoffs`, prefix `gso_`, retention `permanent`, append-only) [A]

| Column | Type | Rule |
| --- | --- | --- |
| `id` | text | `gso_` ULID |
| `item_id`, `item_generation` | text, int | |
| `admin_user_id`, `credential_id` | text, text | The `AdminUser` and the passkey (`acr_`) used |
| `acted_as_role` | text | `reviewer` or `operator`, the role the signer acted under |
| `outcome` | text | One of the item outcomes allowed for its `kind` |
| `note` | text | At most 2,000 characters |
| `conditions_text_hash` | text null | SHA-256 of the conditions text |
| `evidence_set_hash` | text | SHA-256 over canonical JSON of the sorted list of `{evidence_id, content_hash, kind}` of the generation, superseded rows excluded |
| `watch_digest` | text | The watched values at signing |
| `attestation_copy_key` | text | Which attestation sentence the signer accepted (`copy.launch.attest_*`) |
| `digest` | text | The sign-off digest below |
| `assertion` | json | WebAuthn assertion fields (`client_data_json`, `authenticator_data`, `signature`, base64url) so the signature can be re-verified offline |
| `session_id`, `request_id` | text | `ses_`, `req_` |
| `created_at` | timestamptz | |

Unique on `(item_id, item_generation, admin_user_id, digest)`. [D]

**Sign-off digest** [D][A]: `digest = sha256` over RFC 8785 canonical JSON (0.6.4) of `{item_id, catalog_key, scope_id, generation, catalog_version, outcome, conditions_text_hash, evidence_set_hash, watch_digest, attestation_copy_key}`. The WebAuthn challenge for a sign-off is those 32 bytes, so a stolen admin session token alone cannot produce a sign-off and a recorded assertion cannot be replayed onto different evidence.

### 14.4.4 `LaunchAuthorization` (`launch_authorizations`, prefix `lau_`, retention `permanent`) [A]

One row records one decision to open one launch switch.

| Column | Type | Rule |
| --- | --- | --- |
| `id`, `switch_name` | text | `lau_`; one of `launch.members_may_join`, `launch.member_jobs_enabled`, `launch.minting_enabled` |
| `proposal_action_id` | text | `act_` of the proposal `AdminAction` |
| `proposed_by`, `approved_by` | text | Distinct `adm_` ids (`CHECK proposed_by <> approved_by`) |
| `evaluation_digest` | text | SHA-256 of the canonical evaluation result (S14.7) |
| `relied_on` | json | List of `{item_id, generation, signoff_ids[]}` the evaluation used |
| `authorized_until` | timestamptz | Minimum `valid_until` over every relied-on item; the authorization expires by itself at this instant |
| `created_at` | timestamptz | |
| `revoked_at`, `revoked_reason`, `revoked_by` | timestamptz, text, text | Null until revoked, then set once (trigger allows null-to-value only). Reasons: `gate_regressed`, `closed_by_admin`, `expired`, `superseded`, `stop_adopted` |

Active means `revoked_at is null and now < authorized_until`. A launch switch is open only if its parameter is `true` and an active authorization exists for it (`GI-01`, S14.9). Time expiry therefore needs no background job to take effect. [D]

### 14.4.5 `KillSwitch` rows (`kill_switches`, prefix `ksw_`, retention `permanent`, append-only)

Each engage or release is a new row; the current state of a key is its row with the highest `seq`. [D]

| Column | Type | Rule |
| --- | --- | --- |
| `id`, `switch_key` | text | `ksw_`; one of `kill.all_minting`, `kill.all_new_jobs`, `kill.template.<tpl_id>`, `kill.service.<svc_id>`, `kill.member.<mem_id>` |
| `scope_type`, `scope_id` | text, text null | `global`, `template`, `service`, `member`; null id for `global` |
| `seq` | int | Per key, starting at 1; unique with `switch_key` |
| `state` | text | `released` or `engaged` |
| `reason_code` | text | `terms_change`, `safety_incident`, `abuse`, `ledger_concern`, `legal_hold`, `provider_warning`, `operator_decision` [A] |
| `reason_text` | text | Required, 10 to 2,000 characters, plain text |
| `acted_by`, `approved_by` | text, text null | `adm_` ids; `approved_by` is required and distinct from `acted_by` when `state = released` |
| `request_id`, `created_at` | | |

Migrations insert `seq = 1`, `state = released` for `kill.all_minting` and `kill.all_new_jobs`. Scoped keys have no row until first engaged. Missing-row semantics differ on purpose and are fixed in S14.9. [D]

### 14.4.6 State machine of `LaunchGateItem`

State and event names are those of 0.9.8; one event is added (`gate.item_created`, `ISS-147`). Events carry `item_id`, `catalog_key`, `gate_id` and `generation` beside the standard fields of 0.9.1. [D]

```
(none)             --gate.item_created-->       open
open               --gate.evidence_attached-->  evidence_attached    first evidence of the generation (human or system)
reopened           --gate.evidence_attached-->  evidence_attached    first evidence of the new generation
evidence_attached  --gate.signed_off-->         signed_off           guard SO-1..SO-8 (S14.6)
signed_off         --gate.reopened-->           reopened             generation + 1; reason: expired, watched_change, manual,
                                                                     evidence_superseded, catalog_changed, service_state
evidence_attached  --gate.reopened-->           reopened             reason manual only; partial sign-offs stay stored and stop counting
```

Further evidence on an item already in `evidence_attached` is not a state change; it writes an `AdminAction` and changes the evidence set hash, so earlier partial sign-offs no longer match the current digest and stop counting. Evidence attached to a `signed_off` item first reopens it (`evidence_superseded`) and then attaches, in one transaction, emitting `gate.reopened` then `gate.evidence_attached`. `open` cannot be reopened. [D]

| Event | Guard | Side effects |
| --- | --- | --- |
| `gate.item_created` | Catalog row exists; for scope `service` or `template` the entity exists | `AdminAction` with actor `system` |
| `gate.evidence_attached` | Actor holds `perm.launch.attach_evidence` for the item scope, or is `system`; rules EV-1..EV-6 | `AdminAction`; evidence set hash recomputed |
| `gate.signed_off` | `SO-1`..`SO-8` (S14.6.2) | Sets `outcome`, `signed_off_at`, `valid_until`, `watch_digest`; runs `reevaluate_dependents` (S14.7); for a service item, may unlock `service.approved` |
| `gate.reopened` | Actor holds `perm.launch.reopen`, or the actor is `system` for the automatic reasons | `generation + 1`; clears `outcome`, `valid_until`, `watch_digest`; in the same transaction revokes every `LaunchAuthorization` that relied on the item and closes the switches that depended on it (S14.7); for a service item moves the service to `review_due` (S14.6.5) |

### 14.4.7 Database protections [D]

- The running service uses a role that has `SELECT` and `INSERT` on `gate_evidences`, `gate_signoffs` and `kill_switches`; `SELECT`, `INSERT` and `UPDATE (revoked_at, revoked_reason, revoked_by)` on `launch_authorizations`; `SELECT`, `INSERT` and a column-restricted `UPDATE` on `launch_gate_items`. It has no `DELETE` on any table of this part. Migrations run under a different role that the service never holds.
- Trigger `signed_off_needs_signoffs` on `launch_gate_items` refuses `state = 'signed_off'` unless the qualifying sign-off rows exist (the trigger recomputes `SO-1`, `SO-2`, `SO-4`).
- Trigger `launch_param_needs_authorization` on `parameter_versions`: a row that sets `launch.members_may_join`, `launch.member_jobs_enabled` or `launch.minting_enabled` to `true` requires an active `LaunchAuthorization` for that switch written in the same transaction; a row that sets one to `false` is always allowed (fail-closed direction).
- Guard triggers on `members`, `jobs` and `ledger_entries` are listed in S14.9.
- All of these are exercised by `AC-launch-40` and `AC-launch-18`.

## 14.5 The checklist: G0..G5 as concrete items

The catalog is seed data in migrations (`catalog_version` per row). Every gate below is broken into items a person can attach evidence to and sign. Global items are created at first boot; service items when `service.created` fires; the template item when a `Template` first reaches `approved`. Keys are stable. The catalog says what must be recorded; it contains no provider fact, no legal conclusion and no measured value. Every answer is entered by a human and is [V]. [D]

Columns: **Role** is `required_role` (SO-3). **Watch** names the descriptors of S14.6.4. **Validity** refers to S14.6.3.

### 14.5.1 G0, per service (scope `service`, 12 items per service)

Created for every `ServiceRegistryEntry`, including those that stay `unreviewed`. Role `reviewer`. Watch for all: `terms_hash(svc)`, `flag_answers(svc)`. The system attaches the saved `TermsCopy` and the latest `FlagAnswer` rows as evidence (`terms_copy_ref`, `flag_answer_ref`) when the reviewer saves them, which moves the item to `evidence_attached`. [D]

| `catalog_key` | FD section 8.3 | Question recorded against the saved terms | Flag keys (0.8.3) | Outcome rule |
| --- | --- | --- | --- | --- |
| `g0.svc.terms` | G0 lead-in | Dated copy of the terms saved: bytes, hash, source reference, capture date | none | `satisfied` only if a `TermsCopy` exists, its hash was re-verified at attach, and the capture date is within `service.review_max_age_days` of sign-off |
| `g0.svc.a` | G0(a) | May a personal free account be used to do tasks for other people? | `third_party_task_use` | Gate flag |
| `g0.svc.b` | G0(b) | Is sharing, pooling, reselling or crediting access prohibited? | `access_pooling_or_crediting` | Gate flag |
| `g0.svc.c` | G0(c) | What do the terms say about automation, scraping, prefilled links and copy-and-paste workflows? | `human_copy_paste_use`, `prefilled_link_use`; reviewer note for automation and scraping (`ISS-147`) | Gate flags |
| `g0.svc.d` | G0(d) | Regional availability: may people in each required region use the service, and what do the terms say about circumvention? | `regional_availability`, one answer per region in the catalog attribute `required_regions` (initially `IR`, from FD section 8.3 G0(d)) [P]; regions of the operator's jurisdiction are added after counsel [V] | Gate flag per region |
| `g0.svc.e` | G0(e) | Is commercial use of outputs allowed on the free tier? | `commercial_use_of_output` | Gate flag |
| `g0.svc.f` | G0(f) | Is using outputs to train or develop other models allowed? | `training_use_of_output` | Gate flag |
| `g0.svc.g` | G0(g) | Is publishing outputs openly allowed? | `open_publication_of_output` | Gate flag |
| `g0.svc.h` | G0(h) | Does the provider train on user chats by default; could account memory or connectors leak content? | `info.provider_trains_on_chats`, `info.memory_or_connectors_risk` | Info flags |
| `g0.svc.i` | G0(i) | What do the usage policy and prohibited-content rules require; are they compatible with the content Hamyar accepts (R3)? | `prohibited_content_compatible`; reviewer summary of the requirements | Gate flag |
| `g0.svc.j` | G0(j) | What does 'free allowance' formally mean and can it change without notice? | `info.allowance_may_change` | Info flag |
| `g0.svc.k` | G0(k) | Would the provider give written permission for this use? | `info.written_permission`; if `yes`, the permission document as evidence (`document`, `restricted`) | Info flag |

**Outcome rule for flag items** (`SO-7`): `satisfied` is allowed only when every gate flag behind the item is `yes` for the latest `TermsCopy`. If any is `no`, `unknown` or absent, the only allowed outcomes are `satisfied_with_conditions`, whose `conditions_text` states the effect (for example 'adapter is copy-only', 'purpose P2 stays locked', 'service stays unreviewed'), or `not_satisfied`. Info flags accept any recorded answer as `satisfied`, because the item records that the question was answered, not that the answer is favorable. A service can be approved only if `g0.svc.a` and `g0.svc.i` are `satisfied` (FD section 5.3, 0.8.3). [D]

### 14.5.2 G0, counsel (scope `global`, role `operator`)

FD section 8.3 lists legal questions for counsel in the operator's jurisdiction. The operator's jurisdiction is an open owner decision (S3.*) and entity form is itself a question, so the first item records the jurisdiction and the counsel engaged. Evidence for every item: a `counsel_memo` (restricted, `occurred_at` = memo date) and an `attestation` that the memo is a written answer from a person qualified in that jurisdiction and not an internal opinion [V]. Validity: generic. No watch is possible for law, so validity is the only re-validation. [D]

| `catalog_key` | FD section 8.3 legal question |
| --- | --- |
| `g0.cns.jurisdiction` | Operator's jurisdiction and the counsel engaged (owner decision, S3.*) |
| `g0.cns.entity` | Entity form |
| `g0.cns.credit_status` | Whether credit counts as regulated stored value or a virtual currency |
| `g0.cns.consumer` | Consumer-protection and gambling-like-mechanics exposure |
| `g0.cns.sanctions` | Sanctions and export-control exposure for dealings with people or services in Iran |
| `g0.cns.privacy` | Privacy law for pseudonymous data and IP logs |
| `g0.cns.copyright` | Copyright of AI output and the wording of the contributor waiver |
| `g0.cns.name` | Use of the name and of the words 'cooperative' and 'bank' |

Conditions that counsel attaches go into `conditions_text` and the signers name which flag, parameter, policy rule or copy key implements each one; the tool does not verify that they are implemented. [A]

### 14.5.3 G0, fallbacks (scope `global`, kind `decision`, role `operator`)

FD section 8.3: 'Fallbacks if no service clears G0'. Each is a recorded decision, not a mode. Outcome `adopted` or `declined`; the decision record carries the rationale, the person-level decider list (admin ids), the date and a review date (`valid_until`). Their effect on the exit rule is defined once, in S14.7.4. [D]

| `catalog_key` | FD section 8.3 wording | Evidence required |
| --- | --- | --- |
| `g0.fb.i` | (i) Seek written permission from a provider | `decision_record` naming the service entries concerned; later the permission itself on `g0.svc.k` of that service |
| `g0.fb.ii` | (ii) Restrict the commons to open-weight models run by members or on free hosted services, after their own terms check | `decision_record`; the entries concerned go through `g0.svc.*` like any service; license checks for local models follow S7.* [V] |
| `g0.fb.iii` | (iii) A human-review-only commons | `decision_record`; confirmation that `ff.channel.human_review` is configured |
| `g0.fb.iv` | (iv) Stop, and publish what was learned | `decision_record`; link to the published write-up |

### 14.5.4 G1, safety (scope `global`, role `operator`)

FD section 8.3 G1 asks for a written threat model for Iranian participants. S10.* owns the content (threat table `THR-nn`, data inventory, retention). These items are the sign-off points. [D]

| `catalog_key` | What must be attached | Machine check at attach | Watch |
| --- | --- | --- | --- |
| `g1.data_inventory` | Inventory of everything the platform stores, mapped to retention classes (0.7) | CI artifact `schema lint`: every table has a retention class and no column stores a raw IP, a clear e-mail, a provider credential, a provider session or chat-page text (0.7). The lint is also a standing CI check (S18.*); a later failure blocks the merge, not the launch | none |
| `g1.observer` | What a network observer and the host can see, per surface | none | none |
| `g1.compelled` | Who could compel disclosure, what a subpoena or seizure yields, and the resulting decisions | none | none |
| `g1.logging_retention` | Decisions on logging and retention | Parameter values equal the evidence: `retention.raw_ip_stored` false, `analytics.third_party_trackers` false, `analytics.cookies_enabled` false, `public.location_display` `never` | `parameters(retention.*, analytics.*, public.location_display, identity.email_optional)` |
| `g1.threat_table` | The S10.* threat table with every required threat, mitigation and residual risk | CI artifact: every `THR-nn` row has non-empty mitigation and residual-risk fields | none |
| `g1.member_notice` | The member-facing notice, drafted with someone qualified to advise (FD section 8.3 G1) | Hash of the deployed `fa` and `en` text of the notice keys equals the evidence | `copy_bundle(copy.privacy., copy.risk.)` |
| `g1.risk_ack` | Report showing that the first-contribution flow cannot complete without the explicit risk acknowledgement of FD section 9 Phase 1 | CI artifact of the end-to-end test | `copy_bundle(copy.risk.)` |

### 14.5.5 G2, technical feasibility (role `operator`; measurements are `TEC`)

All results are [V] until measured on real phones and desktops. Evidence is a measurement report with the device matrix; testers are never identified (`EV-6`). [D]

| `catalog_key` | Scope | What must be attached | Machine check or watch |
| --- | --- | --- | --- |
| `g2.device_matrix` | global | The list of phones, desktops, browsers and networks used | none |
| `g2.svc.prefill` | service | Prefill support and URL length limit measured on the matrix | Registry `adapter.supports_prefill`, `adapter.max_url_chars` equal the report; watch `adapter(svc)` |
| `g2.clipboard` | global | The clipboard flow (copy, open, paste-back) on the matrix | none |
| `g2.copy_error_rate` | global | Measured copy-and-paste error rate, with sample size | `calibration_ref` to the `CalibrationRecord` rows used |
| `g2.result_return` | global | The paste-back path works end to end; replay, forgery and size-limit tests pass | CI artifact of the adversarial suite |
| `g2.reachability` | global | Reachability of the host from Iran as an outcome `reachable`, `partial` or `blocked`, with the method and date. A `blocked` result is signed as `not_satisfied`, which blocks any launch that requires G2 and triggers the hosting decision in S4.* [V] | none |
| `g2.rtl` | global | Persian right-to-left and mixed-direction rendering on the matrix | CI artifact of the RTL suite |

### 14.5.6 G3, empirical calibration (role `operator`; measurements are `CAL`)

| `catalog_key` | Scope | What must be attached | Machine check or watch |
| --- | --- | --- | --- |
| `g3.svc.throughput` | service | Cells per day a free account completes before limits bite | `CalibrationRecord` count for the service at least `calibration.min_samples_per_service`; `calibration_ref` auto-attached |
| `g3.svc.seconds` | service | Seconds per cell | same |
| `g3.svc.failures` | service | Refusal and failure rates | same |
| `g3.tpl.consistency` | template | Consistency across services on this template | `template_set`; at least two services with the minimum samples |
| `g3.envelope_defined` | global | Decision that fixes the cell envelope and timing: for each of `cell.envelope.max_input_chars`, `cell.envelope.max_output_chars`, `cell.envelope.max_submission_bytes`, `cell.envelope.expected_time_s`, `lease.timeout_s`, `lease.submit_grace_s`, `verify.timing_min_s`, either a `calibration_source` pointer to the evidence or an explicit decision to keep the default | `parameters(cell.envelope.*, lease.*, verify.timing_min_s)`; constraint `C3` holds |
| `g3.mint_cap_decision` | global | Decision that fixes `mint.monthly_cap_credits` and `mint.per_member_daily_cap_credits` from `CAL` or a founders' decision (`FND`); never above forecast redeemable capacity (0.10.6) | `parameters(mint.*)` |

Signing an item does not change any parameter. Replacing a default is still a parameter change: prospective, versioned and logged (0.10.3). [D]

### 14.5.7 G4, repo review and secret rotation (role `operator`)

The existing panel repo is unreviewed [V] (prompt J). The source review in `docs/source/panel-review.md` is facts from static reading by the owner's tooling; it ran nothing and lists what it could not determine. It is an input to these items, not a substitute for a human reading the code. [P]

| `catalog_key` | What must be attached | Machine check or watch |
| --- | --- | --- |
| `g4.repo_review` | Report of a human review of the code and `docs/` of the panel repo | none |
| `g4.panel_dispositions` | A disposition (keep, wrap, replace, not applicable, accepted risk) for each of the 15 numbered weaknesses in section 4.5 of the panel review | Evidence lists all 15 numbers |
| `g4.panel_unknowns` | An owner and a status (verified, out of scope, accepted risk) for each item in section 9 of the panel review ('things I could not determine') | Evidence lists every item |
| `g4.keep_wrap_replace` | Decision per concept (cells, leases, status graph, bottleneck view, Release and Hand over) feeding S4.* | none |
| `g4.secret.panel_token`, `g4.secret.admin_token`, `g4.secret.github_token`, `g4.secret.mcp_auth_token` | The four secrets of FD section 10, one item each (see below) | Validity formula in S14.6.3 |
| `g4.secret.ext_token` | The fifth secret found by static reading (`EXT_TOKEN`, panel review section 4); evidence may instead show it is unset and its route removed [V] | same |
| `g4.secret.register` | Every secret in the S10.* register (the new ones) has a rotation record | Watch `secret_register` |

Evidence of every `g4.secret.*` item: (1) `secret_audit_note` on where the secret is read, logged and stored; (2) `rotation_record` with the date (`occurred_at`) and an identifier fingerprint, never the value; (3) `history_scan_report` of version control and CI logs for old values [V]; (4) an attestation that the old value was revoked and a test with it fails. If the panel code is not reused, the evidence is revocation instead of rotation. `security.rotate_before_public_exposure` is a constant `true` (0.10.6), so all `g4.secret.*` items are required for every launch switch regardless of `launch.required_gate_ids` (S14.7, `ISS-141`). [D]

### 14.5.8 G5, demand check (role `operator`; measurements are `DEM`)

FD section 8.3 G5 says 'a handful' of interviews. The tool invents no minimum; it records the count and the signers attest that it is enough (`ISS-141` lists this as an owner decision). Evidence is anonymized summaries (`interview_summary`). [D]

| `catalog_key` | What must be attached | Replaces defaults of |
| --- | --- | --- |
| `g5.interviews` | Interview summaries and their count | none |
| `g5.job_sizes` | What big jobs requesters really have | `credit.member_cap_credits`, `admission.max_job_cells` |
| `g5.splittable_nonsensitive` | Whether those jobs split into independent cells and are public or non-sensitive (S0 or S1) | template set priorities |
| `g5.windows` | What completion window they would accept | `admission.min_window_s`, `admission.max_window_days` |

## 14.6 Evidence, sign-off and validity

### 14.6.1 Attaching evidence

Attaching evidence never asserts an outcome; it only makes sign-off possible. An item can receive evidence in state `open` (becoming `evidence_attached`) or `evidence_attached` (replacing the evidence set hash), following `EV-1`..`EV-6` and the state machine of S14.4.6. System-attached evidence (`terms_copy_ref`, `flag_answer_ref`, `calibration_ref`, `ci_artifact`) is written by the service identity `system` inside the same transaction as the event that produced it (saving a `TermsCopy`, saving a `FlagAnswer`, writing a `CalibrationRecord`, a CI run reporting its result), never by a later poll. [D]

### 14.6.2 Sign-off guards `SO-1`..`SO-8`

`gate.signed_off` succeeds only if all hold; a failure returns `FORBIDDEN` with `details.reasons` naming every failed guard, not only the first (fail-closed rule 1). [D]

- `SO-1` The item is in `evidence_attached`. Signing from `open` is impossible by construction; there is no evidence yet to sign.
- `SO-2` At least `launch.min_signoffs` (default 2) `GateSignoff` rows exist for `(item_id, item_generation)` whose `evidence_set_hash` equals the item's current evidence set hash, recomputed fresh at the moment of the check, never read from a cache.
- `SO-3` Among those rows, at least one has `acted_as_role` equal to the item's `required_role`.
- `SO-4` The qualifying rows come from at least two distinct `admin_user_id` values (R10's two-person rule; a single admin cannot sign the same item twice under two credentials to satisfy `SO-2`).
- `SO-5` All qualifying rows carry the same `outcome`; signers who disagree record `not_satisfied` or a note, and the item stays `evidence_attached` until agreement, or an admin with `perm.launch.reopen` starts a fresh generation to reset the discussion. The tool does not arbitrate disagreement (ground rule 8).
- `SO-6` The chosen `outcome` is one the item's `kind` allows: `attestation`, `evidence` and `measurement` items allow `satisfied`, `satisfied_with_conditions`, `not_satisfied`; `decision` items allow only `adopted`, `declined`; `machine_check` items are set by the system only, from the referenced check's own result, and never by a human `GateSignoff` (`SO-8`).
- `SO-7` If the item is a G0 service flag item, the outcome rule of S14.5.1 holds: `satisfied` is refused by the server (not merely by convention) when any required gate flag is `no`, `unknown` or absent for the current `TermsCopy`; the check reads `FlagAnswer` rows directly rather than trusting the signers' evidence note.
- `SO-8` `outcome = satisfied_with_conditions` requires non-empty `conditions_text` on every qualifying `GateSignoff`, and the qualifying rows' `conditions_text_hash` values are identical (the signers signed the same conditions, not merely the same outcome label).

When all guards pass, the item moves to `signed_off`; `outcome`, `signed_off_at = now`, `valid_until` (S14.6.3) and `watch_digest` (S14.6.4) are set from the qualifying generation, and `reevaluate_dependents` runs in the same transaction (S14.7). [D]

### 14.6.3 Validity: `valid_until`

Every signed item gets a `valid_until`, computed at sign-off from the catalog's validity rule for that `catalog_key` and the evidence's `occurred_at` values. An item past its `valid_until` is evaluated as not valid everywhere this part reads 'signed and valid' (`GI-02`); a nightly sweep also reopens it with `reopen_reason = expired`, but the real-time predicates in S14.7 never rely on the sweep having already run — they compare `now` to `valid_until` directly. [D]

| Validity class | Formula | Applies to |
| --- | --- | --- |
| Generic | `signed_off_at + param('launch.generic_validity_days') * 86400` | Items with no more specific rule |
| Terms-bound | `min(generic, terms_copy.captured_at + param('service.review_max_age_days') * 86400)` | `g0.svc.*` |
| Counsel | `signed_off_at + param('launch.counsel_validity_days') * 86400` | `g0.cns.*` |
| Secret rotation | `rotation_record.occurred_at + param('security.secret_rotation_max_age_days') * 86400` | `g4.secret.*` |
| Measurement | `max(occurred_at of evidence) + param('launch.measurement_validity_days') * 86400` | `g2.*`, `g3.*`, `g5.*` |
| Non-expiring | `null` (never expires by time; still reopened by a watched change) | `g1.*` structural items, `decision` items |

Parameter defaults (S16.* holds the authoritative table; these are the ones this part introduces): `launch.generic_validity_days` 180, `launch.counsel_validity_days` 365, `security.secret_rotation_max_age_days` 90, `launch.measurement_validity_days` 120. [A]

### 14.6.4 Watch descriptors and automatic reopening

A watch descriptor names a value; its digest is included in `watch_digest` at sign-off. A background check (and, for parameters, a synchronous check inside the same transaction that changes the watched value) compares the current digest to the stored one; a mismatch reopens the item with `reopen_reason = watched_change`, in the same transaction as the change when the change is itself a parameter write or a `TermsCopy`/`FlagAnswer` save, and otherwise within one run of the nightly sweep. [D]

Descriptors used above: `terms_hash(svc)` hashes the latest `TermsCopy.content_hash` of the service; `flag_answers(svc)` hashes the sorted `{key, answer, terms_copy_id}` of its latest `FlagAnswer` rows; `parameters(prefix.*)` hashes the current values of every parameter matching the prefix; `copy_bundle(prefix.*)` hashes the deployed copy text for keys matching the prefix in both `fa` and `en`; `adapter(svc)` hashes the registry's adapter fields for the service; `secret_register` hashes the sorted `{secret_name, last_rotated_at}` of the S10.* register; `template_set` hashes the sorted list of service ids approved for the template. [A]

### 14.6.5 Reopening a service item and its effect on the registry

When any `g0.svc.*` item of a service is reopened for any reason, the service moves from `approved` to `review_due` in the same transaction (`RL-7`); it does not drop straight to `unreviewed`, because `review_due` preserves the grace period of S14.3's gate-obligations table and avoids silently aborting in-flight cells. If the grace period elapses without the item returning to `signed_off` and valid, a scheduled check moves the service to `suspended`, which has no grace period. [D]
