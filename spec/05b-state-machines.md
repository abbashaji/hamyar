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

## 5.24 Member trust tiers and status

Trust tier (`new`, `established`, `trusted`, `restricted`) and status (`active`, `suspended`, `banned`, `closed`) are two independent columns (S0.9.4). Tier is computed by the system from verified work; status is set by people or by the member. [D]

**Reliability estimate used by the guards.** `r = (a + p) / (a + b + p + f)`, with `a` = `verify.reliability_prior_a`, `b` = `verify.reliability_prior_b`, `p` and `f` the passes and fails among the member's most recent `verify.reliability_window_obs` gold and audit observations (S8.* owns the estimator and its limits). With the initial configurable defaults (a = b = 1) and no failures, `r >= x` needs `p >= (2x - 1) / (1 - x)` clean observations: 3 for `trust.established_min_reliability` (0.80) and 18 for `trust.trusted_min_reliability` (0.95). A tier therefore cannot be reached on cell count alone. [D][H: the defaults are priors, replaced by `P1M` measurement]

```
 new --tier_promoted--> established --tier_promoted--> trusted
 trusted --tier_demoted--> established --tier_demoted--> new
 new, established, trusted --restricted--> restricted --restriction_lifted--> tier_before_restriction
 STATUS: active --suspended--> suspended --reinstated--> active ; active, suspended --banned--> banned ; active, suspended --closed--> closed (T)
         banned --reinstated--> active  (only through an overturned appeal; convention addition 6)
```

| id | from | event | to | guard | side effects | ledger effects | audit-log entry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MT-01 | (none) | `member.created` | new (status `active`) | `launch.members_may_join` true, else `403 LAUNCH_GATE_CLOSED`; the per-device, per-IP-hash and per-invite-tree creation limits of `ratelimit.*` and `invite.*` hold (S10.*) | Create `Member`, `MemberKey`, `Device`, and the member's `ledger_account` of type `member` | none (an account starts at zero; the starter grant is a separate `grant` txn, S6.*) | `member.created {invite_id?}` |
| MT-02 | new | `member.tier_promoted` | established | Status `active`; accepted cells >= `trust.established_min_cells`; `r >= trust.established_min_reliability`; not restricted | Cap multiplier `trust.cap_multiplier.established`; audit multiplier `trust.audit_multiplier.established` | none | `member.tier_promoted {accepted, r_ppm}` |
| MT-03 | established | `member.tier_promoted` | trusted | Accepted cells >= `trust.trusted_min_cells`; `r >= trust.trusted_min_reliability` | Caps and sampling per the `trusted` multipliers | none | as MT-02 |
| MT-04 | trusted | `member.tier_demoted` | established | `r < trust.demote_below_reliability` | Multipliers of `established`; existing balance above the new cap is kept (no clawback); earning pauses until the balance is under the cap (headroom guard, 5.29.3) | none | `member.tier_demoted {r_ppm}` |
| MT-05 | established | `member.tier_demoted` | new | As MT-04 | As MT-04 | none | as MT-04 |
| MT-06 | new, established, trusted | `member.restricted` | restricted | `trust.restrict_after_gold_fails` consecutive failed gold cells, or an anomaly finding of S9.* (forged nonce attempts, timing anomalies, duplicate-of-other-output), or an `admin` with `perm.member.restrict` | Store `tier_before_restriction` and `restricted_until` = now + `trust.restriction_days` x 86,400 s; multipliers of `restricted`; leases already held are kept | none | `member.restricted {trigger}`; +AA when an admin |
| MT-07 | restricted | `member.restriction_lifted` | `tier_before_restriction` | Timer `restriction_lifter`: now >= `restricted_until`, or an admin lifts early | The `tier_evaluator` then runs at once, so a member whose `r` is under `trust.demote_below_reliability` is demoted immediately (MT-04, MT-05) | none | `member.restriction_lifted {tier}` |
| MS-01 | active | `member.suspended` | suspended | `admin` with `perm.member.suspend`, or `kill.member.<mem_id>` engaged | Revoke active leases (CT-18); end sessions; pause the member's jobs with cause `kill_member` (JT-11); cells already `submitted` are DEFERred at `G-accept`. Credit lots keep expiring [A]; an overturned suspension appeal restitutes lots that expired meanwhile (APT-07) | none | `member.suspended {reason_code}`; +AA |
| MS-02 | suspended | `member.reinstated` | active | `admin` with `perm.member.suspend`, kill switch released (two admins, `killswitch.release`), or an overturned appeal | Resume paused jobs; re-enqueue deferred acceptances | none | `member.reinstated {via}`; +AA |
| MS-03 | active, suspended | `member.banned` | banned | `admin` with `perm.member.ban` and a reason code; appealable | As MS-01; the member's non-terminal jobs get `job.stop_requested` with `operator_killed`; the balance is frozen (no spending, no earning, expiry continues). The member may still use the appeal endpoint only (S10.*) [A] | none | `member.banned {reason_code}`; +AA |
| MS-04 | active, suspended | `member.closed` | closed (T) | Member-initiated or inactive for `retention.member_inactive_days`; no job, reservation or lease is non-terminal; balance is 0 or the member confirms donating it | Release leases; delete or reduce rows per the retention classes (S0.7); sessions and keys revoked | If balance > 0: `reserve_donation` txn, `member` -> `reserve` of the whole balance, key `closedonate:<mem_id>`. A closure by inactivity always has balance 0 because `retention.member_inactive_days` (365) exceeds `credit.lifetime_days` (60) [D] | `member.closed {via}` |
| MS-05 | banned | `member.reinstated` | active | Only an `Appeal` `overturned` with `appeal.ban_min_reviewers` agreeing reviewers (APT-07) | As MS-02 | none | `member.reinstated {via: appeal}` |

Other member events (`member.key_rotated`, `member.device_linked`, `member.recovered`, `member.optin_changed`) change no tier or status and are log-only events owned by S10.*. `identity.recovery_cooldown_s` after `member.recovered` blocks JT-09 and every spend, but not earning. [D]

## 5.25 Template review (second-reviewer rule)

Applies to `TemplateVersion.review_status` (S0.9.5). A version is mutable only in `draft` and `changes_requested`; from `in_review` on its content is frozen and every approval is bound to its `content_hash`. [D]

```
 (none) --version_created--> draft --review_requested--> in_review --first_approved--> awaiting_second_review --second_approved--> approved
 in_review, awaiting_second_review --changes_requested--> changes_requested --review_requested--> in_review
 in_review, awaiting_second_review --rejected--> rejected (T)
 approved --paused--> paused --resumed--> approved          approved, paused --retired--> retired (T)
```

| id | from | event | to | guard | side effects | ledger effects | audit-log entry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TT-01 | (none) | `template.version_created` | draft | `admin` with `perm.template.author`; version number = previous + 1 (unique per `Template`) | A new `Template` row if none; `author_id` recorded | none | `template.version_created {version, parent_version?}`; +AA |
| TT-02 | draft, changes_requested | `template.review_requested` | in_review | Template lint passes (slots, delimiters, output schema, checks, comparator, envelope inside `cell.envelope.*`; S8.*) | Freeze content, store `content_hash`; clear approvals of earlier rounds | none | `template.review_requested {content_hash, round}`; +AA |
| TT-03 | in_review | `template.first_approved` | awaiting_second_review, or approved when the required count is 1 | Approver is an `admin` with the `reviewer` role; approver is not the author; approver has not approved this `content_hash` before (unique `(template_version_id, reviewer_id, content_hash)`); required count k = `template.min_reviewers_new` for a new `Template`, `template.min_reviewers_edit` for a new version of an approved one; after inserting the approval, the count of distinct approvals under the version row lock is < k (-> awaiting) or >= k (-> approved) | Insert the approval row with its checklist; if the target is `approved`, run the approval side effects below | none | `template.first_approved {reviewer, count, k}`; +AA |
| TT-04 | awaiting_second_review | `template.second_approved` | approved | As TT-03 for a second, different reviewer; count >= k under the row lock. Approvals 2..k-1 when k > 2 only insert a row and emit the log-only event `template.approval_recorded` (convention addition 7) | Approval side effects below | none | `template.second_approved {reviewer, count, k}`; +AA |
| TT-05 | in_review, awaiting_second_review | `template.changes_requested` | changes_requested | A reviewer who is not the author gives a comment | Approvals of this round are voided | none | `template.changes_requested {reviewer}`; +AA |
| TT-06 | in_review, awaiting_second_review | `template.rejected` | rejected (T) | A reviewer who is not the author gives a reason code | Appeal path `template_rejection` opens | none | `template.rejected {reviewer, reason_code}`; +AA |
| TT-07 | approved | `template.paused` | paused | `kill.template.<tpl_id>` engaged by an operator with a logged reason, or the autopause: `template.autopause_report_count` reports inside `template.autopause_window_s` (system) | Pause every non-terminal job that uses the template (JT-11, cause `kill_template` or `template_paused`); no new job may be quoted or admitted on it (guards JT-04, JT-09) | none | `template.paused {cause}`; +AA when an admin |
| TT-08 | paused | `template.resumed` | approved | Kill switch released by two distinct admins (`killswitch.release`); after an autopause, a reviewer has triaged the reports | Clear the pause cause on each job; jobs resume when their last cause clears (JT-12) | none | `template.resumed {}`; +AA |
| TT-09 | approved, paused | `template.retired` | retired (T) | `cause` = `superseded` (automatic when a newer version of the same `Template` reaches `approved`) or `withdrawn_for_cause` (an admin with a reason) | `superseded`: nothing happens to jobs; they finish on the version stamped at admission. `withdrawn_for_cause`: `job.stop_requested` with `template_retired` for every non-terminal job on it | none | `template.retired {cause}`; +AA |

**Approval side effects** (inside the TT-03 or TT-04 transaction that reaches `approved`): freeze the version permanently; CAS `Template.active_version_id` from the previous version to this one (the previous `approved` version is retired with cause `superseded` through TT-09 in the same transaction, so a template never has two active versions); write a public `ChangeLogEntry` (S12.*); write the `AdminAction` rows. Concurrent approvals by two reviewers serialize on the version row lock, so the count is exact (RC-26). The second-reviewer rule is enforced three times: the unique key above, the `reviewer is not the author` predicate in the guard, and a database check at insert. [D]

## 5.26 Service review

Applies to `ServiceRegistryEntry` (S0.9.6). Only `approved` allows new jobs; every service is created `unreviewed` and counts as no. [D]

```
 (none) --created--> unreviewed ; unreviewed, rejected, review_due, revoked --review_started--> in_review
 in_review --approved--> approved --review_due--> review_due --review_lapsed--> suspended
 in_review --rejected--> rejected ; approved, review_due --suspended--> suspended --resumed--> approved
 approved, review_due, suspended --revoked--> revoked
```

| id | from | event | to | guard | side effects | ledger effects | audit-log entry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SVT-01 | (none) | `service.created` | unreviewed | `admin` with `perm.service.create`; every flag starts as `unknown` | none | none | `service.created {}`; +AA |
| SVT-02 | unreviewed, rejected, review_due, revoked | `service.review_started` | in_review | `admin` with the `reviewer` role; no other review of this entry is open (CAS) | From `review_due`: keep `grace_deadline_at`; the lapse timer still applies (convention addition 8) | none | `service.review_started {from_state}`; +AA |
| SVT-03 | in_review | `service.approved` | approved | `third_party_task_use` = `yes` and `prohibited_content_compatible` = `yes`, each a dated `FlagAnswer` with the reviewer recorded and pointing at a saved `TermsCopy` (bytes, `sha256:` hash, source reference, capture date, <= `service.terms_copy_max_bytes`) captured during this review; at least `service.min_approvers` distinct reviewers; every other gate flag has an answer (`unknown` evaluates as `no`) | Set `approved_at`, `review_due_at` = `approved_at` + `service.review_max_age_days` x 86,400 s; publish a `ChangeLogEntry` (class `loosen`, `effective_from` per S7.*); a job may use the service only when `effective_from` <= now | none | `service.approved {terms_copy_id, flag_answer_ids[]}`; +AA |
| SVT-04 | in_review | `service.rejected` | rejected | A reviewer with a reason code | none | none | `service.rejected {reason_code}`; +AA |
| SVT-05 | approved | `service.review_due` | review_due | Timer `service_review_timer`: now >= `review_due_at` | New jobs blocked at once (guards JT-04, JT-09); in-flight cells continue; `grace_deadline_at` = now + `service.review_grace_days` x 86,400 s; reviewer queue entry | none | `service.review_due {grace_deadline_at}` |
| SVT-06 | review_due, or in_review entered from review_due | `service.review_lapsed` | suspended | Timer: now >= `grace_deadline_at` and no approval has happened | As SVT-07 with cause `review_lapsed` | none | `service.review_lapsed {}` |
| SVT-07 | approved, review_due | `service.suspended` | suspended | `kill.service.<svc_id>` engaged by an operator with a logged reason | Jobs pinned (M1) to the service: JT-11 with `kill_service`; the card stops offering the service; a submission that reports the service is REJECT_POLICY at `G-accept` | none | `service.suspended {cause}`; +AA |
| SVT-08 | suspended | `service.resumed` | approved | Only when `suspended_cause` = `kill_switch`; kill switch released by two admins. A lapse (`review_lapsed`) is resolved only through a new review | Clear the pause cause on jobs (JT-12); if `review_due_at` has passed the timer moves the entry to `review_due` again | none | `service.resumed {}`; +AA |
| SVT-09 | approved, review_due, suspended | `service.revoked` | revoked | `admin` with a reason code, and the field `inflight_policy` in `drain` or `void` | Public `ChangeLogEntry` (class `tighten`, published within `change.tighten_publish_within_s`); jobs pinned only to this service get `job.stop_requested` with `service_revoked`; M0 jobs continue on other approved services; attested-service cells in flight follow `inflight_policy` at `G-accept` (the choice and its wording belong to S7.*; this part only fixes the two hooks) | none | `service.revoked {reason_code, inflight_policy}`; +AA |

## 5.27 Appeal

States and events are S0.9.7. `appeal_kind` is `cell_rejection`, `member_suspension`, `member_ban`, `job_rejection`, `template_rejection` or `report_outcome`. [D]

```
 (none) --filed--> filed --assigned--> assigned --review_started--> in_review --upheld--> upheld (T)
 assigned --reassigned--> assigned ; in_review --second_review_requested--> awaiting_second_review
 in_review, awaiting_second_review --upheld--> upheld (T) ; in_review, awaiting_second_review --overturned--> overturned (T)
 filed, assigned, in_review --withdrawn--> withdrawn (T)
```

| id | from | event | to | guard | side effects | ledger effects | audit-log entry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| APT-01 | (none) | `appeal.filed` | filed | Caller is the affected principal for the kind; the decision exists and now <= decision time + `appeal.window_days` x 86,400 s, else `422 UNPROCESSABLE` with `details.reason` = `window_closed`; appeals on this decision < `appeal.max_per_decision` (unique `(decision_ref, sequence)` closes the double-filing race, RC-29); `Idempotency-Key` present | Freeze an evidence snapshot (hashes, states, `StateTransition` ids, policy version) in the `Appeal` so the 30-day purge of job data cannot destroy it; `due_by` = now + `appeal.reviewer_sla_days` x 86,400 s (a published target, not a state) | none | `appeal.filed {kind, decision_ref}` |
| APT-02 | filed | `appeal.assigned` | assigned | Assignee is an `admin` with the `reviewer` role and is not the admin who made the original decision; no conflict recorded | Assignment row | none | `appeal.assigned {reviewer}`; +AA |
| APT-03 | assigned | `appeal.reassigned` | assigned | A conflict of interest is declared | New assignment row | none | `appeal.reassigned {from, to}`; +AA |
| APT-04 | assigned | `appeal.review_started` | in_review | Caller is the assignee | none | none | `appeal.review_started {}`; +AA |
| APT-05 | in_review | `appeal.second_review_requested` | awaiting_second_review | Mandatory for `member_ban` and `template_rejection`; optional for other kinds | Second assignee distinct from the first and from the original decider | none | `appeal.second_review_requested {}`; +AA |
| APT-06 | in_review, awaiting_second_review | `appeal.upheld` | upheld (T) | Reviewer decision with a reason; for kinds that need two reviewers, anything short of `appeal.ban_min_reviewers` agreeing to overturn is `upheld` [D][A] | Notify; the original decision stands | none | `appeal.upheld {reviewers[], reason_code}`; +AA |
| APT-07 | in_review, awaiting_second_review | `appeal.overturned` | overturned (T) | Reviewer decision with a reason; for `member_ban` and `template_rejection`, at least two distinct reviewers agree, neither the original decider | Effects by kind in the table below | Effects by kind in the table below | `appeal.overturned {reviewers[], reason_code, effects[]}`; +AA |
| APT-08 | filed, assigned, in_review | `appeal.withdrawn` | withdrawn (T) | Caller is the appellant | none | none | `appeal.withdrawn {}` |

**Effects of `appeal.overturned` by kind** [D][A]

| `appeal_kind` | State effect | Ledger effect |
| --- | --- | --- |
| `cell_rejection` | The rejected `Submission` is marked overridden; the `VerificationRecord` is excluded from reliability estimates and from consecutive-gold-failure counts (so MT-06 can be undone by MT-07); the cell is not reopened, it follows its own course | Restitution of 1,000,000 `ucr` to the donor: a `grant` txn, entry `grant` reserve -> member with reason `appeal_restitution`, key `appealpay:<apl_id>`. It is paid by the Reserve, never by escrow (the job may be settled) and never by `mint` (not an accepted Commons cell). If the Reserve is at or below `grant.reserve_floor_credits` the payment stays `pending` and the `restitution_payer` job retries; grants pause rather than overdraw (FD§4.6). See `ISS-56` |
| `member_suspension` | `member.reinstated` (MS-02) | Restitution `grant` equal to the lots that expired during the suspension, key `appealpay:<apl_id>`, same Reserve rule |
| `member_ban` | `member.reinstated` (MS-05), jobs stopped by the ban stay settled | As `member_suspension` |
| `job_rejection` | The rejected job stays `rejected`; the system creates a new job in `draft` with the stored upload (if still retained), the same declarations, and `waived_rules` listing only input-screening findings (R1, R3 detections, R4 mistakes); rules driven by the declarations themselves (R2, R5, R6, R7) cannot be waived by appeal | none |
| `template_rejection` | The version stays `rejected`; a new version is created as a copy in `in_review` with the appeal reference; reviewers must be distinct from the one who rejected it | none |
| `report_outcome` | The action taken on the report is reversed through its own machine (for example `template.resumed`, `member.restriction_lifted`); a dismissed report is reopened as a new `Report` linked to the old one (`report` states are terminal) | none |

## 5.28 Escrow and Reservation machines (the ledger-touching small machines)

The small machines of S0.9.8 that move credit are specified here because settlement and double-spend protection depend on them. `Audit`, `Report`, `LaunchGateItem` and kill-switch machines are owned by S8.*, S10.* and S14.*. [D]

| id | machine | from | event | to | guard | ledger effects (kind, key) |
| --- | --- | --- | --- | --- | --- | --- |
| ET-01 | Escrow | (none) | `escrow.opened` | open | Same transaction as JT-09; unique `(job_id)` | `hold`, `hold:<job_id>` |
| ET-02 | Escrow | open | `escrow.settling_started` | settling | Same transaction as JT-14, JT-15 or JT-18. In `settling` no new cell may be created, but payouts for cells that already exist are allowed (drain) | none |
| ET-03 | Escrow | settling | `escrow.closed` | closed (T) | Same transaction as JT-16, JT-17 or JT-20; escrow balance is exactly 0 after the entries | `settle:<job_id>` or `cancel:<job_id>` |
| RT-01 | Reservation | (none) | `reservation.held` | held | `ff.job.reservations` on; `reservation.max_active_per_member`; horizon <= `reservation.max_horizon_days`; capacity share <= `reservation.capacity_share_cap`; balance >= escrow | `hold`, `hold:<rsn_id>` |
| RT-02 | Reservation | held | `reservation.activated` | activated (T) | The member confirms the job for the booked day (JT-09 for that job) | `reservation_activate`, entry `escrow_release` reservation escrow -> job escrow, key `resact:<rsn_id>`; JT-09 then posts no `hold` |
| RT-03 | Reservation | held | `reservation.cancelled` | cancelled (T) | The member cancels; fees or none by `reservation.free_cancel_notice_s` (S6.*) | `cancel`, entry `refund`, key `rsncancel:<rsn_id>` |
| RT-04 | Reservation | held | `reservation.expired` | expired (T) | Timer `reservation_expirer`: booked day passed unused | `cancel`, entry `refund`, key `rsnexpire:<rsn_id>` |

## 5.29 Idempotency, concurrency and race handling

This section states what the system guarantees, exactly, and the mechanism behind each guarantee. A guarantee holds at every instant, including during a crash, unless it says otherwise. Any mechanism that provides the same guarantee is allowed; the mechanisms written here are the reference. [D]

### 5.29.1 Storage requirements and the guarantee list

S4.* chooses the concrete store; it MUST provide all of the following, because without them the guarantees below cannot hold and the ledger cannot be hosted. [D]

| id | Requirement |
| --- | --- |
| SR-1 | Atomic multi-row transactions covering state tables, ledger tables, outbox and idempotency records together |
| SR-2 | Exclusive and shared row locks, or an equivalent CAS on `row_version` with retry |
| SR-3 | Unique constraints, including partial unique indexes (`UNIQUE (cell_id) WHERE state = 'active'`) |
| SR-4 | Isolation of at least read committed with the lock rules of 5.29.2; serializable is allowed if serialization failures are retried |
| SR-5 | One authoritative clock, read inside the statement (5.21.4) |
| SR-6 | Durable commit: an acknowledged commit survives a crash (replication mode chosen by S4.*) |

| id | Guarantee (exact) | Mechanism | Sections |
| --- | --- | --- | --- |
| GU-01 | At every instant a cell has at most one `active` lease | Partial unique index on `leases(cell_id)` where `state = 'active'`, plus the CAS on the cell | 5.29.3 |
| GU-02 | Among any number of concurrent lease attempts on one cell, at most one succeeds, and exactly one succeeds if the cell is leasable; the others receive `409 LEASE_CONFLICT` and change nothing | CAS `queued` -> `leased` with `active_lease_id IS NULL` | 5.29.3 |
| GU-03 | A nonce is valid for exactly one lease and one member; only the holder who presents it can submit; the server stores only its SHA-256 | 128-bit CSPRNG nonce, hash compare in constant time, binding to `(lease_id, member_id)` | 5.29.4 |
| GU-04 | A lease has at most one `Submission`; a replay of the same submission returns the stored outcome and emits nothing | `UNIQUE (lease_id)` on `submissions`; CAS on the lease | 5.29.4 |
| GU-05 | For one lease, exactly one of `lease.submission_received` and `lease.expired` (or `released`, `revoked`) happens, never two; the winner is the first CAS on the lease row | Both transitions are `UPDATE ... WHERE state = 'active'` with disjoint clock predicates | 5.29.4 |
| GU-06 | No lease is issued when its guards forbid it at the commit instant; a pause or stop is cleaned up by fan-out within one worker pass, and nothing is paid in that window | Guards read under shared locks; `G-accept` re-checks at acceptance | 5.23.2, 5.29.3 |
| GU-07 | Every accepted cell has exactly one `mint` or `payout` ledger transaction, and every cell that is not accepted has none | Acceptance and ledger posting in one transaction; key `mint:<cell_id>` or `payout:<cell_id>` | 5.29.6 |
| GU-08 | A rejected, voided, cancelled, exhausted or overturned-and-reversed cell leaves no net credit with the donor | No payment before acceptance; `reversal` for overturned cells | 5.23.1 |
| GU-09 | A job is settled exactly once; its escrow ends at exactly 0; payouts + levy + refund = the amount held, with zero tolerance | Key `settle:<job_id>` or `cancel:<job_id>`; CAS on job and escrow | 5.29.8 |
| GU-10 | No double-spend: a member balance never goes below 0, a job has at most one `hold`, a reservation at most one `hold` and one activation | Conditional balance update, lot consumption in the same transaction, unique keys | 5.29.7 |
| GU-11 | Crash atomicity: after any crash a transition is either fully applied or not at all | 5.21.2 | 5.21.2 |
| GU-12 | Credit earned never exceeds the member cap K x tier multiplier, and Commons minting never exceeds `mint.monthly_cap_credits` or `mint.per_member_daily_cap_credits` | Headroom reserved at lease, consumed at acceptance | 5.29.3 |
| GU-13 | Events are delivered at least once, in order per entity, and every consumer is idempotent on `event_id` | Outbox in the same transaction, relay, consumer dedupe | 5.29.10 |
| GU-14 | An API call with an `Idempotency-Key` takes effect at most once per key within `api.idempotency_ttl_s`, and its stored response is replayed | S0.11.5 | 5.29.5 |

### 5.29.2 Lock order [D]

Every transaction acquires locks in this order and never goes back; two rows of the same kind are taken in ascending id. This removes deadlocks between request paths and workers.

| Order | Row | Taken by |
| --- | --- | --- |
| 1 | `Member` (exclusive) | `lease()` (serializes one member's lease cap), JT-09, MS-* |
| 2 | Policy pointer row (shared; exclusive for publish) | `G-accept`, JT-09; `policy.version_published` |
| 3 | `Job` (shared on request paths; exclusive for JT-11 to JT-20 and workers) | all |
| 4 | `Cell` (exclusive) | lease, submit, accept, fan-out |
| 5 | `Lease` (exclusive) | submit, reaper, extension |
| 6 | `Submission` | verification pipeline |
| 7 | `Escrow` | accept (payout), settle |
| 8 | `LedgerAccount` rows, ascending id | any ledger posting |
| 9 | Ledger head (sequence and hash chain) | the last step of any ledger posting, held only for the append |

The ledger head serializes ledger commits to keep one hash chain (S0.6.4) [A]; because it is taken last and held only for the append, contention is bounded by the append time, not by the length of the transaction.

### 5.29.3 Leasing

**Offer is not a hold.** A card shown to a donor reserves nothing; only a successful `lease()` does. Candidate selection for a server-chosen card uses `SELECT ... FOR UPDATE SKIP LOCKED` (or a CAS loop) on `queued` cells and then runs the same `lease()` transaction, so two donors are never handed the same cell by the selector, and the CAS below remains the authority. [D]

**`G-leasable`** (all must hold; the error is returned for the first failure):

| Check | Error |
| --- | --- |
| Member `status` = `active` | `403 FORBIDDEN` |
| `launch.members_may_join` true | `403 LAUNCH_GATE_CLOSED` |
| `kill.member.<mem_id>` and `kill.template.<tpl_id>` released | `503 KILL_SWITCH_ENGAGED` |
| Job `admitted` or `running`; template version `approved` | `409 STATE_CONFLICT`, `details.reason` = `job_not_leasable` |
| Commons job: `launch.minting_enabled` true and `kill.all_minting` released | `403 LAUNCH_GATE_CLOSED` / `503 KILL_SWITCH_ENGAGED` |
| R8: the cell's purpose, sensitivity, license, service requirement and topic are covered by the member's `OptIn` | `422 UNPROCESSABLE`, `details.reason` = `optin_mismatch` |
| No self-dealing: the member is not the job's requester, nor linked to the requester by S9.* rules | `403 FORBIDDEN` |
| Independence: the member is not in `independence_set(cell)` (below) | `409 STATE_CONFLICT`, `details.reason` = `not_independent` |
| The member's `active` leases < `lease.max_active_per_member` | `422 CAP_EXCEEDED`, `details.cap` = `lease.max_active_per_member` |
| Rate: `ratelimit.member_leases_per_hour` | `429 RATE_LIMITED` |
| Earning headroom: `cap_ucr(member) - balance - reserved_ucr(member) >= 1,000,000`, where `cap_ucr` = `credit.member_cap_credits` x the tier's `trust.cap_multiplier.*` x 1,000,000 and `reserved_ucr` = 1,000,000 x the member's cells in `leased`, `submitted`, `flagged_for_audit` (derived from state under the member lock, so it cannot drift) | `422 CAP_EXCEEDED`, `details.cap` = `credit.member_cap_credits` |
| Commons job: mint headroom, one conditional update: `UPDATE mint_budget SET reserved_ucr = reserved_ucr + 1,000,000 WHERE period = :utc_month AND minted_ucr + reserved_ucr + 1,000,000 <= cap_ucr` (and the same for the member's UTC day under `mint.per_member_daily_cap_credits`); 0 rows means no headroom | `422 CAP_EXCEEDED`, `details.cap` = `mint.monthly_cap_credits` |

The mint-headroom reservation is the answer to a cap that is reached while cells are in flight: no Commons cell is leased unless its mint is already covered, so acceptance can never find the cap exhausted (GU-12). The reservation is released by every transition that leaves `leased`, `submitted` or `flagged_for_audit` without paying (CT-04, CT-05, CT-08, CT-10, CT-13, CT-15, CT-16, CT-18) and consumed by CT-06 and CT-09 in the same transaction as the `mint`. S6.* owns the counter's table and the reconciliation check CK-05. [D][A]

**`independence_set(cell)`** [D]: the members who submitted any earlier attempt of this cell; for an `audit` or `third` cell also the member who submitted the audited cell and every earlier executor in its chain; for a `gold` cell also every member who already received this gold cell on any attempt (answer harvesting); S9.* adds linked devices and invite-tree relatives. A member who only declined, let a lease expire or was revoked is not excluded.

**At most one active lease per cell, and linearizable acquisition (GU-01, GU-02).** Two independent mechanisms: the CAS on the cell row (`state = 'queued' AND active_lease_id IS NULL AND row_version = :seen`) and the partial unique index on `leases`. If the first is bypassed by a defect, the second still refuses the insert and the transaction fails; `ledger_invariant_checker` also checks GU-01 as CK-01 (5.29.10).

```
def lease(principal, cell_id, idem_key, body):
    check_auth(principal, scheme='member')
    rate_limit(principal.member_id, 'ratelimit.member_leases_per_hour')
    rec = idempotency.begin(principal.id, 'POST', '/v1/cells/{id}/leases', idem_key, body_hash(body))
    if rec.is_replay:                                   # same key, same body (S0.11.5)
        return replay_lease_response(rec)               # rotates the nonce, see below
    # IDEMPOTENCY_IN_PROGRESS and IDEMPOTENCY_KEY_MISMATCH are raised inside begin()
    with tx():
        m    = lock_exclusive(Member, principal.member_id)              # order 1
        job0 = read(Job, read(Cell, cell_id).job_id)
        job  = lock_shared(Job, job0.id)                               # order 3
        cell = lock_exclusive(Cell, cell_id)                           # order 4
        if cell.state != 'queued' or cell.active_lease_id is not None:
            raise Error(409, 'LEASE_CONFLICT')                         # race lost, nothing written
        g_leasable(m, job, cell)                                       # table above; may raise
        lse = new_id('lse')
        nonce = csprng_bytes(lease.nonce_bytes)                        # 16 bytes
        n = sql('UPDATE cells SET state=:leased, active_lease_id=:lse, row_version=row_version+1 '
                'WHERE id=:id AND state=:queued AND active_lease_id IS NULL AND row_version=:seen')
        if n != 1: raise Error(409, 'LEASE_CONFLICT')
        sql('INSERT INTO leases(id, cell_id, attempt, member_id, state, nonce_hash, '
            'issued_at, expires_at, hard_expires_at, extensions) VALUES (:lse, :id, :attempt, :m, :active, '
            'sha256(:nonce), now(), now()+:timeout, now()+:timeout+:grace, 0)')   # partial unique index
        if cell.job.origin == 'commons': mint_headroom.reserve(utc_month(), m.id, 1_000_000)
        record_transition(cell, 'cell.leased'); record_transition(lease, 'lease.issued')
        if job.state == 'admitted': transition(job, 'job.started')     # JT-10, same transaction
        response = lease_response(lse, cell, nonce_omitted_in_store=True)
        idempotency.complete(rec, 201, response_without_nonce)
    return 201, response_with(nonce)                                    # the only time the nonce is sent
```

`timeout` = `lease.timeout_s`, `grace` = `lease.submit_grace_s` (initial configurable defaults 1,200 s and 120 s). **Replay and the nonce.** The nonce is never stored, so a replayed acquisition response cannot repeat it. `replay_lease_response` rotates it: `UPDATE leases SET nonce_hash = sha256(:new_nonce) WHERE id = :lse AND state = 'active'`, returns the lease with the new nonce, and the lost first nonce is dead. If the lease is no longer `active` it returns the stored response without a nonce and the current state. Only the same principal with the same key and body can reach this path. [D]

### 5.29.4 Nonce, submission, duplicates and the expiry race

**Nonce rules** [D]. 128 bits from the OS CSPRNG; stored as SHA-256 only; compared in constant time; valid only with its `lease_id` and the member who holds the lease; never reused after rotation; never logged. S9.* may add a per-lease marker inside the wrapped prompt; this part requires only the binding above. A submission whose lease is missing or belongs to another member is `404 NOT_FOUND` (existence does not leak); a correct lease with a wrong nonce is `403 FORBIDDEN` with `details.reason` = `nonce_invalid`, changes no state, leaves the lease `active`, and is counted as an abuse signal (S9.*; `reject.nonce_invalid` names it for the donor-facing history).

**Pre-checks that consume nothing** [D]: a body over `cell.envelope.max_submission_bytes` is `413 PAYLOAD_TOO_LARGE` (`reject.size_exceeded` is shown to the donor) and an empty body is `400 VALIDATION_FAILED`; in both cases the lease stays `active` and the donor may paste again until `hard_expires_at`. Schema and quality failures of a received body are not pre-checks: they follow SBT-02 and CT-08.

```
def submit(principal, lease_id, nonce, body, idem_key):
    check_auth(principal, scheme='member')
    if bytes(body.content) > cell.envelope.max_submission_bytes: raise Error(413, 'PAYLOAD_TOO_LARGE')
    if is_blank(body.content): raise Error(400, 'VALIDATION_FAILED')
    rate_limit(principal.member_id, 'ratelimit.member_submissions_per_hour')
    rec = idempotency.begin(principal.id, 'POST', '/v1/leases/{id}/submission', idem_key, body_hash(body))
    if rec.is_replay: return rec.stored_response
    lse0 = read(Lease, lease_id)
    if lse0 is None or lse0.member_id != principal.member_id: raise Error(404, 'NOT_FOUND')
    if not ct_equal(sha256(nonce), lse0.nonce_hash): abuse.count('nonce_invalid', principal); raise Error(403, 'FORBIDDEN')
    with tx():
        cell = lock_exclusive(Cell, lse0.cell_id)                       # order 4
        lse  = lock_exclusive(Lease, lease_id)                          # order 5
        if lse.state == 'submitted':                                    # natural replay
            sub = read(Submission, lease_id=lease_id)
            if sub.content_hash == sha256(body.content): return 200, outcome_of(sub)    # no event
            raise Error(409, 'STATE_CONFLICT', reason='already_submitted')              # body discarded
        n = sql('UPDATE leases SET state=:submitted, submitted_at=now() '
                'WHERE id=:id AND state=:active AND hard_expires_at >= now()')
        if n != 1:
            raise Error(410, 'LEASE_EXPIRED', reason=lse.state if lse.state != 'active' else 'expired')
        n = sql('UPDATE cells SET state=:submitted, row_version=row_version+1 '
                'WHERE id=:cell AND state=:leased AND active_lease_id=:lse')
        if n != 1: alarm('invariant: active lease on a non-leased cell'); raise Error(500, 'INTERNAL')
        sql('INSERT INTO submissions(id, lease_id, cell_id, state, content, content_hash, bytes, '
            'reported_service_id, reported_model, time_to_submit_s, late) VALUES (...)')   # UNIQUE(lease_id)
        record_transition(lease, 'lease.submission_received'); record_transition(cell, 'cell.submitted')
        record_transition(submission, 'submission.received')
        enqueue_verification(submission)                                 # through the outbox
        idempotency.complete(rec, 202, submission_resource)
    return 202, submission_resource
```

**Duplicate submission handling** [D]

| Case | Outcome | Mechanism |
| --- | --- | --- |
| D1 Same `Idempotency-Key`, same body, within `api.idempotency_ttl_s` | The stored response is replayed with `Idempotent-Replayed: true`; nothing is written or emitted | S0.11.5 |
| D2 Same key, different body | `422 IDEMPOTENCY_KEY_MISMATCH` | S0.11.5 |
| D3 Same key while the first call still runs | `409 IDEMPOTENCY_IN_PROGRESS` with `Retry-After` | S0.11.5 |
| D4 New key, same lease, same content (a client retry that lost its key) | `200` with the stored outcome; no event | lease `submitted` and equal `content_hash` |
| D5 New key, same lease, different content (two tabs, an edited paste) | `409 STATE_CONFLICT`, `already_submitted`; the second body is discarded, never stored; an abuse counter is incremented (S9.*) | lease `submitted`, hash differs |
| D6 Any submission after the lease left `active` by expiry, release or revocation | `410 LEASE_EXPIRED` with `details.reason` in `expired`, `released`, `revoked`; the donor's UI explains; nothing is stored | CAS finds `state` != `active` |
| D7 Content identical or near-identical (>= `verify.duplicate_similarity_threshold`) to another donor's output for the same cell or audit chain | The first is judged on its merits; the later one is `reject.duplicate_of_other_output` at CT-08, and S9.* raises a copy-paste finding (MT-06 trigger) | S9.* comparator, not a concurrency matter |
| D8 The same content for two different leases of the same member on different cells | Allowed; two independent submissions | no constraint |

**Lease expiry while a submission is arriving** [D]. The two competing statements are `UPDATE leases SET state = 'submitted' ... WHERE id = :id AND state = 'active' AND hard_expires_at >= now()` and the reaper's `UPDATE leases SET state = 'expired' ... WHERE id = :id AND state = 'active' AND hard_expires_at < now()`. Both need the lease row lock and both test `state = 'active'`, so exactly one succeeds (GU-05).

| Interleaving | Outcome |
| --- | --- |
| Submit commits first | Lease `submitted`; the reaper's update affects 0 rows and the candidate is skipped. The donor is paid if the work passes |
| Reaper commits first | The submit's update affects 0 rows: `410 LEASE_EXPIRED`; the donor's work is lost, the cell requeues (CT-11) |
| Submit arrives within `[expires_at, hard_expires_at]` | Accepted, `late` = true (the grace period exists for this) |
| Submit arrives after `hard_expires_at` but before the reaper ran | Refused: the clock predicate is false even though the row still says `active`. The result does not depend on reaper timing |
| Submit arrives after the cell was re-leased to another donor | Refused, as above: the old lease is `expired` and has a different `lease_id` and nonce |

The guarantee is mutual exclusion, not boundary fairness: a submission arriving within the commit latency of `hard_expires_at` can lose. The documented margin is `lease.submit_grace_s`. [D][H: 120 s is enough for copy-paste delay; replaced by the `CAL` measurement of copy-paste timing]

### 5.29.5 Idempotency: layers, natural keys and ledger keys

Four layers, from the outside in. Each layer alone is enough to prevent a double effect on its own object; together they cover a client that loses its key. [D]

| Layer | Mechanism | Covers |
| --- | --- | --- |
| L1 HTTP | `Idempotency-Key` on every state-changing call that affects jobs, leases, submissions, escrow, ledger, grants, referrals, reports, appeals and every admin write (S0.11.5); scope (principal, method, path); stored with the SHA-256 of the canonical body | client retries, double taps, flaky networks |
| L2 Natural keys | Unique constraints below | a missing or reused key, a second client, a bug |
| L3 Ledger keys | `ledger_transactions.idempotency_key` UNIQUE; `ledger_entries.entry_key` = key plus leg number, UNIQUE | any repeated posting, including by a worker |
| L4 Events | `event_id` unique in the outbox; consumers record processed ids | duplicate delivery |

**L2 natural keys**

| Object | Constraint | Prevents |
| --- | --- | --- |
| `cells` | `UNIQUE (job_id, ordinal, cell_kind)` | duplicate cell creation on a retried JT-09 |
| `leases` | `UNIQUE (cell_id) WHERE state = 'active'`; `UNIQUE (cell_id, attempt)` | two active leases; two leases for one attempt |
| `submissions` | `UNIQUE (lease_id)` | two submissions per lease |
| `escrows` | `UNIQUE (job_id)` | two escrows per job |
| `state_transitions` | `UNIQUE (entity_type, entity_id, entity_seq)` | lost or duplicated transitions |
| template approvals | `UNIQUE (template_version_id, reviewer_id, content_hash)` | one reviewer approving twice |
| `appeals` | `UNIQUE (decision_ref, sequence)` | double filing beyond `appeal.max_per_decision` |
| outbox | `UNIQUE (event_id)` | duplicate events |

**L3 ledger idempotency keys** [D][A: S6.* owns the final table and may rename keys, not remove them]

| `ledger_txn_kind` | Key | Written by |
| --- | --- | --- |
| `mint` | `mint:<cell_id>` | CT-06, CT-09 (Commons) |
| `payout` | `payout:<cell_id>` | CT-06, CT-09 (member job) |
| `hold` | `hold:<job_id>` or `hold:<rsn_id>` | JT-09, RT-01 |
| `settle` | `settle:<job_id>` | JT-16, JT-17 |
| `cancel` | `cancel:<job_id>`, `rsncancel:<rsn_id>`, `rsnexpire:<rsn_id>` | JT-20, RT-03, RT-04 |
| `reservation_activate` | `resact:<rsn_id>` | RT-02 |
| `expire` | `expire:<lot_id>` | `credit_expiry_sweeper` |
| `retire` | `retire:<utc_date>` | `reserve_retirer` |
| `grant` | `grant:starter:<mem_id>`, `grant:referral:<ref_id>:<side>`, `appealpay:<apl_id>` | S6.*, S12.*, APT-07 |
| `reserve_donation` | `donate:<principal_id>:<Idempotency-Key>`, `closedonate:<mem_id>` | member action, MS-04 |
| `reversal` | `reversal:<original_txn_id>` | CT-17 |

`ledger.post(kind, key, legs)` first looks the key up. If it exists with the same canonical hash of legs, it returns the stored transaction and writes nothing (success, idempotent). If it exists with different legs, that is a defect: the call fails and an `Alarm` is raised, because two different postings were intended under one key. A job gets exactly one of `settle` and `cancel`, decided by the job state, so the keys cannot both exist for it. [D]

### 5.29.6 Acceptance: exactly-once payment (GU-07)

Acceptance is where credit is created or moved, so it is one transaction in which the cell state, the submission state, the headroom and the ledger posting commit together or not at all.

```
def accept_cell(cell_id, via):             # via in ('checks_passed', 'audit_passed'); called by the verification pipeline
    with tx():
        pol  = lock_shared(PolicyPointer)                                # order 2
        cell = read(Cell, cell_id); job = lock_shared(Job, cell.job_id)  # order 3
        cell = lock_exclusive(Cell, cell_id)                             # order 4
        if cell.state == 'accepted': return 'already_accepted'           # idempotent no-op
        require(cell.state == ('submitted' if via == 'checks_passed' else 'flagged_for_audit'))
        sub = lock(Submission, cell_id=cell_id, attempt=cell.attempt)    # order 6
        verdict = g_accept(cell, job, sub, pol)                          # 5.23.2
        if verdict == 'DEFER':         mark_deferred(cell); return 'deferred'
        if verdict == 'VOID':          transition(cell, 'cell.voided'); return 'voided'
        if verdict == 'REJECT_POLICY': transition(cell, 'cell.checks_failed', reason='reject.policy_changed'); return 'rejected'
        donor = sub.member_id
        if job.origin == 'commons':
            mint_headroom.consume(utc_month(donor_lease_issued_at), donor, 1_000_000)   # reserved -> minted
            ledger.post('mint', 'mint:' + cell_id, legs=[mint(issuance -> donor.account, 1_000_000)], new_lot=True)
        else:
            esc = lock_exclusive(Escrow, job.escrow_id)                  # order 7
            require(esc.state in ('open', 'settling') and payable_ucr(job) >= 1_000_000)
            ledger.post('payout', 'payout:' + cell_id, legs=[transfer(esc.account -> donor.account, 1_000_000)], new_lot=True)
        transition(cell, 'cell.checks_passed' if via == 'checks_passed' else 'cell.audit_passed')
        transition(sub, 'submission.accepted')
        enqueue(tier_evaluator, donor); enqueue(job_progress, job.id)
        return 'accepted'
```

If two workers run `accept_cell` for the same cell, the loser blocks on the cell lock and then sees `accepted` and returns. If a defect lets both through, the ledger key `payout:<cell_id>` rejects the second posting and the transaction rolls back. The amount is always exactly 1,000,000 `ucr` (FD§4.3, S0.6.1). The mint month for the headroom is the month in which the lease was issued, because that is when the reservation was made. [D]

### 5.29.7 Double-spend of escrow and of balances (GU-10)

Every debit is a conditional update inside the posting transaction, with the account lock held (order 8): `UPDATE ledger_accounts SET balance_ucr = balance_ucr - :amt WHERE id = :a AND balance_ucr >= :amt`. Zero rows affected aborts the transaction (`ledger.allow_negative_balance` is a constant false). Lot consumption happens in the same transaction: lots of the account are selected oldest-first and each is reduced by `UPDATE credit_lots SET remaining_ucr = remaining_ucr - :x WHERE id = :lot AND remaining_ucr >= :x AND expires_at > now()`; the sum of the lots' `remaining_ucr` must equal the account balance after commit (an `INV-L` check of S6.*). [D]

| Attack or accident | Outcome | Mechanism |
| --- | --- | --- |
| E1 Two `escrow_confirmed` calls for one job (double click, retry with a new key) | One `hold`; the second is `409 STATE_CONFLICT` (job already `admitted`) or replays the first | CAS `quoted` -> `admitted`; key `hold:<job_id>`; `UNIQUE (job_id)` on `escrows` |
| E2 Two different jobs of one member confirmed together against one balance | Both succeed only if the balance covers both; otherwise the second is `422 INSUFFICIENT_CREDIT`; the balance never goes negative | Member row lock (order 1) and the conditional debit; `admission.max_concurrent_jobs_per_member` evaluated under the same lock |
| E3 `hold` against a lot while the expiry sweep expires that lot | Exactly one of them consumes the lot's remaining amount; the other sees `remaining_ucr` = 0 or the lot gone and uses other lots or fails with `INSUFFICIENT_CREDIT`. Expired credit is never held | Account lock; `expires_at > now()` predicate; `expire:<lot_id>` |
| E4 A reservation activated twice, or activated while cancelled or expired | One terminal state wins; the loser is `409 STATE_CONFLICT`; the escrow moves once | CAS on the `Reservation`; key `resact:<rsn_id>` |
| E5 Donors paid more than the escrow holds, including through verification cells beyond the pool | Impossible by construction: `pool_ok` at cell creation (CT-01), `payable_ucr >= 1,000,000` at payout, and the levy portion is never payable | `payable_ucr(job)` = escrow balance - `levy_reserved_ucr` |
| E6 Refund posted twice (settle run twice, cancel then settle) | One `refund`; the second run returns the stored transaction | Keys `settle:<job_id>` and `cancel:<job_id>`, and the job state decides which exists |
| E7 Payout racing a cancel or stop | A payout posted before the job left `running` stands; a cell not yet accepted is DEFERred, voided or paid as a drain per table 5.22.1; settlement waits until every cell is terminal | `G-accept` under the shared job lock; the settle precondition |

### 5.29.8 Settlement: exactly once (GU-09)

`settle()` is called only by the `settler` worker (and by the cancel path when a job has no in-flight cells). It is a single transaction. The closing identity is checked inside it: amount held at JT-09 = payouts + levy + refund, with zero tolerance, and the escrow balance is exactly 0 afterwards. [D]

```
def settle(job_id, mode):                    # mode in ('complete', 'cancel')
    with tx():
        job = lock_exclusive(Job, job_id)                                # order 3
        if job.state in TERMINAL_JOB_STATES:  return 'already_settled'   # idempotent no-op, also after a crash
        expected = 'settling' if mode == 'complete' else 'cancelling'
        if job.state != expected:             raise Error(409, 'STATE_CONFLICT')
        if exists(Cell where job_id == job_id and state not in TERMINAL_CELL_STATES):
            return 'not_yet'                                             # an acceptance may still be in flight; retry later
        if job.origin == 'commons':
            transition(job, 'job.settled' if all_primary_accepted(job) else 'job.settled_partial'); return 'ok'
        esc = lock_exclusive(Escrow, job.escrow_id)                      # order 7
        require(esc.state == 'settling')
        acc_n   = count(Cell where job_id == job_id and cell_kind == 'primary' and state == 'accepted')
        levy    = levy_due_ucr(job, acc_n)               # S6.*: acc_n x lambda_ppm, with the lambda stamped in the quote
        bal     = ledger.balance(esc.account_id)
        refund  = bal - levy
        require(refund >= 0)                                             # else alarm and abort
        kind    = 'settle' if mode == 'complete' else 'cancel'
        legs    = [levy_leg(esc.account_id -> reserve, levy)] if levy > 0 else []
        legs   += [refund_leg(esc.account_id -> job.member_account, refund, restore_lots=True)] if refund > 0 else []
        ledger.post(kind, kind + ':' + job_id, legs)                     # order 8, 9; idempotent on the key
        require(ledger.balance(esc.account_id) == 0)
        require(job.held_ucr == payouts_total(job) + levy + refund)      # closing identity
        transition(esc, 'escrow.closed')
        if mode == 'complete':
            transition(job, 'job.settled' if job.all_primary_accepted else 'job.settled_partial')
        else:
            transition(job, 'job.cancel_settled')
        return 'ok'
```

- **Run twice or by two workers.** The second sees a terminal job and returns; if both pass the state test, the second blocks on the job lock and then sees the terminal state. If a defect let both post, the key rejects the second posting.
- **Crash.** A crash before commit leaves the job in `settling` or `cancelling` and the escrow untouched; the next sweep runs `settle()` again. There is no state in which levy is posted and the refund is not.
- **Late acceptance during settlement.** Settlement refuses to run while any cell is non-terminal, and an acceptance commits the cell as `accepted` atomically with its payout, so the count the settler sees is never between the two.
- **Overturn after settlement.** A reversal (CT-17) of a cell paid from a closed escrow is a ledger correction between the donor and the Reserve decided by S6.*; it never reopens the escrow (`closed` is terminal). [A]

### 5.29.9 What is not guaranteed [D]

- **Donor effort.** A donor can lose work to a timeout, a lost race at `hard_expires_at`, or a refusal under `reject.policy_changed`. The platform bounds this with the grace period and DEFER, not with a promise.
- **Prompt state flips.** The stored state of a lease or job can lag its true state by one worker pass (for example an `active` lease past `hard_expires_at`). Guards that matter test the time or the cause directly, so a lagging row never lets work through; only visibility is late.
- **Event timing and order across entities.** Events are at least once and ordered per entity only (GU-13).
- **Liveness during an outage.** If the store is unavailable no transition happens; the system fails closed.
- **Fairness at a boundary.** First commit wins; there is no tie-break by arrival time.
- **Clock exactness.** Timers fire within one sweep interval of their time; the database clock is authoritative.

### 5.29.10 Background jobs: crash recovery and consistency checks

**Worker protocol** [D]. Every worker is a stateless, convergent sweep: select candidates by predicate (batches with `SKIP LOCKED` or a CAS claim), process each candidate in its own transaction, and re-test the predicate inside it. Any number of copies may run concurrently; the CAS or key makes the loser a no-op. A worker keeps nothing in memory that cannot be rebuilt from the database, so a crash costs only latency. A candidate that fails is skipped with backoff and the run continues. Each worker exports `hamyar_bgjob_last_success_seconds` and `hamyar_bgjob_failures_total` labelled with its name (S4.* and S13.* set alarm thresholds); money-moving workers (`settler`, `credit_expiry_sweeper`, `reserve_retirer`, `restitution_payer`, `accept` retries) alarm on every failure. Timers without their own parameter run on the `lease.reap_interval_s` cadence [A: S16.* may add parameters].

| Worker (`actor_id`) | Schedule | Selects | Action | Crash recovery |
| --- | --- | --- | --- | --- |
| `lease_reaper` | `lease.reap_interval_s` | `active` leases with `hard_expires_at < now()` | CT-04 then CT-11, CT-12 or CT-15 | CAS per lease. A crash between CT-04 and the next step leaves `Cell.expired`; `cell_requeuer` finishes it |
| `cell_requeuer` | `lease.reap_interval_s` | cells in `rejected` or `expired` | CT-11, CT-12 or CT-15 | Idempotent by the cell CAS |
| `job_fanout_worker` | event-driven, plus sweep | cells whose job is `suspended`, `settling`, `cancelling` and whose state does not match table 5.22.1 | CT-13, CT-15, CT-16, CT-18 | Per-cell CAS; reruns converge; a job's pause or stop is complete only when the sweep finds nothing left |
| `job_progress` | event-driven, plus sweep | running jobs with all primary accepted (JT-13), assembling jobs (JT-14), jobs past their overrun deadline or with exhausted primaries (JT-15) | the named transition | CAS on the job; no state is held outside the database |
| `settler` | event-driven, plus sweep | jobs in `settling` or `cancelling` whose cells are all terminal | `settle()` (5.29.8) | Whole transaction or nothing; rerun is a no-op after commit |
| `acceptance_retry` | on `job.resumed`, `template.resumed`, `member.reinstated`, `killswitch.released`, plus sweep | cells with `acceptance_deferred_until` set | `accept_cell()` (5.29.6) | Key `payout:<cell_id>` / `mint:<cell_id>` |
| verification pipeline (S8.*, S9.*) | event-driven, plus sweep | submissions in `received` or `checks_passed` with no verdict | SBT-02..05, CT-06..10 | Each step is idempotent on `(submission_id, step)`; a submission with no progress is re-enqueued |
| `credit_expiry_sweeper` | `credit.expiry_sweep_interval_s` | lots with `expires_at <= now()` and `remaining_ucr > 0` | `expire` txn, `member` -> `reserve`, key `expire:<lot_id>` | Atomic per lot; rerun skips lots already expired. A notice goes out `credit.expiry_notice_days` before |
| `reserve_retirer` | `reserve.retire_interval_s` | Reserve balance above `reserve.ceiling_credits` by at least `reserve.retire_min_credits` | `retire` txn, key `retire:<utc_date>` | A rerun on the same date is a no-op; any excess still present is retired on the next date |
| `restitution_payer` | `lease.reap_interval_s` | `pending` appeal restitutions | `grant` txn, key `appealpay:<apl_id>` | Idempotent by key; stays pending while the Reserve is at or below `grant.reserve_floor_credits` |
| timers: `quote_expirer`, `waitlist_expirer`, `waitlist_releaser`, `reservation_expirer`, `service_review_timer`, `restriction_lifter`, `template_autopause_monitor` | cadence above | rows whose deadline has passed | JT-05, JT-08, JT-07, RT-04, SVT-05/06, MT-07, TT-07 | CAS on each row; a missed run only delays |
| `tier_evaluator` | event-driven, plus hourly sweep | members with new observations | MT-02..05 | Pure function of stored observations; rerun gives the same tier |
| `policy_tighten_sweep` | on `policy.version_published` | non-terminal jobs after a `tighten` | JT-11, JT-12, JT-15 | Per-job CAS; rerun converges |
| `ledger_invariant_checker` | `ledger.invariant_check_interval_s` (sampled), `ledger.full_recompute_interval_s` (full) | read-only | `ledger.invariants_passed` or `ledger.invariant_violated` (S6.*) | Read-only, so a crash changes nothing; a missed run is itself alarmed |
| `ledger_checkpointer` | `ledger.checkpoint_interval_s` | none | Publish the checkpoint hash, key `checkpoint:<utc_date>` | Idempotent by date |
| `metric_rollup` | `metrics.rollup_interval_s` | raw events | Upsert by `(metric, window)` | Idempotent upsert |
| `outbox_relay` | continuous | unsent outbox rows | Deliver, then mark sent | A crash between delivery and marking redelivers; consumers dedupe on `event_id` (GU-13) |
| `idempotency_purger`, `retention_purger` | hourly [A] | records past `api.idempotency_ttl_s`, rows past their retention class | Delete | Deleting an expired key is safe because L2 and L3 still protect the objects |
| `fsm_consistency_checker` | `ledger.invariant_check_interval_s` | read-only | Checks CK-01..CK-08 below | Read-only |

**Consistency checks** [D][A: S6.* may register CK-03 to CK-05 as `INV-L` ids]. They run continuously beside the ledger invariants and raise an `Alarm`; CK-03 to CK-05 also emit `ledger.invariant_violated` with `details.check_id`.

| id | Check |
| --- | --- |
| CK-01 | No cell has two `active` leases |
| CK-02 | A cell is `leased` if and only if it has exactly one `active` lease whose id equals `active_lease_id`; an `active` lease past `hard_expires_at` by more than the reaper's lag is a finding |
| CK-03 | Every `accepted` cell has exactly one `mint` or `payout` transaction of 1,000,000 `ucr`, unless reversed by CT-17; no other cell has one |
| CK-04 | Every `closed` escrow has exactly one `settle` or `cancel` transaction, balance 0, and the closing identity holds; no `open` escrow belongs to a terminal job |
| CK-05 | `mint_budget.reserved_ucr` = 1,000,000 x Commons cells in `leased`, `submitted`, `flagged_for_audit`; `minted_ucr` = the sum of `mint` entries of the period |
| CK-06 | No terminal job has a non-terminal cell, an `active` lease or a non-`closed` escrow |
| CK-07 | `entity_seq` is gapless for every entity and the last `to_state` equals the entity's `state` |
| CK-08 | No submission exists without a lease in `submitted`, and no `submitted` lease without a submission |

## 5.30 Race table

Every row names the scenario, the single outcome the system produces, and the mechanism. Rows are the contract for the tests in 5.31 (`AC-race-<nn>` has the same number as `RC-<nn>`). [D]

| id | Scenario | Outcome | Mechanism |
| --- | --- | --- | --- |
| RC-01 | Two donors lease the same `queued` cell at the same moment | One gets `201`; the other gets `409 LEASE_CONFLICT`; one `cell.leased` event | CAS `queued` -> `leased`, partial unique index (GU-01, GU-02) |
| RC-02 | One donor double-taps lease; same `Idempotency-Key` and body | One lease; the second call replays the response with a rotated nonce; the first nonce is dead | L1 idempotency, nonce rotation (5.29.3) |
| RC-03 | Same donor retries lease with a new key after the first succeeded | `409 LEASE_CONFLICT` (the cell is no longer `queued`); the donor's UI reloads its active leases | CAS; the cell state |
| RC-04 | One donor sends parallel lease calls for different cells to exceed `lease.max_active_per_member` | At most `lease.max_active_per_member` succeed; the rest `422 CAP_EXCEEDED` | Member row lock (order 1) with the count inside the lock |
| RC-05 | A lease is requested while a kill switch for the cell's template is engaged or the job is being paused | If the pause committed first: refusal. If the lease committed first: the lease exists, then `job_fanout_worker` revokes it (CT-13) within one pass; nothing is paid in the window | Guards under shared locks; fan-out; `G-accept` |
| RC-06 | A submission and the reaper race at `hard_expires_at` | Exactly one wins (submission accepted, or `410 LEASE_EXPIRED` and requeue) | Two disjoint CAS statements on the lease row (GU-05) |
| RC-07 | A donor submits after the cell was re-leased to someone else | `410 LEASE_EXPIRED`; the other donor's lease is untouched | Old lease is `expired`; nonce and `lease_id` differ |
| RC-08 | The same content arrives twice for one lease with different keys | The first is processed; the second returns the stored outcome; no second event | `UNIQUE (lease_id)`; lease `submitted`; equal hash |
| RC-09 | Two different bodies arrive concurrently for one lease (two tabs) | One wins; the other is `409 STATE_CONFLICT` `already_submitted` and its body is discarded | Lease row lock; CAS |
| RC-10 | A submission carries a wrong nonce, or another member's `lease_id` | Wrong nonce: `403 FORBIDDEN`, lease stays `active`. Other member's lease: `404 NOT_FOUND` | Constant-time hash compare; ownership check |
| RC-11 | A donor declines while the same lease's submission arrives | One wins: either the cell is `queued` (decline) or `submitted`; never both | CAS on the lease row |
| RC-12 | A member is suspended or killed while submitting | If the submission committed first it is `submitted` and DEFERred at `G-accept` until reinstatement; if the revocation committed first the submission is `410 LEASE_EXPIRED` (`revoked`) and the cell requeues | Lease CAS; `G-accept` donor check |
| RC-13 | A lease extension and the reaper race | One wins: extended (reaper skips) or expired (extension `410`) | The extension CAS has `now() <= expires_at` and `state = 'active'` |
| RC-14 | Two workers accept the same cell | One payment; the other returns `already_accepted` | Cell lock; key `payout:<cell_id>` or `mint:<cell_id>` (GU-07) |
| RC-15 | `audit_passed` and `audit_failed` arrive for one flagged cell | The first committed verdict stands; the other is `STATE_CONFLICT` and is dropped | CAS from `flagged_for_audit`; `Audit` terminal states |
| RC-16 | Two `escrow_confirmed` calls for one job | One `hold`, one escrow, N cells once | Job CAS; `hold:<job_id>`; `UNIQUE (job_id)` |
| RC-17 | Two jobs of one member confirmed together against one balance | Only as many as the balance covers; never a negative balance | Member lock; conditional debit (5.29.7) |
| RC-18 | `hold` and the expiry sweep take the same lot | One consumes it; the other uses other lots or fails | Account lock; `expires_at > now()`; `expire:<lot_id>` |
| RC-19 | A payout races a cancel | A payout committed first stands; later cells follow table 5.22.1; settle waits for all cells | `G-accept`; settle precondition |
| RC-20 | `settle()` runs twice or in two workers | One `settle` transaction; escrow 0; second run returns `already_settled` | Job lock; key `settle:<job_id>` (GU-09) |
| RC-21 | `settle()` runs while a cell is being accepted | Settle returns `not_yet` until the acceptance commits, then settles with the cell counted | All-cells-terminal precondition |
| RC-22 | A requester cancels while the last cell is accepted | First commit wins: either `assembling` (cancel is `409 STATE_CONFLICT`) or `cancelling` (JT-13 guard fails) | Job CAS |
| RC-23 | Many concurrent leases try to take the last Commons mint headroom | Exactly the headroom's worth succeed; the rest `422 CAP_EXCEEDED`; no accepted cell lacks headroom | Conditional counter update (GU-12) |
| RC-24 | Parallel leases from one donor near the cap K | Never more reserved than the headroom allows | Member lock; derived `reserved_ucr` |
| RC-25 | A reservation is activated while cancelled or expiring | One terminal state; one escrow movement | `Reservation` CAS; keys `resact`, `rsncancel`, `rsnexpire` |
| RC-26 | Two reviewers approve the same template version at the same moment, or the author approves | Count is exact; the version reaches `approved` once; the author's approval is refused | Version row lock; unique approval key; author predicate |
| RC-27 | A policy tightening is published while a cell is being accepted | If the acceptance committed first it is legitimate; otherwise `G-accept` returns VOID `reject.policy_changed`; never accepted under a policy that no longer permits it | Shared lock on the policy pointer vs exclusive on publish |
| RC-28 | A service is suspended or revoked while submissions that report it are pending | Per `G-accept`: suspended -> REJECT_POLICY, donor not penalized; revoked -> per `inflight_policy` | `G-accept` reads the service state under lock |
| RC-29 | Two appeals for one decision, or a filing at the window edge | At most `appeal.max_per_decision`; a filing after `appeal.window_days` is `422 UNPROCESSABLE` `window_closed` | `UNIQUE (decision_ref, sequence)`; DB-clock check |
| RC-30 | The relay crashes after delivering an event and before marking it sent | The event is delivered again; consumers do nothing the second time | `event_id` dedupe (GU-13) |
| RC-31 | `stop_requested` and `cancel_requested` hit one job together | First commit wins; the other is `STATE_CONFLICT` or skipped | Job CAS |
| RC-32 | Two pause causes arrive, then one clears | The job stays `suspended` until the last cause clears, then resumes once | `pause_causes` set under the job lock (JT-12) |

## 5.31 Given / When / Then criteria

Concurrency tests use a deterministic interleaving harness with named injection points (`before_cas`, `after_cas_before_commit`, `after_commit_before_ack`) and a randomized-interleaving property run whose oracle is the consistency checks CK-01..CK-08 plus the ledger invariants of S6.*. S18.* maps each criterion to a `T-fsm-*` or `T-adv-*` test; this part owns the criteria. [D]

**Races**

- `AC-race-01` Given a `queued` cell and two donors, When both call lease at the same time, Then exactly one gets `201` and one active `Lease`, the other gets `409 LEASE_CONFLICT`, and `leases` holds one `active` row for the cell.
- `AC-race-02` Given a lease call that succeeded but whose response was lost, When the client repeats it with the same key and body, Then the response is replayed with `Idempotent-Replayed: true`-equivalent behavior, no second lease exists, and the nonce from the first response no longer validates.
- `AC-race-03` Given a donor who holds the lease on a cell, When the donor leases it again with a new key, Then `409 LEASE_CONFLICT` and nothing changes.
- `AC-race-04` Given `lease.max_active_per_member` = 3 and a donor holding 2 leases, When the donor sends 5 parallel lease calls on different cells, Then exactly 1 succeeds and 4 get `422 CAP_EXCEEDED`.
- `AC-race-05` Given a job whose template has `kill.template` engaged at the same instant as a lease call, When both commit in either order, Then either the lease is refused, or the lease is revoked by fan-out within one pass and no `payout` exists for that cell.
- `AC-race-06` Given a lease at `hard_expires_at` minus 1 ms, When the submission and the reaper run concurrently, Then exactly one of `lease.submission_received` and `lease.expired` is recorded, never both, and the `StateTransition` rows show one outcome.
- `AC-race-07` Given a cell re-leased after expiry, When the first donor submits with the old nonce, Then `410 LEASE_EXPIRED`, the second donor's lease is `active`, and no submission is stored for the first.
- `AC-race-08` Given a `submitted` lease, When the same content arrives with a different key, Then `200` with the stored outcome, no new event, and one `Submission`.
- `AC-race-09` Given a `submitted` lease, When different content arrives for it, Then `409 STATE_CONFLICT` `already_submitted`, the stored submission is unchanged, and the second body is not stored.
- `AC-race-10` Given an `active` lease, When a submission has a wrong nonce, Then `403 FORBIDDEN`, the lease is still `active`, and an abuse counter increases; When the `lease_id` belongs to another member, Then `404 NOT_FOUND`.
- `AC-race-11` Given an `active` lease, When decline and submission arrive together, Then the cell ends either `queued` with the lease `released` or `submitted` with the lease `submitted`, and never a mix.
- `AC-race-12` Given an `active` lease, When the donor is suspended while submitting, Then either the lease is `revoked` and the cell `queued`, or the cell is `submitted` and its acceptance is deferred until `member.reinstated`; no credit moves meanwhile.
- `AC-race-13` Given a lease within `lease.extend_s` of `expires_at`, When an extension and the reaper race, Then the lease is either extended once (`extensions` = 1) or expired, never both.
- `AC-race-14` Given a `submitted` cell that passed checks, When two workers call `accept_cell`, Then exactly one ledger transaction with key `payout:<cell_id>` (or `mint:<cell_id>`) exists and the donor's balance rose by exactly 1,000,000 `ucr`.
- `AC-race-15` Given a `flagged_for_audit` cell, When `audit_passed` and `audit_failed` are applied concurrently, Then one transition commits, the other is `STATE_CONFLICT`, and the ledger matches the committed one.
- `AC-race-16` Given a `quoted` job, When `escrow_confirmed` is called twice at once, Then one `hold` transaction, one `Escrow`, N cells, and the member balance is reduced by `escrow_ucr` once.
- `AC-race-17` Given a balance of 300 credits and two quoted jobs needing 276 each, When both are confirmed at once, Then one is `admitted`, the other gets `422 INSUFFICIENT_CREDIT`, and the balance never goes below 0.
- `AC-race-18` Given a lot expiring now holding part of the balance, When `escrow_confirmed` and the expiry sweep run together, Then no expired credit is held, the lot is consumed once, and the account balance equals the sum of its lots.
- `AC-race-19` Given a running job with a cell in `submitted`, When the requester cancels while the cell is accepted, Then the donor is paid once, the job settles only after the cell is terminal, and the closing identity holds.
- `AC-race-20` Given a `settling` job with all cells terminal, When `settle()` runs twice concurrently, Then one `settle` transaction exists, the escrow balance is exactly 0, and the second call returns `already_settled`.
- `AC-race-21` Given a `settling` job with one cell mid-acceptance, When `settle()` starts, Then it returns `not_yet` and does not post, and after the acceptance commits a later run settles with that payout counted.
- `AC-race-22` Given a `running` job with one cell left, When the last cell is accepted and the requester cancels at the same time, Then the job is `assembling` and cancel is `409 STATE_CONFLICT`, or the job is `cancelling` and `job.all_cells_accepted` does not fire; never both.
- `AC-race-23` Given `mint.monthly_cap_credits` headroom of exactly 5 cells, When 20 donors lease Commons cells at once, Then exactly 5 succeed, 15 get `422 CAP_EXCEEDED`, and after acceptance `minted_ucr + reserved_ucr` never exceeds the cap.
- `AC-race-24` Given a donor whose headroom to the cap K x multiplier is 2 cells, When 5 parallel leases are sent, Then exactly 2 succeed.
- `AC-race-25` Given a `held` reservation, When activation and cancellation arrive together, Then one of `activated` or `cancelled` holds, and the escrow moved at most once.
- `AC-race-26` Given `template.min_reviewers_new` = 2, When two reviewers approve at once, Then the version is `approved` exactly once with 2 approvals; When the author approves, Then the approval is refused and no state changes.
- `AC-race-27` Given a job stamped under policy version 4, When version 5 tightens the rule it relied on while a cell is being accepted, Then the cell is accepted before the publish commit or voided with `reject.policy_changed`, and no credit is paid in the second case.
- `AC-race-28` Given a submission that reports a service, When the service is suspended before acceptance, Then the cell is `rejected` with `reject.policy_changed`, the donor's reliability is unchanged, and the cell requeues.
- `AC-race-29` Given `appeal.max_per_decision` = 1, When two appeals for one decision are filed at once, Then one `Appeal` exists and the other is `409 ALREADY_EXISTS`; When one is filed after `appeal.window_days`, Then `422 UNPROCESSABLE` `window_closed`.
- `AC-race-30` Given an outbox event delivered but not marked sent, When the relay restarts, Then the event is delivered again and the consumer produces no second effect.
- `AC-race-31` Given a `running` job, When `stop_requested` and `cancel_requested` arrive together, Then one of `settling` or `cancelling` holds, and the other request is `409 STATE_CONFLICT`.
- `AC-race-32` Given a job paused by two causes, When one clears, Then it stays `suspended`; When the last clears, Then it resumes exactly once and `paused_total_s` is extended once.

**State-machine properties**

- `AC-fsm-01` Given a cell in `accepted`, When `cell.checks_failed` is applied, Then `409 STATE_CONFLICT` with `transition_not_allowed`, and no event or `StateTransition` row is written.
- `AC-fsm-02` Given any transition of any table in this part, When it commits, Then exactly one `StateTransition` row and one outbox event with the table's event name exist with consecutive `entity_seq`.
- `AC-fsm-03` Given an injected failure after the CAS and before the ledger posting, When the transaction ends, Then neither the state change nor any ledger entry exists.
- `AC-fsm-04` Given every state marked (T) in S0.9, When any event is applied, Then it is refused, except `accepted` -> `overturned` through CT-17 and `banned` -> `active` through MS-05.
- `AC-fsm-05` Given a restricted member with `trust.restriction_days` elapsed, When `restriction_lifter` runs twice, Then the tier is restored once and `member.restriction_lifted` is emitted once.
- `AC-fsm-06` Given a template version in `awaiting_second_review` and `template.min_reviewers_new` = 2, When the same reviewer approves again, Then the unique key refuses it.
- `AC-fsm-07` Given a service with only `unknown` flags, When `service.approved` is attempted, Then it is refused (`unknown` evaluates as `no`) and the state stays `in_review`.
- `AC-fsm-08` Given the FD§3.3 job (N = 240, price 1.15), When it runs to `completed` with all cells accepted, Then 264 `payout` transactions of 1,000,000 `ucr`, one `levy` of 12,000,000 `ucr`, refund 0, escrow balance 0, and CK-03 and CK-04 pass. The inputs are the FD's illustrative values, not measurements.

## Issues raised

Each resolution is already applied in this file; `C-001` consolidates them into S2.* and may record a different one. [D]

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-54` | major | FD§3.4 | S0.10.6 describes `lease.submit_grace_s` as accepting a late paste-back "if the cell is not yet re-leased", while S0.9.3 and FD§3.4 requeue an expired cell at once. The outcome would depend on reaper timing and on which donor leased first, and two lease CAS statements could race | `hard_expires_at` = `expires_at` + `lease.submit_grace_s` is stored at issue; the cell cannot be re-leased before it; a submission is valid through it and refused after it regardless of reaper timing (5.23.3, 5.29.4) | proposed |
| `ISS-55` | major | FD§3.4, FD§5.6 | Every transition must be logged with the policy version, but `Event` has retention class `ops` (30 days by default), shorter than an appeal or a provenance question can last | New append-only entity `StateTransition` (`stt_`) with the retention class of the parent entity and a per-entity gapless `entity_seq` (5.21.3) | proposed |
| `ISS-56` | major | FD§4.4, FD§5.5 | A rejected cell "can appeal", but the FD does not say what pays the donor when a rejection is overturned after the job's escrow is closed, and `mint` is only for accepted Commons cells | An overturned `cell_rejection` (and the lots lost during an overturned suspension or ban) is restituted by a `grant` entry from the Reserve, reason `appeal_restitution`, never from escrow or `mint`; it waits while the Reserve is at or below `grant.reserve_floor_credits` (5.27). Whether the Reserve may be used this way is an owner decision | needs_owner |

Convention additions made by this part (not issues, listed so `C-001` can fold them back):

1. Headings of this file are numbered `5.21`..`5.39` (5.21).
2. New entities and fields: `StateTransition` (`stt_`, `ISS-55`); `TemplateApproval` (`tap_`, `template_approvals`, `member_bound`-free, `permanent`) for per-reviewer approvals with `content_hash`; `MintBudget` (`mbd_`, `mint_budgets`, `permanent`, S6.* owns: `period`, `minted_ucr`, `reserved_ucr`, `cap_ucr`). Fields this part needs from S5a: `Job.origin`, `quote_expires_at`, `closure_reason`, `pause_causes`, `state_before_pause`, `pause_started_at`, `paused_total_s`, `admitted_at`, `escrow_id`, `levy_reserved_ucr`, `held_ucr`; `Cell.active_lease_id`, `attempt`, `acceptance_deferred_until`; `Lease.member_id`, `attempt`, `nonce_hash`, `expires_at`, `hard_expires_at`, `extensions`, `release_reason`; `Submission.content_hash`, `late`, `time_to_submit_s`, `reported_service_id`; `Member.tier_before_restriction`, `restricted_until`; `ServiceRegistryEntry.approved_at`, `review_due_at`, `grace_deadline_at`, `suspended_cause`; `Appeal.decision_ref`, `sequence`, `due_by`, evidence snapshot.
3. Transition `screening --job.cancel_requested--> cancelled` (JT-19).
4. `closure_reason` value `cells_exhausted` (JT-15).
5. Log-only event `lease.extended` (5.23.3) with no state change.
6. Transition `banned --member.reinstated--> active`, only through an overturned appeal (MS-05).
7. Log-only event `template.approval_recorded` for approvals 2..k-1 when `template.min_reviewers_new` or `template.min_reviewers_edit` exceeds 2 (TT-04).
8. Transition `in_review --service.review_lapsed--> suspended` when the review began from `review_due` and the grace elapsed (SVT-06).
9. `cell.declined` is also the event for a system revocation not caused by the cell, with `details.initiator` = `system` (CT-18); `cell.cancelled` from `leased` only with `revoke_lease` (CT-15).
10. `grant` entries with reason `appeal_restitution` (`ISS-56`) and `reserve_donation` on member closure (MS-04).
11. Metrics `hamyar_bgjob_last_success_seconds` and `hamyar_bgjob_failures_total`, and the worker names of 5.29.10 as `actor_id` values.
12. Permission names `perm.job.*`, `perm.member.*`, `perm.template.*`, `perm.service.*`, `perm.submission.release` are proposals for S10.* (5.21.1).
