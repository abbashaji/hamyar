# Hamyar — Founding Document

*Draft v0.1 · 11 November 2026 · for review and editing. Not legal advice: nothing here has been checked by a lawyer or against any provider’s current terms.*

**Tags used throughout:** \[D\] a decision this document makes · \[H\] a hypothesis to be tested · \[V\] must be verified before anyone relies on it · \[P\] a premise taken from the brief and not independently checked.

## 0. Review of the brief (read first; delete when no longer needed)

### 0.1 Contradictions and weak points, and how they are resolved

1. **Capacity cannot be stored, so what is the deposit-phase work for?** The brief corrects “store tokens” to “store credit”, but credit minted for work nobody needs is make-work, and bursty member demand cannot absorb steady supply. *Resolution:* a standing **Commons backlog** of useful, verifiable, openly licensed jobs absorbs steady supply and is the only place credit is minted; member jobs move credit between members (§4.2).
2. **“Credit only from verified work, no free credit” vs. “newcomers need a bootstrap”.** A bootstrap is free credit. *Resolution:* the starter grant is a transfer from a public Commons Reserve (funded by a levy and by expired credit), paid only after a first verified contribution. No credit is ever unbacked (§4.6).
3. **“Completed in one go” vs. queued withdrawals.** *Resolution:* “one go” means one submission by the requester. Completion is promised inside a quoted window, and only if capacity has been reserved (§4.8).
4. **The default policy profile contradicts itself.** “Open-license publication” and “no use of outputs to train other models” cannot both hold downstream: an open license generally cannot forbid training by third parties. *Resolution:* the no-training default binds declared purposes (requesters and the project itself), not downstream readers of openly published output, which is tagged “downstream use uncontrolled”. Whether a given provider allows openly publishing its outputs is \[V\] (§5).
5. **Launch audience vs. access limits.** Persian speakers inside Iran may be unable to use some services lawfully or technically, so supply may sit abroad and demand inside. Credit then flows as aid rather than reciprocity, and “find a workaround” is not an acceptable answer. *Resolution:* members may be donors, requesters or both; a second contribution channel that needs no provider account (human review of outputs) is tested as a hypothesis; the project never instructs anyone to circumvent restrictions; sanctions and terms questions are \[V\] (§6, §8).
6. **Pseudonymity vs. fraud resistance.** *Resolution:* resist fraud with economics, not identity: credit only from verified work, a small starter grant, sampling floors, vouched invitations, rate limits. Residual abuse is accepted and monitored (§4.4, §8).
7. **“Under 60 seconds” vs. “volunteer must see the prompt” vs. prompt injection.** A batch prompt cannot be audited in 60 seconds. *Resolution:* prompts come only from reviewed templates; a one-line card (purpose, license, model, template) is always shown; the full text is one tap away and mandatory for first use of a template and for non-default categories. “Can see” is guaranteed; “has read” is not (§5.5).
8. **“No signup” vs. a per-member ledger.** *Resolution:* an anonymous identity is created locally on first use and protected by a recovery key; e-mail is optional (§10).
9. **“Enforced” data policy is overstated.** Requesters self-declare sensitivity and purpose, and the project cannot observe downstream use. *Resolution:* enforcement is “as far as technically possible” (templates, screening, sampling, bans) and the interface never calls it a guarantee (§5.7, Principle 11).
10. **“Exchange rate near 1:1” vs. verification cost.** *Resolution:* donors always earn exactly 1 credit per accepted cell, audits included; the requester pays 1 + v + λ, where v (verification and rework overhead) and λ (reserve levy) are measured and published. Round-trip efficiency η = 1/(1+v+λ) is the headline number (§4.3).
11. **The panel is tied to one provider and to Windows, but Principle 7 forbids provider dependence.** *Resolution:* a service-adapter layer and a no-install web flow become the default; the launcher becomes optional (§10).
12. **“Clear owner” of outputs.** Whether AI output is protected by copyright, and who holds rights under provider terms, is unsettled and jurisdiction-dependent \[V\]. *Resolution:* every job carries a declared license; volunteers waive claims; the project asserts no ownership (§5, Principle 6).
13. **“Cooperative” and “bank” are loaded words.** Both may carry legal meaning or invite regulation \[V\]. *Resolution:* use “commons” and “contribute / request” publicly; keep “deposit / withdrawal” for internal use.
14. **Pilot design limits.** A 30-day pilot cannot observe 60-day expiry, and 30–50 people cannot statistically test virality. *Resolution:* an accelerated-expiry arm in Phase 1; virality tests move to Phase 2 (§9).
15. **“Collective intelligence” claim.** Excluded from the foundation, as instructed; one optional experiment is parked in Phase 2.
16. **Time-bank precedent is weaker support than it looks.** Time banks typically equate one hour with one hour; here cells differ by task, service and verification cost. Precedent shows people will keep ledgers of mutual help; it says nothing about viability here \[H\].

### 0.2 Assumptions made (no clarifying questions were needed)

- The operator’s legal jurisdiction is unknown, so legal items stay \[V\] until it is chosen. **This is a decision only you can make.**
- The pilot uses one to three general chat services chosen after a terms review. None is named here, on purpose.
- Most members will use phones, and the interface must work in Persian (right-to-left) and English \[H\].
- Founders act as template and policy reviewers in Phase 1.
- A “cell” is one prompt-and-response unit that fits a single Send.
- No money moves in Phase 1.

### 0.3 Name

Working name: **Hamyar (همیار, “fellow helper”)** \[D, provisional\]. It is not tied to any provider or to “tokens”, is short in both scripts, and says what the project is. Availability of the name (organizations, domains, trademarks) is unchecked \[V\]. “Cooperative” is kept only as a description of intent, because in some jurisdictions it is a regulated legal form \[V\]. Public descriptor: “a capacity commons”.

## 1. Vision and definition

**Definition.** Hamyar is a pseudonymous, human-in-the-loop commons in which people spend about a minute a day pressing Send on small, reviewed batches of non-sensitive work using their own free AI accounts, and earn expiring credit for each verified result. Later, when a member has a large job that can be split into independent pieces, they spend credit and other members complete it in parallel within a quoted window, with every result verified and traceable. What members get back is **scale and speed, not tokens**. The commons does not store, transfer or resell anyone’s allowance, does not automate anyone’s account, does not accept sensitive data, and does not claim that many people answer better than one.

**Mission \[D\].** Make large AI-assisted tasks possible for people who cannot pay for them, beginning with Persian speakers, by pooling effort that would otherwise be lost.

**What it is not \[D\].** Not a token exchange; not a reseller of provider access; not an automation or agent system; not a marketplace (deferred); not a privacy service; not a cooperative in the legal sense (yet).

## 2. Problem and who it is for

**Premises \[P\].** Many people have free access to chat AI; the allowance resets or expires; it cannot be stored or moved between accounts; individual need is spiky.

**The problem \[H\].** Someone occasionally has a job too large for one free account in the time available (a long translation, a batch of documents, a code migration with tests), while the same allowance goes unused at other times. A counterpoint to test: heavy users hit their limits daily, so the supply side works only if enough people are *not* using their allowance. How much is idle, per service and per person, is unmeasured \[V\].

**Who it is for \[D\].**

- **Requesters (launch focus):** people without a paid plan who occasionally have a large, splittable job: students, researchers, translators, independent developers.
- **Donors:** anyone with free access and a minute a day. A donor is often a future requester.
- **Launch audience:** Persian speakers, including inside Iran, plus Iranians abroad as donors. This is a launch audience, not a design limit: nothing in the credit or policy layer is language-specific.
- **Reviewers:** people who check outputs or templates, a role that needs no provider account (§6).

**Job-fit test \[D\].** A job is eligible only if all five hold: (1) it splits into independent cells; (2) its data is S0 or S1 (§5); (3) each cell has an automatic or sampled check; (4) the requester accepts a queue window of hours to days; (5) each cell fits one Send within the cell envelope.

- *Likely fits \[H\]:* translation of long public or openly licensed texts with a shared glossary; classification, extraction or summarization of public text into a fixed schema; code changes with supplied tests; format conversion and data cleaning with a validator.
- *Does not fit:* confidential or personal data; interactive drafting; tasks needing whole-document coherence beyond a shared glossary; anything needing web, file or tool access; individual medical, legal or financial advice.

## 3. How it works end to end

### 3.1 Roles

**Donor**, **Requester**, **Reviewer** (templates, policy, appeals) and **Operator** (runs the platform; in Phase 1, the founders). One person can hold several roles.

### 3.2 Flow

1. **Join.** Open the site; an anonymous identity and recovery key are created locally. No install, no e-mail required \[D\].
2. **First contribution.** Pick a Commons card showing purpose, license, required service class and expected time. Copy or open the prompt in your chosen service, press Send, paste the answer back. Target: under 60 seconds once practiced, about 2 minutes the first time \[H\].
3. **Check.** The result is validated automatically and may be a hidden gold cell or be sampled for audit. An accepted cell mints (Commons) or transfers (member jobs) 1 credit.
4. **Habit.** A daily batch is one card or a few. Credit expires after E days (§4.5).
5. **Request.** The requester picks a template, supplies data, and declares purpose, license and sensitivity. The policy engine accepts or rejects (§5). On acceptance the platform quotes a price and a completion window and escrows the credit.
6. **Execution.** Cells are leased to donors with a server-side timeout; cells not returned go back to the queue.
7. **Verification and assembly.** Accepted cells are assembled into one deliverable with a provenance manifest.
8. **Settlement.** Donors receive credit, unspent escrow is refunded, and the ledger and public counters update.

### 3.3 Worked example (all numbers illustrative; none measured)

Sara, a translator without a paid plan, contributes about 10 Commons cells a day for 30 days: 300 credits, none expired (E = 60 days). She then wants a 240-cell translation of an openly licensed text, using a shared 100-term glossary.

- **Price.** Assume the published v = 0.10 and λ = 0.05, so the price is 1.15 per cell: 276 credits are escrowed and she keeps 24.
- **Admission.** Assume 40 active donors average 8 cells a day, and φ = 0.5 of capacity may be committed to member jobs. Over a 2-day window that is 40 × 8 × 2 × 0.5 = 320 cells, at least the 264 that will be executed (240 primary + 24 verification and rework). The job is accepted with a 2-day quote.
- **Settlement.** Donors earn 264 credits by transfer; 12 credits (λ × 240) go to the Commons Reserve; 264 + 12 = 276, so nothing is created or lost.
- **Value to Sara.** Not cell count (η = 1/1.15 ≈ 0.87) but time: one free account at 8 cells a day would need about 30 days for 240 cells; the commons delivers in about 2.

### 3.4 Cell lifecycle

queued → leased (with expiry) → submitted → accepted, rejected or flagged for audit. Rejected and expired cells return to the queue. Every transition is logged with the policy version.

## 4. Credit model

### 4.1 Unit \[D\]

One credit = one standard cell: one prompt-and-response unit inside a fixed envelope (maximum input size, maximum expected output size, one Send, one service class). Phase 1 has a single size class, and the envelope numbers are measured in Phase 0, not guessed. Provider tokens are never the unit. Credit is not money, property or a promised entitlement, and the terms say so; its legal characterization is \[V\].

### 4.2 How credit moves \[D\]

- **Mint.** Only for accepted Commons cells (public-benefit jobs with openly licensed outputs). Minting is bounded by a published monthly issuance cap, set no higher than forecast redeemable capacity (§4.7).
- **Transfer.** For member jobs, the requester’s escrow pays donors 1 credit per accepted cell, verification and rework cells included. No new credit is created.
- **Reserve.** The Commons Reserve is a public account. Inflows: the levy λ and expired credit. Outflow: starter grants (§4.6). If the Reserve exceeds a published ceiling, the excess is retired, which is the only way credit leaves the system, and every retirement is logged.
- **Ledger invariant.** Total credit in existence = cumulative mint − cumulative retired. Member balances + escrow + Reserve always sum to that total, and every unit traces to an accepted Commons cell.

### 4.3 Price and exchange rate \[D\]

The requester’s price per accepted primary cell is **p = 1 + v + λ**.

- **v** = (audit + gold + rework cells) ÷ accepted primary cells, measured over a trailing period per job type and published monthly. Verification cost is shown, not hidden.
- **λ** = the Reserve levy, a published constant.
- **Donor earn rate:** exactly 1 credit per accepted cell of any kind.
- **Round-trip efficiency η = 1/(1+v+λ):** cells a member can request per cell contributed. The design target is η near 1. The acceptance threshold is set by the founders before Phase 1; a suggested starting point is η ≥ 0.8, which is arbitrary, not derived from data.
- Changes apply prospectively, with advance notice and a public change log (Principle 5).
- All service classes and sizes are priced the same in Phase 1; scarce classes simply queue longer. Differential pricing waits for data.

### 4.4 Verification \[D\]

Cheapest first:

1. **Automatic checks:** schema validation, unit tests, format and language checks, length and refusal-pattern detection. Eligible job types are chosen mainly because they have these.
2. **Hidden gold cells:** known-answer cells inserted at rate g into batches, used to estimate each donor’s reliability.
3. **Sampled audit:** a second donor re-executes a sample at rate s; a mismatch under a task-specific comparator triggers a third execution.
4. **Human review:** for subjective tasks, reviewers rate sampled outputs. Review cells are paid and have their own gold cells.

Rules: sampling is adaptive (it falls with a clean record and rises on anomalies) but has a floor, so a patient bad actor cannot coast. Blanket triple redundancy is allowed only for new donors’ first cells and high-risk templates. Model-based judging is not used to mint credit in Phase 1 \[H: may be tested later\]. Rejected cells earn nothing; the donor can see why and appeal. Verification cost is the main threat to a fair rate \[H\], so v is the quantity Phase 1 measures most closely.

### 4.5 Expiry and caps \[D; parameters to be tested\]

Earned credit expires E days after minting (proposal: E = 60, from the brief) and is spent oldest-first; every balance shows its expiry dates. A per-member cap K on unexpired credit bounds any one claimant’s share of future capacity. Expired credit moves to the Reserve; it is never silently deleted. Expiry may feel punitive \[H\]; Phase 1 therefore includes a shorter (for example 14-day) arm, because a 30-day pilot cannot observe a 60-day rule.

### 4.6 Bootstrap \[D\]

A newcomer receives a starter grant G (a taster job of a few cells) from the Reserve after one verified contribution. It is non-transferable and expires quickly. Per-device, per-invite-tree and per-day limits apply. In Phases 0–1 the Reserve is seeded by the founders’ own verified Commons work, not by decree. If the Reserve is empty, grants pause; they are never printed.

### 4.7 Hoarding and inflation \[D\]

Credit earns no interest, expires, and is capped, so hoarding is bounded. Inflation here means more claims than capacity to honor them. Two published gauges apply: the **claim ratio** (unexpired credit ÷ verified weekly throughput, in weeks of capacity) and **mint-cap utilization**. If the claim ratio passes a published threshold, the mint cap is lowered and quoted windows lengthen; credit is not silently devalued.

### 4.8 Queueing and run-on-the-bank handling \[D\]

- **Escrow** at submission; unstarted cells are refundable on cancel.
- **Admission control:** a job is accepted only if committed cells over its window ≤ φ × forecast active capacity (φ < 1; set from measurement, 0.5 in the example). Otherwise the requester gets a later quote or a waitlist place. The remaining (1 − φ) of capacity stays with Commons work, so minting never stops.
- **Reservations:** requesters may book capacity for a future date (exam week, a deadline), with credit escrowed at booking \[H: flattens bursts\].
- **Fairness:** a per-member cap on concurrent jobs; first-come ordering within a deadline class; deadline-class multipliers fixed at 1.0 in Phase 1.
- **Promise:** a quoted window, never instant completion (Principle 10).

### 4.9 Parameter table

| Parameter | Meaning | Initial value |
| --- | --- | --- |
| Cell envelope | Max input and output size per cell | TBD from Phase 0 measurement |
| E | Credit lifetime | 60 days (proposal); 14-day test arm |
| K | Cap on unexpired credit per member | TBD from the size of a typical large job |
| v | Verification and rework overhead | Measured in Phase 1 |
| λ | Reserve levy | TBD (0.05 used in the example) |
| g, s | Gold-cell and audit rates | TBD; adaptive with a floor |
| φ | Share of capacity open to member jobs | TBD (0.5 used in the example) |
| G | Starter grant | A few cells; TBD |
| Mint cap | Monthly issuance ceiling | TBD from measured throughput |
| Lease timeout | Time before a leased cell returns to queue | TBD from measured time per cell |

## 5. Purpose and policy layer

### 5.1 Principle \[D\]

The platform is neutral about end use but never blind to it. Every job carries four mandatory declarations; a policy engine checks the combination against an allowlist; anything not explicitly allowed is rejected. The default profile is the most restrictive safe one: public or non-sensitive data, personal use or open-license publication, and no training use.

### 5.2 Mandatory job metadata \[D\]

Declared by the requester: (1) purpose, (2) output license, (3) data sensitivity, (4) service requirement. Added by the system: template ID and version, content hash, requester pseudonym, deadline, and the policy version at admission.

### 5.3 Taxonomy

**Purposes**

| Code | Purpose | Status in Phases 1–2 |
| --- | --- | --- |
| P0 | Personal, study or internal non-commercial use; output stays with the requester | Allowed (default) |
| P1 | Open publication under an open license; includes all Commons jobs | Allowed (default) |
| P2 | Commercial or professional use of outputs, no training | Locked; unlocks per service only after its terms are verified |
| P3 | Training, fine-tuning, distillation or benchmark creation using outputs | Locked; only on open-weight models with checked licenses, or on services whose terms permit it, and only for S0 data |

No declared purpose → rejected.

**Output licenses**

| Code | Terms | Pairs with |
| --- | --- | --- |
| L0 | Requester only; no publication; volunteers waive claims | P0 |
| L1 | Public-domain dedication (for example CC0) | P1 |
| L2 | Open license with attribution (for example CC BY) | P1 |
| L3 | Requester-defined commercial terms | P2 only |

The project asserts no ownership or copyright in any output. Whether AI output is protectable at all is \[V\].

**Data sensitivity**

| Level | Meaning | Status |
| --- | --- | --- |
| S0 | Public: already public, public-domain, openly licensed, or written for publication | Accepted |
| S1 | Private but non-sensitive: the requester’s own non-confidential material; no credentials, no personal data of identifiable people, nothing under confidentiality; the requester accepts that a stranger will read it | Accepted |
| S2 | Personal data of others, confidential business material, unpublished third-party work | Rejected in Phases 1–2 |
| S3 | Special-category or dangerous: health, legally privileged, minors’ data, credentials, financial identifiers, anything that could identify or endanger a person (including material identifying activists or dissidents) | Never accepted |

**Service requirement**

| Code | Meaning | Use |
| --- | --- | --- |
| M0 | Any approved general chat service; the volunteer chooses; the service is recorded | Default |
| M1 | Pinned approved service(s) named by the requester | Allowed |
| M2 | Open-weight model with a checked license (hosted or local) | Required for P3 unless a service permits training use in writing |

**Service Registry \[D\].** Each service has a dated record with a saved copy of its terms and these flags: third-party-task use, pooling or crediting of access, automation limits, regional availability, commercial use of output, training use of output, open publication of output. Each flag is yes / no / unknown, and **unknown is treated as no**. A service is “approved” only after a reviewer records acceptable answers on third-party-task use and prohibited content.

### 5.4 Policy rules (evaluated in order; the first failing rule rejects)

1. **R1.** Missing or inconsistent metadata → reject.
2. **R2.** S2 or S3 → reject, with the reason shown to the requester.
3. **R3.** Prohibited content → reject: illegal content; harassment or targeting of individuals; malware or exploit work; sexual content involving minors; weapons uplift; deception campaigns; anything a service’s usage policy forbids. Also reject any task that asks the volunteer to do more than copy, press Send and return text (no links to open, files to download, installs or credentials).
4. **R4.** Prompts come only from reviewed templates. Free-form prompts are unavailable in Phase 1.
5. **R5.** P2 runs only on services whose registry flag for commercial output is yes.
6. **R6.** P3 runs only on M2, or on services whose training-use flag is yes; S0 data only.
7. **R7.** The license may not exceed what the service’s flags allow (for example, P1 requires the open-publication flag to be yes for that service).
8. **R8.** A cell is shown only to volunteers whose opt-ins cover its purpose, sensitivity, license, service and topic. Volunteer defaults: P0–P1 and S0–S1; P2, P3 and each sensitive topic category are opt-in.
9. **R9.** The policy version is stamped at admission and re-checked when a result is accepted. A change may stop work in flight but never retroactively legitimizes it.
10. **R10.** Any rule may be tightened immediately; loosening requires a public change-log entry and a stated reason.

### 5.5 What the volunteer sees before sending \[D\]

Every cell shows a fixed card: purpose, license, sensitivity, required service, template name, expected time, and one plain sentence: “A stranger asked for this; the text below was reviewed by a reviewer on \[date\].” The full prompt is one tap away and must be expanded on first use of a template and for any non-default category. Volunteers may decline any cell without penalty (the decline rate is tracked as a demand-quality signal, never punished), and every card has a report button.

*Prompt-injection note.* Input data can carry instructions aimed at the volunteer or at their account’s memory or connectors. Templates wrap data in delimiters and tell the model to treat it as data; reviewers screen inputs for links and instruction-like text; volunteers are advised to use a clean chat with memory off where the service allows; outputs containing links, code to run or requests for action are flagged instead of shown as results. This reduces the risk; it does not remove it.

### 5.6 Provenance \[D\]

Each output stores: job and cell IDs; template and version; input and output hashes; declared purpose, license and sensitivity; policy profile and version; the service and model *as reported by the volunteer* (attested, not proven); the verification method and result; timestamps; and a salted-hash volunteer ID that requesters never see. Exports carry this as a manifest, including the license and a “no-training” flag where applicable. That flag is contractual, not technically enforced.

### 5.7 Failure modes of this approach

1. **False declarations.** Requesters can lie about sensitivity or purpose. Mitigation: reviewed templates, automatic screening for personal-data patterns, audits, bans, reputation. Residual risk remains and is disclosed.
2. **Policy as theatre.** There is no technical way to stop a requester training on outputs. Leverage is limited to terms of use, license tags and bans, so the interface says “declared”, never “guaranteed”.
3. **Open-license leakage.** P1 output is reusable by anyone, by design. The card and the job form must say so.
4. **Empty catalog.** Deny-by-default with unknown flags can leave no approved service or template. Mitigation: Phase 0 builds a small approved set; if none clears, see the fallbacks in §8.3.
5. **Combinatorial drift.** Too many profiles cannot be reviewed. Mitigation: two active profiles in Phase 1 (P0/P1 × S0/S1 × M0/M1).
6. **Banner blindness.** Volunteers stop reading cards. Mitigation: acknowledgement only for non-default categories; occasional comprehension checks \[H\].
7. **Forged provenance.** Self-reported service and model can be false, so they serve audit, not proof.
8. **Opt-out fragmentation.** Restrictive opt-ins starve some categories and stretch windows. Mitigation: a per-category supply gauge feeding the quote.
9. **Jurisdictional mismatch.** Law and terms differ by country; the matrix cannot encode all of it \[V\].
10. **Reviewer bottleneck or capture.** Founders review everything in Phase 1, which does not scale. Mitigation: published criteria, a second reviewer for new templates, later delegation.

## 6. Motivation and growth design

### 6.1 Incentives, ranked (the order is a hypothesis to be revised by data)

| Rank | Incentive | Whom it moves, and why it may work | Main tradeoff or risk | Phase |
| --- | --- | --- | --- | --- |
| 1 | Reciprocal credit (the core) | Requesters who expect a big job; the payoff is speed and scale | Delayed and abstract. The first completed request is the make-or-break moment, and slipping windows destroy trust | 1 |
| 2 | Mission and identity | Donors with no imminent job; a Persian-language community building open resources | Needs visible, concrete outcomes and can fade. Framing stays on knowledge access, not politics, because the context may be risky for members \[D\] | 1 |
| 3 | Collective progress (live counter, milestones) | Everyone; cheap to build | Vanity risk. The counter shows verified cells only | 1 |
| 4 | Recognition and reputation | Regulars; trust tiers raise caps and lower sampling | Pseudonymity limits status. No streak penalties (anxiety). Reputation comes from verified quality, not volume | 1 |
| 5 | Gamified competition (self-created teams; optional city or university groups) | Competitive and social members | Rewards volume unless scored on verified cells. Location or affiliation can expose members, so it is opt-in, never required or inferred, and Iran-based members are not shown by place by default \[D\] | 1 basic, 2 full |
| 6 | Money (deferred) | Possibly sponsors of Commons jobs, or requesters paying for guaranteed capacity: the only buyers identifiable so far | Money moves value but creates no capacity. It invites farming and fraud and may crowd out intrinsic motivation \[H\]. It raises regulatory questions \[V\]. Payment rails for people in Iran are an unresolved problem \[V\] | 2 at the earliest |

### 6.2 Viral mechanics (hypotheses, not predictions)

Each test needs its success and kill criteria written down before it starts.

| ID | Mechanic | Hypothesis | Metric | Tested in |
| --- | --- | --- | --- | --- |
| V1 | First contribution in under 60 seconds, no install, no signup | Raises landing-to-first-verified-cell conversion | Median time; conversion | 1 (instrumented), 2 (A/B) |
| V2 | Live counter of verified cells and members active today | Raises day-7 return | Return rate, counter shown vs. hidden | 2 |
| V3 | Shareable personal card (cells, badge; no personal data, no location) | Brings new first contributions | Share rate; referral-to-first-cell conversion | 2 |
| V4 | Team competition scored on verified cells | Raises week-2 return among those offered teams | Return rate; randomize the offer, because joiners self-select | 2 |
| V5 | Two-sided referral: both sides get a small bonus after the newcomer’s first verified cell | Raises activation without enabling farming | Referred activation rate; farming flags | 2 |
| V6 | Public milestones tied to real outputs (for example “the first 10,000 verified cells became an open dataset”) | Strengthens mission motivation and sharing | Return and share spikes around milestones | 1–2 |

With 30–50 members these cannot be tested statistically. Phase 1 only instruments them.

### 6.3 Phasing \[D\]

- **Phase 1: no money.** Mission, counter, basic teams, reciprocal credit.
- **Phase 2: small, capped, conditional rewards**, only when (a) the verification false-accept rate has been measured and is acceptable, (b) a sponsor exists, and (c) a reward form that works without banking for members in Iran is found or those members are explicitly excluded. Rewards attach only to verified cells.
- **Deferred: any order marketplace**, until the terms-of-service and legal items in §8 are resolved.

### 6.4 Contribution channels \[H\]

Channel 1 is running cells on a free-tier account. Channel 2 is human review of outputs, which needs no provider account and may suit Persian speakers inside Iran or anyone without access to a service; its accuracy and fraud profile are untested. Channel 3, later, is running open-weight models locally. Phase 1 uses channel 1, with channel 2 as an experimental arm.

## 7. Principles

Your eight principles, challenged one by one, become eleven. Each line shows what changed and why.

1. **The unit of account is a verified cell.** *Kept, sharpened.* The cell has a defined envelope, and credit is stated not to be money or property. Provider tokens vary and cannot be audited; verified cells can.
2. **No unbacked credit.** *Changed from “no large free credit”.* Every credit traces to an accepted Commons cell, and the starter grant is a Reserve transfer. The original wording forbade the bootstrap it also required.
3. **A human presses every Send.** *Changed, narrowed.* The project never holds volunteers’ credentials or sessions, never submits on their behalf and never reads their chat pages; it automates only its own side. “No automation” left open whether a prefilled link counts.
4. **Declared metadata, deny-by-default policy.** *Merged from old 4 and 8.* Purpose, license, sensitivity and service on every job; only allowlisted combinations run; Phases 1–2 accept S0 and S1 data only. Sensitivity is one of the four declarations, so two principles were saying one thing.
5. **Public rules, no secret changes.** *Kept, extended.* Formulas, parameters, expiry and the ledger are public; changes are prospective, announced and logged; credit is never created or altered outside the published rules.
6. **Declared license, no ownership claims.** *Changed from “clear owner”.* Every output has a declared license from the start; the project claims no ownership and does not promise that AI output is protectable; volunteers waive claims. “Clear owner” promises what the law may not support \[V\].
7. **Provider-neutral by design.** *Kept, narrowed.* An adapter layer and a registry; the pilot may use few services, but nothing is irreversible. This extends to hosting and payment choices.
8. **Pseudonymous by default; member safety outranks growth.** *New.* No mandatory traceable identity; collect the minimum; promise minimization, never anonymity; a growth tactic that endangers members loses. It was in your risks but not in your principles.
9. **No circumvention, no terms-breaking asks.** *New.* The project never asks or advises anyone to bypass regional or technical limits or to violate a service’s terms; a service enters use only after a recorded review. This protects members’ accounts and the project.
10. **Promise only measured capacity.** *New.* Requests are admitted against measured capacity with a quoted window; there is no promise of instant completion. This is the run-on-the-bank defense expressed as a principle.
11. **Claim only what can be shown.** *New.* No privacy guarantees we cannot prove, no “collective intelligence” claim, no invented statistics; metrics are published, including bad ones. Trust is the asset.

Net effect: three kept (sharpened), three changed, two merged into one, four added.

## 8. Risks, assumptions, and what is unverified

### 8.1 Status of claims

- **Premises from the brief, not independently checked \[P\]:** free allowances reset or expire; they cannot be transferred between accounts; many people have free access; individual need is spiky; some services are unavailable in Iran.
- **Follows from reasoning, not from data:** capacity cannot be stored, so only credit can be; steady supply with bursty demand creates run-on-the-bank risk; blanket redundancy makes an exchange rate unfair; the ledger identities in §4 hold by construction.
- **Hypotheses \[H\]:** idle capacity exists at useful scale; people will give a minute a day; parallel completion is valuable enough to motivate joining; a 60-second contribution is achievable; v is small; human review by Persian speakers is accurate enough; expiry is acceptable; the mechanics in §6.2 work; Commons jobs sustain motivation.
- **Must verify \[V\]:** everything in §8.3.
- **Precedent \[P\]:** time banks and mutual-credit systems exist; how such a system fares here is unknown.

### 8.2 Risk register

| # | Risk | Why it matters | Design response | Status |
| --- | --- | --- | --- | --- |
| 1 | Provider terms (personal accounts doing others’ work, a credit market, automation limits, output use) | Members’ accounts could be suspended; the project could be forced to close | Service Registry; no service in use before review; human-in-the-loop; ask providers for written permission | \[V\] |
| 2 | Regional restrictions and sanctions | Members in Iran may breach terms or face personal risk; the operator may face legal exposure | No circumvention; member roles; counsel; member-facing notice | \[V\] |
| 3 | Privacy: strangers read content inside personal accounts that may have memory or connectors | Exposure of requesters’ data and of volunteers’ accounts | S0/S1 only; template-only prompts; prompt visible; clean-chat advice | \[H\] |
| 4 | Prompt injection against volunteers | Malicious input steers a volunteer’s chat | Delimiters, input screening, flagged outputs, no action beyond copy and paste | \[H\] |
| 5 | Safety of Iranian participants | Participation may carry personal risk; metadata can identify people | Pseudonymity, data minimization, no place display, no mandatory identity, threat model before launch | \[V\] |
| 6 | Abuse: fake accounts, credit farming, junk outputs, malicious jobs | Credit integrity | Credit only from verified work; gold cells; sampling floor; small starter grant; rate limits; vouched invitations; bans | \[H\] |
| 7 | Verification cost and false accepts | Unfair rate or poisoned results | Automatic checks; adaptive sampling; v and false-accept rate measured | \[H\] |
| 8 | Run on the bank; credit inflation | Broken promises and loss of trust | Escrow; admission control (φ); mint cap; claim ratio | \[H\] |
| 9 | Result return and forgery | Forged results mean free credit | Server-issued cell IDs; lease-bound nonce; schema checks; gold cells; rate limits | \[D\] |
| 10 | Cold start on both sides | No jobs for donors, no donors for jobs | Commons backlog; founder seeding | \[H\] |
| 11 | Quality differences across services | Inconsistent outputs | Verifiable job types; service pinning; task-specific comparators | \[H\] |
| 12 | Legal character of credit, the name, the entity | Stored-value, money-transmission, consumer-protection and cooperative-law questions | Credit non-monetary, non-redeemable for cash, expiring; counsel | \[V\] |
| 13 | Reviewer bottleneck; founders as single point of failure | Growth stalls or quality drops | Published criteria; second reviewers; later delegation | \[H\] |
| 14 | Infrastructure reachability (can members in Iran reach the panel’s host?) | Members cannot join | Test reachability; keep adapters so hosting can move | \[V\] |
| 15 | Volunteer burnout | Falling retention | 60-second design; no streak penalties; skipping allowed | \[H\] |

### 8.3 Verification checklist before building

**G0. Terms and law (blocks everything).** For each candidate service, create a dated Service Registry entry with a saved copy of the terms, answering:

- (a) May a personal free account be used to do tasks for other people?
- (b) Is sharing, pooling, reselling or crediting access prohibited?
- (c) What do the terms say about automation, scraping, prefilled links and copy-and-paste workflows?
- (d) Regional availability: may people in Iran use the service, and what do the terms say about circumvention?
- (e) Is commercial use of outputs allowed on the free tier?
- (f) Is using outputs to train or develop other models allowed?
- (g) Is publishing outputs openly allowed?
- (h) Does the provider train on user chats by default, and could account memory or connectors leak content?
- (i) What do the usage policy and prohibited-content rules require?
- (j) What does “free allowance” formally mean, and can it change without notice?
- (k) Would the provider give written permission for this use?

Legal questions for counsel in the operator’s jurisdiction \[V\]: entity form; whether credit counts as regulated stored value or a virtual currency; consumer-protection and gambling-like-mechanics exposure; sanctions and export-control exposure for dealings with people or services in Iran; privacy law for pseudonymous data and IP logs; copyright of AI output and the wording of the contributor waiver; use of the name and of the words “cooperative” and “bank”.

**G1. Safety.** A written threat model for Iranian participants: what the platform stores, what a network observer can see, who could compel disclosure; decisions on logging and retention; a member-facing notice drafted with someone qualified to advise.

**G2. Technical feasibility.** On real phones and desktops: prefill and URL length limits per service; the clipboard flow; copy-and-paste error rate; the result return path; reachability of the panel from Iran; Persian right-to-left rendering.

**G3. Empirical calibration (founders’ own accounts, small sample).** Cells per day a free account can complete per service before limits bite; seconds per cell; refusal and failure rates; consistency across services on candidate templates.

**G4. Repo review.** Read the code and docs/ (§10); audit how the four secrets are handled.

**G5. Demand check.** Interview a handful of target requesters: what big jobs they really have, whether those jobs split into independent cells and are public or non-sensitive, and what completion window they would accept.

**Exit rule \[D\].** Building beyond a throwaway prototype starts only when G0 yields at least one approved service (or a documented fallback) and G1 is complete.

**Fallbacks if no service clears G0:** (i) seek written permission from a provider; (ii) restrict the commons to open-weight models run by members or on free hosted services, after their own terms check; (iii) a human-review-only commons; (iv) stop, and publish what was learned.

## 9. Phased roadmap with a measurable experiment for each phase

### Phase 0. Verify and prototype (no members)

**Deliverables:** Service Registry, 3–5 templates with automatic checks, threat model, calibration data. **Experiment:** founders and a few testers run cells on their own accounts. **Measures:** cells per day per service; seconds per cell; copy-and-paste error rate; automatic-check pass rate. **Exit:** G0 and G1 done; cell envelope defined.

### Phase 1. Closed pilot, no money

**Setup \[D\]:** 30–50 people for 30 days; Persian-speaking donors with a mix of requesters; the Phase 0 templates; one size class; a Commons backlog; a planned large-job event in weeks 3–4 plus any organic requests; the accelerated-expiry arm (§4.5) for part of the group; every participant informed of the account risks in G0 and opting in explicitly.

**Measures (thresholds pre-registered before day 1):**

- Deposit-to-withdrawal ratio: cells contributed ÷ cells requested, weekly.
- Time to complete a large job: submission to all cells accepted, compared with the quote.
- Rejection rate overall and by template; false-reject rate from gold cells; false-accept estimate from audits.
- Verification overhead v and the implied η.
- Week-2 return rate (share of week-1 contributors active in week 2), also week 4.
- Median time per contribution, share under 60 seconds, and time to first verified cell for newcomers.
- Active capacity per member per day, and concentration (share of cells from the top 10% of donors).
- Decline and opt-out rates by category.
- Incidents: policy violations, injection attempts, abuse flags, any provider warning or account problem, each reported.
- Qualitative: 8–10 interviews, including reasons for stopping.

**Decision rules (starting proposals; arbitrary until you set them):** proceed to Phase 2 only if (a) at least two of three trial large jobs finish within their quotes, (b) η meets the threshold you set, (c) there is no unresolved safety or provider-account incident, and (d) week-2 return meets the bar you set. If (a) fails, diagnose capacity, verification and friction separately before changing anything else.

### Phase 2. Open beta

**Scope:** public, pseudonymous, Persian-first; teams, share cards, referral, public counter, the human-review channel; a sponsor for Commons jobs; small conditional rewards only if the conditions in §6.3 hold. **Experiments:** V2–V5 as randomized tests; human-review accuracy against gold cells; effect of reservations on burstiness; and, parked and independent of the core, whether combining several answers beats one. **Measures:** activation rate, referral conversion, day-7 / week-2 / week-8 retention, claim ratio, queue-time distribution, cost per verified cell. **Exit:** a stable claim ratio below its threshold for a period you set, and a sustainable Commons sponsor or equivalent.

### Phase 3. Marketplace and money

Not scheduled. Entry requires answers to the payment and legal questions in G0 and an explicit decision memo.

## 10. Technical implications for the existing panel repo

**Caveat \[V\]:** this section rests on the README only. The code and docs/ have not been reviewed.

**What the README describes:** a Cloudflare Worker serving a web panel; cells in a left-to-right dependency graph colored by status with the bottleneck highlighted; teammates start cells; the owner can Release or Hand over a stuck cell; a small offline Windows launcher registers a blueprint:// protocol and opens a chosen browser profile at claude.ai/new?q=\<prompt>, and the human presses Send; four secrets (PANEL\_TOKEN, ADMIN\_TOKEN, GITHUB\_TOKEN, MCP\_AUTH\_TOKEN); automatic release at the usage limit and automatic chat-link capture removed; result return unclear.

**What carries over:** the cell and lease concept, the status graph (it can become a public capacity map), the bottleneck view, the human-presses-Send model, and Release / Hand over as operator tools.

**Gaps for a public commons:** shared single-password auth; no per-user identity; no redundancy or voting; no server-side lease timeouts; a Windows-only, single-provider launcher; an unclear result return path; no user-facing project description.

**What to add, in order:**

1. **Review the repo** (code, docs/, secrets handling, how results currently return) and decide keep versus rewrite. It was built for a team; the commons needs a public threat model. Rotate existing secrets before any public exposure.
2. **Per-member pseudonymous identity.** Replace the shared token with per-member keys (store hashes, rate-limit); keep admin access separate.
3. **Cell data model with server-side leases:** queued → leased (expiry) → submitted → accepted or rejected; automatic return to queue on timeout; idempotent submissions.
4. **Result return path with anti-forgery:** a paste-back form bound to the cell ID and a lease nonce; server-side schema validation and size limits; never execute submitted content; escape everything on display.
5. **Append-only ledger:** accounts for members, escrow and the Reserve; double entry; invariants checked automatically; public counters read from it.
6. **Policy engine and template registry:** metadata fields, rules R1–R10 as data rather than code, policy versioning, the Service Registry.
7. **Verification pipeline:** per-template validators, gold-cell injection, audit scheduling, adaptive sampling with a floor.
8. **Volunteer interface:** no-install, mobile-first web flow showing the card, copy and open buttons through service adapters, and paste-back; Persian right-to-left; dates shown in Jalali and Gregorian. The launcher becomes optional (extend beyond Windows or retire).
9. **Admission control and quoting:** capacity estimator, φ, waitlist, reservations.
10. **Public surfaces:** live counter, public ledger and parameter page, change log, provenance export.
11. **Later:** teams, share cards, referral, the human-review channel.

**Two cautions \[V\]:** the Worker’s host may not be reachable from Iran or acceptable to members, so keep storage and hosting behind an interface; and prefilled-link support differs by provider, so other services may need copy-only flows.

## 11. Glossary

- **Cell.** One prompt-and-response unit that fits a single Send inside the cell envelope; the unit of credit.
- **Credit.** A non-monetary, expiring claim on future cells of work, minted only for accepted Commons cells.
- **Commons job.** A public-benefit job with openly licensed output, run from the standing backlog; the only place credit is minted.
- **Commons Reserve.** The public account funded by the levy and by expired credit, paying starter grants.
- **Mint / transfer / retire.** Create credit for an accepted Commons cell / move credit between accounts / remove surplus Reserve credit from existence.
- **Escrow.** Credit held from submission until the job settles or is cancelled.
- **Donor, Requester, Reviewer, Operator.** The four roles in §3.1.
- **Gold cell.** A hidden known-answer cell used to estimate a donor’s reliability.
- **Audit cell.** A sampled re-execution by a second donor.
- **v (verification overhead).** (Audit + gold + rework cells) ÷ accepted primary cells.
- **λ (levy).** The published fraction of the price paid into the Reserve.
- **η (round-trip efficiency).** 1/(1+v+λ): cells a member can request per cell contributed.
- **φ.** The share of forecast active capacity open to member jobs.
- **Claim ratio.** Unexpired credit ÷ verified weekly throughput.
- **Admission control.** Accepting a job only if its committed cells fit within φ × forecast capacity over its window.
- **Template.** A reviewed prompt pattern with data slots and an automatic check.
- **Policy engine / profile.** The rule evaluator (R1–R10) and the allowed combination of purpose, sensitivity, license and service.
- **Service Registry.** The dated record of each service’s terms flags; unknown counts as no.
- **Provenance manifest.** The record of job, template, policy, service, verification and hashes attached to every output.
- **Downstream use uncontrolled.** The tag on openly licensed output, meaning anyone may reuse it.
- **Starter grant.** A small Reserve transfer to a newcomer after a first verified contribution.
- **Recovery key.** The secret that restores a pseudonymous identity without e-mail.

## Persian summary / خلاصهٔ فارسی

«همیار» یک «مشترک ظرفیت» (capacity commons) است: افراد روزانه حدود یک دقیقه از سهمیهٔ رایگان هوش مصنوعی خود را، که در غیر این صورت هدر می‌رود، صرف کارهای بازبینی‌شده و غیرحساس می‌کنند و برای هر نتیجهٔ تأییدشده «اعتبار» با تاریخ انقضا می‌گیرند.

بعدها، وقتی عضوی کار بزرگ و قابل‌تقسیمی دارد، با همین اعتبار از اعضای دیگر می‌خواهد آن را موازی و در بازهٔ زمانی اعلام‌شده انجام دهند. آنچه بازمی‌گردد توکن نیست؛ سرعت و مقیاس است.

واحد حساب «سلول کار تأییدشده» است، نه توکن. اعتبار فقط با انجام کارهای عمومی مشترک (Commons) ساخته می‌شود و در کارهای اعضا فقط جابه‌جا می‌شود. قیمت برابر است با ۱ + سربار راستی‌آزمایی + عوارض ذخیره، و هر سه عدد منتشر می‌شوند.

هر کار باید هدف، مجوز خروجی، حساسیت داده و سرویس مجاز را اعلام کند. سیاست پیش‌فرض «رد کن، مگر آنکه صریحاً مجاز باشد» است و فقط داده‌های عمومی یا غیرحساس پذیرفته می‌شود. هر خروجی شجرهٔ (provenance) مشخص دارد.

دکمهٔ ارسال را همیشه خودِ انسان می‌زند و هیچ حسابی خودکار اداره نمی‌شود. مشارکت با نام مستعار ممکن است و ایمنی اعضا، به‌ویژه در ایران، بر رشد اولویت دارد. پروژه هیچ‌کس را به دور زدن محدودیت‌ها یا نقض شرایط سرویس‌ها تشویق نمی‌کند.

انگیزه‌ها به ترتیب: اعتبار متقابل، مأموریت و هویت، شمارندهٔ جمعی، شهرت، رقابت تیمی؛ پول فعلاً به تعویق افتاده است. این ترتیب یک فرضیه است، نه یافته.

پیش از ساخت باید راستی‌آزمایی شود: شرایط استفادهٔ هر سرویس، مسائل حقوقی و تحریم، ایمنی مشارکت‌کنندگان، امکان‌پذیری فنی و میزان واقعی ظرفیت بلااستفاده. تا آن زمان هیچ‌یک از این‌ها قطعی تلقی نمی‌شود.

نقشهٔ راه: فاز ۰ راستی‌آزمایی و نمونهٔ اولیه؛ فاز ۱ آزمایش بستهٔ ۳۰ تا ۵۰ نفره به مدت یک ماه و بدون پول؛ فاز ۲ بتای عمومی؛ بازارچه و پول فقط پس از روشن‌شدن مسائل حقوقی.

برای پنل موجود (Blueprint Panel) لازم است: هویت جداگانهٔ هر عضو، مهلت (lease) سمت سرور، مسیر امن بازگشت نتیجه همراه با ضدجعل، و دفتر کل (ledger) فقط‌افزودنی. این ارزیابی فقط بر پایهٔ README است و کد هنوز بازبینی نشده است.

این سند مشورت حقوقی نیست؛ هر ادعای مربوط به قانون یا شرایط سرویس‌ها باید جداگانه راستی‌آزمایی شود.
