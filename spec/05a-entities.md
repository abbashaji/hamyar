# 5. Domain Model: Entities

*Spec part 5a · owner cell C-003 · binding on every part that stores or reads these entities. Written against Founding Document draft v0.1 (FD) and `spec/00-conventions.md` (S0). Nothing here is legal advice and nothing here has been verified against any provider's terms or any law.*

## 5.1 Scope, sources and how to read this part

- **Scope.** This part fixes the stored shape of every entity named in S0.7: the 28 entities named by the prompt (scope B) and the 29 entities added by S0. That is 57 entities. For each: fields, types, constraints, keys, unique constraints, indexes, retention, what is stored and what is deliberately not stored. DDL is given for the critical entities in S5.14. [D]
- **Out of scope.** Guards, side effects and concurrency of the state machines (state-machine part of S5.*), ledger postings, price and admission algorithms (S6.*), the policy evaluator and registry workflow (S7.*), identity protocols (S10.*) and API shapes (S15.*). This part fixes only the columns they read and write, and the stored state names, which are exactly the names in S0.9. [D]
- **File name.** S0.13 proposes `spec/05a-domain-model.md`; the owning cell's `allowed_paths` are authoritative, so this file is `spec/05a-entities.md` (`ISS-52`). [D]
- **Field tables** have the columns `Field`, `Type`, `Null / constraint`, `Note`. Types use the aliases of S5.2.1. `NN` means NOT NULL. Common columns (S5.2.2) are not repeated unless they differ.
- **Per entity** a header line gives table, prefix, mutability class (S5.2.3) and retention class (S0.7). After the table come `Keys`, `Unique`, `Indexes`, `Stored` and `Not stored`.
- **Normative names.** Entity, table, prefix, enum, state, event and parameter names are used exactly as in S0. A name this part needs that S0 lacks is marked [A] and listed in `ISS-51`.
- **No provider fact is stored as a constant.** Every provider-dependent value (terms flags, prefill templates, URL limits, regional answers) lives in rows entered by a reviewer and is [V] until a human records it. [D]

## 5.2 Modelling conventions

### 5.2.1 Column type aliases [D]

| Alias | SQL type | Rule |
| --- | --- | --- |
| `id` | `text` | `<prefix>_<ulid>` (S0.6.3); a `CHECK (is_id(col,'<prefix>'))` on every id and foreign-key column |
| `ts` | `timestamptz` | UTC only, server-assigned (S0.6.2) |
| `day` | `date` | UTC calendar day; used where only day granularity may be kept (privacy) |
| `int` / `int64` | `integer` / `bigint` | |
| `ucr` | `bigint` | micro-credits, signed; column suffix `_ucr` (S0.6.1) |
| `ppm` | `bigint` | parts per million; suffix `_ppm` |
| `hash` | `text` | `sha256:<64 lowercase hex>`; `CHECK (col ~ '^sha256:[0-9a-f]{64}$')` |
| `bytes32` | `bytea` | `CHECK (octet_length(col) = 32)`; used for keyed hashes and token hashes |
| `enum(x)` | `text` | `CHECK (col IN (...))` using the values of S0.8 or S5.2.5 |
| `json` | `jsonb` | canonicalized (RFC 8785) before hashing; size capped by a `CHECK (octet_length(col::text) <= n)` |
| `arr` | `text[]` | members validated against an enum by a `CHECK` |

No `float`, `real`, `numeric` or `money` column exists anywhere in the model. [D]

### 5.2.2 Common columns [D]

Every table has `id` (PK) and `created_at` (`ts`, NN, server default `now()`). A table in class `MUT`, `IMS` or `DER` also has `updated_at` (`ts`, NN) and `row_version` (`int`, NN, default 1, incremented by 1 on every update by a trigger). A table in class `IMM` or `CHN` has neither and no update or delete path.

### 5.2.3 Mutability classes [D]

| Class | Meaning | Enforcement |
| --- | --- | --- |
| `IMM` | Immutable: insert only. A correction is a new row that points at the old one (`supersedes_id` or a reversal) | `INSERT`/`SELECT` privileges only; a `BEFORE UPDATE OR DELETE` trigger raises `immutable_row` as defense in depth |
| `CHN` | `IMM` plus a hash chain (`prev_hash`, `entry_hash`) and a gap-free `seq` | as `IMM`, plus the sole writer function of S5.14 and the daily checkpoint |
| `IMS` | Immutable content, mutable state: content columns are frozen by a trigger from a named point; only the state and timestamp columns named in the table change, and only through the state machine | column-level trigger lists them; any other column change raises `frozen_column` |
| `MUT` | Mutable with optimistic concurrency (`row_version`, S0.11.7). Every change also emits its state event (S0.9.1) | |
| `DER` | Derived cache (a balance, a remaining amount, a counter). The truth is in `IMM`/`CHN` rows; an invariant check recomputes it | update allowed only by the single module that owns it |

### 5.2.4 Database roles [A]

| Role | May do | May not |
| --- | --- | --- |
| `app_rw` | `INSERT`/`UPDATE` on `MUT` and `IMS` tables; `INSERT` on `IMM` tables except ledger tables | any change to `CHN` tables; `DELETE` anywhere; `SELECT` on `gold_cells.answer_*` |
| `ledger_svc` | calls `ledger_post()` (S5.14), the only function that inserts into `ledger_transactions` and `ledger_entries` and updates `ledger_accounts.balance_ucr` and `credit_lots.remaining_ucr` | anything else |
| `verifier_svc` | `SELECT` on `gold_cells.answer_*`; `INSERT` on `verification_records` | writing ledger tables |
| `retention_svc` | `DELETE`/`UPDATE ... SET col = NULL` only on the columns and tables named in the retention rules; nothing on `CHN` or `permanent` tables | |
| `readonly` | `SELECT` through views that exclude secret and answer columns | |

Backups, replicas and restore tooling are S4.* concerns. A restore MUST re-run the chain verification of S5.15 before the system accepts writes. [D]

### 5.2.5 Local enumerations (convention gaps) [A]

Values S0.8 does not list but the model needs. They are stored exactly as written and are reported in `ISS-51`.

| Enum | Values |
| --- | --- |
| `invite_status` | `issued`, `redeemed`, `expired`, `revoked` |
| `key_purpose` / `key_status` | `auth`, `recovery` / `active`, `rotated`, `revoked` |
| `admin_status` / `credential_status` | `invited`, `active`, `disabled` / `active`, `revoked` |
| `device_status` | `active`, `blocked` |
| `topic_status` / `badge_status` / `team_status` | `active`, `retired` / `active`, `retired` / `active`, `archived` |
| `upload_status` | `received`, `screening`, `accepted`, `rejected`, `split`, `purged` |
| `upload_media_type` | `text/plain`, `text/csv`, `application/json` |
| `waitlist_state` | `waiting`, `released`, `expired`, `cancelled` |
| `service_kind` | `general_chat`, `open_weight_hosted`, `open_weight_local` |
| `document_kind` / `terms_media_type` | `terms`, `usage_policy`, `written_permission` / `text/html`, `text/plain`, `application/pdf` |
| `suspension_cause` | `kill_switch`, `review_lapsed` |
| `risk_class` | `standard`, `high` (high-risk templates use blanket redundancy, FD§4.4) |
| `audit_trigger` | `sampled`, `anomaly`, `new_donor`, `blanket_redundancy`, `high_risk_template` |
| `audit_verdict` | `primary_correct`, `primary_incorrect`, `inconclusive` |
| `gold_status` | `active`, `retired`, `compromised` |
| `quarantine_reason` | `output_url`, `code_to_run`, `action_request`, `other_flag` |
| `report_kind` | `suspected_injection`, `prohibited_content`, `sensitive_data_present`, `harassment_or_targeting`, `forged_or_copied_result`, `malicious_template`, `other` |
| `report_subject_type` | `cell`, `job`, `template_version`, `member`, `submission`, `service` |
| `report_outcome` | `no_action`, `template_paused`, `job_stopped`, `member_suspended`, `member_banned`, `service_flagged`, `other_action` |
| `appeal_subject_type` | `cell`, `member`, `job`, `template_version`, `report` |
| `referral_state` | `issued`, `redeemed`, `qualified`, `paid`, `voided`, `expired` |
| `lot_effect` | `create`, `consume`, `restore`, `none` |
| `deliverable_state` / `deliverable_format` | `assembling`, `ready`, `purged` / `jsonl`, `csv`, `txt`, `json` |
| `gate_id` | `G0`, `G1`, `G2`, `G3`, `G4`, `G5` (FD§8.3) |
| `changelog_subject_type` | `parameter`, `policy_version`, `template_version`, `service_registry_entry`, `other` |
| `experiment_status` / `prereg_status` | `draft`, `running`, `stopped` / `draft`, `locked` |
| `alarm_severity` / `alarm_state` | `info`, `warning`, `critical` / `open`, `acknowledged`, `resolved` |
| `check_run_kind` / `check_result` | `per_commit`, `sampled`, `full_recompute`, `checkpoint` / `passed`, `violated`, `error` |
| `metric_scope` / `metric_unit` | `global`, `job_type`, `template`, `service` / `count`, `ppm`, `ucr`, `seconds` |

### 5.2.6 Foreign keys [D]

All foreign keys are `ON DELETE RESTRICT ON UPDATE RESTRICT`; no cascade exists. Circular references (`escrows` and `ledger_accounts`, `cells` and `leases`, `cells` and `submissions`) are `DEFERRABLE INITIALLY DEFERRED`. A foreign key may point at a row whose payload columns were purged by retention; purging nulls payload columns and never removes the row, except where the retention rule of an entity says rows are reduced to counts. A reference to a `members` row stays valid after closure because that row is reduced, not deleted (S5.6.1).

## 5.3 Data minimization: stored versus deliberately not stored

### 5.3.1 Global rules [D]

| Never stored in any table, column, log or event | Why | Where the nearest permitted thing lives |
| --- | --- | --- |
| A raw IP address | FD Principle 8; `retention.raw_ip_stored` = false (constant) | A keyed hash with a TTL: `devices.creation_ip_hash` and the rate-limit counters (S5.3.3) |
| A clear-text e-mail address | S0.7 naming rules; `identity.email_optional` = true | Field-encrypted ciphertext plus a keyed lookup hash on `members` |
| A provider credential, cookie, session, API key or account identifier | Ground rule 3 | Nothing. A volunteer reports only the service and a model label, as text |
| The text of a volunteer's chat page, a chat share-link, a clipboard capture, a screenshot | Ground rule 3; the panel's automatic chat-link capture was removed (FD§10) | `submissions.output_text` holds only what the volunteer pasted back into the form |
| A real name, phone number, postal address, country, city, coordinates, device model, user-agent string or browser fingerprint | FD Principle 8; `public.location_display` = `never` | Optional `members.time_zone` (an IANA zone the member chose) |
| A password or a private key | S0.6.4 | Public keys (`member_keys`, `admin_credentials`) |
| A nickname, avatar or profile text of a member | Not needed for any scope A to I feature; adding one is a convention edit (S0.1) | Teams carry a team name, not member names |
| Precise last-seen times of a member | Timing leaks | `members.last_active_day` (UTC day) |
| The original file name of an upload | May contain a name | `uploads.content_hash` |

### 5.3.2 The salted-hash volunteer id and its salt scope [D]

Provenance (FD§5.6) records "a salted-hash volunteer ID that requesters never see". Definition, from S0.6.4: `volunteer_handle = 'vol_' || hex(first 16 bytes of HMAC-SHA-256(key = secret.volunteer_handle_key[v], data = member_id))`.

| Item | Decision |
| --- | --- |
| Salt scope | One system-wide secret per key version `v`. It is not per job, per requester or per template |
| Stored in | `submissions.volunteer_handle` with `handle_key_version`, and in the internal manifest (S5.8.8). Computed on read, never stored, for `vol_` shown on public pages (S5.9.2) |
| Never exposed to | Any requester surface, including the exported manifest (the export is a redacted rendering, `ISS-53`) |
| Linkability | Within one key version all of a member's handles are linkable to each other by anyone holding the data, but not to `member_id` without the key. The platform needs this linkage: detection of one donor acting as both primary and auditor, and copy detection |
| Rotation | Rotating the key creates version `v+1`; old handles stay as written and become unlinkable to new ones. Rotation before any public exposure is required (`security.rotate_before_public_exposure`) |
| Alternative not adopted | Per-job salting (`data = member_id \|\| job_id`) would reduce cross-job linkability inside a dump. S0.6.4 fixed `data = member_id`; independence checks use `member_id` inside the verifier instead. Domain separation between provenance and public handles is left to S10.* [A] |
| Limit | A handle is a pseudonym, not anonymity. Anyone holding both the database and the key can link it to a `mem_` id (S5.3.4) |

### 5.3.3 Keyed hashes held in the model [D]

| Column | Computed as | Key (secret, S10.* owns the list) [A] | Kept for |
| --- | --- | --- | --- |
| `devices.device_token_hash` | HMAC-SHA-256 of a random 256-bit token the client keeps in its own storage | `secret.device_hash_key[v]` | `retention.session_days` after last use |
| `devices.creation_ip_hash` | HMAC-SHA-256 of the client IP at identity creation | `secret.ip_hash_key[v]` | `retention.ip_hash_ttl_days` (default 1 day), then set to NULL |
| `members.email_lookup_hash` | HMAC-SHA-256 of the lower-cased address | `secret.email_lookup_key[v]` | while the member is not `closed` |
| `members.email_ciphertext` | AES-256-GCM field encryption of the address | `secret.email_encryption_key[v]` | as above |
| `sessions.token_hash`, `leases.nonce_hash`, `invites.code_hash` | SHA-256 of a 128- or 256-bit CSPRNG value (no key needed, S0.6.4) | none | their TTLs |
| `submissions.volunteer_handle` | S5.3.2 | `secret.volunteer_handle_key[v]` | with the submission row (a hash, so it stays after payload purge) |

Rate-limit counters (per member, per IP hash, per invite tree) are infrastructure state keyed by these hashes with a TTL equal to their window; they live in the cache or in a `rate_counters` table that is not a domain entity, and they hold no payload (S4.*, S10.*). [A]

### 5.3.4 What a database dump reveals [D]

A full dump reveals pseudonymous `mem_` ids; public keys; day-granular activity; the submitted text of cells still inside the payload retention window; ciphertext of optional e-mails (not readable without the secrets); keyed hashes (not reversible without the keys); the ledger; and the registry. It reveals no IP address and no provider credential, because none is stored. Whether a seizure of the host, the secrets or both defeats pseudonymity, and what the platform can NOT promise, is stated in S10.*; this part states only that the data model never contains more than the list above. Legal questions about compelled disclosure and about keyed IP hashes with a one-day TTL are [V] for counsel (`CNS`).

## 5.4 Entity catalogue, mutability and retention

One row per entity of S0.7 (57 rows). `Class` is S5.2.3. `Retention` is the S0.7 class, with exceptions marked [A] in `ISS-51`. The last column says how a correction is modelled, because no `IMM` or `CHN` row is ever edited. [D]

| Entity | Section | Class | Retention | A correction is modelled as |
| --- | --- | --- | --- | --- |
| `Member` | S5.6.1 | `MUT` | `member_bound` | status and tier changes (events); closure reduces the row to a tombstone |
| `MemberKey` | S5.6.2 | `MUT` | `member_bound` | rotation: new key row, old row `rotated` |
| `Device` | S5.6.3 | `MUT` | `short` | `blocked` status; purge nulls hashes |
| `Session` | S5.6.4 | `MUT` | `short` | `revoked_at`; expiry |
| `Invite` | S5.6.5 | `MUT` | `member_bound` | `revoked` status |
| `OptIn` | S5.6.6 | `MUT` | `member_bound` | new version of the row; change event carries before and after hashes |
| `TopicCategory` | S5.6.7 | `MUT` | `permanent` | `retired` status; every change is a `ChangeLogEntry` |
| `AdminUser` | S5.6.8 | `MUT` | `permanent` | `disabled` status; never deleted |
| `AdminCredential` | S5.6.9 | `MUT` | `permanent` | `revoked` status |
| `AdminAction` | S5.6.10 | `CHN` | `permanent` | a later action that references the earlier one |
| `Template` | S5.7.1 | `MUT` | `permanent` | pointer to the active `TemplateVersion` |
| `TemplateVersion` | S5.7.2 | `IMS` | `permanent` | a new version; the old one is `retired` |
| `Glossary` | S5.7.3 | `IMS` | `job_bound` | a new glossary row for a new job |
| `Upload` | S5.7.4 | `IMS` | `job_bound` | a new upload; the old is `purged` or `rejected` |
| `Job` | S5.7.5 | `MUT` | `job_bound` | state machine; terminal states never reopen |
| `Reservation` | S5.7.6 | `MUT` | `job_bound` | `cancelled` or `expired`; escrow refund is a ledger entry |
| `WaitlistEntry` | S5.7.7 | `MUT` | `job_bound` | `cancelled` or `expired` |
| `Cell` | S5.8.1 | `MUT` | `job_bound` | state machine; `overturned` plus a `rework` cell |
| `Lease` | S5.8.2 | `MUT` | `job_bound` | `expired`, `released`, `revoked`; a new lease row per attempt |
| `Submission` | S5.8.3 | `IMS` | `job_bound` | `rejected`; the output text is never edited |
| `VerificationRecord` | S5.8.4 | `IMS` | `job_bound` | a superseding record (`supersedes_id`) |
| `GoldCell` | S5.8.5 | `IMS` | `permanent` | `retired` or `compromised`; a new gold cell |
| `Audit` | S5.8.6 | `MUT` | `job_bound` | state machine; `cancelled` |
| `Deliverable` | S5.8.7 | `IMS` | `job_bound` | a new deliverable row is not allowed; reassembly is a new job state, see S5.8.7 |
| `Manifest` | S5.8.8 | `IMM` | `job_bound` (rows stay) | superseding manifest row |
| `LedgerAccount` | S5.9.1 | `DER` | `permanent` | never edited except its cached balance |
| `LedgerEntry` | S5.9.2 | `CHN` | `permanent` | a `reversal` entry (two approvers) |
| `LedgerTransaction` | S5.9.3 | `IMM` | `permanent` | a `reversal` transaction |
| `CreditLot` | S5.9.4 | `DER` | `permanent` | rebuilt from entries; never edited by hand |
| `Escrow` | S5.9.5 | `MUT` | `permanent` | state machine; caches checked against entries |
| `Reserve` | S5.9.6 | `MUT` | `permanent` | singleton; caches checked against entries |
| `Policy` | S5.10.1 | `MUT` | `permanent` | pointer to the active `PolicyVersion` |
| `PolicyVersion` | S5.10.2 | `IMM` | `permanent` | a new version |
| `Rule` | S5.10.3 | `IMM` | `permanent` | new rows under a new `PolicyVersion` |
| `ServiceRegistryEntry` | S5.10.4 | `MUT` | `permanent` | review machine; evidence rows are `IMM` |
| `TermsCopy` | S5.10.5 | `IMM` | `permanent` | a new capture that supersedes |
| `FlagAnswer` | S5.10.6 | `IMM` | `permanent` | a later dated answer; the latest wins |
| `Report` | S5.11.1 | `MUT` | `moderation` | state machine; reduced to counts after retention |
| `Appeal` | S5.11.2 | `MUT` | `moderation` | state machine; a resulting `AdminAction` |
| `Team` | S5.11.3 | `MUT` | `member_bound` | `archived` status |
| `Badge` | S5.11.4 | `IMS` | `permanent` | a new badge row; the old is `retired` |
| `BadgeAward` | S5.11.5 | `IMM` | `member_bound` | none; deleted with the member's data on closure |
| `Referral` | S5.11.6 | `MUT` | `member_bound` | `voided` with a reason |
| `Parameter` | S5.12.1 | `MUT` | `permanent` | pointer to the current `ParameterVersion` |
| `ParameterVersion` | S5.12.2 | `IMM` | `permanent` | a new version |
| `KillSwitch` | S5.12.3 | `IMM` | `permanent` | a new state row (`engaged`, `released`) |
| `FeatureFlag` | S5.12.4 | `MUT` | `permanent` | every change is an `AdminAction` and a `ChangeLogEntry` |
| `ChangeLogEntry` | S5.12.5 | `IMM` | `permanent` | a later entry that references it |
| `LaunchGateItem` | S5.12.6 | `IMM` | `permanent` | a new revision row (`ISS-53`) |
| `Experiment` | S5.13.1 | `IMS` | `permanent` | `stopped`; arms are frozen once `running` |
| `ExperimentAssignment` | S5.13.2 | `IMM` | `permanent` | none; assignments are never changed |
| `PreRegistration` | S5.13.3 | `IMS` | `permanent` | after lock, an amendment row that points at it |
| `Event` | S5.13.4 | `IMS` | `ops` | none; only `published_at` is set once |
| `MetricSnapshot` | S5.13.5 | `IMM` | `permanent` | a superseding snapshot |
| `CalibrationRecord` | S5.13.6 | `IMM` | `permanent` | a superseding record |
| `InvariantCheck` | S5.13.7 | `IMM` | `ops` (exception [A]) | none; checkpoint and `violated` rows are exempt from purging |
| `Alarm` | S5.13.8 | `MUT` | `ops` | state machine (`open`, `acknowledged`, `resolved`) |

## 5.5 Entity-relationship summary

Notation: `A 1--* B` means one `A` has many `B` (the foreign key is on `B`); `0..1` marks an optional parent. Arrows show the direction of the foreign key. [D]

```
IDENTITY
  Member 1--* MemberKey            Member 1--* Session(member)       Member 0..1--1 OptIn
  Device 1--* MemberKey (device_id)   Device 1--* Member (creating_device_id)
  Member 1--* Invite (issuer)      Invite 0..1--1 Member (redeemed_by)   Member *--0..1 Team
  AdminUser 1--* AdminCredential   AdminUser 1--* Session(admin)     AdminUser 1--* AdminAction

TEMPLATES AND JOBS
  Template 1--* TemplateVersion    Template 0..1--1 TemplateVersion (active_version_id)
  Job *--1 TemplateVersion         Job *--1 PolicyVersion (stamped)  Job *--0..1 Member (requester; null = Commons)
  Job 1--0..1 Upload               Job 1--0..1 Glossary             Job 1--0..1 Escrow
  Job 1--0..1 WaitlistEntry        Reservation 1--0..1 Job (activated_job_id)   Reservation 1--1 Escrow

EXECUTION AND VERIFICATION
  Job 1--* Cell                    Cell *--1 TemplateVersion        Cell *--0..1 GoldCell
  Cell 1--* Lease (one active)     Lease *--1 Member                Lease 1--0..1 Submission
  Cell 1--* Submission             Submission 1--* VerificationRecord   Cell *--0..1 Audit
  Audit 1--1 Cell (primary_cell)   Audit 0..1--1 Cell (second) / (third)
  Job 1--0..1 Deliverable          Deliverable 1--1 Manifest

CREDIT
  Member 1--1 LedgerAccount(member)    Escrow 1--1 LedgerAccount(escrow)    Reserve 1--1 LedgerAccount(reserve)
  LedgerTransaction 1--* LedgerEntry   LedgerEntry *--1 LedgerAccount (debit) and (credit)
  LedgerEntry *--0..1 CreditLot        CreditLot *--1 Member            LedgerEntry 0..1--1 LedgerEntry (reverses / restores)
  Cell *--0..1 LedgerTransaction (credit_txn_id)    Escrow *--0..1 LedgerTransaction (closing_txn_id)

POLICY AND REGISTRY
  Policy 1--* PolicyVersion        PolicyVersion 1--* Rule          PolicyVersion 0..1--1 ChangeLogEntry (loosen)
  ServiceRegistryEntry 1--* TermsCopy   ServiceRegistryEntry 1--* FlagAnswer   FlagAnswer *--0..1 TermsCopy
  ServiceRegistryEntry 0..1--1 TermsCopy (current)     Lease/Submission *--0..1 ServiceRegistryEntry (reported)

MODERATION, COMMUNITY
  Report *--0..1 Member (reporter)     Appeal *--1 Member (appellant)    Appeal *--0..1 AdminUser (assigned, second)
  Team 1--* Member                     Badge 1--* BadgeAward *--1 Member
  Referral *--1 Member (referrer)      Referral 0..1--1 Member (newcomer)   Referral *--0..2 LedgerTransaction (bonus)

CONFIGURATION, LAUNCH, MEASUREMENT
  Parameter 1--* ParameterVersion      Parameter 0..1--1 ParameterVersion (current)   ParameterVersion 0..1--1 ChangeLogEntry
  KillSwitch rows by switch_key        FeatureFlag *--0..1 Experiment   Experiment 1--* ExperimentAssignment *--1 Member
  PreRegistration 0..1--* Experiment   LaunchGateItem revisions by item_key    LaunchGateItem *--0..1 ServiceRegistryEntry
  MetricSnapshot, Event, InvariantCheck, Alarm, CalibrationRecord reference subjects by (subject_type, subject_id) or by a named FK
```

**Reference rules** [D]

1. The ledger is reached from business entities only through `LedgerTransaction.natural_key` and `Cell.credit_txn_id`, `Escrow.closing_txn_id`, `Referral.bonus_*_txn_id`. No business table stores an amount that it also posts; the amount lives in `LedgerEntry`, and business columns that echo it are caches checked by the invariants.
2. `AdminAction` is the audit trail for every privileged write. Approvals (template, service, ledger reversal, launch sign-off) are `AdminAction` rows that reference the approved row and its content hash, not columns edited on the approved row (S5.15).
3. Polymorphic references (`subject_type`, `subject_id`) exist only on `AdminAction`, `Report`, `Appeal`, `Event`, `Alarm` and `ChangeLogEntry`. Every other relationship is a real foreign key. Polymorphic ids are validated by the writing service against the prefix of the id (S0.6.3).
