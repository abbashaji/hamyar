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
| LD-02 | The five account types of S0 0.8.5. No entry type moves credit from one member to another; the only member-to-member effect is a `transfer` out of a job's escrow (and the restitution reversal of 6.6.3 after an escrow has closed) | [D] | FD§4.2 |
| LD-03 | Donors are paid at acceptance, one `transfer` per accepted cell; settlement posts only the levy and the refund | [D] | ISS-09 |
| LD-04 | Escrow is exactly N x `p_ucr` and is tracked in three bookkeeping budgets: primary, verification pool, levy | [D] | FD§4.3; FD§3.3 |
| LD-05 | A verification cell is paid from the job's pool, then from the job's levy budget, never from mint or from the Reserve; the scheduler may not create a verification cell the budgets cannot pay | [D][A] | ISS-61 |
| LD-06 | Spending order is earliest expiry first; escrow drains its slices in the same order; a refund restores the original lots with their original expiry | [D] | FD§4.5; ISS-07; ISS-63 |
| LD-07 | Every earning event creates its own lot; a lot expires after the lifetime fixed at `earned_at` | [D] | FD§4.5 |
| LD-08 | K bounds 'owned' credit (unexpired balance plus the member's own open escrow) and is enforced by a headroom reservation at lease time, so acceptance never fails for lack of headroom | [D][A] | FD§4.5; ISS-63 |
| LD-09 | Acceptance of a cell and its mint or payout are one atomic database transaction; there is no 'accepted but unpaid' state | [D][A] | FD§4.2 |
| LD-10 | Starter grant: once per member for life, after one verified contribution that was not checked by automatic checks alone, funded only from the Reserve; grants pause when the Reserve cannot pay | [D] | FD§4.6 |
| LD-11 | Retirement of Reserve excess above `reserve.ceiling_credits` is the only way credit leaves existence, apart from a two-operator `reversal` that cancels a `mint` (6.6.3); each retirement is an entry and a public log line | [D] | FD§4.2 |
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
| Automatic mint-cap cut | `new_cap_ucr = 10^6 x div_floor(cap_ucr x (10^6 - cut_ppm), 10^12)` (a whole number of credits, as the type `credits` requires) | down | A cut is never smaller than declared |
| Forecast redeemable capacity | `div_floor(phi_ppm x accepted_cells x 30, 10^6 x throughput_window_days)` | down | Alarm only (6.11.5) |
| Retirement interval index | `div_floor(now_s, reserve.retire_interval_s)` | down | Idempotency key only (6.9.3) |
| Effective levy gauge | `div_floor(levy_posted_ucr, accepted_primary_cells)` (levy per cell in ucr equals ppm) | down | Gauge only (6.7.3) |
| Display of balances | credits, at most 2 decimals | down | Never show more than is held |
| Display of prices and escrow | credits, exact expansion (at most 6 places), trailing zeros trimmed | exact | The quote shown is the amount escrowed |

### 6.3.3 Why FD§3.3 is exact under this representation [D]

The escrow of a job of N primary cells is `escrow_ucr = N x (1,000,000 + v_ppm + lambda_ppm)`, a product and a sum of integers, so it is exact for every N, v and lambda. Its three parts are `N x 1,000,000` (primary pay), `N x v_ppm` (verification pool) and `N x lambda_ppm` (levy), and their sum is the escrow with no remainder. Rounding happens only where a ratio is measured (v, ceiling) and where a gauge is displayed. For the FD§3.3 inputs (v = 0.10, lambda = 0.05, N = 240) every part is a whole number of credits: 240, 24 and 12. That is a property of those inputs (240 x 0.10 = 24 exactly), not of the model; 6.14 states what happens when the pool is not a whole number of cells. Where the rounding remainder goes: the only rounding that reaches an amount is the `div_ceil` in v; the surplus it puts in the pool (under N ucr for a job of N primary cells, because each cell is over-charged by less than 1 ucr) stays in escrow as unspent pool and returns to the requester in the refund at settlement (6.7.3). The levy `N x lambda_ppm` is a product of integers and has no remainder, and no entry splits an amount, so no entry has a remainder to allocate; floored values (K_eff, the cap cut, gauges, displayed balances) are never posted as amounts. The line-by-line reproduction is 6.15 and the test is `AC-ledger-01` / `T-unit-01` (6.16).

## 6.4 Accounts, lots and escrow slices

### 6.4.1 Accounts [D]

`ledger_accounts` (entity `LedgerAccount`, prefix `lac_`, retention `permanent`):

| Column | Type | Constraint |
| --- | --- | --- |
| `id` | text | primary key, `lac_` |
| `account_type` | text | CHECK in `member`, `escrow`, `reserve`, `issuance`, `retired` (S0 0.8.5) |
| `member_id` | text | not null iff type `member`; unique |
| `escrow_id` | text | not null iff type `escrow`; unique |
| `balance_ucr` | bigint | Cache of credits minus debits; written only by the posting function; verified by INV-L03 |
| `created_at`, `row_version` | | |

Constraints: partial unique indexes allow exactly one row each of type `reserve`, `issuance` and `retired`. CHECK `balance_ucr >= 0` for `member`, `escrow`, `reserve`, `retired`; CHECK `balance_ucr <= 0` for `issuance` (its balance is minus cumulative mint). `ledger.allow_negative_balance` is a constant false (S0 0.10.6), so no code path may bypass these checks. A member account is created with the `Member`; an escrow account in the same transaction as its first `escrow_hold`.

Sign convention: a credit leg increases `balance_ucr` and a debit leg decreases it, for every type. `issuance` therefore falls below zero as credit is minted, and the sum of all balances is always 0 (INV-L01).

### 6.4.2 Credit lots [D]

A lot is a dated portion of one member's balance (entity `CreditLot`, `lot_`). Lots are a projection of entries: every column that changes can be recomputed from `lot_movements` (INV-L05).

| Column | Type | Constraint |
| --- | --- | --- |
| `id`, `member_id`, `ledger_account_id` | text | `lot_`; the owning member account |
| `origin_entry_id` | text | The `mint`, `transfer` or `grant` entry that created it |
| `origin_kind` | text | `mint`, `transfer`, `grant_starter`, `grant_referral` |
| `initial_ucr` | bigint | > 0 |
| `remaining_ucr` | bigint | 0 <= remaining <= initial |
| `earned_at`, `expires_at` | timestamptz | `expires_at > earned_at` |
| `lifetime_param_name`, `lifetime_param_version` | text, int | The parameter and version that fixed `expires_at` (LD-14) |
| `is_grant` | bool | True for starter and referral grants (non-transferable, `grant.non_transferable`) |
| `status` | text | `active` (remaining > 0), `exhausted` (remaining = 0), `expired` (swept); a refund that restores credit to an `exhausted` or `expired` lot sets it back to `active` |

Indexes: spending index `(ledger_account_id, expires_at, earned_at, id) WHERE remaining_ucr > 0`; sweep index `(expires_at) WHERE remaining_ucr > 0`.

Lifetime at creation [D]: `mint` and `transfer` lots use `credit.lifetime_days`, or `credit.lifetime_days_accelerated` when the member is assigned to the accelerated-expiry arm (`ff.experiment.expiry_arm`, assignment logged by S13.*); `grant_starter` lots use `grant.starter_lifetime_days`; `grant_referral` lots use `credit.lifetime_days`. `expires_at = earned_at + lifetime_days x 86,400 s` (S0 0.6.2). A lot earned by transfer starts its own clock at the acceptance time: credit that is earned again after being spent is new credit, so expiry bears on idle holdings, not on credit in circulation [H: this may weaken the expiry incentive; measured by the claim ratio and the share of credit that expires, `P1M`].

### 6.4.3 Lot movements and escrow slices [D][A]

Because a refund must restore original expiry dates (ISS-07), credit held in escrow keeps the identity of the lots it came from. Table `lot_movements` (new entity `LotMovement`, prefix `lmv_`, permanent, append-only; a convention addition, 6.17):

| Column | Type | Meaning |
| --- | --- | --- |
| `id`, `ledger_entry_id` | text | The entry that caused the movement |
| `lot_id` | text | The lot concerned |
| `holder_account_id` | text | The member account (the lot's own remaining) or an escrow account (a slice of that lot) |
| `delta_ucr` | bigint | Non-zero; positive adds to the holder, negative removes |

`lot.remaining_ucr` = sum of `delta_ucr` where the holder is the lot's own account. A slice of lot L held by escrow E = sum of `delta_ucr` where the holder is E. For every entry, the sum of deltas over member holders equals (credit to member accounts minus debit from member accounts) and the sum over escrow holders equals the same for escrow accounts (INV-L05, INV-L06). Reserve, issuance and retired accounts have no lots: credit in the Reserve is fungible.

Spending order [D]:

```
function pick_lots(account, amount_ucr, now, exclude_grants):
    rows = SELECT * FROM credit_lots
           WHERE ledger_account_id = account AND remaining_ucr > 0 AND expires_at > now
                 AND (NOT exclude_grants OR is_grant = false)
           ORDER BY expires_at ASC, earned_at ASC, id ASC   -- earliest expiry first
           FOR UPDATE
    need = amount_ucr; moves = []
    for lot in rows:
        take = min(lot.remaining_ucr, need)
        moves.append((lot.id, -take)); need -= take
        if need == 0: return moves
    raise INSUFFICIENT_CREDIT        -- only unexpired credit can be spent

function pick_slices(escrow_account, amount_ucr):
    -- same ordering over the escrow's slices (by the lot's expires_at); used by transfer and levy
```

FD§4.5 says 'oldest-first'. With one lifetime that is the same as earliest-expiry-first; with several lifetimes (a 14-day starter lot, a 60-day lot, the accelerated arm) only earliest-expiry-first achieves what the FD wants, that the least credit expires. The order is therefore by `expires_at`, with `earned_at` and `id` as deterministic tie-breakers (ISS-63). Expired credit (`expires_at <= now`) can never be spent, even before the sweeper has moved it (6.9).

Escrow disbursements (`transfer`, `levy`) drain slices in the same earliest-expiry-first order, so what is left for the final `refund` is the longest-lived part, which is the most favorable restoration for the requester [D]. A `refund` restores each remaining slice to its original lot (`delta_ucr` positive on the lot's own account, negative on the escrow). A restored lot that has already passed `expires_at` is moved to the Reserve by the next sweep (ISS-07); escrow neither extends nor stops expiry.

Lineage [D]: within one `transfer` entry the slices removed from escrow are the parents of the lot created for the donor. These rows are the only per-unit provenance the ledger keeps (6.14 states what that does and does not prove).

### 6.4.4 Escrow record [D]

`escrows` (entity `Escrow`, `esc_`; the ledger-side columns). One row per job or reservation. Counters are caches written only by the posting function and recomputed by INV-L06 and INV-L07.

| Column | Meaning |
| --- | --- |
| `ledger_account_id`, `job_id` or `reservation_id`, `state` | State `open`, `settling`, `closed` (S0 0.9.8) |
| `cells_n` | N, primary cells covered |
| `quote_p_ucr`, `quote_v_ppm`, `quote_lambda_ppm`, `quote_snapshot_ids` | The price in force when the quote was made (6.11.6); frozen |
| `funded_ucr` | N x `quote_p_ucr`, set at the hold |
| `primary_budget_ucr`, `pool_budget_ucr`, `levy_budget_ucr` | N x 1,000,000; N x `quote_v_ppm`; N x `quote_lambda_ppm` |
| `paid_primary_ucr` | Sum of `transfer` for accepted primary cells |
| `paid_pool_ucr`, `paid_levy_budget_ucr` | Sum of `transfer` for accepted verification cells, drawn from the pool and then from the levy budget (LD-05) |
| `levy_posted_ucr`, `refunded_ucr` | Settlement postings |
| `reversed_in_ucr` | Sum of `reversal` entries credited into this escrow (6.6.3); 0 unless a payout was reversed while the escrow was `open` or `settling` |
| `accepted_primary_cells`, `accepted_verification_cells` | Counts, for settlement |

Identity (INV-L06): `balance = funded_ucr + reversed_in_ucr - paid_primary_ucr - paid_pool_ucr - paid_levy_budget_ucr - levy_posted_ucr - refunded_ucr`, and the balance is 0 when `state` = `closed` (INV-L07).

## 6.5 Entries, transactions, sequencing

### 6.5.1 Schema [D]

`ledger_entries` (`LedgerEntry`, `lge_`, permanent, no `updated_at`, no delete path):

| Column | Type | Constraint |
| --- | --- | --- |
| `id`, `seq` | text, bigint | `seq` unique, gap-free, starts at 1 |
| `ledger_transaction_id` | text | not null |
| `entry_type` | text | CHECK in the 11 types of S0 0.8.5 |
| `debit_account_id`, `credit_account_id` | text | different accounts; types must match the matrix in INV-L16 |
| `amount_ucr` | bigint | > 0 |
| `job_id`, `cell_id`, `escrow_id`, `lot_id` | text | nullable references used for traceability |
| `reverses_entry_id` | text | Unique where not null (an entry is reversed at most once) |
| `owned_after_ucr`, `cap_ucr` | bigint | Set on `mint`, `transfer`, `grant`: the member's owned credit after the entry and the effective cap used (6.8) |
| `month_mint_after_ucr`, `mint_cap_ucr`, `member_day_mint_after_ucr` | bigint | Set on `mint` (6.8) |
| `reserve_balance_after_ucr`, `reserve_ceiling_ucr` | bigint | Set on `grant` and `retire` |
| `parameter_versions` | json | Name-to-version map of every parameter the posting read |
| `prev_hash`, `entry_hash` | text | 6.5.3 |
| `created_at` | timestamptz | Server time; order is `seq`, never time (S0 0.6.2) |

`ledger_transactions` (`LedgerTransaction`, `txn_`, permanent): `id`, `txn_kind` (CHECK in the S0 0.8.5 list), `natural_key`, `requested_by` (`principal_type` plus opaque id), `admin_action_id` (null unless an admin approved it), `shortfall_ucr` (default 0; used only by `reversal`, 6.6), `created_at`. Unique `(txn_kind, natural_key)`: this is the idempotency barrier. `ledger_head` is a single row `(seq, entry_hash)`.

### 6.5.2 Append-only enforcement [D][A]

1. The database role used by the application can INSERT into `ledger_entries`, `ledger_transactions` and `lot_movements` only through the posting function; it has no UPDATE or DELETE privilege on them. Triggers raise an error on UPDATE or DELETE as a second barrier.
2. `ledger_accounts.balance_ucr`, `credit_lots` and the `escrows` counters are updated only inside the posting function. Admin tools and the ledger explorer have read-only access; there is no administrative write path to ledger tables (a correction is a `reversal`, 6.6).
3. Honest limit: a database superuser, or whoever controls the host, can bypass 1 and 2. The hash chain and the published daily checkpoint make such an edit detectable by anyone holding a checkpoint (INV-L14); they do not make it impossible. The threat is carried to `S10.*` (ledger tampering, insider risk).

### 6.5.3 Hash chain [D]

`entry_hash = SHA-256(prev_hash followed by canonical(entry))`, where `canonical(entry)` is the RFC 8785 canonical JSON of every entry column except `entry_hash` (S0 0.6.4); `prev_hash` of the first entry is 64 zero hex digits. Every `ledger.checkpoint_interval_s` (default 86,400 s) the head `(seq, entry_hash)` is stored as a `MetricSnapshot` of kind `ledger_checkpoint` and published on the public ledger page (`S12.*`).

### 6.5.4 The posting function and its guarantees [D][A]

Every change to credit goes through one function; nothing else writes ledger tables.

```
function post(txn_kind, natural_key, requested_by, build):
    repeat up to 3 times (a constant [A]) on SERIALIZATION_FAILURE:
      BEGIN ISOLATION LEVEL SERIALIZABLE
        t = SELECT * FROM ledger_transactions WHERE txn_kind = ? AND natural_key = ?
        if t exists: COMMIT; return stored result of t                -- exactly once
        head = SELECT * FROM ledger_head FOR UPDATE                    -- single writer, orders seq
        lock affected accounts FOR UPDATE in ascending account id      -- no deadlocks
        plan = build(read view)       -- entries, lot moves, escrow counter deltas, shortfall
        check_guards(plan)            -- the guards of 6.6; failure aborts, nothing is written
        insert LedgerTransaction
        for e in plan.entries in order:
            e.seq = head.seq + 1; e.prev_hash = head.entry_hash
            e.entry_hash = sha256(e.prev_hash + jcs(e)); head = (e.seq, e.entry_hash)
            insert e; insert its lot_movements; update balance caches, lots, escrow counters
        run_commit_checks(plan)       -- INV-L01, L04, L05, L06, L11, L12, L16 on touched rows
        update ledger_head; insert outbox events ledger.entry_committed (one per entry)
      COMMIT
```

Guarantees (stated exactly):

1. **Exactly once.** A transaction with the same `(txn_kind, natural_key)` is posted at most once; a retry or replay returns the stored result and emits no event. Natural keys are deterministic (6.6), so two workers racing on the same cell, job or lot cannot both post.
2. **Atomic.** All entries, lot movements, counter updates and outbox events of a transaction commit together or not at all. A cell's change to `accepted` and its mint or payout are in the same database transaction (LD-09); the storage choice in `S4.*` must therefore keep ledger and cell state in one transactional store, or give up the rule explicitly [A].
3. **Serializable and ordered.** Postings are totally ordered by `seq`. The single `ledger_head` lock makes posting a serial section [A]; at the volume this system targets (the FD§3.3 illustration implies 40 donors x 8 cells = 320 cells a day, an illustration and not a forecast) that is expected to be sufficient, and the throughput limit is measured in `T-load-*` (`S18.*`).
4. **No partial effects on failure.** A guard failure returns the API error of S0 0.11.3 (`INSUFFICIENT_CREDIT`, `CAP_EXCEEDED`, `LAUNCH_GATE_CLOSED`, `KILL_SWITCH_ENGAGED`, `STATE_CONFLICT`) and changes nothing.
5. **Clock independence.** Guards that read time use one server timestamp `now` taken at the start of the transaction; `now` is stored in `created_at` of every entry of that transaction.

## 6.6 Posting rules

One row per operation. Entry types and transaction kinds are those of S0 0.8.5; 'M' is the member account, 'E' an escrow account, 'R' the Reserve, 'I' issuance, 'X' retired. Amounts are ucr. [D]

| Operation | Trigger (S0 event) | `txn_kind` | Entries (debit -> credit, amount) | Lot effect | Natural key |
| --- | --- | --- | --- | --- | --- |
| Mint | `cell.checks_passed` or `cell.audit_passed` on a Commons cell of any `cell_kind` (ISS-03) | `mint` | `mint` I -> M, 1,000,000 | creates lot, `earned_at` = now | `mint:{cell_id}` |
| Payout | the same events on a member-job cell, any `cell_kind` charged to that job | `payout` | `transfer` E -> M, 1,000,000 | drains escrow slices, creates donor lot | `payout:{cell_id}` |
| Hold | `job.escrow_confirmed` | `hold` | `escrow_hold` M -> E, N x `p_ucr` | consumes lots (`pick_lots`), creates slices | `hold:{job_id}` |
| Reservation booking | `reservation.held` | `hold` | `escrow_hold` M -> E(reservation), N x `quote_p_ucr` | as hold | `hold:{reservation_id}` |
| Reservation activation | `reservation.activated` | `reservation_activate` | `escrow_release` E(reservation) -> E(job), N' x `quote_p_ucr`; `refund` E(reservation) -> M for the unused rest | slices move; refund restores | `activate:{reservation_id}` |
| Settlement | `job.settled`, `job.settled_partial`, or `job.stop_requested` after drain | `settle` | `levy` E -> R, `levy_posted`; `refund` E -> M, rest (6.7) | levy drains slices; refund restores lots | `settle:{job_id}` |
| Cancel | `job.cancel_settled`; `reservation.cancelled`; `reservation.expired` | `cancel` | as settlement; for a reservation only the `refund` | as settlement | `cancel:{job_or_reservation_id}` |
| Expiry | sweeper (6.9) | `expire` | `expire` M -> R, lot remaining | lot remaining to 0, status `expired` | `expire:{lot_id}:{k}`, k = number of earlier `expire` entries of that lot (0 at the first sweep; a lot restored by a refund after a sweep is swept again as k + 1) |
| Retirement | scheduler (6.9) | `retire` | `retire` R -> X, excess over ceiling | none | `retire:{interval_index}` |
| Starter grant | eligibility check (6.10) | `grant` | `grant` R -> M, `grant.starter_credits` | creates lot, `grant_starter` | `grant:starter:{member_id}` |
| Referral bonus | S12 event after the newcomer's verified cell and `growth.referral.hold_s` | `grant` | `grant` R -> M, bonus (ISS-06) | creates lot, `grant_referral` | `grant:referral:{referral_id}:{referrer_or_newcomer}` |
| Reserve donation | member request (ISS-08) | `reserve_donation` | `reserve_donation` M -> R, amount | `pick_lots` excluding grant lots | `donate:{member_id}:{idempotency_key}` |
| Reversal | two operators approve (6.6.3) | `reversal` | mirror of the reversed entry, up to what can be recovered | mirrors | `reversal:{reversed_entry_id}` |

There is no other way to create or move credit. No row moves credit from member to member except through an escrow (`escrow_hold` then `transfer`), apart from the two-operator restitution reversal of 6.6.3, so there is no peer-to-peer transfer to farm or launder [D].

### 6.6.1 Guards (every one must hold, otherwise nothing is written) [D]

| Operation | Guards and error |
| --- | --- |
| Mint | `launch.minting_enabled` true (`LAUNCH_GATE_CLOSED`); `kill.all_minting`, `kill.template.<tpl_id>`, `kill.service.<svc_id>`, `kill.member.<mem_id>` all `released` (`KILL_SWITCH_ENGAGED`); the cell is `accepted` in this same transaction, is charged (`charged_job_id`, else its own job) to a job with `is_commons`, has no earlier `mint` entry, and the R9 re-check passed; member `status` = `active`; amount is exactly 1,000,000; the three headroom checks of 6.8 hold against the versions stored on the lease (`CAP_EXCEEDED`) |
| Payout | Escrow `state` in (`open`, `settling`); the cell is `accepted`, charged to this job and unpaid; the budget rule of 6.7 holds; headroom of 6.8 (lease-time reservation); the donor is not `banned` at lease time |
| Hold and booking | `launch.member_jobs_enabled` true; `kill.all_new_jobs`, template and service switches released; member `active` and past `identity.recovery_cooldown_s`; the quote is unexpired (`price.quote_ttl_s`) and its snapshots are those it was made under; the admission result of file 06b is `admitted` (or a reservation slot); unexpired credit >= escrow (`INSUFFICIENT_CREDIT`); `admission.max_concurrent_jobs_per_member` not exceeded |
| Settlement and cancel | Escrow `state` = `settling`; no cell of the job is in `leased`, `submitted` or `flagged_for_audit` (S5.* drains or voids them first; `STATE_CONFLICT` otherwise) |
| Expiry | `expires_at <= now` and `remaining_ucr > 0` |
| Retirement | `reserve_balance_ucr - reserve.ceiling_credits x 10^6 >= reserve.retire_min_credits x 10^6`; the amount is exactly that excess |
| Grant | 6.10 |
| Reserve donation | member `active`; amount <= unexpired non-grant credit; irrevocable; never shown per member on public pages |
| Reversal | 6.6.3 |

If a mint is refused by a switch after the cell was decided, the cell's acceptance rolls back with it (LD-09): the cell stays `submitted` (or `flagged_for_audit`) and is retried by `S5.*` when the switch is released. No cell is ever `accepted` without its payment [D][A].

### 6.6.2 Pseudocode of the two hot paths [D]

```
function post_mint(cell, now):                            -- inside post('mint', 'mint:'+cell.id)
    m = account_of(cell.donor); lot_expiry = now + lifetime_days(m) * 86400
    check switches, cell, member as in 6.6.1
    check_headroom(m, now, versions_of(cell.lease))       -- 6.8
    entry = mint(I -> m, 1_000_000); lot = new_lot(m, 1_000_000, now, lot_expiry, 'mint')
    entry.month_mint_after_ucr = minted_in_utc_month(now) + 1_000_000
    entry.owned_after_ucr = owned(m, now) + 1_000_000

function post_payout(cell, now):                          -- inside post('payout', 'payout:'+cell.id)
    e = escrow_of(cell.job); assert e.state in ('open','settling')
    if cell.cell_kind == 'primary':
        assert e.paid_primary_ucr + 1_000_000 <= e.primary_budget_ucr ; e.paid_primary_ucr += 1_000_000
    else:                                                 -- verification cell: pool first, then levy budget
        from_pool = min(e.pool_budget_ucr - e.paid_pool_ucr, 1_000_000)
        from_levy = 1_000_000 - from_pool
        assert from_levy <= e.levy_budget_ucr - e.paid_levy_budget_ucr
        e.paid_pool_ucr += from_pool ; e.paid_levy_budget_ucr += from_levy
    moves = pick_slices(e.account, 1_000_000)
    entry = transfer(e.account -> account_of(cell.donor), 1_000_000)
    lot = new_lot(donor, 1_000_000, now, now + lifetime_days(donor) * 86400, 'transfer')
```

### 6.6.3 Reversal [D]

A reversal corrects an earlier entry without editing it (S0 0.8.5). Reasons: `cell_overturned`, `fraud_finding`, `appeal_upheld`, `posting_error`. It needs `ledger.reversal_min_approvers` = 2 distinct `AdminUser`s (`ledger.reversal` is in `security.two_person_actions`), is logged as an `AdminAction`, and is idempotent per reversed entry (`reverses_entry_id` is unique).

| Reversed entry | Mirror posted | If the recipient no longer holds enough |
| --- | --- | --- |
| `mint` | M -> I, taken from the minted lot first, then from the member's other lots earliest expiry first | Reverse what the member holds; record `shortfall_ucr` on the transaction. Credit already spent stays in existence (6.14) |
| `transfer`, escrow `open` or `settling` | M -> E (the original escrow); the cell is then replaced by a `rework` cell paid from the pool (ISS-05) | As above |
| `transfer`, escrow `closed` | M -> requester's member account. Escrow accounts never reopen, so this is a restitution, not a mirror; no rework cell is created (the job is closed) | As above |
| `grant`, `expire`, `levy`, `retire`, `refund`, `escrow_hold` | Mirror along the original accounts | Only for `posting_error`, never for reasons about cells |

A reversal never creates credit and never drives an account below zero. A reversal of a `transfer` into an open or settling escrow raises `reversed_in_ucr` and leaves the `paid_*` counters and `accepted_primary_cells` unchanged; the returned credit is part of the balance at settlement and goes back to the requester in the refund, and the rework cell is paid from the pool budget like any verification cell (6.7.2). Reversal entries are excluded from the cap checks of 6.8 (they return credit that was already counted) [D][A].

## 6.7 Escrow, settlement, refunds on cancel

### 6.7.1 Escrow lifecycle [D]

```
(none) --escrow.opened--> open            at the hold; funded_ucr = N x quote_p_ucr
open   --escrow.settling_started--> settling   job.all_cells_accepted, job.stop_requested or job.cancel_requested
settling --escrow.closed--> closed (T)    after the settle or cancel transaction; balance_ucr = 0
```

In `settling`, payouts for in-flight cells still post until the drain ends. The drain is bounded: `drain_s = lease.timeout_s + lease.max_extensions x lease.extend_s + lease.submit_grace_s` = 1200 + 1 x 600 + 120 = 1920 s at the initial defaults (formula, not a measurement); after it the lease reaper has expired every lease of the job and a late paste-back is `LEASE_EXPIRED`.

### 6.7.2 Verification budget [D][A]

A verification cell (`cell_kind` in `gold`, `audit`, `third`, `review`, `rework`) is charged to a job through the cell field `charged_job_id` (required from `S5.*`, 6.17) and pays its donor exactly 1,000,000 ucr (FD§4.3). Its payment is drawn from the pool, and when the pool is spent, from the job's levy budget (code in 6.6.2). The scheduler may create a verification cell for job J only if

```
free(J) = (pool_budget - paid_pool) + (levy_budget - paid_levy_budget)
free(J) - 1_000_000 x in_flight_verification_cells(J) >= 1_000_000
```

so a payout can never fail for lack of budget. When this is false the scheduler stops creating optional verification for J (gold insertion, sampled audits) and logs `ledger.verification_budget_exhausted`; automatic checks still run. A mandatory third execution (`verify.third_exec_on_mismatch`) that cannot be funded sends the contested cell back to `queued` as a new attempt instead (S8.* owns the cell side). The sampling floor (`verify.audit_rate_floor`, FD§4.4) is therefore a rate over funded verification: where a job's budget cannot fund the floor, that fact is published as `hamyar_ledger_verification_unfunded_total` and counted in the false-accept analysis (S8.*) [A]. No path creates credit to fund verification of a member job (ISS-61).

### 6.7.3 Settlement and cancel algorithm [D]

```
function settle(job):                                    -- post('settle'|'cancel', ... )
    e = escrow_of(job); assert e.state == 'settling'; assert no cell in leased|submitted|flagged_for_audit
    levy_due       = e.accepted_primary_cells x e.quote_lambda_ppm
    levy_available = e.levy_budget_ucr - e.paid_levy_budget_ucr
    levy_posted    = min(levy_due, levy_available)
    if levy_posted > 0: post levy(E -> R, levy_posted), draining slices earliest expiry first
    refund         = balance(e) - levy_posted               -- balance(e) is the value read before the levy entry is planned; everything else: unspent primary, unspent pool, unspent levy
    if refund > 0: post refund(E -> M(requester), refund), restoring remaining slices to their lots
    e.state = 'closed'; assert balance(e) == 0              -- INV-L07
```

Properties [D]: the levy is charged on accepted primary cells only, so a job that completes in part pays the levy in part; unspent pool is refunded, so the requester pays for verification actually performed, not for the quoted average; `levy_posted <= levy_due` always, and is lower than `levy_due` only when verification overran its pool (6.7.2). The published gauge `hamyar_pricing_effective_levy_ppm` = levy posted / accepted primary cells over the trailing window keeps that visible. Cancel runs the same function after the drain: unstarted cells cost nothing (their primary, pool and levy shares are in the refund), accepted cells have already been paid at acceptance (LD-03).

Examples (exact; full FD§3.3 case in 6.15): partial, N = 240, 100 primary and 10 verification cells accepted: balance = 276,000,000 - 110,000,000 = 166,000,000; levy = 100 x 50,000 = 5,000,000; refund = 161,000,000. Fractional, N = 7: escrow 8,050,000, pool 700,000, levy budget 350,000; with no verification cell: payouts 7,000,000, levy 350,000, refund 700,000; with one verification cell: it takes the 700,000 pool and 300,000 of the levy budget, so the levy posted is 50,000 and the refund is 0 (ISS-61).

## 6.8 Per-member cap K and mint caps

### 6.8.1 Owned credit and the effective cap [D][A]

FD§4.5: K bounds one claimant's share of future capacity. Credit locked in the member's own escrow is still that member's claim (it returns on refund), so the cap counts it; otherwise a member could hold K, escrow it, earn another K, and receive 2K back as a refund.

```
K_eff(m)    = div_floor(credit.member_cap_credits x 10^6 x trust.cap_multiplier.<tier of m>_ppm, 10^6)
owned(m, t) = sum(remaining_ucr of m's lots with expires_at > t)
            + sum(slices, with lot.expires_at > t, held by escrows of m's jobs and reservations in state open or settling)
headroom(m, t) = max(0, K_eff(m) - owned(m, t) - 1,000,000 x active_leases(m))
```

Each undecided lease counts as one credit that may arrive: `active_leases(m)` (and `active_commons_leases`) counts the member's cells in `leased`, `submitted` or `flagged_for_audit`, so the reservation lasts from the lease until the cell is accepted, rejected or expired, not only while the Lease is `active`; at posting, the cell being accepted is left out of the count. The tier multipliers are `trust.cap_multiplier.new` / `.established` / `.trusted` / `.restricted` = 0.50 / 1.00 / 1.50 / 0.25 (initial configurable defaults, S0 0.10.6), so at K = 350 a `new` member holds at most 175, an `established` member 350 and a `trusted` member 525. A new member therefore cannot yet reach the 300 credits of the FD§3.3 example; Sara is `established` (T-unit-01 fixture) [A].

### 6.8.2 Headroom is reserved at lease time [D]

A lease may be issued only if all three hold (the function is `ledger.can_lease(member, cell, now)`, called by `S5.*` inside the leasing transaction, after `SELECT ... FOR UPDATE` on the member's account and, for a Commons cell, on the `issuance` account row (both in ascending account id, the lock order of `post()`), so that concurrent leases of one member, and concurrent Commons leases of different members at the monthly-cap boundary, cannot both pass):

| Check | Applies to | Condition |
| --- | --- | --- |
| Member cap | every cell | `headroom(m, now) >= 1,000,000` (`CAP_EXCEEDED`) |
| Per-member daily mint cap | Commons cells | `mint.per_member_daily_cap_credits x 10^6 - minted_today_utc(m) - 1,000,000 x active_commons_leases(m) >= 1,000,000` |
| Monthly mint cap | Commons cells | `mint.monthly_cap_credits x 10^6 - minted_this_utc_month - 1,000,000 x active_commons_leases(all) >= 1,000,000`, and `launch.minting_enabled` true and `kill.all_minting` released |

The lease stores the versions of the parameters it read (`ledger_versions`, a json field required from `S5.*`, 6.17). The later posting copies the resolved caps into the entry (`cap_ucr`, `mint_cap_ucr`) so that INV-L10 and INV-L11 compare an entry with the cap that was in force when headroom was promised. A cap that is tightened after the lease does not void it: in-flight cells are honored, so a tightening can overshoot the new cap by at most the number of leases then active [D]. Day and month boundaries are UTC (S0 0.6.2).

When the monthly check fails the scheduler stops offering Commons cells ('Commons backlog paused until the next UTC month or a cap change') and may still offer member-job cells; mint-cap utilization (6.11.5) shows this coming. Because headroom is reserved up front, a decided cell is never left unpaid for want of headroom; the guards of 6.6.1 re-check it as defense in depth.

What K does not do [D]: it does not stop a member from receiving a refund, a reversal restitution or an expired-lot restoration (all return credit already counted in `owned`); and credit above a cap that was later lowered is not confiscated, it simply stops further earning until the member spends below the cap (prospective change, LD-14).

## 6.9 Expiry, the Reserve and retirement

### 6.9.1 Expiry [D]

Every lot has its own date (6.4.2); the balance view returns the unexpired lots grouped by expiry day (UTC), so a member sees how much expires when. The balance shown as available is the sum of unexpired lots; `expires_at <= now` lots are never spendable (6.4.3) even before they are swept.

```
every credit.expiry_sweep_interval_s (default 3600 s):
    for lot in SELECT * FROM credit_lots WHERE remaining_ucr > 0 AND expires_at <= now
                 ORDER BY expires_at, id LIMIT batch:
        post('expire', 'expire:' + lot.id + ':' + count_expire_entries(lot.id)):  expire(M(lot) -> R, lot.remaining_ucr); lot -> status 'expired'
```

Expired credit moves to the Reserve and is never silently deleted (FD§4.5). A lot restored from a refund after its date is swept the same way (ISS-07): the restoration sets its status back to `active`, and the sweep count k in the natural key (6.6) stops the second sweep being read as a replay of the first. One entry per sweep keeps the trail exact. Notice: members are told `credit.expiry_notice_days` (default 7) before a lot expires by an in-app notice computed from the same query (no e-mail is required, FD§3.2). A swept lot emits `ledger.lot_expired` (new log event, 6.17).

### 6.9.2 The Reserve [D]

A public account (FD§4.2). Inflows: `levy` (6.7), `expire` (6.9.1), `reserve_donation` (ISS-08). Outflows: `grant` (6.10) and `retire`. Its balance, ceiling and every inflow and outflow total are public (`S12.*`, lagging by `public.ledger_lag_s`). Nothing else may debit it (INV-L12), except a two-operator `reversal` (6.6.3).

### 6.9.3 Retirement above the ceiling [D]

```
every reserve.retire_interval_s (default 86,400 s), interval_index = div_floor(now_s, reserve.retire_interval_s):
    ceiling = reserve.ceiling_credits x 10^6 ; excess = balance(R) - ceiling
    if excess >= reserve.retire_min_credits x 10^6:
        post('retire', 'retire:' + interval_index): retire(R -> X, excess); entry.reserve_balance_after_ucr = ceiling
        publish a ChangeLogEntry kind 'retirement' with seq, amount and balance after
```

Retirement is the only way credit leaves existence (the one other case is a two-operator reversal of a `mint`, 6.6.3, which cancels the mint itself), so every retirement is public and `retired` equals cumulative retired (INV-L02). Defaults: ceiling 1,000 credits, minimum retirement 10 credits (avoids noise). `reserve.ceiling_credits >= grant.starter_credits` (constraint C5) so the Reserve can always fund at least one grant [D]. Retirement does not look at queued grants: with the defaults the ceiling is 333 times G, and lowering the ceiling is a parameter change with notice (6.12) [A].

## 6.10 Starter grant G and anti-farming limits

### 6.10.1 Conditions [D]

An eligible member is credited `grant.starter_credits` (default 3, 'a few cells', FD§4.6) from the Reserve, once for life. All conditions must hold at the moment of posting:

| # | Condition | Parameter | Reason code on denial |
| --- | --- | --- | --- |
| 1 | `launch.member_jobs_enabled` true; member `active`; tier not `restricted` | | `gate`, `status`, `restricted` |
| 2 | No starter grant ever posted for this member (natural key makes a second post impossible) | | `already_granted` |
| 3 | At least `grant.required_verified_cells` verified cells (default 1), where a verified cell is an `accepted` cell whose `VerificationRecord` has outcome `pass` by `gold`, `audit_second`, `audit_third`, `human_review` or `blanket_redundancy`; `auto_check` alone does not count, and an `overturned` cell does not count [A] | `grant.required_verified_cells` | `not_verified` |
| 4 | Grants already posted to members sharing this member's `Device` record < limit | `grant.max_per_device` (default 1, lifetime) | `device_limit` |
| 5 | Grants posted today (UTC) inside this member's invite tree < limit | `grant.max_per_invite_tree_per_day` (default 2) | `tree_limit` |
| 6 | Grants posted today (UTC) in total < limit | `grant.max_per_day` (default 20) | `day_limit` |
| 7 | `balance(R) - G x 10^6 >= grant.reserve_floor_credits x 10^6` (default floor 0) | `grant.reserve_floor_credits` | `reserve_empty` |
| 8 | `owned(m) + G x 10^6 <= K_eff(m)` | K | `cap` |

The grant lot is non-transferable (`grant.non_transferable` = true, constant): it is spendable only through the member's own `escrow_hold`, is excluded from `reserve_donation`, expires after `grant.starter_lifetime_days` (default 14), and when its escrow is refunded it comes back as the same lot with the same date.

```
every credit.expiry_sweep_interval_s, and after each accepted cell of a member without a grant:
    for m in members satisfying 1-3 ordered by (time the qualifying verified cell was accepted, member id):  -- first come, first served
        denial = first failing of 4-8 ; if none: post('grant', 'grant:starter:' + m.id)
        elif denial == 'reserve_empty': stop the loop    -- grants pause, they are never printed (FD§4.6)
        else: record ledger.grant_denied(reason) ; continue
```

A member denied only for `reserve_empty`, `day_limit`, `tree_limit` or `cap` is not marked; the next run reconsiders them, in the same order, so a pause does not reorder the queue. No ledger path creates credit for a grant.

### 6.10.2 Farming analysis [D][H]

| Attack | Limit | Residual risk |
| --- | --- | --- |
| Many fake members, each taking G | Condition 3 needs real verified work per fake member (and a new donor's first cells are blanket-verified, `verify.new_donor_blanket_cells`); conditions 4 to 6 cap the rate | A farm with many real devices can still collect; the loss is bounded below |
| One person, many devices | `grant.max_per_device`; device records are keyed hashes (S0 0.7), so evasion is possible and is [H] to be measured | Not preventable by this layer alone; invite-tree limits and the trust tiers add friction |
| Invite-tree rings | Condition 5; `invite.tree_max_members`, `invite.min_accepted_cells_to_issue` (S10.*) | Same |
| Draining the Reserve | The Reserve never goes below `grant.reserve_floor_credits` (grants pause); daily drain <= `grant.max_per_day` x G = 20 x 3 = 60 credits of starter grants a day at the initial defaults (formula); referral bonuses (S12.*) draw on the same Reserve and floor, and S12.* states whether `grant.max_per_day` counts them | An attacker can hold grants permanently at the daily maximum until an operator lowers `grant.max_per_day` or pauses grants |
| Selling or pooling grants | No member-to-member entry exists; grant lots are non-transferable | Account sale is outside the ledger (S10.*) |
| Referral bonuses as a second channel | Same Reserve floor and the limits `growth.referral.*` (S12.*); a bonus is a `grant` entry (ISS-06) and is checked against `K` | Owned by S12.* |

The ledger exposes `hamyar_ledger_grants_denied_total{reason}` and `hamyar_ledger_grants_paid_total` so that denial rates and a farm signature (many grants, almost no later contribution) are visible to operators and, in aggregate, to the pilot analysis (`S13.*`). Whether the limits deter farming is [H]; the success criterion is that grants per day stay below the limit with a first-job completion rate above the founders' pre-registered threshold (`P1M`, `FND`).

## 6.11 Pricing: v, lambda, p, eta, claim ratio, mint-cap utilization

### 6.11.1 The price [D]

For a job type t (`job_type`, S0 0.8.6) the requester's price per accepted primary cell is

```
p_ucr(t, at) = 1,000,000 + v_ppm(t, at) + lambda_ppm(at)           (p = 1 + v + lambda, FD§4.3)
escrow_ucr   = N x p_ucr        primary N x 1,000,000 ; pool N x v_ppm ; levy N x lambda_ppm
```

All job types and sizes share one lambda; v differs per job type because verification burden differs by template (FD§4.3 'per job type'). The donor earn rate is exactly 1,000,000 ucr per accepted cell of any kind. `size_class` and `deadline_class` have one value in Phase 1, so no multiplier exists (FD§4.3, FD§4.8). The quote interface used by file 06b and by the job wizard is

```
price_quote(job_type, n_cells, at) -> { p_ucr, v_ppm, lambda_ppm, escrow_ucr, pool_ucr, levy_ucr,
                                        snapshot_ids, expires_at = at + price.quote_ttl_s }
```

### 6.11.2 Measuring v [D][A]

Definitions. A cell is counted at its acceptance time `accepted_at`. A verification cell is a cell with `cell_kind` in `gold`, `audit`, `third`, `review`, `rework`; it is attributed to the job type of the cell or template it serves (a gold cell to its `GoldCell` template's job type). FD§4.3 names audit, gold and rework cells; `third` (the third execution of FD§4.4) and `review` (paid human review cells, FD§4.4) cost credit in the same way and are included, otherwise v would understate the cost [A: clarification of FD§4.3].

```
function measure_v(t, T):                        -- T = measurement instant (publication instant)
    W0 = T - price.v_window_days x 86400         -- default 28 days; the window is [W0, T)
    A  = count(cells: charged_job_type = t, cell_kind = 'primary',  state = 'accepted', accepted_at in [W0, T))
    V  = count(cells: charged_job_type = t, cell_kind in verification set, state = 'accepted', accepted_at in [W0, T))
    if A < price.v_min_sample_cells:             -- default 100 accepted primary cells
        return { v_ppm = price.v_prior_ppm, basis = 'prior', A, V }         -- default 100,000 = 0.10
    v_obs = div_ceil(10^6 x V, A)
    if v_obs > price.v_cap_ppm: return { v_ppm = price.v_cap_ppm, basis = 'capped', A, V, v_obs }   -- default 500,000
    return { v_ppm = v_obs, basis = 'measured', A, V }
```

| Question | Decision |
| --- | --- |
| Which jobs count? | Commons and member jobs of the same type together: the burden belongs to the template, and Phase 1 will have few member jobs. The two ratios are also published separately (`v_commons`, `v_member`) so the assumption can be tested [A][H: equal burden; falsified if they differ by more than the founders' pre-registered tolerance, `FND`] |
| What happens below the minimum sample? | The prior `price.v_prior` applies and the snapshot says `basis = prior`. With the defaults this reproduces FD§3.3 (v = 0.10) before any data exists |
| What if v_obs exceeds the cap? | The cap applies (`basis = capped`), the excess cost is absorbed by the levy through the rule of 6.7.2, and the alarm `ledger.v_cap_hit` is raised (severity `warn`); the cap protects requesters, the levy absorbs the difference, and publishing both makes the loss visible |
| Overturned cells? | A cell that is `overturned` is no longer `accepted` at the next measurement and drops out of both counts |
| Rounding | `div_ceil` (6.3.2); the pool is never smaller than measured cost |
| Windows | The trailing window is fixed-length and half-open; it moves with each publication |
| Limits | v measures cells, not cost in time or tokens (provider tokens are never the unit, FD§4.1); a template whose verification gets cheaper or dearer shows it only after the window turns over |

### 6.11.3 lambda [D]

`price.levy_lambda` (default 0.05, FD§3.3 illustrative; replaced by `P1M` Reserve inflow versus grant demand, then `FND`). It is a published constant, changed only through 6.12. Effective levy (levy posted divided by accepted primary cells) is published beside it (6.7.3).

### 6.11.4 Round-trip efficiency eta [D]

```
eta_ppm(t)   = div_floor(10^12, p_ucr(t))                  -- 1 / (1 + v + lambda); p = 1,150,000 gives 869,565 (0.870 displayed)
eta_blend    = div_floor(10^12 x sum_t A_t, sum_t (A_t x p_ucr(t)))      -- A_t = accepted primary cells of member jobs of type t in the window
```

`price.eta_alarm_threshold` (default 0.80, arbitrary, FD§4.3, replaced through a `PreRegistration`, `FND`) is compared with `eta_ppm` of each job type and with `eta_blend`; below it the alarm `ledger.eta_below_threshold` (`warn`) is raised and shown on the capacity dashboard. No automatic price change follows: whether to change v, lambda or verification rates is a founders' decision (FD§4.3 says the threshold is set by the founders).

### 6.11.5 Claim ratio, throughput and mint-cap utilization [D]

```
claims_ucr          = sum(unexpired lot remaining of all member accounts) + sum(unexpired slices held by reservation escrows)
accepted_cells      = count of accepted cells of any kind (Commons and member) with accepted_at in the last inflation.throughput_window_days (default 28)
claim_ratio_ppm     = div_floor(claims_ucr x inflation.throughput_window_days, 7 x accepted_cells)        -- weeks of capacity, in ppm
mint_utilization_ppm = div_floor(10^6 x minted_this_utc_month_ucr, mint.monthly_cap_credits x 10^6)
```

Why the formula is in these units: one credit pays one executed cell, because the donor earn rate is 1 credit per accepted cell of any kind; credit held in escrow of an admitted job is already counted as committed by admission control (file 06b), so claims are credit that is not yet committed. Weekly throughput is `accepted_cells x 7 / window_days`; dividing credits (cells) by cells per week gives weeks. If `accepted_cells` = 0 the ratio is undefined: the gauge is published as null, `ledger.claim_ratio_undefined` (`warn`) is raised, and no automatic cut is applied (cutting minting because nobody contributes would not help).

Gauges are recomputed every `metrics.rollup_interval_s` (default 3,600 s) and published (6.11.6). Utilization at or above `inflation.mint_utilization_alarm` (default 0.90) raises `ledger.mint_utilization_high` (`warn`).

Automatic response (FD§4.7: 'the mint cap is lowered and quoted windows lengthen; credit is not silently devalued') [D]:

```
after each rollup:
    if claim_ratio_ppm > inflation.claim_ratio_threshold_weeks x 10^6          -- default 6.0 weeks
       and no automatic cut in the last price.publish_period_days             -- one cut per 30 days
       and mint.monthly_cap_credits > 0:
        new_cap_ucr = 10^6 x div_floor(cap_ucr x (10^6 - inflation.mint_cap_cut_ratio_ppm), 10^12)       -- default cut 25%
        write ParameterVersion for mint.monthly_cap_credits by principal 'system', change_class 'tighten',
        effective at once; ChangeLogEntry published within change.tighten_publish_within_s;
        events parameter.changed and ledger.mint_cap_cut
```

File 06b reads `claim_ratio_ppm` to lengthen quoted windows. Raising the cap again is a `loosen` change: notice, a second operator, and the forecast check below. Mint cap against capacity: FD§4.2 says the cap is no higher than forecast redeemable capacity. Redeemable capacity is the cells member jobs can use, so `redeemable_per_month = div_floor(admission.phi_ppm x accepted_cells x 30, 10^6 x inflation.throughput_window_days)` (in cells, which equal credits) and the alarm `ledger.mint_cap_above_forecast` (`warn`, plus a required second approver on the edit) fires when `mint.monthly_cap_credits x 10^6 > redeemable_per_month x 10^6`; with the FD§3.3 illustration (40 donors x 8 cells x 30 days x phi 0.5) it gives 4,800, the default cap. S0 0.10.6 writes that derivation with (1 - 0.5); the two agree only at phi = 0.5, and this file uses phi (ISS-63). Before throughput data exists (Phase 0) the check is skipped and the cap is the configured default [A].

### 6.11.6 Publication and versioning [D]

Published values are immutable `MetricSnapshot` rows (S0 0.7; schema owned by `S13.*`; the fields this file requires are below). A value is never edited: a new row supersedes it.

| Field | Meaning |
| --- | --- |
| `kind` | `price`, `eta`, `claim_ratio`, `mint_utilization`, `reserve`, `ledger_checkpoint` |
| `job_type` | For `price` and `eta`; null otherwise |
| `window_start`, `window_end` | The measurement window |
| `value_ppm`, `sample_primary_cells`, `sample_verification_cells`, `basis` | v (or the gauge), A, V, and `measured`, `prior` or `capped` |
| `inputs` | json of the counts used, so anyone can recompute |
| `formula_version` | Integer; 1 for the formulas of this file; a formula change is a spec change and a new number |
| `version`, `supersedes_id` | Per `kind` and `job_type` |
| `published_at`, `effective_from` | Notice: `effective_from = published_at + change.notice_days_price x 86,400 s` (default 14 days) |

Schedule: a `price` snapshot per job type is published when at least `price.publish_period_days` (default 30, 'monthly', FD§4.3) have passed since the last one, at the next UTC day boundary. The first snapshot (v = `price.v_prior`) takes effect when published, because there is no earlier price to protect. Every later change in v, up or down, takes effect after the notice and is announced in the public change log (`ChangeLogEntry` kind `price`, with old and new `p_ucr` and eta); until then quotes use the snapshot in force and the page shows the upcoming one. Gauges (`eta`, `claim_ratio`, `mint_utilization`, `reserve`) are recomputed each rollup and are not subject to notice, because they are not parameters.

Binding [D]: a quote stores the snapshot ids it used; the escrow stores `quote_p_ucr`, `quote_v_ppm`, `quote_lambda_ppm` at the hold and never changes them; a quote is valid for `price.quote_ttl_s` (default 1,800 s), far shorter than the notice period, so a price change can never fall inside a quote's life. A reservation fixes the price at booking (6.6).

## 6.12 Prospective-only changes, notice and the public change log

### 6.12.1 Rule [D]

Changes to any parameter in this file follow S0 0.10.3: a new `ParameterVersion`, `effective_from >= now + notice_days`, a `ChangeLogEntry`, an `AdminAction` and the event `parameter.changed`. `tighten` changes (R10 pattern) apply at once and are published within `change.tighten_publish_within_s`. A `loosen` or `neutral` change also needs a second operator [A]. Nothing is recomputed retroactively: a report or audit for time t uses the versions in force at t.

### 6.12.2 What each parameter binds to [D]

| Parameter(s) | Bound to | A change affects |
| --- | --- | --- |
| `credit.lifetime_days`, `credit.lifetime_days_accelerated` | the lot (`lifetime_param_version`) | lots earned after `effective_from`; no existing lot changes |
| `credit.member_cap_credits`, `trust.cap_multiplier.*` | the lease (`ledger_versions`) | leases issued after; balances above a lowered cap are not touched |
| `price.levy_lambda`, the `price` snapshots | the quote and the escrow | quotes made after `effective_from`; open escrows keep their price |
| `price.v_window_days`, `price.v_min_sample_cells`, `price.v_cap`, `price.v_prior` | the next measurement | the next publication, then after its notice |
| `mint.monthly_cap_credits`, `mint.per_member_daily_cap_credits` | the lease | leases after; leases in flight are honored (6.8.2) |
| `grant.*` | the evaluation run | members not yet granted; posted grants stay |
| `reserve.ceiling_credits`, `reserve.retire_*` | the next retirement run | after notice, because retirement is irreversible |
| `inflation.*`, `ledger.*_interval_s` | the next rollup or run | immediately after `effective_from` |

Tighten directions required from `S16.*` for the parameter record (`tighten_direction`): `mint.monthly_cap_credits` = `down`; `grant.starter_credits`, `grant.max_per_device`, `grant.max_per_invite_tree_per_day`, `grant.max_per_day` = `down`; `verify.*` rates as in S0; every price, lifetime, cap-K and Reserve-ceiling parameter = `none` (always notice, `change.notice_days_price` = 14 days), because they change what members hold or pay [D][A].

### 6.12.3 Content of the public log line [D]

Parameter name, old and new value, versions, `change_class`, `effective_from`, notice days, a mandatory reason, the approvers' pseudonymous admin handles, and an impact line computed by the system: for price, old and new `p_ucr` and eta per job type; for K, the count of members above the new cap (published only if >= `analytics.min_cohort_k`); for lifetimes, 'existing lots affected: 0'; for the mint cap, the new utilization. Automatic changes (6.11.5) are labeled with the principal `system` and the gauge value that triggered them.

## 6.13 The FD§4.2 invariants as continuous automated checks

FD§4.2 states the ledger invariant: total credit in existence = cumulative mint - cumulative retired; member balances + escrow + Reserve always sum to that total; every unit traces to an accepted Commons cell. This section turns it, and the rules around it, into checks that run without a human. IDs `INV-L<nn>` are those of S0 0.5. [D]

### 6.13.1 How checks run [D][A]

| Run kind | When | Scope | Source of truth |
| --- | --- | --- | --- |
| `commit` | Inside every `post()` (constant, not a parameter) | Rows touched by the transaction | The plan and the rows themselves |
| `incremental` | Every `ledger.invariant_check_interval_s` (default 60 s) | Entries with `seq` above the last checked | Entries, recomputed |
| `full` | Every `ledger.full_recompute_interval_s` (default 3,600 s) | Whole ledger | Entries only; caches (`balance_ucr`, lots, escrow counters) are compared against recomputation, never trusted |
| `checkpoint` | Every `ledger.checkpoint_interval_s` (default 86,400 s) | Hash chain head | Published hash |

The checker is a separate process with a read-only database role and its own code path: it does not call `post()` code and does not read a cache as truth (a check that shares a bug with the writer proves nothing). Each run writes an `InvariantCheck` row (`ivc_`: `invariant_id`, `run_kind`, `from_seq`, `to_seq`, `status`, `observed`, `expected`, `detail`, `started_at`, `finished_at`) and emits `ledger.invariants_passed`; a failure writes an `Alarm` (`alm_`), emits `ledger.invariant_violated` and increments `hamyar_ledger_invariant_violations_total{invariant_id}`. A dead-man alarm `ledger.checks_stale` (`critical`) fires when no `full` run has passed for twice `ledger.full_recompute_interval_s` [A: the factor 2 here, in `INV-L13` and in `INV-L18` is a constant, not a measurement]; `hamyar_ledger_last_full_check_age_s` exposes it. Exact integer equality, zero tolerance (S0 0.6.1).

### 6.13.2 The checks [D]

| ID | Statement (formula) | Runs | Severity |
| --- | --- | --- | --- |
| `INV-L01` | Zero-sum: `sum(balance_ucr over all accounts) = 0`; every entry has `amount_ucr > 0` and different debit and credit accounts | commit, incremental, full | critical |
| `INV-L02` | Conservation (FD§4.2): `sum(member) + sum(escrow) + balance(R) = cum_mint_net - cum_retired_net`, with `-balance(issuance) = cum_mint_net` and `balance(retired) = cum_retired_net` | incremental, full | critical |
| `INV-L03` | Every cached `balance_ucr` equals credits minus debits recomputed from entries | full (touched accounts at commit) | critical |
| `INV-L04` | Signs: member, escrow, Reserve, retired >= 0; issuance <= 0; closed escrow = 0 | commit, incremental, full | critical |
| `INV-L05` | Lots: member balance = sum of its lots' `remaining_ucr`; `0 <= remaining <= initial`; `remaining` = sum of movements; per entry, member-holder deltas equal the entry's net effect on member accounts | commit, full | critical |
| `INV-L06` | Escrow: balance = `funded + reversed_in - paid_primary - paid_pool - paid_levy_budget - levy_posted - refunded`; counters equal sums of entries; slices sum to the balance; no budget exceeded | commit, full | critical |
| `INV-L07` | Closing identity: a closed escrow has balance 0 and `funded + reversed_in = paid_primary + paid_pool + paid_levy_budget + levy_posted + refunded`; `levy_posted <= accepted_primary x quote_lambda` | incremental, full | critical |
| `INV-L08` | Mint backing: each `mint` entry has amount 1,000,000, a `cell_id` of a Commons cell that was `accepted` when posted (now `accepted` or `overturned`), and no second mint for that cell | incremental, full | high |
| `INV-L09` | Payout backing: each `transfer` has amount 1,000,000, debits the escrow of the cell's job, a cell `accepted` or `overturned`, and at most one per cell | incremental, full | high |
| `INV-L10` | Mint caps: for each `mint`, `month_mint_after_ucr <= mint_cap_ucr` and `member_day_mint_after_ucr <=` the daily cap of the recorded version; running sums equal recomputed sums | incremental, full | high |
| `INV-L11` | Member cap: for each `mint`, `transfer`, `grant`, `owned_after_ucr <= cap_ucr` | commit, incremental, full | high |
| `INV-L12` | Reserve: only `grant`, `retire` and `reversal` debit it; after a `grant` the balance >= `grant.reserve_floor_credits`; after a `retire` the balance >= the ceiling used | commit, incremental, full | high |
| `INV-L13` | Expiry: no unexpired-spend (no `escrow_hold` or `reserve_donation` movement from a lot with `expires_at <=` entry time); no `expire` before `expires_at`; no lot with `remaining > 0` older than `expires_at` plus twice `credit.expiry_sweep_interval_s` | incremental, full | high |
| `INV-L14` | Chain: `seq` gap-free from 1; `prev_hash` equals the previous `entry_hash`; each `entry_hash` recomputes; head equals the last entry; the published checkpoint equals the recomputed prefix hash | incremental, checkpoint, full | critical |
| `INV-L15` | Transactions: every entry has a transaction; `settle` and `cancel` leave their escrow at 0; every `reversal` mirrors (or, for restitution, matches amount and reason) an entry reversed at most once, and `shortfall_ucr = original - reversed` | incremental, full | high |
| `INV-L16` | Entry-type matrix: each entry's (type, debit account type, credit account type) is one of the S0 0.8.5 rows; no entry other than a `reversal` moves credit member to member | commit, incremental, full | critical |
| `INV-L17` | Grants: at most one starter grant per member; per device, per invite tree per UTC day and per UTC day within the limits of the version recorded on the entry | incremental, full | high |
| `INV-L18` | Reserve ceiling lag: the Reserve is not above ceiling plus `reserve.retire_min_credits` for longer than twice `reserve.retire_interval_s` | full | warn |
| `INV-L19` | Unrecovered mint: `sum(shortfall_ucr)` of reversals of `mint` entries is published and alarmed when it increases | full | warn |

### 6.13.3 SQL and pseudocode [D]

PostgreSQL-style SQL; the storage engine is chosen in `S4.*`, and the checks are required in whatever form it supports [A]. Each query returns violating rows; an empty result is a pass.

```
-- INV-L01
SELECT SUM(balance_ucr) FROM ledger_accounts;                                    -- must be 0
SELECT id FROM ledger_entries WHERE amount_ucr <= 0 OR debit_account_id = credit_account_id;

-- INV-L02 (cum_mint_net = sum(mint) - sum(reversal of a mint); cum_retired_net likewise)
held     = SELECT SUM(balance_ucr) FROM ledger_accounts WHERE account_type IN ('member','escrow','reserve');
expected = cum_mint_net - cum_retired_net ;  assert held = expected
assert -balance(issuance) = cum_mint_net  AND  balance(retired) = cum_retired_net

-- INV-L03
SELECT a.id FROM ledger_accounts a
 LEFT JOIN (SELECT credit_account_id id, SUM(amount_ucr) c FROM ledger_entries GROUP BY 1) cr ON cr.id = a.id
 LEFT JOIN (SELECT debit_account_id  id, SUM(amount_ucr) d FROM ledger_entries GROUP BY 1) db ON db.id = a.id
 WHERE a.balance_ucr <> COALESCE(cr.c,0) - COALESCE(db.d,0);

-- INV-L04
SELECT id FROM ledger_accounts
 WHERE (account_type IN ('member','escrow','reserve','retired') AND balance_ucr < 0)
    OR (account_type = 'issuance' AND balance_ucr > 0)
    OR (account_type = 'escrow' AND balance_ucr <> 0 AND escrow_id IN (SELECT id FROM escrows WHERE state = 'closed'));

-- INV-L05
SELECT l.id FROM credit_lots l
 LEFT JOIN (SELECT lot_id, holder_account_id, SUM(delta_ucr) s FROM lot_movements GROUP BY 1,2) m
        ON m.lot_id = l.id AND m.holder_account_id = l.ledger_account_id
 WHERE l.remaining_ucr <> COALESCE(m.s,0) OR l.remaining_ucr < 0 OR l.remaining_ucr > l.initial_ucr;
SELECT a.id FROM ledger_accounts a WHERE a.account_type = 'member'
   AND a.balance_ucr <> COALESCE((SELECT SUM(remaining_ucr) FROM credit_lots WHERE ledger_account_id = a.id), 0);
per entry: sum(delta_ucr where holder is a member account) = credit_to_members - debit_from_members

-- INV-L06
SELECT e.id FROM escrows e JOIN ledger_accounts a ON a.id = e.ledger_account_id
 WHERE a.balance_ucr <> e.funded_ucr + e.reversed_in_ucr - e.paid_primary_ucr - e.paid_pool_ucr - e.paid_levy_budget_ucr
                        - e.levy_posted_ucr - e.refunded_ucr
    OR e.funded_ucr <> e.primary_budget_ucr + e.pool_budget_ucr + e.levy_budget_ucr
    OR e.paid_primary_ucr > e.primary_budget_ucr OR e.paid_pool_ucr > e.pool_budget_ucr
    OR e.paid_levy_budget_ucr + e.levy_posted_ucr > e.levy_budget_ucr;
recompute reversed_in = sum(reversal credited into E), paid_primary = sum(transfer of primary cells), paid_pool + paid_levy_budget = sum(transfer of verification cells),
          levy_posted = sum(levy), refunded = sum(refund) from entries; compare; and sum(slices of E) = balance(E)

-- INV-L07 (closed escrows)
SELECT e.id FROM escrows e JOIN ledger_accounts a ON a.id = e.ledger_account_id
 WHERE e.state = 'closed' AND (a.balance_ucr <> 0
   OR e.funded_ucr + e.reversed_in_ucr <> e.paid_primary_ucr + e.paid_pool_ucr + e.paid_levy_budget_ucr + e.levy_posted_ucr + e.refunded_ucr
   OR e.levy_posted_ucr > e.accepted_primary_cells * e.quote_lambda_ppm);

-- INV-L08
SELECT e.id FROM ledger_entries e LEFT JOIN cells c ON c.id = e.cell_id LEFT JOIN jobs j ON j.id = COALESCE(c.charged_job_id, c.job_id)
 WHERE e.entry_type = 'mint'
   AND (c.id IS NULL OR j.is_commons IS NOT TRUE OR e.amount_ucr <> 1000000 OR c.state NOT IN ('accepted','overturned'));
SELECT cell_id FROM ledger_entries WHERE entry_type = 'mint' GROUP BY cell_id HAVING COUNT(*) > 1;

-- INV-L09
SELECT e.id FROM ledger_entries e JOIN cells c ON c.id = e.cell_id JOIN escrows s ON s.job_id = COALESCE(c.charged_job_id, c.job_id)
 WHERE e.entry_type = 'transfer'
   AND (e.amount_ucr <> 1000000 OR e.debit_account_id <> s.ledger_account_id OR c.state NOT IN ('accepted','overturned'));
SELECT cell_id FROM ledger_entries WHERE entry_type = 'transfer' GROUP BY cell_id HAVING COUNT(*) > 1;

-- INV-L10 / INV-L11
SELECT id FROM ledger_entries WHERE entry_type = 'mint' AND month_mint_after_ucr > mint_cap_ucr;
recompute month_mint_after and member_day_mint_after as running sums over UTC month and day; compare with stored; compare with cap of the recorded version
SELECT id FROM ledger_entries WHERE entry_type IN ('mint','transfer','grant') AND owned_after_ucr > cap_ucr;

-- INV-L12
SELECT e.id FROM ledger_entries e JOIN ledger_accounts a ON a.id = e.debit_account_id
 WHERE a.account_type = 'reserve' AND e.entry_type NOT IN ('grant','retire','reversal');
SELECT id FROM ledger_entries WHERE entry_type = 'retire' AND reserve_balance_after_ucr < reserve_ceiling_ucr;
SELECT id FROM ledger_entries WHERE entry_type = 'grant' AND reserve_balance_after_ucr < grant_floor_of_recorded_version;

-- INV-L13
SELECT id FROM credit_lots WHERE remaining_ucr > 0 AND expires_at < now() - 2 * (credit.expiry_sweep_interval_s) * interval '1 second';
SELECT m.id FROM lot_movements m JOIN credit_lots l ON l.id = m.lot_id JOIN ledger_entries e ON e.id = m.ledger_entry_id
 WHERE m.delta_ucr < 0 AND e.entry_type IN ('escrow_hold','reserve_donation') AND l.expires_at <= e.created_at;
SELECT e.id FROM ledger_entries e JOIN credit_lots l ON l.id = e.lot_id WHERE e.entry_type = 'expire' AND e.created_at < l.expires_at;

-- INV-L14
assert min(seq) = 1 AND max(seq) - min(seq) + 1 = count(*)
for each e in order of seq: assert e.prev_hash = previous.entry_hash AND e.entry_hash = sha256(e.prev_hash + jcs(e))
assert head.entry_hash = last.entry_hash ; for each published checkpoint (seq, h): assert prefix_hash(seq) = h

-- INV-L15
SELECT e.id FROM ledger_entries e LEFT JOIN ledger_transactions t ON t.id = e.ledger_transaction_id WHERE t.id IS NULL;
SELECT t.id FROM ledger_transactions t WHERE t.txn_kind IN ('settle','cancel') AND escrow_balance_after(t) <> 0;
for each reversal r: o = reversed entry; assert amount(r) <= amount(o) AND shortfall(r) = amount(o) - amount(r) AND r.accounts mirror o.accounts (or landing rule 6.6.3)

-- INV-L16
SELECT e.id FROM ledger_entries e JOIN ledger_accounts d ON d.id = e.debit_account_id JOIN ledger_accounts c ON c.id = e.credit_account_id
 WHERE e.entry_type <> 'reversal' AND (e.entry_type, d.account_type, c.account_type) NOT IN
  (VALUES ('mint','issuance','member'), ('grant','reserve','member'), ('escrow_hold','member','escrow'),
          ('transfer','escrow','member'), ('escrow_release','escrow','escrow'), ('levy','escrow','reserve'),
          ('refund','escrow','member'), ('expire','member','reserve'), ('retire','reserve','retired'),
          ('reserve_donation','member','reserve'));

-- INV-L17
SELECT e.credit_account_id FROM ledger_entries e JOIN credit_lots l ON l.origin_entry_id = e.id WHERE l.origin_kind = 'grant_starter' GROUP BY 1 HAVING COUNT(*) > 1;
per device: count(starter grants of members sharing a Device record) <= grant.max_per_device
per UTC day: count(grants) <= grant.max_per_day ; per invite tree per UTC day <= grant.max_per_invite_tree_per_day
```

### 6.13.4 Alarm and automatic response [D][A]

| Severity | Meaning | Automatic response (principal `system`) | Release |
| --- | --- | --- | --- |
| `critical` | Integrity of balances or of the chain (`INV-L01` to `L07`, `L14`, `L16`, `ledger.checks_stale`) | Engage `kill.all_minting` and `kill.all_new_jobs` with reason `invariant:<id>`; set `ledger_head.is_frozen`, after which `post()` refuses every transaction except a `reversal`; page operators; publish a status line on the public surface without detail | Fix the cause, then a `full` run passes; two operators release (`killswitch.release` in `security.two_person_actions`) |
| `high` | A rule was broken but balances are consistent (`INV-L08` to `L13`, `L15`, `L17`) | Engage `kill.all_minting` and `kill.all_new_jobs`; page operators; postings continue so donors are still paid | Two operators release after review |
| `warn` | A gauge or lag (`INV-L18`, `L19`, `ledger.v_cap_hit`, `ledger.eta_below_threshold`, `ledger.mint_utilization_high`, `ledger.mint_cap_above_forecast`, `ledger.claim_ratio_undefined`) | Alarm and ticket; no switch | Acknowledge in the admin tool |

The response stops new credit and new claims, which is the direction that cannot make a corrupt ledger worse. Limits [D]: the checks detect, they do not repair; a checker bug can freeze a healthy ledger, so the checker is itself tested (6.16) and a freeze drill is added to the `BM9` drills (S0 0.12 names only the backup and secret-rotation drills; S17.* to adopt it); the alarm path is the monitoring stack of `S4.*`.

## 6.14 Two things the Founding Document cannot promise as written

### 6.14.1 Fractional credit [D]

Where fractions arise. The price p = 1 + v + lambda has up to six decimal places, so escrow, the pool, the levy, refunds and member balances are not whole credits in general (N = 7 gives an escrow of 8.05 credits). Donor earnings and verification cells are whole: one accepted cell pays exactly 1.000000 credit, and a cell cannot be half executed.

| Effect | What this file does | What it does not do |
| --- | --- | --- |
| Escrow and refunds are fractional | Exact in ucr; shown exactly (6.3.2); a refund restores the exact fractional amount | No rounding to whole credits, which would move credit systematically between requester, donors and Reserve (S0 0.6.1) |
| The pool N x v is rarely a whole number of cells (ISS-04) | The pool is a budget in ucr, not a count of cells; verification cells are paid 1 credit each from it; unspent pool is refunded at settlement | It does not promise N x v cells will be run; the number of verification cells is whatever sampling and the budget allow |
| A small job's pool is below one cell (N = 7: 0.7 credit) | The next verification cell takes the pool and the remainder from the job's levy budget (6.7.2); if the budgets cannot pay, optional verification stops | It does not charge the requester extra after the quote, and it does not mint (ISS-61) |
| Balances below 1 credit (dust) | Kept as lots; usable in a job escrow, since escrow is in ucr; they expire and move to the Reserve like any lot | No sweeping of dust into the Reserve, no rounding up |
| v is rounded up | The pool can exceed measured cost by less than 1 ppm per primary cell (under 1 ucr) | The requester is never under-charged relative to the published v |
| FD§3.3 is whole-numbered | It is exact because 240 x 0.10 = 24 and 240 x 0.05 = 12; the model does not rely on that (6.15 and `AC-ledger-03` test non-integral cases) | |

### 6.14.2 'Every unit traces to an accepted Commons cell' [D][H]

Credit is fungible: when Sara's lot funds an escrow and a donor's lot is created from it, the donor's credit has several parents, and the Reserve mixes everything it receives. A unit-by-unit proof of origin does not exist, and the ledger must not claim one. What does hold, and what is checked:

1. **Conservation.** Only `mint` creates credit and only `retire` destroys it (INV-L16), except that a two-operator `reversal` can cancel a `mint` (net mint falls) or correct a posting error; INV-L02 is stated in net terms for that reason. Therefore the credit in existence at any time equals cumulative net mint minus cumulative net retired (INV-L02), and each `mint` is backed by one distinct cell that was `accepted` in a Commons job at the moment of posting (INV-L08). Every unit in existence is therefore part of a pool created entirely by accepted Commons cells; this is the sense in which FD§4.2 is implementable.
2. **Lineage where it is well defined.** `lot_movements` record, for each `transfer`, which slices of which lots became the donor's lot (6.4.3), so any lot can be traced back along transfer chains to mint lots, to a grant (whose origin is the Reserve) or to the Reserve boundary. Tracing stops at the Reserve because Reserve credit is pooled; a lineage query reports 'Reserve' there and does not guess.
3. **What can break it.** (a) A Commons cell that is `overturned` after its credit was minted and spent: the mint can be reversed only up to what the donor still holds (6.6.3); the rest is the unrecovered mint, recorded as `shortfall_ucr`, published, and alarmed (`INV-L19`). Its bound is 1 credit per overturned minted cell. (b) ISS-03: gold, audit and review cells inside Commons jobs mint like any other Commons cell, so a share of minted credit pays for verification of Commons work, not for output a requester wanted; the Commons verification share is published beside v so this is visible. (c) Genesis: the ledger starts at zero with no pre-mint; test or simulation credit lives in a separate database and is never loaded into the production ledger (S18.*).
4. **What the platform may say publicly.** 'Credit in existence equals credit minted for accepted Commons cells minus credit retired, checked every minute (declared), with the unrecovered amount shown.' It may not say that each credit unit is individually backed or that credit is guaranteed redeemable (FD Principle 11; credit is not money or a promised entitlement, FD§4.1).

This is ISS-62.

## 6.15 Worked example: FD§3.3, line by line

All inputs are the FD's illustrative values, not measurements. This is `AC-ledger-01` (behavior) and `T-unit-01` (`test_fd33_worked_example_exact`, 6.16). The admission step belongs to file 06b (`AC-admission-01`); here it is a test double that returns `admitted`.

**Fixture** (parameters at their `initial configurable default`, S0 0.10.6): `price.v_prior` = 0.10 (= 100,000 ppm) with no snapshot above the minimum sample, so `basis = prior`; `price.levy_lambda` = 0.05 (= 50,000 ppm); `credit.lifetime_days` = 60; `credit.member_cap_credits` = 350; `mint.monthly_cap_credits` = 4,800; `mint.per_member_daily_cap_credits` = 30; `launch.minting_enabled` and `launch.member_jobs_enabled` = true (test fixture only; production default false). Member Sara has `trust_tier` = `established` (K_eff = 350 x 1.00 = 350 credits). Forty donors `D00`..`D39`, tier `established`. The Reserve and every other account start at 0. Clock: Sara's Commons cells are accepted at 12:00 UTC on each of the 30 days `d0`..`d29`, 10 per day; the job is requested on day 30.

| FD§3.3 line | Computation (integers) | Result and assertion |
| --- | --- | --- |
| Sara contributes about 10 Commons cells a day for 30 days: 300 credits, none expired (E = 60) | 300 `mint` entries `I -> M(Sara)` of 1,000,000 ucr; lot expiry = acceptance + 60 d, so the oldest lot expires on day 60 | `balance(Sara)` = 300,000,000 ucr; 300 lots; `balance(issuance)` = -300,000,000; `available` = 300,000,000 on day 30 |
| Price: v = 0.10, lambda = 0.05, price 1.15 | `p_ucr = 1,000,000 + 100,000 + 50,000` | `p_ucr` = 1,150,000 (displayed 1.15) |
| 276 credits are escrowed | `escrow_ucr = 240 x 1,150,000`; parts 240 x 1,000,000, 240 x 100,000, 240 x 50,000 | 276,000,000 = 240,000,000 + 24,000,000 + 12,000,000 |
| She keeps 24 | `escrow_hold` `M(Sara) -> E`, 276,000,000; `pick_lots` takes the 276 earliest-expiring lots: all 270 lots of `d0`..`d26` and 6 of the 10 lots of `d27` | `balance(Sara)` = 24,000,000 (4 lots of `d27`, 10 of `d28`, 10 of `d29`); `balance(E)` = 276,000,000; `K` headroom check passes (owned 300 <= 350) |
| Admission: 40 x 8 x 2 x 0.5 = 320 >= 264 | Test double returns `admitted` with `2 days`; the real computation is `AC-admission-01` | Job reaches `admitted`; not asserted here |
| 264 will be executed (240 primary + 24 verification and rework) | Pool 24,000,000 / 1,000,000 = 24 verification cells; `free(J)` = 24,000,000 + 12,000,000 at the start, so every one of the 24 is creatable | 24 cells of `cell_kind` `audit` accepted after the 240 `primary` cells; `paid_pool_ucr` = 24,000,000; `paid_levy_budget_ucr` = 0 |
| Donors earn 264 credits by transfer | 264 `transfer` entries `E -> M(donor)` of 1,000,000, cell `k` (k = 1..264) executed by donor index `(k - 1) mod 40`; each slice drain is earliest expiry first | Donors `D00`..`D23` hold 7,000,000 each, `D24`..`D39` hold 6,000,000 each; sum = 24 x 7 + 16 x 6 = 264 credits = 264,000,000 ucr; `balance(E)` = 12,000,000 |
| 12 credits (lambda x 240) go to the Reserve | `settle`: `levy_due = 240 x 50,000 = 12,000,000`; `levy_available = 12,000,000 - 0`; `levy_posted` = 12,000,000; `refund = 12,000,000 - 12,000,000 = 0`, so no refund entry | `levy` entry `E -> R` of 12,000,000; `balance(R)` = 12,000,000; `balance(E)` = 0; escrow `closed` |
| 264 + 12 = 276: nothing is created or lost | Closing identity (`INV-L07`): 240,000,000 + 24,000,000 + 0 + 12,000,000 + 0 = 276,000,000 = `funded_ucr` | Holds exactly |
| Value to Sara: eta = 1/1.15 = 0.87 | `eta_ppm = floor(10^12 / 1,150,000)` | 869,565 (displayed 0.870) |
| Value to Sara in time: about 30 days alone versus about 2 | 240 cells / 8 per day = 30 days; the quote is 2 days | Not a ledger quantity; asserted by the pricing and admission pages, not here |

**End state** [D]: Sara 24,000,000; donors 264,000,000; Reserve 12,000,000; escrow 0; issuance -300,000,000; retired 0. Existence: members + escrow + Reserve = 24 + 264 + 0 + 12 = 300 credits = cumulative mint 300 - retired 0. Entries: 566 in total with `seq` 1..300 the mints, 301 the hold, 302..565 the transfers, 566 the levy. Every invariant `INV-L01`..`INV-L17` passes in a `full` run; Sara paid 276 credits, donors received 264 and the Reserve received 12.

## 6.16 Test specification

Ids follow S0 0.5. The numbers `AC-ledger-01`..`16`, `T-unit-01`..`02`, `T-prop-01`..`07`, `T-adv-01`..`05` and `T-fsm-01` are reserved for this file; `S18.*` keeps them and numbers its own tests from 10 upward within each layer [A]. Inputs are illustrative defaults, not measurements.

### 6.16.1 `T-unit-01` `test_fd33_worked_example_exact` (the FD§3.3 test)

| Part | Specification |
| --- | --- |
| Setup | The fixture of 6.15. Ledger empty. Clock controlled by the test. Admission is a double returning `admitted`. Checker implementation is the independent one of 6.13.1 |
| Step 1 | For each day `d0`..`d29` accept 10 Commons cells for Sara at 12:00 UTC; each call posts `mint:{cell_id}` |
| Step 2 | On day 30 call `price_quote('translation_glossary', 240, now)`. Assert `p_ucr` = 1,150,000, `v_ppm` = 100,000, `lambda_ppm` = 50,000, `escrow_ucr` = 276,000,000, `pool_ucr` = 24,000,000, `levy_ucr` = 12,000,000, and `eta_ppm` = 869,565 |
| Step 3 | Post `hold:{job_id}`. Assert exactly one `escrow_hold` entry of 276,000,000 ucr, `balance(Sara)` = 24,000,000, `balance(E)` = 276,000,000, Sara's remaining lots are 4 of `d27`, 10 of `d28`, 10 of `d29`, and the 276 consumed slices are those of `d0`..`d26` (270) and 6 of `d27` |
| Step 4 | Accept 240 primary cells then 24 `audit` cells; each posts `payout:{cell_id}`; cell `k` goes to donor `(k - 1) mod 40`. Assert 264 `transfer` entries of 1,000,000, `paid_primary_ucr` = 240,000,000, `paid_pool_ucr` = 24,000,000, `paid_levy_budget_ucr` = 0 |
| Step 5 | Move the job to `settling` and post `settle:{job_id}`. Assert one `levy` entry of 12,000,000 to the Reserve and no `refund` entry; escrow `closed`, balance 0 |
| Expected entries | 566 entries: 300 `mint`, 1 `escrow_hold`, 264 `transfer`, 1 `levy`; `seq` 1..566 gap-free; hash chain verifies |
| Expected balances (ucr) | Sara 24,000,000; `D00`..`D23` 7,000,000 each; `D24`..`D39` 6,000,000 each (donor total 264,000,000); Reserve 12,000,000; escrow 0; issuance -300,000,000; retired 0 |
| Expected checks | A `full` run of `INV-L01`..`INV-L17` passes with zero violations; `INV-L02`: 24 + 264 + 0 + 12 = 300 = 300 - 0 |
| Replay | Posting every transaction a second time returns the stored results and adds no entry (`T-adv-01` covers the race) |

### 6.16.2 Acceptance criteria (Given / When / Then)

| ID | Given | When | Then |
| --- | --- | --- | --- |
| `AC-ledger-01` | The fixture of 6.15 | The sequence of `T-unit-01` runs | Sara pays 276 credits, donors receive 264, the Reserve receives 12, Sara keeps 24, all invariants pass |
| `AC-ledger-02` | A 240-cell job funded as above; 100 primary and 10 verification cells accepted | The job is stopped (`job.stop_requested`) and settled | Payouts 110,000,000; levy `100 x 50,000` = 5,000,000; refund 161,000,000 restores the unspent slices to their lots; escrow 0 |
| `AC-ledger-03` | N = 7 (escrow 8,050,000, pool 700,000, levy budget 350,000) | (a) No verification cell; (b) one verification cell is accepted | (a) payouts 7,000,000, levy 350,000, refund 700,000. (b) the cell takes 700,000 from the pool and 300,000 from the levy budget; levy posted 50,000, refund 0; no mint, no Reserve outflow |
| `AC-ledger-04` | An admitted 240-cell job, no cell accepted | The requester cancels and the drain ends | `cancel` posts a refund of 276,000,000 and no levy; each lot is restored with its original `expires_at`; Sara's balance is 300,000,000 |
| `AC-ledger-05` | Sara holds a 14-day grant lot, a 60-day lot earned earlier and a 60-day lot earned later | She funds a job needing more than the grant lot | Lots are consumed in order of `expires_at`; a lot with `expires_at <= now` is never consumed even if not yet swept |
| `AC-ledger-06` | A job escrow includes a slice of a lot that expires while the job runs, and the member still holds the rest of that lot, which an earlier sweep has already expired | The job settles with a refund covering that slice after `expires_at` | The lot is restored with its original date and the next sweep posts a second `expire` entry (`expire:{lot_id}:1`) to the Reserve (ISS-07) |
| `AC-ledger-07` | Reserve balance = ceiling + 25 credits; `reserve.retire_min_credits` = 10 | The retirement run executes twice in the same interval | One `retire` entry of 25 credits (`retire:{interval_index}` makes the second a replay); `balance(retired)` = 25; a public log line exists |
| `AC-ledger-08` | Member owned 349 credits, K_eff 350 | Two leases are requested concurrently | Exactly one passes (headroom 1 credit); with owned 349.5 neither passes; `owned_after <= cap` on every mint (`T-adv-02`) |
| `AC-ledger-09` | Reserve at 2 credits, G = 3, floor 0, 5 eligible members | The grant run executes | No grant is posted, `reserve_empty` is the only denial, order is preserved; after the Reserve reaches 3, the earliest-qualified member is granted first. A second grant for the same member, a second member on the same `Device`, or a 21st grant in a UTC day is denied with `already_granted`, `device_limit`, `day_limit` |
| `AC-ledger-10` | Window with A = 120, V = 13; another with A = 99; another with A = 100, V = 60 | `measure_v` runs | v = `div_ceil(10^6 x 13, 120)` = 108,334 (`measured`); A = 99 gives 100,000 (`prior`); A = 100 and V = 60 gives 500,000 (`capped`) and the alarm `ledger.v_cap_hit` |
| `AC-ledger-11` | `claims_ucr` = 2,400,000,000; 1,120 accepted cells in 28 days; cap 4,800 credits | The rollup runs | `claim_ratio_ppm` = `floor(2,400,000,000 x 28 / (7 x 1,120))` = 8,571,428 > 6,000,000, so the cap becomes 3,600 credits by principal `system`, `tighten`, effective at once, logged; a second rollup the same day makes no further cut. eta: p = 1,250,000 gives 800,000 (no alarm); p = 1,300,000 gives 769,230 (alarm) |
| `AC-ledger-12` | Monthly cap 4,800 credits, 4,799 minted, 2 Commons leases wanted | Both are requested | The first is granted (headroom 1), the second is refused; the month rollover restores headroom; a lease granted before a cap cut still mints |
| `AC-ledger-13` | A running ledger and a test-only role | The role adds 1 ucr to a member's `balance_ucr`; separately edits one `entry_hash` | The next `incremental` run fails `INV-L01` and `INV-L03`, the `full` run fails `INV-L14`; `ledger.invariant_violated` is emitted, `kill.all_minting` and `kill.all_new_jobs` are engaged by `system`, `ledger_head.is_frozen` is set, and `post()` refuses new transactions until two operators release |
| `AC-ledger-14` | A payout for cell `c` | The same `payout:{c}` is posted twice, sequentially and concurrently | Exactly one entry and one donor lot exist; the replay returns the stored result and emits no event |
| `AC-ledger-15` | A Commons cell whose minted credit was spent | A reversal is approved by one admin, then by two distinct admins | One approver: refused (`FORBIDDEN`). Two: the held part is reversed, `shortfall_ucr` records the rest, `INV-L19` raises `warn`; a second reversal of the same entry is refused |
| `AC-ledger-16` | Open escrow quoted at lambda 0.05; lambda raised to 0.08 with 14 days notice | Days pass | The escrow settles at 0.05; quotes made before `effective_from` still show 1.15; after it they show the new price; the change log shows both |

### 6.16.3 Property, adversarial and state-machine tests

| ID | Test |
| --- | --- |
| `T-prop-01` | Stateful model-based test: random valid sequences of mint, hold, payout, settle, cancel, expire, retire, grant, donate and reverse with random clock advances; after every step the independent checker finds no violation of `INV-L01`..`INV-L17`; shrinking enabled; failing seeds stored |
| `T-prop-02` | `pick_lots` consumes exactly the prefix of lots sorted by (`expires_at`, `earned_at`, `id`); never consumes an expired lot; sum equals the request or `INSUFFICIENT_CREDIT` |
| `T-prop-03` | For any hold followed by any payouts, settlement and refund restore each lot's amount exactly to what the escrow slices still hold; total restored plus levy plus payouts equals the hold |
| `T-prop-04` | For N, v, lambda in the validated ranges: `escrow_ucr` = primary + pool + levy; `eta_ppm` is monotone non-increasing in v and lambda; `div_ceil` never over-states v by more than 1 ppm |
| `T-prop-05` | Any single-field mutation, deletion, reordering or insertion in the entry sequence is detected by `INV-L14` |
| `T-prop-06` | For random cell outcomes in a job, `funded + reversed_in = paid + levy_posted + refunded`, `refund >= 0`, `levy_posted <= levy_due`, balance 0 at close |
| `T-prop-07` | Static check: no float type or non-helper division in the ledger, pricing and invariant modules |
| `T-adv-01` | Two workers post the same `(txn_kind, natural_key)` concurrently: exactly one commits its entries |
| `T-adv-02` | Many concurrent lease requests at the headroom boundary never push owned credit above K_eff (`INV-L11`), and concurrent Commons leases by different members never push the month's mint above the cap (`INV-L10`) |
| `T-adv-03` | Two concurrent holds by one member for two jobs that together exceed the balance: one succeeds, one gets `INSUFFICIENT_CREDIT` |
| `T-adv-04` | With `launch.minting_enabled` false or `kill.all_minting` engaged, an accepting transition is refused and the cell stays undecided (LD-09) |
| `T-adv-05` | The application role cannot UPDATE or DELETE ledger tables, nor write to them outside `post()` |
| `T-fsm-01` | `Escrow`: `open -> settling -> closed`; a payout in `closed` is `STATE_CONFLICT`; `settle` with a cell still `leased` is `STATE_CONFLICT` |
| `T-unit-02` | Boundary cases for `div_floor` and `div_ceil` at every site of 6.3.2, including `b <= 0` rejection and exact multiples |

## 6.17 Interfaces, required names and convention gaps

**Provided by this file** [D]: `post(...)` and the posting operations of 6.6; `ledger.can_lease(member, cell, now)`; `price_quote(job_type, n_cells, at)`; `ledger.available_credit(member, now)` (unexpired lots); `ledger.owned_credit(member, now)`; gauges `claim_ratio_ppm`, `mint_utilization_ppm`, `eta_ppm` per job type; the lineage query of 6.14.2. File 06b consumes the quote, the claim ratio and the hold, release and cancel postings; it owns the capacity and window logic. In pseudocode, `x_ppm` is the stored ppm value of the ratio parameter `x` (for example `price.v_prior` is read as `price.v_prior_ppm`).

**Required from other parts** (names are proposals; the owning part's name wins) [A]:

| Needed | From | Why |
| --- | --- | --- |
| `Job.is_commons` (bool) | `S5.*` | Mint backing (INV-L08) |
| `Cell.charged_job_id`, `Cell.charged_job_type` | `S5.*` | Verification cells charged to a job and a type (6.7.2, 6.11.2) |
| `Lease.ledger_versions` (json) | `S5.*` | Parameter versions read at lease time (6.8.2) |
| `Escrow` ledger columns of 6.4.4 and the `escrows` counters | `S5.*` | Settlement and INV-L06 |
| Acceptance and posting in one transaction; undecided cells retried after a switch is released | `S5.*`, `S4.*` | LD-09 |
| `MetricSnapshot` fields of 6.11.6 | `S13.*` | Price and gauge publication |
| `tighten_direction` values of 6.12.2 | `S16.*` | Immediate or noticed changes |
| Reserve, price, claim ratio and retirement public pages | `S12.*` | Publication |
| Verification scheduler honoring `free(J)` | `S8.*` | 6.7.2 |

**Convention gaps** (to be folded into S0 by C-001) [A]: entity `LotMovement` / `lot_movements` / `lmv_` / permanent; `ledger_head` single-row table with `is_frozen`; `LedgerTransaction` columns `natural_key`, `shortfall_ucr`; log and alarm events `ledger.lot_expired`, `ledger.grant_denied`, `ledger.verification_budget_exhausted`, `ledger.v_cap_hit`, `ledger.eta_below_threshold`, `ledger.mint_utilization_high`, `ledger.mint_cap_above_forecast`, `ledger.claim_ratio_undefined`, `ledger.mint_cap_cut`, `ledger.checks_stale`; `MetricSnapshot` kinds of 6.11.6; metrics `hamyar_ledger_grants_denied_total`, `hamyar_ledger_grants_paid_total`, `hamyar_ledger_last_full_check_age_s`, `hamyar_ledger_verification_unfunded_total`, `hamyar_pricing_effective_levy_ppm`; `CreditLot.origin_kind` values; txn natural-key formats of 6.6. The S6 split over two files shares one number space: this file uses `6.1`..`6.17`, and file 06b should start at `6.20` so that `S6.<m>` references stay unique. The cell text asked for ids `ISS-5x`, but S0 0.4 gives part 6 the block `ISS-61`..`ISS-69` (first file `ISS-61`..`ISS-63`); S0 is followed.

## Issues raised

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-61` | major | FD§3.3, FD§4.3, FD§4.4 | v is a ratio of cells but a verification cell is indivisible and paid 1 credit, so a job's pool N x v is rarely a whole number of cells; a small job's pool can be below one cell while sampling may still require a cell; the FD does not say who pays an overrun or what happens to an underrun | Pool is a budget in ucr; unspent pool is refunded; a verification cell draws from the pool then from the job's levy budget (so the Reserve inflow, not the requester or mint, absorbs overrun); the scheduler cannot create a cell the budgets cannot pay; effective levy is published. Rejected: charging the requester after the quote (breaks the quote promise, FD Principle 10) and funding by mint (breaks FD§4.2). Also: v counts `third` and `review` cells (FD§4.3 lists only audit, gold, rework) | proposed |
| `ISS-62` | major | FD§4.2 | 'Every unit traces to an accepted Commons cell' cannot hold per unit (credit is fungible and the Reserve is a pool) nor after a Commons cell is overturned when its credit has been spent; a payout reversal after the escrow has closed has no escrow to mirror into | Restate as conservation (only `mint` creates, only `retire` destroys) plus each mint backed by one distinct accepted Commons cell at posting, checked every minute; lineage is kept along transfers and stops at the Reserve; the unrecovered mint is recorded, published and alarmed (`INV-L19`); reversal after close lands on the requester as restitution (6.6.3, 6.14.2) | proposed |
| `ISS-63` | minor | FD§4.5, FD§4.7, FD§4.2; S0 0.10.6 | Definition gaps: (a) 'oldest-first' differs from earliest-expiry-first when lifetimes differ (starter 14 days, 60 days, accelerated arm); (b) K must count the member's own open escrow or a refund can push a member above K; (c) S0 0.10.6 derives the default mint cap with (1 - phi), which equals phi only at 0.5, while redeemable capacity is phi x capacity; (d) 'unexpired credit' in the claim ratio does not say whether escrow counts | (a) spend by `expires_at`; (b) K bounds unexpired balance plus own open escrow, enforced by headroom reserved at lease; (c) the bound on the cap is phi x forecast capacity, the default 4,800 is unchanged; (d) claims = unexpired member lots plus reservation escrow, escrow of admitted jobs excluded because admission control counts it as committed | proposed |
