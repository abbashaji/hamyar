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
