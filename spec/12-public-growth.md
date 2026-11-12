# 12. Public surfaces and growth experiments

*Spec part 12 · owner cell C-017 · vocabulary, IDs, enums, states and parameter names are those of `spec/00-conventions.md` (S0) and are used exactly · written against Founding Document draft v0.1 (FD). Nothing here is legal advice, and nothing has been verified against a provider's terms, a law or a measurement. Growth mechanics are hypotheses, not predictions; simulation output is never evidence about human behavior (prompt K).*

## 12.1 Scope, binding rules and surface inventory

This part specifies what the project shows the public and how it tests growth (prompt scope G, FD§6): the live counter, the public ledger, the parameter page, the change log, milestone pages, badges, share cards, teams, referral, and the growth mechanics `V1`..`V6` as feature-flagged, instrumented, randomizable experiments. The event schema, metric pipeline and pre-registration storage are `S13.*`; in-app screens are `S11.*`; flags, kill switches and launch gates are `S14.*`; routes are `S15.*`; ledger postings are `S6.*`. Every route and operation id below is a proposal for `S15.*` [A: its owner may rename; the behavior stays].

### 12.1.1 Rules binding every feature in this part [D]

| # | Rule | Reason |
| --- | --- | --- |
| 1 | **Aggregate only.** No public surface shows a `mem_`, `vol_`, `lac_`, `dev_` or `ses_` identifier, a handle, an alias, a location, device data, or the activity pattern of one member. A figure computed from fewer than `analytics.min_cohort_k` distinct members is withheld or merged into a coarser figure. | FD Principle 8; S0.6 |
| 2 | **Verified only.** Public counts include only cells in `Cell.accepted`. Cells in `submitted`, `flagged_for_audit`, `rejected`, `expired`, `overturned` and `voided` never count. | FD§6.1 rank 3 |
| 3 | **Declared, not guaranteed.** Copy says “declared”, “may”, “can be reversed”. No public figure is called correct, safe or guaranteed. | FD Principle 11; prompt F |
| 4 | **No rewards that move money.** Nothing here pays, credits or promises money, a cash equivalent, a prize, a raffle or a sponsor reward. The only ledger effect this part may cause is the referral `grant` pair (credit, not money, non-redeemable) and the `reversal` of those entries (S12.10). Money-moving rewards (FD§6.3 Phase 2) are not specified here (`ISS-127`). Whether credit bonuses or randomized offers raise consumer-protection or gambling-like questions is [V] for counsel (FD§8.3 G0); the answer is stored in the counsel memo referenced by the `LaunchGateItem` for G0. | cell instruction; FD§6.3, FD§8.3 |
| 5 | **No inference.** The platform never infers, stores for display or shows a member's location, affiliation, language-derived origin, provider or device. `public.location_display` = `never` by default. | FD§6.1 rank 5, Principle 8 |
| 6 | **Hidden verification stays hidden.** Every figure a member can see that moves with verification outcomes (own accepted-cell count, team score, badges) counts accepted cells of every `cell_kind` identically. Otherwise a score that did or did not move would reveal that a cell was a hidden `gold` cell. | FD§4.4; `ISS-126` |
| 7 | **Flags default off and are gated.** A `ff.growth.*` flag can be enabled only while `launch.members_may_join` is true; disabling is immediate (S12.11). | S0.10 table C; R10 pattern |
| 8 | **No arm weakens safety.** No experiment arm removes, shortens, reorders or softens a policy, privacy or risk notice (`S11.*`) or the mandatory first-use prompt expansion (`ui.card.expand_required_first_use`). | FD§5.5 |
| 9 | **Safety outranks growth.** A growth surface that raises a member's exposure risk is dropped, not tuned. Every surface in this part is listed in the G1 threat model (`THR-nn`, `S10.*`) before its flag may be enabled. | FD Principle 8; FD§8.3 G1 |
| 10 | **No third-party dependency; low bandwidth.** Public pages load no third-party script, font, image or analytics resource (`analytics.third_party_trackers` = false, `analytics.cookies_enabled` = false), render RTL-first in `fa` and LTR in `en`, and work as plain server-rendered text without JavaScript. Reachability of the host from Iran is [V] (FD§8.3 G2; stored in the `LaunchGateItem` for G2). | FD§10; prompt I |

### 12.1.2 Surface inventory [A]

| Surface | Proposed operations and routes | Auth | Gate | Cache `max-age` no larger than | Screen |
| --- | --- | --- | --- | --- | --- |
| Live counter | `getPublicCounter` `GET /v1/public/counter` | `none` | `ff.growth.v2_live_counter` | `public.counter_refresh_s` | `SCR-pub-01` |
| Public ledger | `listPublicLedgerCheckpoints`, `getPublicLedgerCheckpoint`, `listPublicLedgerFlows`: `GET /v1/public/ledger-checkpoints`, `GET /v1/public/ledger-checkpoints/{checkpoint_date}`, `GET /v1/public/ledger-flows` | `none` | `ff.public.ledger_page` | `public.counter_refresh_s` (a checkpoint by date is immutable: `ledger.checkpoint_interval_s`) | `SCR-pub-02` |
| Parameter page | `listPublicParameters`, `getPublicParameter`, `listPublicParameterVersions`: `GET /v1/public/parameters[/{name}[/versions]]` | `none` | none (served whenever the API is up) | `public.counter_refresh_s` | `SCR-pub-03` |
| Change log | `listPublicChangeLog`, `getPublicChangeLogEntry`: `GET /v1/public/change-log[/{chg_id}]` | `none` | none | `public.counter_refresh_s` | `SCR-pub-04` |
| Milestones | `listPublicMilestones`, `getPublicMilestone`: `GET /v1/public/milestones[/{milestone_key}]` | `none` | `ff.growth.v6_milestones` | `public.counter_refresh_s` | `SCR-pub-05`, `SCR-pub-06` |
| Public teams | `listPublicTeams` `GET /v1/public/teams` | `none` | `ff.growth.v4_teams` | `public.counter_refresh_s` | `SCR-pub-07` |
| Experiments | `listPublicExperiments` `GET /v1/public/experiments` | `none` | none | `public.counter_refresh_s` | `SCR-pub-08` |
| Share card payload | `getShareCardPayload` `GET /v1/share-cards/preview` | `member` | `ff.growth.v3_share_card` | `no-store` | in-app, `S11.*` |
| Teams (member) | S12.9 table | `member` | `ff.growth.v4_teams` | `no-store` | in-app, `S11.*` |
| Referral | `createReferral` `POST /v1/referrals`, `listReferrals`, `getReferral` | `member` | `ff.growth.v5_referral` | `no-store` | in-app, `S11.*` |
| Flags and exposure | `listEffectiveFlags` `GET /v1/flags`, `recordExperimentExposure` `POST /v1/experiment-exposures` | `member` | none | `no-store` | none |

All public routes are rate-limited by `ratelimit.public_rpm` per IP hash, carry an `ETag` (S0.11.7), and accept no query that selects one member. Public screens are `SCR-pub-nn` (role `pub`, S0.5), owned here; this part specifies their content and states (empty, suppressed, stale, error), `S11.*` specifies layout and typography.

### 12.1.3 Phase configuration (FD§6.2, FD§6.3, FD§9) [D]

Phase 1 only instruments the mechanics, because 30-50 members cannot test them statistically (FD§6.2); Phase 2 randomizes them. Both phases run the same finished system with different configuration (ground rule 7).

| Flag | FD§6.2 “tested in” | Phase 1 configuration | Phase 2 configuration |
| --- | --- | --- | --- |
| `ff.growth.v1_fast_path` (`V1`) | 1 instrumented, 2 A/B | Enabled for all new members; instrumented; no `Experiment` running | Experiment `running`: `fast_path` versus `explained` |
| `ff.growth.v2_live_counter` (`V2`) | 2 | Enabled for all (FD§6.3 puts the counter in Phase 1); instrumented; no experiment | Experiment: in-app counter widget shown versus hidden |
| `ff.growth.v3_share_card` (`V3`) | 2 | Disabled (built, dark) | Enabled; experiment on the share offer |
| `ff.growth.v4_teams` (`V4`) | 2 (FD§6.1 rank 5: 1 basic, 2 full) | Enabled, basic teams (aggregate score only); no experiment | Experiment on the in-app team offer; full teams if `public.location_display` allows |
| `ff.growth.v5_referral` (`V5`) | 2 | Disabled (built, dark) | Enabled; experiment on bonus presence |
| `ff.growth.v6_milestones` (`V6`) | 1-2 | Enabled for all: pages and in-app announcements; instrumented | Experiment on the in-app announcement |
| `ff.public.ledger_page` | not tiered in FD | Enabled only after the G1 item “public ledger page reviewed” is signed off (S12.3) | Same |

FD§6.3 lists the counter and basic teams under Phase 1 while FD§6.2 says V2 and V4 are tested in Phase 2; this part resolves that by enabling both for everyone in Phase 1 and randomizing only in Phase 2 (`ISS-123`).

## 12.2 Live counter

### 12.2.1 Definition [D]

- **Verified cell** = a `Cell` whose `state` is `accepted` (S0.9). It passed the verification the pipeline applied to it (automatic checks and, where sampled, an audit). “Verified” means accepted under the declared checks, never “correct”; the measured false-accept estimate is published beside it (`S13.*`, FD§4.4).
- **Headline `verified_output_cells_total`** counts accepted cells of `cell_kind` `primary` and `rework` (cells that produce deliverable output). **`verified_verification_cells_total`** counts accepted `gold`, `audit`, `third` and `review` cells and is always shown next to the headline, so verification overhead (v) and make-work minting stay visible (`ISS-03`, `ISS-122`). Reason: a headline that mixed both would inflate with verification effort, which FD§4.3 already treats as overhead.
- **Split by job family:** `commons_output_cells_total` (Commons jobs) and `member_job_output_cells_total`.
- **Active members:** `active_members_today` = distinct members with at least one accepted cell of any kind whose `accepted_at` falls in the current UTC day; `active_members_window` = the same over the last `admission.active_donor_window_days` UTC days including today.
- **Corrections:** `overturned_cells_total` = cells that were `accepted` and became `overturned`. The headline is a current count and can fall when a cell is overturned; it is not monotone, and the correction figure is shown beside it. Reason: a counter that never falls would overstate (FD Principle 11).
- **Freshness:** “live” means recomputed at most every `public.counter_refresh_s`, not real time. Member-count figures use the same lag as the ledger (`public.ledger_lag_s`) so one member's action is not visible as a +1 within seconds. Residual: an observer who can trigger a contribution and watch the counter can see a +1; that reveals activity, not identity [H: acceptable; reviewed in the G1 threat model].

### 12.2.2 Query (source of truth) [D]

Column names `accepted_member_id` and `accepted_at` stand for whatever `S5.*` names the accepting submission's member and acceptance time; `S5.*` wins on naming.

```sql
-- full recount; the incremental counter (if S4.* builds one) must equal this
SELECT count(*) FILTER (WHERE cell_kind IN ('primary','rework'))              AS verified_output_cells_total,
       count(*) FILTER (WHERE cell_kind IN ('gold','audit','third','review')) AS verified_verification_cells_total,
       count(*) FILTER (WHERE cell_kind IN ('primary','rework') AND job_family = 'commons') AS commons_output_cells_total
FROM cells WHERE state = 'accepted';

SELECT count(DISTINCT accepted_member_id) FROM cells
WHERE state = 'accepted' AND accepted_at >= :window_start AND accepted_at < :window_end;

SELECT count(*) FROM cell_state_history WHERE from_state = 'accepted' AND to_state = 'overturned';
```

### 12.2.3 Response, suppression, failure [D]

```
GET /v1/public/counter  ->  200 (object)
  schema_version: int
  as_of: timestamp (RFC 3339 UTC)
  stale: bool                       // true when the refresh job failed; as_of is then the last good time
  verified_output_cells_total: int
  verified_verification_cells_total: int
  commons_output_cells_total: int
  member_job_output_cells_total: int
  overturned_cells_total: int
  active_members_today:  { value: int or null, suppressed: bool, min_cohort_k: int }
  active_members_window: { value: int or null, suppressed: bool, window_days: int, min_cohort_k: int }
  next_milestone: { milestone_key: string, threshold: int } or null   // only when ff.growth.v6_milestones is on
```

- A member figure below `analytics.min_cohort_k` returns `value: null, suppressed: true`; no other field may allow it to be derived.
- Failure never shows zero or an invented value: the last good snapshot is served with `stale: true` and its own `as_of`; if none exists the route returns `503 UNAVAILABLE`.
- Daily at the UTC day boundary the counter values are stored as `MetricSnapshot` rows (`permanent`) with the counter definition version; milestone checks (S12.6) read these and the live recount.
- If `S4.*` implements the counter incrementally, a reconciliation job compares it with the full recount every `metrics.rollup_interval_s`, publishes the recount, and raises an `Alarm` on any difference.

## 12.3 Public ledger

### 12.3.1 What is shown and what is not [D]

FD Principle 5 makes the ledger public; FD Principle 8 forbids exposing members. Resolution (`ISS-121`): the public ledger is a **series of daily checkpoints plus grouped flows**, never per-member or per-entry rows. It is enabled by `ff.public.ledger_page` only after the G1 threat-model item “public ledger page reviewed” is signed off: [V] whether even aggregated flows are acceptable for members at risk; checked by the G1 reviewers; stored as a `LaunchGateItem` under G1.

| Shown | Not shown |
| --- | --- |
| Totals at each checkpoint: cumulative mint, cumulative retired, credit in existence, Reserve balance and ceiling, member balances total, escrow total | Any `lac_`, `mem_` or `vol_` id; any per-member or per-job row; any timestamp finer than the UTC day |
| Grouped flows per `ledger_entry_type` (S0.8.5) | Recipient or payer of any entry |
| The result of the latest invariant checks, failures included | Operator identities (`adm_`) on reversals: only the count of approvers |
| A hash per checkpoint | The entries behind the hash |

### 12.3.2 Checkpoint record [D]

One immutable record per UTC day, published `public.ledger_lag_s` after the checkpoint boundary (`ledger.checkpoint_interval_s`).

```
LedgerCheckpoint (public projection)
  checkpoint_date: date (UTC)           through_seq: int (last ledger seq included)
  schema_version: int                   published_at: timestamp
  cumulative_mint_ucr: string           cumulative_retired_ucr: string
  in_existence_ucr: string              // = cumulative_mint_ucr - cumulative_retired_ucr  (INV)
  reserve_ucr: string                   reserve_ceiling_ucr: string
  members_ucr: string or null           escrow_ucr: string or null
  member_and_escrow_ucr: string or null // present when either of the two above is withheld
  invariant_difference_ucr: string      // in_existence - (members + escrow + reserve); must be "0"
  suppressed: [field names]             last_invariant_check: { at, result: passed or failed }
  checkpoint_hash: sha256:<hex>         // entry_hash of the ledger entry at through_seq (S0.6.4)
  prev_checkpoint_hash: sha256:<hex>    corrects_checkpoint_date: date or null
```

- `members_ucr` is withheld (and merged into `member_and_escrow_ucr`) when fewer than `analytics.min_cohort_k` member accounts hold a nonzero balance; `escrow_ucr` is withheld likewise when fewer than that many escrows are open. Reason: on a quiet day the difference of two daily totals would otherwise be one job.
- The hash commits to the full ledger without disclosing it. Whether an audit export that replaces account ids with per-export random pseudonyms is ever published is an owner decision [A], deferred to `S10.*`.
- Mirroring checkpoint hashes to a second host is a hosting decision (`S4.*`) [A].

### 12.3.3 Grouped flows: emit-when-k algorithm [D]

A flow row covers an interval and is emitted only when at least `analytics.min_cohort_k` distinct non-system accounts took part, so no row describes a small group and published rows partition time (no complementary-suppression leak).

```
for each ledger_entry_type T:
    if T == retire:                       // system-only; no member involved
        emit one row per entry {from=to=day, count=1, amount}
        continue
    acc = carried_state[T]                // entries, amount, set of non-system accounts, from_day
    for each UTC day d after the last emitted day up to the latest published checkpoint date:
        acc.add(all entries of type T with day == d and seq <= checkpoint.through_seq)
        if len(acc.accounts) >= analytics.min_cohort_k:
            emit {entry_type: T, from: acc.from_day, to: d, count: len(acc.entries),
                  amount_ucr: acc.amount}
            acc.reset(from_day = d + 1)
    carried_state[T] = acc                // unpublished remainder; counted nowhere
```

Consequences [D]: founders' `reserve_donation` rows appear only once at least `analytics.min_cohort_k` distinct donors have contributed; until then they are inside the Reserve total only. Row sums through a date equal the totals at that date's checkpoint minus the carried remainder, which each row set states as `carried_not_published: true`.

### 12.3.4 Versioning, corrections, failures [D]

- Checkpoints and rows are immutable. An error is fixed by a **correction checkpoint** with `corrects_checkpoint_date` set and a `ChangeLogEntry` of `subject_kind` `correction`; the original stays visible, marked superseded.
- `schema_version` increases only for breaking shape changes (which need `/v2`, S0.11.1); additive fields stay in `/v1`.
- A failed invariant check is published, not hidden: after `ledger.invariant_violated` the page shows `last_invariant_check.result` = `failed` until a full recompute passes (`ledger.full_recompute_interval_s`). Disabling `ff.public.ledger_page` is an operator action recorded in `AdminAction` and the change log.
- Copy: `copy.public.ledger_notice` (S12.14). The page says figures are as declared by the system's own checks at the time shown.
