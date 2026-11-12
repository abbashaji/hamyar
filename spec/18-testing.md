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

## 18.6 Policy-engine tests (reference S7.*)

The rules `R1`..`R10` are data (a `Rule` table inside a `PolicyVersion`) evaluated by a small evaluator (prompt D). These tests treat `S7.*` as authoritative: where an expected value below disagrees with `S7.*`, the `S7.*` text wins, the oracle is edited in the same change, and the difference is recorded as an issue. The oracle is written independently of the evaluator, in test code, from the text of FD§5.4 and `S0.8`. [D]

### 18.6.1 Oracle (independent of the evaluator)

```
PAIRS_OK = {(P0,L0), (P1,L1), (P1,L2), (P2,L3), (P3,L0), (P3,L1), (P3,L2)}     # license pairing, FD5.3 (P3 pairing: ISS-186)
ALLOWLIST_V1 = {P0} x {L0} x {S0,S1} x {M0,M1}  U  {P1} x {L1,L2} x {S0,S1} x {M0,M1}   # 4 + 8 = 12 combinations

def oracle(job, service, template, policy_version):
    if any declaration missing or value outside its enum or (purpose, license) not in PAIRS_OK:   return REJECT R1
    if job.sensitivity in {S2, S3}:                                                               return REJECT R2
    if job.content is prohibited or task asks more than copy, Send, return text:                  return REJECT R3
    if template is not an approved, unpaused, current TemplateVersion:                            return REJECT R4
    if job.purpose == P2 and service.commercial_use_of_output != yes:                             return REJECT R5
    if job.purpose == P3 and (job.sensitivity != S0
                              or not (job.service_req == M2 or service.training_use_of_output == yes)):   return REJECT R6
    if license exceeds service flags (P1 needs open_publication_of_output == yes):                 return REJECT R7
    if (P, L, S, M) not in policy_version.allowlist:                                              return REJECT R1 (detail allowlist_miss)   # ISS-182
    return ACCEPT, stamped with policy_version
```

Reasons are rendered `policy.<rule>.<slug>` (`S0.8.4`). `R8` applies at display and lease time, `R9` at acceptance, `R10` at publication of a new `PolicyVersion`; they are tested separately below. [D]

### 18.6.2 The exhaustive combination table (`T-policy-01`)

The test enumerates every combination of purpose (4) x license (4) x sensitivity (4) x service requirement (3) = 192, with a valid approved template, content that passes `R3`, and a fixture service `svc_A` that is `approved` with every gating flag `yes` and a saved `TermsCopy`. It compares evaluator and oracle for all 192 and asserts the totals below, so a silent change in the allowlist is caught by a count as well as by a diff.

| Outcome with `svc_A` | Rows | How the count is derived |
| --- | --- | --- |
| Rejected `policy.R1.metadata_missing_or_inconsistent` (license does not pair with purpose) | 108 | (16 - 7) inconsistent pairs x 4 sensitivities x 3 requirements |
| Rejected `policy.R2.sensitivity_not_accepted` | 42 | 7 consistent pairs x 2 (`S2`, `S3`) x 3 requirements |
| Rejected `policy.R6.training_needs_m2_or_flag` (`P3` with `S1`; `S0` only) | 9 | 3 `P3` pairs x `S1` x 3 requirements |
| Rejected `policy.R1...` with detail `allowlist_miss` (passes `R1`..`R7` but is outside the allowlist) | 21 | 33 survivors reaching the allowlist (`P0` 6, `P1` 12, `P2` 6, `P3` with `S0` 9) minus 12 allowed |
| Accepted | 12 | `P0`,`L0`,{`S0`,`S1`},{`M0`,`M1`}: 4; `P1`,{`L1`,`L2`},{`S0`,`S1`},{`M0`,`M1`}: 8 |
| Total | 192 | 108 + 42 + 9 + 21 + 12 |

The 12 accepted rows are exactly the two active profiles of FD§5.7 failure mode 5 (`P0`/`P1` x `S0`/`S1` x `M0`/`M1`, with the license pairing of FD§5.3). `R3`, `R4`, `R5` and `R7` cannot fire with `svc_A`; they are covered by the tables below. [D]

### 18.6.3 Flag-dependent and ordered cases (`T-policy-02`, `T-policy-03`)

| Case | Declarations (P, L, S, M) | Service or template state | Expected |
| --- | --- | --- | --- |
| F1 | `P2`,`L3`,`S1`,`M0` | `commercial_use_of_output` = `unknown` | `policy.R5.commercial_needs_flag` (unknown is no) |
| F2 | same | `commercial_use_of_output` = `no` | `policy.R5.commercial_needs_flag` |
| F3 | same | `commercial_use_of_output` = `yes`, allowlist v1 | rejected, `R1` detail `allowlist_miss` (`P2` is locked until a `PolicyVersion` unlocks it, FD§5.3) |
| F4 | `P3`,`L1`,`S0`,`M0` | `training_use_of_output` = `unknown` | `policy.R6.training_needs_m2_or_flag` |
| F5 | `P3`,`L1`,`S0`,`M2` | allowlist v1 | rejected, `R1` detail `allowlist_miss` |
| F6 | `P3`,`L1`,`S1`,`M2` | any | `policy.R6.training_needs_m2_or_flag` (`S0` only) |
| F7 | `P1`,`L2`,`S0`,`M0` | `open_publication_of_output` = `unknown` | `policy.R7.license_exceeds_service_flags` |
| F8 | `P1`,`L1`,`S0`,`M1` pinned service | `open_publication_of_output` = `no` | `policy.R7.license_exceeds_service_flags` |
| F9 | `P0`,`L0`,`S0`,`M0` | every output flag `unknown`; `third_party_task_use` and `prohibited_content_compatible` `yes` | accepted (`L0` needs no output-publication flag) |
| O1 | `P0`,`L1`,`S3`,`M0`, no template | | `R1` (first failing rule wins) |
| O2 | `P0`,`L0`,`S3`,`M0`, free-form prompt | | `R2` (before `R4`) |
| O3 | `P2`,`L3`,`S1`,`M0`, free-form prompt, flag `unknown` | | `R4` (before `R5`) |
| O4 | `P0`,`L0`,`S2`,`M0`, prohibited content | | `R2` (before `R3`) |
| O5 | valid declarations, task text asks the volunteer to open a link, download a file, install something or enter a credential | | `policy.R3.prohibited_content` |
| O6 | valid declarations, `TemplateVersion` in `paused` or `retired`, or a prompt not from any template | | `policy.R4.template_required` |

The flag matrix (`T-policy-03`) additionally runs every gating flag key of `S0.8.3` through `yes`, `no` and `unknown`, asserting that `unknown` and `no` give identical results everywhere and that no info flag (`info.*`) ever changes an outcome (`ISS-02`).

### 18.6.4 Catalogue

| Id | Subject | Assertion | BM |
| --- | --- | --- | --- |
| `T-policy-01` | Exhaustive combinations | The 192-row table above, evaluator versus oracle, with the totals | `BM3` |
| `T-policy-02` | Rule order | Cases `O1`..`O6` and a generated set in which two or more rules fail: the reported reason is the first failing rule only | `BM3` |
| `T-policy-03` | Flags | Cases `F1`..`F9`, plus the flag matrix; `unknown` equals `no` | `BM3` |
| `T-policy-04` | Approval guard | `service.approved` is refused unless `third_party_task_use` and `prohibited_content_compatible` are `yes`, a `TermsCopy` (bytes, hash, source reference, capture date) is saved and a reviewer is recorded; with `service.min_approvers` = 2 a single approval is refused; every `FlagAnswer` is dated and points at its `TermsCopy` | `BM3` |
| `T-policy-05` | Rules are data | A fixture `PolicyVersion` that adds one allowlist row and disables nothing else changes the evaluator's outcome for exactly that row, with no code change and no restart; the rules table has one row per `R1`..`R10` per version; the evaluator contains no rule-specific branch on a rule id outside the data (static check) | `BM3` |
| `T-policy-06` | Stamp and re-check (`R9`) | A job stamped with version n and accepted under version n passes; if version n+1 tightens the rule the job touches, acceptance is refused with `reject.policy_changed` and the job is paused or stopped as `S7.*` says; if version n+1 loosens, work already done under n is not retroactively legitimized: results produced before the loosening stay judged under n | `BM3`, `BM6` |
| `T-policy-07` | Tighten and loosen (`R10`) | A tightening takes effect at once and its public entry follows within `change.tighten_publish_within_s`; a loosening without a change-log entry and a stated reason is refused; a loosening takes effect only after `policy.loosen_min_notice_days`; `change_class` is computed by the system from the diff, not supplied by the editor | `BM3` |
| `T-policy-08` | Opt-in matching (`R8`) | A volunteer with default opt-ins (`optin.default_purposes` `P0`,`P1`; `optin.default_sensitivities` `S0`,`S1`; no sensitive topic) is offered no cell outside them; adding `P2` makes `P2` cells eligible and nothing else; an attempt to lease an uncovered cell is refused without leaking its existence (`NOT_FOUND`, [V: `S9.*`]); the supply gauge per category is computed from eligible members only | `BM3`, `BM6` |
| `T-policy-09` | Template required (`R4`) | The job API has no free-form prompt field; a request that carries one is `VALIDATION_FAILED`; a job on a template version that is paused after admission suspends its unleased cells | `BM5` |
| `T-policy-10` | Prohibited content (`R3`) | The prohibited-content screen and the copy-Send-return rule are applied to every template at review time and to every input at screening time; the template review checklist contains the rule; a template whose prompt asks for more than copy, Send and return text cannot reach `approved` (`T-fsm-05`) | `BM5` |
| `T-policy-11` | Launch gate on jobs | With every `ServiceRegistryEntry` in `unreviewed`, `createJob` is refused for every combination (`policy` reason or `LAUNCH_GATE_CLOSED` as `S14.*` says) and no `Job` leaves `draft`; with `launch.member_jobs_enabled` false, member jobs are refused even for an `approved` service | `BM3` |
| `T-policy-12` | Reason codes and copy | Every `policy.<rule>.<slug>` the evaluator can emit has a `copy.*` key with `fa` and `en` text and the review marker (`T-rtl-11`); the API puts the codes in `details.reasons` | `BM3`, `BM8` |
| `T-policy-13` | Revocation in flight | When a service is `revoked`, new jobs stop at once; in-flight cells are handled as `S7.*` specifies (`cell.voided` or drained); no credit moves for a voided cell; the escrow share for voided cells is refunded at settlement | `BM3`, `BM7` |

## 18.7 Adversarial tests

### 18.7.1 Method and the guarantees under test [D]

- **Controlled interleaving.** Components expose failpoints (after read, before write, after write, before commit, after commit, before outbox relay). A scheduler enumerates or samples `test.race.schedules` interleavings of the competing requests and checks the guarantees after each. Real-concurrency stress with `test.race.workers` workers repeats the same scenarios against a real database, because a controlled scheduler cannot find every storage-level anomaly.
- **Attack scripts** call the public, member and admin APIs with crafted requests, never reaching around the API except where a test is about database privileges.
- **Exact guarantees** (the statements are the tests' pass criteria; their normative wording is owned by `S5.*` and `S6.*` [V]):

| Id | Guarantee |
| --- | --- |
| `X1` | At most one `Lease` is `active` per `Cell` at any time |
| `X2` | At most one `Submission` is `accepted` per `Lease`, and at most one per `Cell` |
| `X3` | A replayed submission (same lease and nonce) returns the stored outcome, changes nothing and emits no event |
| `X4` | Each accepted cell is paid exactly once (one `payout` per cell) |
| `X5` | Each `Escrow` settles at most once and closes at exactly 0 |
| `X6` | Each job is admitted at most once; one `escrow_hold` per job |
| `X7` | A lot's remaining amount is consumed exactly once, however many requests race for it |
| `X8` | An operation refused by a guard leaves no partial state |

### 18.7.2 Catalogue

| Id | Attack or race | Expected result | Guarantee or AC | BM |
| --- | --- | --- | --- | --- |
| `T-adv-01` | Forgery matrix: submit with a lease id that does not exist, belongs to another member, belongs to another cell, or carries another lease's nonce; guess cell ids (ids are opaque) | `NOT_FOUND`, `FORBIDDEN` or `reject.nonce_invalid` as `S9.*` says; no state change; every attempt counted by the rate limiter and logged without personal data | `AC-return-01` | `BM6` |
| `T-adv-02` | Replay: resubmit with the same lease and nonce (identical and altered body); submit after `lease.timeout_s`; submit within and beyond `lease.submit_grace_s`; reuse a nonce after expiry | Identical body: stored outcome, `X3`. Altered body: refused (`IDEMPOTENCY_KEY_MISMATCH` or `LEASE_CONFLICT`). After expiry and grace: `LEASE_EXPIRED` (`reject.lease_expired`). Inside grace and cell not re-leased: accepted into checks. Nonce reuse: `reject.nonce_invalid` | `AC-return-02` | `BM6` |
| `T-adv-03` | Double submission: N concurrent submissions for one lease, with the same and with different idempotency keys | Exactly one accepted outcome, all others return it or a conflict; one payout (`X2`, `X4`) | `AC-fsm-03` | `BM6` |
| `T-adv-04` | Idempotency abuse: the same key with a different body; the same key on another path; keys outside the allowed class; a missing key on a required route | `IDEMPOTENCY_KEY_MISMATCH`, a fresh execution scoped to its own path, `VALIDATION_FAILED`, `VALIDATION_FAILED`; no double effect | `AC-api-02` | `BM0` |
| `T-adv-05` | Copy of another donor's output: two donors submit the same text for different leases of the same or of audit-related cells; near-duplicates above `verify.duplicate_similarity_threshold` | `reject.duplicate_of_other_output` for the later one; both recorded for the abuse queue; the first is not penalized | `AC-return-04` | `BM6` |
| `T-adv-06` | Timing anomalies: submit faster than `verify.timing_min_s`; submit at exactly the threshold; submit with a clock-skewed client timestamp | Below the threshold `reject.timing_anomaly` and sampling rises (`T-unit-16`); the client clock is never used | `AC-return-05` | `BM6` |
| `T-adv-07` | Size and schema abuse: body at, over and far over `cell.envelope.max_submission_bytes` and `api.max_body_bytes`; deeply nested JSON; wrong content type; invalid UTF-8; output over `cell.envelope.max_output_chars` | `PAYLOAD_TOO_LARGE`, `UNSUPPORTED_MEDIA_TYPE`, `reject.size_exceeded`, `reject.length_out_of_bounds`, `reject.schema_invalid`; parser limits stop work before allocation | `AC-return-03` | `BM6` |
| `T-adv-08` | Leasing race: M workers lease the same queued cell; one worker leases while the cell is paused, cancelled or voided; a member at `lease.max_active_per_member` leases more | Exactly one succeeds, the rest `LEASE_CONFLICT`; paused or cancelled cells cannot be leased; the active-lease cap holds (`X1`) | `AC-fsm-03` | `BM6` |
| `T-adv-09` | Reaper versus submit at the expiry boundary; two reapers running at once; extension request racing expiry | One of {expired, submitted} wins, never both; the cell is requeued once with `attempt + 1`; a lease extends at most `lease.max_extensions` times (`X1`, `X2`) | `AC-fsm-03` | `BM6` |
| `T-adv-10` | Settlement races: `settle` and `cancel` together; `settle` twice; `settle` while the last `payout` is in flight; settlement concurrent with a late audit that overturns a cell | Escrow settles once and closes at 0; payouts either precede the settlement or are refused after it; an overturn after settlement uses `reversal`, never edits (`X4`, `X5`) | `AC-fsm-05` | `BM7` |
| `T-adv-11` | Admission races: two confirmations of one quote; two jobs competing for the last capacity; quote used after `price.quote_ttl_s`; parameter changed between quote and confirmation | One `escrow_hold` per job (`X6`); the second job is re-quoted or waitlisted, never both admitted over capacity (`T-prop-17`); an expired quote is `STATE_CONFLICT`; the quote keeps its parameter versions | `AC-admit-01` | `BM7` |
| `T-adv-12` | Expiry sweep versus spend: a spend and the sweep touch the same lot; two sweeps overlap | The lot is consumed once (`X7`); the sweep moves only the remaining amount; totals conserved (`T-prop-12`) | `AC-ledger-05` | `BM1` |
| `T-adv-13` | Cancel versus submit: a job is cancelled as a donor submits; a kill switch engages as a lease is issued | The submission is accepted and paid or refused as a unit; no credit is paid for a cell in `cancelled`; a lease issued after the switch is impossible (`kill.*` checked inside the lease transaction) | `AC-ops-08` | `BM6` |
| `T-adv-14` | Two-person bypass: one admin attempts `ledger.reversal`, `launch.signoff`, `parameter.loosen` or `killswitch.release` alone, with two sessions of the same admin, or with an admin who authored the change | Refused; a second distinct `AdminUser` is required (`security.two_person_actions`); every attempt writes an `AdminAction` | `AC-admin-02` | `BM2` |
| `T-adv-15` | Scheme confusion: a member token on `/v1/admin/*`, an admin token on a member route, an expired token, a token replayed from another device, an admin call from the member origin | `AUTH_INVALID` or `AUTH_EXPIRED`, counted by the rate limiter; admin routes are not served from the member origin | `AC-ident-08` | `BM2`, `BM4` |
| `T-adv-16` | Recovery abuse: brute-force of the recovery key; recovery start flood; a recovered identity trying to spend inside `identity.recovery_cooldown_s`; more than `identity.recovery_max_per_90d` recoveries; recovery from a freshly linked device | `RATE_LIMITED` after `ratelimit.recovery_attempts_per_day`; spending and job start refused during the cooldown; the old keys are rotated out; no response distinguishes a valid from an invalid identity | `AC-ident-02` | `BM4` |
| `T-adv-17` | Farming: many identities from one device, one IP hash, one invite tree; grant and referral loops; self-referral; bonuses to accounts with no verified cell | Limits of `S0.10.6` hold; flags raised for the abuse queue; the Reserve never goes below its floor (`T-prop-16`) | `AC-ident-06`, `AC-public-08` | `BM4`, `BM7` |
| `T-adv-18` | Collusion: two or more members cross-execute each other's audit cells and agree; a ring routes its own cells to itself | Audit assignment never gives a cell to its author or to a member of the same invite tree or device group where `S8.*` forbids it; agreement among ring members is not accepted as an audit pass when the assignment rule was broken; a gold-cell miss raises restriction | `AC-verify-03` | `BM6` |
| `T-adv-19` | Rate-limit evasion: spoofed forwarding headers, many IP hashes, many sessions, slow requests | Limits key on the trusted peer address chain defined in `S10.*` [V], never on a client-supplied header; per-member limits hold across sessions | `AC-ident-06` | `BM4` |
| `T-adv-20` | Reviewer capture: the author approves their own template; one reviewer approves twice; two reviewers from the same team approve | Refused or counted once (`T-fsm-05`); every approval is an `AdminAction`; an operator cannot approve as a reviewer unless holding both roles, and the audit trail shows it | `AC-tpl-01` | `BM5` |
| `T-adv-21` | Ledger tampering: the application role tries `UPDATE` and `DELETE` on ledger tables; an operator edits a balance column; a restored backup with an altered entry | Privileges refuse; a column edit breaks reconciliation (`T-prop-05`) and the hash chain (`T-prop-10`) within `ledger.invariant_check_interval_s` and raises `ledger.invariant_violated` and an `Alarm`; the daily checkpoint hash disagrees | `AC-ledger-12` | `BM1` |
| `T-adv-22` | Information leakage: responses and timing for existing versus non-existing ids of other members, other members' jobs and leases; error bodies; list endpoints | Same status and body shape (`NOT_FOUND`); no `mem_` id of another member appears anywhere; no total counts by default | `AC-ident-08` | `BM4` |
| `T-adv-23` | Resource exhaustion: oversized uploads, zip-like archives, regular-expression-heavy input, many simultaneous large requests from one member | Parser and regex time limits; per-member and global limits; other members' latency stays inside the `T-load-09` budget | `AC-api-04` | `BM5`, `BM9` |

## 18.8 Injection and XSS tests

### 18.8.1 Principles [D]

- **Two different questions.** (a) Is hostile text *inert* wherever the platform stores, transports or displays it (XSS, injection, spoofing)? That is a hard property: every payload in every sink. (b) Are hostile *instructions aimed at a volunteer* screened or flagged (prompt injection, prompt-injection note of FD§5.5)? That is a mechanism with a false-positive and false-negative profile, which is measured on the corpus and never claimed to be complete: the spec says the mechanisms reduce the risk and do not remove it. [D]
- **Payloads never reach a real service.** The corpus is fed to the platform's own screens, storage and renderers. It is never pasted into a real chat service by any test. [D]
- **Never execute submitted content.** Submitted text is stored and served as data (`application/json` or `text/plain`), rendered only through text-node APIs, never evaluated, never used to build markup, a query, a file path, a shell command or a header. A lint rule fails the build on any dynamic-code or raw-HTML sink that can receive submitted or requester data; `T-inj-02` runs it. [D]
- **Sinks.** Every place user-controlled text appears: the cell card, the expandable full prompt, the paste-back preview, result feedback, history, balance view, requester progress map, results download, manifest viewer, template and service review queues, audit queue, appeals and abuse queues, ledger explorer, parameter editor, change log, public pages, share cards, team names, error messages, e-mail text if the optional e-mail exists, exports. The sink list is a generated inventory (`T-inj-01` fails when a new screen of `S11.*` or `S12.*` lacks an entry). [D]

### 18.8.2 Payload corpus categories

The corpus is a versioned data file with one record per payload: `id`, `category`, `text`, `target` (`inert` or `screened`), `expected_action`. Illustrative members are given only to show the shape; the corpus is built from public lists and written by reviewers, and its completeness is not claimed. Every category is also supplied in Persian and in mixed Persian and Latin text. [D][A]

| Category | What it tries | Illustrative member (shape only) | Target |
| --- | --- | --- | --- |
| `markup` | Script elements, attribute breakout, event-handler attributes, SVG and MathML elements | an element with an event-handler attribute | `inert` |
| `url_scheme` | `javascript:` and `data:` links, protocol-relative links, link text that hides its target | a link whose scheme is not http or https | `inert`, and `screened` as a link |
| `style` | CSS injection through style attributes or text that is later placed in a stylesheet | a declaration that loads an external resource | `inert` |
| `markdown_template` | Markdown, template-literal and mustache-style placeholders; format-string tokens | double braces around a slot name | `inert` |
| `json_sql_header` | Quotes and control characters aimed at JSON, query, log and header construction, including line breaks | a value ending in a quote and a statement separator | `inert` |
| `export_formula` | Cells beginning with `=`, `+`, `-`, `@` or a tab in CSV and spreadsheet exports | a value that starts with an equals sign | `inert` (`ISS-188`) |
| `path_archive` | Path traversal in upload file names; oversized, nested or compressed uploads | a file name with parent-directory segments | `inert`, refused |
| `unicode_spoof` | Bidirectional control characters (for example the right-to-left override), zero-width characters, homoglyphs, combining-mark floods, lone surrogates, null bytes | a string containing an override control | `inert`, and normalized or stripped for display where `S11.*` says |
| `length_resource` | Very long strings, very long unbroken words, regex-heavy input | a million-character token | `inert`, refused before allocation |
| `instruction_pattern` | Text aimed at the volunteer or the model: "ignore the previous instructions", role-play framing, requests to reveal memory or connected tools, requests to send data elsewhere | the Persian for "ignore the previous instructions" (needs human review [V]) | `screened` |
| `link_and_action` | URLs, e-mail addresses, requests to open, download, install, log in, run code, send a message or visit a page | a bare URL in input data | `screened` (`screen.url_action`, `screen.max_urls_per_input`) |
| `pii_pattern` | Phone, national-id-like and card-like number patterns, e-mail addresses, names with addresses | a number pattern shaped like a card number | `screened` (`screen.pii_action`) |
| `delimiter_collision` | Input that contains the template's own delimiters or the closing delimiter, to break out of the data block | the closing delimiter of a template | `screened`, never rendered as a break-out (`S8.*` [V]) |
| `output_flag` | Submitted outputs that contain links, code to run or requests for action | an output that tells the reader to open an address | `screened` (`screen.output_url_action`, quarantine) |
| `benign` | Ordinary inputs that look hostile: URLs in a bibliography, code in a code-change job, angle brackets in a math text, Persian text with ZWNJ | a reference list with web addresses | accepted or flagged per the configured action; the rate is reported |

### 18.8.3 Catalogue

| Id | Subject | Assertion | BM |
| --- | --- | --- | --- |
| `T-inj-01` | Sink matrix | Every inert-target payload, stored through every write path (job input, glossary, submission, report text, appeal text, team name, template text, parameter and change-log reasons) and read through every sink in the generated inventory, appears in the DOM as text; no new element, attribute, handler or style is created; no script runs (verified by a navigation and a console-error trap); no content-security-policy violation is reported | `BM8` (DOM); the API half in `BM3` |
| `T-inj-02` | No dynamic evaluation | Static analysis fails the build on any raw-HTML, dynamic-code or shell sink reachable from stored user text; submitted content is never parsed as markup or code; code-change submissions are stored and compared as text and are never run by the platform | `BM0` |
| `T-inj-03` | Headers and policy | Every response has `Content-Type` with charset, `X-Content-Type-Options: nosniff`, a content-security-policy without inline script allowances, `Cache-Control: no-store` on authenticated routes, and no cookies; the front end loads no third-party host (`T-rtl-06`) [A: exact header set owned by `S10.*`] | `BM0`, `BM8` |
| `T-inj-04` | Origin isolation | The admin application is served from an origin different from the member application; a payload that executes in the member origin cannot read admin state; admin tokens are not accepted from the member origin (`T-adv-15`) | `BM2` |
| `T-inj-05` | Export injection | CSV and spreadsheet exports prefix or quote cells that begin with a formula character so that they open as text; manifests are canonical JSON with escaped strings; the escaping rule is the one `S15.*` fixes (`ISS-188`) | `BM7` |
| `T-inj-06` | Backend injection | JSON, query, log and header payloads never alter a query, a log record structure or a header; parameterized access only (static check); a payload with line breaks produces one log record | `BM0` |
| `T-inj-07` | Uploads | Path traversal names are refused or replaced by generated names; size above `job.max_upload_bytes` is `PAYLOAD_TOO_LARGE`; nested or compressed archives are refused unless `S5.*` accepts them; content type and extension are checked against the declared one; the upload is never opened by a tool that executes content | `BM5` |
| `T-inj-08` | Unicode spoofing | Bidirectional controls and zero-width characters are rendered inside an isolated, labelled run, never able to reorder surrounding interface text; identifiers and team names are normalized and compared after confusable folding where `S11.*` says [V]; the stored bytes are not altered (hash stability) | `BM8` |
| `T-inj-09` | Input screening | Each `screened` payload receives the action configured in `screen.url_action`, `screen.pii_action`, `screen.max_urls_per_input` (reject, flag for review, or accept with a flag); the reviewer sees the matched span; every `link_and_action`, `pii_pattern` and `instruction_pattern` record in the corpus is caught at the default configuration or recorded as a known miss in `S19.*` | `BM5` |
| `T-inj-10` | Delimiter collision | A payload containing the delimiter never changes the rendered prompt's structure: the render is refused or the delimiter escaped as `S8.*` specifies, and the golden structure test (`T-unit-17`) is run on every corpus record | `BM5` |
| `T-inj-11` | Output flagging | An output containing a link, code to run or a request for action is `quarantined` (`submission.quarantined`), is withheld from results, earns nothing until a reviewer releases it, and is shown to reviewers as inert text; a benign output with a link in a bibliography follows the same path and is released by a reviewer (the cost is measured, `T-inj-14`) | `BM6` |
| `T-inj-12` | Template wrapping at runtime | The prompt actually presented on the cell card equals the rendered template for that cell (hash equality with the reviewed `TemplateVersion` plus input hash); the card cannot be altered by input text; the instruction "treat the delimited block as data" is present and positioned as the template says | `BM5` |
| `T-inj-13` | Log hygiene | A payload with line breaks, control characters or personal-data patterns in any field never appears raw in logs; logs contain ids and hashes only (`T-e2e-20`) | `BM0` |
| `T-inj-14` | False-positive profile | On the `benign` category and on a reviewer-authored sample of ordinary Persian and English inputs the screens report: share rejected, share flagged, share accepted. The numbers are printed for the owners; there is no pass threshold, because the threshold is a decision (`P1M`), and the results are not claims about real traffic | `BM5` |

## 18.9 RTL and Persian rendering tests

Persian is the default locale (`i18n.default_locale` = `fa`). Every screen of `S11.*` and `S12.*` is tested in `fa` and `en`. Tests run on DOM and on screenshots, on the viewports of `test.rtl.viewports`. [D]

| Id | Subject | Assertion | BM |
| --- | --- | --- | --- |
| `T-rtl-01` | Direction and language | `lang` and `dir` are set on the root and switch with the locale; embedded Latin runs carry `dir="ltr"` or an isolation wrapper; a lint rule fails the build on physical-direction CSS properties (left, right, margin-left and the like) where a logical property exists; icons that imply direction (back, next, progress) are mirrored | `BM8` |
| `T-rtl-02` | Numerals | `i18n.digits_default_fa` = `persian`; the member can switch to `latin` and the choice persists; amounts, counters, dates and times follow the choice everywhere; numeric input accepts Latin, Persian and Arabic-Indic digits and normalizes them before validation and before hashing [A]; API fields stay Latin digits (`S0.11.1`) | `BM8` |
| `T-rtl-03` | Calendars | `fa` defaults to Jalali, `en` to Gregorian; detail views show both (`i18n.dual_calendar_detail`); the server never stores, accepts or emits Jalali strings; conversion passes a fixture table produced by an independent reference implementation, including a year boundary and a leap-year end of the last month. Example fixture: 1 Farvardin 1405 is 21 March 2026, and 21 Aban 1405 is 12 November 2026 [V: every fixture is confirmed by a human against an independent source before it is committed] | `BM8` |
| `T-rtl-04` | Mixed direction | Prompts, outputs, glossary terms and card text that mix Persian with Latin words, numbers, URLs and code are displayed with each run isolated (`bdi` or `unicode-bidi: isolate`, or `dir="auto"` for user text); code blocks are always left to right; punctuation at run boundaries does not jump sides in a screenshot of the fixture set; the same content in the paste-back box, the card and the history list renders the same | `BM8` |
| `T-rtl-05` | ZWNJ and letter variants | The zero-width non-joiner (U+200C) survives storage, API, display, copy, paste-back, manifest hashing and export; the normalization function of `S8.*` (Arabic and Persian yeh and kaf variants, digits) is used identically by comparators, duplicate detection and search; a round-trip test over a Persian corpus changes no displayed text and no stored hash [V: normalization owner `S8.*`, `ISS-189`] | `BM6`, `BM8` |
| `T-rtl-06` | Fonts and third parties | The application loads with every third-party host blocked: no font, script, style, image or analytics request leaves the origin; Persian and Latin fonts are bundled (subset covering the Persian alphabet, digits and punctuation); a glyph-coverage check renders every character of a Persian test corpus without a fallback box; if a bundled font fails, a system fallback is used and the layout holds | `BM8` |
| `T-rtl-07` | Visual regression | Screenshots of every `SCR-*` screen state (default, empty, loading, error, long text) in `fa` and `en`, light and dark if offered, at each viewport; a diff above `test.rtl.visual_diff_tolerance` fails; baselines are changed only in a reviewed commit | `BM8` |
| `T-rtl-08` | Accessibility (automated) | An automated accessibility scan finds no critical violation on any screen: names and roles for the copy, open-in-service, paste-back, decline and report controls; contrast; text resize to 200 percent without loss; no information by colour alone; reduced-motion respected | `BM8` |
| `T-rtl-09` | Keyboard and focus in RTL | Tab order follows reading order in RTL; focus is visible and never trapped; the paste-back and card actions work from the keyboard; screen-reader labels exist in the page language; a manual screen-reader script is stored with the tests and run before each release (not automatable) | `BM8` |
| `T-rtl-10` | Low bandwidth | Under `test.lowbw.profile` the first-contribution flow transfers no more than `test.lowbw.first_flow_budget_kb` on a cold cache and works on a warm cache offline up to the paste-back call; images are optional; a request that fails mid-flow shows a retry state that does not lose pasted text; the profile is arbitrary and no claim is made about any real network [V] | `BM8` |
| `T-rtl-11` | Copy lint | Every `copy.<area>.<key>` has non-empty `fa` and `en` text and the marker `needs_human_and_legal_review`; no user-facing string in either language contains "guarantee", "guaranteed" or the Persian equivalents (the stem of the word for guarantee, with and without ZWNJ forms); promises use "declared" and its Persian equivalent (Principle 11); a copy key used in code but missing from the catalogue fails the build; the Persian text is flagged for review by a Persian-speaking human, because this test checks presence and wording rules, not language quality | `BM3`, `BM8` |
| `T-rtl-12` | Clipboard fidelity | The copy button puts exactly the rendered prompt (bytes, including ZWNJ, bidirectional marks and line breaks) on the clipboard; paste-back normalizes line endings only; a prompt that exceeds `adapter.max_url_chars` is never truncated into a link, and falls back to copy-only (`adapter.copy_only`) | `BM8` |
| `T-rtl-13` | Text expansion | Persian strings 40 percent longer than their English source, very long unbroken words and four-digit Persian numerals do not clip, overlap or force horizontal scrolling at 360 px | `BM8` |
| `T-rtl-14` | Time display | A stored UTC instant displays in the device zone or the chosen IANA zone, in both calendars, and the cap or reset time next to a limit shows its local equivalent (`S0.6.2`); a zone change shows the same instant | `BM8` |
