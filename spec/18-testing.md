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
