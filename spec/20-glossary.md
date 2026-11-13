# 20. Glossary

*Spec part 20 · provenance: cell C-029 · extends the Founding Document glossary (FD§11) with the terms of the specification. Written against Founding Document draft v0.1 (FD) and `spec/00-conventions.md` (cited S0.*). Nothing here is legal advice and nothing here has been verified against any provider's terms or any law.*

## 20.1 How to read this glossary

- Terms are alphabetical, case-insensitive, ignoring backticks, spaces and hyphens. Greek and single-letter symbols come first in 20.2. [D]
- Where FD§11 defines a term, the meaning below is the FD§11 meaning with the spec identifiers added; where it does not, the term is defined by the spec part named in the last column. [D]
- The last column names the part whose normative text defines the term, in the cross-reference style of S0.3 (`S0.8.1` is a heading of this spec, `FD§11` the Founding Document). A part that is not yet written is cited as `S<n>.*` and `C-001` checks at assembly that every reference resolves. [D][V]
- Identifiers in `code font` are normative and exactly as in S0.*; a glossary entry never overrides the part that defines the term. [D]
- A fact about provider terms, regional availability, pricing, limits or law is never defined here; it is configuration data entered by a human reviewer and tagged [V] where it is mentioned. [D]

## 20.2 Symbols

| Symbol | Meaning | Name in the spec | Defined in |
| --- | --- | --- | --- |
| `E` | Credit lifetime | `credit.lifetime_days` | `FD§4.5`; `S0.10.1` |
| `G` | Starter grant (not the launch gates `G0`..`G5`) | `grant.starter_credits` | `FD§11`; `S0.3`; `S0.10.1` |
| `g` | Gold-cell insertion rate | `verify.gold_rate_g` | `FD§4.4`; `S0.10.1` |
| `K` | Cap on unexpired credit per member | `credit.member_cap_credits` | `FD§4.5`; `S0.10.1` |
| `s` | Audit sampling rate | `verify.audit_rate_s` | `FD§4.4`; `S0.10.1` |
| `v` | Verification overhead; measured, with a prior | `price.v_prior`, `v_ppm` | `FD§11`; `S0.6.1`; `S0.10.1` |
| `p` | Price per accepted primary cell, `p = 1 + v + λ` | `p_ucr` | `FD§4.3`; `S0.6.1` |
| `λ` | Reserve levy | `price.levy_lambda` | `FD§11`; `S0.10.1` |
| `η` | Round-trip efficiency | `eta_ppm` | `FD§11`; `S0.6.1` |
| `φ` | Share of forecast active capacity open to member jobs | `admission.phi` | `FD§11`; `S0.10.1` |

## 20.3 Terms

| Term | Meaning | Defined in |
| --- | --- | --- |
| **Accelerated-expiry arm** | Experiment arm in which credit lifetime is `credit.lifetime_days_accelerated` instead of `credit.lifetime_days`; assignment is random and logged | `FD§4.5`; `S0.10.6`; `S13.*` |
| **Adapter capability fields** | The `adapter.*` fields of a `ServiceRegistryEntry` (prefill support, URL template, URL length limit, copy-only, clean-chat hint); entered by a reviewer, never hardcoded [V] | `S0.8.3` |
| **Admin action** | `AdminAction`: the logged record of every operator and reviewer action | `S0.7` |
| **Admission control** | Accepting a job only if its committed cells over its window fit within φ x forecast active capacity; otherwise a later quote or a waitlist place | `FD§11`; `S6.*` |
| **Allowlist** | The set of permitted purpose, license, sensitivity and service-requirement combinations; data inside a `PolicyVersion` | `S0.8.1`; `S7.*` |
| **Appeal** | `Appeal`: a challenge to a rejection, ban or report outcome, filed within `appeal.window_days` of the decision | `S0.9.7` |
| **Application service** | A module that owns a set of entities and the transactions that change them | `S4.1` |
| **Approved (service)** | The only service state that allows new jobs; reached only with the gate flags `yes`, a saved `TermsCopy` and a recorded reviewer | `S0.8.3`; `S0.9.6` |
| **Attested** | Said of the service and model named in provenance as reported by the volunteer; recorded for audit, not proof | `FD§5.6`; `S0.7` |
| **Audit cell** | A sampled re-execution of a cell by a second donor, compared by a task-specific comparator, with a third execution on mismatch | `FD§11`; `S0.9.8`; `S8.*` |
| **Auth scheme** | `none`, `member` or `admin`; a token of one scheme is never valid on endpoints of another | `S0.8.2`; `S0.11.4` |
| **Badge** | `Badge`: a badge definition whose criteria use verified cells only; a badge held by a member is a `BadgeAward` | `FD§6.1`; `S0.7` |
| **BM0..BM9 (build milestone)** | The ids of the ten build milestones; written `BM`, never `M`, so they do not collide with the service requirements `M0`..`M2` | `S0.12`; `S17.*` |
| **Build is not launch** | The principle that everything is built but no launch switch is on until the gates are signed off; every brake is enforced in the domain layer, inside the transaction it guards | `S4.2.1`; `S14.*` |
| **Calibration (Phase 0)** | Recording cells per day per service, seconds per cell, refusal and failure rates and the copy-paste error rate; stored as `CalibrationRecord`; measurement code `CAL` | `FD§9`; `S0.10.4`; `S13.*` |
| **Cell** | One prompt-and-response unit that fits a single Send inside the cell envelope; the unit of credit. A `Cell` row persists across attempts (`attempt`, limit `cell.max_attempts`) | `FD§11`; `S0.7`; `S0.9.3` |
| **Cell envelope** | Maximum input and output size and expected time of one cell: the parameters `cell.envelope.*` | `FD§4.1`; `S0.10.6` |
| **Cell kind** | `primary`, `gold`, `audit`, `third`, `review` or `rework` | `S0.8.6` |
| **Change class** | `tighten`, `loosen` or `neutral`; tightening takes effect at once, loosening needs notice and a change-log entry (R10) | `S0.8.6`; `S0.10.3` |
| **Change log** | The public record of every parameter, policy, template or service change: `ChangeLogEntry` | `FD§4.3`; `S0.7`; `S12.*` |
| **Claim ratio** | Unexpired credit divided by verified weekly throughput, in weeks of capacity; published, with a threshold parameter `inflation.claim_ratio_threshold_weeks` | `FD§11`; `S0.10.6`; `S6.*` |
| **Commons job** | A public-benefit job with openly licensed output, run from the standing Commons backlog; the only place credit is minted | `FD§11`; `FD§0.1` |
| **Commons Reserve** | The public account funded by the levy and by expired credit, paying starter grants and referral bonuses; entity `Reserve`, bound to the `reserve` ledger account | `FD§11`; `S0.7`; `S0.8.5` |
| **Convention gap** | A name a part needs that S0 does not define; the part reports it in its `## Issues raised` so it can be folded back | `S0.1`; `S0.4` |
| **Copy key** | `copy.<area>.<key>`: a user-facing text key with `fa` and `en` text and the marker `needs_human_and_legal_review` | `S0.5` |
| **Credit** | A non-monetary, expiring claim on future cells of work, minted only for accepted Commons cells; stored as integer micro-credits | `FD§11`; `S0.6.1` |
| **Credit lot** | `CreditLot`: a dated, expiring portion of a member's credit; credit is spent oldest-first | `S0.7`; `S0.8.5` |
| **Deadline class** | `standard` only; its multiplier is fixed at 1.0 in Phase 1 | `FD§4.8`; `S0.8.6` |
| **Declared** | The wording rule for every user-facing promise and policy outcome: "declared" (Persian اعلام‌شده), never "guaranteed"; purpose, license and sensitivity are declarations by the requester that the platform cannot observe | `FD Principle 11`; `S0.2` |
| **Device** | `Device`: a keyed-hash device record used for rate limits and device linking; no fingerprinting beyond what S10.* lists | `S0.7`; `S10.*` |
| **Domain library** | Pure code with no I/O: price, admission, policy evaluation, estimators and state transitions | `S4.1`; `S4.2.1` |
| **Donor** | A member who executes cells with their own account and earns exactly 1 credit per accepted cell of any kind; one of the four roles | `FD§11`; `S0.8.2` |
| **Downstream use uncontrolled** | The tag on openly licensed output, meaning anyone may reuse it; the no-training default binds declared purposes only | `FD§11`; `FD§0.1` |
| **Driver** | One implementation of a port; every port has an in-memory fake and a real driver | `S4.1` |
| **Escrow** | Credit held for a job or reservation from escrow confirmation until settlement or cancel; entity `Escrow` with its own `escrow` ledger account, exactly zero when closed | `FD§11`; `S0.7`; `S0.8.5`; `S0.9.8` |
| **Event** | A domain event named `<entity>.<past_participle>`; one per state change, written to the outbox in the same transaction | `S0.9.1`; `S4.*` |
| **Evidence tag** | `[D]` decision, `[H]` hypothesis, `[V]` verify, `[P]` premise, `[A]` assumption introduced by the spec | `S0.2` |
| **Expiry (of a lot)** | `expires_at = earned_at + credit.lifetime_days x 86,400 s` under the parameter version in force at `earned_at`; expired credit moves to the Reserve | `FD§4.5`; `S0.6.2`; `S0.8.5` |
| **Feature flag** | `ff.<area>.<name>`, default off; includes the growth mechanics `V1`..`V6` | `S0.10.6`; `S12.*` |
| **Flag answer / flag key** | A dated `yes`, `no` or `unknown` for one flag of one registry entry; gating flags are phrased as permissions and `unknown` is evaluated as `no`; `info.*` flags never gate | `FD§5.3`; `S0.8.3` |
| **G0..G5** | The launch gates; see Launch gate. Not the starter grant G | `FD§8.3`; `S0.3` |
| **Gold cell** | A hidden known-answer cell used to estimate a donor's reliability; entity `GoldCell`, answers access-restricted | `FD§11`; `S0.7`; `S8.*` |
| **Hash chain** | Per ledger, `entry_hash` is the SHA-256 of the previous hash concatenated with the canonical entry, with a daily published checkpoint; detects edits, does not replace access control | `S0.6.4`; `S6.*` |
| **Human review cell** | A `review` cell in which a member rates a sampled output; needs no provider account and has its own gold cells; different from the `reviewer` role [H] | `FD§6.4`; `S0.8.2`; `S0.8.6` |
| **Idempotency-Key** | Client header on every state-changing request; same key and body replays the stored response, same key and another body is `IDEMPOTENCY_KEY_MISMATCH` | `S0.11.5` |
| **Invariant (ledger)** | An automated check with an id `INV-L<nn>`, for example total credit in existence equals cumulative mint minus cumulative retired; exact integer equality, zero tolerance | `FD§4.2`; `S0.5`; `S6.*` |
| **Invite tree** | The edges of `Invite` records (vouched invitations); size and depth are limited by `invite.tree_max_members` and `invite.tree_max_depth` | `S0.7`; `S10.*` |
| **Issue** | `ISS-nn`: a problem or gap found in the FD or in an instruction, with a proposed resolution; ids are allocated in blocks per part | `S0.4` |
| **Job** | `Job`: a requester's request, or a Commons job, split into cells; has the state machine of S0.9.2 | `S0.7`; `S0.9.2` |
| **Job type** | `translation_glossary`, `classify_extract`, `summarize_schema`, `code_change_tests`, `format_convert_validator` or `human_review`; extensible as data | `S0.8.6`; `S8.*` |
| **Kill switch** | `KillSwitch`, `released` or `engaged`, for `kill.all_minting`, `kill.all_new_jobs`, a template, a service or a member; engaged by an operator with a logged reason | `S0.9.8`; `S0.10.6`; `S14.*` |
| **Launch gate** | One of `G0`..`G5` (FD§8.3), a checklist of `LaunchGateItem`s with evidence and sign-offs; `G0` (provider terms and law) and `G1` (safety threat model) are always required before launch | `FD§8.3`; `S0.9.8`; `S14.*` |
| **Launch switch** | `launch.members_may_join`, `launch.member_jobs_enabled`, `launch.minting_enabled`; `false` in every build and flipped only by the gate sign-off flow | `S0.10.6`; `S0.12`; `S14.*` |
| **Lease** | Time-boxed hold of a cell by one member, bound to a lease nonce; expires after `lease.timeout_s`; states `active`, `submitted`, `expired`, `released`, `revoked` | `S0.7`; `S0.9.3` |
| **Ledger** | The one append-only, hash-chained double-entry record of credit, in integer micro-credits; accounts of type `member`, `escrow`, `reserve`, `issuance` and `retired`; entries of types such as `mint`, `transfer`, `levy`, `refund`, `expire`, `retire`; grouped in `LedgerTransaction`s | `FD§4.2`; `S0.8.5`; `S6.*` |
| **License** | `L0`..`L3`: the declared output license of a job; the project asserts no ownership of any output [V] | `FD§5.3`; `S0.8.1` |
| **Member** | `Member`: a pseudonymous identity with a `status` and a `trust_tier`, holding the donor and requester capabilities | `S0.7`; `S0.8.2` |
| **Mint** | Create credit for one accepted Commons cell of any `cell_kind`: ledger entry `issuance` to `member`, exactly 1,000,000 `ucr`, bounded by the monthly cap | `FD§11`; `S0.8.5` |
| **Mint cap** | `mint.monthly_cap_credits`: the monthly issuance ceiling per UTC month, never above forecast redeemable capacity | `FD§4.2`; `S0.10.6` |
| **Nonce (lease nonce)** | A 128-bit CSPRNG value (`lease.nonce_bytes` = 16), stored only as a hash, that binds a submission to its lease; replay returns the stored outcome | `S0.6.4`; `S9.*` |
| **Operator** | The admin-side role that runs the platform (in Phase 1 the founders); holds `perm.*` for parameters, kill switches and ledger operations; one of the four roles | `FD§11`; `S0.8.2` |
| **Opt-in** | `OptIn`: a volunteer's purpose, sensitivity, license, service and topic opt-ins; defaults are `P0`, `P1`, `S0`, `S1`; each sensitive topic category is opt-in (R8) | `FD§5.4`; `S0.7`; `S0.10.6` |
| **Outbox** | The table into which an event is written in the same database transaction as the state change it announces | `S0.9.1`; `S4.7` |
| **Parameter** | A named, validated, versioned configuration value `area.name`; changes are prospective unless they tighten (R10); every default is an `initial configurable default` replaced by a named measurement | `S0.10`; `S16.*` |
| **Policy engine / profile** | The evaluator of rules `R1`..`R10` and the allowed combination of purpose, sensitivity, license and service; rows `Policy`, `PolicyVersion` and `Rule` | `FD§11`; `S0.7`; `S7.*` |
| **Policy rule** | One of `R1`..`R10`, with a slug and a reason code; rules are data, evaluated in order, and the first failing rule rejects | `FD§5.4`; `S0.8.4` |
| **Port** | An interface the domain depends on (store, clock, scheduler, alert delivery, backup target); not related to the service-adapter | `S4.1` |
| **ppm** | Parts per million: the fixed-point form of every ratio, 1.0 = 1,000,000 | `S0.6.1` |
| **Pre-registration** | `PreRegistration`: thresholds and decision rules recorded before launch and then locked | `FD§9`; `S0.7`; `S13.*` |
| **Price** | `p = 1 + v + λ` per accepted primary cell; in integers `p_ucr = 1,000,000 + v_ppm + lambda_ppm`; escrow for N primary cells is `N * p_ucr` | `FD§4.3`; `S0.6.1`; `S6.*` |
| **Provenance manifest** | The record of job, template, policy, service, verification and hashes attached to every output; entity `Manifest`; the no-training flag is contractual, not technically enforced | `FD§11`; `FD§5.6`; `S0.7` |
| **Purpose** | `P0`..`P3`: the declared purpose of a job; `P2` and `P3` are locked in Phases 1-2 | `FD§5.3`; `S0.8.1` |
| **Quarantine** | The submission state for output that contains links, code to run or requests for action; withheld from results rather than shown | `FD§5.5`; `S0.9.3`; `S9.*` |
| **Reason code** | `policy.<policy_rule_id>.<slug>` for a requester's rejection and `reject.*` for a volunteer's cell rejection | `S0.8.4` |
| **Recovery key** | The secret that restores a pseudonymous identity without e-mail; at least `identity.recovery_key_bits` bits | `FD§11`; `S0.10.6`; `S10.*` |
| **Report** | `Report`: an abuse or content report from a volunteer or requester | `S0.7`; `S0.9.8` |
| **Requester** | A member who spends credit on a job; one of the four roles | `FD§11`; `S0.8.2` |
| **Reservation** | `Reservation`: a capacity booking for a future date, with credit escrowed at booking | `FD§4.8`; `S0.7`; `S0.9.8` |
| **Reserve ceiling** | `reserve.ceiling_credits`: the published ceiling above which Reserve excess is retired | `FD§4.2`; `S0.10.6` |
| **Retention class** | `permanent`, `member_bound`, `job_bound`, `moderation`, `short` or `ops`: how long a table's rows are kept | `S0.7`; `S10.*` |
| **Retire** | Remove surplus Reserve credit from existence: ledger entry `reserve` to `retired`; the only way credit leaves the system, always logged | `FD§11`; `S0.8.5` |
| **Reviewer** | The admin-side role for templates, services, policy, appeals and audits; distinct from the member activity of executing `review` cells; one of the four roles | `FD§11`; `S0.8.2` |
| **Rework cell** | A replacement cell created when an accepted cell is overturned; paid from the verification pool and counted in v | `FD§4.3`; `S0.8.6`; `ISS-05` |
| **Round-trip efficiency (η)** | `η = 1/(1+v+λ)`: cells a member can request per cell contributed; in integers `eta_ppm = floor(10^12 / p_ucr)` | `FD§11`; `S0.6.1` |
| **Sensitivity** | `S0`..`S3`: the declared data sensitivity; `S2` is rejected and `S3` is never accepted; written without a dot, so it never collides with a spec reference such as `S1.2` | `FD§5.3`; `S0.3`; `S0.8.1` |
| **Service-adapter** | The client-side module that prepares a prompt for one chat service from registry data (prefill where supported, copy-only otherwise); the human presses Send and the chat page is never read | `S4.1`; `S4.14` |
| **Service Registry** | The dated record of each service's terms flags, saved terms copies and review state; every service ships `unreviewed`, and unknown counts as no | `FD§11`; `S0.7`; `S0.8.3`; `S7.*` |
| **Service requirement** | `M0`..`M2`: any approved service, pinned approved services, or an open-weight model with a checked license | `FD§5.3`; `S0.8.1` |
| **Session** | `Session`: a member or admin session; only the hash of the token is stored | `S0.6.4`; `S0.7` |
| **Size class** | `standard`, the only value in Phases 1-2 | `S0.8.6` |
| **Spec reference** | The form `S<n>.<m>`, a heading `## <n>.<m>` of spec part `<n>`; a whole part is `S<n>.*` | `S0.3` |
| **Starter grant** | A small, non-transferable Reserve transfer to a newcomer after `grant.required_verified_cells` verified contribution(s); ledger entry `grant`; expires after `grant.starter_lifetime_days`; pauses, never overdraws, when the Reserve is at or below its floor | `FD§11`; `S0.8.5` |
| **Submission** | `Submission`: one pasted-back result for one lease | `S0.7`; `S0.9.3` |
| **Team** | `Team`: a self-created opt-in group; not shown publicly below `team.min_public_members` | `FD§6.1`; `S0.7`; `S12.*` |
| **Template** | A reviewed prompt pattern with data slots and an automatic check; `Template` is the stable identity and `TemplateVersion` is immutable once approved | `FD§11`; `S0.7`; `S0.9.5`; `S8.*` |
| **Terms copy** | `TermsCopy`: a saved copy of a service's terms (bytes, hash, source reference, capture date); required before a service can be approved | `S0.7`; `S0.8.3` |
| **Transfer** | Move credit between accounts: ledger entry `escrow` to `member`, paid to a donor at acceptance of each cell of a member job; creates no new credit | `FD§11`; `S0.8.5` |
| **Trust tier** | `new`, `established`, `trusted` or `restricted`; raises caps and lowers sampling with a clean record; orthogonal to `member_status` | `FD§6.1`; `S0.9.4`; `S10.*` |
| **ucr** | Micro-credit: 1 credit = 1,000,000 `ucr`; the integer unit of every ledger amount | `S0.6.1` |
| **Unknown** | The flag answer `unknown`, evaluated as `no` everywhere; likewise a service in state `unreviewed` counts as no | `FD§5.3`; `S0.8.3`; `S0.9.6` |
| **Verification method** | `auto_check`, `gold`, `audit_second`, `audit_third`, `human_review` or `blanket_redundancy`, with outcome `pending`, `pass`, `fail` or `inconclusive` | `S0.8.6`; `S8.*` |
| **Verification overhead (v)** | (Audit + gold + rework cells) divided by accepted primary cells over a trailing window per job type; `v_ppm = ceil(10^6 * verification_cells / accepted_primary_cells)`; measured and published | `FD§11`; `S0.6.1`; `S6.*` |
| **Volunteer handle** | `vol_<32 hex>`: the keyed hash of a member id used in provenance; requesters never see it | `S0.6.4` |
| **Waitlist** | `WaitlistEntry`: a place for a job the capacity cannot honor now; the job state is `waitlisted` and the entry lapses after `admission.waitlist_ttl_days` | `FD§4.8`; `S0.7`; `S0.9.2` |

## Issues raised

Problems found while extending the glossary. Each resolution is already applied in this file; `C-001` consolidates them into S2.* and may record a different resolution. [D]

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-201` | minor | FD§11 | FD§11 folds several terms into one entry ("Mint / transfer / retire", "Donor, Requester, Reviewer, Operator"), so a reader looking up one term must know its neighbours | Each term has its own row in 20.3 with the FD§11 meaning kept | applied |
| `ISS-202` | minor | FD§11, FD§4.8 | FD§11 says escrow is held "from submission"; S0.9.2 posts the `escrow_hold` at `job.escrow_confirmed`, after policy and quote | The glossary says "from escrow confirmation"; `S6.*` owns the exact moment | proposed |
| `ISS-203` | minor | none | Several terms are defined by parts that are not written yet, so their "Defined in" cells cite `S<n>.*` | Every such cite uses the `S<n>.*` form of S0.3; `C-001` verifies them at assembly and narrows each to a heading [V] | proposed |
