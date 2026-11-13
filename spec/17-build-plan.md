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

