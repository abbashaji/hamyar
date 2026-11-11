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
