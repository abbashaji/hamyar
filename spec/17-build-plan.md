# 17. Build plan: milestones, dependencies, acceptance tests

*Spec part 17 · owner cell C-023 · written against `spec/00-conventions.md` (S0) and Founding Document draft v0.1 (FD). Milestones are `BM0`..`BM9` (S0.12, `ISS-01`), never `M0..Mn`, because `M0`..`M2` already mean service requirements. Nothing here was checked against any provider's terms, any law, or the code of the existing panel repository; every such dependence is tagged [V].*

## 17.1 Purpose, scope and how to read

- This part turns the milestone list of S0.12 into an executable plan: for each of `BM0`..`BM9` the scope (by reference to the owning part), dependencies, what is stubbed, acceptance tests in Given / When / Then form, a Definition of Done and a demo. It does not restate feature specifications; features live in `S4.*`..`S16.*` and are referenced, never copied. [D]
- BUILDING is separated from LAUNCHING (brief, FD§8.3). Finishing a milestone, including `BM9`, never authorizes a launch; launching is the sign-off of the gates in `S14.*`. Every build of every milestone ships with `launch.members_may_join`, `launch.member_jobs_enabled` and `launch.minting_enabled` equal to `false` (S0.10.6 table C, S0.12 ordering rule 3). [D]
- Phase 1 of the FD is a configuration of the finished system, not a reduced product (S0.12 ordering rule 4; FD§9). Section 17.11 lists the configuration levers that make the pilot out of the full build. [D]
- Evidence tags follow S0.2. Every number in this part is either derived from a formula in S0 or is a reference to a parameter name in S0.10.6; no performance target or pilot size is invented here. Targets of load, restore and alert tests are set in `S18.*` and `S19.*` and recorded as `[V]` until a human sets them. [D]
- Milestone acceptance tests use the id area `bm<n>` in lowercase: `AC-bm3-04` is the fourth acceptance test of `BM3`. This keeps them from colliding with feature-level `AC-<area>-<nn>` ids owned by other parts (reported as `ISS-172`). A test that is owned by another part is cited by its own id (for example `AC-ledger-01`). [D]
- Work packages are `WP-BM<n>-<kk>` (17.9). A work-package id never appears in normative text of other parts. [A]

**Build rules** (apply to every milestone; each is checked by CI, not by memory) [D]

| Rule | Statement | How it is enforced |
| --- | --- | --- |
| `BR1` | Every milestone ends with a deployable, testable system and no half-wired path reachable from a public or member surface (S0.12 rule 1) | 17.3 argument; per-milestone demo run on `staging` |
| `BR2` | Migrations are forward-only and expand-then-contract; each migration has an up test on an empty database and an upgrade test from the final schema of the previous milestone | CI job `migrations`; rollback of code is allowed, rollback of schema is not |
| `BR3` | New behavior is either complete or behind a feature flag (`ff.*`, default off) or an operation that is not registered; no build flips a `launch.*` value or a flag | Seed test (17.8); route registration test |
| `BR4` | A stub is an implementation of a port with a contract test; it is replaced, never edited into the real thing. Every stub is listed in the "Stubbed" row of its milestone with the milestone that removes it. Production configuration refuses to start with a stub bound | Config validator test `AC-bm0-12`; stub register in `build/stubs.md` |
| `BR5` | Every state change emits its event (S0.9) into the outbox in the same transaction, and every log line and metric uses the names of S0.5, from the first milestone that has the state | Event-coverage test per machine; metric-name linter |
| `BR6` | Regression ratchet: tests added by a milestone stay in CI and stay green (S0.12 rule 5) | Manifest `ci/milestone-suites.yaml` lists the suites per milestone; removing or skipping a suite fails the build unless a spec change is referenced |
| `BR7` | No parameter value is hardcoded: code reads parameters from the config store; a parameter name used in code but absent from S0.10.6 / S16 fails CI, and so does a parameter with no seed row | Test family `T-unit` (parameter registry) |
| `BR8` | No provider is hardcoded and no external host is required: test fixtures use fictitious services; the built front-ends request nothing from a host outside the project's own allowlist (no third-party CDN, font or tracker) | CI job `external-hosts` scans sources and a recorded network log of the e2e run |
| `BR9` | Nothing automates a volunteer's account (ground rule 3): no dependency, route or field accepts a provider credential, session, chat-page content or an auto-submit; the paste-back accepts only the fields of `S9.*` | Test `AC-bm0-13` (forbidden-capability scan of manifests and routes), re-run in every milestone |
| `BR10` | A milestone is closed by a human who runs the demo script on `staging`, ticks its Definition of Done and files the record `build/dod/BM<n>.md`; for `BM1`, `BM2`, `BM6` and `BM7` (money and safety) a second human also signs [A] | Release checklist; not a launch sign-off |

## 17.2 Dependency graph

Milestone graph (arrows point from prerequisite to dependent; the `Depends on` column of S0.12 is authoritative, this is its text rendering). [D]

```
BM0 foundation
  +--> BM1 ledger_and_invariants
         +--> BM2 admin_gates_and_config
                +--> BM3 registry_and_policy -----+
                |                                  +--> BM5 templates_and_commons_jobs
                +--> BM4 identity_and_access -----+
   BM1 ------------------------------------------+
   BM5 -------------------------------------------> BM6 execution_and_verification   (also needs BM1)
   BM6 --> BM7 member_jobs_and_credit_economy
   BM6, BM7 --> BM8 experiences_and_public
   BM7, BM8 --> BM9 measurement_simulation_hardening
```

- **Critical path:** `BM0 -> BM1 -> BM2 -> BM3 -> BM5 -> BM6 -> BM7 -> BM8 -> BM9`. `BM4` is off the critical path (parallel with `BM3`) but must finish before `BM5`. [D]
- **Parallel pairs:** `BM3` with `BM4` (both need only `BM2`); inside every milestone the work packages of 17.9. The Persian-first front-end foundations (design system, i18n, Jalali conversion, bundled fonts, RTL test harness; module `web/shared`) have no route and no data dependency, so their work packages may start after `BM2` and merge as library-only code; no screen using them merges before the milestone that owns it. [A]
- **Phase 0 runs concurrently.** The calibration tool and the gate checklist exist at the end of `BM2`; the founders run Phase 0 (FD§9) on their own accounts while `BM3`..`BM9` are built, because the defaults for the cell envelope, lease timeout and sampling are replaced only by measurement (`CAL`, S0.10.4). [D]

| Edge | Why the dependency exists (the capability that is missing without it) |
| --- | --- |
| `BM0 -> BM1` | The ledger needs the money type, id format, time source, hashing, outbox and migration runner |
| `BM1 -> BM2` | Two-person reversal and `kill.all_minting` need a ledger to act on; the launch rule's `minting` switch needs minting to guard |
| `BM2 -> BM3` | Registry approval is an admin action with two-person options and public change-log entries; the gate rule counts approved services |
| `BM2 -> BM4` | Admin sessions and permission checks precede member-affecting actions (suspend, ban); `launch.members_may_join` guards member creation |
| `BM3, BM4 -> BM5` | Job creation needs the policy evaluator and a service in a reviewed state; roles and the permission matrix gate template and upload actions |
| `BM1, BM5 -> BM6` | Cells exist only after templates and jobs; accepted cells mint through the ledger |
| `BM6 -> BM7` | Admission capacity uses verified throughput; payout and the starter grant need accepted cells; v is measured from verification cells |
| `BM6, BM7 -> BM8` | Screens are built against finished behavior: card, lease, paste-back, balance, quote, escrow, public counters |
| `BM7, BM8 -> BM9` | Metrics read events of all earlier milestones; simulation and load tests need the finished flows and screens |

**Why the ledger and the gates come early** (prompt J, ground rule 6) [D]: (a) every later feature that moves credit posts through the ledger, so its invariants must be running before the first posting, not retrofitted; (b) the ledger is the one component whose errors are not recoverable by redeploying code, so it gets the longest soak time; (c) the launch-gate machinery (`BM2`) and the Service Registry with every service `unreviewed` (`BM3`) precede every feature that creates a job or shows a cell to a member (`BM5`, `BM6`), which makes the safe default structural instead of procedural; (d) the property-test harness built for the ledger in `BM1` is reused for admission control in `BM7`.

**Where FD§10 "What to add, in order" differs** [D]: FD§10 puts per-member identity second and the ledger fifth. This plan puts the ledger and the gates before identity because identity without the launch switch would let members exist before the gates are signed, and because the ledger has no dependency on identity (member accounts are created by `BM4`, 17.8). The FD list is a priority list for a panel rewrite; the build order of S0.12 is a dependency order. The mapping of all eleven FD§10 items to milestones is in 17.10.

## 17.3 Why every milestone leaves a working system

Claim: for every `k` in `0..9`, the build `S_k` made of `BMk` and all its prerequisites (17.2) is deployable, passes its own tests and every earlier milestone's tests, and exposes no path that depends on a component built later. [D] Argument, by construction:

1. **Ports, not calls.** A component that needs something from a later milestone calls a port (an interface) whose default binding is a stub with a contract test (`BR4`). The stub answers in the safe direction: the policy evaluator's template lookup says "not approved" (so rule `R4` rejects) until `BM5`; the launch rule's approved-service count is `0` until `BM3`; the trust-tier promotion inputs are empty until `BM6`. A stub never answers in the permissive direction. [D]
2. **Additive schema.** Migrations only add tables, columns and nullable foreign keys; a later milestone adds the constraint after backfill (17.8, deferred foreign keys). The code of `BMk` therefore runs on the schema of `BMk+j`. [D]
3. **Registered operations only.** Every operation of `S15.*` carries `x-milestone: BM<n>`; a build registers exactly the operations whose milestone is at most the build's level, and the conformance suite fails if a registered operation lacks its tests or its error-model, idempotency or rate-limit-header checks. A route that would need a later milestone is not registered, so there is no half-wired path. [D]
4. **Gates default closed.** Without a signed gate rule, member creation, member jobs and minting return `LAUNCH_GATE_CLOSED` (S0.11.3). A milestone that adds a member-facing path adds the check for its switch in the same change (`AC-bm4-01`, `AC-bm6-01`, `AC-bm7-01`). [D]
5. **Tests are exercised through the real gate.** Acceptance tests that need an open gate (members, minting) obtain it by the real sign-off flow with fixture admins in environments `ci` and `dev`, and with clearly marked rehearsal sign-offs on fictitious services in `staging`; `production` refuses both (`ISS-175`). No test bypasses the guard it is testing. [D]
6. **One-way ratchet.** `BR6` makes the set of green suites grow monotonically; a milestone that breaks an earlier suite is not finished. [D]
7. **Amendment, not reopening.** If a later milestone finds a gap in an earlier one, the fix is an additive change with its own acceptance test, recorded in the earlier milestone's file `build/dod/BM<n>.md` as an amendment; it never silently edits the closed record. [D]

What is reachable at the end of each milestone (a summary; the per-milestone rows in 17.6 are authoritative):

| End of | An operator or reviewer can | A member can | Credit can move? | Public surface |
| --- | --- | --- | --- | --- |
| `BM0` | read health and run CI | nothing | no | `/v1/public/health` |
| `BM1` | run the ledger tools (command line) and see invariant alarms | nothing | only in test databases, through the internal ledger interface | health |
| `BM2` | sign in with a passkey, edit parameters, engage kill switches, run calibration, attempt a gate sign-off | nothing | no | health, public parameter and change-log data |
| `BM3` | review services, save terms copies, answer flags, dry-run the policy evaluator | nothing | no | as `BM2` |
| `BM4` | moderate members | nothing until `launch.members_may_join` is signed on (never in a build); in `ci`, create, recover and rate-limit identities through the client SDK | no | as `BM2` |
| `BM5` | approve templates, author Commons jobs, split them into queued cells | nothing (no lease path yet) | no | as `BM2` |
| `BM6` | work audit, abuse and appeal queues | a scripted test donor completes cells through the SDK (in `ci` and rehearsal) | mint in `ci` and rehearsal only, under the monthly cap | as `BM2` |
| `BM7` | see capacity and economy dashboards | a scripted requester runs a job to settlement (in `ci` and rehearsal) | transfer, levy, refund, expiry, retirement, grant | as `BM2` |
| `BM8` | use every console screen in both locales | complete the first-contribution flow and the requester wizard in both locales (rehearsal) | as `BM7` | counter, public ledger, parameters, change log, milestones |
| `BM9` | read every Phase 1 measure, run the simulation harness, run the drills | as `BM8` | as `BM7` | as `BM8` |

## 17.4 Preparatory steps before the first line of BM0 code

Three steps are completed (or explicitly deferred with an owner decision in `S3.*`) before `BM0` writes platform code. They are human steps with recorded outputs; agents may assist but a named human signs. [D]

### 17.4.1 Step PB-1 (gate G4): review the existing panel repository and decide keep / wrap / replace

**Premise [P].** The panel (`github.com/abbashaji/panel`, a Cloudflare Worker based "Blueprint Panel") is treated as unreviewed [V] (brief J). The only facts available are the owner's static read in `docs/source/panel-review.md` (nothing executed; section 9 of that file lists what could not be determined). This plan cites it and assumes nothing it lists under "could not determine".

| Step | Action | Output |
| --- | --- | --- |
| 1 | A human reviewer reads the repository code and `docs/` against the checklist: every item of panel-review sections 4.5 (weaknesses) and 9 (undetermined) is either resolved by reading or kept as an open `[V]` | Annotated checklist |
| 2 | The reviewer may run the repository's own tests on a local machine; nothing is run against production or against live accounts | Test log (optional) |
| 3 | For each row of the table below, the reviewer records `keep`, `wrap` or `replace` with a reason and an evidence pointer; a row may be split | Decision record `docs/adr/panel-reuse` in the Hamyar repository |
| 4 | The record is attached as evidence to the `LaunchGateItem` of gate `G4` when `BM2` seeds the checklist (until then it lives in the repository) | Gate evidence (not a sign-off) |

Preliminary proposals (the reviewer may overturn every row; none is a finding about the code) [A][V]:

| Panel concept (panel-review reference) | Proposal | Reason and condition |
| --- | --- | --- |
| Cell dependency graph and computed status (sections 1, 3) | `keep` for the development process that builds Hamyar; `replace` for the product runtime | The product's `Job`, `Cell`, `Lease` machines (S0.9, `S5.*`) are database-backed with server-side timers; the panel computes status lazily from git (panel-review 3.3). A graph cannot carry a ledger or leases for strangers |
| Lease and fencing pattern: unique lock plus fast-forward with a `base` (3.3) | concept `keep`, implementation `replace` | Product leases are rows bound to a nonce with a reaper job (`lease.reap_interval_s`); fencing is the nonce plus `row_version` |
| Status graph, bottleneck view, status colors (sections 1, 8) | `wrap` as the operator queue and capacity map (`BM7`, completed in `BM8`) and as the public capacity map (`BM8`) | Read model fed by the Hamyar API through a new adapter. Conditions: licence and quality acceptable [V]; the external font request noted in panel-review 4.5 item 12 is removed (`BR8`) |
| Release and Hand over (3.4) | `replace` by native operator actions: `lease.revoked`, release of a leased cell, kill switches (`BM2`, `BM6`) | The panel's takeover works on git branches; the product has no git state |
| Shared-password auth, single `owner` principal, self-declared `who`, stateless cookie (4.1-4.5) | `replace` | FD§10 item 2; `S10.*` (member keypairs, per-admin passkeys, separate origin) |
| KV reservations keyed by display name, eventually consistent (2.2, 3.4) | `replace` | Authoritative transactional store keyed by member id |
| CI gate design: trusted plan and tools checkout, untrusted code in a no-secret job, merge pinned to the head commit (8) | `wrap` for the Hamyar development pipeline (the work packages of 17.9) | Condition: the `shell=True` acceptance execution and the setup script described in panel-review 4.5 items 9 and 15 are reviewed before any untrusted contributor runs code there [V] |
| Helper code such as `redact()` and constant-time compare (8) | `keep` after review, ported as module `platform/` utilities | Small, testable; the parity-fixture test pattern (7.1) is kept as a technique |
| Windows launcher and `blueprint://` protocol (6) | `replace` with registry-driven service adapters (`BM3`, `BM8`); no launcher is part of the platform | It hardcodes one provider host (6.2), which breaks the no-hardcoded-provider rule; FD§10 says the launcher becomes optional, extended or retired (`ISS-178`) |
| Opt-in auto-send userscript (6.4) | `exclude` | It presses Send on the human's behalf, which ground rule 3 forbids for volunteers. The human presses Send, always [D] |
| MCP tool surface and OAuth provider (1, 4) | `exclude` from the product runtime; development tooling only | Not part of any Hamyar surface |

### 17.4.2 Step PB-2: stack and host decision record

`S4.*` specifies the architecture stack-agnostically first and then recommends a concrete stack with reasons and alternatives; the choice of stack and host is an open owner decision (`S3.*`). The record `docs/adr/stack-and-host` fixes: runtime and language; the database and the isolation level that satisfies the ledger's consistency requirements (`S6.*`); the host and where object bytes live; how each port of `BM0` is bound. Constraints that any choice must meet: `BR8` (no mandatory third-party resource), no raw IP storage (S0.6.4), and reachability from Iran of the chosen host is `[V]`, measured with the reachability probe (17.7), never assumed. Until the record exists, this part names modules logically (17.9) and no work package may import a framework. [D]

### 17.4.3 Step PB-3: secret inventory and rotation before any public exposure

| Secret | Origin | Disposition |
| --- | --- | --- |
| `PANEL_TOKEN`, `ADMIN_TOKEN`, `GITHUB_TOKEN`, `MCP_AUTH_TOKEN` (the four existing secrets, FD§10) | Panel | Rotate before any public exposure of the panel or of any Hamyar environment (`security.rotate_before_public_exposure`, constant `true`); never reuse a value in Hamyar |
| `EXT_TOKEN` (a fifth secret, present only if set; panel-review section 4 overview) | Panel | Same; delete if the extension is retired |
| `secret.volunteer_handle_key[version]`, `secret.ip_hash_key[version]` | Hamyar (S0.6.4) | Created per environment when the environment is created; rotated in the drill of `BM9`; rotation of the handle key unlinks old handles by design |
| Every other secret named in `S10.*` (session signing, ledger checkpoint, storage, mail, database) | Hamyar | Same lifecycle; none is ever stored in the parameter table or returned by an API |

Rules [D]: (1) a secret is never pasted into a chat, ticket, commit, work-package prompt or log; coding agents never receive production secrets (panel-review 4.5 item 6 shows how a legacy flow would have put one into a transcript); (2) each environment has its own secret store behind the `secrets` port; (3) rotation is: generate in the store, deploy, invalidate the old value, verify the old value is refused, record the names, date and performer (never values), attach the record to the gate items named in `S14.*`; (4) the full history of the panel repository and its logs are searched for secret values, with the caveat that the reviewed clone had one commit and the earlier history is unknown [V]; (5) the scope of the panel's `GITHUB_TOKEN` and the owner-wide `ALLOWED_REPOS` setting (panel-review 4.5 items 8 and 9) are narrowed or retired as part of PB-1.

## 17.5 Environments, exposure boundary and the global Definition of Done

### 17.5.1 Environments [D]

| Environment | Purpose | Reachable by | Data | Gate behavior |
| --- | --- | --- | --- | --- |
| `dev` | Developer machine | The developer | Fixtures | Fixture profile `launch-open` allowed |
| `ci` | Ephemeral, per run | CI only | Fixtures; simulated clock | Fixture profile allowed; real sign-off flow with fixture admins |
| `staging` | Persistent rehearsal and demo | Named operators only (access control in front of the application) [A] | Fictitious services; no real member data | Rehearsal sign-offs flagged `rehearsal`; a banner says so |
| `production` | The real system | Nobody outside the operators until the exposure rule below holds | Real | Refuses the fixture profile and rehearsal sign-offs; only real gates |

A fresh `production` database is seeded as in 17.8 and stays closed: services `unreviewed`, gates unsigned, `launch.*` off, no members. [D]

### 17.5.2 Exposure boundary [D]

An **exposure event** is the first moment anyone other than the named operators can reach any Hamyar environment or any panel endpoint (public DNS, a shared link, open registration). Preconditions, each recorded as evidence: (E1) the PB-3 rotation record exists; (E2) the logging and retention decisions of the G1 threat model are implemented (`BM0` log scrubber, `BM4` retention jobs) [V]; (E3) transport security and the access-control layer are in place; (E4) the security headers, the content policy and the `external-hosts` check pass; (E5) the kill switches of `BM2` are exercised on that environment. Exposure of the application is not a launch: joining stays closed until `launch.members_may_join` is turned on by the sign-off flow of `S14.*`. The **reachability probe** is exempt: a static page with no data and no secrets, deployed to candidate hosts only to measure reachability for gate `G2`, may be exposed earlier [A][V].

### 17.5.3 Global Definition of Done (applies to every milestone) [D]

A milestone is done only if every box is ticked and a human has filed `build/dod/BM<n>.md` (`BR10`). Each milestone's own checklist in 17.6 adds to this list; it never removes from it.

- [ ] `GD1` All acceptance tests of the milestone pass in CI on a clean checkout and an empty database.
- [ ] `GD2` All suites of earlier milestones are still green (`BR6`); no suite was skipped without a referenced spec change.
- [ ] `GD3` Migrations pass the up test and the upgrade-from-previous-milestone test (`BR2`); no migration edits a published ledger, registry, policy, parameter or change-log row.
- [ ] `GD4` The seed of 17.8 runs on an empty database and the post-seed invariants test passes (services `unreviewed`, gates unsigned, `launch.*` false, no members, ledger sums to zero).
- [ ] `GD5` Every operation added carries `x-milestone`, an `op` id, the error model of S0.11.3, idempotency behavior of S0.11.5 where required, pagination of S0.11.6 where a list, and rate-limit headers of S0.11.7, each with a passing test.
- [ ] `GD6` Every state change added emits its S0.9 event in the same transaction as the change; logs and metrics use S0.5 names; the log-scrub test finds no raw IP, e-mail or credential.
- [ ] `GD7` Every parameter added exists in the seed with default, validation, owner and `calibration_source` (`BR7`); no value of a `[V]` fact (terms, region, price, limit, URL parameter) is hardcoded.
- [ ] `GD8` Every flag added defaults to off; `launch.members_may_join`, `launch.member_jobs_enabled` and `launch.minting_enabled` are `false` in the shipped build.
- [ ] `GD9` Secret scan, dependency audit [V], forbidden-capability scan (`BR9`) and external-host scan (`BR8`) pass.
- [ ] `GD10` Every stub of the milestone is in `build/stubs.md` with its removal milestone, and production configuration refuses to bind it (`BR4`).
- [ ] `GD11` The demo script of the milestone has been run on `staging` and its result recorded.
- [ ] `GD12` The previous release can be redeployed against the migrated schema (expand-then-contract holds).
- [ ] `GD13` Newly found problems in the Founding Document or in this spec are filed as issues in the `## Issues raised` list of the owning part (S0.4).

## 17.6 Milestones in detail

Each milestone has the same rows: scope (by reference), dependencies, stubbed, the working system at its end, acceptance tests, its Definition of Done (added to 17.5.3) and its demo. Acceptance tests are written Given / When / Then; every number is a parameter name or a value derived in S0.6.1. [D]

### BM0 `foundation`

| Row | Content |
| --- | --- |
| Scope | Steps PB-1..PB-3 (17.4) as exit conditions. Repository, module map and protected files (17.9); CI pipelines (`lint`, `unit`, `migrations`, `api-conformance`, `secret-scan`, `forbidden-capability`, `external-hosts`, `regression-manifest`); environments of 17.5.1. Libraries of S0.6: id generator with the prefix registry of S0.7 as data, `Money` (int64 `ucr`, integer-string JSON), `Clock` (UTC, injectable), SHA-256 and RFC 8785 canonical JSON, CSPRNG token helpers, `HMAC` IP hashing. API framework of S0.11: error model and code list, `Idempotency-Key` store, cursor pagination with MAC, rate-limit headers and limiter port, `ETag`/`If-Match`, auth-scheme skeleton, request ids, 415 on non-JSON. Config store: tables `parameters`, `parameter_versions`, `change_log_entries`; the validation engine for the `validation` json and constraints `C1`..`C8` (S0.10.3); the seed loader for the full parameter list of S0.10.6 / `S16.*`. Outbox and event bus (`S4.*`). Observability skeleton: structured logs named `<area>.<event>`, log scrubber, metric registry with the `hamyar_<area>_<name>_<unit>` linter, health endpoint. Ports with local bindings: `storage`, `objects`, `secrets`, `scheduler`, `clock`, `mail`, `ratelimit_store`. i18n scaffold: copy-key registry (`copy.<area>.<key>`, `fa` and `en`, marker `needs_human_and_legal_review`) and the logical-property CSS convention for RTL. Backup and restore runbook. Reachability probe (static, no data) for gate `G2` |
| Entities | `Parameter`, `ParameterVersion`, `ChangeLogEntry`, `Event` (S0.7) and the outbox table |
| Endpoints | `GET /v1/public/health` (public, S0.11.2); test-only conformance routes mounted only when environment is `ci` |
| Depends on | none (PB-1..PB-3 inputs) |
| Stubbed | Member and admin token verifiers (answer `AUTH_REQUIRED`); `secrets` (local file in `dev` only); `mail` (no-op); `objects` (local directory); `scheduler` (in-process); `ratelimit_store` (in memory). Removed by: `BM2` (admin verifier), `BM4` (member verifier, `mail`), host-bound implementations by `BM9` |
| Working system | An API serves `/v1/public/health` in the S0.11 shapes; migrations, seeds and API conformance run in CI; production configuration refuses stubs |
| Demo | Call health; list the seeded parameters; replay an idempotent request; show the CI run and the stub register |

**Acceptance tests (BM0)**

- `AC-bm0-01` Given an empty database, When migrations and the seed run, Then every parameter name of S0.10.6 exists with `ParameterVersion` 1 equal to its default, and `launch.members_may_join`, `launch.member_jobs_enabled`, `launch.minting_enabled` are `false`.
- `AC-bm0-02` Given an operation that requires `Idempotency-Key`, When it is called without the header, Then `400 VALIDATION_FAILED`; When called twice with the same key and body, Then the stored response is replayed with `Idempotent-Replayed: true`; When called with the same key and a different body, Then `422 IDEMPOTENCY_KEY_MISMATCH`.
- `AC-bm0-03` Given a request still running, When a second request with the same key arrives, Then `409 IDEMPOTENCY_IN_PROGRESS` with `Retry-After`; a `5xx` outcome is not stored.
- `AC-bm0-04` Given the id generator, When many ids are generated across processes, Then each matches `^[a-z]{3}_[0-9a-hjkmnp-tv-z]{26}$`, prefixes match S0.7, ids sort by creation time within a process, and no two prefixes collide.
- `AC-bm0-05` Given amounts above 2^53, When serialized to JSON, Then they are integer strings and round-trip exactly; a value outside int64 is refused; no float type exists in the money path.
- `AC-bm0-06` Given an injected `Clock`, When time advances, Then `_days` parameters mean exactly 86,400 seconds, no column stores local time, and a client-supplied timestamp never sets `expires_at`.
- `AC-bm0-07` Given a list operation, When the cursor is altered or older than `api.cursor_ttl_s`, Then `400 VALIDATION_FAILED`; the page size never exceeds `api.page_size_max`.
- `AC-bm0-08` Given a rate-limited route, When the limit is exceeded, Then `429 RATE_LIMITED` with `Retry-After`, every response carries `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`, the key is an HMAC of the IP, and a canary IP address appears in no database dump and no log line.
- `AC-bm0-09` Given a non-JSON body, Then `415 UNSUPPORTED_MEDIA_TYPE`; given an unknown id, Then `404 NOT_FOUND`; every error has the one-key body of S0.11.3 with a `request_id` equal to `X-Request-Id`.
- `AC-bm0-10` Given the validation engine, When a write violates `C1`..`C7`, Then `VALIDATION_FAILED`; `C8` yields a warning only; a constant parameter cannot be written; a non-tightening change with `effective_from` earlier than `now + notice_days` is refused.
- `AC-bm0-11` Given health is called, Then `200` with no authentication and a `Cache-Control` no larger than its refresh setting; authenticated responses carry `Cache-Control: no-store`.
- `AC-bm0-12` Given a production configuration that binds a stub from `build/stubs.md`, When the application starts, Then it refuses to start and names the stub.
- `AC-bm0-13` Given the forbidden-capability scan, When it inspects dependency manifests, route tables and request schemas, Then it finds no browser-automation dependency, no field named for a provider credential, session or chat content, and no auto-submit mechanism (`BR9`).
- `AC-bm0-14` Given a built front-end bundle and a recorded network log, When scanned, Then no request goes to a host outside the allowlist and the content policy header is present (`BR8`).
- `AC-bm0-15` Given a populated CI database, When backup then restore into an empty database runs, Then row counts and the content hashes of all tables are equal.
- `AC-bm0-16` Given a state change and its event, When the transaction rolls back, Then neither exists; When it commits, Then both exist (outbox atomicity).
- `AC-bm0-17` Given the repository, Then `docs/adr/panel-reuse` and `docs/adr/stack-and-host` exist with the required headings, a secret scan of the tree finds nothing, `staging` refuses a request from a non-allowlisted source, and `security.rotate_before_public_exposure` is `true`.

**Definition of Done (BM0)** adds to 17.5.3:

- [ ] PB-1 decision record and PB-2 stack record merged; PB-3 inventory filed (rotation done or scheduled before exposure per 17.5.2).
- [ ] Module map, protected-file list and the work-package template of 17.9 merged and enforced by CI path rules.
- [ ] The seed covers every name in S0.10.6 and `S16.*`; the metric-name linter and `copy.*` registry validator run in CI.
- [ ] Restore from backup is rehearsed once on `staging`.

### BM1 `ledger_and_invariants`

| Row | Content |
| --- | --- |
| Scope | `S6.*` ledger core: append-only double-entry ledger in integer `ucr`; account types and entry types of S0.8.5; `LedgerTransaction` groups (`ledger_txn_kind`); `CreditLot` with oldest-first spending, per-lot `expires_at` using the parameter version at `earned_at`, refund that restores lots with their original expiry (`ISS-07`); per-ledger `seq`; hash chain `entry_hash = SHA-256(prev_hash \|\| canonical(entry))` and daily checkpoint; `Escrow` and `Reserve` rows; bootstrap of the three singleton accounts (`issuance`, `retired`, `reserve`); reversal with two approvers (`ledger.reversal_min_approvers`, constant) as a ledger function that takes two distinct approver ids. Invariant machinery: the per-commit check (constant) and the sampled and full recompute jobs (`ledger.invariant_check_interval_s`, `ledger.full_recompute_interval_s`, `ledger.checkpoint_interval_s`), `InvariantCheck`, `Alarm`, event `ledger.invariant_violated`, metric `hamyar_ledger_invariant_violations_total`. Invariant classes (exact `INV-L<nn>` ids are in `S6.*`): conservation (all accounts sum to zero); `issuance` equals minus cumulative mint; `retired` equals cumulative retired; non-negative member, escrow and reserve balances; a closed escrow is exactly zero; lots of a member sum to the member balance; gapless `seq`; unbroken hash chain; no update or delete path |
| Entities | `LedgerAccount`, `LedgerEntry`, `LedgerTransaction`, `CreditLot`, `Escrow`, `Reserve`, `InvariantCheck`, `Alarm` |
| Endpoints | None public. Internal ledger interface and a command-line tool `ledger-cli` (`verify`, `checkpoint`, `explain`) |
| Depends on | `BM0` |
| Stubbed | Approver identities (test principals; admin flow arrives in `BM2`); lot-lifetime resolver (returns `credit.lifetime_days`; the expiry-arm resolver arrives in `BM6`); member accounts refer to a `mem_` id without a foreign key and escrows to a `job_` id without one (constraints added by `BM4`, `BM5`, 17.8, `ISS-176`); alarm delivery is log and console only |
| Working system | A ledger driven through its internal interface; the FD§3.3 example posts and closes exactly; a seeded corruption raises `ledger.invariant_violated` |
| Demo | In a throwaway database post the FD§3.3 example with `ledger-cli`, print the closing identity (264,000,000 + 12,000,000 = 276,000,000 ucr); then run the corruption script and watch the alarm |

**Acceptance tests (BM1)**

- `AC-bm1-01` `AC-ledger-01` (the FD§3.3 example of S0.6.1) passes against the real ledger, including the refund of 0 and the closing identity.
- `AC-bm1-02` Given random sequences of valid operations (property test `T-prop-*`), When executed, Then every invariant class holds after every commit.
- `AC-bm1-03` Given a member balance of `b` ucr, When a hold of more than `b` is posted, Then it is refused, nothing is written and `ledger.allow_negative_balance` is not consulted (constant `false`).
- `AC-bm1-04` Given lots with different `earned_at`, When a hold consumes credit, Then the oldest lot is consumed first; When the escrow is refunded, Then the consumed lots are restored with their original `expires_at`.
- `AC-bm1-05` Given a lot, When the sweep runs before `expires_at`, Then nothing moves; after `expires_at`, Then an `expire` entry moves exactly the lot's remaining amount to the `reserve` account, using the lifetime in force at `earned_at` even if `credit.lifetime_days` changed since.
- `AC-bm1-06` Given the Reserve above `reserve.ceiling_credits` by at least `reserve.retire_min_credits`, When the retirement job runs, Then a `retire` entry removes exactly the excess and `retired` equals cumulative retired.
- `AC-bm1-07` Given the application database role, When it attempts `UPDATE` or `DELETE` on any ledger table, Then the database refuses.
- `AC-bm1-08` Given an entry altered by a privileged test role, When the full recompute runs, Then the chain check fails, `ledger.invariant_violated` is emitted once per violation, an `Alarm` is raised and stays raised until acknowledged, and the metric increments.
- `AC-bm1-09` Given parallel postings on the same account, When run, Then no balance goes negative, `seq` is gapless and strictly ordered, and the result equals some serial order.
- `AC-bm1-10` Given a reversal request, When only one approver, or the same approver twice, is supplied, Then it is refused; with two distinct approvers it posts the mirror entry with the mirrored lot effect and the original row is untouched.
- `AC-bm1-11` Given a posting with an idempotency key, When it is retried, Then exactly one transaction exists.
- `AC-bm1-12` Given the checkpoint job, When it runs, Then a checkpoint hash is stored, and verification from that checkpoint forward succeeds and fails after tampering.
- `AC-bm1-13` Given a synthetic escrow, When `settle` posts the levy and the refund, Then the escrow account is exactly zero and `Escrow` is `closed`.
- `AC-bm1-14` Given a transaction that would break conservation, When it commits, Then the per-commit check rejects it.
- `AC-bm1-15` Given the integer rules of S0.6.1 (`p_ucr = 1,000,000 + v_ppm + lambda_ppm`, `v_ppm` rounded up, `eta_ppm = floor(10^12 / p_ucr)`), When property-tested, Then identities hold with zero tolerance.

**Definition of Done (BM1)** adds to 17.5.3:

- [ ] Every invariant class has a positive test and a deliberately corrupting negative test.
- [ ] The database-level append-only guarantee is verified under the real application role, not only in application code.
- [ ] The property-test harness is reusable (documented inputs, seedable generator) for `BM7`.
- [ ] Second human signature on the DoD record (`BR10`).

### BM2 `admin_gates_and_config`

| Row | Content |
| --- | --- |
| Scope | `S10.*` admin authentication: `AdminUser`, `AdminCredential` (WebAuthn passkeys, no shared password), admin `Session` with `session.admin_*` TTLs, admin API on a separate origin, one-time bootstrap command that refuses to run when an `AdminUser` exists and seeds no credential [A]. `AdminAction` log (append-only) and the two-person framework for `security.two_person_actions` (`ledger.reversal`, `launch.signoff`, `parameter.loosen`, `killswitch.release`). `S14.*`: `LaunchGateItem` checklist for `G0`..`G5` with evidence and sign-offs (machine in S0.9.8), the gate rule and enforcement of `launch.*` (settable only when the rule passes; reopening a required gate turns the dependent switches off), `KillSwitch` (`kill.all_minting`, `kill.all_new_jobs`, `kill.template.<tpl_id>`, `kill.service.<svc_id>`, `kill.member.<mem_id>`) with the evaluation library `assertNotKilled(scope)`. `S16.*`: the parameter editor (versions, `effective_from`, `tighten` immediate and `loosen` with notice and second operator, public `ChangeLogEntry`, `change.tighten_publish_within_s`). `FeatureFlag`, `Experiment`, `ExperimentAssignment` (seeded, append-only, logged) and `PreRegistration` with lock. Phase 0 `CalibrationRecord` tool (S0.10.4 `CAL`) with `calibration.min_samples_per_service`. Operator console (`SCR-ops`) for the above, plus a read-only ledger explorer and alarm list. Admin side of the permission matrix (`reviewer`, `operator`). Reachability-probe evidence entry for `G2` |
| Entities | `AdminUser`, `AdminCredential`, `Session` (admin), `AdminAction`, `KillSwitch`, `FeatureFlag`, `Experiment`, `ExperimentAssignment`, `PreRegistration`, `LaunchGateItem`, `CalibrationRecord`; `Parameter` editor on the `BM0` tables |
| Endpoints | `/v1/admin/*` families: sessions, admin users, parameters, change-log, kill-switches, feature-flags, experiments, pre-registrations, launch-gates, calibration-records, admin-actions, ledger (read), alarms; public read: `/v1/public/parameters`, `/v1/public/change-log` (exact paths and `op` ids in `S15.*`) |
| Depends on | `BM0`, `BM1` |
| Stubbed | The approved-service count used by the gate rule is `0` until `BM3`, so the rule can never pass in `BM2`; `CalibrationRecord.service_key` is a free-text label until `BM3` adds a link to the registry (`ISS-173`); alarm delivery is console only (paging is an owner decision, `S3.*`); the assignment library is exercised with synthetic subjects until `BM4` |
| Working system | An operator signs in with a passkey, edits a parameter prospectively, engages a kill switch, records calibration data, attaches evidence to a gate, and is refused when trying to turn a `launch.*` switch on |
| Demo | Virtual passkey sign-in; loosen a parameter (needs second operator, notice period shown); engage and release a kill switch; enter calibration rows; try `launch.members_may_join` and read the list of unmet gate conditions |

**Acceptance tests (BM2)**

- `AC-bm2-01` Given a fresh database, When an operator sets `launch.members_may_join` to `true`, Then `403 LAUNCH_GATE_CLOSED`, the parameter version is unchanged, and the reply lists the unmet conditions; this still holds when every gate is signed, because the approved-service count is `0`.
- `AC-bm2-02` Given two sign-offs by the same admin, When counted, Then they count once; `launch.min_signoffs` distinct admins are required.
- `AC-bm2-03` Given the admin sign-in flow, Then no password field or password endpoint exists; a passkey registration and authentication complete with a virtual authenticator; a member-scheme token sent to `/v1/admin/*` returns `AUTH_INVALID` and counts against the rate limit.
- `AC-bm2-04` Given an injected clock, When `session.admin_idle_ttl_s` or `session.admin_abs_ttl_s` elapses, Then `AUTH_EXPIRED`.
- `AC-bm2-05` Given a `loosen` change, When made, Then it needs a second operator and `effective_from >= now + notice_days`; Given a `tighten` change, Then it applies at once and its public `ChangeLogEntry` is published within `change.tighten_publish_within_s`; each change writes one `ParameterVersion`, one `ChangeLogEntry`, one `AdminAction` and `parameter.changed`.
- `AC-bm2-06` Given a constant parameter or a violation of `C1`..`C7`, When written through the editor, Then `VALIDATION_FAILED`.
- `AC-bm2-07` Given a kill switch engaged, Then a fixture route using `assertNotKilled` answers `503 KILL_SWITCH_ENGAGED`; release needs two operators; each state change is a row and an event.
- `AC-bm2-08` Given any feature flag, Then its default is off; Given an experiment assignment, When requested twice for the same subject and `experiment.assignment_seed_version`, Then the same arm is returned and the assignment is logged once and cannot be edited.
- `AC-bm2-09` Given a pre-registration, When locked, Then edits return `409 STATE_CONFLICT`, its content hash is stable and the lock is logged; the lock time is recorded for the gate rule.
- `AC-bm2-10` Given fewer than `calibration.min_samples_per_service` records for a service label, Then the aggregate is marked insufficient; no parameter is changed automatically from a calibration record (a human edits the parameter citing it) [D].
- `AC-bm2-11` Given any admin write, Then exactly one `AdminAction` exists and the log has no update or delete path.
- `AC-bm2-12` Given an existing `AdminUser`, When the bootstrap command runs, Then it refuses; given none, Then it creates a single-use, expiring enrollment and no credential is seeded.
- `AC-bm2-13` Given a request to the admin API with a foreign `Origin`, Then it is refused.
- `AC-bm2-14` Given a ledger reversal request, When two distinct admins approve, Then `AC-bm1-10` is satisfied through the admin flow; one admin cannot complete it.
- `AC-bm2-15` Given the checklist seeded at `open`, When evidence is attached, Then the item does not become `signed_off`; When a required gate is reopened in a database where the rule had been satisfied by fixtures, Then the dependent `launch.*` switches become `false` and `launch.members_may_join_changed` is emitted (`S14.*`).

**Definition of Done (BM2)** adds to 17.5.3:

- [ ] No production code path reads a `launch.*` value without going through the gate library.
- [ ] The console works in `en` with copy keys for every string and logical-property CSS; Persian strings and polish are completed in `BM8` (`ISS-174`).
- [ ] The reachability-probe result and the PB-1, PB-3 records can be attached to gate items `G2`, `G4`, `G1`.
- [ ] Second human signature on the DoD record (`BR10`).

### BM3 `registry_and_policy`

| Row | Content |
| --- | --- |
| Scope | `S7.*` Service Registry: `ServiceRegistryEntry` with the review machine of S0.9.6 (every service starts `unreviewed`, counts as `no`), `TermsCopy` (bytes in the `objects` port plus `sha256:` hash, source reference, capture date), dated `FlagAnswer`s per `flag_key` of S0.8.3 with optional `region`, review screens (`SCR-rev`), approval guard (`third_party_task_use` and `prohibited_content_compatible` are `yes`, a saved `TermsCopy`, reviewer recorded, `service.min_approvers`), timers `service.review_max_age_days` and `service.review_grace_days`, link of `CalibrationRecord.service_key` to entries. Service-adapter port: capability object from the registry (`adapter.supports_prefill`, `adapter.prefill_url_template`, `adapter.max_url_chars`, `adapter.copy_only`, `adapter.clean_chat_hint_key`), a pure URL-builder with `{prompt}` substitution and length check, tested only with fictitious templates [V]. Policy engine: `Policy`, `PolicyVersion`, `Rule` rows `R1`..`R10` as data plus the evaluator, the metadata schema and validation (purpose `P0`..`P3`, license `L0`..`L3`, sensitivity `S0`..`S3`, service requirement `M0`..`M2`), the allowlist of permitted combinations as data, reason codes `policy.<rule>.<slug>`, stamping and the acceptance re-check library (`R9`), the tighten-at-once versus loosen-with-change-log workflow (`R10`, `policy.loosen_min_notice_days`), `TopicCategory` and the `OptIn` data model with defaults from `optin.*` and the `R8` visibility predicate. Admin dry-run endpoint that evaluates a job-shaped declaration and returns the decision and reasons [A] |
| Entities | `ServiceRegistryEntry`, `TermsCopy`, `FlagAnswer`, `Policy`, `PolicyVersion`, `Rule`, `TopicCategory`, `OptIn` (data model only) |
| Endpoints | `/v1/admin/*` families: services, terms-copies, flag-answers, service-reviews, policies, policy-versions, rules, topic-categories, policy-evaluations (dry run); the gate rule's service counter is now real (`S15.*` for paths) |
| Depends on | `BM2` |
| Stubbed | `TemplateLookup` port answers "not approved", so `R4` rejects every request in a production binding until `BM5`; `OptIn` rows have no member until `BM4`; in-flight cell handling on revocation is defined by the machine but has no cells until `BM6`; `kill.service.<svc_id>` is evaluated but has no cells to pause |
| Working system | A job-shaped declaration is accepted or rejected with `policy.<rule>.<slug>` reasons; no service can reach `approved` without a saved terms copy; the gate rule counts real approved services |
| Demo | A reviewer creates a fictitious service, saves a terms file, answers flags, approves it (second approver if configured), dry-runs declarations that pass and fail each rule, then revokes the service and shows the state |

**Acceptance tests (BM3)**

- `AC-bm3-01` Given a fresh database, When any service entry is listed, Then its state is `unreviewed`; When a declaration naming it is evaluated, Then the decision is reject with the service-state reason defined in `S7.*`.
- `AC-bm3-02` Given a service in `in_review`, When approval is attempted without a `TermsCopy`, or with `third_party_task_use` or `prohibited_content_compatible` equal to `no` or `unknown`, Then `409 STATE_CONFLICT`; `unknown` is evaluated as `no` for every gating flag.
- `AC-bm3-03` Given a stored `TermsCopy`, When its bytes are re-hashed, Then the hash equals the stored `sha256:` value; no operation edits or deletes it; a new capture is a new row.
- `AC-bm3-04` Given a new `FlagAnswer`, Then the previous answer remains in history; a `region`-specific answer is stored apart from the global one; no region value is hardcoded anywhere.
- `AC-bm3-05` Given an approved service older than `service.review_max_age_days`, When the timer runs, Then `service.review_due` is emitted and new declarations naming it are rejected at once; after `service.review_grace_days`, Then `service.review_lapsed` and the state `suspended`.
- `AC-bm3-06` Given the table of allowed and rejected combinations in `S7.*` as oracle, When every row is evaluated, Then the decision and reason codes equal the table; a property test shows no declaration with `S2` or `S3` is accepted and `P3` is accepted only with `S0` and (`M2` or `training_use_of_output` = `yes`).
- `AC-bm3-07` Given a test policy version without the `R5` row, When a `P2` declaration is evaluated, Then the `R5` check no longer applies (rules are data; the evaluator has no rule-specific branch outside registered handlers).
- `AC-bm3-08` Given a loosening change without a published `ChangeLogEntry`, Then it is refused; a tightening change applies at once; a loosening change takes effect only after `policy.loosen_min_notice_days`.
- `AC-bm3-09` Given a declaration stamped with policy version `n`, When version `n+1` tightens a rule and the acceptance re-check runs, Then the result carries `reject.policy_changed` (`R9`; fixture cell).
- `AC-bm3-10` Given a fictitious prefill template and a prompt, When the builder runs, Then `{prompt}` is substituted URL-encoded; if the result exceeds `adapter.max_url_chars` or `prefilled_link_use` is not `yes`, Then `adapter.copy_only` is true and no URL is produced; for an `unreviewed` service no URL is ever produced.
- `AC-bm3-11` Given the `optin.*` defaults, When the `R8` predicate is evaluated for a cell and a set of opt-ins, Then it returns visible only if purpose, sensitivity, license, service requirement and topic all match; sensitive topics default to not opted in.
- `AC-bm3-12` Given the gate rule of `AC-bm2-01`, When an approved fictitious service exists and all required gates are signed by fixture admins in `ci`, Then the rule passes in `ci`, and still fails in a `production` binding.
- `AC-bm3-13` Given the repository, Then no provider name, URL template or region claim appears outside the fictitious fixtures (`BR8`).

**Definition of Done (BM3)** adds to 17.5.3:

- [ ] The policy oracle table of `S7.*` is executable and complete for every combination of the four axes.
- [ ] The seed policy version 1 is published with its genesis change-log entry and contains `R1`..`R10`.
- [ ] Reviewer screens exist in `en` with copy keys; no screen can approve a service without showing the saved terms copy.
- [ ] Every `FlagAnswer` shows who recorded it and when.

### BM4 `identity_and_access`

| Row | Content |
| --- | --- |
| Scope | `S10.*` identity: anonymous `Member` creation with no e-mail and no signup (`launch.members_may_join` guard), `MemberKey` (Ed25519 [A], S0.6.4), challenge-response sessions (member `Session`, tokens stored as hashes), `Device` (keyed hash), recovery key (generation on the client; the server stores only what `S10.*` specifies), recovery flow with `identity.recovery_cooldown_s` and `identity.recovery_max_per_90d`, key rotation with `identity.key_rotation_grace_s`, device linking with `identity.device_link_code_ttl_s`, optional e-mail (`identity.email_optional`, constant), `Invite` and invite trees (`invite.*`), rate limits per device, IP hash, invite tree and day (`ratelimit.*`), roles and the permission matrix as data (`perm.<area>.<action>`), the member trust-tier and status machines (S0.9.4) with their events, suspend, ban, close admin actions, retention jobs (`retention.*`), IP-hash handling with `retention.ip_hash_ttl_days`, creation of the member's `LedgerAccount` in the same transaction, experiment assignment hook (`BM2` library) on creation, foreign-key backfill from ledger accounts to members (17.8). The browser-compatible identity client SDK (no UI) and a test harness client. Member-side safety design: no location display, minimal collection, no raw IP or clear e-mail anywhere |
| Entities | `Member`, `MemberKey`, `Device`, `Invite`, `Session` (member), `OptIn` rows created with defaults |
| Endpoints | Member surface: members (anonymous create), sessions, keys, devices, recoveries, invites, opt-ins, settings, `GET` own profile (`S15.*`); admin: members (suspend, ban, close, restrict), invites tree view |
| Depends on | `BM2` |
| Stubbed | The `mail` port stays a no-op (optional e-mail verification is not delivered until a mail binding is chosen, `S3.*`); trust-tier promotion inputs (accepted cells, reliability) are empty until `BM6`, so tiers stay `new` except by admin action; the invites-issued counter port returns `0` until `BM6`, so only operator-issued root invites exist [A]; recovery cooldown is exposed as a queryable flag and enforced on spending in `BM7` |
| Working system | A member can be created, recovered, rate-limited and moderated; the permission-matrix suite passes; no raw IP appears in storage or logs |
| Demo | Using the client SDK in `ci`: create three members, issue an invite tree, link a device, rotate a key, recover an identity, trip each rate limit; an admin suspends one member |

**Acceptance tests (BM4)**

- `AC-bm4-01` Given a fresh database with default parameters, When anonymous member creation is called, Then `403 LAUNCH_GATE_CLOSED`; Given the gate satisfied through the real flow in `ci`, Then `201` with a `mem_` id and no e-mail field.
- `AC-bm4-02` Given `ratelimit.device_new_members_per_day` creations from one device, When one more is attempted, Then `429 RATE_LIMITED`; the same holds for `ratelimit.ip_hash_new_members_per_day` and `ratelimit.invite_tree_new_members_per_day`.
- `AC-bm4-03` Given a signed challenge, Then a session is issued; a wrong signature returns `AUTH_INVALID`; a database scan finds no raw session token, only hashes.
- `AC-bm4-04` Given a member with a lost device, When the recovery key is used, Then a new `MemberKey` is registered, `member.recovered` is emitted, `recovery_cooldown_active` is true for `identity.recovery_cooldown_s`, and more than `ratelimit.recovery_attempts_per_day` attempts return `429`; a third recovery inside 90 days beyond `identity.recovery_max_per_90d` is refused.
- `AC-bm4-05` Given a key rotation, Then the old key works until `identity.key_rotation_grace_s` has passed and `member.key_rotated` is emitted; a device link code is single use and expires after `identity.device_link_code_ttl_s`.
- `AC-bm4-06` Given an invite tree at `invite.tree_max_depth` or `invite.tree_max_members`, When a further invite is accepted, Then it is refused; an invite older than `invite.ttl_days` cannot be accepted.
- `AC-bm4-07` Given the permission-matrix table of `S10.*` (principal x operation), When each cell is exercised, Then the result is `401`, `403` or `404` exactly as tabled; a token of one scheme on an endpoint of another is `AUTH_INVALID`.
- `AC-bm4-08` Given rows older than their `retention.*` limits, When the retention jobs run, Then they are purged; on closure `member_bound` rows are deleted or reduced to the opaque id.
- `AC-bm4-09` Given canary values for an IP address and an e-mail address, When a full database dump, all logs and all metrics are scanned, Then neither canary appears in clear text.
- `AC-bm4-10` Given a suspended or banned member, Then new sessions are refused and active sessions are revoked; `kill.member.<mem_id>` returns `503 KILL_SWITCH_ENGAGED`.
- `AC-bm4-11` Given member creation, Then the `LedgerAccount` exists in the same transaction; a forced failure of either rolls back both; the foreign key from `ledger_accounts` to `members` is validated.
- `AC-bm4-12` Given more than `ratelimit.member_api_rpm` calls in a minute, Then `429`.
- `AC-bm4-13` Given an experiment assignment on creation, Then it is logged once and the arm is reproducible.

**Definition of Done (BM4)** adds to 17.5.3:

- [ ] The permission matrix in the repository is generated from the table in `S10.*`; a test fails if an operation has no row.
- [ ] The client SDK has no dependency that reaches a third-party host and stores keys only on the device.
- [ ] The retention table of `S10.*` is implemented for every entity class named `member_bound`, `short` or `moderation`.
- [ ] The threat-model rows for fake accounts, account takeover and de-anonymization each point at at least one test of this milestone.

### BM5 `templates_and_commons_jobs`

| Row | Content |
| --- | --- |
| Scope | `S8.*`: `Template` and `TemplateVersion` (slots, prompt body, delimiters, output schema, automatic checks, comparator, cell envelope, review status), the review machine of S0.9.5 with the second-reviewer rule (`template.min_reviewers_new`, `template.min_reviewers_edit`) and a review queue with diff (`SCR-rev`), immutability after approval, versioning and supersession. The first template set seeded as `draft` (never `approved` by a seed, effectiveness `[H]`): `translation_glossary`, `classify_extract`, `summarize_schema`, `code_change_tests`, `format_convert_validator`, each with prompt skeleton, input and output schema and automatic checks; a template test harness where a reviewer runs the checks on supplied sample outputs without any lease. `S9.*` defenses at the template and input side: wrapping of untrusted input in delimiters, delimiter-collision handling, template lint (a task may only ask the volunteer to copy, press Send and return text, `R3`), `Upload` and `Glossary`, input screening (`screen.*`: URLs, PII patterns, instruction patterns) with a reviewer queue. `S5.*` `Job` machine for Commons jobs and the `Cell` machine up to `Cell.queued`; Commons backlog authoring by operators; the template-specific splitter that cuts an upload into cells inside `cell.envelope.max_input_chars`; hashes of inputs. Pause by `kill.template.<tpl_id>` |
| Entities | `Template`, `TemplateVersion`, `Job`, `Cell`, `Upload`, `Glossary` |
| Endpoints | Admin: templates, template-versions, template-reviews, commons-jobs, uploads, screening-queue; member job endpoints exist as operations only for `BM7` and are not registered yet (`S15.*`) |
| Depends on | `BM3`, `BM4` |
| Stubbed | No lease path: cells stay `queued`; the verification checks are defined and runnable in the harness but not in a pipeline; gold cells are not authored yet; the `human_review` template is added in `BM6`; `Job` states for member jobs (`quoted`, `waitlisted`, escrow) are present in the machine but unreachable until `BM7` |
| Working system | A reviewer approves a template; an operator authors a Commons job which splits into queued cells; creation is refused for every `unreviewed` service |
| Demo | Author a template version, run its harness on fixtures, have two reviewers approve it, upload a data file, watch screening flag a URL, create the Commons job, view the queued cells, then try to create a job for an `unreviewed` service |

**Acceptance tests (BM5)**

- `AC-bm5-01` Given a new template version by author A, When A requests review, B approves, Then `awaiting_second_review`; When B approves again, Then still `awaiting_second_review`; When C approves, Then `approved`; A cannot approve own work; an edit of an approved template needs `template.min_reviewers_edit` approvals.
- `AC-bm5-02` Given an approved `TemplateVersion`, When any field is edited, Then `409 STATE_CONFLICT`; a change is a new version and its content hash differs.
- `AC-bm5-03` Given a Commons job declaration, When the service is `unreviewed`, Then it is rejected by the evaluator; When the template version is not `approved`, Then `policy.R4.template_required`.
- `AC-bm5-04` Given an upload of `N` records, When split, Then each cell input is at most `cell.envelope.max_input_chars`, ids are server-issued `cel_` ids, order is preserved for reassembly, and the sum of record counts over cells equals `N`.
- `AC-bm5-05` Given an input with a URL and `screen.max_urls_per_input` equal to 0, Then it is handled per `screen.url_action`; given a PII pattern, Then `screen.pii_action`; flagged inputs wait in the reviewer queue and create no cells.
- `AC-bm5-06` Given a set of adversarial template bodies (ask to visit a link, run code, send a message, reveal context), When linted, Then each is rejected under `policy.R3.prohibited_content` and none can reach `in_review`.
- `AC-bm5-07` Given untrusted input containing the template delimiter, When the prompt is built, Then the delimiter is neutralized as `S9.*` specifies and the wrapped prompt parses back to exactly the original input.
- `AC-bm5-08` Given the seed, Then the five required templates exist as `draft`, each with every field of the template format; none is `approved`; the harness reports pass or fail on fixture samples as expected.
- `AC-bm5-09` Given `kill.template.<tpl_id>` engaged, Then the job becomes `suspended` and its queued cells `suspended` (`job.paused`, `cell.paused`); release requires two operators.
- `AC-bm5-10` Given the `Job` and `Cell` machines, When every transition of S0.9.2 and S0.9.3 reachable in this milestone is driven (state-machine test `T-fsm-*`) and every invalid one is attempted, Then valid ones emit exactly their event and invalid ones return `409 STATE_CONFLICT` with no event.
- `AC-bm5-11` Given an upload larger than `job.max_upload_bytes`, Then `413 PAYLOAD_TOO_LARGE`.
- `AC-bm5-12` Given a template review, Then every action is an `AdminAction` and the review history is read-only.

**Definition of Done (BM5)** adds to 17.5.3:

- [ ] Every template field is covered by a schema test; the seeded templates carry the tag that their effectiveness is a hypothesis `[H]` and no copy claims otherwise.
- [ ] The state-machine tests are table-driven from S0.9 so a change to the machine tables fails the build until tests follow.
- [ ] No code path creates a job without calling the policy evaluator and the gate library.

### BM6 `execution_and_verification`

| Row | Content |
| --- | --- |
| Scope | `S5.*`, `S8.*`, `S9.*`: the full `Cell` machine and `Lease` and `Submission` machines (S0.9.3); cell offer endpoint that applies `R8` and the adapter capability of `BM3`; leasing with server-issued nonce (`lease.nonce_bytes`), timeout, extension, decline and release (`lease.*`), the reaper job (`lease.reap_interval_s`), paste-back with size limits (`cell.envelope.max_submission_bytes`), schema validation, escaping rules, never executing content, quarantine of outputs with links, code or requests for action, duplicate-submission replay returning the stored outcome. Verification: automatic checks in a pipeline, `GoldCell` library and insertion at `verify.gold_rate_g` (hidden: same shape as primary cells), `Audit` machine with sampling at `verify.audit_rate_s`, comparator and third execution, adaptive sampling with the floor, blanket redundancy for new donors (`verify.new_donor_blanket_cells`) and high-risk templates, donor reliability estimate (Beta prior `verify.reliability_prior_a`, `verify.reliability_prior_b`, window `verify.reliability_window_obs`) and the false-accept and false-reject estimators with their stated limits, timing and duplicate detection, human-review cells (`cell_kind` `review`, own gold cells, behind `ff.channel.human_review`), `rework` cells and `cell.overturned` with ledger reversal. Trust tiers: promotion, demotion, restriction (`trust.*`). Commons minting at acceptance: exactly 1,000,000 `ucr` per accepted cell of any `cell_kind` (`ISS-03`), under `mint.monthly_cap_credits`, `mint.per_member_daily_cap_credits`, `launch.minting_enabled` and `kill.all_minting`. Expiry-arm resolver for lot lifetimes (`ff.experiment.expiry_arm`). `Report`, `Appeal` (all `appeal_kind` values) and ban processes with the reviewer-is-not-the-decider rule; template auto-pause (`template.autopause_report_count`, `template.autopause_window_s`); service revocation effect on in-flight cells (`cell.voided`, `lease.revoked`); `R9` re-check at acceptance; queues for audits, abuse flags and appeals in the console; the `human_review` template; a scripted test donor built on the client SDK that supplies pre-written outputs and never touches any provider |
| Entities | `Lease`, `Submission`, `VerificationRecord`, `GoldCell`, `Audit`, `Report`, `Appeal`; `Cell` completed; `Member` trust tier fed |
| Endpoints | `POST /v1/cells/{cell_id}/leases`, `POST /v1/leases/{lease_id}/submission` (S0.11.1), cell-offer, my-leases, reports, appeals, decline and release; admin: audits, gold-cells, reports, appeals, bans, verification-records (`S15.*`) |
| Depends on | `BM1`, `BM5` (and through them `BM0`..`BM4`) |
| Stubbed | No UI for volunteers (scripted donor only); no member jobs, so no payout or settlement and no requester; starter grant, per-member cap K and expiry sweeps are `BM7`; notifications absent; share, teams and referral absent |
| Working system | A test donor drives a Commons cell from `Cell.queued` to `Cell.accepted` and the ledger mints exactly 1,000,000 `ucr`; replay, forgery and leasing-race suites pass |
| Demo | The scripted donor works a batch that includes a gold cell and an audited cell; a forged and a replayed submission are refused; a reviewer overturns a rejection on appeal; the ledger explorer shows the mints and the invariants stay green |

**Acceptance tests (BM6)**

- `AC-bm6-01` Given default parameters, When a lease is requested, Then `403 LAUNCH_GATE_CLOSED` while `launch.members_may_join` is false; and with minting off no `mint` entry is posted on acceptance (behavior per `S6.*`).
- `AC-bm6-02` Given one `queued` cell and many concurrent lease requests, When run, Then exactly one `Lease` is `active`, the rest get `409 LEASE_CONFLICT`, and the cell is `leased` once.
- `AC-bm6-03` Given an expired lease, When the reaper runs, Then `lease.expired` and `cell.lease_expired` are emitted and the cell is requeued with `attempt + 1`; at `cell.max_attempts` it becomes `exhausted`; a submission inside `lease.submit_grace_s` on a not-yet-re-leased cell is accepted.
- `AC-bm6-04` Given a submission with a missing, wrong, or another lease's nonce, or from a member who does not hold the lease, Then `410 LEASE_EXPIRED` or `reject.nonce_invalid` and nothing is accepted; guessing is rate-limited (`ratelimit.member_submissions_per_hour`).
- `AC-bm6-05` Given a repeated submission for the same lease and nonce, Then the stored outcome is returned and no event is emitted a second time.
- `AC-bm6-06` Given a submission over `cell.envelope.max_submission_bytes`, Then `413 PAYLOAD_TOO_LARGE`; given invalid schema, Then `reject.schema_invalid` and the cell requeues.
- `AC-bm6-07` Given an output containing a link, script-like text or an instruction to act, Then `submission.quarantined`, it is withheld from every result, and a reviewer can release it (`submission.released_from_quarantine`).
- `AC-bm6-08` Given gold insertion, When a cell is offered, Then the response schema of a gold cell equals that of a primary cell (no `cell_kind` leak); with a seeded generator the observed insertion rate converges on `verify.gold_rate_g` within the test's stated tolerance; gold answers are unreadable by the application role outside the verifier.
- `AC-bm6-09` Given `trust.restrict_after_gold_fails` consecutive gold failures, Then `member.restricted`, sampling rises per `trust.audit_multiplier.restricted` and caps fall per `trust.cap_multiplier.restricted`; after `trust.restriction_days`, `member.restriction_lifted` returns the recorded tier.
- `AC-bm6-10` Given an audit, When the second output matches by the template comparator, Then `audit.matched`; When it mismatches, Then a third execution is requested (`verify.third_exec_on_mismatch`) and `audit.resolved` decides both cells.
- `AC-bm6-11` Given adaptive sampling, When `verify.adapt.clean_streak` clean observations occur, Then the rate steps down by `verify.adapt.step_down_ratio` but never below `verify.audit_rate_floor`; on a failure it steps up by `verify.adapt.step_up_ratio` but never above `verify.audit_rate_max`.
- `AC-bm6-12` Given a new donor, Then their first `verify.new_donor_blanket_cells` cells use `blanket_redundancy` with `verify.blanket_redundancy_n` executions; the same applies to a template marked high-risk.
- `AC-bm6-13` Given a known sequence of gold and audit outcomes, Then the reliability estimate equals the Beta posterior computed by hand in the test, restricted to the last `verify.reliability_window_obs` observations.
- `AC-bm6-14` Given synthetic observations, Then the false-accept and false-reject estimators return their values and carry the documented limits (sample size, bias of audit-only evidence); no estimate is displayed as a finding.
- `AC-bm6-15` Given a submission faster than `verify.timing_min_s` or with similarity to another donor's output above `verify.duplicate_similarity_threshold`, Then `reject.timing_anomaly` or `reject.duplicate_of_other_output` and the cell is flagged for audit.
- `AC-bm6-16` Given `ff.channel.human_review` on, Then review cells are offered with their own gold share (`verify.human_review_gold_rate`) and a review rate of `verify.human_review_rate`; with the flag off no review cell exists.
- `AC-bm6-17` Given an accepted cell that is overturned, Then `cell.overturned`, a ledger `reversal` with two approvers, and a `rework` cell is created and counted toward v.
- `AC-bm6-18` Given acceptance of a Commons cell of any `cell_kind`, Then one `mint` of exactly 1,000,000 `ucr` and one new lot; at `mint.monthly_cap_credits` or `mint.per_member_daily_cap_credits` no further mint is posted and `inflation.mint_utilization_alarm` raises an alarm at its threshold.
- `AC-bm6-19` Given `ff.experiment.expiry_arm` on and a member assigned to the accelerated arm, Then new lots carry `credit.lifetime_days_accelerated`; otherwise `credit.lifetime_days`.
- `AC-bm6-20` Given a property test over members, opt-ins and cells, Then a cell is never offered to a member whose opt-ins do not cover it (`R8`); Given a tightened policy at acceptance, Then `reject.policy_changed` (`R9`).
- `AC-bm6-21` Given a service revoked while cells are in flight, Then leases are revoked, cells `voided`, nothing is minted for them, and events are emitted (`S7.*`).
- `AC-bm6-22` Given an appeal, Then the assigned reviewer is not the original decider, filing after `appeal.window_days` is refused, a ban needs `appeal.ban_min_reviewers`, and an overturn triggers the appropriate reversal.
- `AC-bm6-23` Given `template.autopause_report_count` reports on one template inside `template.autopause_window_s`, Then `template.paused` and its cells pause.
- `AC-bm6-24` Given submitted text containing markup, script and control characters, Then it is stored as data, returned only as `application/json`, never executed or interpreted, and every console view escapes it (injection and XSS suite `T-inj-*`).
- `AC-bm6-25` Given the adversarial suite `T-adv-*` (forgery, replay, double submission, race between lease, requeue and cancel), Then every case ends in a valid state, the ledger invariants hold and no credit is minted that is not backed by an accepted cell.

**Definition of Done (BM6)** adds to 17.5.3:

- [ ] The statement of exact guarantees for leasing, submission and idempotency in `S5.*` is verified one by one by a test.
- [ ] Every rejection reason of S0.8.4 that this milestone can produce has a test.
- [ ] The estimation limits of `S8.*` appear in the console help text and in the operator runbook.
- [ ] The scripted donor and its fixtures are marked as test code and are excluded from production artifacts.
- [ ] Second human signature on the DoD record (`BR10`).

### BM7 `member_jobs_and_credit_economy`

| Row | Content |
| --- | --- |
| Scope | `S6.*`: requester-side job creation (draft, upload, declarations, policy result), price quote `p_ucr = 1,000,000 + v_ppm + lambda_ppm` with v measured per job type over `price.v_window_days` (fallback to `price.v_prior` below `price.v_min_sample_cells`, capped by `price.v_cap`, rounded by `price.v_rounding`), quote lifetime `price.quote_ttl_s`, escrow hold at confirmation, admission control (capacity forecast from verified throughput and active donors over `admission.forecast_window_days` and `admission.active_donor_window_days`, `admission.phi`, `admission.forecast_haircut`, window quote within `admission.min_window_s`..`admission.max_window_days`, waitlist, fairness caps `admission.max_concurrent_jobs_per_member` and `admission.waitlist_*`), capacity reservations behind `ff.job.reservations` (`reservation.*`), the member `Job` machine in full (S0.9.2), payout per accepted cell (`transfer`, `payout` transaction), settlement (levy to the Reserve, refund of the remainder, escrow closed at zero), cancellation, overrun handling (`job.max_overrun_ratio`), `Deliverable` and `Manifest` (provenance, FD§5.6) with results download and requester rating, expiry sweeps (`credit.expiry_sweep_interval_s`, notices at `credit.expiry_notice_days`), Reserve inflow and retirement (`reserve.*`), starter grant (`grant.*`, non-transferable) with anti-farming limits, referral bonus ledger operation funded from the Reserve (`ISS-06`), per-member cap K (`credit.member_cap_credits` times `trust.cap_multiplier.*`), claim ratio and eta publication as `MetricSnapshot` every `price.publish_period_days`, inflation gauges and the automatic response of `inflation.*`, recovery-cooldown enforcement on spend and job start, capacity and economy dashboards (`SCR-ops`) |
| Entities | `Escrow` and `Reserve` wired to jobs, `Reservation`, `Deliverable`, `Manifest`, `WaitlistEntry`, `MetricSnapshot`, `Referral` (data and ledger side) |
| Endpoints | Member surface: jobs (create, upload, evaluate, quote, confirm, cancellation), quotes, results, ratings, balance, lots, reservations, waitlist; public read: counter inputs only; admin: capacity, economy, reserve, grants (`S15.*`) |
| Depends on | `BM6` |
| Stubbed | No requester wizard screens (SDK-driven requester); no public pages; referral and share mechanics have no UI; `deadline_class` and `size_class` have the single value `standard` (S0.8.6); notifications absent |
| Working system | A member job runs from request to settlement; the closing identity holds; the FD§3.3 example passes end to end |
| Demo | The scripted requester posts the 240-cell job, watches admission, payouts and settlement, cancels a second job midway, and the explorer shows levy, refund, expiry and retirement entries with invariants green |

**Acceptance tests (BM7)**

- `AC-bm7-01` Given default parameters, When a job is confirmed, Then `403 LAUNCH_GATE_CLOSED` while `launch.member_jobs_enabled` is false.
- `AC-bm7-02` Given the inputs of S0.6.1 (`v_ppm` 100,000, `lambda_ppm` 50,000, N = 240, balance 300 credits, 40 donors, 8 cells a day, `admission.phi` 0.5, 2-day window), When the job runs end to end, Then price 1,150,000 `ucr`, escrow 276,000,000, verification pool 24,000,000 (24 cells), levy 12,000,000, donor payout 264,000,000, refund 0, `eta_ppm` 869,565, capacity 320 cells against 264 committed, and the requester keeps 24 credits (`AC-ledger-01` extended to the whole flow).
- `AC-bm7-03` Given verification cells in the trailing window, When v is measured, Then it equals `ceil(10^6 * verification_cells / accepted_primary_cells)` ppm; below `price.v_min_sample_cells` the prior is used; the result never exceeds `price.v_cap`; the publication is versioned and the old value stays readable.
- `AC-bm7-04` Given committed cells that would exceed `phi * forecast capacity` over the window, When a quote is requested, Then the job is `waitlisted` with a re-quote path, never over-admitted; a member at `admission.max_concurrent_jobs_per_member` is refused with `NO_CAPACITY` or `CAP_EXCEEDED` as `S6.*` specifies.
- `AC-bm7-05` Given random capacities, jobs and arrivals (property test `T-prop-*`), Then at every instant committed cells never exceed the admitted share of forecast capacity and waitlist order is first come first served.
- `AC-bm7-06` Given a balance below the escrow, Then `422 INSUFFICIENT_CREDIT`; given a hold that would break the cap, Then `422 CAP_EXCEEDED`; given two confirmations with different idempotency keys, Then exactly one `escrow_hold` exists for the job.
- `AC-bm7-07` Given an accepted cell of a member job, Then one `transfer` of exactly 1,000,000 `ucr` is paid to the donor at acceptance (`ISS-09`) and creates a lot.
- `AC-bm7-08` Given a cancel in `running`, Then unstarted cells are refunded, in-flight cells drain, accepted cells stay paid, the escrow is exactly zero and the job is `cancelled` with `job.cancel_settled`.
- `AC-bm7-09` Given a job that cannot finish, When `job.max_overrun_ratio` of the quoted window passes or a stop is requested, Then `job.settled_partial` leaves state `failed` with payouts and refunds posted and a zero escrow.
- `AC-bm7-10` Given concurrent cancel, settlement and acceptance on one job, Then the outcome equals some serial order, no cell is paid twice or not at all, and the invariants hold.
- `AC-bm7-11` Given lots near expiry, Then the notice is created `credit.expiry_notice_days` before; the sweep posts `expire` to the Reserve; a restored lot already past expiry moves at the next sweep (`ISS-07`).
- `AC-bm7-12` Given a Reserve above `reserve.ceiling_credits`, Then `retire` posts the excess only when it is at least `reserve.retire_min_credits`.
- `AC-bm7-13` Given a newcomer with `grant.required_verified_cells` verified cells, Then one `grant` of `grant.starter_credits` with lifetime `grant.starter_lifetime_days`; a second grant to the same device, more than `grant.max_per_invite_tree_per_day` in one tree, more than `grant.max_per_day` overall, or a Reserve at or below `grant.reserve_floor_credits`, Then the grant is refused or paused; the credit cannot be transferred.
- `AC-bm7-14` Given a member at `credit.member_cap_credits` times their tier multiplier, Then further credit is handled as `S6.*` specifies and never breaks an invariant.
- `AC-bm7-15` Given the publication period, Then eta, v, lambda and the claim ratio are published as a `MetricSnapshot`; when the claim ratio passes `inflation.claim_ratio_threshold_weeks`, Then the mint cap is cut by `inflation.mint_cap_cut_ratio` as an immediate tightening with a public change-log entry; when `eta` falls below `price.eta_alarm_threshold`, Then an alarm is raised.
- `AC-bm7-16` Given `ff.job.reservations` on, Then escrow is held at booking, activation posts `escrow_release`, cancellation inside `reservation.free_cancel_notice_s` is free, and one member's reservations never exceed `reservation.capacity_share_cap` of a day's capacity.
- `AC-bm7-17` Given a manifest, Then it is hashed over canonical JSON, immutable after assembly, lists job, template version, policy version, service, verification summary and input and output hashes, and holds no `mem_` id and no volunteer handle except where `S9.*` and `S12.*` allow.
- `AC-bm7-18` Given a recovered identity inside `identity.recovery_cooldown_s`, Then job start and spending return `403 FORBIDDEN` with the cooldown copy key.
- `AC-bm7-19` Given an expired quote (`price.quote_ttl_s`), Then confirmation is refused and the job is `quote_expired`.

**Definition of Done (BM7)** adds to 17.5.3:

- [ ] The worked example of S0.6.1 is a permanent regression test at three levels: unit (`T-unit-01`), ledger (`AC-ledger-01`) and whole flow (`AC-bm7-02`).
- [ ] Every ledger entry type of S0.8.5 has been produced by at least one acceptance test and checked by the invariants.
- [ ] The admission-control property tests use the harness built in `BM1`.
- [ ] Dashboards show v, eta, claim ratio, mint utilization and Reserve balance from the published snapshots, not from ad hoc queries.
- [ ] Second human signature on the DoD record (`BR10`).

### BM8 `experiences_and_public`

| Row | Content |
| --- | --- |
| Scope | `S11.*` and `S12.*`. Volunteer web app, no install, mobile first: landing, first-contribution flow (the sub-60-second path is a hypothesis `[H]`, measured not asserted), cell card (purpose, license, sensitivity, service, template, expected time, one-sentence provenance line, expandable full prompt, mandatory expansion per `ui.card.expand_required_first_use`, decline and report), copy and open-in-service buttons through the service-adapter layer (prefill where the registry says supported and `prefilled_link_use` is `yes`, copy-only otherwise), paste-back, result feedback, balance and expiry view, history, opt-in settings, teams, share card, invite flow, recovery-key handling, appeals, help. Requester screens: wizard (template choice, upload and screening, declarations, policy result, quote and window, escrow confirmation), progress map per cell, cancellation, results download with manifest, rating. Reviewer and Operator screens completed in both locales (`ISS-174`). Persian first: full RTL, Persian numerals option (`i18n.digits_default_fa`), Jalali and Gregorian dates (`i18n.dual_calendar_detail`), bidi isolation of mixed-direction text in prompts and outputs, bundled fonts (no third-party font), accessibility, low-bandwidth behavior. Copy for every policy, privacy and risk notice in `fa` and `en`, each key marked `needs_human_and_legal_review`, every promise worded "declared". Informed, explicit opt-in of Phase 1 participants about the account risks of gate `G0` (FD§9) as a required screen. Public surfaces: live counter (verified cells only), public ledger and parameter pages, change log, milestone pages. Share cards without personal data or location, teams (opt-in only), referral with the two-sided bonus, growth mechanics `V1`..`V6` behind `ff.growth.*` with logged randomized assignment. Capacity map and bottleneck view wrapped from the panel concept per the PB-1 record (17.4.1) |
| Entities | `Team`, `Badge`, `BadgeAward`, `Referral` (UI and rules), `MetricSnapshot` read models; no new money entity |
| Endpoints | Member: teams, badges, referrals, share-cards, notices, feedback; public: counter, ledger, parameters, change-log, milestones, capacity (`S15.*`) |
| Depends on | `BM6`, `BM7` |
| Stubbed | Real prefill behavior for any named service stays registry data `[V]`; analytics dashboards are `BM9`; the legal and linguistic review of copy is a human step recorded as pending, never skipped silently |
| Working system | A new member completes the first-contribution flow and a requester completes the wizard in both locales (rehearsal); accessibility and low-bandwidth checks pass |
| Demo | Phone-sized walkthrough in `fa` and `en`: landing, consent, first contribution with copy-only and with a fictitious prefill service, balance and expiry in both calendars, requester wizard to a quote, public pages |

**Acceptance tests (BM8)**

- `AC-bm8-01` Given a new member in `ci` (gate opened by the real flow with fixtures) on a phone-sized viewport, When the first-contribution flow is completed, Then it passes only through the screens listed in `S11.*`, requires no field beyond the declared ones, and emits timing events; the share under `ui.fast_contribution_threshold_s` is reported as a measurement `[H]`, not asserted.
- `AC-bm8-02` Given a cell card, Then it shows purpose, license, sensitivity, service, template, expected time, the provenance line and the collapsed full prompt; on first use the prompt must be expanded before copy is enabled; decline and report are present.
- `AC-bm8-03` Given a service whose adapter has `supports_prefill` and `prefilled_link_use` = `yes`, Then an open-in-service control is shown; otherwise only copy; in both cases no control sends, submits or reads anything on the provider's side and no field accepts provider credentials or page content (`BR9`).
- `AC-bm8-04` Given pasted text containing markup, right-to-left and left-to-right runs, code and control characters, Then it is escaped, bidi-isolated and displayed without reordering damage (`T-rtl-*`).
- `AC-bm8-05` Given the recovery-key screen, Then the key is shown once, a confirmation is required, and a network log of the flow contains no recovery key.
- `AC-bm8-06` Given the `fa` locale, Then the layout is mirrored with logical properties, numerals follow the member's setting, a table of known dates converts correctly between Gregorian and Jalali with the bundled fallback, and detail views show both calendars (platform calendar support `[V]`).
- `AC-bm8-07` Given the copy registry, When linted, Then every `copy.*` key has `fa` and `en` text and the marker `needs_human_and_legal_review`, and no key promises with the words "guarantee" or its Persian equivalent; promises use "declared".
- `AC-bm8-08` Given each screen, Then automated accessibility checks pass, every action is reachable by keyboard, text resizing and reduced motion are honored, and the manual checklist of `S18.*` is filed.
- `AC-bm8-09` Given a throttled network profile and no third-party hosts, Then the first-contribution flow completes with only the project's own assets and bundled fonts (`BR8`); degradation follows `S11.*`.
- `AC-bm8-10` Given the requester wizard, When a declaration is rejected, Then the plain-language copy for `policy.<rule>.<slug>` is shown; When accepted, Then the quote shows price, window and escrow; the progress map shows one status per cell; cancellation and download with manifest work; a rating can be submitted once.
- `AC-bm8-11` Given each Reviewer and Operator screen, Then it is complete in `fa` and `en`, permission-gated by the matrix and shows no volunteer identifier beyond what its task needs.
- `AC-bm8-12` Given pending, rejected and accepted cells, Then the public counter counts verified cells only and refreshes within `public.counter_refresh_s`; the public ledger page trails the ledger by `public.ledger_lag_s`; a scan of every public response finds no `mem_` id, IP address or location.
- `AC-bm8-13` Given a share card, Then it holds no personal data and no location while `public.location_display` is `never`.
- `AC-bm8-14` Given teams, Then they are opt-in, need `team.create_min_tier`, hold at most `team.max_members`, and are not shown publicly below `team.min_public_members`.
- `AC-bm8-15` Given a referral, Then the bonus is posted as a `grant` from the Reserve only after the newcomer has `growth.referral.min_newcomer_verified_cells`, after `growth.referral.hold_s`, within `growth.referral.max_per_referrer_per_30d`, and never when the Reserve is at its floor; a scripted self-referral loop earns nothing.
- `AC-bm8-16` Given each of `ff.growth.v1_fast_path` .. `ff.growth.v6_milestones`, Then it is off by default; when on, assignment is randomized, logged and instrumented; when off again no residue changes behavior.
- `AC-bm8-17` Given the notices of `S11.*`, Then the policy, privacy and risk notices exist in both languages, and the Phase 1 opt-in screen must be accepted before the first contribution.
- `AC-bm8-18` Given the capacity map, Then it renders from the Hamyar API without any external font or script and shows the bottleneck as the PB-1 record specifies.

**Definition of Done (BM8)** adds to 17.5.3:

- [ ] A Persian reader has reviewed all `fa` strings and a lawyer has the notice texts for review `[V]`; the status of both is recorded in `build/dod/BM8.md` and no string is presented as final.
- [ ] The flows were tried on real phones and desktops for gate `G2` (clipboard flow, URL length, copy-and-paste error rate) with the results stored as gate evidence `[V]`.
- [ ] The bundle contains no font or script request to a third party and Persian glyph coverage is verified.

### BM9 `measurement_simulation_hardening`

| Row | Content |
| --- | --- |
| Scope | `S13.*`: event schema and the metrics pipeline (outbox events and client timing events to `Event`, rollups every `metrics.rollup_interval_s`, `MetricSnapshot`), aggregate-only analytics (`analytics.min_cohort_k`, `analytics.third_party_trackers` and `analytics.cookies_enabled` constant `false`, `retention.event_raw_days`), a query for every FD§9 Phase 1 measure (table below), arm analysis for the accelerated-expiry experiment, the pre-registration lock verified before launch. `S18.*`: the simulation harness (synthetic honest, lazy, farming, forging, colluding and run-on-the-bank agents, bursts; driven through the real API on a simulated clock; seedable; scenario catalog; parameter sweeps), load suite, end-to-end suite, adversarial and chaos suites. Drills: restore from backup, secret rotation, kill switches, key-handle rotation. Hardening: threat-model coverage (each `THR-<nn>` has a test or a documented residual), dependency audit `[V]`, a human penetration test `[V]`, alert tuning, runbooks. Closure of the pre-build checklist of `S19.*`. Host-bound bindings for every port (`BR4`) once the owner has chosen them (`S3.*`) |
| Entities | `Event`, `MetricSnapshot`, `ExperimentAssignment` (analysis), `InvariantCheck` history |
| Endpoints | Admin: metrics, experiments (results), simulation reports (read), drills log; public: none new |
| Depends on | `BM7`, `BM8` |
| Stubbed | Nothing may remain bound in a production configuration. A port whose real provider the owner has not chosen (mail, alerting, host, object bytes) is reported as an open owner decision with a contract-tested candidate binding, never silently stubbed |
| Working system | Every FD§9 Phase 1 measure has a query that returns a value on a simulated dataset; simulation reports carry the label "not evidence about human behavior"; the drills are logged |
| Demo | Run the pilot-like simulation scenario and show the measures; run the run-on-the-bank scenario and show admission, the claim-ratio alarm and green invariants; restore a backup; rotate a key |

FD§9 Phase 1 measures and their sources (metric names and queries are owned by `S13.*`; event names are those of S0.9) [D]:

| FD§9 measure | Source events and tables |
| --- | --- |
| Deposit-to-withdrawal ratio, weekly (cells contributed ÷ cells requested) | `cell.checks_passed` / `audit.resolved` for Commons and member cells; `job.escrow_confirmed` cell counts |
| Time to complete a large job versus quote | `job.escrow_confirmed`, `job.all_cells_accepted`, the stored quote window |
| Rejection rate overall and by template; false-reject rate from gold; false-accept estimate from audits | `cell.checks_failed`, `VerificationRecord` (`gold`, `audit_second`, `audit_third`), template id |
| v and the implied eta | `MetricSnapshot` from `BM7` |
| Week-2 and week-4 return | `member.created`, `lease.issued` by cohort (suppressed below `analytics.min_cohort_k`) |
| Median time per contribution, share under `ui.fast_contribution_threshold_s`, time to first verified cell | `lease.issued`, `submission.received`, `cell.checks_passed`, client timing events |
| Active capacity per member per day; concentration (share of cells from the top 10% of donors) | `cell.checks_passed` per member, aggregated |
| Decline and opt-out rates by category | `cell.declined`, `member.optin_changed` |
| Incidents: policy violations, injection attempts, abuse flags, provider warnings or account problems | `submission.quarantined`, `report.filed`, screening queue, operator incident entries |
| Qualitative interviews | Outside the system `[P]`; only their summary is attached to the decision record |

**Acceptance tests (BM9)**

- `AC-bm9-01` Given the pilot-like simulation scenario, When the rollup runs, Then every row of the table above returns a value, with cohorts smaller than `analytics.min_cohort_k` suppressed.
- `AC-bm9-02` Given any simulation output (report, chart data, CSV, log), Then it carries the label "Simulation output is not evidence about real human behavior" and a seed; no simulated figure appears on any public page or in a `MetricSnapshot`.
- `AC-bm9-03` Given the run-on-the-bank scenario (members try to redeem more than forecast capacity), Then admission waitlists or refuses, no escrow is under-funded, the claim-ratio gauge raises its alarm at `inflation.claim_ratio_threshold_weeks`, and all invariants hold throughout.
- `AC-bm9-04` Given the credit-expiry scenario over simulated weeks, Then lots expire to the Reserve, the Reserve retires its excess, conservation holds, and the accelerated arm's lots expire after `credit.lifetime_days_accelerated`.
- `AC-bm9-05` Given adversarial agents (forgers, replayers, farmers, colluders, malicious requesters), Then no credit is minted without an accepted cell, farming stays inside the `grant.*` and `invite.*` limits, and every attack ends in a valid state; detection rates are reported with the simulation label, never as a pass criterion about humans.
- `AC-bm9-06` Given the load suite of `S18.*` at its recorded targets `[V]`, Then the lease, submission, quote and settlement paths meet them without invariant violations and without double payment.
- `AC-bm9-07` Given the chaos suite (process kill during settlement, database failover, duplicated outbox delivery), Then every operation either completes or is safely retried with the same effect.
- `AC-bm9-08` Given a backup, When restored into an empty environment, Then ledger invariants pass from the last checkpoint, public counters equal the ledger, and the measured recovery time and data-loss window are recorded against targets set by the owner `[V]`.
- `AC-bm9-09` Given the rotation drill on `staging`, When each secret class is rotated, Then there is no outage, old values are refused, member sessions behave as `S10.*` specifies, rotating `secret.volunteer_handle_key` unlinks old handles by design, and the record (names, dates, performer, no values) is stored as gate evidence.
- `AC-bm9-10` Given the pre-registration, Then it is locked, and the launch rule of `S14.*` refuses to turn on `launch.members_may_join` while it is unlocked.
- `AC-bm9-11` Given analytics, Then no third-party tracker or cookie exists (network log and headers), and no aggregate query can return a cohort below `analytics.min_cohort_k`.
- `AC-bm9-12` Given the threat-model table of `S10.*`, Then every `THR-<nn>` row maps to at least one test of `T-adv`, `T-inj` or `T-sim` or to a documented residual risk, and the mapping is a checked file.
- `AC-bm9-13` Given the pre-build checklist of `S19.*`, Then every item has a status and an evidence pointer; open items are `[V]` with a named owner.
- `AC-bm9-14` Given the full end-to-end suite on `staging` (rehearsal), When a new member contributes, a requester posts a job, it settles and the manifest is downloaded, in both locales, Then every step passes and the recorded network log meets `BR8`.
- `AC-bm9-15` Given production configuration validation, Then no stub is bound, the fixture profile and rehearsal sign-offs are refused, and `launch.*` are `false`.

**Definition of Done (BM9)** adds to 17.5.3:

- [ ] All five drills are logged: restore, secret rotation, kill switches, key-handle rotation, and a full gate walk-through on `staging` with rehearsal sign-offs.
- [ ] Every open `[V]` of this part and of `S19.*` has an owner and a place where its answer will be stored.
- [ ] Completion of `BM9` is recorded as a build fact only; the statement "this authorizes no launch" is part of the record (`BR10`, S0.12 rule 6).
- [ ] Second human signature on the DoD record (`BR10`).

## 17.7 Launch gates versus build milestones

Building and launching are separate tracks. The build supplies the machinery and the evidence slots; humans supply the answers. Gates `G0`..`G5` are defined in FD§8.3 and specified as product features in `S14.*`. [D]

| Gate | What must be true (FD§8.3) | Machinery built in | Evidence a human enters | Effect on the build |
| --- | --- | --- | --- | --- |
| `G0` terms and law | A dated `ServiceRegistryEntry` per candidate service with saved terms copy and flags `(a)`..`(k)`; counsel answers `[V]` | `BM2` (checklist), `BM3` (registry, flags, terms copies, review machine) | Flags, terms copies, counsel memo reference | None: nothing in the build depends on a particular provider; fictitious services stand in |
| `G1` safety | Written threat model, logging and retention decisions, member notice | `BM2` (checklist), `BM0`/`BM4` (scrubber, retention), `BM8` (notices) | Threat-model decision, notice review | Retention and logging defaults are parameters; exposure rule 17.5.2 |
| `G2` technical feasibility | Prefill and URL limits, clipboard flow, copy-paste error rate, result path, reachability from Iran, Persian RTL on real devices | `BM0` (probe), `BM3` (adapter fields), `BM8` (flows) | Device test results, probe results | Adapter capabilities are data; copy-only is always available |
| `G3` calibration | Cells per day per service, seconds per cell, refusal and failure rates, copy-paste error rate | `BM2` (`CalibrationRecord` tool) | Calibration records (`CAL`) | Defaults stay until a human edits a parameter citing the records |
| `G4` repo review | Code and docs of the panel read; the four secrets audited | PB-1 and PB-3 (17.4), `BM2` (evidence slot) | Decision record, rotation record | Decides keep, wrap, replace |
| `G5` demand check | Interviews on real jobs, splittability, acceptable windows | `BM2` (evidence slot) | Interview summary (`DEM`) | Informs `admission.*`, `credit.member_cap_credits`, `admission.max_job_cells` |

**Exit rule versus the build-everything instruction** [D]. FD§8.3 says building beyond a throwaway prototype starts only when `G0` yields at least one approved service (or a documented fallback) and `G1` is complete. The brief instructs the opposite for construction: build the full system, and launch only through the gates. This plan reads the FD exit rule as governing launch (`launch.required_gate_ids` defaults to `G0`, `G1`; `launch.min_approved_services` to 1) and construction as proceeding under the owner's instruction. The cost is that effort is at risk if no service clears `G0` (`ISS-171`, `needs_owner`). The built system already supports every FD§8.3 fallback without a rebuild: (i) written permission is recorded with `info.written_permission` and a saved terms copy; (ii) open-weight models run through service requirement `M2` and registry entries for those services; (iii) a human-review-only commons runs on `cell_kind` `review` and the `human_review` template behind `ff.channel.human_review` (`BM6`); (iv) stopping leaves a working, closed system [H].

**Reachability probe** (`BM0`, evidence in `BM2`) [A][V]. A static page and a static JSON file, no data, no secrets, no third-party resource, deployed to each candidate host. Testers record whether it loads from their vantage points and when; the record is attached to gate `G2`. The probe measures reachability only. It does not provide, test or recommend any way around a restriction, and nothing in the build does (ground rule 3).

## 17.8 Migration and seed order (fresh database)

### 17.8.1 Migration numbering [D]

Migration number `= 100 * n + 10 * j + i`, where `n` is the milestone index, `j` in `1..9` is the work package index inside the milestone (`WP-BM<n>-<jj>`) and `i` in `0..9` is the sequence inside the package. Migrations apply in ascending number. Two work packages therefore never collide, and ordering inside a milestone follows package order only where a dependency says so. A milestone has at most nine work packages (17.9).

Tables are created in this order (each group is one or more migrations of its milestone; a table appears once):

| Milestone | Tables created (S0.7 names) |
| --- | --- |
| `BM0` | `parameters`, `parameter_versions`, `change_log_entries`, `events`, outbox, idempotency store |
| `BM1` | `ledger_accounts`, `ledger_transactions`, `ledger_entries`, `credit_lots`, `escrows`, `reserves`, checkpoint rows (`S6.*`), `invariant_checks`, `alarms` |
| `BM2` | `admin_users`, `admin_credentials`, `sessions` (admin rows), `admin_actions`, `kill_switches`, `feature_flags`, `experiments`, `experiment_assignments`, `pre_registrations`, `launch_gate_items`, `calibration_records` |
| `BM3` | `service_registry_entries`, `terms_copies`, `flag_answers`, `policies`, `policy_versions`, `rules`, `topic_categories`, `opt_ins` |
| `BM4` | `members`, `member_keys`, `devices`, `invites`; `sessions` extended with member rows (relaxation of the principal check, expand-only) |
| `BM5` | `templates`, `template_versions`, `jobs`, `cells`, `uploads`, `glossaries` |
| `BM6` | `leases`, `submissions`, `verification_records`, `gold_cells`, `audits`, `reports`, `appeals` |
| `BM7` | `reservations`, `deliverables`, `manifests`, `waitlist_entries`, `metric_snapshots`, `referrals` |
| `BM8` | `teams`, `badges`, `badge_awards` |
| `BM9` | Rollup tables and indexes for metrics (`S13.*`); no new domain entity |

**Deferred foreign keys** (`ISS-176`) [D]. A table that points at an entity of a later milestone stores the opaque id first; the constraint is added, validated, by the milestone that creates the target. There is no data to backfill in a fresh database; in an upgraded database the validation step fails the migration if an orphan exists.

| Column | Target | Added by |
| --- | --- | --- |
| `ledger_accounts.member_id` (member accounts) | `members` | `BM4` |
| `opt_ins.member_id` | `members` | `BM4` |
| `calibration_records.service_id` (nullable link next to `service_key`) | `service_registry_entries` | `BM3` |
| `escrows.job_id` | `jobs` | `BM5` |
| `escrows.reservation_id` | `reservations` | `BM7` |
| `cells.template_version_id`, `jobs.template_version_id`, `jobs.policy_version_id` | `template_versions`, `policy_versions` | created with their tables (`BM5`) |

### 17.8.2 Seed order [D]

Seeds are idempotent scripts run after the migrations in this order. The reason for the order is in the last column: a seed never refers to something a later seed creates.

| Order | Seed | Milestone | Why here |
| --- | --- | --- | --- |
| 1 | Every parameter of S0.10.6 / `S16.*`: `Parameter` row and `ParameterVersion` 1 equal to the default, `effective_from` = seed time; constants immutable | `BM0` | Everything else reads parameters |
| 2 | Genesis `ChangeLogEntry` stating that the initial parameters were published | `BM0` | The public log starts at the first values [A] |
| 3 | Ledger singletons: `issuance`, `retired`, `reserve` accounts, the `Reserve` row, the chain anchor of `S6.*`; all balances zero | `BM1` | No member account may exist before the Reserve |
| 4 | Global kill switches `kill.all_minting`, `kill.all_new_jobs` in state `released`; scoped switches are created on first use | `BM2` | Needed by every guard |
| 5 | Feature flags `ff.*` (all off) and the `Experiment` definition of the expiry arm (inactive, fraction from `experiment.expiry_arm.fraction`) | `BM2` | Flags are read by later features |
| 6 | `LaunchGateItem` rows for `G0`..`G5` in state `open` (per-service `G0` items are created with each service entry) | `BM2` | The gate rule needs the checklist |
| 7 | Roles and the permission matrix from the table of `S10.*` | `BM4` | Before any principal exists |
| 8 | `Policy` default profile and `PolicyVersion` 1 with `R1`..`R10` and the allowlist, published with its genesis change-log entry | `BM3` | Templates and jobs validate against it |
| 9 | `TopicCategory` list of `S7.*` | `BM3` | Opt-ins refer to it |
| 10 | Templates: the five required as `draft`; the `human_review` template as `draft` | `BM5`, `BM6` | A seed never approves a template [D] |
| 11 | Badge definitions (criteria in verified cells only) | `BM8` | Referenced by awards |
| 12 | Services: entries read from an owner-supplied file; each `unreviewed`, no flag answered (every flag therefore `unknown`, evaluated as `no`), no adapter value. The repository ships no provider data. Fictitious services exist only in `dev`, `ci` and `staging` fixtures | `BM3` | Registry exists before jobs |
| 13 | No admin (enrolled out of band by the bootstrap command, `AC-bm2-12`), no member, no session, no gold cell, no job, no waitlist entry | all | Closed by default |

**Fixture overlays** (`seed/fixtures/`) create fixture admins, fictitious services, sample templates and the `launch-open` profile; they load only when the environment is `dev` or `ci` (and a marked rehearsal subset in `staging`); the loader refuses in `production` and startup validation fails if any fixture row exists there (`AC-bm9-15`). [D]

**Post-seed closed-state test** (`seed-closed`; part of `GD4`, grows with each milestone) [D]:

| Assertion on a fresh seeded database | Expected |
| --- | --- |
| Services whose state is not `unreviewed` | 0 |
| Launch gate items not `open` | 0 |
| `launch.members_may_join`, `launch.member_jobs_enabled`, `launch.minting_enabled` | all `false` |
| Kill switches engaged | 0 |
| Feature flags on | 0 |
| Members, admin users, sessions, jobs, cells, leases | 0 |
| Templates `approved` | 0 |
| Ledger entries; sum of all account balances | 0; 0 |
| Parameter rows without a `ParameterVersion` 1 equal to the default | 0 |


## 17.9 Work packages for parallel coding agents [A]

A **work package** (`WP-BM<n>-<kk>`, `kk` = `01`..`09`; the same number `j` as in the migration formula of 17.8.1) is the unit of assignment to one coding agent or one human. The shape is borrowed from the cells of the existing panel (small, one owner of a path set, a test command that decides pass or fail, inputs given as contracts, protected shared files; panel-review sections 1, 3 and 8), as a working method only; no panel runtime is reused by this rule (17.4.1). Everything in 17.9 is an assumption [A]: it organizes the build and changes no product behavior. A work-package id never appears in the normative text of another part.

### 17.9.1 Rules, module map, protected files, WP card

**Rules for every work package** [A]

| Rule | Statement |
| --- | --- |
| `WR1` | One WP is one reviewable change set that a single agent can finish in one session. A WP that grows past that is split; a milestone never has more than nine (17.8.1), so a split is first made by merging two small neighbours elsewhere or by moving the extra work to the milestone's last package |
| `WR2` | A WP owns a set of paths (`owns`) and may write only there. CI path rules (`ci/path-rules`) fail a change that touches a path outside the `owns` of the WP named in its branch. Two WPs of the same milestone never own the same path |
| `WR3` | Inputs are contracts, not code: the S-part cited in `needs`, the names of S0, and a mock or fake of every port or neighbour module. A WP never waits for, reads or depends on the implementation of another WP; it codes against the contract and the port's contract test (`BR4`) |
| `WR4` | A WP ends with its acceptance tests green by id (`AC-bm<n>-nn`, `T-*`), the regression manifest updated by append, its stubs registered in `build/stubs.md` and its parameters, flags, copy keys and operations added to the files it owns (`BR7`, `GD5`..`GD10`) |
| `WR5` | A name that is wrong or missing in S0 is not invented or locally varied: the WP files a convention issue against the owning part (S0.1, S0.4) and stops on that point |
| `WR6` | No agent receives or writes a production secret; tests use fixtures and fictitious services; a WP never embeds a provider name, URL template or terms fact (`BR8`, ground rule 2) |
| `WR7` | Merge happens through the CI gate on the head commit that was tested; a WP that needs a change in a protected file asks the file's owner (table below) instead of editing it |
| `WR8` | A WP that adds a screen adds its copy keys in `fa` and `en` (marker `needs_human_and_legal_review`) and no hardcoded string; a milestone before `BM8` may ship `en` only for console screens (`ISS-174`) |

**Module map** (logical directories; the extension, framework and test runner come from `docs/adr/stack-and-host`, PB-2, and no WP imports a framework before that record exists) [A]

| Module | Content | Layer | May import | Built in |
| --- | --- | --- | --- | --- |
| `platform/` | ids, `Money`, `Clock`, hashing and canonical JSON, tokens; error model, idempotency, pagination, rate-limit headers, ETag; config store and validation; outbox and events; log scrubber, metric registry; ports and local bindings; migration runner; the S0 name registries as data | L0 | nothing | `BM0` |
| `ledger/` | accounts, postings, lots, escrow and reserve operations, reversal, invariants, `ledger-cli` | L1 | `platform` | `BM1` |
| `admin/` | admin identity and sessions, admin actions and two-person rule, parameter editor, kill switches, flags, experiments, pre-registrations, launch gates, calibration | L1 | `platform`, `ledger` (read) | `BM2` |
| `registry/` | services, terms copies, flag answers, adapter port and URL builder | L1 | `platform`, `admin` (guards) | `BM3` |
| `policy/` | policy data, evaluator, change workflow, opt-ins and `R8` | L1 | `platform`, `registry` | `BM3` |
| `identity/` | members, keys, sessions, devices, recovery, invites, roles and permissions, trust and status machines, retention | L1 | `platform`, `admin`, `ledger` (account creation port) | `BM4` |
| `templates/` | template model and review, lint, wrapping, seed set, harness | L2 | `platform`, `admin`, `policy`, `registry` | `BM5` |
| `jobs/` | `Job` and `Cell` creation and machines, uploads, glossaries, screening, splitter | L2 | `platform`, `policy`, `registry`, `templates`, `identity` | `BM5`, completed `BM7` |
| `execution/` | leases, submissions, verification, gold, audits, trust inputs, minting at acceptance, reports, appeals | L3 | `platform`, `ledger`, `jobs`, `policy`, `identity`, `templates` | `BM6` |
| `economy/` | pricing, admission, escrow flow, payout, settlement, sweeps, grants, snapshots, reservations, deliverables, manifests | L3 | `platform`, `ledger`, `jobs`, `policy`, `identity` | `BM7` |
| `metrics/` | event schema, rollups, Phase 1 measures, arm analysis | L4 | `platform` and read models | `BM9` |
| `sim/` | simulation harness and agents | L4 | the public API only | `BM9` |
| `api/` | route registration, `x-milestone` manifest, generated operation list, conformance suite | top | every server module | `BM0`, extended each milestone |
| `web/shared`, `web/member`, `web/requester`, `web/console`, `web/public` | design system, i18n, calendar and bidi helpers; member screens; requester screens; reviewer and operator console; public pages | UI | the generated API client and `web/shared` only | `BM0` scaffold, `BM2`, `BM8` |
| `seed/`, `migrations/`, `ci/`, `build/`, `copy/`, `docs/adr/` | seeds and fixtures; migrations; pipelines and manifests; stub register and DoD records; copy registry; decision records | support | n/a | all |

Import direction is one-way (lower layers never import higher ones); modules of the same layer talk through ports or events (outbox, S0.9), never through each other's tables. `economy/` reads verified throughput from the read model fed by `execution/` events, not from `execution/` code. A boundary test (`T-unit-arch`) fails the build on a forbidden import. [A]

**Protected shared files** (a WP may only append its own rows or ask the owner) [A]

| File or path | Why shared | Who changes it |
| --- | --- | --- |
| `spec/**` | The contract | Spec cells only; a WP raises an issue (`WR5`) |
| `platform/registry/*` (ids, events, error codes, metric names, enums) | Data copy of S0.5, S0.7..S0.9, S0.11.3 | Changed only after the S0 change; `WP-BM0-02`, `WP-BM0-03`, `WP-BM0-05` own the loaders |
| `seed/parameters/<area>.*` | One file per area, so parameter additions never collide | The WP that owns that area; the loader and validator are owned by `WP-BM0-04` |
| `migrations/` | Numbered by 17.8.1 | A WP adds files only inside its own number range; the runner and numbering check are owned by `WP-BM0-07` |
| `api/ops/<area>.*` (operation declarations with `op` id and `x-milestone`) | Route registration | One file per area, owned by the area's WP; `api/` assembly is owned by `WP-BM0-03` |
| `ci/**`, `ci/milestone-suites.yaml` | Gate definitions and the regression ratchet (`BR6`) | `WP-BM0-01`; each milestone's closer appends one block; removal needs a referenced spec change |
| `build/stubs.md`, `build/dod/BM<n>.md` | Stub register; closure records | Append by the WP that adds a stub; removal by the WP that replaces it; DoD records by the human closer (`BR10`) |
| `copy/<area>.*` | One file per area | The area's WP; the registry validator is owned by `WP-BM0-09` |
| `web/shared/**` | Used by every screen | `WP-BM0-09` (scaffold), `WP-BM2-08` (console shell), `WP-BM8-01` (design system); other WPs import only |
| `docs/adr/**` | Decisions | Humans (PB-1, PB-2) |

**Work-package card** (what the person or tool that assigns a WP writes; one per WP, stored as `build/wp/WP-BM<n>-<kk>.md`) [A]

```
id:        WP-BM<n>-<kk>
title:     <name from the 17.9.2 tables>
owns:      <path globs from the table; nothing else may change>
needs:     <contracts: S-part sections, S0 names, ports to mock>
provides:  <operations (op ids), tables, events, parameters, copy keys, ports>
stubs:     <ports bound to a stub, with the removing milestone>
accept:    <AC and T ids that must pass; the CI command that runs them>
forbidden: <everything outside owns; production secrets; provider facts>
done_when: GD1..GD13 for the parts this WP touches, plus the milestone checklist rows it owns
```

### 17.9.2 Work packages by milestone

Columns: `After` lists the packages of the same milestone whose provided contract this package needs a mock of; packages with an empty `After` start at once, and packages that do not list each other run in parallel (17.9.3). `Accept` lists the tests of 17.6 that the package makes pass (`BM` tests are cited by the number only). [A]

**BM0 `foundation`** (steps PB-1..PB-3 are human tasks with recorded outputs, not work packages, 17.4)

| WP | Title | Owns | Needs | After | Accept |
| --- | --- | --- | --- | --- | --- |
| `WP-BM0-01` | `repo-ci-skeleton` | `ci/**`, repository layout, path rules, regression manifest, CI job definitions | 17.1 `BR1`..`BR10`, 17.5.3 | none | `AC-bm0-17` (partly) |
| `WP-BM0-02` | `core-libs` | `platform/ids`, `platform/money`, `platform/clock`, `platform/hash`, `platform/tokens`, id-prefix registry data | S0.6, S0.7 | none | `AC-bm0-04`, `-05`, `-06`; `T-unit-01` |
| `WP-BM0-03` | `api-framework` | `platform/http`, `api/` assembly, conformance suite, `GET /v1/public/health` | S0.11 | `-02` | `AC-bm0-02`, `-03`, `-07`, `-08`, `-09`, `-11` |
| `WP-BM0-04` | `config-store-and-seed` | `platform/config`, `seed/parameters/` loader and validator, genesis change-log seed | S0.10 (`C1`..`C8`, 0.10.6), S16 | `-02` | `AC-bm0-01`, `-10` |
| `WP-BM0-05` | `outbox-observability` | `platform/events`, `platform/obs` (scrubber, metric registry and linter), event registry data | S0.5, S0.9, S4 | `-02` | `AC-bm0-16`; `GD6` linters |
| `WP-BM0-06` | `ports-and-stub-guard` | `platform/ports/*` (storage, objects, secrets, scheduler, clock, mail, ratelimit_store), local bindings, `build/stubs.md`, production config validator | S4 | `-02` | `AC-bm0-12` |
| `WP-BM0-07` | `migrations-backup-restore` | `migrations/` runner, numbering check (17.8.1), upgrade-test harness, backup and restore runbook and test | 17.8.1, S4 | `-06` | `AC-bm0-15`; `BR2` |
| `WP-BM0-08` | `scanners` | `ci/scanners/*`: secret scan, forbidden-capability scan, external-hosts scan | `BR8`, `BR9`, S10 | none | `AC-bm0-13`, `-14` |
| `WP-BM0-09` | `i18n-scaffold-and-probe` | `web/shared` scaffold (copy registry and validator, logical-property CSS convention, bundled-font loader), `probe/` (static reachability page and JSON) | S11, S0.3 | none | `AC-bm0-14` (bundle side); copy-registry validator |

**BM1 `ledger_and_invariants`**

| WP | Title | Owns | Needs | After | Accept |
| --- | --- | --- | --- | --- | --- |
| `WP-BM1-01` | `ledger-schema-and-accounts` | `ledger/schema`, migrations `1xx`, singleton bootstrap seed | S6, S0.8.5 | none | seed-closed rows for the ledger |
| `WP-BM1-02` | `posting-engine` | `ledger/posting`: transactions, entries, `seq`, hash chain, per-commit check, idempotent postings | S6, S0.6 | `-01` | `AC-bm1-09`, `-11`, `-14` |
| `WP-BM1-03` | `lots-and-expiry` | `ledger/lots`: oldest-first spend, restore with original expiry, sweep and retirement functions | S6, `ISS-07` | `-02` | `AC-bm1-04`, `-05`, `-06` |
| `WP-BM1-04` | `escrow-and-reserve-ops` | `ledger/escrow`: hold, release, settle, refund, `reserve_donation`, `transfer`, `grant` primitives | S6, S0.8.5 | `-02`, `-03` | `AC-bm1-01`, `-03`, `-13` |
| `WP-BM1-05` | `reversal` | `ledger/reversal` (two distinct approver ids, mirrored lot effect) | S6, S0.10.6 `ledger.reversal_min_approvers` | `-02`, `-03` | `AC-bm1-10` |
| `WP-BM1-06` | `invariant-engine` | `ledger/invariants`: per-class checks, sampled and full jobs, `InvariantCheck`, `Alarm`, event and metric | S6 (`INV-L<nn>`), S0.5 | `-02` | `AC-bm1-08` |
| `WP-BM1-07` | `db-role-append-only` | `ledger/dbrole`: application role grants, trigger or equivalent refusing update and delete, tamper test role | S4, S6 | `-01` | `AC-bm1-07` |
| `WP-BM1-08` | `property-harness` | `ledger/testkit`: seedable operation generators, serial-order oracle, documented inputs | S6, S18 `T-prop-*` | `-02` | `AC-bm1-02`, `-15` |
| `WP-BM1-09` | `ledger-cli-and-checkpoint` | `ledger/cli` (`verify`, `checkpoint`, `explain`), checkpoint job | S6 | `-02`, `-06` | `AC-bm1-12` |

**BM2 `admin_gates_and_config`**

| WP | Title | Owns | Needs | After | Accept |
| --- | --- | --- | --- | --- | --- |
| `WP-BM2-01` | `admin-auth` | `admin/auth`: `AdminUser`, `AdminCredential`, admin `Session`, WebAuthn, origin rule, bootstrap command | S10, S0.11.4 | none | `AC-bm2-03`, `-04`, `-12`, `-13` |
| `WP-BM2-02` | `admin-actions-two-person` | `admin/actions`: `AdminAction` log, two-person framework | S10, S0.10.6 `security.two_person_actions` | `-01` | `AC-bm2-11`, `-14` |
| `WP-BM2-03` | `parameter-editor` | `admin/params`: versions, `effective_from`, tighten and loosen, public change-log entries | S16, S0.10.3 | `-02` | `AC-bm2-05`, `-06` |
| `WP-BM2-04` | `kill-switches-and-flags` | `admin/kill` (`assertNotKilled`), `admin/flags` | S14 | `-02` | `AC-bm2-07`, `-08` (flags) |
| `WP-BM2-05` | `experiments-and-prereg` | `admin/experiments`: assignment library, logging, `PreRegistration` lock | S13 | `-02` | `AC-bm2-08`, `-09` |
| `WP-BM2-06` | `launch-gates-and-rule` | `admin/gates`: `LaunchGateItem` machine, sign-offs, gate rule, `launch.*` enforcement library | S14, S0.9.8 | `-02`, `-03` | `AC-bm2-01`, `-02`, `-15` |
| `WP-BM2-07` | `calibration-tool` | `admin/calibration`: `CalibrationRecord`, aggregates, insufficiency flag | S13, S0.10.4 | `-02` | `AC-bm2-10` |
| `WP-BM2-08` | `ops-console-shell` | `web/console` shell and screens for parameters, gates, kill switches, calibration, ledger explorer, alarms (`en`) | S11, S15 (mock API) | contracts of `-01`..`-07` | console part of 17.6 `BM2` DoD |
| `WP-BM2-09` | `public-params-and-changelog` | `api/ops/public-config.*`: `/v1/public/parameters`, `/v1/public/change-log` | S12, S15 | `-03` | cache and `ETag` checks of `GD5` |

**BM3 `registry_and_policy`**

| WP | Title | Owns | Needs | After | Accept |
| --- | --- | --- | --- | --- | --- |
| `WP-BM3-01` | `registry-core` | `registry/services`: entries, review machine (S0.9.6), approval guard, age and grace timers, gate-rule counter binding | S7 | none | `AC-bm3-01`, `-02`, `-05`, `-12` |
| `WP-BM3-02` | `terms-copies-and-flags` | `registry/terms`, `registry/flags`: `TermsCopy` in the `objects` port, `FlagAnswer` history, region field, link of `CalibrationRecord` | S7, S0.8.3 | `-01` | `AC-bm3-03`, `-04` |
| `WP-BM3-03` | `adapter-port-and-builder` | `registry/adapter`: capability object, pure URL builder, copy-only logic | S7, S11 | none | `AC-bm3-10` |
| `WP-BM3-04` | `policy-data-and-seed` | `policy/model`, `seed/policy/*`: `Policy`, `PolicyVersion`, `Rule` rows `R1`..`R10`, allowlist, `TopicCategory` seed | S7 | none | seed rows 8 and 9 of 17.8.2 |
| `WP-BM3-05` | `policy-evaluator` | `policy/eval`: registered handlers, metadata validation, reason codes, stamping, acceptance re-check library | S7 | `-04` | `AC-bm3-06`, `-07`, `-09` |
| `WP-BM3-06` | `policy-change-workflow` | `policy/change`: tighten at once, loosen with change-log and notice (`R10`) | S7, S16 | `-04` | `AC-bm3-08` |
| `WP-BM3-07` | `optin-model-and-r8` | `policy/optin`: `OptIn` data model, `optin.*` defaults, `R8` predicate | S7, S10 | `-04` | `AC-bm3-11` |
| `WP-BM3-08` | `review-screens-services` | `web/console/review/services` (`SCR-rev`, `en`) | S11 (mock API) | contracts of `-01`, `-02` | DoD rows on screens |
| `WP-BM3-09` | `dry-run-and-oracle` | `api/ops/policy-eval.*`, `policy/oracle` (executable table of S7), `AC-bm3-13` repository scan | S7, S15 | `-05` | `AC-bm3-06`, `-13` |

**BM4 `identity_and_access`**

| WP | Title | Owns | Needs | After | Accept |
| --- | --- | --- | --- | --- | --- |
| `WP-BM4-01` | `member-identity-core` | `identity/core`: `Member`, `MemberKey`, member `Session`, challenge-response, creation guard | S10, S0.6.4 | none | `AC-bm4-01`, `-03` |
| `WP-BM4-02` | `recovery-rotation-devices` | `identity/recovery`: recovery flow and cooldown flag, rotation, `Device`, link codes, optional e-mail via `mail` port | S10 | `-01` | `AC-bm4-04`, `-05` |
| `WP-BM4-03` | `invites-and-trees` | `identity/invites`: `Invite`, tree limits, operator root invites | S10 | `-01` | `AC-bm4-06` |
| `WP-BM4-04` | `rate-limits-and-ip-hash` | `identity/limits`: per device, IP-hash, tree and day limits on the `ratelimit_store` port | S10, S0.11.7 | `-01` | `AC-bm4-02`, `-12` |
| `WP-BM4-05` | `roles-and-permission-matrix` | `identity/perm`, `seed/roles`, generator from the S10 table, coverage test | S10 | none | `AC-bm4-07` |
| `WP-BM4-06` | `trust-status-and-moderation` | `identity/trust`: tier and status machines (S0.9.4), suspend, ban, close, restrict; `kill.member` binding | S10, S0.9.4, S14 | `-01` | `AC-bm4-10` |
| `WP-BM4-07` | `retention-and-privacy-tests` | `identity/retention`: retention jobs, canary scans for IP and e-mail | S10 (retention table) | `-01` | `AC-bm4-08`, `-09` |
| `WP-BM4-08` | `identity-client-sdk` | `sdk/identity`, `web/shared/keystore` (keys stay on the device), test harness client | S10, S15 | contract of `-01` | SDK rows of the `BM4` DoD |
| `WP-BM4-09` | `member-ledger-link` | `identity/accounts`: ledger account created in the member transaction, deferred foreign keys of 17.8.1, experiment assignment hook, opt-in defaults | S10, S6, 17.8.1 | `-01` | `AC-bm4-11`, `-13` |
