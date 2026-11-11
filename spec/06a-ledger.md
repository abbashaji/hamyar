# 6. Credit, Ledger and Pricing

*Spec part 6, file 06a · owner cell C-005 · prompt scope C except admission control, which is file 06b (owner C-006). Written against Founding Document draft v0.1 (FD) and `spec/00-conventions.md` (S0). Nothing here is legal advice; credit is not money, property or an entitlement, and its legal characterization is [V] for counsel (FD§4.1).*

## 6.1 Scope, inputs and reading rules

**In scope** [D]: the append-only double-entry ledger (accounts, entry types, posting rules, lots, escrow, settlement, refunds on cancel, levy, expiry, retirement, per-member cap K, starter grant G); the FD§4.2 invariants as continuous automated checks with alarms and responses; the numeric representation; the price p = 1 + v + lambda with the measurement of v, eta, the claim ratio and mint-cap utilization; prospective-only parameter changes with a public change log; a worked example and test specification for FD§3.3.

**Out of scope** (owned elsewhere): admission control, capacity forecast, phi, completion-window quotes, waitlist, the capacity side of reservations and fairness (file 06b); the state machines themselves (`S5.*`; this file adds only ledger guards and effects); trust-tier computation (`S10.*`); public pages and API operations (`S12.*`, `S15.*`); screens and copy (`S11.*`).

Reading rules [D]:

1. Names, enums, event names, ID prefixes and parameter names are those of S0, used exactly. Names this file needs that S0 lacks are listed in 6.17 and in `## Issues raised` as convention gaps.
2. Amounts are integers in micro-credits (`ucr`; 1 credit = 1,000,000 ucr); ratios are integers in ppm. A decimal appears only where a sentence says 'displayed'.
3. Every number is derived by the formula next to it or is a named parameter whose `initial configurable default` is in S0 0.10.6. No number in this file is a measurement; FD§3.3 inputs are illustrations (FD§3.3 header).
4. 'Commons cell' means a cell of a job with `is_commons` = true (name required from `S5.*`, see 6.17). 'Member job' means any other job.
5. Phase 1 is a configuration of everything below, not a reduced version of it (ground rule 7). Every build ships with `launch.minting_enabled`, `launch.member_jobs_enabled` and `launch.members_may_join` set to false (S0 0.12); the posting code refuses to mint or to hold escrow while the relevant switch is false.

## 6.2 Decisions at a glance

| # | Decision | Tag | Basis |
| --- | --- | --- | --- |
| LD-01 | One global append-only ledger in integer micro-credits, hash-chained, with a single gap-free sequence | [D] | FD§4.2; S0 0.6.1 |
| LD-02 | The five account types of S0 0.8.5. No entry type moves credit from one member to another; the only member-to-member effect is a `transfer` out of a job's escrow | [D] | FD§4.2 |
| LD-03 | Donors are paid at acceptance, one `transfer` per accepted cell; settlement posts only the levy and the refund | [D] | ISS-09 |
| LD-04 | Escrow is exactly N x `p_ucr` and is tracked in three bookkeeping budgets: primary, verification pool, levy | [D] | FD§4.3; FD§3.3 |
| LD-05 | A verification cell is paid from the job's pool, then from the job's levy budget, never from mint or from the Reserve; the scheduler may not create a verification cell the budgets cannot pay | [D][A] | ISS-61 |
| LD-06 | Spending order is earliest expiry first; escrow drains its slices in the same order; a refund restores the original lots with their original expiry | [D] | FD§4.5; ISS-07; ISS-63 |
| LD-07 | Every earning event creates its own lot; a lot expires after the lifetime fixed at `earned_at` | [D] | FD§4.5 |
| LD-08 | K bounds 'owned' credit (unexpired balance plus the member's own open escrow) and is enforced by a headroom reservation at lease time, so acceptance never fails for lack of headroom | [D][A] | FD§4.5; ISS-63 |
| LD-09 | Acceptance of a cell and its mint or payout are one atomic database transaction; there is no 'accepted but unpaid' state | [D][A] | FD§4.2 |
| LD-10 | Starter grant: once per member for life, after one verified contribution that was not checked by automatic checks alone, funded only from the Reserve; grants pause when the Reserve cannot pay | [D] | FD§4.6 |
| LD-11 | Retirement of Reserve excess above `reserve.ceiling_credits` is the only way credit leaves existence; each retirement is an entry and a public log line | [D] | FD§4.2 |
| LD-12 | v is measured per job type over a trailing window; below the minimum sample the prior applies; a measured value is capped; a new v takes effect after notice | [D] | FD§4.3 |
| LD-13 | A violated critical invariant engages `kill.all_minting` and `kill.all_new_jobs` automatically; releasing them needs two operators | [D][A] | prompt C |
| LD-14 | Every object keeps the parameter versions it was created under (lot, escrow, lease, quote); changes are prospective | [D] | FD Principle 5 |
| LD-15 | Reversals are new entries approved by two operators; the original is never edited. A reversal can fail to recover spent credit; the shortfall is recorded and published, not hidden | [D] | ISS-62 |

## 6.3 Numeric representation

### 6.3.1 Types [D]

S0 0.6.1 fixes the unit (integer `ucr`, scale 10^6, ratios in ppm). This section adds the rules that make it safe to implement.

| Quantity | Type | Suffix | JSON | Rule |
| --- | --- | --- | --- | --- |
| Amount | signed int64 | `_ucr` | integer string | Never float, decimal or JavaScript number; database column `bigint` |
| Price per cell | int64 | `p_ucr` | integer string | Numerically equal to p in ppm because 1 credit = 10^6 ucr (S0 0.6.1) |
| Ratio (v, lambda, eta, phi) | int64 | `_ppm` | integer | 1.0 = 1,000,000; decimals only at the display edge |
| Count (cells, entries) | int64 | none | integer | |
| Aggregate over many accounts | 128-bit or arbitrary precision | `_ucr` | integer string | Used only inside checks and gauges |

Rules [D]:

1. No floating-point type appears in the ledger, pricing or invariant modules. A lint rule fails the build on `float`, `double` or a language-level `Number` in those modules.
2. Division exists only at the sites in 6.3.2, through the helpers `div_floor(a, b)` and `div_ceil(a, b)`, both of which reject `b <= 0`. No other division is allowed.
3. Every multiplication uses `checked_mul`; an overflow aborts the transaction with `INTERNAL` and raises an alarm. Inside the validated parameter ranges it cannot happen: the largest job product is `admission.max_job_cells` (<= 100,000 by validation) x `p_ucr` (<= 3,000,000 because v <= 1 and lambda < 1) = 3 x 10^11, against a limit of about 9.2 x 10^18.
4. A negative amount is never stored; direction is carried by the debit and credit accounts. An entry amount is always > 0, so a zero refund or a zero levy posts no entry.

### 6.3.2 Every division in the credit system [D]

| Site | Formula (integers) | Rounding | Why |
| --- | --- | --- | --- |
| Measured v | `v_ppm = div_ceil(10^6 x V, A)` | up | The pool is never under-funded (S0 0.6.1) |
| Round-trip efficiency | `eta_ppm = div_floor(10^12, p_ucr)` | down | Never overstate what a member gets |
| Blended eta | `div_floor(10^12 x sum_A, sum over t of (A_t x p_ucr_t))` | down | Same |
| Claim ratio (weeks, in ppm) | `div_floor(claims_ucr x throughput_window_days, 7 x accepted_cells)` | down | Gauge only |
| Mint-cap utilization | `div_floor(10^6 x minted_ucr, cap_ucr)` | down | Gauge only |
| Effective member cap | `K_eff_ucr = div_floor(K_ucr x cap_multiplier_ppm, 10^6)` | down | Never allow more than the tier allows |
| Automatic mint-cap cut | `new_cap_ucr = div_floor(cap_ucr x (10^6 - cut_ppm), 10^6)` | down | A cut is never smaller than declared |
| Display of balances | credits, at most 2 decimals | down | Never show more than is held |
| Display of prices and escrow | credits, exact expansion (at most 6 places), trailing zeros trimmed | exact | The quote shown is the amount escrowed |

### 6.3.3 Why FD§3.3 is exact under this representation [D]

The escrow of a job of N primary cells is `escrow_ucr = N x (1,000,000 + v_ppm + lambda_ppm)`, a product and a sum of integers, so it is exact for every N, v and lambda. Its three parts are `N x 1,000,000` (primary pay), `N x v_ppm` (verification pool) and `N x lambda_ppm` (levy), and their sum is the escrow with no remainder. Rounding happens only where a ratio is measured (v, ceiling) and where a gauge is displayed. For the FD§3.3 inputs (v = 0.10, lambda = 0.05, N = 240) every part is a whole number of credits: 240, 24 and 12. That is a property of those inputs (240 x 0.10 = 24 exactly), not of the model; 6.14 states what happens when the pool is not a whole number of cells. The line-by-line reproduction is 6.15 and the test is `AC-ledger-01` / `T-unit-01` (6.16).
