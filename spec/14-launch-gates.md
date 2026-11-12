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
