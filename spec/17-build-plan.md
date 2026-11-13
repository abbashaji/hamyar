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

