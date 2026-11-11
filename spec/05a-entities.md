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

## 5.8 Cells, leases, submissions and verification

### 5.8.1 `Cell` · `cells` · `cel_` · `MUT` · `job_bound`

One prompt-and-response unit inside the envelope; the unit of credit. The row persists across attempts and carries `attempt` (S0.9.3). States are the 12 of S0.9.3. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `job_id` | id `job_` | NN, FK | |
| `cell_kind` | enum | NN | `primary`, `gold`, `audit`, `third`, `review`, `rework`. **Never sent to a volunteer-facing API**: a gold cell must look like any other cell (FD§4.4) |
| `ordinal` | int | NN iff `primary`, >= 1 | position in the job; unique per job among primary cells |
| `state` | enum | NN, default `queued` | |
| `attempt` | int | NN, default 1, `<= cell.max_attempts` | |
| `template_version_id` | id `tpv_` | NN, FK | copied from the job so a gold or audit cell can use another version of the same template |
| `purpose`, `license`, `sensitivity`, `service_requirement` | enum | NN | copied from the job for the R8 query; never changed |
| `pinned_service_ids` | arr | NN | copied |
| `topic_category_id` | id `top_` | null | |
| `input_payload` | text | null after purge | the slot data of this cell |
| `input_hash`, `rendered_prompt_hash` | hash | NN | |
| `rendered_prompt` | text | null after purge | the exact text a volunteer sees; stored so the card can be re-shown and audited |
| `input_chars` | int | NN, `<= cell.envelope.max_input_chars` | |
| `gold_cell_id` | id `gld_` | NN iff `gold` | |
| `audit_id` | id `aud_` | NN iff `audit` or `third` | |
| `subject_cell_id` | id `cel_` | NN iff `rework`; the cell that was overturned | |
| `subject_submission_id` | id `sub_` | NN iff `review`; the output being reviewed | |
| `priority_key` | int64 | NN | queue order: first-come within a deadline class, then `ordinal` (FD§4.8) |
| `queued_at` | ts | NN | reset at each requeue |
| `earliest_lease_at` | ts | null | a requeued cell may wait before it is shown again [A] |
| `current_lease_id` | id `lse_` | NN iff `leased` | |
| `accepted_submission_id`, `accepted_at` | id, ts | NN iff `accepted` or `overturned` | |
| `accept_policy_version_id` | id `plv_` | null until acceptance | R9 re-check result (policy in force at acceptance) |
| `last_reject_code` | text | null | a `reject.*` code of S0.8.4 |
| `credit_txn_id` | id `txn_` | null, unique | the `payout` (member job) or `mint` (Commons) transaction; set once, which makes double payment structurally impossible |
| `payload_purged_at` | ts | null | |

**Keys** PK; FKs to `jobs`, `template_versions`, `gold_cells`, `audits`, `cells` (self), `submissions`, `leases`, `ledger_transactions`. **Unique** `(job_id, ordinal) WHERE cell_kind = 'primary'`; `credit_txn_id`; `accepted_submission_id`. **Indexes** the queue `(priority_key) WHERE state = 'queued' AND (earliest_lease_at IS NULL OR earliest_lease_at <= now())`; `(job_id, state)`; `(subject_cell_id)`; GIN on `pinned_service_ids`. **Stored** envelope-bounded inputs and the rendered prompt until purge, hashes forever. **Not stored** the volunteer's identity on the cell (it is on the `Lease` and `Submission`), the cell's gold status in any column a volunteer API selects.

### 5.8.2 `Lease` · `leases` · `lse_` · `MUT` · `job_bound`

Time-boxed hold of a cell by one member, bound to a nonce (FD§3.4, S0.9.3). Every lease belongs to one attempt of one cell. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `cell_id` | id `cel_` | NN, FK | |
| `member_id` | id `mem_` | NN, FK | |
| `device_id` | id `dev_` | null, FK | the device of the authenticating key; used for rate limits |
| `attempt` | int | NN | equals `cells.attempt` at issue |
| `state` | enum | NN, default `active` | `active`, `submitted`, `expired`, `released`, `revoked` |
| `nonce_hash` | bytes32 | NN | SHA-256 of a `lease.nonce_bytes` = 16 byte nonce; the nonce is returned once and never stored |
| `issued_at`, `expires_at` | ts | NN, `expires_at > issued_at` | both server clock (S0.6.2) |
| `timeout_s_applied` | int | NN | `lease.timeout_s` in force; extensions add `lease.extend_s` up to `lease.max_extensions` |
| `extensions_used` | int | NN, default 0 | |
| `optin_version` | int | NN | `opt_ins.version` at issue (R8 evidence) |
| `policy_version_id` | id `plv_` | NN, FK | policy in force at issue |
| `ended_at`, `end_reason` | ts, text | null | reason is one of `submitted`, `expired`, `declined`, `released`, `revoked_policy`, `revoked_service`, `revoked_job_cancelled`, `revoked_integrity` |

**Unique** `(cell_id, attempt)`; **`(cell_id) WHERE state = 'active'`**, the race guard: at most one active lease per cell, enforced by the database, not only by application code. **Indexes** `(expires_at) WHERE state = 'active'` (reaper, `lease.reap_interval_s`); `(member_id) WHERE state = 'active'` (`lease.max_active_per_member`, checked under a row lock on the member). **Not stored** the nonce, IP, the service the volunteer opened.

### 5.8.3 `Submission` · `submissions` · `sub_` · `IMS` · `job_bound`

One pasted-back result for one lease. Content columns are frozen at insert; only the state columns change. A replay with the same lease and nonce returns the stored outcome and inserts nothing (S0.9.3). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `lease_id` | id `lse_` | NN, FK, **unique** | one submission per lease |
| `cell_id`, `member_id` | id | NN, FK | |
| `volunteer_handle`, `handle_key_version` | text, int | NN | `vol_` + 32 hex (S5.3.2); never in a requester surface |
| `state` | enum | NN, default `received` | `received`, `schema_failed`, `checks_failed`, `checks_passed`, `quarantined`, `accepted`, `rejected` |
| `output_text` | text | null after purge | what the volunteer pasted; stored as data, escaped on every display, never executed (FD§10) |
| `output_hash` | hash | NN | SHA-256 of the raw bytes |
| `normalized_output_hash` | hash | NN | hash of whitespace- and case-normalized text; exact duplicate detection |
| `output_simhash` | int64 | NN | locality-sensitive fingerprint for `verify.duplicate_similarity_threshold` [A] |
| `output_chars`, `output_bytes` | int | NN, `output_bytes <= cell.envelope.max_submission_bytes` | |
| `reported_service_id` | id `svc_` | null, FK | attested by the volunteer, not proven (FD§5.6) |
| `reported_model_label` | text | null, <= 80 chars | free text, attested, escaped on display |
| `submitted_at` | ts | NN | server clock |
| `elapsed_s` | int | NN | `submitted_at - lease.issued_at`, computed server-side; basis for `verify.timing_min_s` |
| `reject_code` | text | null | `reject.*` |
| `quarantine_reason` | enum | null; NN iff `quarantined` | `output_url`, `code_to_run`, `action_request`, `other_flag` |
| `checks_report` | json | null | per-check results; no copy of the output |
| `decided_at` | ts | null | |
| `accept_policy_version_id` | id `plv_` | null | the R9 re-check |

**Unique** `lease_id`. **Indexes** `(cell_id)`; `(member_id, submitted_at)`; `(normalized_output_hash)`; `(output_simhash)`; `(state) WHERE state IN ('received','checks_passed','quarantined')`. **Frozen** every column except `state`, `reject_code`, `quarantine_reason`, `decided_at`, `accept_policy_version_id` and `output_text` (set NULL by purge). **Stored** the paste-back, hashes, attested labels. **Not stored** the chat URL, any page content beyond the pasted text, clipboard history, client timing claims, raw IP.

### 5.8.4 `VerificationRecord` · `verification_records` · `vrf_` · `IMS` · `job_bound`

Outcome of one verification method on one submission. An outcome moves once from `pending` to a final value; after that the row is immutable and a later finding is a new row with `supersedes_id`. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `submission_id`, `cell_id` | id | NN, FK | |
| `method` | enum | NN | `auto_check`, `gold`, `audit_second`, `audit_third`, `human_review`, `blanket_redundancy` |
| `outcome` | enum | NN, default `pending` | `pending`, `pass`, `fail`, `inconclusive` |
| `check_ref` | text | null | check id inside the template (`auto_check`) or comparator id |
| `gold_cell_id`, `audit_id` | id | null, FK | set for `gold` and `audit_*` |
| `related_submission_id` | id `sub_` | null | the other execution compared against |
| `reviewer_member_id` | id `mem_` | null | set for `human_review`; internal only |
| `score_ppm` | ppm | null | similarity or rating |
| `details` | json | null after purge | comparator output; <= 8 KiB |
| `supersedes_id` | id `vrf_` | null, FK | |
| `decided_at` | ts | null | set with the final outcome |

**Indexes** `(submission_id)`; `(cell_id, method)`; `(gold_cell_id) WHERE gold_cell_id IS NOT NULL`; `(outcome) WHERE outcome = 'pending'`. These rows feed the donor reliability estimate and the false-accept and false-reject estimates (S8.*); they stay after payload purge with `details` nulled.

### 5.8.5 `GoldCell` · `gold_cells` · `gld_` · `IMS` · `permanent`

Known-answer cells of the hidden library. Answers are access-restricted. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `template_id` | id `tpl_` | NN, FK | |
| `status` | enum(`gold_status`) | NN, default `active` | `compromised` when an answer is believed leaked; the cell is no longer served |
| `input_payload`, `input_hash` | text, hash | NN | |
| `answer_payload`, `answer_hash` | json, hash | NN; **column grant to `verifier_svc` only** | the expected answer or acceptance spec |
| `purpose`, `license`, `sensitivity`, `service_requirement` | enum | NN; `sensitivity = 'S0'` (CHECK) | gold cells must pass R8 like any cell |
| `topic_category_id` | id `top_` | null | |
| `served_count` | int | NN, default 0 | `DER` |
| `last_served_at` | ts | null | |
| `authored_by_admin_id` | id `adm_` | NN, FK | |

**Indexes** `(template_id, status)`. **Not stored** which donors saw it beyond the `Cell` rows (internal); never exposed through any member or requester API.

### 5.8.6 `Audit` · `audits` · `aud_` · `MUT` · `job_bound`

Sampled re-execution of a cell, comparator result, third execution. Machine S0.9.8.

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `primary_cell_id`, `primary_submission_id` | id | NN, FK | |
| `trigger` | enum(`audit_trigger`) | NN | |
| `sampling_rate_ppm_applied` | ppm | null | `s` applied when sampled; needed to estimate false accepts without bias |
| `state` | enum | NN | `pending`, `second_executed`, `matched`, `mismatched`, `third_pending`, `resolved`, `cancelled` |
| `second_cell_id`, `third_cell_id` | id `cel_` | null, FK | executions by donors different from the primary donor and from each other (enforced when leasing, S9.*) |
| `second_submission_id`, `third_submission_id` | id `sub_` | null, FK | |
| `comparator_ref` | text | NN | the template comparator id |
| `similarity_ppm` | ppm | null | |
| `verdict` | enum(`audit_verdict`) | null; NN when `resolved` | |
| `resolved_at` | ts | null | |

**Indexes** `(state)`; `(primary_cell_id)`.

### 5.8.7 `Deliverable` · `deliverables` · `dlv_` · `IMS` · `job_bound`

The assembled output of a job.

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `job_id`, `version` | id, int | NN; `(job_id, version)` unique | an overturned cell after assembly produces version + 1 with a new manifest |
| `state` | enum(`deliverable_state`) | NN | `assembling`, `ready`, `purged` |
| `format` | enum(`deliverable_format`) | NN | |
| `content_hash`, `byte_size` | hash, int | NN once `ready` | |
| `storage_key` | text | null after purge | |
| `cell_count` | int | NN | accepted primary cells included |
| `supersedes_id` | id `dlv_` | null, FK | |
| `payload_purged_at` | ts | null | `retention.job_payload_days` after the job is terminal |

### 5.8.8 `Manifest` · `manifests` · `mfs_` · `IMM` · `job_bound` (rows stay)

Provenance manifest of a deliverable (FD§5.6). Two renderings of one record: the internal manifest (with volunteer handles) and the requester export (without). Only the internal one is stored in full; the export is derived and its hash is stored. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `deliverable_id` | id `dlv_` | NN, FK, unique | |
| `job_id` | id `job_` | NN, FK | |
| `schema_version` | int | NN | |
| `manifest_json` | json | NN, <= 1 MiB | internal; shape below |
| `manifest_hash` | hash | NN | |
| `export_hash` | hash | NN | hash of the redacted rendering |
| `no_training_flag` | bool | NN | contractual, not technically enforced (FD§5.6) |
| `downstream_use_uncontrolled` | bool | NN | true for `P1` |

```json
{ "schema_version": 1, "job_id": "job_...", "template": { "id": "tpl_...", "version_id": "tpv_...", "content_hash": "sha256:..." },
  "declared": { "purpose": "P1", "license": "L2", "sensitivity": "S0", "service_requirement": "M0" },
  "policy": { "policy_version_id": "plv_...", "version_hash": "sha256:..." },
  "cells": [ { "cell_id": "cel_...", "input_hash": "sha256:...", "output_hash": "sha256:...",
               "service_reported": "svc_...", "model_reported": "text, attested, not proven",
               "verification": [ { "method": "auto_check", "outcome": "pass" } ],
               "accepted_at": "2026-11-12T09:30:00Z",
               "volunteer_handle": "vol_..." } ] }
```

The export removes `volunteer_handle` from every cell and states "declared", never "guaranteed". **Not stored** any input or output text (hashes only), any requester identifier other than `job_id`.

## 5.9 Credit and ledger entities

The ledger is one double-entry book, `ledger_id = 'main'` [A]. Amounts are integer `ucr` (S0.6.1). Business meaning of postings, the invariant list `INV-L<nn>` and the check schedule belong to S6.*; this section fixes the stored shape and the structural guarantees the database itself enforces. [D]

### 5.9.1 `LedgerAccount` · `ledger_accounts` · `lac_` · `DER` · `permanent`

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `account_type` | enum(`ledger_account_type`) | NN | `member`, `escrow`, `reserve`, `issuance`, `retired` |
| `member_id` | id `mem_` | NN iff `member`, unique | |
| `escrow_id` | id `esc_` | NN iff `escrow`, unique, deferred FK | |
| `balance_ucr` | ucr | NN, default 0 | cache, updated only by `ledger_post()`; sign rule below |
| `last_entry_seq` | int64 | NN, default 0 | the highest `seq` that touched this account |

**Sign rule (CHECK)** `member`, `escrow`, `reserve`, `retired`: `balance_ucr >= 0`; `issuance`: `balance_ucr <= 0`. This is `ledger.allow_negative_balance` = false enforced by the database. **Singletons** a unique index allows exactly one `reserve`, one `issuance` and one `retired` account. **Indexes** `(account_type)`. **Public view.** The public ledger (S12.*) shows `vol_` handles computed on read from `member_id`; no `mem_` id and no handle is stored here. **Not stored** any personal datum; the table is the same shape for a member and for a Reserve.

### 5.9.2 `LedgerEntry` · `ledger_entries` · `lge_` · `CHN` · `permanent`

One balanced pair of legs, append-only, hash-chained (S0.8.5). Never updated, never deleted. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `ledger_id` | text | NN, `CHECK = 'main'` | |
| `seq` | int64 | NN; unique with `ledger_id`; gap-free | the order of the ledger (S0.6.2) |
| `txn_id` | id `txn_` | NN, FK | |
| `entry_type` | enum(`ledger_entry_type`) | NN | `mint`, `grant`, `escrow_hold`, `transfer`, `escrow_release`, `levy`, `refund`, `expire`, `retire`, `reserve_donation`, `reversal` |
| `debit_account_id`, `credit_account_id` | id `lac_` | NN, FK, `debit <> credit` | the from and to accounts of S0.8.5 |
| `amount_ucr` | ucr | NN, `> 0` | |
| `lot_id` | id `lot_` | null, FK | the lot created, consumed or restored |
| `lot_effect` | enum(`lot_effect`) | NN | `create`, `consume`, `restore`, `none`, per the table in S0.8.5 |
| `restores_entry_id` | id `lge_` | null, FK | for a `refund` that restores consumed lots: the `escrow_hold` entry it undoes in part |
| `reverses_entry_id` | id `lge_` | null, FK, unique | for a `reversal` |
| `job_id`, `cell_id` | id | null | references for explorers; the transaction is authoritative |
| `prev_hash`, `entry_hash` | hash | NN | `entry_hash = SHA-256(prev_hash \|\| canonical(entry))` (S0.6.4); genesis `prev_hash` is `sha256:` followed by 64 zeros |

`canonical(entry)` is the RFC 8785 serialization of every column except `entry_hash` and `created_at`'s sub-second digits are kept (full `ts`). **Entry shape.** Credit consumed from several lots is posted as several entries in one transaction, one per lot, so each entry stays a single balanced pair with one lot. **Direction rule (trigger)** `(entry_type, debit account type, credit account type, lot_effect)` must appear in the reference table `ledger_entry_type_rules`, seeded from S0.8.5 by a migration (constants, not a domain entity): for example `mint` is `issuance` to `member` with `create`; `levy` is `escrow` to `reserve` with `none`. **Indexes** `(debit_account_id, seq)`; `(credit_account_id, seq)`; `(txn_id)`; `(job_id) WHERE job_id IS NOT NULL`; `(entry_type, seq)`. **Not stored** a member identity (accounts carry opaque ids), a memo field, any free text.

### 5.9.3 `LedgerTransaction` · `ledger_transactions` · `txn_` · `IMM` · `permanent`

Atomic group of entries with one `txn_kind` (S0.8.5). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `txn_kind` | enum(`ledger_txn_kind`) | NN | `mint`, `grant`, `hold`, `payout`, `settle`, `cancel`, `reservation_activate`, `expire`, `retire`, `reserve_donation`, `reversal` |
| `natural_key` | text | NN, **unique** | the business idempotency key, for example `payout:<cell_id>`, `hold:<job_id>`, `settle:<job_id>`, `grant:starter:<member_id>`, `expire:<lot_id>`; a second post with the same key is a no-op that returns the first result |
| `member_id`, `job_id`, `cell_id` | id | null | |
| `reversal_of_txn_id` | id `txn_` | null, FK, unique | |
| `entry_count`, `total_ucr` | int, ucr | NN | checked against the entries at commit |
| `actor_type`, `actor_ref` | enum, text | NN | `principal_type` and an opaque id |
| `approval_action_ids` | arr of `act_` | NN, length 2 iff `txn_kind = 'reversal'` | two distinct admins (`ledger.reversal_min_approvers`) |
| `parameter_versions` | json | NN | versions in force (`credit.*`, `price.*`, `mint.*`) |

**Indexes** `(txn_kind, created_at)`; `(cell_id)`; `(job_id)`.

### 5.9.4 `CreditLot` · `credit_lots` · `lot_` · `DER` · `permanent`

A dated, expiring portion of a member's credit; enables oldest-first spending (FD§4.5). Rebuildable from the entries. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `member_id` | id `mem_` | NN, FK | |
| `origin_entry_id` | id `lge_` | NN, FK, unique | the `mint`, `grant`, `transfer` or `refund` entry that created it |
| `original_ucr`, `remaining_ucr` | ucr | NN, `0 <= remaining <= original` | `remaining` is the cache |
| `earned_at` | ts | NN | |
| `expires_at` | ts | NN | `earned_at + lifetime * 86400 s` using the parameter version at `earned_at` (S0.6.2); a restored lot keeps its original value (`ISS-07`) |
| `lifetime_days_applied` | int | NN | `credit.lifetime_days`, `credit.lifetime_days_accelerated` or `grant.starter_lifetime_days` |
| `expiry_arm` | text | null | the experiment arm that chose the lifetime (S5.13.1) |
| `is_starter` | bool | NN | `grant` entries with the starter lifetime |

**Indexes** `(member_id, expires_at) WHERE remaining_ucr > 0` (oldest-first spending and the expiry sweep, `credit.expiry_sweep_interval_s`); `(expires_at) WHERE remaining_ucr > 0`. **Invariant** per member, `sum(remaining_ucr) = member account balance_ucr`.

### 5.9.5 `Escrow` · `escrows` · `esc_` · `MUT` · `permanent`

Per job or reservation hold, bound to one `escrow` account. Machine S0.9.8 (`open`, `settling`, `closed`). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `job_id` / `reservation_id` | id | exactly one set (CHECK) | a reservation escrow moves into the job escrow by `escrow_release` at activation |
| `owner_member_id` | id `mem_` | NN, FK | |
| `ledger_account_id` | id `lac_` | NN, FK, unique | |
| `state` | enum | NN, default `open` | |
| `escrow_ucr` | ucr | NN, `> 0` | total held at admission |
| `planned_primary_ucr`, `planned_pool_ucr`, `planned_levy_ucr` | ucr | NN; **sum = `escrow_ucr`** (CHECK) | `N * 1000000`, `N * v_ppm`, `N * lambda_ppm` (S0.6.1) |
| `paid_ucr`, `levy_ucr`, `refunded_ucr`, `released_ucr` | ucr | NN, default 0 | `DER` running totals of postings out of this escrow |
| `closing_txn_id` | id `txn_` | null; NN when `closed` | the `settle` or `cancel` transaction |
| `closed_at` | ts | null | |

**Checks** `state = 'closed'` implies the account balance is exactly 0 and `paid + levy + refunded + released = escrow_ucr`. **Unique** `job_id`; `reservation_id`. **Indexes** `(owner_member_id, state)`; `(state)`.

### 5.9.6 `Reserve` · `reserves` · `rsv_` · `MUT` · `permanent`

Singleton: the public Commons Reserve; holds the ceiling state (FD§4.2, FD§4.6). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `ledger_account_id` | id `lac_` | NN, FK, unique | the `reserve` account |
| `ceiling_ucr_applied` | ucr | NN | `reserve.ceiling_credits` in force at the last retirement check |
| `last_retire_check_at`, `last_retire_txn_id` | ts, id | null | |
| `grants_paused` | bool | NN | true while the balance is at or below `grant.reserve_floor_credits` (FD§4.6: grants pause, never print) |
| `grants_paused_since` | ts | null | |
| `cum_levy_in_ucr`, `cum_expired_in_ucr`, `cum_grants_out_ucr`, `cum_retired_ucr`, `cum_donated_in_ucr` | ucr | NN, default 0 | `DER`, checked by the invariants |

A unique index on `((true))` keeps the table to one row. Retirement amounts are public (`ledger.entry_committed`).
