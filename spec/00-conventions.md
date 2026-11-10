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
- Natural keys: `ParameterName` (0.10), `policy_rule_id` (`R1`..`R10`), `flag_key` (0.8.6), invariant ids. These are stable strings, not ULIDs.
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
