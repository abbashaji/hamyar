# 18. Test strategy and simulation harness

*Spec part 18 · owner cell C-024 · prompt scope K · binding on every test written for Hamyar. Uses the names in `S0.*` exactly. Nothing here has been run, and nothing here is evidence about any real person, provider or law.*

## 18.1 Purpose, rules and what tests do and do not establish

**Purpose.** Define how every mechanism of the specified system is tested, how the credit model and the defenses are exercised by a simulation before real users exist, and which Given / When / Then criteria decide that a feature and a milestone are done. [D]

**Rules for every test in this part** [D]

1. Every test has an id `T-<layer>-<nn>` (`S0.5`), a layer, the milestone `BM0`..`BM9` (`S0.12`) in which it first becomes mandatory, and at least one `AC-<area>-<nn>` it supports (`S18.14`). A test without an `AC` reference is deleted or given one.
2. Every test is deterministic: time comes from an injected clock, identifiers from an injected generator, randomness from a seeded generator whose seed is printed on failure. A test that needs the wall clock, the OS entropy source or the network is rejected in review. [D]
3. No test, fixture or simulation contacts a real AI chat service, drives a volunteer's account, reads a chat page, stores a provider credential or submits on anyone's behalf (prompt ground rule 3). The "human" in every end-to-end flow is a scripted test client calling the same member API a browser calls, and the "AI service" is a stub that returns scripted text. [D]
4. No test uses real personal data, real e-mail addresses, real IP addresses or real provider terms. Fixtures are synthetic; anything that looks like a provider fact is a placeholder tagged `[V]` in the fixture header. [D]
5. Tests assert the behavior this spec defines. They do not assert that a hypothesis `[H]` is true. A test that would pass or fail depending on how humans behave is not a test; it is a measurement and belongs to `S13.*` and `S16.*` (`P1M`, `CAL`). [D]
6. Tests added by a milestone stay in CI and stay green in every later milestone (regression ratchet, `S0.12` rule 5). [D]
7. A failing ledger-invariant test (`T-prop-01`..`T-prop-16`, `T-sim-03`) blocks every merge, never gets a retry-until-green policy and is never skipped or quarantined. [D]
8. Where a test needs an expected value that this spec derives from a formula, the test recomputes it with an independent implementation written in the test code (an oracle), never by calling the function under test. [D]

**What passing tests do and do not establish** [D]

| Passing tests establish | Passing tests do NOT establish |
| --- | --- |
| The implementation matches the rules, state machines, formulas and guards written in this spec | That any hypothesis `[H]` in the Founding Document is true (for example that a contribution takes under 60 s) |
| Guards hold under replay, forgery, races and hostile input in the test environment | That real volunteers, requesters or adversaries behave like any simulated agent |
| The ledger invariants hold for every generated operation sequence | That any provider's terms, any law or any regional availability permits the use (`G0`, `[V]` for counsel) |
| The system is deployable and observable at each milestone | That the parameters are right; defaults are replaced only by the measurements in `S0.10.4` |

**Statement that governs the whole part.** Simulation output is NOT evidence about real human behavior. It is the output of a model that this spec invents, with parameters that are arbitrary stress values. It can show that a mechanism is internally consistent or breaks under a stated scenario. It can never support a claim about people, a calibration of a parameter, a pass of a launch gate or a public statement. This is repeated in `S18.12` and `S18.17` on purpose. [D]

## 18.2 Layers, tiers and test configuration

### 18.2.1 Layers

| Layer | Id prefix | Section | What it proves | Tooling class (stack-agnostic; concrete tools follow the stack chosen in `S4.*` [V]) | First mandatory |
| --- | --- | --- | --- | --- | --- |
| Unit | `T-unit` | S18.3 | Pure functions and single components, with exact worked values | Test runner of the chosen language | `BM0` |
| Property-based | `T-prop` | S18.4 | Invariants for all generated operation sequences (ledger, admission control, parameters) | Property-testing library with shrinking and a stateful (model-based) mode | `BM1` |
| State machine | `T-fsm` | S18.5 | Every machine of `S0.9` allows exactly its listed transitions and emits exactly one event per change | Table-driven generator plus model-based runner | `BM1` |
| Policy | `T-policy` | S18.6 | `R1`..`R10`, the allowlist, the registry gate | Table-driven oracle plus differential runner | `BM3` |
| Adversarial | `T-adv` | S18.7 | Forgery, replay, double submission, races, abuse | Controlled-scheduler race harness plus API-level attack scripts | `BM2` (admin side), `BM6` (execution side) |
| Injection and XSS | `T-inj` | S18.8 | Hostile text is inert in every sink and is screened or flagged by the rules | Corpus runner against API and DOM | `BM3` (screening), `BM8` (DOM) |
| RTL and Persian | `T-rtl` | S18.9 | Persian-first rendering, numerals, calendars, bidirectional text, fonts, accessibility, low bandwidth | Headless browser with DOM and screenshot checks | `BM8` |
| Load | `T-load` | S18.10 | Targets met and invariants intact under load | Load generator against an isolated production-like environment | `BM9` |
| End-to-end | `T-e2e` | S18.11 | Whole journeys across components with the stub service | Browser or API-level journey runner | `BM1` (ledger journeys), then each milestone |
| Simulation | `T-sim` | S18.12 | The credit model, defenses and parameters behave consistently under stated agent models. NOT evidence about real human behavior | The harness of S18.12 | `BM9` (a reduced ledger-only form is allowed from `BM7`) |

### 18.2.2 CI tiers [D]

| Tier | When | Contents | Blocks merge |
| --- | --- | --- | --- |
| `ci.commit` | every push | `T-unit`, `T-fsm`, `T-policy`, quick `T-prop`, `T-inj` corpus on API, `T-rtl-01`, `T-rtl-11`, lint rules of S18.8 and S18.9, API conformance of `S15.*` | yes |
| `ci.pr` | every pull request | everything in `ci.commit`, `T-adv`, smoke `T-e2e`, DOM `T-rtl`, migration forward test on an empty database and on the previous milestone's database | yes |
| `ci.nightly` | daily on main | long `T-prop`, full `T-e2e`, visual regression, short `T-load`, `T-sim` smoke scenarios | no, but a red night is a release blocker and an alarm to the owners |
| `ci.weekly` | weekly and before any release | parameter sweeps, soak and failover load, full simulation acceptance runs, backup and restore drill, secret-rotation drill | release blocker |

### 18.2.3 Test and simulation configuration

These are configuration keys of the test and simulation tooling. They are not product parameters: they never exist in a production database, never appear in the parameter editor and are not part of `S0.10.6` or `S16.*` (`ISS-183`). Names follow the regex of `S0.10.1`. Every value is an `initial configurable default`, an arbitrary stress or budget value that the owners may change; none is a finding. [D][A]

| Name | Type | Initial configurable default | Meaning |
| --- | --- | --- | --- |
| `test.prop.cases_quick` | int | 200 | Generated cases per property in `ci.commit` |
| `test.prop.cases_long` | int | 20,000 | Generated cases per property in `ci.nightly` |
| `test.prop.max_ops_per_case` | int | 60 | Operations in one generated ledger or admission sequence |
| `test.race.schedules` | int | 2,000 | Distinct interleavings explored per race test (S18.7) |
| `test.race.workers` | int | 16 | Concurrent workers in real-concurrency stress runs |
| `test.load.members` | int | 5,000 | Registered members in the load model (100 times the 50 members of Phase 1 [P], FD§9) |
| `test.load.active_fraction` | ratio | 0.20 | Share of members active on a day |
| `test.load.cells_per_active_member_day` | int | 10 (the FD§3.2 habit of about 10 cells a day) | Cells per active member per day |
| `test.load.burst_factor` | ratio | 20 | Peak-to-average ratio |
| `test.load.headroom_factor` | ratio | 10 | Safety multiple on the derived peak |
| `test.load.api_calls_per_cell` | int | 6 | Lease, card read, submit, status, feedback and balance reads per cell |
| `test.rtl.viewports` | json | `[[360,640],[768,1024],[1280,800]]` | Viewport sizes for visual and DOM tests |
| `test.rtl.visual_diff_tolerance` | ratio | 0.001 | Largest tolerated share of differing pixels per screenshot |
| `test.lowbw.profile` | json | `{"down_kbps":400,"up_kbps":100,"rtt_ms":400}` (an arbitrary stress profile, not a measurement of any network [V]) | Network throttle for low-bandwidth tests |
| `test.lowbw.first_flow_budget_kb` | int | 300 (compressed transfer for the first-contribution flow, cold cache) [H] | Page-weight budget |
| `test.coverage.branch_min` | ratio | 0.90 for the ledger, admission, policy and verification packages | Branch coverage gate |
| `test.mutation.kill_target` | ratio | 0.85 on the ledger and policy packages [H] | Mutation-testing kill rate that triggers review when missed |
| `sim.seed` | int | 1 | Master seed of a simulation run |
| `sim.replicates` | int | 20 | Seeds per sweep point |
| `sim.duration_days` | int | 90 = ceil(1.5 x `credit.lifetime_days`) so that at least one full expiry cycle completes | Simulated days |
| `sim.metrics_interval_s` | duration_s | 86,400 | Sampling interval of the metrics output |
| `sim.max_agents` | int | 20,000 | Upper bound on agents in one run |
| `sim.sweep.max_points` | int | 500 | Upper bound on grid points in one sweep |
| `sim.bootstrap_resamples` | int | 1,000 | Resamples for percentile intervals across replicates |

## 18.3 Unit tests

Unit tests assert exact values. Every number below is derived from `S0.6.1` and `S0.10.6`; the inputs of `T-unit-01` and `T-unit-02` are the illustrative inputs of FD§3.3, not measurements. [D]

### 18.3.1 The FD§3.3 worked example (`T-unit-01`, `AC-ledger-01`)

The test posts the example through the internal ledger interface and compares every line with the oracle below. It runs in `BM1` against the ledger alone and again in `BM7` end to end (`T-e2e-01`).

| Step | Inputs and formula (integers) | Expected |
| --- | --- | --- |
| Inputs | `v_ppm` = 100,000; `lambda_ppm` = 50,000; N = 240; the requester holds 300 credits = 300,000,000 ucr in lots | |
| Price per cell | `p_ucr` = 1,000,000 + 100,000 + 50,000 | 1,150,000 ucr |
| Escrow hold | `escrow_ucr` = 240 x 1,150,000 | 276,000,000 ucr; requester balance 24,000,000 ucr |
| Components | primary pay 240 x 1,000,000; verification pool 240 x 100,000; levy 240 x 50,000 | 240,000,000; 24,000,000; 12,000,000; sum equals `escrow_ucr` |
| Verification cells | `floor(24,000,000 / 1,000,000)` | 24 |
| Payouts | 264 accepted cells x 1,000,000 (`transfer`, one `payout` transaction per cell) | 264,000,000 ucr to donors |
| Settlement | `levy` 12,000,000 to the Reserve; `refund` = 276,000,000 - 264,000,000 - 12,000,000 | refund 0; escrow account balance exactly 0; `Escrow.closed` |
| Round-trip efficiency | `floor(10^12 / 1,150,000)` | 869,565 ppm |
| Admission | capacity `floor(40 x 8 x 2 x 500,000 / 10^6)` = 320; committed 240 + 24 | 264 <= 320, admitted |
| Ledger totals | Reserve gains 12,000,000; donors gain 264,000,000; requester loses 276,000,000; sum of changes | 0 |

Variants run with the same oracle: pool not a whole number of cells (`v_ppm` = 105,000 gives pool 25,200,000 and 25 cells, remainder 200,000 ucr refunded, `ISS-04`); a cancelled job after 100 accepted cells; a job where 10 primary cells end `exhausted` (`Job.failed`, `job.settled_partial`).

### 18.3.2 The unit-test catalogue

| Id | Subject | Assertion | BM |
| --- | --- | --- | --- |
| `T-unit-01` | FD§3.3 reproduction | Table 18.3.1, plus the three variants | `BM1` |
| `T-unit-02` | Admission arithmetic | With D = 40 active donors, 8 cells per donor per day, window 2 days, `admission.phi` 0.5, `admission.forecast_haircut` 0: capacity 320. A second identical job (committed 264 + 264 = 528) is refused for a 2-day window; the smallest quoted window at a one-day quantum [A] is `ceil(528 / 160)` = 4 days because capacity per day is `floor(40 x 8 x 500,000 / 10^6)` = 160 | `BM7` |
| `T-unit-03` | Identifiers | Every generated id matches `^[a-z]{3}_[0-9a-hjkmnp-tv-z]{26}$`; every prefix of `S0.7` is unique and three letters; ids are monotone within one process; a malformed id is `VALIDATION_FAILED` | `BM0` |
| `T-unit-04` | Time | Storage is UTC; `credit.lifetime_days` 60 gives `expires_at = earned_at + 5,184,000 s`; the accelerated value 14 gives 1,209,600 s; the lot uses the parameter version in force at `earned_at`; UTC day and month boundaries decide the cap windows; no function reads a client timestamp | `BM0` |
| `T-unit-05` | Hashing | `sha256:<hex>` over raw bytes; canonical JSON (RFC 8785) gives one byte string for reordered keys; amounts encode as integer strings; a known test vector set for SHA-256 and for the canonicalizer passes | `BM0` |
| `T-unit-06` | Fixed-point arithmetic | `v_ppm = ceil(10^6 x verification / accepted_primary)` never under-funds; `eta_ppm = floor(10^12 / p_ucr)`; `p_ucr` equals p in ppm; `N x p_ucr` has no rounding; displayed balances round down and displayed prices round up; no float type appears in any ledger code path (static check) | `BM1` |
| `T-unit-07` | Lots | Spending consumes lots by earliest `expires_at`, ties by `earned_at` then id; a refund restores the consumed lots with the original expiry (`ISS-07`); a lot past expiry is never spent | `BM1` |
| `T-unit-08` | Parameter constraints | Each of `C1`..`C8` has one accepting and one rejecting case; a violation is `VALIDATION_FAILED` with `details.fields`; `C8` only warns | `BM2` |
| `T-unit-09` | Parameter changes | `effective_from >= now + notice_days` for `loosen` and `neutral`; `tighten` applies at once and its change-log entry follows within `change.tighten_publish_within_s`; the wrong owner role is `FORBIDDEN`; a `loosen` needs a second `operator`; each accepted change writes one `ParameterVersion`, one `ChangeLogEntry`, one `AdminAction` and `parameter.changed` | `BM2` |
| `T-unit-10` | Error model | Every non-2xx has the single top-level `error` object with the fields of `S0.11.3`; codes and HTTP statuses match the table; `details.copy_key` resolves to an existing `copy.*` key | `BM0` |
| `T-unit-11` | Idempotency key | Length 16 to 64 and the character class are enforced; same key and body replays with `Idempotent-Replayed: true`; different body is `IDEMPOTENCY_KEY_MISMATCH`; concurrent duplicate is `IDEMPOTENCY_IN_PROGRESS`; a 5xx outcome is not stored; scope is (principal, method, path) | `BM0` |
| `T-unit-12` | Cursor | A cursor encodes `(created_at, id)` with a MAC; a tampered or expired cursor is `VALIDATION_FAILED`; `limit` above `api.page_size_max` is clamped or refused as `S15.*` says | `BM0` |
| `T-unit-13` | Rate-limit headers | `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` on every limited route; `Retry-After` on 429; the key is member id, admin id or IP hash, never a raw IP | `BM0` |
| `T-unit-14` | Volunteer handle | `vol_` plus 32 hex equals the first 128 bits of the HMAC of the member id under the versioned key; a rotated key yields different handles; no API response contains a `mem_` id of another member | `BM4` |
| `T-unit-15` | Reliability estimator | With Beta prior (`verify.reliability_prior_a`, `verify.reliability_prior_b`) and a window of `verify.reliability_window_obs` observations, the estimate in ppm is `floor(10^6 x (a + successes) / (a + b + n))`; hand-computed vectors for n = 0, 1, 50, 51 | `BM6` |
| `T-unit-16` | Adaptive sampling | After `verify.adapt.clean_streak` clean observations the rate is multiplied by `verify.adapt.step_down_ratio`; on an anomaly by `verify.adapt.step_up_ratio`; the result is clamped to `[verify.audit_rate_floor, verify.audit_rate_max]` (and the gold equivalents); tier multipliers apply before clamping; the rate never reaches zero | `BM6` |
| `T-unit-17` | Template wrapping | Golden-file rendering of every template: input data sits inside the delimiters, the data-not-instructions sentence is present, and the same input renders the same bytes | `BM5` |
| `T-unit-18` | Tokens and nonces | A lease nonce has `lease.nonce_bytes` = 16 CSPRNG bytes; only its SHA-256 is stored; session tokens are 256 bits and stored hashed; comparison is constant-time | `BM4` |
| `T-unit-19` | Comparators | Each template's audit comparator returns match, mismatch and inconclusive on hand-made pairs, including Persian text that differs only by ZWNJ or by Arabic and Persian letter variants (the normalization is defined in `S8.*` [V]) | `BM6` |
| `T-unit-20` | Automatic checks | For each template of the first set (translation with glossary, classification and extraction, summarization into a schema, code change with tests, format conversion with a validator): a valid output passes; an invalid-schema, refusal-pattern, length-out-of-bounds and wrong-language output fails with the matching `reject.*` code | `BM6` |
| `T-unit-21` | Quote and v window | v is computed over `price.v_window_days` per `job_type`; below `price.v_min_sample_cells` the quote uses `price.v_prior`; v never exceeds `price.v_cap`; a quote carries its parameter versions and expires after `price.quote_ttl_s` | `BM7` |
| `T-unit-22` | Published gauges | Round-trip efficiency, claim ratio (unexpired credit divided by verified weekly throughput) and mint-cap utilization are computed from integers, stored as versioned `MetricSnapshot` rows and never edited; the `price.eta_alarm_threshold` alarm fires below the threshold | `BM7` |
| `T-unit-23` | Trust tiers | Promotion and demotion thresholds of `trust.*`; `restricted` stores `tier_before_restriction` and restores it; cap and audit multipliers apply; status is independent of tier | `BM4` |
| `T-unit-24` | Session and recovery timers | Idle and absolute TTLs for member and admin sessions; a recovered identity cannot start jobs or spend before `identity.recovery_cooldown_s`; at most `identity.recovery_max_per_90d` recoveries | `BM4` |
| `T-unit-25` | Invite and rate limits | `invite.max_active_per_member`, `invite.tree_max_members`, `invite.tree_max_depth`, `ratelimit.device_new_members_per_day`, `ratelimit.ip_hash_new_members_per_day`, `ratelimit.invite_tree_new_members_per_day` each accept at the limit and refuse at limit + 1 with `RATE_LIMITED` or `CAP_EXCEEDED` as `S10.*` says | `BM4` |
| `T-unit-26` | Manifest | A provenance manifest contains exactly the fields of FD§5.6 as in `S9.*`, hashes match the stored bytes, the volunteer appears only as a `vol_` handle, and the no-training flag is present for `P0` and `P1` jobs where `S12.*` requires it | `BM6` |
| `T-unit-27` | Grant and referral rules | A starter grant needs `grant.required_verified_cells` verified cells; limits `grant.max_per_device`, `grant.max_per_invite_tree_per_day`, `grant.max_per_day` hold; a grant never takes the Reserve below `grant.reserve_floor_credits`; referral bonuses need `growth.referral.min_newcomer_verified_cells` and wait `growth.referral.hold_s` | `BM7` |

## 18.4 Property-based tests (ledger, admission control, parameters)

### 18.4.1 Method [D]

- **Stateful generation.** A generator produces a random sequence of up to `test.prop.max_ops_per_case` operations from the alphabet below, applies each through the internal ledger or admission interface, and after every operation checks the properties. A failing sequence is shrunk to a minimal one and stored as a permanent regression case with its seed.
- **Operation alphabet (ledger).** `create_member`, `mint` (accepted Commons cell), `grant`, `hold` (job admission), `payout` (accepted member-job cell), `settle`, `cancel`, `reservation_hold`, `reservation_activate`, `expire_sweep`, `retire_sweep`, `reserve_donation`, `reversal`, `advance_clock`, `change_parameter`, and the faults `replay_last`, `crash_before_commit` and `duplicate_with_new_key`. Operations that the guards must refuse are generated on purpose, with the expected refusal recorded.
- **Operation alphabet (admission).** `submit_quote`, `confirm_escrow`, `waitlist`, `release_waitlist`, `reserve_capacity`, `cancel_job`, `cancel_reservation`, `donor_joins`, `donor_leaves`, `advance_clock`, `change_phi`, `change_haircut`.
- **Numbers.** Amounts and counts are generated at the edges (0, 1, `K`, `K` + 1, the largest int64-safe values) as well as at random. Oracles use exact integers (`T-unit-06`).
- **Model.** A deliberately naive model (a list of accounts and a list of lots in memory, written in the test code) is run in parallel and compared with the implementation after every operation. The properties below are checked on both.
- **Mapping.** The property ids map to the `INV-L<nn>` invariants of `S6.*` one to one or many to one; `C-001` records the map at assembly [V]. Every FD§4.2 sentence has at least one property: *total credit in existence equals cumulative mint minus cumulative retired* (`T-prop-02`); *member balances plus escrow plus Reserve sum to that total* (`T-prop-01`, `T-prop-02`); *every unit traces to an accepted Commons cell* (`T-prop-08`, `T-prop-09`).

### 18.4.2 Ledger properties

| Id | Property (holds after every operation of every generated sequence) | Exact statement | BM |
| --- | --- | --- | --- |
| `T-prop-01` | Zero-sum | The sum of the signed balances of all accounts, including `issuance` (which is <= 0), equals 0 exactly | `BM1` |
| `T-prop-02` | Existence identity | Sum of `member` + `escrow` + `reserve` balances equals cumulative `mint` minus cumulative `retire`; `issuance` balance equals minus cumulative mint; `retired` balance equals cumulative retired | `BM1` |
| `T-prop-03` | Account signs | `member`, `escrow`, `reserve`, `retired` balances >= 0; `issuance` <= 0; a closed `Escrow` is exactly 0; `ledger.allow_negative_balance` is constant false | `BM1` |
| `T-prop-04` | Atomicity | An operation that fails a guard or crashes before commit changes no balance, no lot, no sequence number and writes no event; every committed `LedgerTransaction` has entries that balance pairwise (each entry is one debit and one credit of the same positive amount) | `BM1` |
| `T-prop-05` | Lots reconcile | For every member, the sum of the remaining amounts of its lots equals its account balance; no lot has a negative remainder; every lot has `expires_at = earned_at + credit.lifetime_days x 86,400 s` (or the starter lifetime for a starter grant) under the parameter version in force at `earned_at` | `BM1` |
| `T-prop-06` | Oldest-first and restoration | Consumption order is ascending `expires_at`; a `refund` restores exactly the lots the matching `escrow_hold` consumed, with their original expiry (`ISS-07`); a restored lot already past expiry is moved to the Reserve by the next `expire_sweep` and never spent | `BM1` |
| `T-prop-07` | Escrow closure | For every job, `escrow_ucr = N x p_ucr` at hold; at `settle`, payouts + levy + refund equal `escrow_ucr` exactly; the escrow account is 0 after `settle` or `cancel`; `settle` is the only operation that posts the `levy` | `BM1` (ledger part), `BM7` (job part) |
| `T-prop-08` | Mint only from accepted Commons cells | Every `mint` references one accepted Commons cell of any `cell_kind` (`ISS-03`), exactly once; its amount is 1,000,000 ucr; a cell that is later `overturned` has a `reversal` | `BM1`, `BM6` |
| `T-prop-09` | Caps on issuance | Cumulative mint in a UTC month <= `mint.monthly_cap_credits` (stored in ucr) as of the version in force; mint to one member in a UTC day <= `mint.per_member_daily_cap_credits`; `launch.minting_enabled` false means zero mints; `kill.all_minting` engaged means zero mints | `BM6` |
| `T-prop-10` | Hash chain and append-only | Recomputing `entry_hash = SHA-256(prev_hash \|\| canonical(entry))` over the whole ledger matches the stored hashes; mutating any stored entry byte, deleting an entry or reordering two entries makes verification fail at that index; no `UPDATE` or `DELETE` path exists for `ledger_entries` (privilege test) | `BM1` |
| `T-prop-11` | Idempotent replay | Replaying any committed operation with the same idempotency key, or the same natural key (one `escrow_hold` per job, one `payout` per accepted cell, one `settle` per escrow), any number of times leaves the ledger identical to one application | `BM1` |
| `T-prop-12` | Expiry conserves | `expire_sweep` moves exactly the remaining amount of each expired lot to the Reserve; the total in existence is unchanged; no credit is deleted | `BM1` |
| `T-prop-13` | Retirement | After `retire_sweep` the Reserve balance is <= `reserve.ceiling_credits` unless the excess is below `reserve.retire_min_credits`; a `retire` entry only moves Reserve credit to `retired`, never more than the excess, and is logged | `BM1` |
| `T-prop-14` | Reversal | A `reversal` mirrors its original exactly (including lot effects); it needs `ledger.reversal_min_approvers` = 2 distinct approvers; a second reversal of the same entry is refused; the original entry is unchanged; properties 01 to 05 hold after it | `BM1`, `BM2` |
| `T-prop-15` | Interleaving independence | For any set of operations on disjoint accounts, every serial order gives the same final balances and the same hash-chain validity; for operations touching shared accounts (`reserve`, `issuance`) every order gives a result that equals some serial order (serializability, using the per-ledger `seq`) | `BM1` |
| `T-prop-16` | Starter grant, Reserve floor and cap K | A `grant` or referral bonus never takes the Reserve below `grant.reserve_floor_credits`; grants pause (never print credit) when the Reserve cannot pay; a member's unexpired credit never exceeds the cap `K x trust.cap_multiplier.<tier>` except by the exemption that `S6.*` records for a `refund` restoring lots [V: `S6.*` decides whether earnings above the cap are refused or deferred; this test is parameterized by that rule, `ISS-185`] | `BM7` |

### 18.4.3 Admission-control properties

The oracle is a direct implementation of the FD§4.8 rule: a job is admitted only if the cells committed over its window are at most `admission.phi` times the forecast active capacity, where capacity over a window of w days is `floor(D x c x w x phi_ppm / 10^6)` for D active donors (those active within `admission.active_donor_window_days`), c cells per donor per day (from recent verified throughput over `admission.forecast_window_days`) and the haircut applied as `x (10^6 - haircut_ppm) / 10^6`. `S6.*` owns the algorithm; this test owns the claim that the algorithm never breaks the properties. [D][V]

| Id | Property | Exact statement | BM |
| --- | --- | --- | --- |
| `T-prop-17` | Never over-commit | For every admitted set of jobs and reservations and every window, committed cells (primary + `floor(N x v)` verification) <= capacity of that window at the time of admission | `BM7` |
| `T-prop-18` | Monotonicity | Lowering `admission.phi` or raising `admission.forecast_haircut` never admits a job that the previous setting refused, and never increases capacity | `BM7` |
| `T-prop-19` | Quote determinism and bounds | The same inputs and parameter versions give the same quote; the quoted window is at least `admission.min_window_s` and at most `admission.max_window_days` x 86,400 s, otherwise the job is `waitlisted` (`NO_CAPACITY` only where the API says so) | `BM7` |
| `T-prop-20` | Fairness | Within a deadline class, waitlist release is first-come (by waitlist position); a member never holds more than `admission.max_concurrent_jobs_per_member` running or admitted jobs, `admission.waitlist_max_per_member` waitlist places | `BM7` |
| `T-prop-21` | Reservation share | Active reservations for any day never exceed `reservation.capacity_share_cap` of that day's phi capacity; a member holds at most `reservation.max_active_per_member`; the escrow is held at booking and `reservation_activate` moves it into the job escrow without changing the total | `BM7` |
| `T-prop-22` | Cancellation | Admit then cancel (with no cell started) returns committed cells and the member balance to their previous values exactly; cells in flight are drained, never double-counted | `BM7` |
| `T-prop-23` | Waitlist liveness | If capacity rises (donors join, a job cancels) and no new demand arrives, every waitlisted job whose cells fit is quoted within `admission.waitlist_ttl_days`; a job that cannot fit expires to `cancelled` with its escrow untouched (none was taken) | `BM7` |

### 18.4.4 Pricing, verification and configuration properties

| Id | Property | Exact statement | BM |
| --- | --- | --- | --- |
| `T-prop-24` | Price arithmetic | For all inputs: `p_ucr = 10^6 + v_ppm + lambda_ppm`; `v_ppm` rounded up never gives a verification pool below the measured ratio; `eta_ppm x p_ucr <= 10^12`; `floor(pool / 10^6) x 10^6 <= pool`; escrow components sum to escrow | `BM1` |
| `T-prop-25` | Reliability estimator | The estimate is in `[0, 10^6]`, non-decreasing in successes and non-increasing in failures for fixed n, equals the prior mean at n = 0, and is unchanged by observations older than the window | `BM6` |
| `T-prop-26` | Parameter versions | Versions increase by exactly 1; a value never changes in place; for any timestamp the value in force is the version with the greatest `effective_from` not later than it; a job, lot, lease or quote keeps the version it was stamped with | `BM2` |
| `T-prop-27` | Canonical hashing | Canonical JSON is invariant under key reordering and whitespace, and `canonical(parse(canonical(x))) = canonical(x)` | `BM0` |
| `T-prop-28` | Pagination | For any list and any page size, the union of all pages equals the set, with no duplicate and no omission, while rows are inserted at the head during paging | `BM0` |
| `T-prop-29` | Policy evaluator totality | For any metadata, including malformed and missing fields, the evaluator returns exactly one outcome (accept, or reject with the reasons of the first failing rule in order), never throws and never accepts a combination outside the allowlist | `BM3` |

## 18.5 State-machine (model-based) tests

### 18.5.1 Method [D]

The machines of `S0.9` are the model. The transition tables are converted once into data (`machine`, `from`, `event`, `to`, `guard_id`, `emits`) that both the implementation's own definition and the tests load; the test data is generated from the text of `S0.9` by a script reviewed by hand, so a change to a machine is one edit to the spec table and one regeneration, never an edit in two places.

```
for each machine M, for each non-terminal-or-terminal state s, for each event e in the event alphabet of M:
    expected = table[M][(s, e)]            # a target state, or REFUSED
    put the entity into s by a legal path   # never by direct row edit
    result = apply(e)
    if expected is REFUSED:
        assert result.error.code == STATE_CONFLICT (or the guard's code)
        assert entity.state == s and entity.row_version unchanged
        assert no event emitted and no ledger entry written
    else:
        assert entity.state == expected
        assert exactly one event named e was written to the outbox in the same transaction
        assert event carries event_version, occurred_at, actor, policy and parameter versions
```

A random walk then drives each machine for many steps with events chosen at random, comparing the implementation with the model after each step. Guards that depend on other data (for example attempts left) are driven by the generator, not by stubs. [D]

### 18.5.2 Catalogue

| Id | Machine (source) | Checks beyond the generic matrix | BM |
| --- | --- | --- | --- |
| `T-fsm-01` | All machines of `S0.9` | The generic matrix above: every pair (state, event) outside the table is refused; terminal states `(T)` have no outgoing transition; two machines may share a state name and are never confused (`Cell.expired` is not `Lease.expired`) | `BM1` onward, per machine as built |
| `T-fsm-02` | Job (`S0.9.2`) | Every listed path including `draft -> screening -> rejected` with reasons in `policy.<rule>.<slug>` form; `suspended --job.resumed--> admitted\|running` returns to the state it left; `job.stop_requested` requires a `closure_reason` of the listed set; `settling --job.settled_partial--> failed` posts refunds and payouts; `cancelling --job.cancel_settled--> cancelled` leaves the escrow at 0 | `BM5` (Commons), `BM7` (member jobs) |
| `T-fsm-03` | Cell, Lease, Submission (`S0.9.3`) | `rejected` and `expired` requeue at once with `attempt + 1`; `cell.attempts_exhausted` at `cell.max_attempts`; `cell.paused` revokes a held lease first; `cell.overturned` writes a `reversal`, creates a `rework` cell and is only reachable from `accepted`; a replayed submission with the same lease and nonce returns the stored outcome and emits nothing; `submission.quarantined` withholds output from results and `submission.released_from_quarantine` is the only way out | `BM6` |
| `T-fsm-04` | Member tier and status (`S0.9.4`) | Promotion, demotion and restriction paths; `member.restriction_lifted` restores `tier_before_restriction`; status and tier change independently; a `banned` member holds no active lease | `BM4` |
| `T-fsm-05` | Template review (`S0.9.5`) | A new `Template` needs `template.min_reviewers_new` approvals from distinct reviewers who are not the author; an edit needs `template.min_reviewers_edit`; the same reviewer approving twice counts once; `paused` is entered only by a kill switch or the auto-pause rule (`template.autopause_report_count` within `template.autopause_window_s`) | `BM5` |
| `T-fsm-06` | Service review (`S0.9.6`) | `approved` is reachable only with `third_party_task_use` and `prohibited_content_compatible` both `yes` and a saved `TermsCopy`; `service.review_due` fires at `service.review_max_age_days`; `review_due` blocks new jobs at once and lets in-flight cells run for `service.review_grace_days`, then `service.review_lapsed`; `suspended --service.resumed--> approved` only when the cause was a kill switch | `BM3` |
| `T-fsm-07` | Appeal (`S0.9.7`) | Filing inside `appeal.window_days` only; assignee is never the original decider; bans and template rejections need `awaiting_second_review`; `appeal.max_per_decision` holds | `BM6` |
| `T-fsm-08` | Audit, Escrow, Reservation, Report, `LaunchGateItem`, kill switch (`S0.9.8`) | Each table row of `S0.9.8`; `Escrow.closed` only at balance 0; `Reservation.expired` returns its escrow; `LaunchGateItem` cannot reach `signed_off` without evidence and `launch.min_signoffs` distinct admins; a kill switch release needs a second operator | `BM2` onward |
| `T-fsm-09` | Outbox atomicity | With a failure injected between the state write and the event write (and between event write and commit), state and outbox are either both changed or both unchanged; after a crash the relay delivers each outbox row at least once and consumers are idempotent | `BM0` (generic), then per machine |
| `T-fsm-10` | Cross-machine invariants | A `Job.cancelled` has no cell in `queued`, `leased` or `submitted`; a `Cell.leased` has exactly one `Lease.active`; a `Lease.active` has a `Cell.leased`; an `accepted` cell has exactly one accepted `Submission`; a `Job.completed` has all primary cells `accepted` and escrow 0 | `BM6`, `BM7` |
| `T-fsm-11` | Coverage gate | Every transition of every machine is exercised by at least one test, measured by the event names of `S0.9`; the CI job fails with the list of uncovered transitions | `BM1` onward |
