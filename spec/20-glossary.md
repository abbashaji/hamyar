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
