# 0. Conventions and Shared Vocabulary

*Spec part 0 · owner cell C-000 · binding on every other spec file. Written against Founding Document draft v0.1 (FD). Nothing here is legal advice and nothing here has been verified against any provider's terms or any law.*

## 0.1 How to use this file

- Every other spec file MUST use the names, IDs, enum values, state names, event names and parameter names in this file exactly (case-sensitive). [D]
- A name missing here MAY be added by the owning part, but it MUST be reported in that part's `## Issues raised` list as a convention gap (see 0.4) so C-001 can fold it back. [D]
- MUST, MUST NOT, SHOULD and MAY carry their usual RFC 2119 meaning. [P]
- Identifiers in `code font` are normative; prose labels are not.
- Facts about provider terms, regional availability, pricing, limits, URL parameters or law are configuration data entered by a human reviewer. This file hardcodes none of them; every dependence is tagged [V]. [D]
- Scope boundary: this file fixes vocabulary. Guards, side effects, algorithms, screens and copy live in the parts listed in 0.13. [D]

## 0.2 Evidence-tag legend

| Tag | Meaning | Required companion | Example |
| --- | --- | --- | --- |
| `[D]` | A decision this spec makes; binding on implementers | A one-line reason, or an FD§ reference | "Ledger amounts are integer micro-credits [D]" |
| `[H]` | A hypothesis; may be false | The measurement that tests it and the success or kill criterion | "A contribution takes under 60 s [H]" |
| `[V]` | Must be verified by a human before anyone relies on it | What is verified, by whom, and where the answer is stored (parameter, `ServiceRegistryEntry`, `LaunchGateItem`, counsel memo) | "Iran reachability of the host [V]" |
| `[P]` | A premise taken from the brief or the FD, not independently checked | The FD§ it comes from | "Free allowances cannot be transferred [P]" |
| `[A]` | An assumption introduced by this spec, not present in the FD | The owner decision that could overturn it (collected in S3.*) | "Admin host is a separate origin [A]" |

Writing rules for all parts: [D]

1. One tag per bracket. Combine by adjacency: `[H][V]`. Place the tag directly after the claim it qualifies.
2. Every number is either derived by a formula shown next to it or labeled exactly `initial configurable default` (and then it must exist in the parameter table, 0.10).
3. No statistic is invented. Simulation output is never evidence about human behavior (prompt K).
4. User-facing promises say "declared", never "guaranteed" (FD Principle 11). Legal conclusions are never drawn; they are `[V]` for counsel.
5. An unverified claim is never written as a fact; it is tagged or removed.

## 0.3 Cross-reference style

| Form | Meaning | Example | Rule |
| --- | --- | --- | --- |
| `FD§N` / `FD§N.M` | Section of the Founding Document | `FD§4.3` = price and exchange rate | Never "section 4.3" without the prefix |
| `S<n>.<m>` | Heading `## <n>.<m>` of spec part `<n>` (part number = section number of the required deliverable structure, prompt) | `S6.3` | Always contains a dot. A whole part is written `S<n>.*` |
| `S0.<m>` | This file | `S0.9` = state machines | |
| `ISS-nn` | An Issue (0.4) | `ISS-03` | |
| `R1`..`R10` | Policy rules (FD§5.4) | `R9` | Bare `R<n>`, never "rule 9" |
| `G0`..`G5` | Launch gates (FD§8.3) | `G1` | Not to be confused with parameter `grant.starter_credits` (FD symbol G) |
| `BM0`..`BM9` | Build milestones (0.12) | `BM2` | See `ISS-01` for why not `M0..Mn` |
| `P0`..`P3`, `L0`..`L3`, `S0`..`S3`, `M0`..`M2` | Purpose, license, sensitivity, service requirement (0.8) | `S1` (sensitivity) | Sensitivity has no dot; a spec reference always has one, so `S1` and `S1.2` never collide |
| `C-nnn` | Build cell id | `C-022` | Allowed only in this file, in `## Issues raised` and in provenance notes; never in normative text |

A reference to a section that does not exist yet MUST still be written in this form; C-001 checks every reference resolves at assembly. [D]

## 0.4 Issue ID scheme and how parts report issues

An Issue is a problem, gap or unimplementable rule found in the FD (or in an instruction) together with a proposed resolution. [D]

**ID format.** `ISS-nn`, `nn` at least two digits, never reused, never renumbered. Collisions between parts written in parallel are prevented by fixed blocks: part `p` (first number of the file's top heading) owns `ISS-(10p+1)` .. `ISS-(10p+9)`; part 0 owns `ISS-01`..`ISS-09`, part 1 `ISS-11`..`ISS-19`, part 2 `ISS-21`..`ISS-29`, and so on up to part 21 (`ISS-211`..`ISS-219`). If the plan splits one part over several files, the file that sorts first uses digits 1-3, the second 4-6, the third 7-9. [D]

**Reporting.** Every spec file ends with `## Issues raised`, a table with these columns (an empty table states "none"): [D]

| Column | Values |
| --- | --- |
| `id` | `ISS-nn` from the file's block |
| `severity` | `blocking` (cannot be implemented as written), `major` (changes a design), `minor` (naming, wording) |
| `fd_ref` | `FD§N` or `prompt` or `none` |
| `issue` | One line |
| `resolution` | Proposed resolution, already applied consistently inside the file |
| `status` | `proposed`, `accepted`, `applied`, `rejected`, `needs_owner` (only the owner can decide; also listed in S3.*) |

C-001 consolidates all tables into S2.* (grouped by severity, each with the parts that apply the resolution) and may add its own issues in `ISS-21`..`ISS-29`. A part applies its own proposed resolution until C-001 records a different one. [D]

## 0.5 Other document ID schemes

| Scheme | Format | Owner part | Example |
| --- | --- | --- | --- |
| Ledger invariants | `INV-L<nn>` | S6.* | `INV-L01` |
| Threats | `THR-<nn>` | S10.* | `THR-07` |
| Risks | `RISK-<nn>` (FD§8.2 rows keep their numbers 1-15 as `RISK-01`..`RISK-15`) | S19.* | `RISK-08` |
| Screens | `SCR-<role>-<nn>`, role in `vol`, `req`, `rev`, `ops`, `pub` | S11.*, S12.* | `SCR-vol-03` |
| Acceptance criteria | `AC-<area>-<nn>` (Given / When / Then) | the part that specifies the feature | `AC-ledger-12` |
| Tests | `T-<layer>-<nn>`, layer in `unit`, `prop`, `fsm`, `policy`, `adv`, `inj`, `rtl`, `load`, `e2e`, `sim` | S18.* | `T-prop-04` |
| API operations | `op` ids in lowerCamelCase | S15.* | `createJob` |
| User-facing copy keys | `copy.<area>.<key>`, each with `fa` and `en` text and the marker `needs_human_and_legal_review` | S11.*, S12.* | `copy.privacy.pseudonymity_notice` |
| Metrics | `hamyar_<area>_<name>_<unit>` | S4.*, S13.* | `hamyar_ledger_invariant_violations_total` |
| Log events | `<area>.<event>` lowercase dotted, same names as domain events (0.9) | S4.* | `cell.leased` |
| Experiments | `EXP-<nn>`; growth mechanics keep `V1`..`V6` (FD§6.2) | S12.*, S13.* | `EXP-02` |
| Measurements that replace defaults | codes in 0.10 (`CAL`, `P1M`, `DEM`, `FND`, `CNS`, `SEC`, `TEC`, `OPS`, `CON`) | S16.* | `CAL` |

## 0.6 Technical decisions: numbers, time, IDs, hashing

### 0.6.1 Ledger numeric type [D]

**Decision: integer micro-credits.** One credit = 1,000,000 micro-credits (`ucr`).

| Item | Decision |
| --- | --- |
| Unit and scale | `ucr`; constant `credit.scale_ucr_per_credit` = 1,000,000, immutable (changing it is a data migration, never a configuration edit) |
| Database | signed 64-bit integer, column suffix `_ucr`; never float or decimal |
| JSON | amounts are base-10 integer strings (`"276000000"`) because JavaScript numbers are exact only to 2^53; field suffix `_ucr` |
| Ratios | v, λ, η, φ, g, s and every `ratio` parameter are fixed-point integers in ppm (1.0 = 1,000,000); decimals appear only at the display edge |
| Per-cell price | `p_ucr = 1,000,000 + v_ppm + lambda_ppm`. It equals p expressed in ppm because the credit scale equals the ppm scale; this identity is the reason for scale 10^6 [A] |
| Job escrow | `escrow_ucr = N * p_ucr` for N primary cells: integer times integer, no rounding |
| Components | primary pay `N * 1,000,000`; verification pool `N * v_ppm`; levy `N * lambda_ppm`; their sum is `escrow_ucr` exactly |
| Rounding | only where a ratio is measured: `v_ppm = ceil(10^6 * verification_cells / accepted_primary_cells)` (rounded up so the pool is never under-funded); `eta_ppm = floor(10^12 / p_ucr)`. Displayed balances round down, displayed prices round up |
| Donor earn | exactly 1,000,000 ucr per accepted cell of any kind (FD§4.3) |
| Whole-credit parameters | stored in ucr (a grant of 3 credits is 3,000,000) |
| Range | int64 holds about 9.2 x 10^12 credits; every invariant check uses exact integer equality with zero tolerance |

*Why not integer credits:* p = 1.15 forces job-level rounding (N = 10 gives 11.5 credits); rounding creates a systematic transfer between requester, donors and Reserve and makes the FD§4.2 identities approximate. *Why not decimals or floats:* not exact. *Why not a finer unit:* six decimal places of p are enough and keep every product inside int64 [A].

**Reproduction of the FD§3.3 example** (becomes `AC-ledger-01` and `T-unit-01`; inputs are the FD's illustrative values, not measurements):

| Step | Computation (integers) | Result |
| --- | --- | --- |
| Inputs | v_ppm = 100,000; lambda_ppm = 50,000; N = 240; Sara holds 300 credits | |
| Price per cell | 1,000,000 + 100,000 + 50,000 | 1,150,000 ucr = 1.15 |
| Escrow | 240 x 1,150,000 | 276,000,000 ucr = 276 credits; Sara keeps 24 |
| Verification pool | 240 x 100,000 = 24,000,000 ucr; `floor(pool / 10^6)` | 24 verification and rework cells |
| Levy | 240 x 50,000 | 12,000,000 ucr = 12 credits |
| Donor payout | (240 + 24) cells x 1,000,000 | 264,000,000 ucr = 264 credits |
| Closing identity | 264,000,000 + 12,000,000 | 276,000,000 = escrow; refund 0 |
| Round-trip efficiency | `floor(10^12 / 1,150,000)` | 869,565 ppm, displayed 0.870 (FD: about 0.87) |
| Admission | capacity = `floor(40 x 8 x 2 x 500,000 / 10^6)` = 320 cells; committed = 240 + 24 = 264 | 264 <= 320, admitted with a 2-day quote |
| Time value | 240 cells / 8 per day | 30 days for one account versus a 2-day window |

If the verification pool is not a whole number of cells, `floor` applies and the remainder stays in escrow and is refunded at settlement (S6.* owns the full rule; see `ISS-04`).

### 0.6.2 Time handling [D]

- **Storage:** UTC `timestamptz` only; no local time is stored. API: RFC 3339 with `Z` (`2026-11-11T09:30:00Z`). Durations are integer seconds (suffix `_s`); `_days` parameters mean exactly 86,400 s each, with no calendar arithmetic.
- **Day and month boundaries** for rate limits, the monthly mint cap and daily jobs are UTC calendar boundaries [A]; screens show the local-time equivalent next to any cap or reset.
- **Authority:** server time only. Client clocks are never trusted; `expires_at` of leases, nonces, quotes and lots is computed and stored server-side. Ledger order is the per-ledger sequence number `seq`, never a timestamp.
- **Lot expiry:** `expires_at = earned_at + credit.lifetime_days * 86,400 s`, evaluated with the parameter version in force at `earned_at` (changes are prospective only, FD Principle 5).
- **Display:** converted on the client. Locale `fa` defaults to the Jalali (Solar Hijri) calendar and Persian numerals as a user option; locale `en` defaults to Gregorian; detail views show both calendars (FD§10). Conversion uses the platform calendar support where present [V: support on the target phones] with a bundled arithmetic fallback. The server never stores, accepts or emits Jalali strings; exports use Gregorian ISO dates.
- **Time zone:** the device zone by default, overridable by an IANA zone chosen in settings, never inferred from an IP address (privacy). Offset and daylight-saving rules for any country come from the tz database and are not hardcoded [V].

### 0.6.3 Identifiers [D]

- Format: `<prefix>_<ulid>`: a 3-letter lowercase prefix, an underscore, a 26-character ULID in lowercase Crockford base32. Regex: `^[a-z]{3}_[0-9a-hjkmnp-tv-z]{26}$`. Examples: `mem_01j9z6x4k7q2m8v5t3r1w0c9ab`, `job_...`, `cel_...`.
- Generated server-side only, monotonic within a process; sortable by creation time; opaque to clients (never parsed for meaning). Prefixes are unique across the system (table in 0.7).
- The time part of a ULID is not a secret; it adds nothing beyond `created_at`. Identifiers of other members are never shown: public surfaces and provenance use `vol_` handles (0.6.4), not `mem_` ids. [D]
- Natural keys: `ParameterName` (0.10), `policy_rule_id` (`R1`..`R10`), `flag_key` (0.8.3), invariant ids. These are stable strings, not ULIDs.
- `request_id` uses the prefix `req_` and is not an entity.

### 0.6.4 Hashing, randomness and token choices [D][A]

| Purpose | Choice | Notes |
| --- | --- | --- |
| Content hash (inputs, outputs, terms copies) | SHA-256 over the raw bytes, lowercase hex, written `sha256:<hex>` | Terms copies are stored as bytes plus hash |
| Structured-data hash (manifests, request bodies) | SHA-256 over RFC 8785 canonical JSON | One canonicalizer for the whole system |
| Ledger tamper evidence | `entry_hash = SHA-256(prev_hash \|\| canonical(entry))` per ledger, with a daily published checkpoint hash | Detects edits; does not replace access control (S6.*, S10.*) |
| Provenance volunteer handle | `vol_<32 hex>` = first 128 bits of `HMAC-SHA-256(key = secret.volunteer_handle_key[version], data = member_id)` | Requesters never see it; rotating the key unlinks old handles by design |
| Session and lease tokens, nonces | 256-bit CSPRNG values, stored only as SHA-256 hashes; lease nonce 128 bits (`lease.nonce_bytes` = 16) | High-entropy secrets need no slow hash |
| Member authentication | Public-key keypair generated on the device; server stores public keys (`MemberKey`); signature scheme Ed25519 [A] | Detailed in S10.*; there are no passwords |
| Admin authentication | WebAuthn passkeys per `AdminUser`; no shared password, separate origin and session store [A] | Detailed in S10.* |
| Low-entropy secrets | Not used. If a future feature needs one, use Argon2id with parameters held in configuration | |
| IP addresses | Raw IPs are not stored; rate-limit counters use `HMAC-SHA-256(secret.ip_hash_key[version], ip)` with retention `retention.ip_hash_ttl_days` | Safety principle for members in Iran (FD Principle 8) |
| Randomness | OS CSPRNG only | |

## 0.7 Entities, ID prefixes and table naming

**Naming rules** [D]

- Entity names are `UpperCamelCase`, singular, exactly as below. Tables are `snake_case` plural of the entity name. Columns are singular `snake_case`.
- Every table has `id` (text primary key, format 0.6.3), `created_at` (timestamptz) and, if mutable, `updated_at` and an integer `row_version` for optimistic concurrency. `LedgerEntry` and every other append-only table has no `updated_at` and no delete path.
- Foreign keys are `<entity_snake>_id` (`member_id`, `template_version_id`). Timestamps end `_at`, durations `_s`, amounts `_ucr`, ratios `_ppm`, content hashes `_hash`, booleans start `is_` or `has_`, enums are text columns with a `CHECK` against the enum names in 0.8.
- No soft-delete flag on ledger, registry, policy, parameter or change-log tables; corrections are new rows (`reversal`, new version).
- No table stores a raw IP address, an e-mail address in clear text, a provider credential, a session of a provider, or the text of a volunteer's chat page (FD Principle 3 and 8). [D]

**Retention classes** (the column below; S10.* sets the numbers as `retention.*` parameters) [A]

| Class | Meaning |
| --- | --- |
| `permanent` | Never deleted. Contains no personal data by construction |
| `member_bound` | Kept while the member is not `closed`; on closure the row is deleted or reduced to an opaque `mem_` id |
| `job_bound` | Payload fields purged `retention.job_payload_days` after the job reaches a terminal state; hashes and manifests stay |
| `moderation` | Kept `retention.moderation_days` after resolution, then reduced to counts |
| `short` | Days (`retention.session_days`, `retention.ip_hash_ttl_days`) |
| `ops` | Operational telemetry, `retention.ops_log_days` |

**Entities named by the prompt (scope B)**

| Entity | Table | Prefix | Retention | Role in one line |
| --- | --- | --- | --- | --- |
| `Member` | `members` | `mem_` | `member_bound` | Pseudonymous identity; holds `status` and `trust_tier` |
| `Device` | `devices` | `dev_` | `short` | Keyed-hash device record for rate limits and linking; no fingerprinting beyond what S10.* lists |
| `Invite` | `invites` | `inv_` | `member_bound` | Vouched invitation; edges form the invite tree |
| `Template` | `templates` | `tpl_` | `permanent` | Stable identity of a reviewed prompt pattern; points at its active version |
| `TemplateVersion` | `template_versions` | `tpv_` | `permanent` | Immutable once approved; carries review status |
| `Job` | `jobs` | `job_` | `job_bound` | A requester's request, or a Commons job, split into cells |
| `Cell` | `cells` | `cel_` | `job_bound` | One prompt-and-response unit inside the envelope; unit of credit |
| `Lease` | `leases` | `lse_` | `job_bound` | Time-boxed hold of a cell by one member, bound to a nonce |
| `Submission` | `submissions` | `sub_` | `job_bound` | One pasted-back result for one lease |
| `VerificationRecord` | `verification_records` | `vrf_` | `job_bound` | Outcome of one verification method on one submission |
| `GoldCell` | `gold_cells` | `gld_` | `permanent` | Known-answer cell in the hidden library; answers are access-restricted |
| `Audit` | `audits` | `aud_` | `job_bound` | Sampled re-execution of a cell, comparator result, third execution |
| `LedgerAccount` | `ledger_accounts` | `lac_` | `permanent` | One account of type `member`, `escrow`, `reserve`, `issuance` or `retired` |
| `LedgerEntry` | `ledger_entries` | `lge_` | `permanent` | One balanced pair of legs, append-only, hash-chained |
| `Escrow` | `escrows` | `esc_` | `permanent` | Per job or reservation hold; bound to one `escrow` account |
| `Reserve` | `reserves` | `rsv_` | `permanent` | Singleton: the public Commons Reserve; bound to the `reserve` account; holds ceiling state |
| `Policy` | `policies` | `pol_` | `permanent` | Named policy profile (FD§5.4 default profile) |
| `PolicyVersion` | `policy_versions` | `plv_` | `permanent` | Immutable rule set plus allowlist; stamped on jobs at admission |
| `ServiceRegistryEntry` | `service_registry_entries` | `svc_` | `permanent` | A service with review state, adapter capabilities and dated flags |
| `TermsCopy` | `terms_copies` | `tcp_` | `permanent` | Saved copy of a service's terms: bytes, hash, source reference, capture date |
| `FlagAnswer` | `flag_answers` | `fla_` | `permanent` | One dated yes / no / unknown answer for one flag of one entry |
| `Report` | `reports` | `rpt_` | `moderation` | Abuse or content report from a volunteer or requester |
| `Appeal` | `appeals` | `apl_` | `moderation` | Challenge to a rejection, ban or report outcome |
| `Reservation` | `reservations` | `rsn_` | `job_bound` | Capacity booking for a future date with escrow at booking |
| `Team` | `teams` | `tem_` | `member_bound` | Self-created opt-in group |
| `Badge` | `badges` | `bdg_` | `permanent` | Badge definition (criteria in terms of verified cells only) |
| `ChangeLogEntry` | `change_log_entries` | `chg_` | `permanent` | Public record of a parameter, policy, template or service change |
| `LaunchGateItem` | `launch_gate_items` | `lgi_` | `permanent` | One checklist line of G0..G5 with evidence and sign-offs |

**Entities added by this spec** [A] (each is required by something in the prompt; reported as convention additions)

| Entity | Table | Prefix | Retention | Why it exists |
| --- | --- | --- | --- | --- |
| `MemberKey` | `member_keys` | `mky_` | `member_bound` | Public keys of a member; supports rotation and device linking (scope A) |
| `Session` | `sessions` | `ses_` | `short` | Member or admin session (hash of token only) |
| `AdminUser` | `admin_users` | `adm_` | `permanent` | Operator or Reviewer principal, separate from `Member` (scope A) |
| `AdminCredential` | `admin_credentials` | `acr_` | `permanent` | Passkey credential of an `AdminUser` |
| `AdminAction` | `admin_actions` | `act_` | `permanent` | Log of every operator and reviewer action. Named so it does not collide with the sampled `Audit` |
| `Rule` | `rules` | `rul_` | `permanent` | One row per policy rule `R1`..`R10` inside a `PolicyVersion` (rules are data, scope D) |
| `Parameter` | `parameters` | `prm_` | `permanent` | Definition of a configuration parameter (0.10) |
| `ParameterVersion` | `parameter_versions` | `pmv_` | `permanent` | One immutable value with `effective_from` |
| `KillSwitch` | `kill_switches` | `ksw_` | `permanent` | State history of each kill switch (scope F) |
| `FeatureFlag` | `feature_flags` | `ffl_` | `permanent` | Feature flag including growth flags `V1`..`V6` |
| `Upload` | `uploads` | `upl_` | `job_bound` | Requester data file before it is split into cells |
| `Glossary` | `glossaries` | `gls_` | `job_bound` | Shared glossary for translation jobs |
| `Deliverable` | `deliverables` | `dlv_` | `job_bound` | Assembled output of a job |
| `Manifest` | `manifests` | `mfs_` | `job_bound` | Provenance manifest of a deliverable (FD§5.6) |
| `OptIn` | `opt_ins` | `opt_` | `member_bound` | A volunteer's purpose, sensitivity, license, service and topic opt-ins |
| `TopicCategory` | `topic_categories` | `top_` | `permanent` | Data-defined topic categories for opt-in (R8) |
| `CreditLot` | `credit_lots` | `lot_` | `permanent` | A dated, expiring portion of a member's credit; enables oldest-first spending |
| `LedgerTransaction` | `ledger_transactions` | `txn_` | `permanent` | Atomic group of entries with a `txn_kind` (0.8.5) |
| `Experiment` | `experiments` | `exp_` | `permanent` | An arm configuration, including the accelerated-expiry arm |
| `ExperimentAssignment` | `experiment_assignments` | `asg_` | `permanent` | Logged, randomized assignment (scope G) |
| `PreRegistration` | `pre_registrations` | `prr_` | `permanent` | Thresholds and decision rules recorded before launch, then locked |
| `Event` | `events` | `evt_` | `ops` | Analytics event without personal data |
| `MetricSnapshot` | `metric_snapshots` | `mts_` | `permanent` | Aggregated published metric (v, η, claim ratio, ...) |
| `CalibrationRecord` | `calibration_records` | `cal_` | `permanent` | Phase 0 calibration observation |
| `Referral` | `referrals` | `ref_` | `member_bound` | Referral link and its two-sided bonus state |
| `WaitlistEntry` | `waitlist_entries` | `wlt_` | `job_bound` | Admission waitlist position |
| `BadgeAward` | `badge_awards` | `baw_` | `member_bound` | A badge held by a member |
| `InvariantCheck` | `invariant_checks` | `ivc_` | `ops` | Result of one run of a ledger invariant |
| `Alarm` | `alarms` | `alm_` | `ops` | A raised alarm and its acknowledgement |

Every prefix above is unique and exactly three letters; `req_` (request ids) is the only other prefix in use. [D]

## 0.8 Enumerations

Stored values are exactly the values in the first column, case-sensitive. A new value requires a convention edit (0.1). [D]

### 0.8.1 Purpose, license, sensitivity, service requirement (FD§5.3)

| Enum | Value | Meaning | Status in Phases 1-2 (FD§5.3) |
| --- | --- | --- | --- |
| `purpose` | `P0` | Personal, study or internal non-commercial use; output stays with the requester | allowed, default |
| `purpose` | `P1` | Open publication under an open license; includes all Commons jobs | allowed, default |
| `purpose` | `P2` | Commercial or professional use of outputs, no training | locked; unlocks per service after its terms are verified [V] |
| `purpose` | `P3` | Training, fine-tuning, distillation or benchmark creation | locked; `M2` or a service whose `training_use_of_output` is `yes`; `S0` only |
| `license` | `L0` | Requester only, no publication; volunteers waive claims | pairs with `P0` |
| `license` | `L1` | Public-domain dedication (for example CC0) | pairs with `P1` |
| `license` | `L2` | Open license with attribution (for example CC BY) | pairs with `P1` |
| `license` | `L3` | Requester-defined commercial terms | pairs with `P2` only |
| `sensitivity` | `S0` | Public, public-domain, openly licensed, or written for publication | accepted |
| `sensitivity` | `S1` | Private but non-sensitive; no personal data of identifiable people; the requester accepts that a stranger reads it | accepted |
| `sensitivity` | `S2` | Personal data of others, confidential business material, unpublished third-party work | rejected |
| `sensitivity` | `S3` | Special-category or dangerous (health, privileged, minors, credentials, financial identifiers, anything that could identify or endanger a person) | never accepted |
| `service_requirement` | `M0` | Any approved general chat service; the volunteer chooses; the service is recorded | default |
| `service_requirement` | `M1` | Pinned approved service(s) named by the requester | allowed |
| `service_requirement` | `M2` | Open-weight model with a checked license (hosted or local) | required for `P3` unless a service permits training use in writing [V] |

The allowlist of permitted combinations is data in `PolicyVersion` (S7.*); this table only names the axes. Output pairing of `L*` with `P*` is the starting allowlist, not a separate rule. [D]

### 0.8.2 Roles and principals [D]

| Enum | Value | Notes |
| --- | --- | --- |
| `role` | `donor`, `requester`, `reviewer`, `operator` | FD§3.1. One person may hold several |
| `principal_type` | `anonymous`, `member`, `admin`, `system` | `member` holds `donor` and `requester` capabilities (no separate accounts); `admin` is an `AdminUser` holding `reviewer` and/or `operator`; `system` is a background job |
| `auth_scheme` | `none`, `member`, `admin` | 0.11.4. A token of one scheme is never valid on endpoints of another |

Executing human-review cells (FD§6.4 channel 2) is a member activity on `cell_kind` = `review`, not the `reviewer` role; the `reviewer` role is the admin-side role for templates, services, policy, appeals and audits [A]. The permission matrix is S10.*. Permission names: `perm.<area>.<action>`.

### 0.8.3 Flag answers and Service Registry flag keys [D]

`flag_answer` = `yes` | `no` | `unknown`. **`unknown` is evaluated as `no` everywhere** (FD§5.3). Every gating flag is phrased as a permission, so `yes` always means the terms permit it and `unknown`-as-`no` is always the safe direction (`ISS-02`). A `FlagAnswer` is dated, carries the reviewer, an optional `region` (ISO 3166-1 alpha-2) and points at the `TermsCopy` it was read from.

| `flag_key` | Kind | `yes` means the saved terms permit... | FD source |
| --- | --- | --- | --- |
| `third_party_task_use` | gate | using a personal or free account to perform tasks for other people | FD§8.3 G0(a) |
| `access_pooling_or_crediting` | gate | pooling, sharing or crediting of access | G0(b) |
| `human_copy_paste_use` | gate | a human copying a prompt, pressing Send and copying the answer out | G0(c) |
| `prefilled_link_use` | gate | opening the service with a prefilled prompt from a link | G0(c) |
| `regional_availability` | gate | use by people in the stated `region` (recorded per region) | G0(d) |
| `commercial_use_of_output` | gate | commercial use of outputs on the free tier (`R5`) | G0(e) |
| `training_use_of_output` | gate | using outputs to train or develop other models (`R6`) | G0(f) |
| `open_publication_of_output` | gate | publishing outputs openly (`R7`) | G0(g) |
| `prohibited_content_compatible` | gate | the service's usage policy is compatible with the content Hamyar accepts (FD§5.4 R3) | G0(i) |
| `info.provider_trains_on_chats` | info | (`yes` = it does; informs volunteer advice, never gates) | G0(h) |
| `info.memory_or_connectors_risk` | info | (`yes` = account memory or connectors could leak content) | G0(h) |
| `info.allowance_may_change` | info | (`yes` = the free allowance may change without notice) | G0(j) |
| `info.written_permission` | info | (`yes` = written permission for this use was obtained) | G0(k) |

A service reaches `approved` only if `third_party_task_use` and `prohibited_content_compatible` are `yes` with a saved `TermsCopy` (FD§5.3); further per-purpose conditions are rules `R5`..`R7`. [D]

**Adapter capability fields** of `ServiceRegistryEntry` (no provider is hardcoded; every value is entered by a reviewer [V]): `adapter.supports_prefill` (bool), `adapter.prefill_url_template` (string with `{prompt}` placeholder), `adapter.max_url_chars` (int), `adapter.copy_only` (bool; true when prefill is not supported or `prefilled_link_use` is not `yes`), `adapter.clean_chat_hint_key` (copy key).

### 0.8.4 Policy rules and reason codes [D]

| `policy_rule_id` | Slug | FD§5.4 meaning |
| --- | --- | --- |
| `R1` | `metadata_missing_or_inconsistent` | Missing or inconsistent declarations |
| `R2` | `sensitivity_not_accepted` | `S2` or `S3` |
| `R3` | `prohibited_content` | Prohibited content, or a task asking more than copy, Send, return text |
| `R4` | `template_required` | Prompts only from reviewed templates |
| `R5` | `commercial_needs_flag` | `P2` needs `commercial_use_of_output` = `yes` |
| `R6` | `training_needs_m2_or_flag` | `P3` needs `M2` or `training_use_of_output` = `yes`; `S0` only |
| `R7` | `license_exceeds_service_flags` | License may not exceed the service flags |
| `R8` | `volunteer_optin_mismatch` | Cell shown only to volunteers whose opt-ins cover it |
| `R9` | `policy_version_stale` | Policy stamped at admission, re-checked at acceptance |
| `R10` | `loosen_without_changelog` | Tighten at once; loosen only with a public change-log entry |

Reject reason codes shown to requesters: `policy.<policy_rule_id>.<slug>` (for example `policy.R2.sensitivity_not_accepted`). Cell rejection reasons shown to volunteers (seed list, S8.* and S9.* may extend through a convention gap): `reject.schema_invalid`, `reject.refusal_pattern`, `reject.length_out_of_bounds`, `reject.language_mismatch`, `reject.test_failed`, `reject.gold_mismatch`, `reject.audit_mismatch`, `reject.duplicate_of_other_output`, `reject.timing_anomaly`, `reject.forbidden_content`, `reject.nonce_invalid`, `reject.lease_expired`, `reject.size_exceeded`, `reject.policy_changed`.

### 0.8.5 Ledger enums [D]

**`ledger_account_type`**

| Type | Count | Constraint | Meaning |
| --- | --- | --- | --- |
| `member` | one per `Member` | balance >= 0 | Holds `CreditLot`s |
| `escrow` | one per `Escrow` | balance >= 0; zero when closed | Held credit of a job or reservation |
| `reserve` | one (the `Reserve`) | balance >= 0 | Commons Reserve |
| `issuance` | one | balance <= 0; equals minus cumulative mint | Source of minted credit |
| `retired` | one | balance >= 0; equals cumulative retired | Sink of retired credit |

**`ledger_entry_type`** (one entry = one balanced pair `debit_account -> credit_account`, amount > 0 ucr)

| Type | From -> To | Lot effect | Meaning |
| --- | --- | --- | --- |
| `mint` | `issuance` -> `member` | creates a lot | Accepted Commons cell (FD§4.2) |
| `grant` | `reserve` -> `member` | creates a lot with `grant.starter_lifetime_days` (starter) or `credit.lifetime_days` (referral) | Starter grant and referral bonus (`ISS-06`) |
| `escrow_hold` | `member` -> `escrow` | consumes lots oldest-first | Job admission or reservation booking |
| `transfer` | `escrow` -> `member` | creates a lot | Donor earns 1 credit for one accepted cell of a member job, paid at acceptance (`ISS-09`) |
| `escrow_release` | `escrow` -> `escrow` | none | Reservation escrow moves into the activated job's escrow |
| `levy` | `escrow` -> `reserve` | none | λ share of a job, paid at settlement |
| `refund` | `escrow` -> `member` | restores consumed lots with their original expiry (`ISS-07`) | Unspent escrow after settlement or cancel |
| `expire` | `member` -> `reserve` | consumes the expired lot | Expired credit to the Reserve (FD§4.5) |
| `retire` | `reserve` -> `retired` | none | Reserve excess above its ceiling leaves existence (FD§4.2) |
| `reserve_donation` | `member` -> `reserve` | consumes lots oldest-first | A member (a founder) voluntarily funds the Reserve (`ISS-08`) |
| `reversal` | the mirror of the original entry | mirrors | Correction of an earlier entry; two-operator approval; the original is never edited |

**`ledger_txn_kind`** (an atomic group of entries with one `LedgerTransaction`): `mint`, `grant`, `hold`, `payout`, `settle`, `cancel`, `reservation_activate`, `expire`, `retire`, `reserve_donation`, `reversal`. `settle` closes a job: its entries are `levy`, `refund` and any final `transfer`, and it leaves the escrow account at exactly zero. `payout` groups the `transfer` for one accepted cell. [D]

### 0.8.6 Cell, verification and job-type enums [D]

| Enum | Values |
| --- | --- |
| `cell_kind` | `primary`, `gold`, `audit`, `third`, `review`, `rework` (`rework` is defined in `ISS-05`) |
| `verification_method` | `auto_check`, `gold`, `audit_second`, `audit_third`, `human_review`, `blanket_redundancy` |
| `verification_outcome` | `pending`, `pass`, `fail`, `inconclusive` |
| `job_type` (initial templates, FD§2 and prompt E; extensible as data) | `translation_glossary`, `classify_extract`, `summarize_schema`, `code_change_tests`, `format_convert_validator`, `human_review` |
| `size_class` | `standard` (the only value in Phases 1-2) |
| `deadline_class` | `standard` (multiplier fixed at 1.0 in Phase 1, FD§4.8) |
| `member_status` | `active`, `suspended`, `banned`, `closed` (orthogonal to `trust_tier`, 0.9.4) |
| `change_class` (R10) | `tighten`, `loosen`, `neutral` |
| `locale` / `digits` / `calendar` | `fa`, `en` / `latin`, `persian` / `jalali`, `gregorian` |

## 0.9 State machines: state names and event names

This section fixes names only. Guards, side effects, concurrency and the ledger postings belong to S5.*, S6.*, S7.*, S8.*, S9.* (the owning part is named per machine). [D]

### 0.9.1 Naming rules [D]

- States are `snake_case` adjectives or past participles, scoped to their machine (two machines may both have `expired` or `cancelled`; a state is always written with its machine, for example `Cell.expired`). `(T)` marks a terminal state.
- Events are `<entity>.<past_participle>` in lowercase, for example `cell.lease_expired`. Every state change emits exactly one event with the name shown on the transition; the event is stored in the outbox in the same database transaction (S4.*), logged under the same name (0.5) and carries `event_version`, `occurred_at`, `actor` (`principal_type` plus opaque id) and the policy and parameter versions in force.
- An event that is rejected by a guard changes nothing and is not emitted; the rejection is an API error (0.11.3), not an event.
- Transition notation: `from --event--> to`; `*` means any non-terminal state.

### 0.9.2 Job (owner S5.*, S6.*)

States: `draft`, `screening`, `rejected` (T), `quoted`, `quote_expired` (T), `waitlisted`, `admitted`, `running`, `suspended`, `assembling`, `settling`, `completed` (T), `cancelling`, `cancelled` (T), `failed` (T).

```
(none)       --job.created-->              draft
draft        --job.submitted-->            screening      wizard complete: template, data, declarations
screening    --job.policy_rejected-->      rejected       reasons use policy.<rule>.<slug>
screening    --job.policy_passed-->        quoted         policy version stamped; price and window quoted
quoted       --job.quote_expired-->        quote_expired
quoted       --job.waitlisted-->           waitlisted     capacity cannot honor the window now
waitlisted   --job.waitlist_released-->    quoted         re-quoted
waitlisted   --job.waitlist_expired-->     cancelled
quoted       --job.escrow_confirmed-->     admitted       escrow_hold posted; cells created and queued
admitted     --job.started-->              running        first cell leased
admitted|running --job.paused-->           suspended      kill switch, template or service pause, policy tightening
suspended    --job.resumed-->              admitted|running (the state it left)
running      --job.all_cells_accepted-->   assembling
assembling   --job.assembled-->            settling
admitted|running|suspended --job.stop_requested--> settling   closure_reason: policy_stopped, service_revoked, template_retired, operator_killed, overrun_timeout
settling     --job.settled-->              completed      all primary cells accepted
settling     --job.settled_partial-->      failed         not all accepted; refunds and payouts posted
admitted|running|suspended --job.cancel_requested--> cancelling
waitlisted|draft|quoted --job.cancel_requested--> cancelled
cancelling   --job.cancel_settled-->       cancelled      unstarted cells refunded, in-flight cells drained
```

### 0.9.3 Cell, Lease, Submission (owner S5.*, S8.*, S9.*)

Cell states (extends FD§3.4): `queued`, `leased`, `submitted`, `flagged_for_audit`, `accepted` (T), `rejected`, `expired`, `suspended`, `cancelled` (T), `voided` (T), `exhausted` (T), `overturned` (T). `rejected` and `expired` are attempt outcomes that requeue at once (FD§3.4), so a cell is only briefly in them. A `Cell` row persists across attempts and carries `attempt` (starts at 1, limit `cell.max_attempts`).

```
(none)            --cell.created-->            queued
queued            --cell.leased-->             leased          creates a Lease
leased            --cell.submitted-->          submitted       paste-back received
leased            --cell.lease_expired-->      expired
leased            --cell.declined-->           queued          decline or release, no penalty (FD§5.5)
submitted         --cell.checks_passed-->      accepted        not selected for audit
submitted         --cell.flagged_for_audit-->  flagged_for_audit   sampled, anomalous, or blanket-redundancy pending
submitted         --cell.checks_failed-->      rejected
flagged_for_audit --cell.audit_passed-->       accepted
flagged_for_audit --cell.audit_failed-->       rejected
rejected|expired  --cell.requeued-->           queued          attempt + 1
rejected|expired  --cell.attempts_exhausted--> exhausted
queued|leased     --cell.paused-->             suspended       a leased cell's lease is revoked first
suspended         --cell.resumed-->            queued
*                 --cell.cancelled-->          cancelled       job cancelled; lease revoked
*                 --cell.voided-->             voided          service revoked, policy stop, integrity finding
accepted          --cell.overturned-->         overturned      appeal or fraud finding; ledger reversal; a rework cell is created
```

Lease states: `active`, `submitted`, `expired`, `released`, `revoked`. Events: `lease.issued` (none -> `active`), `lease.submission_received` (`active` -> `submitted`), `lease.expired` (`active` -> `expired`), `lease.released` (`active` -> `released`), `lease.revoked` (`active` -> `revoked`).

Submission states: `received`, `schema_failed` (T), `checks_failed` (T), `checks_passed`, `quarantined`, `accepted` (T), `rejected` (T). Events: `submission.received`, `submission.schema_failed`, `submission.checks_passed`, `submission.checks_failed`, `submission.quarantined` (output with links, code to run or requests for action; withheld from results, FD§5.5), `submission.accepted`, `submission.rejected`, `submission.released_from_quarantine`. A replayed submission with the same lease and nonce returns the stored outcome and emits nothing.

### 0.9.4 Member trust tier and status (owner S10.*, S8.*)

Trust tier states: `new`, `established`, `trusted`, `restricted`. Status (separate column, 0.8.6): `active`, `suspended`, `banned`, `closed`. Tier changes follow the parameters `trust.*` (0.10).

```
(none)       --member.created-->           new            (status active)
new          --member.tier_promoted-->     established
established  --member.tier_promoted-->     trusted
trusted      --member.tier_demoted-->      established
established  --member.tier_demoted-->      new
new|established|trusted --member.restricted--> restricted   anomaly or gold failures; sampling rises, caps fall
restricted   --member.restriction_lifted-->  the tier recorded as tier_before_restriction
status: active --member.suspended--> suspended --member.reinstated--> active
status: active|suspended --member.banned--> banned   (appealable)
status: active|suspended --member.closed--> closed   (member-initiated or inactivity)
```

Other member events: `member.key_rotated`, `member.device_linked`, `member.recovered`, `member.optin_changed`.

### 0.9.5 Template review (owner S8.*)

Applies to `TemplateVersion.review_status`. States: `draft`, `in_review`, `awaiting_second_review`, `changes_requested`, `approved`, `rejected` (T), `paused`, `retired` (T). A new `Template` needs `template.min_reviewers_new` approvals from distinct reviewers who are not the author (second-reviewer rule, FD§5.7 failure mode 10); a new version of an approved template needs `template.min_reviewers_edit`.

```
(none)                  --template.version_created-->     draft
draft|changes_requested --template.review_requested-->    in_review
in_review               --template.first_approved-->      awaiting_second_review   (or approved when only one approval is required)
awaiting_second_review  --template.second_approved-->     approved
in_review|awaiting_second_review --template.changes_requested--> changes_requested
in_review|awaiting_second_review --template.rejected-->  rejected
approved                --template.paused-->              paused         kill switch (S14.*)
paused                  --template.resumed-->             approved
approved|paused         --template.retired-->             retired        includes superseded by a newer version
```

### 0.9.6 Service review (owner S7.*)

States: `unreviewed` (initial for every service; counts as no), `in_review`, `approved`, `review_due`, `rejected`, `suspended`, `revoked`. Only `approved` allows new jobs. `review_due` blocks new jobs at once and lets in-flight cells continue for `service.review_grace_days`.

```
(none)       --service.created-->         unreviewed
unreviewed|rejected|review_due|revoked --service.review_started--> in_review
in_review    --service.approved-->        approved       guard: gate flags yes, TermsCopy saved, reviewer recorded
in_review    --service.rejected-->        rejected
approved     --service.review_due-->      review_due     timer: service.review_max_age_days
review_due   --service.review_lapsed-->   suspended      timer: service.review_grace_days
approved|review_due --service.suspended--> suspended     kill switch
suspended    --service.resumed-->         approved       only when the cause was a kill switch
approved|review_due|suspended --service.revoked--> revoked   in-flight cells handled per S7.*
```

### 0.9.7 Appeal (owner S10.*, S8.*)

`appeal_kind`: `cell_rejection`, `member_suspension`, `member_ban`, `job_rejection`, `template_rejection`, `report_outcome`. States: `filed`, `assigned`, `in_review`, `awaiting_second_review`, `upheld` (T), `overturned` (T), `withdrawn` (T). Filing is allowed only within `appeal.window_days` of the decision; a late filing is an API error, not a state.

```
(none)       --appeal.filed-->                    filed
filed        --appeal.assigned-->                 assigned       reviewer must not be the original decider
assigned     --appeal.review_started-->           in_review
assigned     --appeal.reassigned-->               assigned       conflict of interest
in_review    --appeal.second_review_requested--> awaiting_second_review   bans and template rejections
in_review|awaiting_second_review --appeal.upheld-->      upheld
in_review|awaiting_second_review --appeal.overturned-->  overturned
filed|assigned|in_review --appeal.withdrawn-->    withdrawn
```

### 0.9.8 Smaller machines [D]

| Machine | States | Events |
| --- | --- | --- |
| `Audit` (S8.*) | `pending`, `second_executed`, `matched` (T), `mismatched`, `third_pending`, `resolved` (T), `cancelled` (T) | `audit.created`, `audit.second_submitted`, `audit.matched`, `audit.mismatched`, `audit.third_requested`, `audit.third_submitted`, `audit.resolved`, `audit.cancelled` |
| `Escrow` (S6.*) | `open`, `settling`, `closed` (T) | `escrow.opened`, `escrow.settling_started`, `escrow.closed` |
| `Reservation` (S6.*) | `held`, `activated` (T), `cancelled` (T), `expired` (T) | `reservation.held`, `reservation.activated`, `reservation.cancelled`, `reservation.expired` |
| `Report` (S10.*) | `open`, `triaged`, `actioned` (T), `dismissed` (T) | `report.filed`, `report.triaged`, `report.actioned`, `report.dismissed` |
| `LaunchGateItem` (S14.*) | `open`, `evidence_attached`, `signed_off`, `reopened` | `gate.evidence_attached`, `gate.signed_off`, `gate.reopened` |
| Kill switch (S14.*) | `released`, `engaged` | `killswitch.engaged`, `killswitch.released` |
| Ledger and configuration events | not machines | `ledger.entry_committed`, `ledger.invariants_passed`, `ledger.invariant_violated`, `parameter.changed`, `policy.version_published`, `changelog.entry_published`, `launch.members_may_join_changed` |

## 0.10 Configuration parameters

### 0.10.1 Naming scheme [D]

- A parameter name is `area.name` or `area.group.name`, lowercase `snake_case` segments: regex `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){1,2}$`. The name is the primary key and never changes; a rename is a new parameter plus retirement of the old one.
- Unit suffixes: `_s` seconds, `_days` days (86,400 s), `_chars`, `_bytes`, `_credits` (whole credits, stored as ucr), `_per_day`, `_per_hour`, `_rpm`. A ratio has no suffix (the type says so) unless the FD symbol is part of the name.
- FD symbols map to names exactly: E -> `credit.lifetime_days`; K -> `credit.member_cap_credits`; v -> measured, published as `MetricSnapshot` (prior `price.v_prior`); λ -> `price.levy_lambda`; g -> `verify.gold_rate_g`; s -> `verify.audit_rate_s`; φ -> `admission.phi`; G -> `grant.starter_credits`; mint cap -> `mint.monthly_cap_credits`; lease timeout -> `lease.timeout_s`; cell envelope -> `cell.envelope.*`.
- Not parameters: feature flags `ff.<area>.<name>` (entity `FeatureFlag`, default off), kill switches `kill.<scope>` (entity `KillSwitch`), and secrets `secret.<name>` (named in S10.*, never stored in the parameter table, never exposed by an API).

### 0.10.2 Types [D]

`int`; `ratio` (integer ppm, 0.6.1; written as a decimal in this table for readability); `credits` (whole credits stored as ucr); `duration_s`; `days`; `bool`; `enum`; `string`; `json`. Constants (`mutable` = false, measurement code `CON`) cannot be edited by the parameter editor.

### 0.10.3 Parameter record [D]

| Field | Type | Rule |
| --- | --- | --- |
| `name` | text | Primary key, 0.10.1 |
| `type`, `unit` | enum, text | 0.10.2 |
| `validation` | json | `min`, `max`, `enum`, `exclusive_bounds`, and named cross-parameter constraints (below); evaluated on write; a violation is `VALIDATION_FAILED` |
| `default` | per type | The `initial configurable default`; never edited after publication |
| `value`, `version` | per type, int | Current value; `version` increases by 1 per accepted change; every version is an immutable `ParameterVersion` |
| `effective_from` | timestamptz | Changes are prospective: `effective_from >= now + notice_days` unless `change_class` = `tighten` (R10: tighten at once) |
| `tighten_direction` | enum `up`, `down`, `none` | Which direction of change counts as tightening (for example `verify.audit_rate_s` is `up`, `admission.phi` is `down`) |
| `notice_days` | int | Advance notice for `loosen` and `neutral` changes; default `change.notice_days_default` |
| `owner` | enum | `operator`, `reviewer` or `founders` (area table 0.10.5); only the owner role may edit; a `loosen` change also needs a second `operator` approval [A] |
| `calibration_source` | enum | Measurement code from 0.10.4 plus a free-text pointer to the replacing measurement |
| `public` | bool | Published on the parameter page and change log (default true except `security.*`) |
| `introduced_in` | text | `S<n>.<m>` of the part that defined it |

Every accepted change writes one `ParameterVersion`, one `ChangeLogEntry` (public when `public`), one `AdminAction` and the event `parameter.changed`. Mutable resources use `ETag` and `If-Match` (0.11.7). A job, lot or lease keeps the parameter version it was created under where the spec says so (lot expiry, policy stamp, quote). [D]

**Named cross-parameter constraints** (checked on every write): `C1` `0 < admission.phi < 1`; `C2` `verify.audit_rate_floor <= verify.audit_rate_s <= verify.audit_rate_max`, and the same for gold (`verify.gold_rate_floor`, `verify.gold_rate_g`, `verify.gold_rate_max`); `C3` `lease.timeout_s >= cell.envelope.expected_time_s`; `C4` `credit.lifetime_days_accelerated <= credit.lifetime_days` and `grant.starter_lifetime_days <= credit.lifetime_days`; `C5` `reserve.ceiling_credits >= grant.starter_credits`; `C6` `0 <= price.levy_lambda < 1` and `price.v_prior <= price.v_cap`; `C7` `admission.min_window_s <= admission.max_window_days * 86400`; `C8` warning only: `credit.member_cap_credits >= admission.max_job_cells * (1 + price.v_prior + price.levy_lambda)`, because a member who cannot hold the price of a maximum job can never request one.

### 0.10.4 Measurement codes (what replaces a default) [D]

| Code | Measurement | Source |
| --- | --- | --- |
| `CAL` | Phase 0 calibration on the founders' own accounts: cells per day per service, seconds per cell, refusal and failure rates, copy-paste error rate | FD§8.3 G3, FD§9 Phase 0; stored as `CalibrationRecord` |
| `P1M` | A Phase 1 pilot measure | FD§9 Phase 1 list |
| `DEM` | Demand check: interviews about real job sizes, splittability, accepted window | FD§8.3 G5 |
| `FND` | A founders' decision recorded in a `PreRegistration` before day 1 | FD§9 Phase 1 |
| `CNS` | Counsel's answer in the operator's jurisdiction [V] | FD§8.3 G0 |
| `SEC` | The G1 threat-model decision | FD§8.3 G1 |
| `TEC` | Feasibility measurement on real phones and desktops | FD§8.3 G2 |
| `OPS` | Operating experience: alerts, incidents, capacity dashboard | S4.*, S13.* |
| `CON` | Constant: no measurement, changed only by a spec change | |

### 0.10.5 Areas, owners and defining parts [D]

| Area | Owner role | Defining part |
| --- | --- | --- |
| `credit`, `price`, `grant`, `reserve`, `mint`, `inflation`, `ledger`, `job` | `operator` | S6.* |
| `admission`, `reservation` | `operator` | S6.* |
| `verify`, `lease`, `cell`, `trust` | `operator` | S8.*, S9.* |
| `policy`, `screen`, `service`, `template`, `optin`, `appeal`, `report` | `reviewer` | S7.*, S8.*, S10.* |
| `identity`, `session`, `invite`, `ratelimit`, `retention`, `security` | `operator` | S10.* |
| `launch`, `change` | `operator` (two approvers for `launch`) | S14.* |
| `analytics`, `experiment`, `growth`, `team`, `public`, `metrics`, `calibration` | `founders` for thresholds, `operator` otherwise | S12.*, S13.* |
| `api`, `ui`, `i18n` | `operator` | S11.*, S15.* |

### 0.10.6 Initial parameter list

The list below is the FULL set of parameter names; names are stable and C-022 completes the table (units, owners, notes) without renaming. Every default is an `initial configurable default`: a safe starting value that is replaced by the measurement in the last column, never a finding. Where a default is derived, the formula is shown. Values marked "FD§3.3 illustrative" are the Founding Document's own example inputs, not measurements. `ratio` values are written as decimals here and stored as ppm.

**Table A: credit, price, admission, reservation, grant, reserve, mint, inflation, ledger, job, change**

| Name | Type | Initial configurable default | Validation | Replaced by |
| --- | --- | --- | --- | --- |
| `credit.scale_ucr_per_credit` | int | 1,000,000 | constant | `CON` |
| `credit.lifetime_days` (E) | days | 60 (FD§4.5 proposal) | 1..365 | `P1M` arm comparison: return, share of credit expiring |
| `credit.lifetime_days_accelerated` | days | 14 (FD§4.5 example arm) | 1..365; C4 | `P1M` arm comparison |
| `credit.member_cap_credits` (K) | credits | 350 = round to 50 of 1.25 x 240 x 1.15 (the FD§3.3 reference job with a 25% margin) | 1..100000; C8 | `DEM` p90 large-job size, then `P1M` |
| `credit.expiry_notice_days` | days | 7 | 0..60 | `OPS` member feedback |
| `credit.expiry_sweep_interval_s` | duration_s | 3600 | 60..86400 | `OPS` |
| `price.levy_lambda` (λ) | ratio | 0.05 (FD§3.3 illustrative) | 0 <= x < 1; C6 | `P1M` Reserve inflow versus grant demand, then `FND` |
| `price.v_prior` | ratio | 0.10 (FD§3.3 illustrative) | 0..price.v_cap | `P1M` measured v |
| `price.v_cap` | ratio | 0.50 | 0..1 | `FND` |
| `price.v_window_days` | days | 28 | 7..90 | `P1M` stability of v |
| `price.v_min_sample_cells` | int | 100 | 1..100000 | `P1M` variance of v |
| `price.publish_period_days` | days | 30 (FD§4.3 "monthly") | 1..90 | `FND` |
| `price.eta_alarm_threshold` | ratio | 0.80 (FD§4.3 suggested, arbitrary) | 0..1 | `FND` (pre-registered) |
| `price.quote_ttl_s` | duration_s | 1800 | 60..86400 | `OPS` |
| `price.v_rounding` | enum | `ceil` | constant | `CON` |
| `admission.phi` (φ) | ratio | 0.50 (FD§3.3 illustrative) | 0 < x < 1; C1 | `P1M` throughput and deposit-to-withdrawal ratio |
| `admission.forecast_window_days` | days | 14 | 3..60 | `P1M` forecast error |
| `admission.active_donor_window_days` | days | 7 | 1..30 | `P1M` |
| `admission.forecast_haircut` | ratio | 0.00 (so FD§3.3 reproduces exactly) | 0 <= x < 1 | `P1M` forecast error; expected to become > 0 [H] |
| `admission.min_window_s` | duration_s | 43,200 | C7 | `DEM` accepted windows |
| `admission.max_window_days` | days | 14 | 1..60; C7 | `DEM` |
| `admission.max_job_cells` | int | 300 = floor(350 / 1.15) rounded down to a multiple of 100 | 1..100000 | `DEM`, then `P1M` |
| `admission.max_concurrent_jobs_per_member` | int | 2 | 1..20 | `FND` |
| `admission.waitlist_ttl_days` | days | 7 | 1..60 | `OPS` |
| `admission.waitlist_max_per_member` | int | 1 | 0..10 | `OPS` |
| `admission.deadline_multiplier_standard` | ratio | 1.0 (FD§4.8 fixed in Phase 1) | constant in Phase 1 | `CON` |
| `reservation.max_horizon_days` | days | 30 | 1..180 | `P1M` |
| `reservation.max_active_per_member` | int | 1 | 0..10 | `FND` |
| `reservation.free_cancel_notice_s` | duration_s | 86,400 | 0..2592000 | `OPS` |
| `reservation.capacity_share_cap` | ratio | 0.25 of the φ capacity of any day | 0..1 | `P1M` burstiness |
| `grant.starter_credits` (G) | credits | 3 (FD§4.6 "a few cells") | 0..1000; C5 | `P1M` first-job completion, Reserve flow |
| `grant.starter_lifetime_days` | days | 14 (FD§4.6 "expires quickly") | 1..365; C4 | `P1M` |
| `grant.required_verified_cells` | int | 1 (FD§4.6) | 1..50 | `FND` |
| `grant.max_per_device` | int | 1 (lifetime) | 0..10 | `OPS` farming flags |
| `grant.max_per_invite_tree_per_day` | int | 2 | 0..100 | `OPS` |
| `grant.max_per_day` | int | 20 | 0..10000 | `OPS` |
| `grant.reserve_floor_credits` | credits | 0 (grants pause rather than overdraw; FD§4.6) | >= 0 | `FND` |
| `grant.non_transferable` | bool | true | constant | `CON` |
| `reserve.ceiling_credits` | credits | 1000 | >= grant.starter_credits; C5 | `P1M` grant demand and expiry inflow |
| `reserve.retire_interval_s` | duration_s | 86,400 | 3600..604800 | `OPS` |
| `reserve.retire_min_credits` | credits | 10 (avoids noise entries) | >= 0 | `OPS` |
| `mint.monthly_cap_credits` | credits | 4800 = 40 donors x 8 cells/day x 30 days x (1 - 0.5) (FD§3.3 illustrative inputs); never above forecast redeemable capacity | >= 0 | `CAL` then `P1M` throughput |
| `mint.cap_period` | enum | `utc_month` | constant | `CON` |
| `mint.per_member_daily_cap_credits` | credits | 30 (three times the FD§3.2 habit of about 10 cells a day) | >= 1 | `P1M` |
| `mint.requires_launch_gate` | bool | true | constant | `CON` |
| `inflation.claim_ratio_threshold_weeks` | ratio | 6.0 (weeks of capacity) | > 0 | `FND`, `P1M` |
| `inflation.mint_cap_cut_ratio` | ratio | 0.25 (cut applied when the threshold is passed) | 0 < x <= 1 | `FND` |
| `inflation.mint_utilization_alarm` | ratio | 0.90 | 0..1 | `OPS` |
| `inflation.throughput_window_days` | days | 28 | 7..90 | `P1M` |
| `ledger.invariant_check_interval_s` | duration_s | 60 (sampled checks; the per-commit check is a constant) | 5..3600 | `OPS` |
| `ledger.full_recompute_interval_s` | duration_s | 3600 | 60..86400 | `OPS` |
| `ledger.checkpoint_interval_s` | duration_s | 86,400 | 3600..604800 | `OPS` |
| `ledger.reversal_min_approvers` | int | 2 | constant | `CON` |
| `ledger.allow_negative_balance` | bool | false | constant | `CON` |
| `job.max_overrun_ratio` | ratio | 2.0 (a job stops with partial settlement at 2 x its quoted window) | >= 1 | `P1M` |
| `job.max_upload_bytes` | int | 4,194,304 (300 cells x 4,000 chars x up to 3 bytes of UTF-8 is about 3.6 MB) | 1..104857600 | `TEC` |
| `change.notice_days_default` | days | 7 (FD Principle 5) | 0..90 | `FND` |
| `change.notice_days_price` | days | 14 (for `price.*`, `admission.*`, `credit.*`) | 0..90 | `FND` |
| `change.tighten_publish_within_s` | duration_s | 86,400 (tightening is immediate, its public log entry follows within a day) | 0..604800 | `FND` |

**Table B: verify, lease, cell, trust, invite, ratelimit, identity, session, retention, policy, screen, service, template, optin, appeal, report**

| Name | Type | Initial configurable default | Validation | Replaced by |
| --- | --- | --- | --- | --- |
| `verify.gold_rate_g` (g) | ratio | 0.05 | C2 | `P1M` reliability-estimate variance and false-accept estimate |
| `verify.gold_rate_floor` | ratio | 0.01 | C2 | `FND` |
| `verify.gold_rate_max` | ratio | 0.20 | C2 | `FND` |
| `verify.audit_rate_s` (s) | ratio | 0.10 | C2 | `P1M` false-accept estimate, v |
| `verify.audit_rate_floor` | ratio | 0.02 (FD§4.4: sampling never falls to zero) | C2; > 0 | `FND` |
| `verify.audit_rate_max` | ratio | 0.50 | C2 | `FND` |
| `verify.blanket_redundancy_n` | int | 3 (FD§4.4 "triple") | 2..5 | `P1M` |
| `verify.new_donor_blanket_cells` | int | 5 first cells of a new donor | 0..50 | `P1M` |
| `verify.adapt.clean_streak` | int | 20 clean observations before a step down | 1..1000 | `P1M` |
| `verify.adapt.step_down_ratio` | ratio | 0.80 | 0 < x < 1 | `P1M` |
| `verify.adapt.step_up_ratio` | ratio | 2.00 | > 1 | `P1M` |
| `verify.reliability_prior_a` | int | 1 (Beta prior, successes) | >= 1 | `P1M` |
| `verify.reliability_prior_b` | int | 1 (Beta prior, failures) | >= 1 | `P1M` |
| `verify.reliability_window_obs` | int | 50 most recent gold and audit observations | 5..1000 | `P1M` |
| `verify.human_review_rate` | ratio | 0.20 of subjective outputs | 0..1 | `P1M` |
| `verify.human_review_gold_rate` | ratio | 0.10 | 0..1 | `P1M` |
| `verify.timing_min_s` | duration_s | 5 (below this a submission is a timing anomaly) | >= 0 | `CAL` seconds-per-cell distribution |
| `verify.duplicate_similarity_threshold` | ratio | 0.95 | 0..1 | `P1M` |
| `verify.false_accept_alarm` | ratio | 0.05 | 0..1 | `FND` (pre-registered) |
| `verify.false_reject_alarm` | ratio | 0.10 | 0..1 | `FND` (pre-registered) |
| `verify.third_exec_on_mismatch` | bool | true (FD§4.4) | constant | `CON` |
| `verify.model_judge_mints_credit` | bool | false (FD§4.4) | constant in Phase 1 | `CON` |
| `lease.timeout_s` | duration_s | 1200 = 10 x 120 s, ten times the FD§3.2 first-contribution estimate | C3 | `CAL` p95 of seconds per cell |
| `lease.max_active_per_member` | int | 3 (a daily batch is one card or a few, FD§3.2) | 1..50 | `P1M` |
| `lease.max_extensions` | int | 1 | 0..5 | `CAL` |
| `lease.extend_s` | duration_s | 600 | 60..3600 | `CAL` |
| `lease.submit_grace_s` | duration_s | 120 (late paste-back accepted if the cell is not yet re-leased) | 0..900 | `CAL` copy-paste timing |
| `lease.reap_interval_s` | duration_s | 30 | 5..300 | `OPS` |
| `lease.nonce_bytes` | int | 16 | constant | `CON` |
| `lease.decline_cooldown_s` | duration_s | 0 (a decline is never punished, FD§5.5) | constant | `CON` |
| `cell.envelope.max_input_chars` | int | 4000 | 200..100000 | `CAL` largest input that completes in one Send |
| `cell.envelope.max_output_chars` | int | 6000 | 200..100000 | `CAL` |
| `cell.envelope.max_submission_bytes` | int | 32,768 (6000 chars x up to 3 UTF-8 bytes = 18,000, plus margin) | 1024..1048576 | `CAL` |
| `cell.envelope.expected_time_s` | duration_s | 120 (FD§3.2 first-contribution estimate) | 10..3600; C3 | `CAL` median seconds per cell |
| `cell.max_attempts` | int | 5 | 1..20 | `P1M` |
| `trust.established_min_cells` | int | 10 accepted cells | 1..10000 | `P1M` |
| `trust.established_min_reliability` | ratio | 0.80 | 0..1 | `P1M` |
| `trust.trusted_min_cells` | int | 100 | 1..100000 | `P1M` |
| `trust.trusted_min_reliability` | ratio | 0.95 | 0..1 | `P1M` |
| `trust.demote_below_reliability` | ratio | 0.70 | 0..1 | `P1M` |
| `trust.restrict_after_gold_fails` | int | 2 consecutive failed gold cells | 1..20 | `P1M` |
| `trust.restriction_days` | days | 7 | 1..90 | `OPS` |
| `trust.cap_multiplier.new` / `.established` / `.trusted` / `.restricted` | ratio | 0.50 / 1.00 / 1.50 / 0.25 of K (FD§6.1: tiers raise caps) | 0..10 | `P1M` |
| `trust.audit_multiplier.new` / `.established` / `.trusted` / `.restricted` | ratio | 1.0 / 1.0 / 0.5 / 3.0 of s, then clamped to the floor and maximum (FD§6.1: tiers lower sampling) | 0..10 | `P1M` |
| `invite.max_active_per_member` | int | 3 | 0..100 | `OPS` farming flags |
| `invite.ttl_days` | days | 14 | 1..90 | `OPS` |
| `invite.min_accepted_cells_to_issue` | int | 3 | 0..1000 | `OPS` |
| `invite.tree_max_members` | int | 50 | 1..10000 | `OPS` |
| `invite.tree_max_depth` | int | 4 | 1..20 | `OPS` |
| `ratelimit.device_new_members_per_day` | int | 3 | 1..100 | `OPS` |
| `ratelimit.ip_hash_new_members_per_day` | int | 10 | 1..1000 | `OPS`, `SEC` |
| `ratelimit.invite_tree_new_members_per_day` | int | 10 | 1..1000 | `OPS` |
| `ratelimit.member_leases_per_hour` | int | 30 | 1..1000 | `P1M` |
| `ratelimit.member_submissions_per_hour` | int | 60 | 1..1000 | `P1M` |
| `ratelimit.member_api_rpm` | int | 120 | 10..10000 | `OPS` |
| `ratelimit.admin_api_rpm` | int | 300 | 10..10000 | `OPS` |
| `ratelimit.public_rpm` | int | 60 per IP hash | 1..10000 | `OPS` |
| `ratelimit.recovery_attempts_per_day` | int | 5 | 1..100 | `SEC` |
| `identity.recovery_key_bits` | int | 128 | >= 128 | `SEC` |
| `identity.key_rotation_grace_s` | duration_s | 604,800 | 0..2592000 | `SEC` |
| `identity.device_link_code_ttl_s` | duration_s | 300 | 30..3600 | `SEC` |
| `identity.recovery_cooldown_s` | duration_s | 86,400 (a recovered identity cannot start jobs or spend for this long) | 0..2592000 | `SEC` |
| `identity.recovery_max_per_90d` | int | 2 | 0..20 | `SEC` |
| `identity.email_optional` | bool | true (FD§3.2) | constant | `CON` |
| `session.member_idle_ttl_s` | duration_s | 2,592,000 | 600..31536000 | `SEC` |
| `session.member_abs_ttl_s` | duration_s | 7,776,000 | 600..31536000 | `SEC` |
| `session.admin_idle_ttl_s` | duration_s | 1800 | 60..86400 | `SEC` |
| `session.admin_abs_ttl_s` | duration_s | 28,800 | 600..86400 | `SEC` |
| `retention.raw_ip_stored` | bool | false | constant | `CON` |
| `retention.ip_hash_ttl_days` | days | 1 | 0..30 | `SEC` |
| `retention.session_days` | days | 90 | 1..365 | `SEC` |
| `retention.request_log_days` | days | 7 | 0..90 | `SEC` |
| `retention.ops_log_days` | days | 30 | 0..365 | `SEC` |
| `retention.event_raw_days` | days | 30 | 0..365 | `SEC` |
| `retention.job_payload_days` | days | 30 | 0..365 | `SEC`, `DEM` |
| `retention.moderation_days` | days | 180 | 0..1095 | `SEC`, `CNS` |
| `retention.member_inactive_days` | days | 365 (then status `closed`) | 30..3650 | `SEC` |
| `policy.loosen_min_notice_days` | days | 7 (R10) | >= change.notice_days_default | `FND` |
| `policy.tighten_immediate` | bool | true (R10) | constant | `CON` |
| `policy.recheck_on_accept` | bool | true (R9) | constant | `CON` |
| `screen.url_action` | enum | `flag_for_review` (`reject`, `flag_for_review`) | enum | `P1M` incident log |
| `screen.pii_action` | enum | `reject` | enum | `P1M` |
| `screen.output_url_action` | enum | `quarantine` (FD§5.5: flagged, not shown as a result) | enum | `P1M` |
| `screen.max_urls_per_input` | int | 0 | 0..100 | `P1M` |
| `screen.review_rate_new_requester` | ratio | 1.0 (every input reviewed) | 0..1 | `OPS` reviewer load |
| `screen.review_rate_established_requester` | ratio | 0.20 | 0..1 | `OPS` |
| `service.review_max_age_days` | days | 90 | 1..365 | `CNS` |
| `service.review_grace_days` | days | 14 | 0..90 | `CNS` |
| `service.min_approvers` | int | 1 (FD§5.3: a reviewer records the answers); 2 is an owner decision [A] | 1..5 | `FND` |
| `service.terms_copy_max_bytes` | int | 5,242,880 | 1024..52428800 | `OPS` |
| `template.min_reviewers_new` | int | 2 (FD§5.7 failure mode 10) | 1..5 | `FND` |
| `template.min_reviewers_edit` | int | 1 | 1..5 | `FND` |
| `template.autopause_report_count` | int | 5 reports inside `template.autopause_window_s` | 1..1000 | `OPS` |
| `template.autopause_window_s` | duration_s | 3600 | 60..604800 | `OPS` |
| `optin.default_purposes` | json | `["P0","P1"]` (FD§5.4 R8) | subset of P0..P3 | `FND` |
| `optin.default_sensitivities` | json | `["S0","S1"]` (R8) | subset of S0..S1 | `FND` |
| `optin.default_licenses` | json | `["L0","L1","L2"]` [A] | subset of L0..L3 | `FND` |
| `optin.default_service_requirements` | json | `["M0","M1","M2"]` [A] | subset of M0..M2 | `FND` |
| `optin.sensitive_topics_default` | bool | false (each sensitive topic category is opt-in, R8) | constant | `CON` |
| `appeal.window_days` | days | 14 | 1..90 | `FND` |
| `appeal.max_per_decision` | int | 1 | 1..5 | `FND` |
| `appeal.reviewer_sla_days` | days | 7 (target, published) | 1..60 | `OPS` |
| `appeal.ban_min_reviewers` | int | 2 | 1..5 | `FND` |
| `report.triage_sla_days` | days | 3 (target, published) | 1..30 | `OPS` |
| `report.max_per_member_per_day` | int | 20 | 1..1000 | `OPS` |

**Table C: launch, analytics, experiment, growth, team, public, api, ui, i18n, security, calibration, metrics**

| Name | Type | Initial configurable default | Validation | Replaced by |
| --- | --- | --- | --- | --- |
| `launch.members_may_join` | bool | false (global switch; stays off until the gate checklist is signed off in the admin tool) | only settable when the gate rule in S14.* passes | `CON` default; flipped by sign-off |
| `launch.member_jobs_enabled` | bool | false | as above | flipped by sign-off |
| `launch.minting_enabled` | bool | false | as above | flipped by sign-off |
| `launch.required_gate_ids` | json | `["G0","G1"]` (FD§8.3 exit rule) | subset of G0..G5 that always contains G0 and G1 | `FND` |
| `launch.min_signoffs` | int | 2 distinct admins [A]; an owner decision if the team has one person | 1..5 | `FND` |
| `launch.min_approved_services` | int | 1 (FD§8.3 exit rule; or a documented fallback) | 0..20 | `FND` |
| `analytics.third_party_trackers` | bool | false | constant | `CON` |
| `analytics.cookies_enabled` | bool | false | constant | `CON` |
| `analytics.min_cohort_k` | int | 10 (cohorts smaller than this are suppressed in aggregates) | 1..1000 | `SEC` |
| `experiment.expiry_arm.fraction` | ratio | 0.50 of Phase 1 members (FD§9 "part of the group") | 0..1 | `FND` |
| `experiment.assignment_seed_version` | int | 1 | >= 1 | `OPS` |
| `experiment.assignment_log_enabled` | bool | true | constant | `CON` |
| `growth.referral.bonus_referrer_credits` | credits | 1 | 0..100 | `FND`, `P1M` |
| `growth.referral.bonus_newcomer_credits` | credits | 1 | 0..100 | `FND`, `P1M` |
| `growth.referral.min_newcomer_verified_cells` | int | 1 (FD§6.2 V5) | 1..50 | `FND` |
| `growth.referral.max_per_referrer_per_30d` | int | 5 | 0..1000 | `OPS` farming flags |
| `growth.referral.hold_s` | duration_s | 86,400 (bonus paid after this delay) | 0..2592000 | `OPS` |
| `team.max_members` | int | 50 | 2..10000 | `OPS` |
| `team.min_public_members` | int | 5 (a team is not shown publicly below this size) | 1..1000 | `SEC` |
| `team.create_min_tier` | enum | `established` | `new`, `established`, `trusted` | `OPS` |
| `public.counter_refresh_s` | duration_s | 60 | 5..3600 | `OPS` |
| `public.ledger_lag_s` | duration_s | 300 (public ledger page trails the ledger by this much) | 0..86400 | `SEC` |
| `public.location_display` | enum | `never` (FD§6.1 row 5) | `never`, `opt_in` | `SEC` |
| `api.idempotency_ttl_s` | duration_s | 86,400 | 3600..604800 | `OPS` |
| `api.page_size_default` | int | 50 | 1..api.page_size_max | `OPS` |
| `api.page_size_max` | int | 200 | 1..1000 | `OPS` |
| `api.cursor_ttl_s` | duration_s | 3600 | 60..86400 | `OPS` |
| `api.max_body_bytes` | int | 1,048,576 (uploads use `job.max_upload_bytes`) | 1024..104857600 | `TEC` |
| `api.request_timeout_s` | duration_s | 30 | 1..300 | `TEC` |
| `ui.card.expand_required_first_use` | bool | true (FD§5.5) | constant | `CON` |
| `ui.comprehension_check_rate` | ratio | 0.00 (FD§5.7 failure mode 6 is a hypothesis [H]) | 0..1 | `P1M` |
| `ui.fast_contribution_threshold_s` | duration_s | 60 (FD§6.2 V1) | 1..600 | `FND` |
| `i18n.default_locale` | enum | `fa` | `fa`, `en` | `FND` |
| `i18n.supported_locales` | json | `["fa","en"]` | subset of `locale` | `CON` |
| `i18n.digits_default_fa` | enum | `persian` [A][H]; the member can switch to `latin` | `latin`, `persian` | `P1M` interviews |
| `i18n.dual_calendar_detail` | bool | true (FD§10: Jalali and Gregorian) | | `FND` |
| `security.secret_rotation_days` | int | 90 | 1..365 | `SEC` |
| `security.rotate_before_public_exposure` | bool | true (FD§10) | constant | `CON` |
| `security.two_person_actions` | json | `["ledger.reversal","launch.signoff","parameter.loosen","killswitch.release"]` [A] | subset of the action names in S10.* | `SEC` |
| `calibration.min_samples_per_service` | int | 30 cells per service before a `CAL` value may replace a default | 1..10000 | `FND` |
| `metrics.rollup_interval_s` | duration_s | 3600 | 60..86400 | `OPS` |

**Kill switches** (entity `KillSwitch`, default `released`, engaged by an operator with a logged reason; S14.*): `kill.all_minting`, `kill.all_new_jobs`, `kill.template.<tpl_id>`, `kill.service.<svc_id>`, `kill.member.<mem_id>`. **Feature flags** (entity `FeatureFlag`, default off): `ff.growth.v1_fast_path`, `ff.growth.v2_live_counter`, `ff.growth.v3_share_card`, `ff.growth.v4_teams`, `ff.growth.v5_referral`, `ff.growth.v6_milestones`, `ff.channel.human_review`, `ff.job.reservations`, `ff.public.ledger_page`, `ff.experiment.expiry_arm`. Each experiment-capable flag has an `Experiment` with a logged assignment (S12.*, S13.*). [D]

## 0.11 API conventions

### 0.11.1 Transport and shape [D]

- Base path `/v1`. HTTPS only. JSON only (`application/json; charset=utf-8`); other media types return 415. Field names `snake_case`; enum values as in 0.8; ids as in 0.6.3; timestamps RFC 3339 UTC; amounts `*_ucr` as integer strings; ratios as integer `*_ppm` fields (the display decimal is computed by the client).
- Resource paths are plural kebab-case nouns: `/v1/<resources>[/{id}[/<sub-resource>]]`. No verbs in paths; a non-CRUD command is a `POST` that creates a sub-resource: `POST /v1/cells/{cell_id}/leases`, `POST /v1/leases/{lease_id}/submission`, `POST /v1/jobs/{job_id}/cancellation`. Operation ids are in S15.* (0.5).
- A single resource is returned as the object itself; a list is `{ "data": [...], "page": { "next_cursor": string|null, "limit": int } }`. `PATCH` uses JSON Merge Patch (RFC 7396). No XML, no cookies, no query-string secrets.
- Breaking changes require `/v2`; additive fields are allowed within `/v1`; clients ignore unknown fields.

### 0.11.2 Surfaces and prefixes [D]

| Surface | Path prefix | `auth_scheme` |
| --- | --- | --- |
| Public (counter, public ledger, parameters, change log, milestones) | `/v1/public/*` | `none` |
| Member (identity, cells, leases, submissions, jobs, balance, settings, teams, appeals) | `/v1/*` except the two other prefixes | `member` |
| Admin (templates, services, policy, parameters, audits, appeals, abuse, ledger explorer, launch gates, kill switches) | `/v1/admin/*` | `admin` |

Anonymous identity creation, recovery start and the public surface are the only `none` endpoints outside `/v1/public/*`; they are rate-limited per IP hash. [D]

### 0.11.3 Error model [D]

Every non-2xx response has this body (the `error` object is the only top-level key):

```json
{ "error": { "code": "STATE_CONFLICT", "message": "developer-facing English text", "details": { }, "request_id": "req_01j9z..." } }
```

`code` is `UPPER_SNAKE` and stable; `message` is for developers and never shown to members; user-facing text comes from `details.copy_key` (a `copy.*` key, 0.5) rendered client-side in `fa` or `en`. `details` is an object, possibly empty; `details.fields` is a list of `{path, code, message}` for validation errors. `request_id` also appears in the `X-Request-Id` header and in logs. [D]

| HTTP | `code` | Use |
| --- | --- | --- |
| 400 | `MALFORMED_REQUEST`, `VALIDATION_FAILED` | Syntax; field rules; missing `Idempotency-Key` where required |
| 401 | `AUTH_REQUIRED`, `AUTH_INVALID`, `AUTH_EXPIRED` | Missing, wrong-scheme or expired token |
| 403 | `FORBIDDEN`, `LAUNCH_GATE_CLOSED` | Permission missing; a launch switch (0.10.6 table C) is off |
| 404 | `NOT_FOUND` | Also returned instead of 403 when existence must not leak |
| 409 | `STATE_CONFLICT`, `LEASE_CONFLICT`, `ALREADY_EXISTS`, `IDEMPOTENCY_IN_PROGRESS` | A guard of a state machine failed; race lost |
| 410 | `LEASE_EXPIRED` | The lease or nonce is no longer valid |
| 412 | `PRECONDITION_FAILED` | `If-Match` does not match |
| 413 | `PAYLOAD_TOO_LARGE` | Body or submission over its limit |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | Not JSON |
| 422 | `POLICY_REJECTED` (`details.reasons` = `policy.<rule>.<slug>` list), `INSUFFICIENT_CREDIT`, `CAP_EXCEEDED`, `NO_CAPACITY`, `IDEMPOTENCY_KEY_MISMATCH`, `UNPROCESSABLE` | Semantically valid request refused by a business rule |
| 429 | `RATE_LIMITED` | With `Retry-After` |
| 500 / 503 | `INTERNAL`, `UNAVAILABLE`, `KILL_SWITCH_ENGAGED` | `Retry-After` when known |

### 0.11.4 Authentication schemes [D][A]

| Scheme | Credential | Rules |
| --- | --- | --- |
| `member` | `Authorization: Bearer <member session token>` obtained by a signed challenge with a `MemberKey` (S10.*) | Valid only on member endpoints; no cookies, so no CSRF surface; CORS allows the one front-end origin |
| `admin` | `Authorization: Bearer <admin session token>` obtained by WebAuthn for an `AdminUser`; no shared password anywhere | Valid only on `/v1/admin/*`, served from a separate origin [A]; shorter session TTLs (`session.admin_*`); sensitive actions need a second admin (`security.two_person_actions`) |
| `none` | nothing | Public and anonymous-bootstrap endpoints only |

A token of one scheme sent to an endpoint of another is `AUTH_INVALID` and is counted by the rate limiter. [D]

### 0.11.5 Idempotency-Key [D]

- Header `Idempotency-Key`: 16 to 64 characters matching `^[A-Za-z0-9_-]+$`, generated by the client (a ULID or random UUID). **Required** on every `POST`, `PUT`, `PATCH` and `DELETE` that creates or changes jobs, leases, submissions, escrow, ledger-affecting state, grants, referrals, reports or appeals, and on every admin write; optional elsewhere.
- Scope: (principal id, method, path with ids substituted). The server stores the SHA-256 of the canonical request body (0.6.4) with the stored response for `api.idempotency_ttl_s`.
- Same key and same body: the stored status and body are replayed with `Idempotent-Replayed: true`. Same key, different body: `422 IDEMPOTENCY_KEY_MISMATCH`. Same key while the first request is running: `409 IDEMPOTENCY_IN_PROGRESS` with `Retry-After`. Only 2xx and deterministic 4xx outcomes are stored; 5xx outcomes are not.
- Natural idempotency still applies underneath (one submission per lease and nonce, one `escrow_hold` per job), so a missing or reused key cannot double-spend. [D]

### 0.11.6 Cursor pagination [D]

Query `?limit=` (default `api.page_size_default`, maximum `api.page_size_max`) and `?cursor=`. The cursor is an opaque base64url string that encodes the sort key `(created_at, id)` and a keyed MAC; a tampered or expired (`api.cursor_ttl_s`) cursor is `400 VALIDATION_FAILED`. Default order is newest first; lists that need another order say so. No total counts by default (they are expensive and can leak). [D]

### 0.11.7 Concurrency, caching, rate-limit headers [D]

- Mutable admin resources return an `ETag` (their `row_version`) and require `If-Match` on `PUT` and `PATCH`; a mismatch is `412 PRECONDITION_FAILED`.
- Authenticated responses carry `Cache-Control: no-store`. Public resources carry an `ETag` and a `Cache-Control: max-age` no larger than their refresh parameter.
- Every response on a rate-limited route carries `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset` (seconds until the window resets) [A: modeled on the IETF draft fields; the names are fixed here even if the draft changes]; a `429` also carries `Retry-After`. The limit key is the member id, admin id, or IP hash, never a raw IP (0.6.4).


## 0.12 Build milestones (names and themes)

Build milestones are written `BM0`..`BM9` (see `ISS-01` for why not `M0..Mn`). This section fixes ids, names and one-line themes only. S17.* details dependencies, acceptance tests (`AC-*`, `T-*`) and the Definition of Done of each milestone. [D]

**Ordering rules** [D]

1. Every milestone ends with a deployable, testable system. No milestone leaves a half-wired path reachable from a public or member surface.
2. The ledger and its invariants (`BM1`) precede every feature that moves credit. The launch-gate machinery and the Service Registry (`BM2`, `BM3`) precede every feature that creates a job or shows a cell to a member (prompt J; ground rule 6).
3. Every build of every milestone ships with `launch.members_may_join`, `launch.member_jobs_enabled` and `launch.minting_enabled` set to `false` (0.10.6, table C). No milestone changes those defaults. Only the sign-off flow built in `BM2` can flip them (S14.*).
4. No milestone is conditional on pilot size. Phase 1 is a configuration of the finished system (FD§9) [P].
5. Tests added by a milestone stay in CI and stay green in every later milestone (regression ratchet).
6. Finishing a milestone never authorizes a launch. Launching is the sign-off of `G0`..`G5` (S14.*), independent of build progress [D].

| ID | Name | One-line theme | Depends on | A working system at the end of it |
| --- | --- | --- | --- | --- |
| `BM0` | `foundation` | Repo, CI, environments, migrations, the ID, time and hash libraries of 0.6, error model, idempotency, pagination, rate-limit headers, config-store schema, observability skeleton, storage and host interfaces | none | An API that serves `/v1/public/health` in the 0.11 shapes; migrations and API conformance tests run in CI |
| `BM1` | `ledger_and_invariants` | Append-only double-entry ledger in integer `ucr`, lots and oldest-first spending, hash chain, continuous invariant checks with alarms, reversal with two approvers | `BM0` | A ledger driven only through its internal interface; the FD§3.3 example passes as `AC-ledger-01`; a seeded corruption raises `ledger.invariant_violated` |
| `BM2` | `admin_gates_and_config` | Admin passkey authentication and sessions, `AdminAction` log, parameter editor with versions and public change log, kill switches, feature flags with logged assignment, `LaunchGateItem` checklist and sign-off, `launch.*` enforcement, pre-registration lock, Phase 0 calibration tool | `BM0`, `BM1` | An operator can change a parameter prospectively, engage a kill switch, record calibration observations and sign off a gate; a `launch.*` switch refuses to turn on unless the rule in S14.* holds |
| `BM3` | `registry_and_policy` | Service Registry with every service `unreviewed`, `TermsCopy` capture, dated `FlagAnswer`s, service review machine, rules `R1`..`R10` as data plus the evaluator, metadata validation, allowlist, reason codes, opt-in data model | `BM2` | A job-shaped request is accepted or rejected with `policy.<rule>.<slug>` reasons; no service can reach `approved` without a saved terms copy |
| `BM4` | `identity_and_access` | Anonymous identity, `MemberKey`, recovery key, device linking, key rotation, optional e-mail, invites and invite trees, per-device, per-tree and per-day limits, roles and permission matrix, retention jobs, IP-hash handling | `BM2` | A member can be created, recovered and rate-limited; the permission-matrix suite passes; no raw IP appears in storage or logs |
| `BM5` | `templates_and_commons_jobs` | `Template` and `TemplateVersion` review with the second-reviewer rule, the first template set, upload and screening, Commons backlog authoring, the `Job` machine for Commons jobs, cell creation | `BM3`, `BM4` | A reviewer approves a template; a Commons job splits into queued cells; job creation is refused for every `unreviewed` service |
| `BM6` | `execution_and_verification` | Leasing with nonces, submission, anti-forgery checks, quarantine, automatic checks, gold cells, audits, adaptive sampling, reliability estimates, human-review cells, rework, rejection appeals, Commons minting under the monthly cap | `BM1`, `BM5` | A test donor drives a Commons cell from `Cell.queued` to `Cell.accepted` and the ledger mints exactly 1,000,000 `ucr`; replay, forgery and leasing-race tests pass |
| `BM7` | `member_jobs_and_credit_economy` | Price quote from v and λ, escrow, admission control and waitlist, reservations, payout, settlement, refunds, expiry sweeps, Reserve and retirement, starter grant, per-member cap K, claim ratio and η publication, inflation gauges | `BM6` | A member job runs from request to settlement; the closing identity holds; the FD§3.3 example passes end to end |
| `BM8` | `experiences_and_public` | Volunteer, Requester, Reviewer and Operator screens in Persian and English (RTL, numerals, Jalali), service-adapter layer, notices and copy, public counter, public ledger and parameter pages, change log, milestone pages, share cards, teams, referrals, growth flags `V1`..`V6` | `BM6`, `BM7` | A new member completes the first-contribution flow and a requester completes the wizard in both locales; accessibility and low-bandwidth checks pass |
| `BM9` | `measurement_simulation_hardening` | Event schema and metrics pipeline for every FD§9 Phase 1 measure, expiry-arm assignment, simulation harness with adversarial agents, load and end-to-end suites, backup and restore drill, secret rotation drill, pre-build checklist closure | `BM7`, `BM8` | Every FD§9 Phase 1 measure has a query; simulation reports carry the label "not evidence about human behavior"; the drills are logged |

Rationale for the order [D]: money-like state (`BM1`) and the legal and safety brakes (`BM2`, `BM3`) are built before anything a member can touch; the Phase 0 calibration tool is in `BM2` so the founders can run Phase 0 measurements (`CAL`, 0.10.4) while the remaining milestones are built, because the envelope, lease and sampling defaults can only be replaced by measurement.

## 0.13 Spec files and owner cells

One row per spec file. File names are proposals [A]: the `allowed_paths` of the owning cell are authoritative, and assembly orders files by the number in their top heading (`# <n>. <title>`), never by file name. A file carries one top-level heading unless its owner cell says otherwise. [D]

| Part | Required section (prompt structure) | File | Owner cell | Issue block (0.4) |
| --- | --- | --- | --- | --- |
| S0 | Conventions and decisions skeleton | `spec/00-conventions.md`, `spec/00-decisions.md` | `C-000` | `ISS-01`..`ISS-09` |
| S1 | Purpose, scope, how to read (evidence-tag legend, reusing 0.2) | `spec/01-purpose.md` | `C-001` | `ISS-11`..`ISS-19` |
| S2 | Issues found in the Founding Document, consolidated from every `## Issues raised` | `spec/02-issues.md` | `C-001` | `ISS-21`..`ISS-29` |
| S3 | Assumptions [A] and open owner decisions | `spec/03-assumptions.md` | `C-001` | `ISS-31`..`ISS-39` |
| S4 | System overview and architecture | `spec/04-architecture.md` | `C-002` | `ISS-41`..`ISS-49` |
| S5 | Domain model: entities | `spec/05a-domain-model.md` | `C-003` | `ISS-51`..`ISS-53` |
| S5 | State machines, idempotency, concurrency | `spec/05b-state-machines.md` | `C-004` | `ISS-54`..`ISS-56` |
| S6 | Credit, ledger and pricing | `spec/06a-credit-ledger-pricing.md` | `C-005` | `ISS-61`..`ISS-63` |
| S6 | Admission control | `spec/06b-admission-control.md` | `C-006` | `ISS-64`..`ISS-66` |
| S7 | Policy engine and Service Registry | `spec/07-policy-registry.md` | `plan` | `ISS-71`..`ISS-79` |
| S8 | Templates and verification pipeline | `spec/08-templates-verification.md` | `plan` | `ISS-81`..`ISS-89` |
| S9 | Result return, anti-forgery and abuse defenses | `spec/09-result-return-abuse.md` | `plan` | `ISS-91`..`ISS-99` |
| S10 | Identity, access, privacy and safety, with the threat model table | `spec/10-identity-privacy-safety.md` | `plan` | `ISS-101`..`ISS-109` |
| S11 | Volunteer, Requester, Reviewer and Operator experiences, Persian first | `spec/11-experiences.md` | `plan` | `ISS-111`..`ISS-119` |
| S12 | Public surfaces and growth experiments | `spec/12-public-growth.md` | `plan` | `ISS-121`..`ISS-129` |
| S13 | Measurement, experiment support and pre-registration | `spec/13-measurement.md` | `plan` | `ISS-131`..`ISS-139` |
| S14 | Launch gates G0..G5, exit rule, kill switches | `spec/14-launch-gates.md` | `plan` | `ISS-141`..`ISS-149` |
| S15 | API specification | `spec/15-api.md` | `plan` | `ISS-151`..`ISS-159` |
| S16 | Configuration parameter table (completes 0.10.6 without renaming) | `spec/16-parameters.md` | `C-022` | `ISS-161`..`ISS-169` |
| S17 | Build plan: milestones `BM0`..`BM9` in detail | `spec/17-build-plan.md` | `C-023` | `ISS-171`..`ISS-179` |
| S18 | Test strategy and simulation harness | `spec/18-tests-simulation.md` | `plan` | `ISS-181`..`ISS-189` |
| S19 | Risks, what remains unverified, pre-build checklist | `spec/19-risks.md` | `plan` | `ISS-191`..`ISS-199` |
| S20 | Glossary | `spec/20-glossary.md` | `plan` | `ISS-201`..`ISS-209` |
| S21 | Short Persian summary (about 10 lines) | `spec/21-persian-summary.md` | `plan` | `ISS-211`..`ISS-219` |

Notes [D]

- `plan` means the owner cell is not named in the text available to `C-000`, and this file does not guess it; `C-001` fills the column at assembly [V]. The ids `C-001`..`C-006` come from the cell engine's dependents listing for this cell, which was truncated, and `C-022` and `C-023` from this cell's goal text [V].
- A part split over several files uses the issue sub-blocks of 0.4 in file sort order. A part that is not split uses all nine ids.
- Cross-part ownership of names: entities and enums are owned by `S0` (0.7, 0.8); states and events by `S0` (0.9) with guards and effects in `S5.*`..`S9.*`; parameters by `S0` (0.10.6) and `S16`; API conventions by `S0` (0.11) and operations by `S15`. A part that needs a missing name reports a convention gap (0.1).

## Issues raised

Problems and gaps found while fixing the shared vocabulary. Each resolution is already applied in this file; `C-001` consolidates them into S2.* and may record a different resolution. [D]

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-01` | minor | prompt | The brief and this cell's goal call build milestones `M0..Mn`, but `M0`..`M2` already denote service requirements (FD§5.3), so a bare `M1` would be ambiguous in every part | Build milestones are `BM0`..`BM9` (0.12); `M0`..`M2` stay reserved for service requirements | applied |
| `ISS-02` | major | FD§5.3, FD§8.3 | "Unknown is treated as no" is safe only for flags whose `yes` is the permissive answer. A flag phrased as a risk (for example "the provider trains on chats") would make `unknown` mean the optimistic reading | All gating flags are phrased as permissions (`yes` = the saved terms permit it). Risk-style flags are `info.*` keys and never gate (0.8.3) | applied |
| `ISS-03` | major | FD§4.2, FD§4.3 | Gold, audit and review cells inside Commons jobs have no escrow and no requester, yet FD§4.3 pays exactly 1 credit per accepted cell "of any kind". The FD does not say whether those cells mint | Every accepted Commons cell of any `cell_kind` mints exactly 1,000,000 `ucr` and counts against `mint.monthly_cap_credits`; the Commons verification share is measured and published beside v so make-work minting is visible | proposed |
| `ISS-04` | minor | FD§3.3, FD§4.3 | v is a ratio of cells, so N x v is rarely a whole number of verification cells; the FD example is exact only because 240 x 0.10 = 24 | v is stored in ppm and rounded up (0.6.1); the verification pool is `floor(pool / 10^6)` cells and any remainder is refunded at settlement (S6.* owns the full rule) | proposed |
| `ISS-05` | minor | FD§4.3 | v counts "rework cells" but FD§3.4 and FD§4.4 never define one | `cell_kind` `rework` is a replacement cell created when an accepted cell is overturned (`cell.overturned`, 0.9.3); it is paid from the verification pool and counts toward v | proposed |
| `ISS-06` | major | FD§4.6, FD§6.2 V5 | The referral two-sided bonus has no funding source in the FD; the Reserve is defined only as the source of starter grants | Referral bonuses are `grant` entries from the Reserve, never `mint`; they pause when the Reserve is at or below `grant.reserve_floor_credits` (0.8.5) | proposed |
| `ISS-07` | major | FD§4.5, FD§4.8 | Credit held in escrow for a long job can pass its expiry date, and the FD does not say what a refund does with it | A refund restores the consumed lots with their original expiry; escrow neither extends nor stops expiry; a restored lot already past expiry moves to the Reserve at the next sweep (0.8.5) | proposed |
| `ISS-08` | minor | FD§4.6 | "The Reserve is seeded by the founders' own verified Commons work" has no ledger operation that moves a member's credit to the Reserve | New entry type `reserve_donation`, `member` to `reserve`, consuming lots oldest-first (0.8.5) | applied |
| `ISS-09` | major | FD§3.2, FD§3.3, FD§4.2 | FD§3.2 step 8 pays donors at settlement; FD§4.2 says escrow pays "per accepted cell". If payment waited for settlement, a donor's earned credit would sit unusable and could expire, and a failed job would leave accepted cells unpaid | Donors are paid per accepted cell at acceptance (`transfer`, `payout` transaction). Settlement posts only the levy and the refund and closes the escrow at exactly zero (0.8.5) | proposed |

Convention additions made by this part (not issues, listed so `C-001` can fold them back): the entities marked [A] in 0.7, the `rework` cell kind (0.8.6), the `grant`, `reserve_donation` and `reversal` entry types (0.8.5), the flag-key list (0.8.3), the `BM0`..`BM9` ids (0.12) and the `ISS-nn` block rule (0.4).
