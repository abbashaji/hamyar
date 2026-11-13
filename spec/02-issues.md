# 2. Issues found in the Founding Document, and resolutions

*Spec part 2 · owner cell C-028 (supersedes C-001) · consolidates the `## Issues raised` tables of the other parts · every finding below was checked against the text of the Founding Document draft v0.1 (FD) and cites the section it rests on. Nothing here is legal advice, and nothing here has been verified against any provider's terms or any law.*

## 2.1 How issues are recorded

- An issue is a conflict inside the FD, a gap that blocks an implementation, a rule that cannot be implemented or tested as written, or a conflict between the FD and the brief. Each has one resolution that every part applies. [D]
- A finding is listed only if the FD text it rests on was read and cited. Where the FD is silent the issue says “gap”, not “contradiction”. Items that were examined and found consistent are in 2.7, so the reader can see what was checked. [D]
- A resolution is a decision of this spec [D] unless it carries another tag. Where it introduces a number, the number is derived by a shown formula or is an `initial configurable default` already in S0.10.6.
- Where a resolution needs a name that S0 lacks, the name is listed in 2.8 as a convention gap (S0.1). Where a resolution would change an S0 decision, the issue says so and its status is `proposed` until the owner accepts it; until then every part uses the S0 text.

**Numbering.** `ISS-01`..`ISS-09` are the part-0 issues, kept with their ids and consolidated in 2.3. The findings of this part are numbered inside the three blocks inherited from the superseded first cell (S0.13): `ISS-11`..`ISS-19`, `ISS-21`..`ISS-29` and `ISS-31`..`ISS-38`, in order of severity and then of FD section. Blocks `ISS-41` onward belong to the later parts (S0.13). See `ISS-37`. [D]

| Severity | Meaning (S0.4) |
| --- | --- |
| `blocking` | Cannot be implemented as written |
| `major` | Changes a design |
| `minor` | Naming, wording, counting |

| Status | Meaning |
| --- | --- |
| `applied` | Already embodied in S0 or in the text of this spec |
| `proposed` | Resolution is applied by the parts until the owner accepts or replaces it |
| `needs_owner` | Rests on a decision only the owner can make; listed in S3.2 with the default used meanwhile |
| `accepted`, `rejected` | Set by the owner after review; none yet |

## 2.2 Register

| id | severity | FD ref | One-line finding | status | Detail |
| --- | --- | --- | --- | --- | --- |
| `ISS-01` | minor | prompt | `M0`..`M2` clash with build milestones | applied | 2.3 |
| `ISS-02` | major | FD§5.3, FD§8.3 | “Unknown is no” is safe only for permission-phrased flags | applied | 2.3 |
| `ISS-03` | major | FD§4.2, FD§4.3 | Do verification cells inside Commons jobs mint? | proposed | 2.3 |
| `ISS-04` | minor | FD§3.3, FD§4.3 | v times N is rarely a whole number of cells | proposed | 2.3 |
| `ISS-05` | minor | FD§4.3 | “Rework cell” is undefined | proposed | 2.3 |
| `ISS-06` | major | FD§4.6, FD§6.2 | Referral bonus has no funding source | proposed | 2.3 |
| `ISS-07` | major | FD§4.5, FD§4.8 | Escrow versus credit expiry | proposed | 2.3 |
| `ISS-08` | minor | FD§4.6 | No ledger operation seeds the Reserve | applied | 2.3 |
| `ISS-09` | major | FD§3.2, FD§4.2 | When donors are paid | proposed | 2.3 |
| `ISS-11` | blocking | FD§4.2, FD§5.4 R7, FD§8.3 | The exit rule can pass while no service can run a Commons cell, so nothing can mint | proposed | 2.4 |
| `ISS-12` | blocking | FD§2, FD§4.4, FD§5.5, FD§10 | The code-change template needs test execution; the FD forbids executing submitted content and quarantines code | proposed | 2.4 |
| `ISS-13` | major | FD§4.1, FD§4.3 | A fractional price against a one-credit unit | applied | 2.4 |
| `ISS-14` | major | FD§4.2, Principle 2 | “Every unit traces to a Commons cell” cannot be checked for fungible credit | proposed | 2.4 |
| `ISS-15` | major | FD§4.2, FD§4.7, FD§4.8 | “Redeemable capacity” is undefined, circular with φ, and the cap has no exhaustion rule | proposed | 2.4 |
| `ISS-16` | major | FD§4.3, FD§4.4 | v does not say who funds blanket redundancy or third executions, and the pool is fixed while the need is random | proposed | 2.4 |
| `ISS-17` | major | FD§3.2, FD§4.4, prompt | No rule for credit already paid when a result is overturned or a member is banned | proposed | 2.4 |
| `ISS-18` | major | FD§4.5 | K ignores escrow and has no rule when earning would exceed it | proposed | 2.4 |
| `ISS-19` | major | FD§4.6, FD§9 | The Reserve cannot be seeded in Phase 0 under the launch gates | needs_owner | 2.4 |
| `ISS-21` | major | FD§2, FD§3.1, FD§4.4, FD§6.4 | “Reviewer” means two roles, and review cells pay a credit though they use no allowance | proposed | 2.5 |
| `ISS-22` | major | FD§4.2, FD§5.2 | Commons jobs have no requester, declarant or publisher | needs_owner | 2.5 |
| `ISS-23` | major | FD§5.3, FD§8.3 | G0 has 11 questions, the registry 7 flags; approval names a flag that does not exist; the region flag has no consumer | proposed | 2.5 |
| `ISS-24` | major | FD§5.3, FD§5.6 | M2 has no registry record and no proof of the model | proposed | 2.5 |
| `ISS-25` | major | FD§5.4 R3, FD§3.2 | R3 forbids links to open, yet the flow says “open the prompt”; the rule is not testable | proposed | 2.5 |
| `ISS-26` | major | FD§5.4 R8, FD§5.2 | R8 filters on topic, but no declaration or source of topic exists | proposed | 2.5 |
| `ISS-27` | major | FD§5.4 R9 | Which policy version the re-check uses, and who is paid for in-flight work | proposed | 2.5 |
| `ISS-28` | major | FD§5.5, FD§4.4 | The fixed card sentence is untrue for gold and Commons cells and for unreviewed data | proposed | 2.5 |
| `ISS-29` | major | FD§5.6 | The scope of the salted volunteer ID is undefined | proposed | 2.5 |
| `ISS-31` | major | FD§8.3 | The exit rule governs building; the brief says build everything and gate launch | applied | 2.6 |
| `ISS-32` | minor | FD§4.4 | Audit comparators for free text versus “no model-based judging” | proposed | 2.6 |
| `ISS-33` | minor | FD§4.5, FD§4.6 | “Expires quickly” is undefined; the default grant buys two cells | applied | 2.6 |
| `ISS-34` | minor | FD§4.8 | Deadline classes are undefined at a multiplier of 1.0 | applied | 2.6 |
| `ISS-35` | minor | FD§5.7 | “Two active profiles” does not match the axes it lists | proposed | 2.6 |
| `ISS-36` | minor | FD§6.1 | “Iran-based members are not shown by place” needs inference of location | proposed | 2.6 |
| `ISS-37` | minor | none | The cell instruction's issue numbering collides with S0.4 | applied | 2.6 |
| `ISS-38` | minor | none | S0 has no id scheme for assumptions and open decisions | proposed | 2.6 |

Counts: 35 issues in all: 2 `blocking`, 22 `major`, 11 `minor`. Part 0 contributes 9 (5 major, 4 minor); this part contributes 26 (2 blocking, 17 major, 7 minor). [D]

## 2.3 Issues consolidated from S0 (`ISS-01`..`ISS-09`)

These nine were raised while fixing the shared vocabulary. Their resolutions are already in S0 and are kept as they are. The last column records what this register adds, so a part reading only S0 does not miss it. [D]

| id | Resolution in force (S0) | Applied in | What this register adds |
| --- | --- | --- | --- |
| `ISS-01` | Build milestones are `BM0`..`BM9`; `M0`..`M2` stay service requirements (S0.12) | S17.*, every part | Nothing |
| `ISS-02` | Every gating flag is phrased as a permission; risk flags are `info.*` and never gate (S0.8.3) | S7.*, S14.* | `ISS-23` shows the flag list still does not cover every G0 question |
| `ISS-03` | Every accepted Commons cell of any `cell_kind` mints 1,000,000 `ucr` and counts against `mint.monthly_cap_credits`; the Commons verification share is published | S6.*, S8.*, S13.* | `ISS-15` adds the lease-time headroom rule so a capped period never leaves accepted work unpaid; `ISS-21` applies the rule to review cells |
| `ISS-04` | v is stored in ppm and rounded up; the pool is `floor(pool / 10^6)` cells; the remainder is refunded | S6.* | `ISS-16` makes the pool a hard budget and says what happens when verification needs more |
| `ISS-05` | `rework` is a replacement cell created by `cell.overturned`, paid from the pool, counted in v | S5.*, S6.*, S8.* | `ISS-17` says what happens to the credit already paid for the overturned cell |
| `ISS-06` | Referral bonuses are `grant` entries from the Reserve, never `mint` | S6.*, S12.* | `ISS-19` says how the Reserve is first funded, which both grants and bonuses depend on |
| `ISS-07` | A refund restores consumed lots with their original expiry; a restored lot past expiry moves to the Reserve at the next sweep | S6.* | Read as set out below; reservations follow the same rule |
| `ISS-08` | Entry type `reserve_donation`, `member` to `reserve`, oldest lots first | S6.*, S10.* | `ISS-19` says when founders can use it |
| `ISS-09` | Donors are paid per accepted cell at acceptance; settlement posts only levy and refund and leaves the escrow at zero | S6.*, S9.* | `ISS-27` says what is paid when a policy change voids work that was already submitted |

**Reading of `ISS-07` applied by this spec [A].** The S0 wording “escrow neither extends nor stops expiry” can be read two ways: that lots inside an escrow keep expiring, or that a lot is not extended by having been escrowed. This spec applies the second reading, because the first would shrink an escrow that is already priced and quoted: [D]

1. Credit consumed into an escrow has left the member's lots (S0.8.5, `escrow_hold`). While it is held it cannot expire.
2. Donors paid from the escrow receive new lots dated from the payout. No lot's expiry is extended.
3. A refund restores the unspent part with its original `expires_at`. If that date has passed, the lot moves to the Reserve at the next `expire` sweep.
4. A reservation (`Reservation`, held up to `reservation.max_horizon_days`) follows the same rule. Booking early with credit close to expiry, then cancelling late, therefore returns that credit to the Reserve and not to the member.

| Check | Given | When | Then |
| --- | --- | --- | --- |
| `ISS-07` reading, carried as an `AC-ledger-nn` in S6.* | A lot of 10 credits expires in 5 days and is consumed into a reservation | The reservation is cancelled on day 10 | The refund restores the lot with the original expiry; the next sweep posts an `expire` entry of 10 credits to the Reserve; all `INV-L*` checks pass |

## 2.4 Blocking and major issues, part A (`ISS-11`..`ISS-19`)

Each entry has the same four parts: what the FD says and where it fails; why it matters; the resolution every part applies; the parts that apply it. [D]

### ISS-11 · blocking · FD§4.2, FD§5.3, FD§5.4 R7, FD§8.3 · proposed

**Finding.**

- FD§4.2 mints credit only for accepted Commons cells, and FD§5.3 makes every Commons job purpose `P1` (open publication).
- R7 requires the open-publication flag of the service to be `yes` for `P1`, and `unknown` counts as `no` (FD§5.3).
- FD§5.3 lets a service reach `approved` on two flags alone (third-party task use, prohibited content), and the exit rule of FD§8.3 asks for one approved service or a documented fallback.
- So one approved service can satisfy the exit rule while no Commons cell may run on it. Nothing can then be accepted, minted or spent.
- R7 gives one example only, `P1` against the open-publication flag. It says nothing about `L1` (public-domain dedication) or `L2` (open license with attribution), although dedicating rights is a different act from publishing.

**Why it matters.** The G0 sign-off would not reveal this. The system would launch into a state where the first donors can do nothing that earns credit.

**Resolution.** [D]

1. The derived predicate `commons_capable(service)` is true when the entry is `approved` and the current dated answers for `open_publication_of_output` and `human_copy_paste_use` are `yes`. `unknown` is `no`.
2. The count compared with `launch.min_approved_services` is the number of `commons_capable` services. The FD's alternative, a documented fallback, is a `LaunchGateItem` signed off with an evidence note, never an implicit pass.
3. R7 becomes data. Each allowlist row (S7.*) lists the flags it requires. Initial rows: `P1` with `L1` and `P1` with `L2` both require `open_publication_of_output`; the `L1` row also carries a counsel note [V: whether a provider's terms let a requester dedicate output to the public domain; stored on the allowlist row and on the `FlagAnswer` note]. If counsel needs a separate flag for dedication, it is added by a convention edit (S0.8.3), not in code. [V]
4. With `M0` the volunteer picks the service, so R7 is evaluated at lease time against the services in the volunteer's declared set, again at submission against the service the volunteer reports, and once more at acceptance (R9). A submission from a service that does not pass is refused with the new reason `reject.service_not_permitted` (2.8).

| Check | Given | When | Then |
| --- | --- | --- | --- |
| Carry as `AC-gate-nn` in S14.* | One `approved` service whose open-publication answer is `unknown` | An operator tries to turn `launch.minting_enabled` on | 403 `LAUNCH_GATE_CLOSED`, the reason names `commons_capable` |

**Applied in.** S7.*, S14.*, S9.*, S6.*.

### ISS-12 · blocking · FD§2, FD§4.4, FD§5.5, FD§10 · proposed

**Finding.**

- FD§2 lists code changes with supplied tests as a likely-fit job type. FD§4.4 lists unit tests among the automatic checks and calls automatic checks the cheapest verification.
- FD§10 requires that submitted content is never executed. FD§5.5 flags outputs containing code to run instead of showing them as results.
- For a code-change cell the output is code. As written, the template's cheapest check requires running submitted code, which FD§10 forbids, and every output of the template trips the quarantine trigger.

**Why it matters.** The template cannot be built as the FD describes it, and the first attempt to build it would either break the no-execution rule or quarantine every result.

**Resolution.** [D]

1. In Phases 1 and 2 the platform never executes submitted content: no sandbox, interpreter, test runner or build step touches a submission. Whether to allow a sandbox later is an owner decision in S3.2; the default is no.
2. The automatic checks of `code_change_tests` execute nothing. The output must parse as a unified diff, apply cleanly to the supplied base text, touch only the declared paths, stay inside the size limits and pass the screening patterns of S9.*. The supplied tests are run by the requester on the downloaded result; the manifest says so.
3. Verification of this template is therefore sampled: a second execution with a normalized-patch comparator, hidden gold cells with known-answer patches, and blanket redundancy because the template is marked high-risk (FD§4.4 allows blanket redundancy for high-risk templates). The job-fit test of FD§2 needs an automatic or a sampled check, so the template still qualifies. Its effectiveness is [H]; success means measured false-accept and false-reject rates inside `verify.false_accept_alarm` and `verify.false_reject_alarm`. [H]
4. The quarantine trigger of FD§5.5 is defined on content addressed to the reader: links, instructions to run, open, install or visit, and requests for action. A template whose output schema declares `output_kind` = `code` expects code blocks. They are stored and delivered as inert text, escaped on display, offered only as a download with `Content-Disposition: attachment`, and never rendered or run. Links and reader-directed instructions inside such an output still quarantine.
5. A platform-side sandbox that runs the supplied tests would be a new capability with its own threat-model entry; it is not specified here. [V]

**Applied in.** S8.* (template format, first templates), S9.* (quarantine), S10.* (threat model), S18.*.

### ISS-13 · major · FD§4.1, FD§4.3 · applied

**Finding.** FD§4.1 makes one credit equal one standard cell and FD§4.2 pays one credit per accepted cell, but FD§4.3 prices a primary cell at p = 1 + v + λ, which is fractional (1.15 in the worked example). A job of 10 cells at 1.15 needs 11.5 credits, so an integer-credit ledger must round, and rounding moves value between requester, donors and Reserve. The FD example avoids this only because 240 × 1.15 = 276 is whole.

**Resolution.** Integer micro-credits, as fixed in S0.6.1: one credit is 1,000,000 `ucr`, prices are in ppm, and rounding happens only where a ratio is measured. [D]

**Consequence to record.** At the illustrative v = 0.10 and λ = 0.05 the default starter grant of 3 credits buys `floor(3,000,000 / 1,150,000)` = 2 primary cells, while FD§4.6 speaks of a taster job of a few cells. The size of the grant, `grant.starter_credits`, is a measurement (`P1M`), not a spec decision. [D]

**Applied in.** S6.*, S5.*, S15.*, S11.* (display rounding).

### ISS-14 · major · FD§4.2, Principle 2 · proposed

**Finding.** FD§4.2 states the conservation identity (member balances plus escrow plus Reserve equal cumulative mint minus cumulative retired) and adds that every unit traces to an accepted Commons cell; Principle 2 repeats the claim. Credit is fungible. A transfer creates a new lot for the donor with no pointer to the mint that created the units, and levy, expiry, grant and refund mix units further. A per-unit trace is not defined, so no continuous check can test it.

**Resolution.** Two exact integer checks replace the per-unit trace; S6.* assigns them `INV-L` ids. [D]

1. Conservation: the sum of `member`, `escrow` and `reserve` balances equals cumulative mint minus cumulative retired; the `issuance` balance equals minus cumulative mint; the `retired` balance equals cumulative retired (S0.8.5).
2. Mint provenance: every `mint` entry names exactly one `Cell` that is `accepted` and belongs to a Commons job; a cell has at most one non-reversed `mint`; no other entry type debits `issuance`.
3. Credit is not traced unit by unit. Public text says that credit is created only by accepted Commons cells and that this is checked continuously. It does not say that each unit can be followed.

**Applied in.** S6.*, S12.* (public ledger copy), S18.*.

### ISS-15 · major · FD§4.2, FD§4.7, FD§4.8 · proposed

**Finding.**

- (a) FD§4.2 caps issuance at the forecast redeemable capacity and points to FD§4.7, but FD§4.7 defines the claim ratio and the cap utilization and never defines redeemable capacity; the glossary does not either.
- (b) FD§4.8 gives member jobs a share φ of forecast capacity and leaves the rest, 1 − φ, with Commons work so that minting continues. Minting happens only on Commons work, which uses 1 − φ of capacity, while redeemable capacity is the φ share. The two are equal only at φ = 0.5. Below that a cap tied to φ falls under the Commons throughput; above it the cap does not bind.
- (c) The S0 default of `mint.monthly_cap_credits` writes its factor as (1 − 0.5) without saying that 0.5 is φ. At φ = 0.5 both readings agree, so the FD example cannot tell them apart.
- (d) The claim ratio of FD§4.7 divides unexpired credit by verified weekly throughput, yet that credit is redeemable only on the φ share.
- (e) The FD is silent on a Commons cell accepted after the monthly cap is used up. It would earn nothing, against exactly one credit per accepted cell of any kind (FD§4.3).

**Resolution.** [D]

1. Definitions: `forecast_capacity_cells(period)` is the FD§3.3 formula (active donors × cells per active donor per day × days) × (1 − `admission.forecast_haircut`); `redeemable_capacity_cells(period)` = φ × `forecast_capacity_cells(period)`; `commons_capacity_cells(period)` = (1 − φ) × `forecast_capacity_cells(period)`.
2. The cap stays the independent parameter `mint.monthly_cap_credits`. A new cross-parameter check `C9` (2.8) warns when it exceeds `redeemable_capacity_cells(30 days)` expressed in credits. Derivation of the S0 default with its own inputs: 40 × 8 × 30 × 0.5 = 4,800.
3. The FD claim ratio is kept (unexpired credit ÷ weekly verified throughput, in weeks). A second published figure, `claim_ratio_redeemable` = unexpired credit ÷ (φ × weekly verified throughput), is added. The weeks actually needed are unexpired credit × (1 + v) ÷ p ÷ (φ × throughput), and (1 + v) ÷ p ≤ 1 because p = 1 + v + λ; the published figure is therefore never below the true weeks. The alarm `inflation.claim_ratio_threshold_weeks` compares against the redeemable figure. [A]
4. Exhaustion: leasing a Commons cell reserves 1,000,000 `ucr` of cap headroom on the `Lease` (`credit_reserved_ucr`, 2.8). A Commons cell is not offered when headroom is below 1,000,000 `ucr`, and a lease request answers 422 `CAP_EXCEEDED`. Every accepted Commons cell therefore mints exactly one credit, and no donor does work that earns nothing. A released or expired lease frees its reservation.
5. The cut of FD§4.7 (`inflation.mint_cap_cut_ratio`) is a `tighten` change of the cap. It takes effect for leases issued after it, and the headroom rule means no accepted cell is left unpaid.

| Check | Given | When | Then |
| --- | --- | --- | --- |
| Carry as `AC-ledger-nn` | Cap headroom of exactly 1,000,000 `ucr`; two donors request different Commons cells together | Both lease requests run | One lease is issued, the other gets 422 `CAP_EXCEEDED`, and the period's minted total never exceeds the cap |

**Applied in.** S6.*, S9.* (lease guard), S13.* (published figures), S16.*.

### ISS-16 · major · FD§4.3, FD§4.4 · proposed

**Finding.** FD§4.3 defines v as audit, gold and rework cells over accepted primary cells, measured per job type over a trailing window, and has each job's escrow pay a verification pool of N × v.

- (a) Blanket triple redundancy (FD§4.4, for new donors' first cells and high-risk templates) adds two paid executions per cell, far above v = 0.10. The FD does not say whether they count in v or who pays.
- (b) The third execution after an audit mismatch is not listed in the numerator.
- (c) Gold cells are inserted at rate g into batches and belong to no requester; the FD does not say which job pays them.
- (d) The pool is fixed at quote time, the need is random (mismatches, sampling that rises on anomaly), and the sampling floor of FD§4.4 may not be waived. The FD does not say what happens when the pool runs out.
- (e) Rejected and expired attempts earn nothing but cost donor effort, so η, which is measured in credit, understates the work behind a requester's cell.

**Resolution.** [D]

1. The numerator of v counts every accepted non-primary cell attributed to a job: `audit`, `third`, `rework`, `review`, `gold`, and every replica of a `blanket_redundancy` execution beyond the first. Each non-primary cell has exactly one job (for a gold cell, the job whose batch it was inserted into) and is paid from that job's pool.
2. The quote uses `v_quote` = max(measured v, v_floor) with v_floor = `verify.audit_rate_floor` + `verify.gold_rate_floor`; the initial value is 0.02 + 0.01 = 0.03, derived. The floors then fit in the pool in expectation.
3. The pool is a hard budget. When it cannot pay another verification cell, and the floor or an anomaly still requires one, the job stops with closure reason `verification_budget_exhausted` (2.8) and settles partially (`job.settled_partial`); unspent escrow is refunded. The Reserve never subsidizes verification, because FD§4.2 gives it one outflow, starter grants. [A]
4. Blanket redundancy for a new donor's first cells (`verify.new_donor_blanket_cells`) applies only to Commons cells, which are funded by mint under `ISS-03`; cells of member jobs are leased only to donors who are past that phase. High-risk templates keep blanket redundancy on every cell; their measured v reflects it and their quote is higher. [A]
5. Next to η the platform publishes `attempt_yield` (accepted cells ÷ leased attempts over the trailing window), so the effort behind η is visible.

**Applied in.** S6.*, S8.*, S13.*.

### ISS-17 · major · FD§3.2, FD§4.2, FD§4.4, prompt scope I · proposed

**Finding.** FD§3.2 and FD§4.2 pay at acceptance (`ISS-09`), and FD§4.4 lets donors appeal rejections. The brief (scope I) adds takedown and bans. S0 adds the state `cell.overturned`. None of these says what happens to credit already paid when a cell is later overturned, when fraud is found after payment, or when a member is banned or closes. S0 forbids negative balances (`ledger.allow_negative_balance` = false), so a reversal that finds the credit spent cannot simply take it back.

**Resolution.** [D][A]

1. A reversal of a `mint` or `transfer` is posted only against the unspent part of the lots it created. Credit already spent stays valid.
2. The shortfall, `unrecovered_ucr`, is recorded on the reversal's `LedgerTransaction` and published as a running total. It is bounded by the monthly mint cap (for mints) and by job size (for transfers).
3. The conservation identity needs no repair: total credit in existence is cumulative mint minus cumulative retired, not credit that was deserved.
4. A ban freezes spending (status `banned` forbids `escrow_hold`, `reserve_donation` and referral), revokes open leases, and settles the member's running jobs by the cancel path. The lots keep expiring to the Reserve on their dates, and nothing is seized into any person's account. An overturned ban restores spending; lots that expired stay expired. Closure (`member.closed`) leaves lots to expire in the same way.
5. Reversals and ban appeals follow `ledger.reversal_min_approvers` and `appeal.ban_min_reviewers` (S0.10.6).

**Applied in.** S6.*, S10.*, S5.*.

### ISS-18 · major · FD§4.5 · proposed

**Finding.** FD§4.5 caps unexpired credit per member at K so that no claimant holds an outsized share of future capacity. It does not say whether credit in escrow counts, nor what happens when an accepted cell would push a donor above K. Without a rule a member can hold K in balance and K more in escrow, a claim of 2K, and a donor at K either loses earned credit or is paid beyond K.

**Resolution.** [D]

1. K applies to the member's unexpired balance plus the member's own escrowed amounts for running jobs and held reservations, which are still the member's claim on capacity.
2. Earning is prevented, not clipped. A cell is not offered to a donor, and a lease request answers 422 `CAP_EXCEEDED`, when holdings plus the `credit_reserved_ucr` of the donor's active leases plus this cell's 1,000,000 `ucr` would exceed the member's effective K, `credit.member_cap_credits` × `trust.cap_multiplier.<tier>`.
3. `refund`, `reversal` and `grant` may take holdings above K; they are exempt from the check, and the member simply cannot earn more until holdings fall below K.
4. Constraint C8 of S0.10.3 already warns when K is below the price of a maximum job.

**Applied in.** S6.*, S9.* (lease guard).

### ISS-19 · major · FD§4.6, FD§9 · needs_owner

**Finding.** FD§4.6 says that in Phases 0 and 1 the Reserve is seeded by the founders' own verified Commons work. FD§9 describes Phase 0 as founders and a few testers running cells on their own accounts, with no members, and ends it on G0 and G1. Under the brief's launch gates `launch.minting_enabled` stays `false` until sign-off, and minting needs an approved service (G0). So no credit can be minted and the Reserve cannot be seeded during Phase 0. After launch the Reserve starts at zero, and grants pause when it is empty (FD§4.6, `grant.reserve_floor_credits` = 0), so early newcomers get no starter grant until founders have worked and donated.

**Resolution.** [A]

1. Phase 0 produces `CalibrationRecord`s only: no ledger entries and no member credit.
2. The Reserve starts empty. Founders join through operator-issued root invites after sign-off. S10.* defines root invites, and they too are refused while `launch.members_may_join` is `false`, so the hard gate stays hard.
3. Founders seed the Reserve with `reserve_donation` (`ISS-08`) after their first accepted Commons cells.
4. The sign-off screen (S14.*) shows the Reserve balance and the number of starter grants it can fund (balance ÷ `grant.starter_credits`). Waiting until that number covers the planned pilot is guidance and a dashboard figure, not a technical block.
5. The owner decides, in S3.2, whether founders run a seeding period before the pilot is invited or accept a start with paused grants.

**Applied in.** S6.*, S10.*, S14.*, S17.* (`BM7` acceptance).

## 2.5 Major issues, part B (`ISS-21`..`ISS-29`)

### ISS-21 · major · FD§2, FD§3.1, FD§4.4, FD§6.4 · proposed

**Finding.**

- “Reviewer” names two things: the admin-side role for templates, policy and appeals (FD§3.1), and the people who rate sampled outputs, a role that needs no provider account (FD§2, FD§4.4, FD§6.4 channel 2). The first needs the admin tools; the second needs to read one output at a time and nothing else.
- FD§4.3 pays exactly one credit per accepted cell of any kind, so a review cell pays a credit. A credit is a claim on future cells of work (FD glossary), and a cell is a prompt-and-response unit that a volunteer runs on their own allowance (FD§4.1); a review cell consumes none.

**Resolution.** [D][H]

1. Two things get two names (S0.8.2). `reviewer` is the admin role. Executing a review cell is a member activity on `cell_kind` `review` and carries no permission beyond reading the one output shown.
2. The FD rate is kept: a review cell pays 1,000,000 `ucr` at acceptance. In a Commons job it mints (`ISS-03`); in a member job it is paid from the pool (`ISS-16`).
3. The risk that review becomes a cheap way to earn credit is a hypothesis [H]. It is measured by `review_share_of_mint` (published beside v) and by each member's accepted-review rate. The founders record, before Phase 1, the thresholds at which `ff.channel.human_review` is switched off (`FND` in a `PreRegistration`); this spec sets none.
4. The monthly cap and `mint.per_member_daily_cap_credits` apply to review cells like any other cell. A member never reviews their own output, and review cells have their own gold cells (`verify.human_review_gold_rate`).
5. The channel stays behind `ff.channel.human_review`, default off. Enabling it for the pilot is an owner decision (S3.2).

**Applied in.** S5.*, S6.*, S8.*, S10.*, S11.*.

### ISS-22 · major · FD§4.2, FD§5.2, FD§9 · needs_owner

**Finding.** A Commons job is a public-benefit job from a standing backlog (FD§4.2 and the glossary). Every other job in the FD has a requester who declares purpose, license, sensitivity and service requirement and whose pseudonym is added to the metadata (FD§5.2). Nobody is named as the requester of a Commons job: who declares its metadata, who approves it, who receives or publishes its output, and what a sponsor is in Phase 2 (FD§9) are all open. Open publication (`P1`) also cannot carry private input.

**Resolution.** [D][A]

1. A Commons job has no `requester_member_id` and carries a public `sponsor_label` (default `Hamyar`). The label stands where the requester pseudonym would stand in the job metadata (2.8).
2. Authoring needs the permission `perm.job.create_commons`, held by operators. The author writes the declarations, and a second admin must approve the job (`commons.job_approve`, added to `security.two_person_actions`) before any cell is created.
3. A Commons job is always `P1`, license `L1` or `L2`, sensitivity `S0` and requirement `M0` or `M1`. Sensitivity `S1` is excluded because publishing private material openly contradicts the definition of `S1` (FD§5.3).
4. Outputs are published only to the `publication_target` recorded on the job. Until the owner has chosen an archive (S3.2), outputs stay in the deliverable and nothing is published.
5. A sponsor label naming an outside party needs the same approval. No money moves in Phase 1 (FD§0.2) [P].

**Applied in.** S5.*, S7.*, S10.*, S11.* (operator tools), S12.*.

### ISS-23 · major · FD§5.3, FD§8.3 G0 · proposed

**Finding.**

- G0 asks 11 questions about each service, (a) to (k). FD§5.3 defines 7 registry flags: third-party task use, pooling or crediting, automation limits, regional availability, commercial use, training use and open publication.
- Questions (h) (what the provider does with chats, memory and connectors), (i) (usage-policy requirements), (j) (what the free allowance means) and (k) (written permission) have no flag. Question (c) bundles automation, scraping, prefilled links and copy-paste, which one yes/no flag cannot hold.
- The approval rule of FD§5.3 requires acceptable answers on prohibited content, which is not one of the 7 flags.
- “Unknown is no” has a meaning only for yes/no flags; for a free-text answer it has none.
- Regional availability is recorded per region, but none of `R1`..`R10` consumes it, and the platform cannot know where a member is (FD Principle 8).

**Resolution.** [D][A]

1. S0.8.3 already maps G0 to 9 gate flags and 4 info flags. This register adds the rules below and fixes the mapping, so no part reinvents it:

| G0 question | Flag key | Kind |
| --- | --- | --- |
| (a) third-party task use | `third_party_task_use` | gate |
| (b) pooling or crediting | `access_pooling_or_crediting` | gate |
| (c) automation, copy-paste, prefilled links | `human_copy_paste_use`, `prefilled_link_use`; the automation part is the note, because Hamyar automates nothing on the volunteer's side | gate |
| (d) regional availability | `regional_availability`, one answer per region | gate |
| (e), (f), (g) commercial, training, publication | `commercial_use_of_output`, `training_use_of_output`, `open_publication_of_output` | gate |
| (h) chats, memory, connectors | `info.provider_trains_on_chats`, `info.memory_or_connectors_risk` | info |
| (i) usage policy | `prohibited_content_compatible` | gate |
| (j), (k) allowance, written permission | `info.allowance_may_change`, `info.written_permission` | info |

2. Every answer is structured (`yes`, `no`, `unknown`) plus a free-text note. Only the structured answer is evaluated; the note is for humans.
3. An `info.*` answer of `unknown` is shown to volunteers as “not known” and never gates.
4. The approval rule uses `prohibited_content_compatible`, so the gap in FD§5.3 is closed.
5. Region answers are stored per region and shown on the cell card and in the opt-in screen as the reviewer's note. The platform neither tests nor infers a member's region. Eligibility is the member's own declaration at opt-in (“I may lawfully use this service from where I am”), declared and not checked [A][V: counsel on whether and how to ask]. Nothing here helps anyone bypass a restriction (brief ground rule 3).

**Applied in.** S7.*, S11.*, S14.*.

### ISS-24 · major · FD§5.3, FD§5.6 · proposed

**Finding.** `M2` (FD§5.3) means an open-weight model with a checked license, hosted or local, and `P3` requires it unless a service permits training use in writing. The Service Registry records services and their terms, not models and their licenses, so an `M2` requirement has nothing to check. The provenance (FD§5.6) stores the model as reported by the volunteer, attested and not proven, so for `P3`, where the origin of the data is the point, the volunteer's word is all there is. `P3` is locked in Phases 1 and 2, and the Phase 1 profiles are `M0` and `M1` only (FD§5.7), so `M2` has no active use yet.

**Resolution.** [D]

1. `ServiceRegistryEntry` gets `service_kind` (`hosted_service`, `open_weight_model`; 2.8). A model entry stores the model's license as a `TermsCopy` and answers the same flag keys about that license, through the same review machine. A model reached through a third-party host is a `hosted_service` entry with its own terms.
2. The service and model of a submission are labeled “reported by the volunteer, not proven” in every manifest. No `P3` deliverable is described as verified-origin.
3. `P3` and `M2` rows are absent from the allowlist in Phases 1 and 2. They can be added only as an R10 loosen with a public change-log entry.
4. Any local-model channel in FD§6.4 gets the data model and stays off.

**Applied in.** S5.*, S7.*, S8.*, S11.*.

### ISS-25 · major · FD§5.4 R3, FD§3.2 · proposed

**Finding.** R3 rejects any task asking the volunteer to do more than copy, press Send and return text, with no links to open, files to download, installs or credentials. But FD§3.2 step 2 tells the volunteer to copy or open the prompt in the chosen service, and FD§10 describes an open-in-service button and a paste-back field. Opening a prefilled link is a link opened, and pasting into the service and pasting back are not on the list. R3 is also written as a rule evaluated on a job at admission, but what the volunteer is asked to do is written by the platform's card and the template, never by the requester; the requester's data can only carry text that tries to ask something. As worded, R3 cannot be tested.

**Resolution.** [D]

1. The permitted volunteer actions are a closed set, `volunteer_action_set`: copy the prompt; open the service through the platform's own button, only when the entry's `prefilled_link_use` is `yes` and the adapter supports prefill; paste into the service; press Send; copy the answer; paste it back. Nothing else.
2. The only text addressed to the volunteer is platform-owned (the cell card). A template skeleton addresses the model, never the volunteer. Template review includes an automatic lint that rejects any skeleton telling the reader to do something outside the set (S8.*).
3. R3 is evaluated as two checks under the one id `R3`: content (screening of input) and volunteer action (template lint at review, plus input screening for instruction-like text and links under `screen.*`). Reason codes stay `policy.R3.prohibited_content` (S0.8.4).
4. Instructions inside requester data are never obeyed and never shown as instructions. An instruction in the model's output that is aimed at the reader is the case FD§5.5 quarantines (`submission.quarantined`).
5. A link inside public input text, for example a page to translate, is data. It is governed by `screen.max_urls_per_input` and `screen.url_action`, not by R3.

**Applied in.** S7.*, S8.*, S9.*, S11.*.

### ISS-26 · major · FD§5.4 R8, FD§5.2 · proposed

**Finding.** R8 shows a cell only to volunteers whose opt-ins cover its purpose, sensitivity, license, service and topic, and sensitive topic categories are opt-in. FD§5.2 lists four requester declarations and a set of system-added fields; topic is in neither list, and the FD defines no topic list. The last clause of R8 can never be evaluated.

**Resolution.** [D][V]

1. `topic_category_ids` is a mandatory field of every `TemplateVersion`, checked by the reviewer. It describes the kind of work.
2. A requester may add categories from the list when declaring a job and can never remove the template's. Screening may add categories and never remove. The topics of a cell are the union.
3. `TopicCategory` (S0.7) gets `is_sensitive` (2.8). The categories themselves are data entered by reviewers; this spec invents none. [V: who writes the list and with whom, and counsel or a safety adviser for the sensitive categories; stored as `TopicCategory` rows]. `optin.sensitive_topics_default` stays `false`.

**Applied in.** S5.*, S7.*, S8.*, S11.*.

### ISS-27 · major · FD§5.4 R9 · proposed

**Finding.** R9 stamps the policy version at admission and re-checks it at acceptance; a change may stop work in flight but never retroactively legitimizes it. A re-check against the stamped version checks nothing. A re-check against the current version would let a loosening legitimize old work, which R9 forbids, and would let a tightening void a result a donor delivered in good faith. The FD does not say what happens to cells already submitted when a tightening lands, nor who pays for them.

**Resolution.** [D][A]

1. Acceptance requires a pass under the stamped version and under the current version, in that order. Loosening cannot rescue; tightening can stop.
2. A cell that fails only because of a tightening that took effect after its lease was issued becomes `Cell.voided` with reason `reject.policy_changed`. When the change affects the whole job, the job stops with closure reason `policy_stopped`.
3. Payment: a cell that reached `submitted` before the tightening's `effective_at` and passed all checks under the stamped version is paid at the `cell.voided` transition, from the escrow (member job) or by mint (Commons), because the donor followed the rules in force at lease time. It is excluded from the deliverable and flagged in the manifest. A cell not yet submitted is not paid, and the unexecuted part of the escrow is refunded. The cost of a paid but excluded cell falls on the job's escrow. The owner may prefer the Reserve to bear it (S3.2); that would be a new Reserve outflow, which FD§4.2 does not allow today.

**Applied in.** S5.*, S6.*, S7.*, S9.*.

### ISS-28 · major · FD§5.5, FD§4.4 · proposed

**Finding.** The cell card carries a fixed provenance sentence (FD§5.5) that says a stranger asked for the work and that a reviewer checked the text on a date.

- (a) Gold cells come from the platform's hidden library and Commons cells from the project's backlog. No stranger asked for them, and gold cells must look like any other cell (FD§4.4).
- (b) The review the sentence claims covers the template. The data in the slots is screened automatically and by reviewer sampling (`screen.review_rate_new_requester`, `screen.review_rate_established_requester`), so a claim that the text below was reviewed is untrue for inputs that were not sampled. FD Principle 11 allows claiming only what can be shown.

**Resolution.** [D]

1. The “who asked” clause is the same for every cell kind and true for all of them: the work was requested by someone, a member or the project, without saying which. The cell kind is never visible to the volunteer.
2. The review clause states what was reviewed: the instructions of this template were reviewed on a date; and separately whether the data between the markers was screened by a reviewer on a date or only automatically. The card derives this from the actual screening record.
3. All of it is declared, never guaranteed, and its copy keys carry `needs_human_and_legal_review`.

**Applied in.** S11.*, S8.*, S9.*.

### ISS-29 · major · FD§5.6 · proposed

**Finding.** FD§5.6 stores with each output a salted-hash volunteer ID that requesters never see, and says exports carry the provenance as a manifest.

- (a) Whether the salt is global, per member or per job is not stated.
- (b) If a published Commons manifest carries the handle, a handle that is stable across jobs lets anyone link all of one volunteer's published work.
- (c) The S0.6.4 derivation, an HMAC of the member id under one key, is such a stable handle. It can be recomputed from any `mem_` id that remains in other tables after closure (S0.7: `member_bound` rows are reduced to opaque ids).
- “Requesters never see it” and “exports carry this” conflict unless the export omits the handle.

**Resolution.** Proposed change of S0.6.4; item 1 needs no change of S0. [D][A]

1. Exported manifests, to requesters and to the public including Commons, omit the volunteer handle. They carry the hash of the internal provenance record, so a requester can show that the record exists without reading who made it.
2. Internally the handle is `vol_` plus the first 128 bits of HMAC-SHA-256 with key `secret.volunteer_handle_key[version]` over `member_salt` followed by `job_id`. `member_salt` is a random 128-bit value stored in the `Member` row and deleted at closure. The handle differs per job, and after closure it cannot be recomputed from any `mem_` id that remains.
3. Until the owner accepts the change to S0.6.4, parts use the S0.6.4 formula.

**Applied in.** S10.*, S5.* (`Manifest`), S12.* (public ledger), S4.* (secrets).

## 2.6 Major and minor issues, part C (`ISS-31`..`ISS-38`)

### ISS-31 · major · FD§8.3 · applied

**Finding.** FD§8.3 sets an exit rule: building beyond a throwaway prototype starts only when G0 yields at least one approved service (or a documented fallback) and G1 is complete. The brief overrides it: build the full system and gate the launch. Applied to building, the FD rule would stop the work this spec exists to enable.

**Resolution.** The exit rule governs launching. [D][A]

1. `launch.required_gate_ids` defaults to `["G0","G1"]`, `launch.min_approved_services` is strengthened by `ISS-11`, and `launch.min_signoffs` applies (S0.10.6, table C).
2. `G2`..`G5` are not required by default. Each stays a `LaunchGateItem` that an operator may add to the required list.
3. Phase 0 calibration (`G3`, FD§9 Phase 0) is what replaces the envelope and lease defaults, and it may not have happened when the switches are turned on. The sign-off screen therefore lists every parameter that still holds an `initial configurable default`, grouped by measurement code (`CAL`, `DEM`, `P1M`, `FND`, ...), so signers know which values are still guesses.

**Applied in.** S14.*, S17.*, S13.*.

### ISS-32 · minor · FD§4.4 · proposed

**Finding.** Audits compare a second execution under a task-specific comparator (FD§4.4), and model-based judging is not used to mint credit in Phase 1. For translation and summarization the correct outputs are not unique, so a deterministic comparator is either exact match, which mismatches almost always, or an overlap measure with a threshold. A high mismatch rate would trigger third executions at scale and inflate v. Whether any deterministic comparator separates good outputs from bad ones is untested [H].

**Resolution.** [D][H]

1. The comparator is a mandatory field of every template (S8.*), chosen from a closed list of deterministic functions: exact match, normalized equality of fields, structural equality, an edit-distance or token-overlap threshold, patch equality. Thresholds are template parameters. No model is used.
2. Before approval a template's comparator is run on reviewer-made pairs of acceptable and unacceptable outputs, and the measured separation is stored on the template version. A template with no usable comparator samples by human-review cells and is marked so.
3. Success of a comparator is the separation measured on those pairs against a threshold the reviewers set before approval; failure means the template is not approved. [H]

**Applied in.** S8.*, S6.* (effect on v).

### ISS-33 · minor · FD§4.5, FD§4.6 · applied

**Finding.** FD§4.5 gives earned credit a lifetime E from minting. FD§4.6 says the starter grant “expires quickly” and gives no number, so oldest-first spending mixes lots of two lifetimes with one of them undefined.

**Resolution.** `grant.starter_lifetime_days`, `initial configurable default` 14, validated by C4 (not above `credit.lifetime_days`) and replaced by a `P1M` measurement (S0.10.6). Every lot carries its own `expires_at`, so oldest-first spending works per lot. See also the consequence recorded in `ISS-13`. [D]

### ISS-34 · minor · FD§4.8 · applied

**Finding.** FD§4.8 orders requests first-come within a deadline class and fixes deadline-class multipliers at 1.0 in Phase 1. No class list exists, and FD§5.2 lists a deadline among the system-added fields. At a multiplier of 1.0 a faster class would be free priority, every requester would pick it, and classes would carry no information.

**Resolution.** One class, `standard` (S0.8.6), with `admission.deadline_multiplier_standard` fixed at 1.0. Requests are ordered by admission time. The deadline of FD§5.2 is the end of the quoted window, computed by the platform and never chosen. Further classes need prices first and wait for data (FD§4.3); adding one is a convention edit. [D]

### ISS-35 · minor · FD§5.7 · proposed

**Finding.** Failure mode 5 of FD§5.7 says Phase 1 runs two active profiles, written as `P0`/`P1` × `S0`/`S1` × `M0`/`M1`. Those axes give 2 × 2 × 2 = 8 value combinations. Adding the license pairing of FD§5.3 (`L0` with `P0`; `L1` or `L2` with `P1`) gives 3 purpose-license pairs × 2 × 2 = 12 allowlist rows. “Two” matches neither count; it presumably means the two purposes.

**Resolution.** The allowlist is data (S7.*). The initial active rows are the 12 derived above, each with its required flags (`ISS-11`). In this spec a profile is one row. The concern of the FD, that too many combinations cannot be reviewed, is met because 12 rows fit on one reviewable table. [D]

### ISS-36 · minor · FD§6.1 · proposed

**Finding.** FD§6.1 says location or affiliation is opt-in, never required and never inferred, and also that Iran-based members are not shown by place by default. The second clause requires the platform to know who is Iran-based, which is inference, which the first clause forbids.

**Resolution.** No member's place is shown by default; display is opt-in, chosen by the member for themselves, and identical for every member (`public.location_display` default `never`, S0.10.6). The platform never infers it. The per-country carve-out is dropped. [D]

**Applied in.** S10.*, S12.*.

### ISS-37 · minor · none · applied

**Finding.** The instruction for this part numbers new issues from `ISS-01` and reserves `ISS-50` onward for later parts. S0.4 already gives `ISS-01`..`ISS-09` to part 0 with other content and gives each part a block of nine; ids are never reused. S0.13 gives later parts blocks starting at `ISS-41`. Following the instruction literally would put two different issues under `ISS-01`, while S0 and every part written in parallel cite the S0 numbers.

**Resolution.** Part-0 issues keep their ids (2.3). This part uses the blocks of the superseded first cell. Later parts keep the S0.13 blocks. The decision was recorded as a binding note on the cell before any file was written. `ISS-37` is listed in S1's table because it concerns how the spec is numbered. It is raised in the table of S3, which owns the block `ISS-31`..`ISS-39`, and not in S1. [D]

### ISS-38 · minor · none · proposed

**Finding.** S0.5 gives id schemes for invariants, threats, risks, screens, acceptance criteria and tests, but none for assumptions [A] or owner decisions. S3 needs stable ids so that other parts can point at them.

**Resolution.** `ASM-nn` for assumptions and `OD-nn` for open owner decisions: two digits at least, never reused, owned by S3 (convention gap, 2.8). [D]

## 2.7 Examined and found consistent (not raised)

Checks made against the FD text and S0 that produced no issue. They are listed so that a reader can see what was examined. [D]

| Item | Check | Result |
| --- | --- | --- |
| Worked example, FD§3.3 | Capacity 40 × 8 × 2 × 0.5 = 320 against committed 240 + 24 = 264; levy 0.05 × 240 = 12; payout 264 + levy 12 = 276 = 240 × 1.15; η = 1 ÷ 1.15 ≈ 0.87; 240 cells at 8 a day = 30 days | Every figure reproduces; S0.6.1 carries the same steps as `AC-ledger-01` |
| FD symbols and the brief's TBD list | Cell envelope, E, K, v, λ, g, s, φ, G, mint cap and lease timeout each map to a named parameter in S0.10.1 | Complete |
| Policy rules | `R1`..`R10` each have a slug and reason code in S0.8.4 | Complete |
| G0 questions | (a) to (k) are 11 questions, each mapped to a flag key in S0.8.3 | Complete once `ISS-23` is applied |
| Principle count, FD§7 | Three kept, three changed, two merged into one, four added: 3 + 3 + 1 + 4 = 11, from 3 + 3 + 2 = 8 originals | Consistent |
| Cell states, FD§3.4 against S0.9.3 | S0 extends the FD states with `suspended`, `cancelled`, `voided`, `exhausted` and `overturned`; none contradicts the FD | Consistent |

## 2.8 Convention gaps reported by this part

S0.1 allows a part to add a missing name if it reports the addition. The names below are used by the resolutions above and are not yet in S0. The owning part finalizes each; assembly folds them into S0. [D]

| Name | Kind | Needed by | Owning part |
| --- | --- | --- | --- |
| `ASM-nn`, `OD-nn` | Id schemes | `ISS-38` | S3.* |
| `reject.service_not_permitted` | Cell rejection reason | `ISS-11` | S8.*, S9.* |
| `verification_budget_exhausted` | Job closure reason (extends the list in S0.9.2) | `ISS-16` | S5.*, S6.* |
| `C9` | Cross-parameter warning: `mint.monthly_cap_credits` against redeemable capacity | `ISS-15` | S16.* |
| `claim_ratio_redeemable`, `attempt_yield`, `review_share_of_mint` | Published `MetricSnapshot` values | `ISS-15`, `ISS-16`, `ISS-21` | S6.*, S13.* |
| `Lease.credit_reserved_ucr` | Field | `ISS-15`, `ISS-18` | S5.*, S9.* |
| `Job.is_commons`, `Job.sponsor_label`, `Job.publication_target`; `Job.requester_member_id` empty for Commons jobs | Fields | `ISS-22` | S5.* |
| `perm.job.create_commons`; `commons.job_approve` added to `security.two_person_actions` | Permission, action | `ISS-22` | S10.* |
| `ServiceRegistryEntry.service_kind` (`hosted_service`, `open_weight_model`); `FlagAnswer.note` | Field, enum | `ISS-23`, `ISS-24` | S5.*, S7.* |
| `TemplateVersion.topic_category_ids`; `TopicCategory.is_sensitive` | Fields | `ISS-26` | S5.*, S8.* |
| Template fields `output_kind` (`text`, `json`, `code`) and `comparator` | Fields | `ISS-12`, `ISS-32` | S8.* |
| `unrecovered_ucr` on the reversal `LedgerTransaction` | Field | `ISS-17` | S6.* |
| `Member.member_salt` | Field, only if the change to S0.6.4 in `ISS-29` is accepted | `ISS-29` | S5.*, S10.* |
| `commons_capable(service)` | Derived predicate, not stored; `launch.min_approved_services` counts services for which it is true | `ISS-11` | S7.*, S14.* |

## 2.9 Appending issues from later parts

Later parts append issues as `ISS-5x` and above, each in its own file and inside its own S0.13 block: S4 `ISS-41`..`ISS-49`, S5 `ISS-51`..`ISS-56`, S6 `ISS-61`..`ISS-66`, and so on. Assembly lists them in this register under the same severity grouping. [D]

1. Every part ends with `## Issues raised`, with the columns of S0.4 (`id`, `severity`, `fd_ref`, `issue`, `resolution`, `status`). An empty table says “none”.
2. Ids are never reused or renumbered. This register uses `ISS-01`..`ISS-38`; no later part may use an id in that range.
3. A part applies its own proposed resolution until this register records a different one. Where the two differ, this register wins.
4. An issue with status `needs_owner` is also listed in S3.2 with the default the spec uses meanwhile.
5. A name that S0 lacks is reported in the same table as a convention gap and appears in 2.8 at assembly.
6. Assembly checks that every `ISS-nn` cited anywhere in the spec appears in this register.

## Issues raised

This file is the register; the table below lists the issues numbered inside its own S0.13 block. The other ids of this part are raised in S1 and S3 and are all in 2.2. [D]

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-21` | major | FD§2, FD§3.1, FD§4.4, FD§6.4 | “Reviewer” means two roles; review cells pay a credit but use no allowance | 2.5 | proposed |
| `ISS-22` | major | FD§4.2, FD§5.2 | Commons jobs have no requester, declarant or publisher | 2.5 | needs_owner |
| `ISS-23` | major | FD§5.3, FD§8.3 | G0 questions, registry flags and region handling do not line up | 2.5 | proposed |
| `ISS-24` | major | FD§5.3, FD§5.6 | `M2` has no registry record and no proof of the model | 2.5 | proposed |
| `ISS-25` | major | FD§5.4 R3, FD§3.2 | R3 conflicts with “open the prompt” and is not testable | 2.5 | proposed |
| `ISS-26` | major | FD§5.4 R8, FD§5.2 | R8 filters on a topic that nothing declares | 2.5 | proposed |
| `ISS-27` | major | FD§5.4 R9 | Re-check version and payment for in-flight work | 2.5 | proposed |
| `ISS-28` | major | FD§5.5, FD§4.4 | The card sentence is untrue for gold and Commons cells and unreviewed data | 2.5 | proposed |
| `ISS-29` | major | FD§5.6 | The scope of the salted volunteer ID | 2.5 | proposed |
