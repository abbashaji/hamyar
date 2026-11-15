# A15 part 1: audit of spec/00-conventions.md sections 0.1 to 0.7

Scope: `## 0.1` to `## 0.7` (lines 5-243 at base 72c26b6). Lines 244-950 were read only to resolve references. File:line values in the table refer to the file at base 72c26b6, before the edits of this cell.

## Checked

- FD§3.3 example in 0.6.1 recomputed in integers: p = 1,000,000 + 100,000 + 50,000 = 1,150,000 ucr; escrow 240 x 1,150,000 = 276,000,000; pool 240 x 100,000 = 24,000,000 = 24 cells; levy 240 x 50,000 = 12,000,000; payout 264 x 1,000,000 = 264,000,000; 264,000,000 + 12,000,000 = 276,000,000; Sara keeps 300 - 276 = 24; eta_ppm = floor(10^12 / 1,150,000) = 869,565; capacity floor(40 x 8 x 2 x 500,000 / 10^6) = 320 >= 264; 240 / 8 = 30 days. All match FD§3.3.
- Identity `eta_ppm = floor(10^12 / p_ucr)` and `p_ucr` = p in ppm hold because the scale equals the ppm scale; int64 limit 2^63 / 10^6 is about 9.2 x 10^12 credits.
- Scope B entity list in 0.7 equals the prompt scope B list: 24 named entities, with Template/TemplateVersion, Policy/PolicyVersion and ServiceRegistryEntry/TermsCopy/FlagAnswer split as the prompt's parentheses require (28 rows in total).
- All 57 ID prefixes (28 named, 29 added) are exactly three lowercase letters and pairwise distinct; table names are the correct snake_case plurals.
- ID regex `^[a-z]{3}_[0-9a-hjkmnp-tv-z]{26}$` matches lowercase Crockford base32 (no i, l, o, u); the example `mem_01j9z6x4k7q2m8v5t3r1w0c9ab` has 26 valid characters.
- ISS block rule: part p owns ISS-(10p+1)..ISS-(10p+9); blocks for parts 0 to 21 do not overlap and match the issue-block column of 0.13.
- Cross-reference forms in 0.3 point to real FD sections (FD§3.3, 4.3, 5.3, 5.4, 5.6, 6.2, 6.4, 8.2 with 15 rows, 8.3 with G0 to G5, 10); the measurement codes in 0.5 equal the table in 0.10.4; BM0..BM9 equal 0.12; `lease.nonce_bytes`, `credit.lifetime_days`, `retention.*`, `i18n.digits_default_fa` and `ledger.checkpoint_interval_s` exist in 0.10.6.
- Test layers in 0.5 cover prompt K (unit, property, state machine, policy, adversarial, injection and XSS, RTL, load, end to end, simulation).
- Ground rules: no provider fact, price or limit is hardcoded in 0.1 to 0.7; the human-presses-Send and no-credential-storage rules appear in 0.7 (no table stores provider credentials or chat text).
- Hashing and time decisions: SHA-256 with RFC 8785 canonical JSON is consistent with amounts being strings; UTC-only storage, server-only time and `seq`-based ordering are internally consistent.

## Findings

| # | severity | file:line | defect | action |
| --- | --- | --- | --- | --- |
| 1 | major | spec/00-conventions.md:128 | Lot expiry formula used only `credit.lifetime_days`, contradicting 0.8.5 (`grant` lots use `grant.starter_lifetime_days`) and the accelerated-expiry arm `credit.lifetime_days_accelerated` of 0.10.6 | fixed |
| 2 | major | spec/00-conventions.md:136, 147, 243 | 0.6.3 said public surfaces and provenance use `vol_` handles while 0.6.4 says requesters never see them; 0.7 claimed `req_` is the only prefix besides the entity table, although `vol_` is also a prefix and is not a ULID | fixed |
| 3 | major | spec/00-conventions.md:152 | "Raw IPs are not stored" with an HMAC of an IPv4 address overstates privacy: the space is 2^32, so a key holder can recompute IPs inside the retention window (FD Principle 11, member safety) | fixed |
| 4 | minor | spec/00-conventions.md:99, 117 | Display rule covered balances and prices only; the worked example showed eta as 0.870 (rounded up), which overstates 0.869565 and is not derivable from any stated rule, so `AC-ledger-01` would be ambiguous | fixed |
| 5 | minor | spec/00-conventions.md:99 | `verification_cells` and `accepted_primary_cells` in the `v_ppm` formula were undefined (FD§4.3 defines v as audit + gold + rework per accepted primary cell) | fixed |
| 6 | minor | spec/00-conventions.md:129 | Persian numerals described as a user option; `i18n.digits_default_fa` defaults to `persian` | fixed |
| 7 | minor | spec/00-conventions.md:160, 137, 219 | Every table has an `id` with prefix, but `Parameter` has prefix `prm_` while 0.6.3 and 0.10.3 make the natural key `name` its primary key | fixed |
| 8 | minor | spec/00-conventions.md:8, 54 | 0.1 sends convention gaps to "0.4", which only defined FD issues; no row format and no rule when the 9-id block of a part is exhausted | fixed |
| 9 | minor | spec/00-conventions.md:169 | `permanent` was defined as containing no personal data, yet permanent tables (`LedgerAccount`, `CreditLot`, `AdminUser`, `AdminAction`) refer to members and admins | fixed |
| 10 | minor | spec/00-conventions.md:27, 146 | Writing rule 2 required every number to be a labeled default, which 128-bit, 256-bit and 10^6 violate; "daily" checkpoint duplicated `ledger.checkpoint_interval_s` | fixed |
| 11 | minor | spec/00-conventions.md:52 vs 0.13 S0 row | 0.4 gives the first file of a split part ids 1-3, but 0.13 lists two S0 files (`00-conventions.md`, `00-decisions.md`) with the whole block ISS-01..ISS-09, which this file already uses fully | logged-cross-part |
| 12 | minor | spec/00-conventions.md:37, 46 | Parts split over files (S5, S6) each have a top heading `# 5.` or `# 6.`; nothing prevents two files both defining `## 5.1`, making `S5.1` ambiguous | logged-cross-part |
| 13 | minor | spec/00-conventions.md:147 | Key rotation "unlinks old handles by design"; S10.* must state whether old key versions are retained, since overturn and ban decisions need to map a manifest handle back to a member | logged-cross-part |
| 14 | minor | FD§5.6 vs spec/00-conventions.md:147 | FD§5.6 says exported manifests carry the salted-hash volunteer ID that requesters never see; the requester export in S9.* and S15.* must omit or redact `vol_` | logged-cross-part |
| 15 | minor | spec/00-conventions.md:204 | Team has no membership entity or table, and requester outcome rating has no stated storage; S5.* must add them as convention gaps (0.1) | logged-cross-part |

## Not verified

- Sections 0.8 to 0.13 and `## Issues raised` were read only to resolve references, not audited; the 0.10.6 defaults (4,800; 350; 300) were not recomputed.
- Whether the platform calendar API and the bundled arithmetic fallback give correct Jalali dates on the target phones (tagged [V] in the file).
- Whether Ed25519 keys and WebAuthn passkeys work on the target phones and browsers.
- Whether web server, proxy or host logs keep raw IPs; that depends on S4.* and S10.* and on the host.
- Whether ULID monotonic order across several server processes is needed anywhere; the file only claims monotonicity within one process.
- No Founding Document claim about law or provider terms was checked.
