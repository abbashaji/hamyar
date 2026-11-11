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
