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

## 12.4 Parameter page

### 12.4.1 Content [D]

FD Principle 5: formulas, parameters, expiry and the ledger are public. The page is generated from `Parameter` and `ParameterVersion` (S0.10.3) and lists every parameter whose `public` field is true.

| Field shown | Source | Note |
| --- | --- | --- |
| `name`, `type`, `unit` | `Parameter` | `S0.10.1`, `S0.10.2` |
| `value`, `version`, `effective_from` | current `ParameterVersion` | `ratio` is shown as integer ppm, `credits` as a `*_ucr` integer string; the client formats decimals (S0.6.1) |
| `default`, `is_initial_default` | `Parameter.default`; true while `value` equals the default | Makes uncalibrated parameters visible (FD Principle 11: bad news is published too) |
| `calibration_source` | measurement code of S0.10.4 plus pointer | Says what will replace the default |
| `validation`, `owner`, `introduced_in` | `Parameter` | |
| `next_version` | a `ParameterVersion` with a future `effective_from` | `{version, value, effective_from, change_log_entry_id}` or null |

Parameters with `public` = false (area `security` by default) are **not listed by name**; the page shows only `withheld: { count, areas }` and `copy.public.parameter_withheld`. Changing any parameter's `public` flag is itself a change-log entry (S12.5), so withholding cannot happen silently (FD Principle 5).

### 12.4.2 Versioning and queries [D]

- `GET /v1/public/parameters` lists current values (`?area=` filters; cursor pagination, S0.11.6). `GET /v1/public/parameters/{name}` returns one. `GET /v1/public/parameters/{name}/versions` lists every `ParameterVersion`, newest first: `{version, value, effective_from, published_at, change_class, change_log_entry_id}`.
- `?as_of=<RFC 3339>` on the single-parameter route returns the version in force at that instant. This lets anyone check a lot's expiry or a job's quote against the parameter version stamped at the time (S0.6.2: changes are prospective only).
- A response never exposes a value before its `effective_from` as current; future versions appear only as `next_version`.
- Responses carry `ETag` and `Cache-Control: max-age` no larger than `public.counter_refresh_s`.

## 12.5 Change log

### 12.5.1 What it records [D]

The change log is the public projection of `ChangeLogEntry` (`chg_`, `permanent`, append-only). It exists so that no rule changes secretly (FD Principle 5) and so that rule R10 is checkable from outside: any rule may tighten at once; loosening needs a public entry and a stated reason (FD§5.4).

`subject_kind` [A, convention addition, `ISS-128`]: `parameter`, `policy_version`, `template_version`, `service`, `feature_flag`, `pre_registration`, `kill_switch`, `milestone`, `correction`.

| Public field | Rule |
| --- | --- |
| `id`, `published_at`, `effective_from` | `effective_from` is the instant the change binds |
| `subject_kind`, `subject_ref` | `parameter`: the name; `policy_version`: `plv_` id and the changed `R1`..`R10` ids; `template_version`: `tpv_` id and transition; `service`: `svc_` id and transition (see label rule); `feature_flag`: `flag_key` and on or off; `pre_registration`: `exp_` id and the locked hash; `kill_switch`: scope; `milestone`: `milestone_key`; `correction`: the corrected checkpoint or entry |
| `change_class` | `tighten`, `loosen` or `neutral` (S0.8.6) |
| `old_value`, `new_value`, `old_version`, `new_version` | Only for public parameters |
| `reason` and `reason_lang` | Required and non-empty for `loosen`; recommended otherwise |
| `approvers` | A count and the roles (`operator`, `reviewer`); never `adm_` ids |
| `corrects_id` | Set on a correction entry |

- **Not published:** `kill.member.<mem_id>` engagements (a personal action); parameters with `public` = false (their entry says only “withheld parameter changed” and the area).
- **Service labels:** a `service` entry shows the `svc_` id; the registry display label is added only when `public.change_log_service_labels` is true. Default false. [V] whether naming a provider publicly is acceptable; decided with counsel and the G1 threat model; stored in that parameter and the G0 counsel memo.

### 12.5.2 Timing rules (R10 and S0.10.3) [D]

| Class | Rule | Check |
| --- | --- | --- |
| `loosen` | `ChangeLogEntry` is published before the change binds; `effective_from >= published_at + notice_days` (`change.notice_days_default`, or `change.notice_days_price` for `price.*`, `admission.*`, `credit.*`) | Write refused with `VALIDATION_FAILED` otherwise |
| `tighten` | Binds at once; the entry is published within `change.tighten_publish_within_s` | An `Alarm` is raised if the entry is late |
| `neutral` | Published with `notice_days` like `loosen`, but `reason` optional | |

Entries are never edited or deleted (S0.7: no soft delete on change-log tables). A mistake is fixed by a new entry of `subject_kind` `correction` with `corrects_id`. `GET /v1/public/change-log` filters by `subject_kind`, `change_class` and a date range and is newest first. A change-log entry is written in the same database transaction as the change it records (S0.10.3). The event is `changelog.entry_published`.

## 12.6 Milestone pages (V6)

### 12.6.1 Entity and states [D][A]

FD§6.2 `V6`: public milestones tied to real outputs. `Milestone` is a new entity (`mst_`, `permanent`; convention addition, `ISS-128`).

| Field | Type | Rule |
| --- | --- | --- |
| `id`, `milestone_key` | `mst_` id; slug | `milestone_key` is the natural key and the public path |
| `metric_key` | enum | `verified_output_cells_total` or `commons_output_cells_total` (S12.2) |
| `threshold` | int | Authored per milestone by the founders (`FND`); FD§6.2's 10,000 is an illustration, not a default |
| `title_key`, `body_key` | copy keys | Need `needs_human_and_legal_review` before the state can reach `published` |
| `state` | enum | `defined`, `reached`, `published` (T), `withdrawn` (T) |
| `reached_at`, `reached_value` | timestamp, int | Set once |
| `output_deliverable_ids`, `output_manifest_hash`, `output_license`, `output_cell_count`, `output_url` | refs, hash, `L1` or `L2`, int, string | Set at publication |

```
(none)    --milestone.defined-->    defined
defined   --milestone.reached-->    reached      metric_key value >= threshold on a daily snapshot or live recount
reached   --milestone.published-->  published    guards below
reached|published --milestone.withdrawn--> withdrawn   legal or safety finding; page stays, marked withdrawn
```

`milestone.reached` is emitted once and is irreversible: if overturns later push the count below the threshold the milestone stays `reached` and the page shows `copy.public.milestone_corrections`. Reason: honesty without retracting history.

### 12.6.2 Publication guards and page content [D]

- **Guards for `milestone.published`:** (1) every included cell is `accepted` at that moment; (2) `output_manifest_hash` equals the stored `Manifest` hash; (3) the included jobs are Commons jobs with `purpose` `P1` and license `L1` or `L2`; policy stamps show R7 passed at admission and acceptance (R9), so the output is not licensed beyond the service flags; (4) the page copy is reviewed; (5) two distinct admins approve, one `reviewer` and one `operator`. `milestone.publish` is a two-person action; `S10.*` appends it to `security.two_person_actions` (`ISS-128`).
- **A page may say only what is recorded:** before `published` it says the threshold was reached and when; it never says an output “became” anything. After `published` it shows the output description, declared license, cell count, manifest hash and link, the measured false-accept estimate from the latest `MetricSnapshot` (or “not yet measured”), and `copy.public.milestone_downstream` (FD glossary: downstream use uncontrolled).
- **Never shown:** member names, handles, ids, places, services used. A contributor count appears only if it is at least `analytics.min_cohort_k`.
- **Framing:** knowledge access, not politics (FD§6.1 rank 2).
- **Where the output lives** (host, mirror, reachability from Iran) is [V]: verified by the operator, stored in `output_url` and the G2 `LaunchGateItem`.
- Phase 1 and 2 behavior and the randomized in-app announcement: S12.12 `V6`.

## 12.7 Badges

### 12.7.1 Definition [D]

A `Badge` (`bdg_`, `permanent`) is a recognition mark whose criterion is expressed in verified cells only (S0.7). FD§6.1 rank 4: reputation comes from verified quality, not volume, and there are no streak penalties. Therefore badges are recognition only; the `trust_tier` (S0.9, `S8.*`, `S10.*`) is the only reputation mechanism with effects.

- A badge **never** changes a cap (K), a sampling rate, a price, admission, `trust_tier`, or any ledger balance. No `LedgerEntry` is created for a badge.
- There is **no individual ranking or leaderboard** of members, public or private (FD Principle 8). Competition exists only between teams (S12.9).
- Criteria count accepted cells of every `cell_kind` identically (S12.1 rule 6).

| Field | Rule |
| --- | --- |
| `badge_key` | Natural key, e.g. `cells_10`, `days_30`, `review_cells_10`, `milestone_<milestone_key>` |
| `family` | `cells`: accepted cells total at least N. `days`: distinct UTC days with at least one accepted cell, at least N (cumulative, never consecutive, so no streak can break). `review_cells`: accepted `review` cells at least N (human-review channel, `ff.channel.human_review`). `milestone`: at least one of the member's cells is inside a `published` milestone output |
| `threshold` | N, from parameter `growth.badge.thresholds` (S12.13); null for `milestone` |
| `title_key`, `description_key`, `version`, `is_active` | Definitions are immutable rows; a changed criterion is a new row and the old one is deactivated for new awards |

`BadgeAward` (`baw_`, `member_bound`): `member_id`, `badge_id`, `awarded_at`, `evidence_value`, `state` (`awarded`, `revoked`), `revoked_at`. Events `badge.awarded`, `badge.revoked`.

### 12.7.2 Evaluation [D]

```
on cell accepted (outbox event) for member m:   re-evaluate families cells, days, review_cells
on milestone.published:                          award family milestone to members with a cell in the manifest
on cell.overturned for member m:                for each held badge of families cells, days, review_cells:
                                                     if current criterion value < threshold: state = revoked  (badge.revoked)
on any later re-evaluation that meets the criterion again: state = awarded (new BadgeAward row)
Awards are idempotent: UNIQUE(member_id, badge_id) among state = awarded.
on member.banned: awards are hidden from every surface; rows are kept.
```

Reason for revocation on overturn only: one honest overturn should not strip recognition permanently, but a badge must not stand on cells that no longer count. Badges are private to the member by default; they appear on a share card only if the member selects them (S12.8).

## 12.8 Share cards (V3)

### 12.8.1 Design decisions [D]

- **Client-side only.** The card is rendered on the member's device from a payload the server returns on request; the server stores no card, hosts no per-member card page and mints no per-member share token. Reason: any per-member public URL or token would link a pseudonym to a public post (FD Principle 8).
- **Explicit action only.** The card is generated only when the member taps a share control; a preview shows exactly the fields and the rendered image; nothing is posted by the platform, no social account is connected, no third-party SDK is loaded (`analytics.third_party_trackers` = false). Sharing uses the device's own share or copy capability [V: support on the target phones, `LaunchGateItem` G2].
- **Eligibility:** `ff.growth.v3_share_card` on, member `status` `active`, tier not `restricted`, at least one accepted cell.
- **No authority:** a card is not a verifiable artifact and the footer says so (`copy.growth.share_card_footer`).
- **Rendering:** bundled fonts only, RTL for `fa`, Persian numerals per `digits`, text alternative provided; no external image or font.

### 12.8.2 Card content spec [D]

`getShareCardPayload` returns an object validated with `additionalProperties: false`:

| Field | Source | Shown on card |
| --- | --- | --- |
| `cells_verified_total` | the member's own accepted cells, all kinds (S12.1 rule 6) | yes, exact |
| `badges` | up to the member-selected `badge_key`s the member holds | yes, only selected |
| `locale`, `digits` | member settings | text language and numerals |
| `landing_url` | the generic landing address with source tag `s=c` | yes; contains no member data |
| `card_version` | int | no |
| static strings | `copy.growth.share_card_footer`, mission line | yes |

**Forbidden on any card or payload:** any id (`mem_`, `vol_`, `lac_`, `dev_`, `ses_`); a handle, alias or name; team name or label; join date or any other time; per-day activity; service, provider or model names and logos; job content or titles; trust tier; credit balance or amounts; rank; location, time zone, device or browser data; a QR code or link that encodes anything member-specific.

### 12.8.3 Attribution and measurement limits [D]

The landing page records a first-touch `source` from the generic tag (`c` card, `r` referral invite, `m` milestone page, none = direct) on the new member's `member.created` event, never from an IP address or cookie. Consequence (`ISS-124`): V3 can measure (a) share taps per exposed member, randomized by the offer, and (b) arrivals with source `c` over time, which is descriptive and confounded. It cannot give a randomized estimate of new members gained per card, because that would need a member-specific token on the card. Adding one is an owner decision for the G1 threat model [V].

## 12.9 Teams (V4)

### 12.9.1 Entities and states [D][A]

`Team` (`tem_`, `member_bound`) as in S0.7. `TeamMembership` is a new entity (`tmm_`, `member_bound`, `ISS-128`): `team_id`, `member_id`, `joined_at`, `left_at` (null while active). A member has at most one active membership.

| `Team` field | Rule |
| --- | --- |
| `name` | Free text up to `team.label_max_chars`; no URLs, e-mail-like or phone-like patterns; reportable (`Report`) |
| `join_mode` | `code` (default, private) or `listed` (appears in the public list) |
| `group_label` | Exists only when `public.location_display` = `opt_in` (below); otherwise the field is rejected with `VALIDATION_FAILED` and never stored |
| `state` | `active`, `locked` (reviewer action after a report), `disbanded` (T) |
| size | at most `team.max_members` active members |

Events: `team.created`, `team.joined`, `team.left`, `team.locked`, `team.unlocked`, `team.disbanded`. Creating needs `trust_tier` at least `team.create_min_tier`; joining needs `status` `active` and tier not `restricted`.

### 12.9.2 Rules [D]

- **Opt-in only.** Creating or joining is an explicit act. No auto-assignment, no suggestion from inferred attributes, no import of contacts. Leaving is one action and removes the member from future scores.
- **Scoring on verified cells.** `score(team, period)` = accepted cells of every `cell_kind` whose acceptance time lies in the period and inside the member's membership interval `[joined_at, left_at)`. A cell counts for the team the member was in at acceptance; history is not imported on joining. Periods: the current UTC calendar week (Monday 00:00 UTC) and all time. A later overturn lowers the score.
- **Teams see only totals.** A team page shows member count, weekly and all-time score. It shows no member list, no per-member contribution, no alias in Phase 1 (basic teams). Reason: pseudonymity inside a group is not guaranteed by the platform, so the platform shows nothing to correlate.
- **Public listing:** only teams with `join_mode` = `listed`, `state` = `active` and at least `team.min_public_members` active members; a team falls out of the list the moment it drops below that size.
- **Location by default: never.** With `public.location_display` = `never` no team carries any place or affiliation label. With `opt_in`: the creator may type a `group_label` (city, school); the platform never infers or verifies it; `copy.growth.team_group_label_warning` is shown before anyone joins; the label is public only for listed teams of at least `team.min_public_members`; no per-member place is ever shown. Iran-based members are not shown by place by default (FD§6.1 rank 5) because the default is `never` and nothing is inferred.
- **Phase 2 “full” teams** (FD§6.1): optional in-team aliases, default off per member, only after the G1 threat model covers them [V].
- **Randomization:** only the in-app offer is randomized (S12.12 `V4`); joining by a code stays possible for everyone while the flag is on.

| Operation (proposal) | Route | Idempotency-Key |
| --- | --- | --- |
| `createTeam` | `POST /v1/teams` | required |
| `getTeam`, `listTeams` | `GET /v1/teams/{team_id}`, `GET /v1/teams` | n/a |
| `joinTeam` | `POST /v1/teams/{team_id}/memberships` | required |
| `leaveTeam` | `DELETE /v1/team-memberships/{membership_id}` (sets `left_at`; the row stays) | required |
| `reportTeam` | `POST /v1/teams/{team_id}/reports` | required |

## 12.10 Referral (V5)

### 12.10.1 Design decisions [D]

- **A referral rides on an `Invite`.** The referral link is a vouched invitation (`Invite`, `invite.*` rules, S0.7), so invite-tree limits apply unchanged. A `Referral` (`ref_`, `member_bound`) adds the bonus state: `invite_id`, `referrer_member_id`, `referred_member_id` (null until joined), `state`, `qualified_at`, `paid_at`, `block_reason`, `grant_txn_id`, `unrecovered_ucr`. A referral link is sent person to person; it is never put on a share card (S12.8), because a public single-use link would be claimed by strangers.
- **Funding: the Reserve, never mint** (`ISS-06`). Both bonuses are `grant` entries `reserve` to `member` with lot lifetime `credit.lifetime_days` (S0.8.5). They pause, never overdraw, at or below `grant.reserve_floor_credits` (FD§4.6: grants are never printed).
- **Two-sided, after the newcomer's verified first cell** (FD§6.2 `V5`): the referrer receives `growth.referral.bonus_referrer_credits`, the newcomer `growth.referral.bonus_newcomer_credits`. This is in addition to the newcomer's starter grant G, which is unaffected.
- **Credit only.** No money, no cash value, non-transferable (`grant.non_transferable`), expiring like any lot (S12.1 rule 4).
- **Phase:** disabled in Phase 1; Phase 2 experiment (S12.12 `V5`).

### 12.10.2 States and events [D][A]

States: `issued`, `joined`, `qualified`, `paid`, `clawed_back` (T), `blocked` (T), `expired` (T). `paid` is terminal except for the clawback transition inside its window (convention addition, `ISS-128`).

```
(none)    --referral.created-->     issued        flag on; referrer caps pass; Invite issued under invite.* rules
issued    --referral.joined-->      joined        newcomer identity created through the invite; device check passes
issued    --referral.expired-->     expired (T)   invite.ttl_days elapsed without a join
joined    --referral.qualified-->   qualified     newcomer has >= growth.referral.min_newcomer_verified_cells accepted cells
joined    --referral.expired-->     expired (T)   growth.referral.qualify_window_days elapsed after joining
qualified --referral.paid-->        paid          payout guards pass; one atomic grant transaction
qualified --referral.blocked-->     blocked (T)   a hard guard fails (see block_reason)
qualified --referral.expired-->     expired (T)   not payable within growth.referral.qualify_window_days of qualified_at (budget paused)
paid      --referral.clawed_back--> clawed_back (T)  clawback triggers below, within growth.referral.clawback_window_days
issued|joined --referral.blocked--> blocked (T)  device match, member status, flag disabled with kill
```

`block_reason` [A]: `same_device`, `referrer_cap`, `tree_cap`, `member_not_in_good_standing`, `qualifying_cell_overturned`, `fraud_finding`, `flag_disabled`.

### 12.10.3 Payout algorithm [D]

A background sweep (`referral.payout_sweep`, every `metrics.rollup_interval_s` [A]) examines `qualified` referrals oldest `qualified_at` first.

```
for ref in referrals where state = qualified order by qualified_at:
    if now < ref.qualified_at + growth.referral.hold_s:                    continue   # delayed payout
    if flag ff.growth.v5_referral is off or kill switch covers it:         block(flag_disabled)
    if either member status != active or tier == restricted:               block(member_not_in_good_standing)
    if newcomer accepted cells (current) < growth.referral.min_newcomer_verified_cells:
                                                                          block(qualifying_cell_overturned)
    if count(paid or qualified refs of referrer, rolling 30*86400 s) > growth.referral.max_per_referrer_per_30d:   block(referrer_cap)
    if count(same for invite tree)  > growth.referral.max_per_invite_tree_per_30d:                                 block(tree_cap)
    # soft guards: wait, do not block
    pair = growth.referral.bonus_referrer_credits + growth.referral.bonus_newcomer_credits   # in ucr
    if paid_today_pairs >= growth.referral.max_per_day:                    continue
    if reserve_balance - pair < grant.reserve_floor_credits:               continue
    if paid_today_ucr + pair > growth.referral.reserve_draw_cap_ratio * reserve_balance_at_utc_day_start:   continue
    post ONE LedgerTransaction kind=grant with two grant entries (reserve->referrer, reserve->newcomer),
         amounts truncated by the K rule of S6.* if a member is at the cap; unique on ref_id (natural idempotency)
    state = paid; emit referral.paid
```

- The `device` check (S0.7 `Device`) runs at `joined`: a newcomer device equal to any device linked to the referrer is `blocked` (`same_device`). **Same IP hash is not a blocking rule**: shared and carrier-grade networks are common, so it would punish real households [H: tested through farming flags, `P1M`]; the caps bound the damage instead.
- **Caps are also enforced at creation:** `createReferral` returns `422 CAP_EXCEEDED` when the referrer already holds `growth.referral.max_per_referrer_per_30d` referrals created in the rolling 30 days, or the tree is at `growth.referral.max_per_invite_tree_per_30d`; and `invite.max_active_per_member`, `invite.min_accepted_cells_to_issue`, `invite.tree_max_members`, `invite.tree_max_depth` apply as for any invite.
- **Worst-case Reserve draw per UTC day** = `growth.referral.max_per_day` x (referrer bonus + newcomer bonus); with the initial defaults that is 5 x 2 = 10 credits, and never more than `growth.referral.reserve_draw_cap_ratio` of the Reserve balance at the start of the day, so the starter grants of FD§4.6 are not starved. Farming economics are a hypothesis [H]: a fake identity costs one verified cell plus an identity, and yields the bonus pair plus G; the per-device, tree, referrer and day caps are the control, measured as farming flags in `P1M`.

### 12.10.4 Clawback [D]

Triggers inside `growth.referral.clawback_window_days` after `paid_at`: (1) the newcomer's accepted cells fall below `growth.referral.min_newcomer_verified_cells` through `cell.overturned`; (2) `member.banned` for either party with a fraud finding; (3) an operator finding. The system opens, for each of the two `grant` entries, a **reversal proposal for the unspent remainder of its lot** only: `ledger.allow_negative_balance` is false, so a spent portion cannot be recovered. A reversal needs two operator approvals (`ledger.reversal_min_approvers`, `security.two_person_actions`); when both commit the referral becomes `clawed_back` and `unrecovered_ucr` records what was already spent. A partial-amount reversal of a partly spent lot is not defined in S0.8.5 and is requested from `S6.*` (`ISS-125`). Until approved the credit remains the member's; a delay is accepted and published as a gauge (`hamyar_growth_referral_unrecovered_ucr_total`).

### 12.10.5 Interfaces [D][A]

| Operation (proposal) | Route | Notes |
| --- | --- | --- |
| `createReferral` | `POST /v1/referrals` | `Idempotency-Key` required; returns the invitation link once; caps checked |
| `listReferrals`, `getReferral` | `GET /v1/referrals[/{referral_id}]` | The referrer sees counts and states only, never who joined or what they did; the newcomer sees only their own bonus state |
| payout, clawback | system and admin only | No member-callable payout route exists |

Copy: `copy.growth.referral_terms` (S12.14): bonuses are declared, may be delayed or withheld, can be reversed, and have no cash value.
