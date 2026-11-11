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
| `Deliverable` | S5.8.7 | `IMS` | `job_bound` | a new version row (`version` + 1, `supersedes_id`) with a new manifest |
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

`canonical(entry)` is the RFC 8785 serialization of every column except `entry_hash`; `created_at` is included at microsecond precision. **Entry shape.** Credit consumed from several lots is posted as several entries in one transaction, one per lot, so each entry stays a single balanced pair with one lot. **Direction rule (trigger)** `(entry_type, debit account type, credit account type, lot_effect)` must appear in the reference table `ledger_entry_type_rules`, seeded from S0.8.5 by a migration (constants, not a domain entity): for example `mint` is `issuance` to `member` with `create`; `levy` is `escrow` to `reserve` with `none`. **Indexes** `(debit_account_id, seq)`; `(credit_account_id, seq)`; `(txn_id)`; `(job_id) WHERE job_id IS NOT NULL`; `(entry_type, seq)`. **Not stored** a member identity (accounts carry opaque ids), a memo field, any free text.

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

## 5.10 Policy and Service Registry entities

### 5.10.1 `Policy` · `policies` · `pol_` · `MUT` · `permanent`

Named policy profile (FD§5.4 default profile). Phase 1 uses two active profiles (`P0`/`P1` x `S0`/`S1` x `M0`/`M1`, FD§5.7 failure mode 5) as allowlist entries of one version, not as separate rows. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `slug` | text | NN, unique | `default_profile` is the first row |
| `description_key` | text | NN | copy key |
| `active_version_id` | id `plv_` | null, FK (deferred) | the version stamped on new jobs; must belong to this policy |

### 5.10.2 `PolicyVersion` · `policy_versions` · `plv_` · `IMM` · `permanent`

Immutable rule set plus allowlist; stamped on jobs at admission and re-checked at acceptance (R9). Rules are data (prompt D). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `policy_id`, `version` | id, int | NN; unique pair; version >= 1 | |
| `allowlist` | json | NN | array of permitted `{purpose, license, sensitivity, service_requirement}` tuples; anything not listed is rejected (FD§5.1) |
| `allowlist_hash`, `rules_hash`, `version_hash` | hash | NN | `version_hash = SHA-256(rules_hash \|\| allowlist_hash)`; the value shown in provenance |
| `change_class` | enum(`change_class`) | NN | relative to the superseded version: `tighten`, `loosen`, `neutral` |
| `changelog_entry_id` | id `chg_` | **NN when `change_class = 'loosen'`** (CHECK) | R10; tightening may publish its entry afterwards |
| `supersedes_id` | id `plv_` | null, FK | |
| `effective_from` | ts | NN | `>= created_at + policy.loosen_min_notice_days` for `loosen`; `created_at` for `tighten` |
| `created_by_admin_id`, `approval_action_ids` | id, arr | NN | |

**Indexes** `(policy_id, version)`. **Not stored** edits: a rule change is a new version with all its `Rule` rows.

### 5.10.3 `Rule` · `rules` · `rul_` · `IMM` · `permanent`

One row per policy rule `R1`..`R10` inside a `PolicyVersion` (S0.8.4).

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `policy_version_id` | id `plv_` | NN, FK | |
| `policy_rule_id` | enum | NN | `R1`..`R10` |
| `ordinal` | int | NN | evaluation order; the first failing rule rejects (FD§5.4) |
| `slug` | text | NN | `metadata_missing_or_inconsistent`, ... as in S0.8.4 |
| `evaluator` | text | NN | a name from the fixed evaluator registry of S7.* (for example `meta_complete`, `sensitivity_max`, `purpose_flag_gate`); no code is stored |
| `params` | json | NN | for example `{"purpose":"P2","requires_flag":"commercial_use_of_output"}` |
| `reason_code` | text | NN | `policy.<policy_rule_id>.<slug>` |
| `enabled` | bool | NN, default true | rows with `enabled = false` are recorded but skipped; turning one off is a `loosen` |

**Unique** `(policy_version_id, policy_rule_id)`; `(policy_version_id, ordinal)`.

### 5.10.4 `ServiceRegistryEntry` · `service_registry_entries` · `svc_` · `MUT` · `permanent`

A service with review state, adapter capabilities and dated flags. Every row starts `unreviewed`, which counts as `no`. No provider name, URL or limit is a constant of the system. [D][V]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `slug` | text | NN, unique | reviewer-entered label |
| `display_name` | text | NN, <= 80 chars | |
| `service_kind` | enum(`service_kind`) | NN | `general_chat`, `open_weight_hosted`, `open_weight_local` |
| `review_status` | enum | NN, default `unreviewed` | the 7 states of S0.9.6; only `approved` allows new jobs |
| `suspension_cause` | enum | null; NN when `suspended` | `kill_switch` or `review_lapsed`; `service.resumed` is allowed only for `kill_switch` |
| `current_terms_copy_id` | id `tcp_` | NN when `approved` | |
| `reviewed_at` | ts | null | |
| `review_due_at` | ts | null | `reviewed_at + service.review_max_age_days * 86400 s` |
| `adapter_supports_prefill` | bool | NN, default false | |
| `adapter_prefill_url_template` | text | NN when supports prefill; must contain `{prompt}` (CHECK) | reviewer-entered [V] |
| `adapter_max_url_chars` | int | NN when supports prefill | reviewer-entered [V] |
| `adapter_copy_only` | bool | NN, default true | true unless prefill is supported and `prefilled_link_use` is `yes`; a guard keeps it consistent with the flags |
| `adapter_clean_chat_hint_key` | text | null | copy key |
| `open_weight_license_ref` | text | NN when `service_kind` is `open_weight_*` and status `approved` | pointer to the `TermsCopy` holding the checked model license (`M2`) |

**Keys** FK `current_terms_copy_id` (deferred). **Indexes** `(review_status)`; `(review_due_at) WHERE review_status = 'approved'`. **Approval guard (trigger, S5.14.8)** a row may enter `approved` only if the effective `third_party_task_use` and `prohibited_content_compatible` answers are `yes`, `current_terms_copy_id` is set and at least `service.min_approvers` distinct admins recorded `service.approve` for that `TermsCopy` hash. **Not stored** an account, key, cookie, login or any credential of any provider or volunteer; no scraped page; no pricing or quota number except as a reviewer's dated flag note.

### 5.10.5 `TermsCopy` · `terms_copies` · `tcp_` · `IMM` · `permanent`

Saved copy of a document: bytes, hash, source reference, capture date (FD§5.3). A reviewer supplies it; the platform does not crawl providers. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `service_id` | id `svc_` | NN, FK | |
| `document_kind` | enum(`document_kind`) | NN | `terms`, `usage_policy`, `written_permission` (`info.written_permission`) |
| `media_type` | enum(`terms_media_type`) | NN | |
| `content_hash` | hash | NN | SHA-256 of the stored bytes |
| `byte_size` | int | NN, `<= service.terms_copy_max_bytes` | |
| `storage_key` | text | NN | content-addressed object key `terms/<hex>` behind the storage interface; the bytes are verified against `content_hash` on every read |
| `source_ref` | text | NN, <= 500 chars | where the reviewer obtained it (a URL or a document title); recorded as text, never fetched by the system |
| `provider_version_label` | text | null | a version or date the provider states, if any |
| `captured_on` | day | NN | capture date entered by the reviewer; `created_at` is the server time |
| `captured_by_admin_id` | id `adm_` | NN, FK | |
| `language` | text | null | BCP 47 |
| `supersedes_id` | id `tcp_` | null, FK | |

**Unique** `(service_id, content_hash)`. **Indexes** `(service_id, document_kind, captured_on DESC)`. A copy is never edited or deleted; a changed document is a new copy that supersedes. **Not stored** private correspondence beyond a reviewer-uploaded `written_permission` document.

### 5.10.6 `FlagAnswer` · `flag_answers` · `fla_` · `IMM` · `permanent`

One dated yes / no / unknown answer for one flag of one entry (S0.8.3). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `service_id` | id `svc_` | NN, FK | |
| `flag_key` | enum | NN | the 13 keys of S0.8.3 (9 gate keys, 4 `info.*` keys) |
| `region` | text | NN iff `flag_key = 'regional_availability'`; otherwise null or an ISO 3166-1 alpha-2 code | one answer per region |
| `answer` | enum(`flag_answer`) | NN | `yes`, `no`, `unknown`; **`unknown` is evaluated as `no` everywhere** |
| `terms_copy_id` | id `tcp_` | NN unless `answer = 'unknown'` (CHECK) | the copy the answer was read from |
| `evidence_note` | text | null, <= 2000 chars | clause reference, for example a section number; no legal conclusion |
| `answered_on` | day | NN | reviewer-dated |
| `reviewer_admin_id` | id `adm_` | NN, FK | |
| `supersedes_id` | id `fla_` | null, FK | |

The **effective answer** for `(service, flag_key, region)` is the row with the latest `(answered_on, created_at)`; if none exists it is `unknown`, so evaluated `no`. The view `effective_flag_answers` implements this and is what every guard reads. **Indexes** `(service_id, flag_key, region, answered_on DESC)`. A flag answer is never edited; a changed reading is a new row, and a change that moves a gate flag from `yes` to `no` or `unknown` is a tightening that takes effect at once (R10).

## 5.11 Moderation and community entities

### 5.11.1 `Report` · `reports` · `rpt_` · `MUT` · `moderation`

Abuse or content report from a volunteer or requester. Machine S0.9.8 (`open`, `triaged`, `actioned`, `dismissed`). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `reporter_member_id` | id `mem_` | null after retention | needed for `report.max_per_member_per_day` and to prevent report abuse |
| `subject_type`, `subject_id` | enum(`report_subject_type`), id | NN | |
| `report_kind` | enum(`report_kind`) | NN | |
| `evidence_cell_id` | id `cel_` | null, FK | |
| `reporter_text` | text | null, <= 1000 chars; null after retention | escaped on display; may hold personal data, hence the short life |
| `state` | enum | NN, default `open` | |
| `triaged_by_admin_id` | id `adm_` | null, FK | |
| `outcome` | enum(`report_outcome`) | null; NN when `actioned` or `dismissed` | |
| `resulting_action_id` | id `act_` | null, FK | |
| `resolved_at` | ts | null | |

**Indexes** `(state, created_at)`; `(subject_type, subject_id)`; `(reporter_member_id, created_at)`. **Retention** `retention.moderation_days` after `resolved_at`: counts are added to a `MetricSnapshot`, then `reporter_member_id` and `reporter_text` are nulled and the row is deleted by `retention_svc`. **Not stored** the reporter's identity in any public surface.

### 5.11.2 `Appeal` · `appeals` · `apl_` · `MUT` · `moderation`

Challenge to a rejection, ban or report outcome. Machine S0.9.7. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `appeal_kind` | enum | NN | `cell_rejection`, `member_suspension`, `member_ban`, `job_rejection`, `template_rejection`, `report_outcome` |
| `appellant_member_id` | id `mem_` | NN, FK | |
| `subject_type`, `subject_id` | enum(`appeal_subject_type`), id | NN | |
| `decision_action_id` | id `act_` | null, FK | the decision under appeal when it was an admin action |
| `decision_event_ref` | text | null | an opaque event id for automatic decisions (for example a `reject.*` outcome) |
| `decision_at` | ts | NN | `filed` is allowed only within `appeal.window_days` of it (API error otherwise) |
| `state` | enum | NN | `filed`, `assigned`, `in_review`, `awaiting_second_review`, `upheld`, `overturned`, `withdrawn` |
| `statement` | text | null after retention, <= 2000 chars | |
| `original_decider_admin_id` | id `adm_` | null | the assigned reviewer must differ (S0.9.7) |
| `assigned_admin_id`, `second_reviewer_admin_id` | id `adm_` | null, FK | bans and template rejections need `appeal.ban_min_reviewers` |
| `resulting_action_id` | id `act_` | null, FK | the reversing action, for example `cell.overturned` or `member.reinstated` |
| `resolved_at` | ts | null | |

**Indexes** `(state, created_at)`; `(appellant_member_id)`; `(subject_type, subject_id)`. `appeal.max_per_decision` is enforced by counting rows with the same `(decision_action_id | decision_event_ref)` inside the filing transaction. A decision is final once `upheld`.

### 5.11.3 `Team` · `teams` · `tem_` · `MUT` · `member_bound`

Self-created, opt-in group (FD§6.1 rank 5). Membership is `members.team_id`. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `name` | text | NN, 2..40 chars | moderated; a team name is public if the team is public |
| `owner_member_id` | id `mem_` | NN, FK | needs `team.create_min_tier` |
| `status` | enum(`team_status`) | NN | |
| `join_code_hash` | bytes32 | NN | joining by private code only; no discovery of members |
| `is_public` | bool | NN, default false | shown only when the member count is at least `team.min_public_members` |
| `member_count` | int | NN, `<= team.max_members` | `DER` |

**Not stored** member lists in this row, member locations, affiliations or any inferred grouping (city, university). Team scores are computed from verified cells and published as aggregates subject to `analytics.min_cohort_k`.

### 5.11.4 `Badge` · `badges` · `bdg_` · `IMS` · `permanent`

Badge definition; criteria are in terms of verified cells only (FD§6.1). Criteria are immutable; only `status` changes.

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `slug` | text | NN, unique | |
| `criteria` | json | NN | declarative, for example `{"metric":"accepted_cells","op":">=","value":100}`; allowed metrics are verified-cell counts only, never streaks (FD§6.1: no streak penalties) |
| `criteria_hash` | hash | NN | |
| `copy_key` | text | NN | |
| `status` | enum(`badge_status`) | NN | |

### 5.11.5 `BadgeAward` · `badge_awards` · `baw_` · `IMM` · `member_bound`

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `member_id`, `badge_id` | id | NN, FK; **unique pair** | |
| `accepted_cells_at_award` | int | NN | |

**Not stored** the criteria snapshot (the badge's `criteria_hash` identifies it).

### 5.11.6 `Referral` · `referrals` · `ref_` · `MUT` · `member_bound`

Referral link and its two-sided bonus state (FD§6.2 V5). The bonus is a `grant` from the Reserve, never a `mint` (`ISS-06`). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `referrer_member_id` | id `mem_` | NN, FK | |
| `newcomer_member_id` | id `mem_` | null, FK, unique; `<> referrer` | set at redemption |
| `invite_id` | id `inv_` | null, FK | the invite used, if the link was also an invite |
| `code_hash` | bytes32 | NN, unique | |
| `state` | enum(`referral_state`) | NN | `issued`, `redeemed`, `qualified`, `paid`, `voided`, `expired` |
| `newcomer_verified_cells` | int | NN, default 0 | qualifies at `growth.referral.min_newcomer_verified_cells` |
| `qualified_at`, `hold_until` | ts | null | payment waits `growth.referral.hold_s` |
| `bonus_referrer_txn_id`, `bonus_newcomer_txn_id` | id `txn_` | null, FK, unique | |
| `void_reason` | text | null | one of `farming_flag`, `same_device`, `same_invite_tree`, `member_closed`, `reserve_paused` |

**Indexes** `(referrer_member_id, created_at)` (`growth.referral.max_per_referrer_per_30d`); `(state, hold_until)`. Anti-farming checks (same device, same tree, shared IP hash within TTL) read `devices` and `invites`; their outcome is only the `void_reason` code.

## 5.12 Configuration, change and launch-gate entities

### 5.12.1 `Parameter` · `parameters` · `prm_` · `MUT` · `permanent`

Definition of a configuration parameter (S0.10.3). The value itself is in the current `ParameterVersion`. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `name` | text | NN, unique, regex of S0.10.1 | never renamed |
| `type` | enum | NN | `int`, `ratio`, `credits`, `duration_s`, `days`, `bool`, `enum`, `string`, `json` |
| `unit` | text | null | |
| `validation` | json | NN | `min`, `max`, `enum`, `exclusive_bounds`, named constraints `C1`..`C8` (S0.10.3) |
| `default_value` | json | NN | the `initial configurable default`; never edited |
| `current_version_id` | id `pmv_` | NN, FK (deferred) | |
| `tighten_direction` | enum | NN | `up`, `down`, `none` |
| `notice_days` | int | NN | |
| `owner` | enum | NN | `operator`, `reviewer`, `founders` |
| `calibration_source` | text | NN | a code of S0.10.4 plus a pointer |
| `is_public`, `is_mutable` | bool | NN | constants have `is_mutable = false`; `security.*` has `is_public = false` |
| `introduced_in` | text | NN, `^S[0-9]+\.[0-9]+$` | |

**Indexes** `(owner)`. A parameter's value is never read from this table by business code; it reads the current version through the cache that S4.* defines, and stamps the version number where S0.10.3 says so.

### 5.12.2 `ParameterVersion` · `parameter_versions` · `pmv_` · `IMM` · `permanent`

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `parameter_id`, `version` | id, int | NN; unique pair; versions start at 1 and rise by 1 | |
| `value` | json | NN | typed per `Parameter.type`; ratios in ppm, credits in `ucr` strings (S0.6.1) |
| `value_hash` | hash | NN | |
| `effective_from` | ts | NN | `>= created_at + notice_days` unless `change_class = 'tighten'` (trigger) |
| `change_class` | enum | NN | |
| `reason` | text | NN, <= 1000 chars | published when the parameter is public |
| `changelog_entry_id`, `admin_action_id` | id | NN for public parameters, FK | |
| `approval_action_ids` | arr | NN | a `loosen` change needs a second `operator` approval (S0.10.3) |
| `supersedes_id` | id `pmv_` | null, FK | |

Prior values are never overwritten, so a job, lot or lease that stamped `(name, version)` can always be reproduced.

### 5.12.3 `KillSwitch` · `kill_switches` · `ksw_` · `IMM` · `permanent`

State history of each kill switch (S0.10.6). Each row is one change; the current state of a key is its latest row, and a key with no row is `released`. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `switch_key` | text | NN | `kill.all_minting`, `kill.all_new_jobs`, `kill.template.<tpl_id>`, `kill.service.<svc_id>`, `kill.member.<mem_id>` |
| `state` | enum | NN | `engaged`, `released` |
| `seq` | int64 | NN, unique | |
| `reason` | text | NN, <= 1000 chars | |
| `admin_action_id` | id `act_` | NN, FK | releasing needs two admins (`security.two_person_actions`) |

**Indexes** `(switch_key, seq DESC)`. The view `kill_switch_current` returns the latest row per key; every guard reads it. Engaging is a tightening and takes effect at once.

### 5.12.4 `FeatureFlag` · `feature_flags` · `ffl_` · `MUT` · `permanent`

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `flag_key` | text | NN, unique, `^ff\.[a-z0-9_]+\.[a-z0-9_]+$` | `ff.growth.v1_fast_path` .. `ff.growth.v6_milestones`, `ff.channel.human_review`, `ff.job.reservations`, `ff.public.ledger_page`, `ff.experiment.expiry_arm` |
| `enabled` | bool | NN, default false | |
| `rollout_ppm` | ppm | NN, default 0 | exposure fraction when an experiment drives it |
| `experiment_id` | id `exp_` | null, FK | experiment-capable flags have one (S0.10.6) |
| `description_key` | text | NN | |

Every change writes an `AdminAction` and, when public, a `ChangeLogEntry`.

### 5.12.5 `ChangeLogEntry` · `change_log_entries` · `chg_` · `IMM` · `permanent`

Public record of a parameter, policy, template or service change (R10, FD Principle 5). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `seq` | int64 | NN, unique | |
| `subject_type`, `subject_id` | enum(`changelog_subject_type`), id | NN | |
| `change_class` | enum | NN | |
| `summary_en`, `summary_fa` | text | NN / null, <= 1000 chars | `fa` carries `needs_human_and_legal_review` until reviewed |
| `before_hash`, `after_hash` | hash | NN | |
| `effective_from` | ts | NN | |
| `published_at` | ts | NN | `published_at <= effective_from` for `loosen` and `neutral` (CHECK); a `tighten` may publish up to `change.tighten_publish_within_s` after |
| `notice_given_days` | int | NN | |
| `admin_action_id` | id `act_` | NN, FK | |
| `supersedes_id` | id `chg_` | null, FK | a correction is a new entry |

### 5.12.6 `LaunchGateItem` · `launch_gate_items` · `lgi_` · `IMM` (revision rows) · `permanent`

One checklist line of `G0`..`G5` with its evidence and sign-offs (FD§8.3). A line is a stable `item_key`; every state change inserts a new revision row, so evidence and sign-offs are never overwritten (`ISS-53`). Machine S0.9.8: `open`, `evidence_attached`, `signed_off`, `reopened`. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `gate_id` | enum(`gate_id`) | NN | |
| `item_key` | text | NN | stable, for example `G0.counsel_memo`, `G0.service_flags:<svc_id>`, `G1.threat_model`, `G2.reachability`, `G3.calibration`, `G4.repo_review`, `G5.demand_check` |
| `revision` | int | NN; `(item_key, revision)` unique | starts at 1 |
| `status` | enum | NN | |
| `title_key` | text | NN | copy key |
| `service_id` | id `svc_` | null, FK | set for per-service G0 lines |
| `evidence` | json | NN | array of `{kind, ref_id, hash, note}`; `kind` is `service_entry`, `terms_copy`, `calibration_record`, `document` (hash and title only) or `counsel_memo` (hash and date only; the memo text is not stored) |
| `evidence_hash` | hash | NN | |
| `signoffs` | json | NN | array of `{admin_user_id, signed_at, admin_action_id, evidence_hash}` |
| `reopen_reason` | text | NN when `reopened`, <= 1000 chars | |
| `supersedes_id` | id `lgi_` | null, FK | previous revision |
| `created_by_admin_id` | id `adm_` | NN, FK | |

**Checks (trigger)** `evidence_attached` requires non-empty `evidence`; `signed_off` requires at least `launch.min_signoffs` distinct `admin_user_id` values in `signoffs`, each signing the current `evidence_hash`, and none of them the `created_by_admin_id` of the evidence unless the parameter allows it [A]. **View** `launch_gate_items_current` returns the highest revision per `item_key`; the rule that decides whether `launch.members_may_join` may be set reads it (S14.*). **Indexes** `(gate_id, item_key, revision DESC)`. Counsel answers and provider answers are [V] data entered by humans; the system never fills them.

## 5.13 Measurement and operations entities

### 5.13.1 `Experiment` · `experiments` · `exp_` · `IMS` · `permanent`

An arm configuration, including the accelerated-expiry arm (FD§9 Phase 1). Arms are frozen once the experiment is `running`. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `experiment_key` | text | NN, unique, `^EXP-[0-9]{2,}$` | S0.5 |
| `kind` | text | NN | `expiry_arm`, `growth`, `other` [A] |
| `flag_key` | text | null | the feature flag it drives (`ff.experiment.expiry_arm`, `ff.growth.v1_fast_path`, ...) |
| `arms` | json | NN | array of `{arm, fraction_ppm, overrides}`; fractions sum to 1000000; `overrides` maps parameter names to values, for example `{"credit.lifetime_days": "14"}` for the accelerated arm |
| `status` | enum(`experiment_status`) | NN, default `draft` | |
| `prereg_id` | id `prr_` | **NN when `running`** (CHECK) | no experiment starts without a locked pre-registration |
| `seed_version` | int | NN | `experiment.assignment_seed_version` at start |
| `started_at`, `stopped_at` | ts | null | |

### 5.13.2 `ExperimentAssignment` · `experiment_assignments` · `asg_` · `IMM` · `permanent`

Logged, randomized assignment (prompt G); `experiment.assignment_log_enabled` is the constant true. [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `experiment_id`, `member_id` | id | NN, FK; **unique pair** | |
| `arm` | text | NN | |
| `bucket_ppm` | int | NN, `0..999999` | `uint32(HMAC-SHA-256(secret.experiment_assignment_key, experiment_key \|\| member_id)[0..4]) mod 1000000` [A]; the arm is the interval of the cumulative `fraction_ppm` that contains it |
| `seed_version` | int | NN | |
| `assigned_at` | ts | NN | |

The `mem_` id is opaque (the member row is reduced on closure, S5.6.1). **Not stored** any trait of the member used to choose the arm; assignment depends only on the bucket.

### 5.13.3 `PreRegistration` · `pre_registrations` · `prr_` · `IMS` · `permanent`

Thresholds and decision rules recorded before launch, then locked (prompt H). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `title` | text | NN, <= 120 chars | |
| `thresholds` | json | NN | named values, for example `eta_min_ppm`, `week2_return_min_ppm`, `large_jobs_within_quote_min`; each name has a `measure_code` and a definition reference to the metric it applies to |
| `decision_rules` | text | NN, <= 8000 chars | |
| `status` | enum(`prereg_status`) | NN, default `draft` | |
| `locked_at` | ts | NN iff `locked` | |
| `content_hash` | hash | NN iff `locked` | |
| `locked_by_admin_ids` | arr of `adm_` | NN iff `locked` | `FND` decisions: recorded by the founders' admin accounts |
| `amends_id` | id `prr_` | null, FK | after a lock a change is a new row that amends the locked one and is published as an amendment |

All columns except `status`, `locked_at`, `content_hash` and `locked_by_admin_ids` are frozen after lock (trigger). The rule that sets `launch.members_may_join` requires every pre-registration listed for Phase 1 to be `locked` (S14.*).

### 5.13.4 `Event` · `events` · `evt_` · `IMS` · `ops`

Domain and analytics event without personal data; also the transactional outbox (S0.9.1). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `name` | text | NN | S0.9 event names and `ledger.*`, `parameter.*`, `policy.*`, `changelog.*`, `launch.*` |
| `event_version` | int | NN | |
| `occurred_at` | ts | NN | |
| `actor_type`, `actor_ref` | enum, text | NN, null | `principal_type` and an opaque id (`mem_`, `adm_` or null) |
| `subject_type`, `subject_id` | text, id | null | |
| `policy_version_id` | id `plv_` | null | |
| `parameter_versions` | json | NN | versions in force |
| `payload` | json | NN, <= 4 KiB | per-name schema of codes, counts and ids; **no free text**, no output text, no IP |
| `request_id` | text | null | |
| `published_at` | ts | null | set once when the outbox relay publishes it |

**Indexes** `(published_at) WHERE published_at IS NULL`; `(name, occurred_at)`; `(subject_type, subject_id)`; `(actor_ref, occurred_at)`. **Retention** `retention.event_raw_days` (default 30), after which rows are deleted and only `MetricSnapshot` aggregates remain; a 28-day return metric therefore fits inside the raw window [A]. `analytics.third_party_trackers` and `analytics.cookies_enabled` are constants false: no event leaves the platform.

### 5.13.5 `MetricSnapshot` · `metric_snapshots` · `mts_` · `IMM` · `permanent`

Aggregated published metric: v, η, claim ratio, mint-cap utilization, return rates, false-accept and false-reject estimates (FD§9 Phase 1 list). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `metric_name` | text | NN, `^hamyar_[a-z0-9_]+$` | S0.5 |
| `scope`, `scope_key` | enum(`metric_scope`), text | NN, null | for example `job_type` / `translation_glossary` for v |
| `window_start`, `window_end` | ts | NN | |
| `value`, `unit` | int64, enum(`metric_unit`) | NN, NN | ratios in ppm, amounts in `ucr` |
| `numerator`, `denominator` | int64 | null | kept so a ratio can be recomputed; v = verification cells / accepted primary cells |
| `sample_size` | int | NN | |
| `is_suppressed` | bool | NN | true when the cohort is below `analytics.min_cohort_k` (the value is then NULL in public views) |
| `published_at` | ts | null | |
| `computation_version` | text | NN | |
| `parameter_versions` | json | NN | |
| `supersedes_id` | id `mts_` | null, FK | a recomputation is a new snapshot |

**Indexes** `(metric_name, scope, scope_key, window_end DESC)`. Simulation output is never written here (prompt K): simulated runs use a separate database.

### 5.13.6 `CalibrationRecord` · `calibration_records` · `cal_` · `IMM` · `permanent`

Phase 0 calibration observation (FD§8.3 G3, S0.10.4 `CAL`). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `service_id` | id `svc_` | NN, FK | |
| `template_version_id` | id `tpv_` | null, FK | |
| `recorded_by_admin_id` | id `adm_` | NN, FK | the founder or tester who ran the cells on their own account |
| `observed_on` | day | NN | |
| `cells_attempted`, `cells_completed`, `cells_refused`, `cells_failed` | int | NN, >= 0, `completed + refused + failed <= attempted` | |
| `cells_until_limit` | int | null | cells completed before the allowance limited the account that day |
| `seconds_per_cell` | arr of int | NN, <= 500 values | raw samples; percentiles are computed from them |
| `copy_paste_errors` | int | NN | |
| `auto_check_passes`, `auto_check_fails` | int | NN | |
| `max_input_chars_completed` | int | null | feeds `cell.envelope.max_input_chars` |
| `note` | text | null, <= 1000 chars | the reviewer is told not to enter credentials or account identifiers |
| `supersedes_id` | id `cal_` | null, FK | |

`calibration.min_samples_per_service` decides when these rows may replace a default; that decision is a `ParameterVersion` with `calibration_source` pointing at the records. **Not stored** the provider account name or any identifier of the tester's account.

### 5.13.7 `InvariantCheck` · `invariant_checks` · `ivc_` · `IMM` · `ops` (with exception)

Result of one run of a ledger invariant (prompt C). [D]

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `invariant_id` | text | NN, `^INV-L[0-9]{2,}$` | |
| `run_kind` | enum(`check_run_kind`) | NN | `per_commit`, `sampled`, `full_recompute`, `checkpoint` |
| `started_at`, `finished_at` | ts | NN | |
| `seq_from`, `seq_to` | int64 | NN | the ledger range covered |
| `result` | enum(`check_result`) | NN | |
| `details` | json | null, <= 8 KiB | expected and actual aggregates; account ids only |
| `checkpoint_hash` | hash | NN iff `checkpoint` | the head `entry_hash` published daily (`ledger.checkpoint_interval_s`) |
| `alarm_id` | id `alm_` | null, FK | |

**Retention** `retention.ops_log_days`, except that rows with `result = 'violated'` and every `checkpoint` row are exempt from purging, because a checkpoint is the external anchor of the chain and a violation is evidence [A]; both are reported in `ISS-51`. **Indexes** `(invariant_id, started_at DESC)`; `(result) WHERE result <> 'passed'`.

### 5.13.8 `Alarm` · `alarms` · `alm_` · `MUT` · `ops`

| Field | Type | Null / constraint | Note |
| --- | --- | --- | --- |
| `alarm_key` | text | NN | `ledger.invariant_violated`, `price.eta_below_threshold`, `inflation.mint_utilization`, `verify.false_accept_alarm`, `verify.false_reject_alarm`, `service.review_due`, `retention.job_failed`, ... |
| `severity` | enum(`alarm_severity`) | NN | |
| `state` | enum(`alarm_state`) | NN, default `open` | |
| `dedupe_key` | text | NN | unique while `open` or `acknowledged` |
| `source_ref` | text | null | an id such as an `ivc_` or `mts_` |
| `details` | json | null, <= 4 KiB | |
| `acknowledged_by_admin_id`, `acknowledged_at`, `resolved_at` | id, ts, ts | null | |

**Retention** `retention.ops_log_days` after `resolved_at`. A `critical` ledger alarm also engages `kill.all_minting` and `kill.all_new_jobs` by policy (S14.*); that is an `AdminAction` by `system`, not a column here.

## 5.14 DDL for the critical entities

SQL-like (PostgreSQL dialect) [A]. It is normative for names, types, nullability, keys and constraints; the migration tool and exact syntax belong to S4.*. `is_id(v, p)` returns true when `v ~ '^' || p || '_[0-9a-hjkmnp-tv-z]{26}$'`; `is_hash(v)` checks `sha256:` plus 64 hex; `set_row_version()` is the `BEFORE UPDATE` trigger of S5.2.2. Check constraints on enum columns repeat the values of S0.8 and S5.2.5; the lists are abbreviated `-- enum(...)` where they are long. All foreign keys are `ON DELETE RESTRICT` (S5.2.6). [D]

### 5.14.1 Member and Device

```sql
CREATE TABLE devices (
  id text PRIMARY KEY CHECK (is_id(id,'dev')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  row_version int NOT NULL DEFAULT 1,
  device_token_hash bytea UNIQUE CHECK (octet_length(device_token_hash) = 32),  -- NULL after purge
  hash_key_version int NOT NULL,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','blocked')),
  first_seen_day date NOT NULL,
  last_seen_day date NOT NULL,
  creation_ip_hash bytea CHECK (octet_length(creation_ip_hash) = 32),
  ip_hash_key_version int,
  creation_ip_hash_expires_at timestamptz,
  grants_claimed int NOT NULL DEFAULT 0 CHECK (grants_claimed >= 0),
  CHECK ((creation_ip_hash IS NULL) = (creation_ip_hash_expires_at IS NULL))
);
CREATE INDEX devices_ip ON devices (creation_ip_hash, created_at) WHERE creation_ip_hash IS NOT NULL;

CREATE TABLE members (
  id text PRIMARY KEY CHECK (is_id(id,'mem')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  row_version int NOT NULL DEFAULT 1,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended','banned','closed')),
  status_changed_at timestamptz NOT NULL DEFAULT now(),
  trust_tier text NOT NULL DEFAULT 'new' CHECK (trust_tier IN ('new','established','trusted','restricted')),
  tier_before_restriction text CHECK (tier_before_restriction IN ('new','established','trusted')),
  restricted_until timestamptz,
  locale text CHECK (locale IN ('fa','en')),            -- NULL only on a closed tombstone
  digits text CHECK (digits IN ('latin','persian')),
  calendar text CHECK (calendar IN ('jalali','gregorian')),
  time_zone text,
  creating_device_id text REFERENCES devices(id),
  invite_id text REFERENCES invites(id) DEFERRABLE INITIALLY DEFERRED,
  invite_root_member_id text REFERENCES members(id),
  invite_depth int NOT NULL DEFAULT 0 CHECK (invite_depth >= 0),
  team_id text REFERENCES teams(id) DEFERRABLE INITIALLY DEFERRED,
  team_joined_at timestamptz,
  email_ciphertext bytea, email_key_version int,
  email_lookup_hash bytea UNIQUE CHECK (octet_length(email_lookup_hash) = 32),
  email_verified_at timestamptz,
  accepted_cells_count int NOT NULL DEFAULT 0,
  first_accepted_at timestamptz,
  reliability_ppm bigint CHECK (reliability_ppm BETWEEN 0 AND 1000000),
  reliability_obs int NOT NULL DEFAULT 0,
  starter_granted_at timestamptz,
  recovery_cooldown_until timestamptz,
  last_active_day date,
  closed_at timestamptz,
  CHECK ((trust_tier = 'restricted') = (tier_before_restriction IS NOT NULL)),
  CHECK (status <> 'closed' OR closed_at IS NOT NULL),
  CHECK ((email_ciphertext IS NULL) = (email_lookup_hash IS NULL)),
  CHECK (status = 'closed' OR (locale IS NOT NULL AND digits IS NOT NULL AND calendar IS NOT NULL))
);
CREATE INDEX members_status ON members (status, trust_tier);
CREATE INDEX members_team ON members (team_id) WHERE team_id IS NOT NULL;
CREATE INDEX members_tree ON members (invite_root_member_id);
CREATE INDEX members_device ON members (creating_device_id, created_at);
```

### 5.14.2 Cell

```sql
CREATE TABLE cells (
  id text PRIMARY KEY CHECK (is_id(id,'cel')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  row_version int NOT NULL DEFAULT 1,
  job_id text NOT NULL REFERENCES jobs(id),
  cell_kind text NOT NULL CHECK (cell_kind IN ('primary','gold','audit','third','review','rework')),
  ordinal int CHECK (ordinal >= 1),
  state text NOT NULL DEFAULT 'queued' CHECK (state IN ('queued','leased','submitted','flagged_for_audit',
    'accepted','rejected','expired','suspended','cancelled','voided','exhausted','overturned')),
  attempt int NOT NULL DEFAULT 1 CHECK (attempt >= 1),            -- upper bound is parameter cell.max_attempts
  template_version_id text NOT NULL REFERENCES template_versions(id),
  purpose text NOT NULL CHECK (purpose IN ('P0','P1','P2','P3')),
  license text NOT NULL CHECK (license IN ('L0','L1','L2','L3')),
  sensitivity text NOT NULL CHECK (sensitivity IN ('S0','S1')),   -- S2 and S3 never reach a cell
  service_requirement text NOT NULL CHECK (service_requirement IN ('M0','M1','M2')),
  pinned_service_ids text[] NOT NULL DEFAULT '{}',
  topic_category_id text REFERENCES topic_categories(id),
  input_payload text, input_hash text NOT NULL CHECK (is_hash(input_hash)),
  rendered_prompt text, rendered_prompt_hash text NOT NULL CHECK (is_hash(rendered_prompt_hash)),
  input_chars int NOT NULL CHECK (input_chars >= 0),
  gold_cell_id text REFERENCES gold_cells(id),
  audit_id text REFERENCES audits(id) DEFERRABLE INITIALLY DEFERRED,
  subject_cell_id text REFERENCES cells(id),
  subject_submission_id text REFERENCES submissions(id) DEFERRABLE INITIALLY DEFERRED,
  priority_key bigint NOT NULL,
  queued_at timestamptz NOT NULL DEFAULT now(),
  earliest_lease_at timestamptz,
  current_lease_id text REFERENCES leases(id) DEFERRABLE INITIALLY DEFERRED,
  accepted_submission_id text UNIQUE REFERENCES submissions(id) DEFERRABLE INITIALLY DEFERRED,
  accepted_at timestamptz,
  accept_policy_version_id text REFERENCES policy_versions(id),
  last_reject_code text CHECK (last_reject_code ~ '^reject\.[a-z_]+$'),
  credit_txn_id text UNIQUE REFERENCES ledger_transactions(id),
  payload_purged_at timestamptz,
  CHECK ((cell_kind = 'primary') = (ordinal IS NOT NULL)),
  CHECK ((cell_kind = 'gold') = (gold_cell_id IS NOT NULL)),
  CHECK ((cell_kind IN ('audit','third')) = (audit_id IS NOT NULL)),
  CHECK ((cell_kind = 'rework') = (subject_cell_id IS NOT NULL)),
  CHECK ((cell_kind = 'review') = (subject_submission_id IS NOT NULL)),
  CHECK ((state = 'leased') = (current_lease_id IS NOT NULL)),
  CHECK (state NOT IN ('accepted','overturned') OR accepted_submission_id IS NOT NULL),
  CHECK (credit_txn_id IS NULL OR state IN ('accepted','overturned'))
);
CREATE UNIQUE INDEX cells_primary_ordinal ON cells (job_id, ordinal) WHERE cell_kind = 'primary';
CREATE INDEX cells_queue ON cells (priority_key) WHERE state = 'queued';
CREATE INDEX cells_job_state ON cells (job_id, state);
CREATE INDEX cells_subject ON cells (subject_cell_id) WHERE subject_cell_id IS NOT NULL;
CREATE INDEX cells_services ON cells USING gin (pinned_service_ids);
-- Trigger cells_frozen: purpose, license, sensitivity, service_requirement, pinned_service_ids,
-- template_version_id, input_hash, rendered_prompt_hash, job_id and cell_kind never change after insert.
```

### 5.14.3 Lease

```sql
CREATE TABLE leases (
  id text PRIMARY KEY CHECK (is_id(id,'lse')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  row_version int NOT NULL DEFAULT 1,
  cell_id text NOT NULL REFERENCES cells(id),
  member_id text NOT NULL REFERENCES members(id),
  device_id text REFERENCES devices(id),
  attempt int NOT NULL CHECK (attempt >= 1),
  state text NOT NULL DEFAULT 'active' CHECK (state IN ('active','submitted','expired','released','revoked')),
  nonce_hash bytea NOT NULL CHECK (octet_length(nonce_hash) = 32),
  issued_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL,
  timeout_s_applied int NOT NULL CHECK (timeout_s_applied > 0),
  extensions_used int NOT NULL DEFAULT 0 CHECK (extensions_used >= 0),
  optin_version int NOT NULL,
  policy_version_id text NOT NULL REFERENCES policy_versions(id),
  ended_at timestamptz,
  end_reason text,   -- enum(submitted, expired, declined, released, revoked_policy, revoked_service, revoked_job_cancelled, revoked_integrity)
  CHECK (expires_at > issued_at),
  CHECK ((state = 'active') = (ended_at IS NULL)),
  UNIQUE (cell_id, attempt)
);
CREATE UNIQUE INDEX leases_one_active_per_cell ON leases (cell_id) WHERE state = 'active';   -- the race guard
CREATE INDEX leases_reaper ON leases (expires_at) WHERE state = 'active';
CREATE INDEX leases_member_active ON leases (member_id) WHERE state = 'active';
```

### 5.14.4 Submission

```sql
CREATE TABLE submissions (
  id text PRIMARY KEY CHECK (is_id(id,'sub')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  row_version int NOT NULL DEFAULT 1,
  lease_id text NOT NULL UNIQUE REFERENCES leases(id),            -- one submission per lease
  cell_id text NOT NULL REFERENCES cells(id),
  member_id text NOT NULL REFERENCES members(id),
  volunteer_handle text NOT NULL CHECK (volunteer_handle ~ '^vol_[0-9a-f]{32}$'),
  handle_key_version int NOT NULL,
  state text NOT NULL DEFAULT 'received' CHECK (state IN ('received','schema_failed','checks_failed',
    'checks_passed','quarantined','accepted','rejected')),
  output_text text,                                              -- NULL after purge
  output_hash text NOT NULL CHECK (is_hash(output_hash)),
  normalized_output_hash text NOT NULL CHECK (is_hash(normalized_output_hash)),
  output_simhash bigint NOT NULL,
  output_chars int NOT NULL CHECK (output_chars >= 0),
  output_bytes int NOT NULL CHECK (output_bytes >= 0),           -- upper bound is cell.envelope.max_submission_bytes
  reported_service_id text REFERENCES service_registry_entries(id),
  reported_model_label text CHECK (char_length(reported_model_label) <= 80),
  submitted_at timestamptz NOT NULL,
  elapsed_s int NOT NULL CHECK (elapsed_s >= 0),
  reject_code text CHECK (reject_code ~ '^reject\.[a-z_]+$'),
  quarantine_reason text CHECK (quarantine_reason IN ('output_url','code_to_run','action_request','other_flag')),
  checks_report jsonb,
  decided_at timestamptz,
  accept_policy_version_id text REFERENCES policy_versions(id),
  CHECK (state <> 'quarantined' OR quarantine_reason IS NOT NULL),
  CHECK (state NOT IN ('rejected','schema_failed','checks_failed') OR reject_code IS NOT NULL)
);
CREATE INDEX submissions_cell ON submissions (cell_id);
CREATE INDEX submissions_member ON submissions (member_id, submitted_at);
CREATE INDEX submissions_dup ON submissions (normalized_output_hash);
CREATE INDEX submissions_simhash ON submissions (output_simhash);
CREATE INDEX submissions_open ON submissions (state) WHERE state IN ('received','checks_passed','quarantined');
-- Trigger submissions_frozen: every column except state, reject_code, quarantine_reason, decided_at,
-- accept_policy_version_id, checks_report, output_text (only to NULL) is immutable after insert.
```

### 5.14.5 Ledger tables

```sql
CREATE TABLE ledger_accounts (
  id text PRIMARY KEY CHECK (is_id(id,'lac')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  row_version int NOT NULL DEFAULT 1,
  account_type text NOT NULL CHECK (account_type IN ('member','escrow','reserve','issuance','retired')),
  member_id text UNIQUE REFERENCES members(id),
  escrow_id text UNIQUE REFERENCES escrows(id) DEFERRABLE INITIALLY DEFERRED,
  balance_ucr bigint NOT NULL DEFAULT 0,
  last_entry_seq bigint NOT NULL DEFAULT 0,
  CHECK ((account_type = 'member') = (member_id IS NOT NULL)),
  CHECK ((account_type = 'escrow') = (escrow_id IS NOT NULL)),
  CHECK ((account_type = 'issuance' AND balance_ucr <= 0) OR (account_type <> 'issuance' AND balance_ucr >= 0))
);
CREATE UNIQUE INDEX ledger_accounts_singletons ON ledger_accounts (account_type)
  WHERE account_type IN ('reserve','issuance','retired');

CREATE TABLE ledger_heads (                -- infrastructure, not a domain entity; one row, locked FOR UPDATE by ledger_post()
  ledger_id text PRIMARY KEY CHECK (ledger_id = 'main'),
  last_seq bigint NOT NULL DEFAULT 0,
  last_hash text NOT NULL CHECK (is_hash(last_hash))   -- initial value 'sha256:' || repeat('0',64)
);

CREATE TABLE ledger_transactions (
  id text PRIMARY KEY CHECK (is_id(id,'txn')),
  created_at timestamptz NOT NULL DEFAULT now(),
  txn_kind text NOT NULL CHECK (txn_kind IN ('mint','grant','hold','payout','settle','cancel',
    'reservation_activate','expire','retire','reserve_donation','reversal')),
  natural_key text NOT NULL UNIQUE,
  member_id text REFERENCES members(id), job_id text REFERENCES jobs(id), cell_id text REFERENCES cells(id),
  reversal_of_txn_id text UNIQUE REFERENCES ledger_transactions(id),
  entry_count int NOT NULL CHECK (entry_count >= 1),
  total_ucr bigint NOT NULL CHECK (total_ucr > 0),
  actor_type text NOT NULL CHECK (actor_type IN ('member','admin','system')),
  actor_ref text,
  approval_action_ids text[] NOT NULL DEFAULT '{}',
  parameter_versions jsonb NOT NULL,
  CHECK ((txn_kind = 'reversal') = (reversal_of_txn_id IS NOT NULL)),
  CHECK (txn_kind <> 'reversal' OR cardinality(approval_action_ids) = 2)
);

CREATE TABLE ledger_entries (
  id text PRIMARY KEY CHECK (is_id(id,'lge')),
  created_at timestamptz NOT NULL,
  ledger_id text NOT NULL CHECK (ledger_id = 'main'),
  seq bigint NOT NULL,
  txn_id text NOT NULL REFERENCES ledger_transactions(id),
  entry_type text NOT NULL CHECK (entry_type IN ('mint','grant','escrow_hold','transfer','escrow_release',
    'levy','refund','expire','retire','reserve_donation','reversal')),
  debit_account_id text NOT NULL REFERENCES ledger_accounts(id),
  credit_account_id text NOT NULL REFERENCES ledger_accounts(id),
  amount_ucr bigint NOT NULL CHECK (amount_ucr > 0),
  lot_id text REFERENCES credit_lots(id) DEFERRABLE INITIALLY DEFERRED,
  lot_effect text NOT NULL CHECK (lot_effect IN ('create','consume','restore','none')),
  restores_entry_id text REFERENCES ledger_entries(id),
  reverses_entry_id text UNIQUE REFERENCES ledger_entries(id),
  job_id text REFERENCES jobs(id), cell_id text REFERENCES cells(id),
  prev_hash text NOT NULL CHECK (is_hash(prev_hash)),
  entry_hash text NOT NULL UNIQUE CHECK (is_hash(entry_hash)),
  UNIQUE (ledger_id, seq),
  CHECK (debit_account_id <> credit_account_id),
  CHECK ((entry_type = 'reversal') = (reverses_entry_id IS NOT NULL)),
  CHECK ((lot_effect = 'none') = (lot_id IS NULL))
);
CREATE INDEX ledger_entries_debit  ON ledger_entries (debit_account_id, seq);
CREATE INDEX ledger_entries_credit ON ledger_entries (credit_account_id, seq);
CREATE INDEX ledger_entries_txn    ON ledger_entries (txn_id);
CREATE INDEX ledger_entries_type   ON ledger_entries (entry_type, seq);
-- Triggers: ledger_entries_no_mutation (BEFORE UPDATE OR DELETE OR TRUNCATE -> raise immutable_row);
--           ledger_entries_via_post_only (BEFORE INSERT: raise unless current_setting('hamyar.in_ledger_post') = 'on').

CREATE TABLE credit_lots (
  id text PRIMARY KEY CHECK (is_id(id,'lot')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  row_version int NOT NULL DEFAULT 1,
  member_id text NOT NULL REFERENCES members(id),
  origin_entry_id text NOT NULL UNIQUE REFERENCES ledger_entries(id) DEFERRABLE INITIALLY DEFERRED,
  original_ucr bigint NOT NULL CHECK (original_ucr > 0),
  remaining_ucr bigint NOT NULL CHECK (remaining_ucr >= 0 AND remaining_ucr <= original_ucr),
  earned_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL CHECK (expires_at > earned_at),
  lifetime_days_applied int NOT NULL CHECK (lifetime_days_applied > 0),
  expiry_arm text,
  is_starter bool NOT NULL DEFAULT false
);
CREATE INDEX credit_lots_spend ON credit_lots (member_id, expires_at) WHERE remaining_ucr > 0;
CREATE INDEX credit_lots_sweep ON credit_lots (expires_at) WHERE remaining_ucr > 0;

CREATE TABLE escrows (
  id text PRIMARY KEY CHECK (is_id(id,'esc')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  row_version int NOT NULL DEFAULT 1,
  job_id text UNIQUE REFERENCES jobs(id) DEFERRABLE INITIALLY DEFERRED,
  reservation_id text UNIQUE REFERENCES reservations(id) DEFERRABLE INITIALLY DEFERRED,
  owner_member_id text NOT NULL REFERENCES members(id),
  ledger_account_id text NOT NULL UNIQUE REFERENCES ledger_accounts(id) DEFERRABLE INITIALLY DEFERRED,
  state text NOT NULL DEFAULT 'open' CHECK (state IN ('open','settling','closed')),
  escrow_ucr bigint NOT NULL CHECK (escrow_ucr > 0),
  planned_primary_ucr bigint NOT NULL CHECK (planned_primary_ucr >= 0),
  planned_pool_ucr bigint NOT NULL CHECK (planned_pool_ucr >= 0),
  planned_levy_ucr bigint NOT NULL CHECK (planned_levy_ucr >= 0),
  paid_ucr bigint NOT NULL DEFAULT 0, levy_ucr bigint NOT NULL DEFAULT 0,
  refunded_ucr bigint NOT NULL DEFAULT 0, released_ucr bigint NOT NULL DEFAULT 0,
  closing_txn_id text REFERENCES ledger_transactions(id),
  closed_at timestamptz,
  CHECK ((job_id IS NULL) <> (reservation_id IS NULL)),
  CHECK (planned_primary_ucr + planned_pool_ucr + planned_levy_ucr = escrow_ucr),
  CHECK (state <> 'closed' OR (closing_txn_id IS NOT NULL AND closed_at IS NOT NULL
         AND paid_ucr + levy_ucr + refunded_ucr + released_ucr = escrow_ucr))
);
```

### 5.14.6 The single ledger writer

Pseudocode of `ledger_post(txn jsonb)`, the only code path that writes the five tables above. It runs as `ledger_svc` inside one database transaction at `SERIALIZABLE` isolation; S6.* defines the callers. [D]

```
ledger_post(txn):
  SET LOCAL hamyar.in_ledger_post = 'on'
  IF exists(ledger_transactions WHERE natural_key = txn.natural_key):
        RETURN stored result of that transaction          -- idempotent replay, nothing written
  head := SELECT * FROM ledger_heads WHERE ledger_id = 'main' FOR UPDATE   -- serializes all postings
  FOR e IN txn.entries IN ORDER:
      rule := ledger_entry_type_rules[e.entry_type]
      ASSERT type(e.debit_account) = rule.debit_type AND type(e.credit_account) = rule.credit_type
      ASSERT e.lot_effect = rule.lot_effect                -- reversal: mirrors the reversed entry
      seq := head.last_seq + 1
      prev := head.last_hash
      hash := sha256(prev || rfc8785(e with seq, txn_id, created_at))
      INSERT ledger_entries(... seq, prev_hash = prev, entry_hash = hash)
      UPDATE ledger_accounts SET balance_ucr = balance_ucr - e.amount WHERE id = e.debit_account      -- CHECK enforces sign rules
      UPDATE ledger_accounts SET balance_ucr = balance_ucr + e.amount WHERE id = e.credit_account
      APPLY lot effect: create / consume oldest-first by expires_at / restore with original expiry
      head := (seq, hash)
  ASSERT sum(e.amount) = txn.total_ucr AND count(entries) = txn.entry_count
  ASSERT sum(balance_ucr over all accounts) = 0           -- the double-entry identity
  UPDATE ledger_heads SET last_seq, last_hash
  INSERT ledger_transactions(...)  ;  emit event ledger.entry_committed for each entry in the outbox
  COMMIT
```

Structural guarantees that hold without any application check: no balance below zero (except `issuance` at or below zero); every entry balanced and between permitted account types; `seq` gap-free and unique; `entry_hash` chained; one business key posts once; a second caller cannot write around the function. The sum of all five account types is zero, which restates FD§4.2: member balances + escrow + Reserve = cumulative mint − cumulative retired. [D]

### 5.14.7 Entry-type rules (reference data)

Seeded by a migration; read by `ledger_post()` and by the invariant checks. Changing a row is a spec change, not a configuration edit. [D]

| `entry_type` | `debit_type` | `credit_type` | `lot_effect` |
| --- | --- | --- | --- |
| `mint` | `issuance` | `member` | `create` |
| `grant` | `reserve` | `member` | `create` |
| `escrow_hold` | `member` | `escrow` | `consume` |
| `transfer` | `escrow` | `member` | `create` |
| `escrow_release` | `escrow` | `escrow` | `none` |
| `levy` | `escrow` | `reserve` | `none` |
| `refund` | `escrow` | `member` | `restore` |
| `expire` | `member` | `reserve` | `consume` |
| `retire` | `reserve` | `retired` | `none` |
| `reserve_donation` | `member` | `reserve` | `consume` |
| `reversal` | credit side of the reversed entry | debit side of the reversed entry | mirror of the reversed entry's effect |

### 5.14.8 Service Registry, flag answers and the launch-gate guards

```sql
CREATE TABLE service_registry_entries (
  id text PRIMARY KEY CHECK (is_id(id,'svc')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  row_version int NOT NULL DEFAULT 1,
  slug text NOT NULL UNIQUE,
  display_name text NOT NULL CHECK (char_length(display_name) <= 80),
  service_kind text NOT NULL CHECK (service_kind IN ('general_chat','open_weight_hosted','open_weight_local')),
  review_status text NOT NULL DEFAULT 'unreviewed' CHECK (review_status IN
    ('unreviewed','in_review','approved','review_due','rejected','suspended','revoked')),
  suspension_cause text CHECK (suspension_cause IN ('kill_switch','review_lapsed')),
  current_terms_copy_id text REFERENCES terms_copies(id) DEFERRABLE INITIALLY DEFERRED,
  reviewed_at timestamptz,
  review_due_at timestamptz,
  adapter_supports_prefill bool NOT NULL DEFAULT false,
  adapter_prefill_url_template text,
  adapter_max_url_chars int CHECK (adapter_max_url_chars > 0),
  adapter_copy_only bool NOT NULL DEFAULT true,
  adapter_clean_chat_hint_key text,
  open_weight_license_ref text,
  CHECK ((review_status = 'suspended') = (suspension_cause IS NOT NULL)),
  CHECK (review_status NOT IN ('approved','review_due') OR current_terms_copy_id IS NOT NULL),
  CHECK (NOT adapter_supports_prefill OR (adapter_prefill_url_template LIKE '%{prompt}%' AND adapter_max_url_chars IS NOT NULL)),
  CHECK (adapter_supports_prefill OR adapter_copy_only)
);

CREATE TABLE terms_copies (
  id text PRIMARY KEY CHECK (is_id(id,'tcp')),
  created_at timestamptz NOT NULL DEFAULT now(),
  service_id text NOT NULL REFERENCES service_registry_entries(id),
  document_kind text NOT NULL CHECK (document_kind IN ('terms','usage_policy','written_permission')),
  media_type text NOT NULL CHECK (media_type IN ('text/html','text/plain','application/pdf')),
  content_hash text NOT NULL CHECK (is_hash(content_hash)),
  byte_size int NOT NULL CHECK (byte_size > 0),          -- upper bound is parameter service.terms_copy_max_bytes
  storage_key text NOT NULL,
  source_ref text NOT NULL CHECK (char_length(source_ref) <= 500),
  provider_version_label text,
  captured_on date NOT NULL,
  captured_by_admin_id text NOT NULL REFERENCES admin_users(id),
  language text,
  supersedes_id text REFERENCES terms_copies(id),
  UNIQUE (service_id, content_hash)
);

CREATE TABLE flag_answers (
  id text PRIMARY KEY CHECK (is_id(id,'fla')),
  created_at timestamptz NOT NULL DEFAULT now(),
  service_id text NOT NULL REFERENCES service_registry_entries(id),
  flag_key text NOT NULL CHECK (flag_key IN ('third_party_task_use','access_pooling_or_crediting',
    'human_copy_paste_use','prefilled_link_use','regional_availability','commercial_use_of_output',
    'training_use_of_output','open_publication_of_output','prohibited_content_compatible',
    'info.provider_trains_on_chats','info.memory_or_connectors_risk','info.allowance_may_change','info.written_permission')),
  region text CHECK (region ~ '^[A-Z]{2}$'),
  answer text NOT NULL CHECK (answer IN ('yes','no','unknown')),
  terms_copy_id text REFERENCES terms_copies(id),
  evidence_note text CHECK (char_length(evidence_note) <= 2000),
  answered_on date NOT NULL,
  reviewer_admin_id text NOT NULL REFERENCES admin_users(id),
  supersedes_id text REFERENCES flag_answers(id),
  CHECK (flag_key <> 'regional_availability' OR region IS NOT NULL),
  CHECK (answer = 'unknown' OR terms_copy_id IS NOT NULL)
);
CREATE INDEX flag_answers_lookup ON flag_answers (service_id, flag_key, region, answered_on DESC, created_at DESC);

CREATE VIEW effective_flag_answers AS            -- latest answer per (service, flag, region); absent = unknown = no
  SELECT DISTINCT ON (service_id, flag_key, COALESCE(region,'')) *
  FROM flag_answers ORDER BY service_id, flag_key, COALESCE(region,''), answered_on DESC, created_at DESC;
```

```
TRIGGER svc_approval_guard BEFORE UPDATE ON service_registry_entries   -- defense in depth for S7.* and BM3
  IF NEW.review_status = 'approved' AND OLD.review_status IS DISTINCT FROM 'approved':
      REQUIRE NEW.current_terms_copy_id IS NOT NULL
      REQUIRE effective_answer(NEW.id,'third_party_task_use') = 'yes'
      REQUIRE effective_answer(NEW.id,'prohibited_content_compatible') = 'yes'
      REQUIRE every gate answer used by the approval points at a terms_copy of this service
      REQUIRE count(DISTINCT admin_user_id) FROM admin_actions
              WHERE action = 'service.approve' AND subject_id = NEW.id
                AND subject_hash = (SELECT content_hash FROM terms_copies WHERE id = NEW.current_terms_copy_id)
              >= parameter('service.min_approvers')
      IF NEW.adapter_copy_only = false: REQUIRE effective_answer(NEW.id,'prefilled_link_use') = 'yes'
      otherwise RAISE 'STATE_CONFLICT'

TRIGGER jobs_service_guard BEFORE UPDATE OF state ON jobs
  IF NEW.state IN ('quoted','admitted') AND OLD.state IS DISTINCT FROM NEW.state:
      candidates := NEW.pinned_service_ids if service_requirement = 'M1', else all services of the
                    kind the requirement allows (M0 general_chat, M2 open_weight_*)
      REQUIRE exists svc IN candidates WITH review_status = 'approved'    -- unreviewed counts as no
      REQUIRE the registry flags needed by NEW.purpose and NEW.license (R5, R6, R7) are 'yes' for that svc
      otherwise RAISE 'POLICY_REJECTED'
```

The trigger is not the policy engine: the engine (S7.*) decides and explains with `policy.<rule>.<slug>` reasons; the trigger makes it impossible to reach `quoted` or `admitted` through any other path, including a bug. [D]

### 5.14.9 PolicyVersion

```sql
CREATE TABLE policy_versions (
  id text PRIMARY KEY CHECK (is_id(id,'plv')),
  created_at timestamptz NOT NULL DEFAULT now(),
  policy_id text NOT NULL REFERENCES policies(id),
  version int NOT NULL CHECK (version >= 1),
  allowlist jsonb NOT NULL,
  allowlist_hash text NOT NULL CHECK (is_hash(allowlist_hash)),
  rules_hash text NOT NULL CHECK (is_hash(rules_hash)),
  version_hash text NOT NULL UNIQUE CHECK (is_hash(version_hash)),
  change_class text NOT NULL CHECK (change_class IN ('tighten','loosen','neutral')),
  changelog_entry_id text REFERENCES change_log_entries(id) DEFERRABLE INITIALLY DEFERRED,
  supersedes_id text REFERENCES policy_versions(id),
  effective_from timestamptz NOT NULL,
  created_by_admin_id text NOT NULL REFERENCES admin_users(id),
  approval_action_ids text[] NOT NULL DEFAULT '{}',
  UNIQUE (policy_id, version),
  CHECK (change_class <> 'loosen' OR changelog_entry_id IS NOT NULL)          -- R10
);
-- Trigger: for 'loosen', effective_from >= created_at + parameter('policy.loosen_min_notice_days') * interval '1 day'.
-- Trigger: version_hash = sha256(rules_hash || allowlist_hash); rules rows of this version are complete (R1..R10 once each).
```

### 5.14.10 LaunchGateItem

```sql
CREATE TABLE launch_gate_items (
  id text PRIMARY KEY CHECK (is_id(id,'lgi')),
  created_at timestamptz NOT NULL DEFAULT now(),
  gate_id text NOT NULL CHECK (gate_id IN ('G0','G1','G2','G3','G4','G5')),
  item_key text NOT NULL,
  revision int NOT NULL CHECK (revision >= 1),
  status text NOT NULL CHECK (status IN ('open','evidence_attached','signed_off','reopened')),
  title_key text NOT NULL,
  service_id text REFERENCES service_registry_entries(id),
  evidence jsonb NOT NULL DEFAULT '[]',
  evidence_hash text NOT NULL CHECK (is_hash(evidence_hash)),
  signoffs jsonb NOT NULL DEFAULT '[]',
  reopen_reason text,
  supersedes_id text REFERENCES launch_gate_items(id),
  created_by_admin_id text NOT NULL REFERENCES admin_users(id),
  UNIQUE (item_key, revision),
  CHECK (status NOT IN ('evidence_attached','signed_off') OR jsonb_array_length(evidence) > 0),
  CHECK (status <> 'reopened' OR reopen_reason IS NOT NULL),
  CHECK ((revision = 1) = (supersedes_id IS NULL))
);
CREATE VIEW launch_gate_items_current AS
  SELECT DISTINCT ON (item_key) * FROM launch_gate_items ORDER BY item_key, revision DESC;
-- Trigger lgi_signoff_guard: when status = 'signed_off',
--   count(DISTINCT signoffs[*].admin_user_id) >= parameter('launch.min_signoffs'), and every signoff.evidence_hash = evidence_hash.
```

The guard that sets `launch.members_may_join`, `launch.member_jobs_enabled` or `launch.minting_enabled` to true (S14.*) reads `launch_gate_items_current` for every gate in `launch.required_gate_ids` and requires `signed_off`, at least `launch.min_approved_services` approved registry entries, and locked pre-registrations. This part fixes only the data it reads. [D]

## 5.15 Append-only guarantees and how corrections are modelled

### 5.15.1 Guarantees [D]

| Id | Guarantee | Enforced by |
| --- | --- | --- |
| `AO-1` | Rows of `ledger_entries`, `ledger_transactions` and `admin_actions` are never updated or deleted by any application role, migration or operator tool | privileges (S5.2.4), `BEFORE UPDATE OR DELETE OR TRUNCATE` trigger, sole writer `ledger_post()` |
| `AO-2` | Every `IMM` table (S5.4) accepts inserts only | privileges and trigger |
| `AO-3` | An `IMS` table changes only its named state columns, and the content columns of an approved or reviewed row never change | column-level triggers (`frozen_column`) |
| `AO-4` | The ledger order is the gap-free `seq`; each `entry_hash` commits to the previous hash, so an edit, deletion or reordering of any past entry changes every later hash | chain, `UNIQUE (ledger_id, seq)`, daily checkpoint |
| `AO-5` | A correction is always a new row that references the old one; nothing that was once visible to a member, requester or the public is silently altered | the correction models of S5.4 |
| `AO-6` | Approvals are bound to content: an approval stored in `admin_actions` carries `subject_hash`, and a changed subject no longer matches it | `subject_hash` comparison in the guards |
| `AO-7` | Parameter, policy, template, terms-copy and flag history is never lost: a value in force at any past time can be reproduced from the stamped version ids | `ParameterVersion`, `PolicyVersion`, `TemplateVersion`, `TermsCopy`, `FlagAnswer` are `IMM` or `IMS` |
| `AO-8` | Retention removes payload and personal columns only, never an `IMM`/`CHN` row, except the `moderation` and `ops` rows listed in S5.15.4 | `retention_svc` column and table grants |

`AO-1` to `AO-8` are guarantees of the data layer. They do not protect against an actor who controls the database superuser, the secrets and the backups together; that residual risk (insider and operator risk) is carried by the threat model in S10.* and is not claimed away here. [D]

### 5.15.2 Chain verification and checkpoint [D]

```
verify_chain(from_seq, to_seq):
  prev := entry(from_seq - 1).entry_hash  (genesis: 'sha256:' + 64 zeros)
  FOR e IN ledger_entries WHERE seq BETWEEN from_seq AND to_seq ORDER BY seq:
      ASSERT e.seq = previous seq + 1                      -- gap-free
      ASSERT e.prev_hash = prev
      ASSERT e.entry_hash = sha256(prev || rfc8785(e without entry_hash))
      prev := e.entry_hash
  RETURN prev

checkpoint():                                              -- every ledger.checkpoint_interval_s
  h := verify_chain(last_checkpoint_seq + 1, head.last_seq)
  INSERT invariant_checks(run_kind = 'checkpoint', checkpoint_hash = h, ...)   -- exempt from purging
  publish h on the public ledger page (S12.*) so an outsider can detect a rewrite of past entries
```

The same procedure runs after every restore (S5.2.4) and in the `full_recompute` run, together with the recomputation of every `DER` cache (account balances, lot remainders, escrow and Reserve totals, member counters). A mismatch inserts an `InvariantCheck` with `result = 'violated'` and raises the `Alarm` `ledger.invariant_violated`. The invariant list `INV-L<nn>` is owned by S6.*. [D]

### 5.15.3 Corrections by entity group [D]

| Group | Model |
| --- | --- |
| Ledger | A `reversal` transaction posts, for each entry of the original transaction, an entry in the opposite direction with `reverses_entry_id` set and the mirrored lot effect. It needs two distinct `AdminAction` approvals (`ledger.reversal_min_approvers` = 2). The original rows stay and remain visible; the public ledger shows both. Reversal is the only way to change a past balance. A reversal that would drive any account below its sign limit is refused and is handled by a further, explicit posting chosen by S6.* |
| Cell acceptance found wrong (appeal, fraud) | `cell.overturned` (S0.9.3): the cell's state changes, the credit effect is a `reversal`, and a new `rework` cell is created; the `Submission` text is not edited |
| Verification | A new `VerificationRecord` with `supersedes_id`; the earlier record stays for the false-accept and false-reject estimates |
| Registry | A changed reading of a term is a new `FlagAnswer`; a changed document is a new `TermsCopy`; the entry's state moves through its machine |
| Policy, template, parameter | A new `PolicyVersion`, `TemplateVersion` or `ParameterVersion`, stamped on what it governs from then on (prospective only, FD Principle 5) |
| Launch gate | A new revision (`reopened`); earlier evidence and sign-offs remain |
| Public record | A new `ChangeLogEntry` or `MetricSnapshot` with `supersedes_id`; the earlier one is never deleted |
| Member data | Retention reduces rows; closure tombstones the member (S5.6.1) |

### 5.15.4 Retention jobs [D]

All jobs run as `retention_svc`, are idempotent, log one `Event` per run with counts only, and raise `retention.job_failed` when a run misses its schedule.

| Class | What the job does | Parameter |
| --- | --- | --- |
| `job_bound` | `retention.job_payload_days` after the job is terminal: set to NULL `cells.input_payload`, `cells.rendered_prompt`, `submissions.output_text`, `uploads.storage_key` (and delete the object), `glossaries.terms`, `deliverables.storage_key` (and delete the object), `verification_records.details`; set the matching `payload_purged_at`. Hashes, states, manifests and ledger rows stay | `retention.job_payload_days` |
| `member_bound` | On `closed` (member-initiated, or inactive for `retention.member_inactive_days`): tombstone the member, delete its keys, sessions, opt-ins, badge awards, referrals and teams-owned data (S5.6.1) | `retention.member_inactive_days` |
| `moderation` | `retention.moderation_days` after resolution: add counts to a `MetricSnapshot`, then null the personal columns and delete the `Report` or `Appeal` row | `retention.moderation_days` |
| `short` | Delete `sessions` past `retention.session_days`; null `devices.creation_ip_hash` after `retention.ip_hash_ttl_days`; purge devices as in S5.6.3 | `retention.session_days`, `retention.ip_hash_ttl_days` |
| `ops` | Delete `events` after `retention.event_raw_days`; `invariant_checks` and `alarms` after `retention.ops_log_days` except `violated` and `checkpoint` rows | `retention.event_raw_days`, `retention.ops_log_days` |
| `permanent` | Never touched | |

If a retention parameter is lowered, the next run applies it to existing rows (shortening retention is a tightening, R10); raising it applies only to rows not yet purged, because purged data cannot be recovered. [D]

## 5.16 Acceptance criteria for the data model

Given / When / Then, to be implemented as tests by S18.* (`T-unit`, `T-prop`, `T-adv`). [D]

- **`AC-data-01`** Given an application database role, when it issues `UPDATE`, `DELETE` or `TRUNCATE` on `ledger_entries`, then the statement fails with `immutable_row` and no row changes.
- **`AC-data-02`** Given a committed ledger, when one historical entry is altered by a superuser in a test copy, then `verify_chain` returns a mismatch at that `seq` and the checkpoint check raises `ledger.invariant_violated`.
- **`AC-data-03`** Given a transaction with `natural_key = 'payout:cel_x'` already posted, when `ledger_post()` is called again with the same key, then no entry is written and the stored result is returned.
- **`AC-data-04`** Given a member account with balance 0, when an `escrow_hold` of any amount is posted, then the transaction fails and no `seq` is consumed.
- **`AC-data-05`** Given a cell with an active lease, when a second lease for the same cell is inserted, then the unique index `leases_one_active_per_cell` rejects it and `LEASE_CONFLICT` is returned.
- **`AC-data-06`** Given a lease with one submission, when a second row is inserted for the same `lease_id`, then it is rejected by uniqueness and the API replays the stored outcome (S0.9.3).
- **`AC-data-07`** Given a `ServiceRegistryEntry` in `unreviewed`, when any job is moved to `quoted` for it, then `jobs_service_guard` refuses with `POLICY_REJECTED`; and given a service without a `TermsCopy`, when its status is set to `approved`, then `svc_approval_guard` refuses.
- **`AC-data-08`** Given a `PolicyVersion` with `change_class = 'loosen'`, when it is inserted without a `changelog_entry_id`, then the `CHECK` rejects it (R10).
- **`AC-data-09`** Given a `LaunchGateItem` revision with `status = 'signed_off'` and one distinct signer while `launch.min_signoffs` is 2, when it is inserted, then the trigger rejects it.
- **`AC-data-10`** Given a database dump, when it is searched for IPv4 and IPv6 patterns, clear e-mail patterns and the bytes of any test provider credential, then there are no matches (S5.3.1).
- **`AC-data-11`** Given the FD§3.3 example posted through `ledger_post()`, when the escrow of 276,000,000 `ucr` is settled, then `paid_ucr` = 264,000,000, `levy_ucr` = 12,000,000, `refunded_ucr` = 0, the escrow account balance is 0, and the sum of all account balances is 0.
- **`AC-data-12`** Given a closed member, when the retention job has run, then the `members` row holds only `id`, `created_at`, `status`, `closed_at` and `row_version`, and every permanent row that referenced the member still resolves.

## Issues raised

Problems and gaps found while fixing the stored shape of the domain model. Resolutions are already applied in this file; C-001 consolidates them. This file uses `ISS-51`..`ISS-53` (the first of the part's files, S0.4). [D]

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-51` | minor | prompt | Convention gaps: S0.8 lacks the enums listed in S5.2.5; S0.7 gives no table for team membership (the prompt needs teams), no recovery-key storage, no optional e-mail storage and no `ledger_heads` or rate-limit counter storage; `InvariantCheck` is `ops` yet daily checkpoints must outlive 30 days | Local enums added as [A] in S5.2.5; team membership is `members.team_id`; the recovery key is a `MemberKey` with `purpose = 'recovery'`; optional e-mail is `email_ciphertext` plus a keyed lookup hash on `members`; `ledger_heads` is infrastructure; `checkpoint` and `violated` `InvariantCheck` rows are exempt from `ops` purging; secret names in S5.3.3 are proposals for S10.* | proposed |
| `ISS-52` | minor | prompt | S0.13 proposes `spec/05a-domain-model.md` for this part; the owning cell's path is `spec/05a-entities.md`. Both the entity part and the state-machine part carry a top-level `# 5.` heading, so `## 5.<m>` numbers can collide at assembly | The cell path is authoritative (S0.13). This file numbers its sections `5.1`..`5.16`; the state-machine part should continue from `5.17` or C-001 renumbers at assembly. References to this file use `S5.<m>` with the numbers above | needs_owner |
| `ISS-53` | major | FD§5.6, FD§8.3, FD§5.7 | Four places where "permanent, never edited" and a changing state conflict: (1) `LaunchGateItem` has the states `open`, `evidence_attached`, `signed_off`, `reopened` but evidence and sign-offs must stay as history; (2) a kill switch has a state history; (3) approvals of templates, services and ledger reversals need a store but S0.7 has no approval entity; (4) FD§5.6 puts the volunteer id in the manifest but requesters must never see it | (1) revision rows with a current view; (2) `KillSwitch` rows are state changes, the latest wins; (3) approvals are `AdminAction` rows with `subject_hash`, counted by guards; (4) the manifest has an internal form with `volunteer_handle` and a redacted export; only the export reaches requesters | proposed |

Convention additions made by this part (not issues, listed so C-001 can fold them back): the local enums of S5.2.5; the columns `members.team_id`, `members.team_joined_at`, `members.email_*`, `cells.credit_txn_id`, `ledger_entries.lot_effect`, `leases.optin_version`; the reference table `ledger_entry_type_rules`; the views `effective_flag_answers`, `kill_switch_current`, `launch_gate_items_current`; the infrastructure table `ledger_heads`; the abbreviations `IMM`, `CHN`, `IMS`, `MUT`, `DER` and `AO-1`..`AO-8`; and the acceptance ids `AC-data-01`..`AC-data-12`.
