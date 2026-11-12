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
