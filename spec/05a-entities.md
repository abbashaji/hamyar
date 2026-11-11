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

## 5.6 Identity and access entities

### 5.6.1 `Member` · `members` · `mem_` · class `MUT` · retention `member_bound`

A pseudonymous identity. Holds the `donor` and `requester` capabilities (S0.8.2); the `reviewer` and `operator` roles belong to `AdminUser`. Machine: trust tier and status (S0.9.4). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `status` | enum(`member_status`) | NN, default `active` | orthogonal to the tier |
| `status_changed_at` | ts | NN | |
| `trust_tier` | enum | NN, default `new` | `new`, `established`, `trusted`, `restricted` |
| `tier_before_restriction` | enum | set iff `trust_tier = 'restricted'` | one of the three non-restricted tiers |
| `restricted_until` | ts | null | `trust.restriction_days` after the restriction |
| `locale`, `digits`, `calendar` | enum | NN | defaults from `i18n.*`; member can change |
| `time_zone` | text | null | IANA name chosen by the member; never inferred from an IP |
| `creating_device_id` | id `dev_` | null, FK | the device that created the identity; used for `ratelimit.device_new_members_per_day` |
| `invite_id` | id `inv_` | null, FK (deferred) | the invite redeemed, if any |
| `invite_root_member_id`, `invite_depth` | id `mem_`, int | root null for a founder; depth >= 0 | denormalized tree position for `invite.tree_*` limits |
| `team_id`, `team_joined_at` | id `tem_`, ts | null | a member is in at most one team [A] |
| `email_ciphertext`, `email_key_version`, `email_lookup_hash`, `email_verified_at` | bytes, int, bytes32, ts | all null or `ciphertext` and `lookup_hash` both set | optional e-mail (FD§3.2); S5.3.3 |
| `accepted_cells_count` | int | NN, default 0 | `DER`; counts accepted cells of every kind |
| `first_accepted_at` | ts | null | set once; the starter-grant and referral condition |
| `reliability_ppm`, `reliability_obs` | ppm, int | `0..1000000`; obs >= 0 | `DER` cache of the Beta estimate over the last `verify.reliability_window_obs` gold and audit observations |
| `starter_granted_at` | ts | null | set once with the `grant` entry |
| `recovery_cooldown_until` | ts | null | `identity.recovery_cooldown_s` after a recovery |
| `last_active_day` | day | null | day granularity only |
| `closed_at` | ts | null; NN when `status = 'closed'` | |

**Keys** PK `id`; FKs as above. **Unique** `email_lookup_hash` (where not null). **Indexes** `(status, trust_tier)`; `(team_id)`; `(invite_root_member_id)`; `(creating_device_id, created_at)`; `(last_active_day)`.
**Stored** status, tier, display preferences, tree position, counters, optional e-mail ciphertext. **Not stored** name, nickname, IP, country, user-agent, provider identifiers, recovery key (only the public key derived from it, in `member_keys`), password.
**Closure.** On `closed` the retention job deletes the rows of `member_keys`, `sessions`, `invites` (issued), `opt_ins`, `badge_awards`, `referrals`, and sets every nullable column above to NULL, keeping `id`, `created_at`, `status`, `closed_at` and `row_version`. The row is a tombstone so permanent rows that hold the opaque `mem_` id stay valid and point at nothing personal. Credit left on a closed member's lots moves to the Reserve through `expire` entries (S6.* owns the rule) [A]. [D]

### 5.6.2 `MemberKey` · `member_keys` · `mky_` · `MUT` · `member_bound`

Public keys of a member (S0.6.4). Supports rotation, device linking and the recovery key. [A]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `member_id` | id `mem_` | NN, FK | |
| `purpose` | enum(`key_purpose`) | NN | `auth` signs challenges; `recovery` is derived from the recovery key and used only to recover |
| `algorithm` | text | NN, `CHECK = 'ed25519'` | scheme fixed by S0.6.4; a new scheme is a convention edit |
| `public_key` | bytes | NN, 32 bytes | |
| `status` | enum(`key_status`) | NN, default `active` | |
| `device_id` | id `dev_` | null, FK | the device this auth key belongs to (device linking adds a key per device) |
| `rotated_at`, `not_after` | ts | null | `not_after` = rotation time + `identity.key_rotation_grace_s` for the old key |
| `replaced_by_key_id` | id `mky_` | null, FK | |

**Unique** `public_key`; one active `recovery` key per member (`(member_id) WHERE purpose='recovery' AND status='active'`). **Indexes** `(member_id, status)`; `(device_id)`. **Stored** public keys only. **Not stored** private keys, the recovery key itself, any seed or passphrase.

### 5.6.3 `Device` · `devices` · `dev_` · `MUT` · `short`

A keyed-hash record of a client installation for rate limits, anti-farming and linking. It is a random token the client generated, not a fingerprint. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `device_token_hash` | bytes32 | NN | S5.3.3; set to NULL by purge |
| `hash_key_version` | int | NN | |
| `status` | enum(`device_status`) | NN, default `active` | `blocked` after a farming finding (S10.*) |
| `first_seen_day`, `last_seen_day` | day | NN | |
| `creation_ip_hash`, `ip_hash_key_version`, `creation_ip_hash_expires_at` | bytes32, int, ts | all null or all set | expiry = creation + `retention.ip_hash_ttl_days` |
| `grants_claimed` | int | NN, default 0 | counts toward `grant.max_per_device` (lifetime) |

**Unique** `device_token_hash`. **Indexes** `(creation_ip_hash, created_at)` where not null; `(last_seen_day)`. **Retention.** After `retention.session_days` without use the row is purged: hashes are set to NULL; a row with `grants_claimed > 0` is kept as a tombstone `(id, grants_claimed)` while any non-closed member has it as `creating_device_id` so the lifetime grant limit cannot be reset by waiting [A].
**Stored** keyed hashes, day-granular first and last use, a grant counter. **Not stored** raw IP, user-agent, screen size, fonts, canvas or audio fingerprints, hardware ids, anything beyond the list the threat model (S10.*) admits.

### 5.6.4 `Session` · `sessions` · `ses_` · `MUT` · `short`

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `principal_type` | enum | NN, `member` or `admin` | |
| `member_id` / `admin_user_id` | id | exactly one set, matching `principal_type` | |
| `key_id` / `credential_id` | id `mky_` / `acr_` | the key or passkey that authenticated | |
| `token_hash` | bytes32 | NN | SHA-256 of a 256-bit token; the token is shown once |
| `last_used_at`, `idle_expires_at`, `abs_expires_at` | ts | NN | `session.member_*` / `session.admin_*` TTLs |
| `revoked_at`, `revoked_reason` | ts, text | null | reason is a code, never free text |

**Unique** `token_hash`. **Indexes** `(member_id)`, `(admin_user_id)`, `(abs_expires_at)`. **Retention** `retention.session_days` after expiry or revocation. **Not stored** the token, IP, user-agent, location.

### 5.6.5 `Invite` · `invites` · `inv_` · `MUT` · `member_bound`

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `issuer_member_id` | id `mem_` | NN, FK | issuing needs `invite.min_accepted_cells_to_issue` accepted cells |
| `code_hash` | bytes32 | NN | SHA-256 of a 128-bit code; the code is shown once to the issuer |
| `status` | enum(`invite_status`) | NN, default `issued` | |
| `expires_at` | ts | NN | `created_at + invite.ttl_days` |
| `redeemed_by_member_id`, `redeemed_at` | id, ts | null, both set or both null | |
| `tree_root_member_id`, `tree_depth` | id, int | NN | the new member's position; depth <= `invite.tree_max_depth` |

**Unique** `code_hash`; `redeemed_by_member_id`. **Indexes** `(issuer_member_id, status)` (for `invite.max_active_per_member`); `(tree_root_member_id)` (for `invite.tree_max_members`). **Stored** hash, tree position. **Not stored** the clear code, any note about the invitee, any contact detail.

### 5.6.6 `OptIn` · `opt_ins` · `opt_` · `MUT` · `member_bound`

The volunteer's opt-ins for rule R8, one current row per member. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `member_id` | id `mem_` | NN, FK, unique | |
| `purposes` | arr | NN, subset of `P0..P3` | default `optin.default_purposes` |
| `sensitivities` | arr | NN, subset of `S0`,`S1` | default `optin.default_sensitivities`; `S2` and `S3` are never selectable |
| `licenses` | arr | NN, subset of `L0..L3` | default `optin.default_licenses` |
| `service_requirements` | arr | NN, subset of `M0..M2` | default `optin.default_service_requirements` |
| `allowed_service_ids` | arr of `svc_` | null = every approved service | |
| `topics_included` / `topics_excluded` | arr of `top_` | NN, default empty | sensitive topics are included only on opt-in (`optin.sensitive_topics_default` = false); other topics are excluded only on opt-out |
| `version` | int | NN, starts 1 | the lease stores it (S5.8.2) so a later dispute can show what the volunteer had opted into |

**Indexes** GIN on `purposes`, `sensitivities`, `licenses`, `service_requirements`, `topics_included`. **Not stored** the history of every earlier setting (the `member.optin_changed` event carries a hash only).

### 5.6.7 `TopicCategory` · `topic_categories` · `top_` · `MUT` · `permanent`

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `slug` | text | NN, unique, `^[a-z][a-z0-9_]{1,40}$` | |
| `copy_key` | text | NN | `copy.topic.<slug>`; labels live in copy, not here |
| `is_sensitive` | bool | NN | sensitive categories are opt-in (R8) |
| `status` | enum(`topic_status`) | NN, default `active` | |
| `created_by_admin_id` | id `adm_` | NN, FK | |

Changes are `AdminAction` plus `ChangeLogEntry` (R10: making a category non-sensitive is a loosening). **Not stored** member-level topic statistics.

### 5.6.8 `AdminUser` · `admin_users` · `adm_` · `MUT` · `permanent`

Operator or Reviewer principal, separate from `Member` (S0.8.2). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `roles` | arr | NN, non-empty, subset of `reviewer`,`operator` | |
| `status` | enum(`admin_status`) | NN | `invited`, `active`, `disabled` |
| `label` | text | NN, unique, 2..40 chars | a pseudonymous label such as `founder-1`; not a legal name |
| `invited_by_admin_id` | id `adm_` | null for the bootstrap admin, FK | |
| `disabled_at` | ts | null | |

**Not stored** a password, e-mail, phone or any shared secret: admin authentication is passkey-only (S0.6.4). Rows are never deleted because `AdminAction` rows must stay attributable; the label is the only identifying datum and is pseudonymous. [D]

### 5.6.9 `AdminCredential` · `admin_credentials` · `acr_` · `MUT` · `permanent`

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `admin_user_id` | id `adm_` | NN, FK | |
| `credential_id` | bytes | NN, unique | WebAuthn credential id |
| `public_key` | bytes | NN | COSE key |
| `sign_count` | int64 | NN, default 0 | monotonic check (clone detection) |
| `transports` | arr | null | |
| `label` | text | null, <= 40 chars | |
| `status` | enum(`credential_status`) | NN | |
| `last_used_at`, `revoked_at` | ts | null | |

**Not stored** private keys, biometrics, attestation blobs beyond what S10.* decides to keep.

### 5.6.10 `AdminAction` · `admin_actions` · `act_` · `CHN` · `permanent`

The log of every operator and reviewer action. Named so it does not collide with the sampled `Audit`. It is also the approval record (S5.15). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `seq` | int64 | NN, unique, gap-free | |
| `principal_type` | enum | NN, `admin` or `system` | |
| `admin_user_id` | id `adm_` | null only when `system` | |
| `action` | text | NN, dotted lowercase | for example `template.approve`, `service.record_flag`, `parameter.change`, `ledger.reversal.approve`, `launch.signoff`, `killswitch.engage` |
| `subject_type`, `subject_id` | text, id | NN | polymorphic reference |
| `subject_hash` | hash | null | content hash that was reviewed or approved (binds an approval to exact content) |
| `reason` | text | NN for sensitive actions (`security.two_person_actions`), <= 1000 chars | |
| `approves_action_id` | id `act_` | null, FK | the first action of a two-person pair |
| `payload` | json | NN, <= 16 KiB | non-personal; schema per `action` |
| `request_id` | text | NN | `req_` id |
| `prev_hash`, `entry_hash` | hash | NN | chain over the table, S5.15 |

**Keys** PK `id`; unique `seq`; FKs. **Indexes** `(subject_type, subject_id, seq)`; `(admin_user_id, seq)`; `(action, seq)`. **Not stored** admin IP, session token, user-agent.

## 5.7 Templates, uploads and jobs

### 5.7.1 `Template` · `templates` · `tpl_` · `MUT` · `permanent`

Stable identity of a reviewed prompt pattern; points at its active version.

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `slug` | text | NN, unique, `^[a-z][a-z0-9_]{2,60}$` | |
| `job_type` | enum(`job_type`) | NN | |
| `active_version_id` | id `tpv_` | null, FK (deferred) | must reference a version of this template with `review_status = 'approved'` |
| `created_by_admin_id` | id `adm_` | NN, FK | |

Pausing a template is the kill switch `kill.template.<tpl_id>` (S5.12.3), not a column. **Indexes** `(job_type)`. **Not stored** statistics about outcomes (those are `MetricSnapshot`).

### 5.7.2 `TemplateVersion` · `template_versions` · `tpv_` · `IMS` · `permanent`

Immutable once it enters review. Machine `review_status` (S0.9.5). Content columns are frozen when `template.review_requested` fires; an edit after `changes_requested` creates a new version, never edits a reviewed one. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `template_id`, `version` | id, int | NN; `(template_id, version)` unique; `version` starts at 1 | |
| `review_status` | enum | NN, default `draft` | `draft`, `in_review`, `awaiting_second_review`, `changes_requested`, `approved`, `rejected`, `paused`, `retired` |
| `author_admin_id` | id `adm_` | NN, FK | the second-reviewer rule needs it (FD§5.7 failure mode 10) |
| `prompt_body` | text | NN, <= 20000 chars | with named data slots |
| `slots` | json | NN | slot name, type, max chars, escaping rule |
| `delimiter_spec` | json | NN | the delimiters wrapping data and the instruction to treat it as data (FD§5.5) |
| `output_schema` | json | NN | JSON Schema of the expected paste-back |
| `auto_checks` | json | NN | ordered list of automatic checks (schema, length, language, refusal pattern, tests) |
| `comparator` | json | null | audit comparator; required when the type is audited |
| `envelope` | json | NN | `cell.envelope.*` limits for this template; each <= the global parameter |
| `risk_class` | enum | NN, default `standard` | `high` forces blanket redundancy (`verify.blanket_redundancy_n`) |
| `allowed_purposes`, `allowed_sensitivities`, `allowed_licenses`, `allowed_service_requirements` | arr | NN | the template's own allowlist, intersected with the `PolicyVersion` allowlist |
| `topic_category_id` | id `top_` | null, FK | |
| `card_sentence_key` | text | NN | copy key of the one-line provenance sentence (FD§5.5) |
| `content_hash` | hash | NN from `in_review` | RFC 8785 hash of every content column above |
| `approved_at` | ts | null | the date shown on the card ("reviewed on [date]") |

**Keys** PK; FK `template_id`, `author_admin_id`, `topic_category_id`. **Indexes** `(template_id, review_status)`; `(content_hash)`. **Approvals** are `AdminAction` rows with `action = 'template.approve'`, `subject_id` = this id and `subject_hash = content_hash`; the guard counts distinct `admin_user_id` different from `author_admin_id` against `template.min_reviewers_new` or `template.min_reviewers_edit`. A content change voids earlier approvals because the hash no longer matches. **Stored** the full prompt text (public by design: volunteers can expand it). **Not stored** any claim that the template works; effectiveness is [H] and is measured outside this table.

### 5.7.3 `Glossary` · `glossaries` · `gls_` · `IMS` · `job_bound`

Shared glossary of a translation job (FD§2). One row per job.

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `job_id` | id `job_` | NN, FK, unique | |
| `source_lang`, `target_lang` | text | NN | BCP 47 tags |
| `terms` | json | null after purge | list of `{source, target}`; <= 500 entries, <= 8 KiB total [A] |
| `entry_count` | int | NN | |
| `terms_hash` | hash | NN | |
| `payload_purged_at` | ts | null | `terms` set to NULL `retention.job_payload_days` after the job is terminal |

**Not stored** the requester's identity beyond the job.

### 5.7.4 `Upload` · `uploads` · `upl_` · `IMS` · `job_bound`

A requester's data file before it is split into cells.

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `member_id` | id `mem_` | NN, FK | |
| `job_id` | id `job_` | null until the draft job exists, FK | |
| `status` | enum(`upload_status`) | NN | `received`, `screening`, `accepted`, `rejected`, `split`, `purged` |
| `media_type` | enum(`upload_media_type`) | NN | |
| `byte_size` | int | NN, `<= job.max_upload_bytes` | |
| `content_hash` | hash | NN | |
| `storage_key` | text | null after purge | object store key behind the storage interface (S4.*) |
| `unit_count` | int | null | segments or rows found by the splitter |
| `screening_report` | json | null | counts and offsets of URL, personal-data and instruction-pattern hits; never copies of the matched text |
| `purged_at` | ts | null | |

**Indexes** `(member_id, created_at)`; `(job_id)`. **Not stored** the original file name, the client's path, EXIF or document metadata (stripped at intake).

### 5.7.5 `Job` · `jobs` · `job_` · `MUT` · `job_bound`

A requester's request, or a Commons job. Machine S0.9.2. The declarations, the policy stamp and the quote are written once and never changed after `job.escrow_confirmed`. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `state` | enum | NN, default `draft` | the 15 states of S0.9.2 |
| `closure_reason` | enum | null; set with `job.stop_requested` | `policy_stopped`, `service_revoked`, `template_retired`, `operator_killed`, `overrun_timeout` |
| `is_commons` | bool | NN | true for Commons jobs; the only jobs whose acceptance mints |
| `requester_member_id` | id `mem_` | NN iff `is_commons` = false | |
| `job_type` | enum | NN | |
| `template_version_id` | id `tpv_` | NN, FK | must be `approved` at screening |
| `purpose`, `license`, `sensitivity`, `service_requirement` | enum | NN | the four declarations (FD§5.2) |
| `pinned_service_ids` | arr of `svc_` | NN; non-empty iff `M1` | |
| `topic_category_id` | id `top_` | null, FK | |
| `upload_id`, `glossary_id` | id | null, FK | |
| `input_hash` | hash | NN from `screening` | hash of the upload; system-added metadata (FD§5.2) |
| `size_class`, `deadline_class` | enum | NN, both `standard` | |
| `deadline_at` | ts | null | requester's latest acceptable date |
| `policy_version_id` | id `plv_` | null until `job.policy_passed`, then NN | R9 stamp |
| `primary_cell_count` | int | NN, 1..`admission.max_job_cells` | N of S0.6.1 |
| `v_snapshot_id` | id `mts_` | null | the published v used in the quote |
| `v_ppm`, `lambda_ppm`, `price_per_cell_ucr` | ppm, ppm, ucr | set at quote; `price = 1000000 + v + lambda` (CHECK) | |
| `escrow_ucr` | ucr | `= primary_cell_count * price_per_cell_ucr` (CHECK) | |
| `verification_pool_cells` | int | `floor(primary_cell_count * v_ppm / 1000000)` | S0.6.1; remainder refunded at settlement (`ISS-04`) |
| `quoted_window_s` | int | NN at quote | |
| `quote_expires_at` | ts | NN at quote | `price.quote_ttl_s` |
| `parameter_versions` | json | NN at quote | map of parameter name to version in force (`admission.*`, `price.*`, `credit.*`, `verify.*`) |
| `escrow_id` | id `esc_` | null until `escrow_confirmed` | |
| `reservation_id` | id `rsn_` | null | set when activated from a reservation |
| `submitted_at`, `admitted_at`, `started_at`, `assembled_at`, `settled_at` | ts | null | |
| `requester_rating` | int | null, 1..5 | rating of the outcome (prompt F); no free text, because free text can hold personal data |

**Keys** PK; FKs. **Indexes** `(requester_member_id, state)` (concurrency cap `admission.max_concurrent_jobs_per_member`); `(state, deadline_at)`; `(template_version_id)`; `(policy_version_id)`. **Checks** `is_commons = (requester_member_id IS NULL)`; every declared combination is in the stamped `PolicyVersion.allowlist` (verified by the writer, recorded by `policy_version_id`). **Defense in depth** a trigger refuses `state` to `quoted` or `admitted` unless every service the job could run on is `approved` with a current `TermsCopy` (S5.14.8). **Stored** declarations, quote, hashes. **Not stored** the uploaded content (that is `Upload`, purged), the requester's identity beyond the pseudonymous id, any rating text.

### 5.7.6 `Reservation` · `reservations` · `rsn_` · `MUT` · `job_bound`

Capacity booking for a future date with escrow at booking (FD§4.8). Machine S0.9.8.

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `member_id` | id `mem_` | NN, FK | |
| `state` | enum | NN | `held`, `activated`, `cancelled`, `expired` |
| `target_day` | day | NN | UTC; at most `reservation.max_horizon_days` ahead |
| `cell_count` | int | NN, >= 1 | |
| `job_type` | enum | NN | |
| `price_per_cell_ucr`, `escrow_ucr` | ucr | NN | priced at booking |
| `escrow_id` | id `esc_` | NN, FK, unique | |
| `activated_job_id` | id `job_` | null, FK | |
| `free_cancel_until` | ts | NN | `target_day` minus `reservation.free_cancel_notice_s` |
| `expires_at` | ts | NN | |

**Indexes** `(member_id, state)` (`reservation.max_active_per_member`); `(target_day, state)` (`reservation.capacity_share_cap`). Cancellation inside the notice window is a ledger fee policy owned by S6.*; this table stores only the state.

### 5.7.7 `WaitlistEntry` · `waitlist_entries` · `wlt_` · `MUT` · `job_bound`

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `job_id` | id `job_` | NN, FK, unique | |
| `member_id` | id `mem_` | NN, FK | |
| `state` | enum(`waitlist_state`) | NN | `waiting`, `released`, `expired`, `cancelled` |
| `position_key` | int64 | NN, from a sequence | FIFO order within a deadline class (FD§4.8) |
| `requested_window_s` | int | NN | |
| `expires_at` | ts | NN | `admission.waitlist_ttl_days` |

**Indexes** `(state, position_key)`; `(member_id, state)` (`admission.waitlist_max_per_member`).
