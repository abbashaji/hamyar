# 5. State machines, idempotency and concurrency

*Spec part 5b (the second file of part 5; the entity model is part 5a) · owner cell C-004 · binding on S6.*, S7.*, S8.*, S9.*, S15.* and S18.* · Written against Founding Document draft v0.1 (FD) and `spec/00-conventions.md` (S0). Nothing here is legal advice and nothing here has been verified against any provider's terms or any law.*

## 5.21 Scope, reading guide and rules common to every machine

S0.9 fixes the names of states and events. This part fixes everything else about them: guards, side effects, ledger effects, audit-log entries and the concurrency mechanism that makes each transition safe. It then states exact guarantees for leasing, submission and settlement (5.29), a race table (5.30) and Given/When/Then tests (5.31). Where this part and S0.9 disagree, the disagreement is a convention gap listed in `## Issues raised`, and the resolution written here applies until `C-001` records another. [D]

**Heading numbers.** Part 5 is split over two files. `spec/05a-domain-model.md` is assumed to use `5.1`..`5.19`; this file uses `5.21`..`5.39`, so every `S5.<m>` reference resolves to one heading (convention addition 1). [A: C-001 confirms at assembly]

### 5.21.1 Transition tables: columns and ids

| Column | Meaning |
| --- | --- |
| id | Local label of one transition: `JT` Job, `CT` Cell, `LT` Lease, `SBT` Submission, `MT` member tier, `MS` member status, `TT` template, `SVT` service, `APT` appeal, `ET` escrow, `RT` reservation. Labels are used in this file and in the `AC-*` criteria of 5.31; they are not a new global id scheme [A] |
| from, event, to | As in S0.9. A comma in `from` means any of those states. In prose a state is written with its machine (`Cell.expired`) |
| guard | Predicates evaluated inside the transition's own transaction. A failed guard changes nothing and emits nothing; an API caller gets the error shown, a system actor skips the candidate (S0.9.1) |
| side effects | Other rows written in the same transaction, and work queued through the outbox |
| ledger effects | Ledger transaction kind (`ledger_txn_kind`, S0.8.5), entry types, amounts in `ucr` and the idempotency key (5.29.5). `none` means the transition never touches the ledger |
| audit-log entry | The event name plus the keys added to `details` (5.21.3). `+AA` means an `AdminAction` row is written in the same transaction because the actor is an `admin` |

Permission names written `perm.<area>.<action>` in these tables are proposals for the matrix owned by S10.* [A].

### 5.21.2 Transition atomicity rule [D]

Every state change is exactly one database transaction containing, together:

1. the compare-and-set (CAS) update of the entity row: `UPDATE <table> SET state = :to, row_version = row_version + 1, updated_at = now() WHERE id = :id AND state = :from AND row_version = :seen`, accepted only when exactly one row is affected (S0.7 gives every mutable table `row_version`);
2. one `StateTransition` row (5.21.3);
3. one outbox event with the name shown in the table (S0.9.1);
4. the ledger transaction, if the table names one;
5. for an API-triggered change, completion of the idempotency record (S0.11.5).

Any failure rolls back all five. No code path writes a `state` column except one `transition()` function that implements this rule; a CI lint forbids other writes [D]. A transition that is not listed in a table does not exist: a request for it is `409 STATE_CONFLICT` with `details.reason` = `transition_not_allowed` and emits nothing. [D]

### 5.21.3 Audit log: the `StateTransition` record and the event envelope [D][A]

S0.9.1 requires every state change to emit one event carrying `event_version`, `occurred_at`, `actor` and the policy and parameter versions in force. That event is stored in the outbox and logged as an `Event`, whose retention class is `ops` (`retention.event_raw_days`, initial configurable default 30 days). FD§3.4 says every transition is logged with the policy version, and an appeal (`appeal.window_days`, 14 days) or a provenance question can outlive a raw log, so `ISS-55` adds one append-only entity:

| Entity | Table | Prefix | Retention | Why |
| --- | --- | --- | --- | --- |
| `StateTransition` | `state_transitions` | `stt_` | class of the parent entity (`job_bound`, `member_bound`, `moderation` or `permanent`), kept in column `retention_class` | Durable, ordered history of every transition of every machine in this part |

Columns: `id`; `entity_type` (an entity name, S0.7); `entity_id`; `entity_seq` (1, 2, 3, ... per entity, unique with `entity_type, entity_id`; a gap is a defect and is checked by CK-07, 5.29.10); `from_state`; `to_state`; `event_name` (S0.9); `event_id` (the outbox event); `reason_code` (a `policy.<rule>.<slug>`, `reject.*` or closure code; nullable); `policy_version_id`; `parameter_versions` (json: ids of the `ParameterVersion`s the guard read); `actor_type` (S0.8.2); `actor_id` (opaque `mem_`, `adm_` or a job name; never a `vol_` handle, never an IP); `occurred_at`; `details` (json; no personal data; never the content of a submission); `retention_class`; `created_at`. No update path, no delete path.

The audit-log column of every table lists `event_name` and the keys added to `details`. Envelope fields (actor, versions, time) are implied and not repeated. [D]

### 5.21.4 Triggers, actors and time [D]

- Actors are the `principal_type` values of S0.8.2. A transition fired by a timer or worker has actor `system` and the worker's name as `actor_id`; the names are in 5.29.10.
- Every comparison with a stored time (`expires_at`, `hard_expires_at`, `quote_expires_at`, deadlines) is made by the database, in the same statement as the CAS, with the database clock. It never uses an application-server clock or a client clock (S0.6.2). [D]
- Lock order, which keeps the transactions of this part deadlock-free, is in 5.29.2; storage requirements are in 5.29.1.

## 5.22 Job state machine

States, events and names are S0.9.2. [D]

```
HAPPY PATH
 draft --submitted--> screening --policy_passed--> quoted --escrow_confirmed--> admitted --started--> running
 running --all_cells_accepted--> assembling --assembled--> settling --settled--> completed (T)

BRANCHES
 screening --policy_rejected--> rejected (T)
 quoted --quote_expired--> quote_expired (T)
 quoted --waitlisted--> waitlisted --waitlist_released--> quoted
 waitlisted --waitlist_expired--> cancelled (T)
 admitted, running --paused--> suspended --resumed--> admitted or running (the state it left)
 admitted, running, suspended --stop_requested--> settling --settled_partial--> failed (T)
 admitted, running, suspended --cancel_requested--> cancelling --cancel_settled--> cancelled (T)
 draft, screening, quoted, waitlisted --cancel_requested--> cancelled (T)
```

| id | from | event | to | guard | side effects | ledger effects | audit-log entry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| JT-01 | (none) | `job.created` | draft | Caller is a `member` (member job) or an `admin` with `perm.job.create_commons` (Commons job); for a member job `launch.member_jobs_enabled` is true, else `403 LAUNCH_GATE_CLOSED`; `kill.all_new_jobs` is released, else `503 KILL_SWITCH_ENGAGED`; `Idempotency-Key` present | none | none | `job.created {job_type, origin}`; +AA for a Commons job |
| JT-02 | draft | `job.submitted` | screening | Wizard complete: template version `approved`; upload stored with its hash and size <= `job.max_upload_bytes`; the four declarations of FD§5.2 present; caller is not inside `identity.recovery_cooldown_s` | Enqueue screening: policy evaluation (S7.*), input screening (S9.*), reviewer sampling by `screen.review_rate_new_requester` or `screen.review_rate_established_requester` | none | `job.submitted {template_version_id, upload_hash}` |
| JT-03 | screening | `job.policy_rejected` | rejected (T) | At least one rule fails (the first failing rule of R1..R10 in order, S7.*), or input screening returns a reject finding with `screen.pii_action` = `reject` | Store reasons as `policy.<rule>.<slug>`; schedule payload purge after `retention.job_payload_days`; appeal path `job_rejection` opens | none | `job.policy_rejected {reasons[]}`; `reason_code` = first reason |
| JT-04 | screening | `job.policy_passed` | quoted | All rules pass; template version `approved` and `kill.template.<tpl_id>` released; every pinned service (M1) is `approved`, or at least one approved service covers M0 | Stamp `policy_version_id` (R9); compute the quote: N, `v_ppm`, `lambda_ppm`, `p_ucr`, `escrow_ucr`, window, each with the `ParameterVersion` used; set `quote_expires_at` = now + `price.quote_ttl_s` | none (a quote is not a hold) | `job.policy_passed {policy_version_id, escrow_ucr, window_s, quote_expires_at}` |
| JT-05 | quoted | `job.quote_expired` | quote_expired (T) | Timer `quote_expirer`: now >= `quote_expires_at` | Purge nothing; the requester may create a new job from the same upload while it is retained | none | `job.quote_expired {}` |
| JT-06 | quoted | `job.waitlisted` | waitlisted | Admission (S6.*) cannot honor the window now; the member's waitlisted jobs < `admission.waitlist_max_per_member` | Waitlist entry (`WaitlistEntry`) with expiry now + `admission.waitlist_ttl_days` | none | `job.waitlisted {position}` |
| JT-07 | waitlisted | `job.waitlist_released` | quoted | Capacity now honors the window; first-come order within the deadline class (FD§4.8) | New quote (as JT-04, new `quote_expires_at`); notify the requester | none | `job.waitlist_released {quote_expires_at}` |
| JT-08 | waitlisted | `job.waitlist_expired` | cancelled (T) | Timer `waitlist_expirer`: now >= entry expiry | Release the waitlist entry | none | `job.waitlist_expired {}` |
| JT-09 | quoted | `job.escrow_confirmed` | admitted | All inside one transaction with the member's account row locked: now < `quote_expires_at`; member `active` and outside `identity.recovery_cooldown_s`; the member's jobs in admitted, running, suspended, assembling, settling or cancelling < `admission.max_concurrent_jobs_per_member`; unexpired spendable balance >= `escrow_ucr`, else `422 INSUFFICIENT_CREDIT`; capacity re-checked and booked atomically (S6.*), else `422 NO_CAPACITY`; policy re-evaluated against the current `PolicyVersion`, else `422 POLICY_REJECTED`; template and services still approved. The quote is honored: a parameter change after the quote does not re-price it (the quote carries its versions) [D] | Create the `Escrow` (`open`) and its `escrow` ledger account; create the N primary cells in `queued` (unique `(job_id, ordinal)`, so a retried creation cannot duplicate); one `cell.created` per cell | `hold` txn: `escrow_hold` member -> escrow of `escrow_ucr`, lots consumed oldest-first; key `hold:<job_id>` | `job.escrow_confirmed {escrow_ucr, n_cells, quote_id}`; also `escrow.opened` |
| JT-10 | admitted | `job.started` | running | The first `cell.leased` of the job (fired in the same transaction as CT-02) | Set `started_at` | none | `job.started {}` |
| JT-11 | admitted, running | `job.paused` | suspended | Job not terminal; a pause cause is added to `pause_causes` (set of `kill_template`, `kill_service`, `kill_member`, `policy_tightened`, `template_paused`, `service_suspended`). If the job is already suspended only the set changes and no event is emitted | Record `state_before_pause`, `pause_started_at`; start the fan-out (5.29.10, `job_fanout_worker`): queued cells -> `suspended`, leased cells -> lease revoked then `suspended`; submitted cells are not paused (see `G-accept`) | none (escrow stays held; escrow does not stop lot expiry, ISS-07) | `job.paused {cause, source_ref}` |
| JT-12 | suspended | `job.resumed` | the state it left | The cause that just cleared was the last member of `pause_causes`; for cause `policy_tightened` the re-evaluation passes (5.22.2) | `paused_total_s` += now - `pause_started_at` (extends the overrun deadline, so a pause never causes `overrun_timeout`) [A]; cells `suspended` -> `queued`; re-enqueue deferred acceptances | none | `job.resumed {state}` |
| JT-13 | running | `job.all_cells_accepted` | assembling | Fired by the `job_progress` worker, never inside an acceptance transaction: under the job row lock, count of accepted primary cells = N | Create the `Deliverable` and `Manifest` (S9.*); cancel queued non-primary cells (`cell.cancelled`); no new non-primary cell may be created (creation guard, 5.23) | none | `job.all_cells_accepted {n}` |
| JT-14 | assembling | `job.assembled` | settling | `Deliverable` and `Manifest` persisted with hashes | Escrow `open` -> `settling` (ET-02) | none | `job.assembled {deliverable_hash}` |
| JT-15 | admitted, running, suspended | `job.stop_requested` | settling | `closure_reason` in `policy_stopped`, `service_revoked`, `template_retired`, `operator_killed`, `overrun_timeout`, `cells_exhausted`. For `overrun_timeout`: now >= `admitted_at` + `job.max_overrun_ratio` x quoted window + `paused_total_s`. For `cells_exhausted`: no primary cell non-terminal and at least one `exhausted`. Otherwise an `admin` with `perm.job.stop` and a reason, or the system acting on the cause event | Stop fan-out by reason (table 5.22.1); escrow -> `settling` (ET-02) | none | `job.stop_requested {closure_reason}`; +AA when an admin |
| JT-16 | settling | `job.settled` | completed (T) | All cells terminal; every primary cell `accepted`; escrow `settling` (a Commons job has no escrow, see 5.22.3) | `settle()` of 5.29.8 in the same transaction; escrow `settling` -> `closed` (ET-03); deliverable released to the requester; payload purge scheduled | `settle` txn: `levy` escrow -> reserve of `levy_due_ucr`; `refund` escrow -> member of the remainder (lots restored with original expiry, ISS-07); escrow balance exactly 0; key `settle:<job_id>` | `job.settled {levy_ucr, refund_ucr, payouts_ucr}` |
| JT-17 | settling | `job.settled_partial` | failed (T) | All cells terminal; at least one primary cell not `accepted` | As JT-16; the accepted outputs stay downloadable as a partial deliverable (S11.*) | As JT-16 with `levy_due_ucr` computed on accepted primary cells | `job.settled_partial {accepted, n, closure_reason, levy_ucr, refund_ucr}` |
| JT-18 | admitted, running, suspended | `job.cancel_requested` | cancelling | Caller is the requester or an `admin` with `perm.job.cancel`; job is not in assembling or settling (else `409 STATE_CONFLICT`) | Queued and suspended cells -> `cancelled`; leased cells keep their lease and drain (CT-15 note); no new lease (guard of CT-02); escrow -> `settling` (ET-02) | none | `job.cancel_requested {by}`; +AA when an admin |
| JT-19 | draft, screening, quoted, waitlisted | `job.cancel_requested` | cancelled (T) | As JT-18 | Release the waitlist entry; purge the upload payload per `retention.job_payload_days` | none (nothing is held before JT-09) | `job.cancel_requested {by}` |
| JT-20 | cancelling | `job.cancel_settled` | cancelled (T) | All cells terminal | As JT-16 | `cancel` txn: `levy` of `levy_due_ucr` on accepted primary cells, `refund` of the remainder; key `cancel:<job_id>` | `job.cancel_settled {levy_ucr, refund_ucr, payouts_ucr}` |

`screening --job.cancel_requested--> cancelled` (in the JT-19 `from` list) is a convention gap: with `screen.review_rate_new_requester` = 1.0 a job can wait in `screening` for a human, so a requester must be able to cancel it (convention addition 3). [D]

### 5.22.1 Stop fan-out by closure reason [D]

| `closure_reason` | Queued and suspended cells | Leased cells | Submitted and flagged_for_audit cells | Why |
| --- | --- | --- | --- | --- |
| `policy_stopped` | `voided` | lease revoked, cell `voided` | `voided` at `G-accept` (R9) | A change may stop work in flight but never retroactively legitimizes it |
| `service_revoked` | `voided` | lease revoked, cell `voided` | per the revocation's `inflight_policy`: `drain` continues to acceptance, `void` voids (S7.* chooses; 5.26) | The terms review decides whether work already done is tainted [V] |
| `template_retired` | `voided` | lease revoked, cell `voided` | `voided` | Only `withdrawn_for_cause` stops jobs (5.25); `superseded` never does |
| `operator_killed` | `voided` | lease revoked, cell `voided` | `voided` | An operator stop means the work must not pay |
| `overrun_timeout` | `cancelled` | drain: the lease runs to `hard_expires_at`, then the cell is `cancelled`, not requeued | continue to acceptance and are paid | The overrun is the platform's, not the donors' |
| `cells_exhausted` | `cancelled` (non-primary cells only) | drain, as above | continue to acceptance and are paid | No primary cell is still in play |

`cells_exhausted` is a convention addition (4): S0.9.2 lists no path from `running` to `settling` when a primary cell hits `cell.max_attempts`. [D]

### 5.22.2 Pause causes and policy tightening [D]

- On `policy.version_published` with `change_class` = `tighten` (R10), every non-terminal job is paused with cause `policy_tightened` at once (JT-11). The `policy_tighten_sweep` worker (5.29.10) re-evaluates each job's stamped declarations and service against the new version (S7.*): if still permitted it emits `job.resumed` (JT-12); if not, `job.stop_requested` with `closure_reason` = `policy_stopped`. A pause caused by tightening therefore lasts one sweep, not an indefinite time.
- Kill switches map as follows: `kill.template.<tpl_id>` -> `kill_template`; `kill.service.<svc_id>` -> `kill_service` for jobs pinned (M1) to it; `kill.member.<mem_id>` -> `kill_member` for that member's jobs; `kill.all_new_jobs` and `kill.all_minting` never pause an admitted job (they block JT-01/JT-09 and Commons leasing). [D]

### 5.22.3 Commons jobs [D][A]

A Commons job runs the same machine with these differences: JT-01 by an `admin`; JT-04 quotes price 0 and no window; JT-09 is confirmed by an `admin` and posts no `hold` and creates no `Escrow`; there is no `levy`, no `refund` and no `settle` transaction, so JT-16 and JT-17 only change state; cells mint on acceptance (CT-06) instead of paying from escrow. A Commons job's `running` state never times out on `overrun_timeout` (it has no quoted window). `launch.minting_enabled` and `kill.all_minting` gate its leasing (5.29.3).

## 5.23 Cell, Lease and Submission state machines

States and events are S0.9.3. A `Cell` row persists across attempts and carries `attempt` (starts at 1, limit `cell.max_attempts`); each attempt has its own `Lease` and at most one `Submission` (5.29.4). [D]

```
CELL, one attempt
 queued --leased--> leased --submitted--> submitted --checks_passed--> accepted (T) --overturned--> overturned (T)
                      |   |                    +--flagged_for_audit--> flagged_for_audit --audit_passed--> accepted
                      |   |                    |                                    +--audit_failed--> rejected
                      |   |                    +--checks_failed--> rejected
                      |   +--lease_expired--> expired
                      +--declined--> queued
 rejected, expired --requeued--> queued (attempt + 1)      rejected, expired --attempts_exhausted--> exhausted (T)
 queued, leased --paused--> suspended --resumed--> queued
 any non-terminal --cancelled--> cancelled (T)            any non-terminal --voided--> voided (T)

LEASE:  (none) --issued--> active --submission_received--> submitted
                           active --expired--> expired   active --released--> released   active --revoked--> revoked
SUBMISSION: (none) --received--> received --checks_passed--> checks_passed --accepted--> accepted (T)
            received --schema_failed--> schema_failed (T)   received --checks_failed--> checks_failed (T)
            received --quarantined--> quarantined --released_from_quarantine--> checks_passed
            checks_passed, flagged cell --rejected--> rejected (T)
```

### 5.23.1 Cell transitions

| id | from | event | to | guard | side effects | ledger effects | audit-log entry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CT-01 | (none) | `cell.created` | queued | Primary cells: created only by JT-09 (member job) or an admin-confirmed Commons job. Non-primary cells (`gold`, `audit`, `third`, `review`, `rework`): job in `admitted` or `running`, and for a member job the creation guard `pool_ok` holds: `payable_ucr(job) - committed_ucr(job) >= 1,000,000`, where `payable_ucr` = escrow balance minus `levy_reserved_ucr` (= N x `lambda_ppm`, stamped at JT-04) and `committed_ucr` = 1,000,000 x non-terminal non-primary cells. This makes it impossible to create a cell that escrow cannot pay [D] | Unique `(job_id, ordinal, cell_kind)`; `attempt` = 1 | none | `cell.created {cell_kind, ordinal, template_version_id}` |
| CT-02 | queued | `cell.leased` | leased | `G-leasable` of 5.29.3 (member active and opted in, job and template and kill switches allow, independence, caps, headroom) and the CAS of 5.29.3 | Create the `Lease` (LT-01) with nonce, `expires_at`, `hard_expires_at`; reserve earning headroom (5.29.3); first lease of a job fires JT-10 | none | `cell.leased {lease_id, attempt}` |
| CT-03 | leased | `cell.submitted` | submitted | The lease is `active`, owned by the caller, nonce matches, and the database clock is <= `hard_expires_at` (5.29.4); body <= `cell.envelope.max_submission_bytes` | Create the `Submission` (SBT-01); lease -> `submitted` (LT-02); enqueue the verification pipeline (S8.*, S9.*) | none | `cell.submitted {submission_id, late}` where `late` = clock > `expires_at` |
| CT-04 | leased | `cell.lease_expired` | expired | Reaper: lease `active` and clock > `hard_expires_at` | Lease -> `expired` (LT-03); release headroom reservation; no trust effect (an expiry is not evidence about quality) [D] | none | `cell.lease_expired {lease_id}` |
| CT-05 | leased | `cell.declined` | queued | Caller owns the active lease; no penalty and no cooldown (FD§5.5, `lease.decline_cooldown_s` = 0) | Lease -> `released` (LT-04) with `release_reason` in `declined`, `reported`; a report also files a `Report`; release headroom | none | `cell.declined {initiator: member, release_reason}` |
| CT-18 | leased | `cell.declined` | queued | System revokes a lease for a cause that is not the cell's fault: `member.suspended`, `member.banned`, `kill.member`, a closed session policy | Lease -> `revoked` (LT-05); release headroom | none | `cell.declined {initiator: system, cause}`. The decline-rate metric counts only `initiator` = member [D] |
| CT-06 | submitted | `cell.checks_passed` | accepted (T) | Submission `checks_passed`; not selected for audit (decided by S8.*); `G-accept` returns ACCEPT (below) | Submission -> `accepted` (SBT-08); release or consume headroom; enqueue `tier_evaluator` for the donor; if gold, record a reliability observation | Commons job: `mint` txn, entry `mint` issuance -> member 1,000,000 `ucr`, new lot, key `mint:<cell_id>`. Member job: `payout` txn, entry `transfer` escrow -> member 1,000,000 `ucr`, new lot, key `payout:<cell_id>` | `cell.checks_passed {verification_methods[], policy_version_id}` |
| CT-07 | submitted | `cell.flagged_for_audit` | flagged_for_audit | Submission `checks_passed` and (sampled with the adaptive rate, or anomaly, or blanket redundancy pending, or a high-risk template; S8.*) | Create the `Audit` (`pending`) and its audit cell through CT-01 (needs `pool_ok` in a member job); the audit cell cannot be leased by anyone in `independence_set` (5.29.3) | none | `cell.flagged_for_audit {audit_id, trigger}` |
| CT-08 | submitted | `cell.checks_failed` | rejected | Submission `schema_failed` or `checks_failed`, a gold mismatch, a timing or duplicate finding (S9.*), or `G-accept` returns REJECT_POLICY | Submission -> `schema_failed` or `checks_failed` (SBT-02, SBT-04); release headroom; set reason `reject.*` visible to the donor with an appeal link (APT-01); two consecutive gold failures feed MT-06; a `reject.policy_changed` result is not a reliability observation [D] | none (a rejected cell earns nothing) | `cell.checks_failed {reason_code}` |
| CT-09 | flagged_for_audit | `cell.audit_passed` | accepted (T) | `Audit` `matched`, or `resolved` in favor (third execution); `G-accept` returns ACCEPT | As CT-06 | As CT-06 | `cell.audit_passed {audit_id}` |
| CT-10 | flagged_for_audit | `cell.audit_failed` | rejected | `Audit` `resolved` against the submission | Submission -> `rejected` (SBT-09); release headroom; reason `reject.audit_mismatch` | none | `cell.audit_failed {audit_id}` |
| CT-11 | rejected, expired | `cell.requeued` | queued | `attempt` < `cell.max_attempts`; job in `admitted` or `running` (for a job in a drain, CT-15 applies instead) | `attempt` + 1; the next lease excludes members who already submitted this cell (5.29.3) | none | `cell.requeued {attempt}` |
| CT-12 | rejected, expired | `cell.attempts_exhausted` | exhausted (T) | `attempt` = `cell.max_attempts` | For a primary cell the `job_progress` worker raises `job.stop_requested` with `cells_exhausted` once no primary cell is non-terminal (JT-15) | none | `cell.attempts_exhausted {attempt}` |
| CT-13 | queued, leased | `cell.paused` | suspended | Job `suspended` (JT-11 fan-out); a leased cell's lease is revoked first, in the same transaction | Lease -> `revoked` (LT-05) if leased; release headroom | none | `cell.paused {pause_causes[]}` |
| CT-14 | suspended | `cell.resumed` | queued | Job resumed (JT-12) | none | none | `cell.resumed {}` |
| CT-15 | queued, suspended, expired, rejected, leased (see note) | `cell.cancelled` | cancelled (T) | Job `cancelling`, or `settling` with reason `overrun_timeout` or `cells_exhausted`, or a non-primary cell when JT-13 fires. A `leased` cell is cancelled only with `revoke_lease` = true, which the system uses only for closures that forbid paying (never for a requester's cancel): a requester's cancel lets leased cells drain, and the cell is cancelled instead of requeued when its lease ends [D]. A cell in `submitted` or `flagged_for_audit` is never cancelled: it completes verification and is paid | Lease -> `revoked` if `revoke_lease`; release headroom | none (the escrow share of an unexecuted cell is refunded by `settle`) | `cell.cancelled {closure_or_cancel, revoke_lease}` |
| CT-16 | queued, suspended, leased, submitted, flagged_for_audit, expired, rejected | `cell.voided` | voided (T) | Closure reason that voids (table 5.22.1), `G-accept` returns VOID, or an integrity finding (S9.*) | Lease -> `revoked` if leased; Submission -> `rejected` if it exists; release headroom; no reliability observation | none (never paid) | `cell.voided {reason}` |
| CT-17 | accepted | `cell.overturned` | overturned (T) | A fraud finding or an `Appeal` `overturned` on an acceptance (kind `report_outcome`); two admins (`ledger.reversal` is in `security.two_person_actions`) | Create a `rework` cell (CT-01; funded from the verification pool, counts toward v, ISS-05); reverse the donor's reliability credit | `reversal` txn mirroring the original `mint` or `transfer` entry, key `reversal:<original_txn_id>`; two approvers (`ledger.reversal_min_approvers`). If the donor already spent the lot, the reversal consumes other lots oldest-first; if the balance cannot cover it the reversal is refused and escalated to S6.* [D] | `cell.overturned {finding, reversal_txn_id}`; +AA |

`Cell.expired` and `Cell.rejected` are attempt outcomes: the reaper performs CT-04 and then CT-11 (or CT-15, CT-12) as separate back-to-back transactions. A crash between them leaves the cell in `expired` or `rejected`, which the `cell_requeuer` sweep (5.29.10) finishes. [D]

### 5.23.2 `G-accept`: the acceptance guard [D]

R9 says the policy is re-checked when a result is accepted. `G-accept` is the one function that decides, inside the acceptance transaction (5.29.6), and it returns exactly one of four outcomes. It first takes a shared lock on the policy-pointer row and on the job row (lock order 5.29.2), so a tightening that commits earlier is always seen and an acceptance that commits earlier is legitimately accepted.

| Check, in order | ACCEPT when | Otherwise |
| --- | --- | --- |
| Job state | `admitted`, `running`, `settling` or `cancelling` (the last two only for a drain that the table 5.22.1 allows) | `suspended`: DEFER. Terminal, or a stop reason that voids: VOID |
| Policy (R9) | the current `PolicyVersion` still permits the job's stamped declarations (S7.* evaluator) | VOID with `reject.policy_changed` |
| Template version | `approved` or `retired` with cause `superseded` | `paused`: DEFER. `retired` with cause `withdrawn_for_cause`: VOID |
| Reported service (the donor's attested service, FD§5.6) | `approved` or `review_due` (grace) | `suspended` or `in_review` after a lapse: REJECT_POLICY with `reject.policy_changed` (the donor is not penalized, the cell requeues). `revoked`: per the revocation's `inflight_policy` (5.26) |
| Donor | `member_status` `active` | `suspended`: DEFER. `banned`: VOID |
| Money | Commons: `launch.minting_enabled` true, `kill.all_minting` released, a headroom reservation exists. Member job: `payable_ucr(job) >= 1,000,000` | Commons switch off: DEFER. A missing reservation or insufficient payable amount is a defect: abort the transaction and raise an `Alarm`; the cell stays as it was |

DEFER changes no state and emits no event; it records `acceptance_deferred_until` and the sweeps re-enqueue the cell when the blocking cause clears (`job.resumed`, `template.resumed`, `member.reinstated`, `killswitch.released`). A deferred cell keeps its headroom reservation. Outcomes map to transitions: ACCEPT to CT-06 or CT-09; VOID to CT-16; REJECT_POLICY to CT-08. [D]

### 5.23.3 Lease transitions

| id | from | event | to | guard | side effects | ledger effects | audit-log entry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LT-01 | (none) | `lease.issued` | active | Same transaction as CT-02; unique partial index allows one `active` lease per cell (5.29.3) | Store `nonce_hash` (SHA-256 of 16 random bytes, `lease.nonce_bytes`); `expires_at` = now + `lease.timeout_s`; `hard_expires_at` = `expires_at` + `lease.submit_grace_s`; `extensions` = 0; return the nonce once in the response and never store it | none | `lease.issued {cell_id, expires_at, hard_expires_at}` |
| LT-02 | active | `lease.submission_received` | submitted | Same transaction as CT-03 | Store `submitted_at`; the nonce is spent | none | `lease.submission_received {submission_id}` |
| LT-03 | active | `lease.expired` | expired | Same transaction as CT-04 | none | none | `lease.expired {}` |
| LT-04 | active | `lease.released` | released | Same transaction as CT-05 | none | none | `lease.released {release_reason}` |
| LT-05 | active | `lease.revoked` | revoked | Same transaction as CT-13, CT-15, CT-16 or CT-18 | none | none | `lease.revoked {cause}` |

**Extension (not a state change).** `POST /v1/leases/{lease_id}/extension` adds `lease.extend_s` to `expires_at` and `hard_expires_at` when `extensions` < `lease.max_extensions`, the lease is `active` and the database clock is <= `expires_at`; the update is one CAS (`WHERE state = 'active' AND extensions = :seen AND now() <= expires_at`), so an extension and a reaper expiry cannot both win. It writes a log-only event `lease.extended` (convention addition 5) and no `StateTransition`. [D]

**Expiry semantics, resolving `ISS-54`.** `lease.timeout_s` is the time the donor is told they have (`expires_at`). `lease.submit_grace_s` is part of the lease, not a race: `hard_expires_at` = `expires_at` + grace is stored at issue, the cell cannot be re-leased before `hard_expires_at`, and a submission is valid up to and including `hard_expires_at`. After it the lease is dead for everyone, even if the reaper has not yet run and even if nobody has re-leased the cell, so the outcome never depends on reaper timing. [D]

### 5.23.4 Submission transitions

| id | from | event | to | guard | side effects | ledger effects | audit-log entry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SBT-01 | (none) | `submission.received` | received | Same transaction as CT-03; unique `(lease_id)` | Store content (never executed, escaped on display, S9.*), `content_hash`, byte and character lengths, reported service and model, `time_to_submit_s` | none | `submission.received {content_hash, bytes}` |
| SBT-02 | received | `submission.schema_failed` | schema_failed (T) | Output fails the template's output schema | Cell -> CT-08 with `reject.schema_invalid` | none | `submission.schema_failed {errors[]}` |
| SBT-03 | received | `submission.checks_passed` | checks_passed | Schema and automatic checks pass and the output flagging of S9.* finds nothing | Cell stays `submitted` until CT-06 or CT-07 | none | `submission.checks_passed {check_ids[]}` |
| SBT-04 | received | `submission.checks_failed` | checks_failed (T) | An automatic check, gold comparison or screening fails | Cell -> CT-08 | none | `submission.checks_failed {reason_code}` |
| SBT-05 | received | `submission.quarantined` | quarantined | Output contains links, code to run or a request for action (FD§5.5, `screen.output_url_action` = `quarantine`) | Withheld from results; queued for a reviewer; cell stays `submitted` | none | `submission.quarantined {pattern_ids[]}` |
| SBT-06 | quarantined | `submission.released_from_quarantine` | checks_passed | A reviewer with `perm.submission.release` clears it (quarantine is the last automatic step, so no check remains) | Cell proceeds to CT-06 or CT-07 | none | `submission.released_from_quarantine {}`; +AA |
| SBT-07 | quarantined | `submission.checks_failed` | checks_failed (T) | A reviewer confirms the finding | Cell -> CT-08 with `reject.forbidden_content` | none | `submission.checks_failed {reason_code}`; +AA |
| SBT-08 | checks_passed | `submission.accepted` | accepted (T) | Same transaction as CT-06 or CT-09 | none | as CT-06 | `submission.accepted {}` |
| SBT-09 | checks_passed | `submission.rejected` | rejected (T) | Same transaction as CT-10 or CT-16 | none | none | `submission.rejected {reason_code}` |

A submission in `quarantined` that no reviewer decides is bounded by the job's `overrun_timeout` and by the alert on `report.triage_sla_days`; it never auto-releases. [D]
