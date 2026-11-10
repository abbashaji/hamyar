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
