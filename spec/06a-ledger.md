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
| `status` | text | `active` (remaining > 0), `exhausted` (remaining = 0), `expired` (swept) |

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
| `accepted_primary_cells`, `accepted_verification_cells` | Counts, for settlement |

Identity (INV-L06): `balance = funded_ucr - paid_primary_ucr - paid_pool_ucr - paid_levy_budget_ucr - levy_posted_ucr - refunded_ucr`, and the balance is 0 when `state` = `closed` (INV-L07).

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
    repeat up to 3 times on SERIALIZATION_FAILURE:
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
3. **Serializable and ordered.** Postings are totally ordered by `seq`. The single `ledger_head` lock makes posting a serial section [A]; at the volume this system targets (thousands of cells a day, FD§3.3 scale) that is sufficient, and the throughput limit is measured in `T-load-*` (`S18.*`).
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
| Expiry | sweeper (6.9) | `expire` | `expire` M -> R, lot remaining | lot remaining to 0, status `expired` | `expire:{lot_id}` |
| Retirement | scheduler (6.9) | `retire` | `retire` R -> X, excess over ceiling | none | `retire:{interval_index}` |
| Starter grant | eligibility check (6.10) | `grant` | `grant` R -> M, `grant.starter_credits` | creates lot, `grant_starter` | `grant:starter:{member_id}` |
| Referral bonus | S12 event after the newcomer's verified cell and `growth.referral.hold_s` | `grant` | `grant` R -> M, bonus (ISS-06) | creates lot, `grant_referral` | `grant:referral:{referral_id}:{referrer_or_newcomer}` |
| Reserve donation | member request (ISS-08) | `reserve_donation` | `reserve_donation` M -> R, amount | `pick_lots` excluding grant lots | `donate:{member_id}:{idempotency_key}` |
| Reversal | two operators approve (6.6.3) | `reversal` | mirror of the reversed entry, up to what can be recovered | mirrors | `reversal:{reversed_entry_id}` |

There is no other way to create or move credit. No row moves credit from member to member except through an escrow (`escrow_hold` then `transfer`), so there is no peer-to-peer transfer to farm or launder [D].

### 6.6.1 Guards (every one must hold, otherwise nothing is written) [D]

| Operation | Guards and error |
| --- | --- |
| Mint | `launch.minting_enabled` true (`LAUNCH_GATE_CLOSED`); `kill.all_minting`, `kill.template.<tpl_id>`, `kill.service.<svc_id>`, `kill.member.<mem_id>` all `released` (`KILL_SWITCH_ENGAGED`); the cell is `accepted` in this same transaction, belongs to a job with `is_commons`, has no earlier `mint` entry, and the R9 re-check passed; member `status` = `active`; amount is exactly 1,000,000; the three headroom checks of 6.8 hold against the versions stored on the lease (`CAP_EXCEEDED`) |
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

A reversal never creates credit and never drives an account below zero. Reversal entries are excluded from the cap checks of 6.8 (they return credit that was already counted) [D][A].

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
    refund         = balance(e) - levy_posted               -- everything else: unspent primary, unspent pool, unspent levy
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

Each active lease counts as one credit that may arrive. The tier multipliers are `trust.cap_multiplier.new` / `.established` / `.trusted` / `.restricted` = 0.50 / 1.00 / 1.50 / 0.25 (initial configurable defaults, S0 0.10.6), so at K = 350 a `new` member holds at most 175, an `established` member 350 and a `trusted` member 525. A new member therefore cannot yet reach the 300 credits of the FD§3.3 example; Sara is `established` (T-unit-01 fixture) [A].

### 6.8.2 Headroom is reserved at lease time [D]

A lease may be issued only if all three hold (the function is `ledger.can_lease(member, cell, now)`, called by `S5.*` inside the leasing transaction, after `SELECT ... FOR UPDATE` on the member's account so concurrent leases cannot both pass):

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
        post('expire', 'expire:' + lot.id):  expire(M(lot) -> R, lot.remaining_ucr); lot -> status 'expired'
```

Expired credit moves to the Reserve and is never silently deleted (FD§4.5). A lot restored from a refund after its date is swept the same way (ISS-07). One entry per lot keeps the trail exact. Notice: members are told `credit.expiry_notice_days` (default 7) before a lot expires by an in-app notice computed from the same query (no e-mail is required, FD§3.2). A swept lot emits `ledger.lot_expired` (new log event, 6.17).

### 6.9.2 The Reserve [D]

A public account (FD§4.2). Inflows: `levy` (6.7), `expire` (6.9.1), `reserve_donation` (ISS-08). Outflows: `grant` (6.10) and `retire`. Its balance, ceiling and every inflow and outflow total are public (`S12.*`, lagging by `public.ledger_lag_s`). Nothing else may debit it (INV-L12).

### 6.9.3 Retirement above the ceiling [D]

```
every reserve.retire_interval_s (default 86,400 s), interval_index = floor(now / reserve.retire_interval_s):
    ceiling = reserve.ceiling_credits x 10^6 ; excess = balance(R) - ceiling
    if excess >= reserve.retire_min_credits x 10^6:
        post('retire', 'retire:' + interval_index): retire(R -> X, excess); entry.reserve_balance_after_ucr = ceiling
        publish a ChangeLogEntry kind 'retirement' with seq, amount and balance after
```

Retirement is the only way credit leaves existence, so every retirement is public and `retired` equals cumulative retired (INV-L02). Defaults: ceiling 1,000 credits, minimum retirement 10 credits (avoids noise). `reserve.ceiling_credits >= grant.starter_credits` (constraint C5) so the Reserve can always fund at least one grant [D]. Retirement does not look at queued grants: with the defaults the ceiling is 333 times G, and lowering the ceiling is a parameter change with notice (6.12) [A].

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
| Draining the Reserve | The Reserve never goes below `grant.reserve_floor_credits` (grants pause); daily drain <= `grant.max_per_day` x G = 20 x 3 = 60 credits at the initial defaults (formula) | An attacker can hold grants permanently at the daily maximum until an operator lowers `grant.max_per_day` or pauses grants |
| Selling or pooling grants | No member-to-member entry exists; grant lots are non-transferable | Account sale is outside the ledger (S10.*) |
| Referral bonuses as a second channel | Same Reserve floor and the limits `growth.referral.*` (S12.*); a bonus is a `grant` entry (ISS-06) and is checked against `K` | Owned by S12.* |

The ledger exposes `hamyar_ledger_grants_denied_total{reason}` and `hamyar_ledger_grants_paid_total` so that denial rates and a farm signature (many grants, almost no later contribution) are visible to operators and, in aggregate, to the pilot analysis (`S13.*`). Whether the limits deter farming is [H]; the success criterion is that grants per day stay below the limit with a first-job completion rate above the founders' pre-registered threshold (`P1M`, `FND`).
