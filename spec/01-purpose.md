# 1. Purpose, scope, and how to read this spec

*Spec part 1 · owner cell C-028 (supersedes C-001) · names, IDs and enums come from S0 and are used exactly · written against Founding Document draft v0.1 of 11 November 2026 (FD). Nothing here is legal advice, and nothing here has been verified against any provider's terms or any law.*

## 1.1 Purpose

- This document specifies the complete Hamyar system: every component, rule, screen, parameter, interface and test needed to build it, and the order in which to build it. An engineer or a coding agent should be able to implement it without asking a question. [D]
- “Complete” is a test, not a length: a part is complete when an implementer can write code and tests for it from its text alone. What the text cannot answer is listed in S3.2 as an owner decision, each with a default the spec uses meanwhile. [D]
- The owner intends to build the full system before running any experiment. Phase 1 (30 to 50 members, one size class, a Commons backlog, an accelerated-expiry arm; FD§9) is therefore a configuration of the finished system, never a reduced product. No part may defer a component because the pilot is small. [D][P]
- The spec decides how to build and how to gate a launch. It does not decide that Hamyar should launch; that is the sign-off of the launch gates in S14.*. [D]

## 1.2 What this document is and is not

| It is | It is not |
| --- | --- |
| The implementable description of the system in the FD, with every TBD parameter named, validated and versioned (S16.*) | A restatement of the vision; that is the FD |
| A list of problems found in the FD, each with a resolution applied consistently (S2.*) | A silent rewrite: every deviation from the FD cites an `ISS-nn` |
| A build order in which every milestone ends in a working, testable system (S17.*) | A plan that waits for pilot results before building |
| A specification of the gates that keep unverified provider, legal and safety questions away from members (S14.*) | A legal opinion, a terms review or a safety assessment; those are human work recorded inside the system [V] |
| A specification of a simulation harness (S18.*) | Evidence about real human behavior; simulation output is never evidence (S0.2, rule 3) |

## 1.3 Scope: brief letters mapped to parts

The brief lists scope letters A to K and a 21-part structure. This table fixes where each letter is specified. [D]

| Brief scope | Content | Specified in |
| --- | --- | --- |
| A | Identity, access, roles, sessions, rate limits, logging | S10.*; screens in S11.* |
| B | Entities, state machines, idempotency, concurrency | S5.*; names in S0.7 to S0.9 |
| C | Credit, ledger, pricing, admission control | S6.* |
| D | Policy rules R1 to R10 as data, Service Registry, opt-ins, injection defenses | S7.*, S9.* |
| E | Templates, verification, result return, anti-forgery | S8.*, S9.* |
| F | Volunteer, Requester, Reviewer and Operator experiences, Persian first | S11.* |
| G | Public surfaces, growth mechanics V1 to V6 | S12.* |
| H | Measurement, pre-registration, calibration, analytics privacy | S13.* |
| I | Threat model, member safety, secrets, hosting, abuse process | S10.*, S4.* |
| J | Architecture, API, background jobs, build order | S4.*, S15.*, S16.*, S17.* |
| K | Test strategy, simulation, acceptance criteria | S18.*, with `AC-*` ids inside each part |
| (brief preamble) | Launch gates G0 to G5, kill switches, the build-versus-launch separation | S14.* |

## 1.4 Excluded by decision

The following are not specified, on purpose. Each is excluded for a stated reason, and a part that seems to need one MUST say so and stop, not work around it. [D]

| Excluded | Reason | Source |
| --- | --- | --- |
| Anything that automates a volunteer's account, reads or scrapes a volunteer's chat page, stores a volunteer's provider credentials or session, submits on a volunteer's behalf, or helps anyone bypass regional or technical restrictions | A human presses Send, always; the platform automates only its own side | brief ground rule 3; FD Principles 3 and 9 |
| Platform-side execution of submitted content, including running a submitted code change | FD§10 says never execute submitted content; the owner may overturn this (see `ISS-12`, S3.2) | FD§10 |
| Money, rewards and any order marketplace | FD§0.2: no money moves in Phase 1; FD§6.3 and FD§9 Phase 3 make them conditional on legal and payment answers, not on pilot size | FD§6.3 |
| Differential pricing by service class, size or deadline | FD§4.3: waits for data (`ISS-34`) | FD§4.3 |
| A claim that many answers beat one (“collective intelligence”) | Excluded from the foundation; one optional experiment is parked in Phase 2 | FD§0.1 item 15 |
| Provider names, terms, regional availability, prices, limits, URL parameters and legal rules stated as facts | They are configuration data entered by a human reviewer and marked [V] | brief ground rule 2 |

## 1.5 Building versus launching

The brief overrides the FD's building rule: everything is built, and launching is gated. [D]

| Switch (S0.10.6, table C) | Default | What it holds back |
| --- | --- | --- |
| `launch.members_may_join` | `false` | Every path that creates a new `Member` |
| `launch.member_jobs_enabled` | `false` | Creation of member `Job`s |
| `launch.minting_enabled` | `false` | Every `mint` ledger entry |

1. A service is `unreviewed` when created and counts as `no` for every flag until a reviewer records the flags with a saved `TermsCopy` (S7.*). A `Job` cannot be created for a service that is not `approved`. [D]
2. Only the sign-off flow built in `BM2` can turn a launch switch on, and only when the rule in S14.* holds. No milestone changes these defaults (S0.12, ordering rule 3). [D]
3. Finishing a milestone never authorizes a launch (S0.12, ordering rule 6). [D]
4. The FD's exit rule (FD§8.3) is applied to launching, not to building; see `ISS-31` and `ISS-11` for the strengthened condition. [D]

## 1.6 Ground rules binding on every part

| # | Rule | Enforced by |
| --- | --- | --- |
| 1 | The FD is the source of truth. A deviation, gap or unimplementable rule is recorded as `ISS-nn` with a resolution applied consistently; nothing is contradicted silently | S2.*, the `## Issues raised` table of each part (S0.4) |
| 2 | No provider term, regional availability, price, limit, URL parameter or legal rule is hardcoded. Each is configuration data tagged [V], with the place where the human's answer is stored | S7.*, S14.*, S19.* |
| 3 | Nothing automates, reads or impersonates a volunteer's account or helps bypass a restriction (1.4) | S9.*, S10.*, S11.* |
| 4 | Evidence tags on every claim that needs one (1.9); every number is derived by a shown formula or labeled `initial configurable default` | S0.2 |
| 5 | TBD parameters (cell envelope, K, λ, g, s, φ, G, mint cap, lease timeout) are named, validated, versioned configuration with a safe initial default and the measurement that replaces it | S0.10, S16.* |
| 6 | Build order always leaves a working, testable system; launch-gate machinery and ledger invariants come early | S0.12, S17.* |
| 7 | No deferral because the pilot is small; Phase 1 is a configuration of the full system | 1.1 |

## 1.7 How the spec is organized

Top-level headings are `# <n>. <title>` and sub-headings `## <n>.<m> <title>`, so assembly orders parts by number. A part may be split over several files; file names are not normative (S0.13). [D]

| Part | Title | What an implementer takes from it |
| --- | --- | --- |
| S0 | Conventions | Names, ID formats, enums, state and event names, parameter names, API conventions, milestone ids |
| S1 | This part | Purpose, scope, reading rules, tag legend |
| S2 | Issues found in the FD | Every deviation from the FD and why |
| S3 | Assumptions and open decisions | What the spec assumed, what only the owner can decide, and the default used meanwhile |
| S4 | System overview and architecture | Components, interfaces, stack-agnostic design, recommended stack, jobs, observability |
| S5 | Domain model and state machines | Entities, fields, constraints, guards, side effects, idempotency |
| S6 | Credit, ledger, pricing and admission control | Ledger, invariants, mint, escrow, expiry, price, algorithms, worked example |
| S7 | Policy engine and Service Registry | Rules as data, allowlist, registry workflow, opt-ins |
| S8 | Templates and verification | Template format, first templates, gold, audit, reliability estimation |
| S9 | Result return and abuse defenses | Leases, nonces, forgery checks, quarantine, injection defenses |
| S10 | Identity, privacy and safety | Keys, recovery, roles, retention, threat model, secrets, what the platform cannot promise |
| S11 | Experiences | Screen by screen, Persian first, copy keys in `fa` and `en` |
| S12 | Public surfaces and growth | Counter, public ledger, teams, referral, experiments V1 to V6 |
| S13 | Measurement | Event schema, every FD§9 Phase 1 measure, pre-registration, calibration tool |
| S14 | Launch gates | G0 to G5 as product features, sign-off rule, kill switches |
| S15 | API | Operations, schemas, errors, idempotency |
| S16 | Parameters | Every parameter with type, validation, default, owner, calibration |
| S17 | Build plan | Milestones `BM0` to `BM9`, dependencies, acceptance, Definition of Done |
| S18 | Tests and simulation | Strategy by layer, harness, adversarial cases |
| S19 | Risks and checklist | What remains unverified, pre-build checklist |
| S20 | Glossary | Terms |
| S21 | Persian summary | About ten lines |

## 1.8 Reader paths

| Reader | Read first | Then |
| --- | --- | --- |
| Engineer or coding agent starting the build | S0, S17 | The part of the current milestone, its `AC-*` and `T-*` ids, S16 for parameters |
| Owner | S3.2, S2 (blocking and major issues) | S14, S19 |
| Reviewer (templates, services, policy) | S7, S8 | S11 (Reviewer tools), S14 |
| Counsel or safety adviser | S3.2, S10, S14 | Every [V] item, which S19 collects |
| Persian-language reviewer | S11 copy keys | S21 |

## 1.9 Evidence-tag legend

The legend reuses S0.2, which stays authoritative if the two ever differ. [D]

| Tag | Meaning | Required companion | Example |
| --- | --- | --- | --- |
| `[D]` | A decision this spec makes; binding on implementers | A reason or an FD§ reference | “Ledger amounts are integer micro-credits [D]” |
| `[H]` | A hypothesis that may be false | The measurement that tests it and its success or kill criterion | “A contribution takes under 60 s [H]” |
| `[V]` | Must be verified by a human before anyone relies on it | What is verified, by whom, and where the answer is stored | “Reachability of the host from Iran [V]” |
| `[P]` | A premise taken from the brief or the FD, not independently checked | The FD§ it comes from | “Free allowances cannot be transferred [P]” |
| `[A]` | An assumption introduced by this spec, absent from the FD | The owner decision that could overturn it, collected in S3.* | “Admin host is a separate origin [A]” |

Writing rules for every part: [D]

1. One tag per bracket; combine by adjacency (`[H][V]`); place the tag directly after the claim it qualifies.
2. A number is derived by a formula shown beside it, or labeled exactly `initial configurable default` and present in the parameter table (S0.10.6, S16.*).
3. No statistic is invented; simulation output is never evidence about people.
4. User-facing promises say “declared”, never “guaranteed” (FD Principle 11); legal conclusions are never drawn and are [V] for counsel.
5. An unverified claim is never written as a fact; it carries a tag or is removed.

## 1.10 Precedence and deviation rule

When sources disagree, the first applicable row wins. [D]

| Order | Source | Governs |
| --- | --- | --- |
| 1 | Brief ground rules (1.6) | Safety, no-automation, no invented provider facts, tags, parameters |
| 2 | S0 | Names, IDs, enums, state and event names, parameter names, API shapes |
| 3 | FD | Intent, definitions, formulas, the worked example in FD§3.3 |
| 4 | Later parts | Detail inside the frame above |

A part that departs from the FD MUST cite the `ISS-nn` that records and justifies the departure. A part MUST NOT depart from S0; a missing or wrong name is reported as a convention gap (S0.1, S2.9). [D]

## 1.11 Reading conventions

- MUST, MUST NOT, SHOULD and MAY carry their RFC 2119 meaning; identifiers in `code font` are normative (S0.1).
- Cross-references: `FD§N`, `S<n>.<m>`, `ISS-nn`, `R1` to `R10`, `G0` to `G5`, `BM0` to `BM9` (S0.3). A reference to a section that does not exist yet is still written in this form; assembly checks that every reference resolves.
- Persian text appears only where a part says so, is right-to-left safe, and carries the marker `needs_human_and_legal_review` (S0.5).
- Build-cell ids (`C-nnn`) appear only in provenance lines and `## Issues raised` tables, never in normative text.

## Issues raised

none. The one finding made while writing this part, `ISS-37` (the instruction's issue numbering collides with S0.4), has its id in the block of S3 and is raised there; its detail is in S2.6.
