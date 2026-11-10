You are a senior product architect and staff engineer. Attached is the "Hamyar — Founding Document" (draft v0.1). Your job is to write the PRODUCT SPECIFICATION for Hamyar: a document precise enough that an engineer, or a coding agent, can implement the complete system from it without asking further questions.

Context about me: I build quickly and cheaply, and I intend to implement the FULL system before running any experiment. So do NOT simplify the design for a pilot, do NOT defer components to "later" because the pilot is small, and do NOT shrink the scope. Specify the complete system, with every parameter configurable. Phase 1 is only a configuration of the full system (small member count, one size class, Commons backlog, accelerated-expiry arm), not a reduced product.

One constraint overrides my "build everything" preference, and you must design it in: the Founding Document's gates G0 (provider terms and law) and G1 (safety threat model) are unresolved. Therefore the spec must separate BUILDING from LAUNCHING. Build everything, but engineer hard launch gates: the Service Registry ships with every service in state "unreviewed", unreviewed counts as "no", a job cannot be created for a service unless a reviewer has recorded the registry flags with a saved copy of the terms, and a global "members may join" switch stays off until the gate checklist is signed off in the admin tool. Treat this as a product feature with its own screens, data model and tests.

## Ground rules

1. The Founding Document is the source of truth. Do not contradict it silently. If you find an inconsistency, a gap, or a rule that cannot be implemented as written, list it in a section called "Issues found in the Founding Document" with a proposed resolution, and apply that resolution consistently. Do not just agree with it; challenge it where warranted.
2. Do not invent facts about any provider's terms, regional availability, pricing, limits, URL parameters, or legal rules. Everything of that kind is configuration data to be recorded by a human reviewer, never hardcoded. Where the spec depends on such a fact, mark it [V] and say what must be verified and where the answer is stored.
3. Never specify anything that automates a volunteer's account, reads or scrapes a volunteer's chat page, stores a volunteer's provider credentials or session, submits on a volunteer's behalf, or helps anyone bypass regional or technical restrictions. The human presses Send, always. The platform automates only its own side. If a feature would require otherwise, say so and exclude it.
4. Keep the evidence tags from the Founding Document ([D] decision, [H] hypothesis, [V] verify, [P] premise) and add [A] for an assumption you introduce. Every number you introduce is either derived by a shown formula or labeled as an initial configurable default.
5. Where the Founding Document leaves a parameter TBD (cell envelope, K, λ, g, s, φ, G, mint cap, lease timeout), specify it as a named, validated, versioned configuration parameter, with a safe initial default and the measurement that will replace it. Never hardcode.
6. Write it so that the system can be built in an order that always leaves a working, testable system.

## Product scope: specify ALL of the following

A. Identity and access
- Anonymous identity created locally with no signup and no e-mail; recovery key design; optional e-mail; key rotation; device linking; account recovery and its abuse risks; per-device, per-invite-tree and per-day rate limits; vouched invitations and invite trees; roles (Donor, Requester, Reviewer, Operator) and permission matrix; admin authentication that is separate from member authentication and uses no shared password; session handling; what is and is not logged (data minimization, retention, IP handling) consistent with the safety principle for members in Iran.

B. Core domain model and state machines
- Entities with fields, types, constraints, indexes and retention: Member, Device, Invite, Template (with versions), Job, Cell, Lease, Submission, Verification record, GoldCell, Audit, LedgerAccount, LedgerEntry, Escrow, Reserve, Policy (with versions), ServiceRegistryEntry (with saved terms copies and dated flag answers), Report, Appeal, Reservation (capacity booking), Team, Badge, ChangeLogEntry, LaunchGateItem.
- Explicit state machines with transitions, guards and side effects for: Job, Cell (queued → leased → submitted → accepted / rejected / flagged-for-audit, plus expiry and requeue), Member trust tiers, Template review, Service review, Appeal.
- Idempotency, concurrency and race handling for leasing, submission and settlement. State the exact guarantees.

C. Credit and ledger
- Append-only double-entry ledger; the invariants from section 4.2 of the Founding Document expressed as automated checks that run continuously and alarm on violation.
- Minting (Commons cells only, with a monthly issuance cap), transfer (member jobs), escrow, settlement, refunds on cancel, levy λ into the Reserve, expiry (oldest-first spending, per-balance expiry dates, expired credit to the Reserve), retirement of Reserve excess above its ceiling, per-member cap K, starter grant G with its conditions and anti-farming limits.
- Price formula p = 1 + v + λ, how v is measured over a trailing window per job type, how η and the claim ratio are computed, published, and versioned; prospective-only parameter changes with notice and a public change log.
- Admission control: capacity forecasting from recent verified throughput and active donors, φ, quoting a completion window, waitlist, capacity reservations for future dates, fairness rules, cancellation. Give the algorithms in pseudocode and a worked numeric example, and make the Founding Document's worked example in section 3.3 pass as an automated test.

D. Policy and purpose layer
- Rules R1–R10 implemented as DATA (a rules table plus a small evaluator), not scattered code; policy versioning; stamping at admission and re-check at acceptance; tighten-immediately versus loosen-with-changelog workflow.
- Full metadata schema for jobs (purpose P0–P3, license L0–L3, sensitivity S0–S3, service requirement M0–M2), with validation, the allowlist of permitted combinations, the rejection reasons shown to requesters, and the volunteer opt-in model (defaults and per-category opt-ins, topic categories).
- Service Registry workflow: how a reviewer records terms flags (yes / no / unknown), saves the dated copy of the terms, approves or revokes a service, and what happens to in-flight cells when a service is revoked.
- Prompt-injection and abuse defenses specified as concrete mechanisms: template wrapping with delimiters, input screening rules, link and instruction-pattern detection, output flagging, the rule that a task may only ask the volunteer to copy, press Send and return text.

E. Templates and verification
- Template format (data slots, prompt body, delimiters, output schema, automatic checks, comparator for audits, cell envelope, review status), template review workflow with second-reviewer rule for new templates, and versioning.
- Specify the first set of templates concretely (at least: translation with a shared glossary, classification/extraction into a fixed schema, summarization into a schema, code change with supplied tests, format conversion with a validator), each with prompt skeleton, input and output schema, and automatic checks. Do not claim any of them works; mark effectiveness [H].
- Verification pipeline: automatic checks, hidden gold cells (insertion rate g, donor reliability estimate), sampled audits (rate s, comparator, third execution on mismatch), adaptive sampling with a floor, blanket redundancy for new donors and high-risk templates, human review cells with their own gold cells, appeals. Give the estimation method for donor reliability and for false-accept and false-reject rates, with its limits stated.
- Result return and anti-forgery: server-issued cell IDs, lease-bound nonces, expiry, size limits, schema validation, escaping everything on display, never executing submitted content, rate limits, duplicate-submission handling, detection of copy-paste of another donor's output, timing anomalies.

F. Volunteer experience (no install, mobile-first)
- Screen-by-screen specification with states and copy intent: landing, first contribution flow (the sub-60-second path), the cell card (purpose, license, sensitivity, service, template, expected time, one-sentence provenance line, expandable full prompt, mandatory expansion rules, decline and report buttons), copy and open-in-service buttons through a service-adapter layer (prefill where a registry entry says it is supported, copy-only otherwise), paste-back, result feedback, balance and expiry view, history, opt-in settings, teams, share card, invite flow, recovery key handling, appeal, help.
- Requester screens: job creation wizard (template choice, data upload and screening, metadata declarations, policy result, price and window quote, escrow confirmation), job progress with a per-cell status map, cancellation, results download with provenance manifest, rating of the outcome.
- Reviewer and Operator tools: template review queue, service review, audit queue, appeals, abuse flags, ledger explorer, parameter editor with versioning and changelog, capacity dashboard, launch-gate checklist, kill switches (pause a template, a service, a member, all minting, all new jobs).
- Persian first: full RTL, Persian numerals option, Jalali and Gregorian dates, mixed-direction text handling inside prompts and outputs, fonts, plus English. Accessibility and low-bandwidth behavior. All user-facing copy that makes a promise must say "declared", never "guaranteed", per Principle 11. Provide the copy for all policy, privacy and risk notices in both Persian and English, marked as needing human and legal review.

G. Public surfaces and growth
- Live counter (verified cells only), public ledger and parameter page, change log, milestone pages, share cards without personal data or location, teams with opt-in only, referral with two-sided bonus after a verified first cell and its anti-farming rules. Implement the growth mechanics V1–V6 as feature-flagged, instrumented, randomizable experiments with an assignment mechanism that is logged.

H. Measurement and experiment support
- An event schema and metrics pipeline that produces every Phase 1 measure listed in section 9 of the Founding Document (deposit-to-withdrawal ratio, time to complete a large job versus quote, rejection and false-reject and false-accept rates, v and η, week-2 and week-4 return, time to first verified cell, share of contributions under 60 seconds, capacity concentration, decline and opt-out rates, incidents).
- Pre-registration support: a place to record thresholds and decision rules BEFORE launch and lock them.
- The accelerated-expiry arm and any other arm as configuration, with random assignment.
- A calibration tool for Phase 0: record cells per day per service, seconds per cell, refusal and failure rates, copy-paste error rate.
- Privacy of analytics: aggregate by default, no third-party trackers, minimal retention.

I. Security, privacy and safety
- A threat model table (actor, goal, attack, impact, mitigation, residual risk) covering at least: forged results, credit farming, fake accounts and invite-tree abuse, malicious requesters and malicious inputs, prompt injection against volunteers, XSS and injection through submitted text, ledger tampering, insider and operator risk, account takeover, de-anonymization of members, compelled disclosure, DoS, and reviewer capture.
- Specific design for member safety in a high-risk context: pseudonymity, minimal collection, retention limits, what a network observer or the host can see, what happens on a subpoena or seizure, no location display by default, no mandatory identity. State plainly what the platform can NOT promise.
- Secrets management for the four existing secrets plus new ones, rotation, and the requirement to rotate before any public exposure.
- Hosting and reachability: keep storage and hosting behind interfaces so the system can move; note that reachability from Iran is [V]; design for low-bandwidth and for blocked third-party resources (no mandatory third-party CDN or font dependency).
- Abuse reporting, takedown and ban process, including appeals.

J. Architecture and implementation plan
- Treat the existing repo (github.com/abbashaji/panel, a Cloudflare Worker based "Blueprint Panel") as unreviewed [V]: its code and docs/ were not read. Specify the target architecture in a stack-agnostic way first, then give a recommended concrete stack with reasons and a short list of alternatives, and state what to keep, wrap, or replace from the existing panel concept (cells, leases, status graph, bottleneck view, Release / Hand over) once the repo is reviewed. Do not assume undocumented behavior of the repo.
- Components and their interfaces, API specification (endpoints, request and response schemas, auth, error model, idempotency keys, pagination, rate limits), event model, background jobs (lease expiry, escrow settlement, credit expiry, audits, metric rollups, ledger invariant checks), storage choices and consistency requirements for the ledger, configuration management, feature flags, migrations, observability (logs without personal data, metrics, alerts), backup and recovery, and deployment and environments.
- A service-adapter interface so that no provider is hardcoded: adapter capabilities (supports prefill, URL length limit, copy-only), configured from the Service Registry.
- A build order in milestones where each milestone ends with a working, testable system and explicit acceptance tests. The launch-gate machinery and the ledger invariants come early, not last.

K. Testing and acceptance
- Test strategy by layer: unit, property-based tests for the ledger and for admission control, state-machine tests, policy-engine tests with a table of allowed and rejected combinations, adversarial tests (forgery, replay, double submission, race conditions on leasing and settlement), injection and XSS tests, RTL and Persian rendering tests, load tests, end-to-end simulation.
- A simulation harness that generates synthetic donors and requesters (including adversarial ones) to exercise the credit model, run-on-the-bank scenarios and credit expiry, so parameters can be explored before real users exist. Specify it, and state clearly that simulation output is not evidence about real human behavior.
- Acceptance criteria that are testable (Given / When / Then) for every major feature, plus the Definition of Done for each milestone.

## Required structure of the deliverable

1. Purpose, scope, and how to read this spec (with the evidence-tag legend)
2. Issues found in the Founding Document, and resolutions
3. Assumptions introduced [A] and open decisions that only I can make (for example operator jurisdiction, who reviews templates, hosting choice)
4. System overview and architecture
5. Domain model and state machines
6. Credit, ledger, pricing and admission control
7. Policy engine and Service Registry
8. Templates and verification pipeline
9. Result return, anti-forgery and abuse defenses
10. Identity, access, privacy and safety design (with the threat model table)
11. Volunteer, Requester, Reviewer and Operator experiences (screen by screen, Persian first)
12. Public surfaces and growth experiments
13. Measurement, experiment support and pre-registration
14. Launch gates (G0–G5 as product features, the exit rule, kill switches)
15. API specification
16. Configuration parameter table (every parameter, type, validation, initial default, owner, how it will be calibrated)
17. Build plan: milestones, dependencies, acceptance tests
18. Test strategy and simulation harness
19. Risks, what remains unverified, and a pre-build checklist
20. Glossary
21. A short Persian summary (about 10 lines)

## Style requirements

- Be precise, not padded. Prefer tables, schemas, pseudocode, state diagrams in text form, and Given/When/Then criteria over prose. Every section must contain decisions, not generalities.
- This will be long. If you cannot fit it in one response, deliver it in clearly numbered parts, announce the plan for the parts at the start, and continue until every section above is complete. Do not stop early and do not summarize away sections.
- Before writing, give me a short list (at most 10 lines) of the biggest decisions you made and anything you want to challenge in my instructions, and then proceed. Ask at most 3 clarifying questions, and only if you truly cannot proceed; otherwise state assumptions and continue.
- Never present an unverified claim as fact. No invented statistics. No invented provider behavior. No legal conclusions: flag them [V] for counsel.
- Output the final spec as a single well-structured document I can save as "Hamyar — Product Specification.md".