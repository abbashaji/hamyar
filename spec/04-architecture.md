# 4. System overview and architecture

*Spec part 4 · provenance: cell C-002 · written against Founding Document draft v0.1 (FD), `spec/00-conventions.md` (cited S0.*) and `docs/source/panel-review.md` (cited PR§n). Nothing here was executed, deployed or checked against any host, product documentation, provider terms or law. Facts about hosts, products, provider terms and law are configuration data or are tagged [V].*

## 4.1 Scope, reading guide and decisions at a glance

This part specifies the architecture of the complete system: stack-agnostic first (4.2 to 4.16), then a recommended concrete stack with alternatives (4.17), then a keep / wrap / replace decision for each item of the existing Blueprint Panel (4.18). It does not repeat entity fields (S5.*), ledger rules (S6.*), policy rules (S7.*), API operations (S15.*) or the full parameter table (S16.*). It fixes the components, their interfaces, the storage and consistency contracts and the operational machinery they run on. Phase 1 is a configuration of this architecture, not a smaller one (FD§9) [P].

Vocabulary [D]:

- **Port**: an interface the domain depends on (store, clock, scheduler, alert delivery, backup target). **Driver**: one implementation of a port. Every port has two drivers from the first milestone: an in-memory fake for tests and a real one.
- **Service-adapter**: the client-side module that prepares a prompt for one chat service from Service Registry data (4.14). It has nothing to do with ports and drivers; the two vocabularies are never mixed.
- **Application service**: a module that owns a set of entities and the transactions that change them (4.4). **Domain library**: pure code with no I/O (4.5).

| # | Decision [D] | Reason | Where |
| --- | --- | --- | --- |
| 1 | Modular monolith plus one optional isolated check runner; ports and drivers for everything outside the process | Ledger atomicity needs one transaction scope; a small team needs few moving parts; module rules keep extraction possible | 4.3, 4.5 |
| 2 | Ledger, escrow, lots, cell and job state, idempotency records and the event outbox commit in one transactional store | The FD§4.2 invariants cannot be kept across stores without distributed transactions | 4.6 |
| 3 | Exactly one ledger and one hash chain; serializable posting; gapless `seq` | Global invariant (total credit in existence) and tamper evidence | 4.6 |
| 4 | Events announce committed facts; they never carry money or commands | Money movement must not depend on a relay being up | 4.7 |
| 5 | A real scheduler running idempotent, state-based jobs; no lazy expiry | PR§3.3: the panel has no scheduler and evaluates expiry only when someone asks | 4.8 |
| 6 | Parameters, flags, kill switches and launch switches are versioned data; brakes are read inside the transaction they guard | Build is not launch; tighten at once (R10) | 4.9 |
| 7 | Forward-only expand/contract migrations; append-only enforced by database privileges, not only by code | Ledger integrity under operator or code error | 4.10 |
| 8 | Logs, metrics and analytics events are built from field allowlists; no personal data | FD Principle 8 | 4.11 |
| 9 | Encrypted, independent backups; restores verified by invariants, the hash chain and the published checkpoint | Detects rollback and tampering | 4.12 |
| 10 | Four environments; launch switches `false` in every build; no bypass of the launch machinery in any environment | Prompt preamble | 4.13 |
| 11 | Service-adapter: pure, client-side, driven by registry data; the human presses Send; the chat page is never read | FD Principle 3, ground rule 3 | 4.14 |
| 12 | No mandatory third-party runtime dependency (CDN, font, analytics, captcha, push); hosting and storage movable | FD§8.2 risk 14, prompt I | 4.15 |
| 13 | Recommended stack: TypeScript, PostgreSQL as system of record, static SPAs; Cloudflare Worker with D1 and Durable Objects is the main alternative | Strong consistency and reachability [V] drive the choice | 4.17 |
| 14 | Panel: keep the concepts (cell, lease, fencing, status colors, release), wrap the data-source seam and graph components, replace storage, identity, secrets, launcher and result path | PR§1 to PR§8 | 4.18 |

## 4.2 Architectural principles and exclusions

### 4.2.1 Principles [D]

| Principle | Rule | Source |
| --- | --- | --- |
| Build is not launch | Every launch brake (launch switches, gate state, Service Registry state, kill switches) is enforced in the domain layer, inside the transaction that would cross it; never only in a screen or a gateway | prompt preamble, FD§8.3 |
| One truth for money | Ledger, escrow, lots, job and cell state and the outbox live in one transactional store and commit together; no distributed transaction exists in the reference architecture | FD§4.2 |
| Deterministic core | Price, admission, policy evaluation, estimators and state transitions are pure functions over plain data; the same code runs in services, in tests and in the simulation harness (S18.*) | prompt K |
| Rules are data | R1..R10, parameters, templates, service flags, adapter capabilities and kill switches are versioned rows, not constants | FD§10 item 6, ground rule 4 |
| Provider-neutral | No provider name, URL, limit or terms fact appears in code or in this spec; it enters as registry data recorded by a reviewer [V] | FD Principle 7, ground rule 2 |
| Human presses Send | The platform has no channel into a volunteer's provider session: it hands text to the human and receives text from the human | FD Principle 3, ground rule 3 |
| Minimal by construction | Storage, logs, metrics and events are built from field allowlists, so personal data cannot enter by accident | FD Principle 8 |
| Replaceable hosts | Hosting, storage, backup and delivery sit behind ports so the system can move; reachability from Iran is [V] | FD§8.2 risk 14 |
| Fail closed | Unknown flag means no; missing configuration means refuse; a failed invariant engages brakes; an unreachable check runner means no code-running template | FD§5.3 |
| Observable without surveillance | Operators can see system health and the flow of credit without seeing who did what | FD Principle 8 |

### 4.2.2 Exclusions [D]

These are not deferred; they are out of the product. Each follows from ground rule 3 or FD Principles 3, 8 and 9.

| Excluded | Why |
| --- | --- |
| Programmatic reading of a provider page, its DOM, screenshots or the volunteer's clipboard | The platform has no channel into the volunteer's session; a clipboard read can expose unrelated content. Paste-back is the human pasting into our own text field |
| Any extension, userscript or native helper that fills, focuses or clicks Send, or that captures a chat URL | The human presses Send. The panel's opt-in auto-send userscript and the launcher's optional chat-link record (PR§1, PR§6.4, PR§6.5) do not carry over (`ISS-46`) |
| Storing a volunteer's provider credentials, cookies, session or API keys; calling any provider from the server | No component needs it. No component calls any AI service; a future server-side call would be a new port and a spec change (`verify.model_judge_mints_credit` stays `false`) |
| Features that help anyone bypass a regional or technical restriction (relays or mirrors aimed at evading a provider's blocks, circumvention advice) | FD Principle 9. Moving the platform's own host because it is unreachable (4.15) is not circumvention of a provider restriction |
| Third-party runtime resources in any client (CDN, web fonts, analytics, captcha, maps, social widgets, web push) | Blocked-resource risk and tracking (`analytics.third_party_trackers` = `false`) |
| Executing submitted content in the application process or in any process that holds secrets or store access | Submitted text is untrusted; the only exception is the isolated check runner (4.4, `ISS-41`) |
| A shared password or shared token for any principal | Per-principal credentials only (S0.11.4); PR§4.5 items 1, 2 and 7 show the cost of a shared one |
| Unsolicited messages of any kind (push, SMS, e-mail marketing, in-site pop-ups) | The public site is notification-free (4.4); the only message the platform may ever send is one the member explicitly requested, such as a recovery action [A] (`ISS-44`) |

## 4.3 System overview

### 4.3.1 Context diagram

```text
 Public visitor           Member (donor and/or requester)          Admin (reviewer / operator)
   browser                    browser, mostly phone                        browser
      |                            |            \                              |
      | HTTPS                      | HTTPS       \ human only: copy, open,      | HTTPS + passkey
      |                            |              \ press Send, paste back       |
      v                            v               v                            v
+------------+            +---------------+   +---------------------+    +--------------+
| public     |            | member app    |   | provider chat site  |    | admin tool   |
| site       |            | (static SPA + |   | (third party; no    |    | (static SPA, |
| (static,   |            | Service-      |   | Hamyar server or    |    | own origin)  |
| no notif.) |            | adapters)     |   | script talks to it) |    |              |
+------------+            +---------------+   +---------------------+    +--------------+
      | GET /v1/public/*          | /v1/* (member scheme)                      | /v1/admin/*
      +---------------------------+---------------------+----------------------+
                                                         v
+--------------------------------------------------------------------------------------+
| HAMYAR SERVER SIDE: API + scheduler + outbox relay in one deployable (4.3.2)          |
+--------------------------------------------------------------------------------------+
     |                   |                    |                       |
     v                   v                    v                       v
[Transactional store] [Blob store]      [Ephemeral store]      [Check runner: isolated,
 ledger, state,        terms copies,     rate-limit counters,   flag-gated, no network,
 outbox, config        uploads,          login challenges       no secrets, no store access]
                       deliverables
     |
     v
[Backup sink: encrypted before it leaves, independent location]   [Alert sink] [Log sink] [Static host]
```

The arrow from the member to the provider chat site is the human's own browser action. No server, script or extension of Hamyar sits on it (4.2.2) [D].

### 4.3.2 Layers and deployable units

```text
+----------------------------------------------------------------------------------+
| API layer: routing by surface (public / member / admin), authentication by       |
| scheme, rate limits, idempotency, error model, request ids, pagination           |
+----------------------------------------------------------------------------------+
| Application services (own entities and transactions)                             |
|  Identity  JobCell  Ledger  Policy  Registry  Templates  Verification            |
|  Admission  Config (params, flags, kill switches, launch gates)  Analytics       |
|  PublicProjection  Reports and Appeals  AdminActions                             |
+----------------------------------------------------------------------------------+
| Domain library (pure, no I/O): ucr arithmetic, price and admission math, policy  |
| evaluator, state machines, estimators, canonical JSON, ids, hashing              |
+----------------------------------------------------------------------------------+
| Ports: TransactionalStore BlobStore EphemeralStore Clock Random Scheduler        |
|  SecretStore LogSink MetricSink AlertSink BackupSink StaticHost CheckRunner      |
|  Mailer (optional, off unless S10.* adopts e-mail recovery)                      |
+----------------------------------------------------------------------------------+
| Drivers: one real and one in-memory fake per port                                |
+----------------------------------------------------------------------------------+
```

| Deployable unit | Contents | State | Scaling and roles |
| --- | --- | --- | --- |
| `server` | API layer, application services, scheduler (4.8), outbox relay (4.7) | none in process; everything in the stores | N identical instances; `HAMYAR_ROLES` selects `api`, `jobs` or both; each background job runs on whichever instance holds its lock |
| `check-runner` | Executes template-defined checks that must run code (4.4, `ISS-41`) | none; ephemeral work directory | Separate host or sandbox; absent unless `ff.verify.sandboxed_tests` is on |
| `static bundles` | Public site, member app, admin tool: build output with content hashes | none | Published to the `StaticHost` port; cacheable; no server code |
| Stores | Transactional store, blob store, ephemeral store | all durable state | Per 4.6 |

Decision [D]: one modular monolith, not services per component. Reason: the ledger, job and cell state, and the outbox must share one transaction (4.6), and the operating team is small [A: the owner decision that could overturn this is a larger team or a hosting model that forces separate deployables, S3.*]. Module boundaries are enforced by import rules in CI (4.5) so a module can later be extracted behind its interface without changing callers.

### 4.3.3 Origins and browser hardening [D][A]

| Origin (bootstrap setting) | Serves | Auth scheme | CORS allow-list |
| --- | --- | --- | --- |
| `public_origin` | Public site bundle (S12.*) | none | n/a (static) |
| `app_origin` | Member app bundle (S11.*) | n/a (static) | n/a |
| `api_origin` | `/v1/public/*` and member `/v1/*` | `none`, `member` | `app_origin`, and `public_origin` for public GET only |
| `admin_origin` | Admin tool bundle (S11.*) | n/a (static) | n/a |
| `admin_api_origin` | `/v1/admin/*` only | `admin` | `admin_origin` only |

Staging and production MUST use five distinct origins; dev and test MAY collapse them onto local ports. The admin origin has its own session store and cookies are not used anywhere (S0.11.4), so there is no cross-origin session to steal. Responses of every origin carry these headers [D]:

| Header | Value (intent) |
| --- | --- |
| `Content-Security-Policy` | `default-src 'none'`; scripts, styles, fonts and images from `'self'` only (images may add `data:`); `connect-src` limited to the origin's API; `frame-ancestors 'none'`; `base-uri 'none'`; `form-action 'self'` |
| `Referrer-Policy` | `no-referrer` |
| `X-Content-Type-Options` | `nosniff` |
| `Strict-Transport-Security` | long max-age with `includeSubDomains` once all origins are HTTPS-only [V: host support] |
| `Cross-Origin-Opener-Policy` | `same-origin` |
| `Permissions-Policy` | camera, microphone, geolocation and clipboard-read denied |

The panel sets no CSP or security headers and its `index.html` loads web fonts from third-party hosts (PR§4.5 item 12); both are replaced, not ported. Untrusted text (submissions, uploads, report text) is rendered only as text nodes: a CI lint forbids `innerHTML`-style sinks and unsanitized markdown-to-HTML in all three bundles; the sanitizer allowlist, if any, is owned by S9.* [D].

### 4.3.4 Trust boundaries [D]

| Boundary | What crosses | Controls |
| --- | --- | --- |
| B1 browser to API | Untrusted input | Schema validation at the edge, authentication by scheme, rate limits, idempotency, size limits (`api.max_body_bytes`) |
| B2 member to provider site | Nothing of ours: the human copies a prompt out and pastes text back | No channel exists; pasted text is untrusted input (S9.*) |
| B3 application to stores | Queries and writes | Separate database roles per component (4.6.5); ledger tables writable only through the ledger module |
| B4 application to check runner | Untrusted content in, verdict out | One-way call, size and time limits, no network, no secrets, no store access |
| B5 admin origin to member origin | Nothing | Separate origins, session stores and CORS lists |
| B6 operators to production | Admin actions | Passkeys per `AdminUser`, `AdminAction` log, two-person actions (`security.two_person_actions`) |
| B7 production to backup sink | Backup artifacts | Encrypted before leaving the host; the sink cannot read them (4.12) |

## 4.4 Components and interfaces

### 4.4.1 Component table [D]

| Component | Responsibility | Owns (entities, S0.7) | Depends on | Detail in |
| --- | --- | --- | --- | --- |
| Identity service | Anonymous members, keys, sessions, device linking, recovery, invites, rate-limit decisions, permission checks | `Member`, `MemberKey`, `Device`, `Invite`, `Session`, `AdminUser`, `AdminCredential`, `OptIn` | Transactional store, ephemeral store, clock, random, secrets | S10.* |
| Ledger service | The only writer of ledger tables: posting, balances, lots, escrow accounts, hash chain, invariant checks, checkpoints | `LedgerAccount`, `LedgerEntry`, `LedgerTransaction`, `CreditLot`, `Escrow`, `Reserve`, `InvariantCheck` | Transactional store, config | S6.* |
| Job and cell service | Job, cell, lease, submission state machines; leasing; paste-back intake; assembly; settlement orchestration | `Job`, `Cell`, `Lease`, `Submission`, `Upload`, `Glossary`, `Deliverable`, `Manifest`, `Reservation`, `WaitlistEntry` | Ledger, policy engine, templates, verification, admission, stores | S5.*, S8.*, S9.* |
| Policy engine | Pure evaluator of rules R1..R10 over data; stamping and re-check; policy versioning | `Policy`, `PolicyVersion`, `Rule` | Service registry, template registry, config | S7.* |
| Service registry | Services, dated flag answers, saved terms copies, review machine, derived Service-adapter descriptors | `ServiceRegistryEntry`, `TermsCopy`, `FlagAnswer` | Blob store, config | S7.*, 4.14 |
| Template registry | Templates, immutable versions, review machine, deterministic rendering of prompts | `Template`, `TemplateVersion`, `TopicCategory`, `GoldCell` (library) | Config | S8.* |
| Verification pipeline | Automatic checks, gold insertion, audit selection and comparison, reliability estimates, human-review cells; optional check runner | `VerificationRecord`, `Audit` | Job and cell service, ledger (via job service), check runner port | S8.*, S9.* |
| Admission control | Capacity forecast, quote, waitlist, reservations, fairness | `Reservation` (with job service), forecast tables | Metrics rollups, config | S6.* |
| Config service | Parameters, feature flags, kill switches, launch switches and gates, config epoch | `Parameter`, `ParameterVersion`, `FeatureFlag`, `KillSwitch`, `LaunchGateItem`, `Experiment`, `ExperimentAssignment`, `PreRegistration`, `CalibrationRecord`, `ChangeLogEntry`, `AdminAction` | Transactional store | 4.9, S14.* |
| Moderation | Reports, appeals, bans, template auto-pause | `Report`, `Appeal` | Identity, template registry, job service | S10.* |
| Analytics pipeline | Projects domain events to analytics events, rolls up metrics, publishes snapshots | `Event`, `MetricSnapshot` | Outbox, transactional store | S13.* |
| Public projection and public site | Read model for counters, ledger page, parameters, change log, milestones; a static site with no notification channel | `Badge`, `BadgeAward`, `Team`, `Referral` (member side with identity) | Ledger (read), analytics | S12.* |
| Admin tool | A thin single-page client of `/v1/admin/*`; no business logic, no direct store access | none | API | S11.* |
| Service-adapter layer | Client-side preparation of copy and open actions from registry descriptors | none | Descriptor from service registry | 4.14 |
| Scheduler and outbox relay | Run background jobs and deliver events | infrastructure tables (4.7, 4.8) | Stores, clock | 4.7, 4.8 |
| Check runner | Runs code-executing checks in isolation | none | none (no network, no secrets) | S8.*, `ISS-41` |

**Notification-free public site [D][A].** The public site (S12.*) is static and read-only. It has no cookies, no service-worker push registration, no sign-up or subscribe form, no e-mail capture and no third-party embed. Anything a member needs to know (expiry dates, a changed parameter, a restored service) is shown in the member app when it is next opened, never pushed. Reason: FD Principle 8, FD§8.2 risk 15 (burnout) and `analytics.cookies_enabled` = `false`. The owner decision that could overturn this is a wish for expiry reminders (`ISS-44`, S3.*).

### 4.4.2 Interface contracts

Notation is neutral pseudo-IDL; any language may realize it. `ctx` is a `RequestContext {request_id, principal, idempotency_key?, config: ConfigSnapshot, now, uow?}`. Every operation returns `Ok(value)` or `Err(DomainError{code, details})`, with `code` taken from S0.11.3. Every mutating operation runs in one unit of work and emits the events of the transitions it performs in the same commit (4.7) [D].

```text
IdentityService                                                    // S10.*
  createMember(ctx, public_key, invite_token?)         -> Member
  issueChallenge(ctx, member_key_id)                   -> Challenge
  verifyChallenge(ctx, challenge_id, signature)        -> Session
  rotateKey / linkDevice / startRecovery / completeRecovery / revokeSession
  createInvite / redeemInvite / setOptIn
  checkRate(ctx, bucket, key_hash)                     -> Allowed | Limited(retry_after_s)
  authorize(principal, permission)                     -> Allow | Deny      // perm.<area>.<action>

LedgerService                                                      // S6.*
  post(ctx, draft: LedgerTransactionDraft)             -> LedgerTransaction  // the ONLY write path
  balance(account_id)                                  -> {balance_ucr, lots[]}
  listEntries(account_id, cursor)                      -> Page<LedgerEntry>
  runInvariants(tier)                                  -> InvariantCheck[]
  verifyChain(from_seq, to_seq)                        -> ChainResult
  publishCheckpoint()                                  -> {seq, entry_hash}

JobCellService                                                     // S5.*, S8.*, S9.*
  createJob / submitJob / confirmEscrow / cancel       // Job machine (S0.9.2)
  leaseNextCell(ctx, member_filters)                   -> {Lease, Cell, rendered_prompt} | NoCell
  declineLease / extendLease / submitResult(lease_id, nonce, payload)
  reapExpiredLeases(batch) / requeue / void / assemble / settle

PolicyEngine                                                       // S7.*   (pure)
  evaluate(rules, facts)                               -> Accepted | Rejected(reasons[])
  stamp(job)                                           -> policy_version_id
  recheckOnAccept(job, cell, current_policy)           -> Ok | Err(policy_changed)

ServiceRegistry                                                    // S7.*
  recordFlagAnswer / saveTermsCopy / startReview / approve / suspend / revoke
  adapterDescriptor(service_id)                        -> AdapterDescriptor  // derived, read-only (4.14)
  listApproved(purpose, region)                        -> ServiceRegistryEntry[]

TemplateRegistry                                                   // S8.*
  createVersion / requestReview / approve / pause / retire
  render(template_version, slots)                      -> {prompt_text, prompt_hash}  // pure, deterministic

VerificationPipeline                                               // S8.*, S9.*
  runAutomaticChecks(submission)                       -> VerificationRecord[]   // inline, bounded
  selectForAudit(cell, member_reliability, config)     -> bool                   // pure
  createAudit / compare(audit) / estimateReliability(member)
  CheckRunner.run(check_spec, content, limits)         -> CheckResult | Unavailable

AdmissionControl                                                   // S6.*
  forecast()                                           -> CapacityForecast      // read of the stored forecast
  quote(job_draft)                                     -> Accept{price_ucr, window_s} | Waitlist | Reject
  reserveCapacity / releaseCapacity / promoteWaitlist

ConfigService                                                      // 4.9
  snapshot()                                           -> ConfigSnapshot{config_epoch, ...}
  valueAt(name, t) / proposeChange / applyChange / engageKillSwitch / releaseKillSwitch

AnalyticsPipeline                                                  // S13.*
  project(domain_event)                                -> AnalyticsEvent | null  // allowlist per event name
  rollup(window) / publishMetricSnapshot() / suppressSmallCohorts(k)
```

### 4.4.3 Cross-component rules [D]

1. Only the ledger service writes ledger tables. Other services call `LedgerService.post` with a draft built by pure domain functions (mint, hold, payout, settle, expire, retire, grant, reserve_donation, reversal; S0.8.5). Posting is inline in the transaction of the state change that causes it, for example `Cell.accepted` and its `payout` share one commit.
2. Only the job and cell service writes job, cell, lease and submission tables; only the config service writes parameter, flag, kill-switch and gate tables. Services read each other's data only through interfaces or declared read models, never by joining foreign tables in application code.
3. The policy evaluator, template rendering, price and admission arithmetic, reliability estimators and sampling decisions are pure. Anything that needs time, randomness or a store receives it as an argument (`Clock`, `Random`), so property tests and the simulation harness can drive it deterministically.
4. A cross-component call inside one request passes the same unit of work; no component opens its own transaction inside another's.
5. Every admin write goes through the same service operations as the equivalent system action, adds one `AdminAction` row in the same commit, and honors `security.two_person_actions`.

### 4.4.4 Check runner [D][A]

Prompt E requires automatic checks including tests for code-change jobs, while the abuse rules forbid executing submitted content. Both hold only if code runs somewhere that cannot hurt anything (`ISS-41`):

- The server never executes submitted content. A check of kind `run_tests` is a request to the `CheckRunner` port.
- The runner has no network, no secrets, no store access, a read-only base image, a fresh working directory per run, and hard limits on CPU time, memory, process count, output size and wall time. It returns a verdict and a bounded log, nothing else.
- It is off by default (`ff.verify.sandboxed_tests`). While it is off or unreachable, `CheckRunner.run` returns `Unavailable`, and templates whose checks need it cannot be approved or leased (R4 then rejects jobs for them). It never fails open.
- Whether a runner design is safe enough to turn on is a G1 decision [V: security reviewer, recorded as `LaunchGateItem` evidence].

## 4.5 Module and dependency rules

[D] Dependencies point inward: API layer, then application services, then the domain library, then port interfaces; drivers implement ports and are wired only at the process entry point.

| Rule | Enforcement |
| --- | --- |
| The domain library imports no port, driver, framework or clock | Import-boundary lint in CI |
| An application service imports other services only through their interface modules | Import-boundary lint |
| No module reads `Date.now`-style ambient time or ambient randomness | Lint; `Clock` and `Random` ports only |
| Every port has an in-memory fake and a contract test suite that runs against the fake and every real driver | CI (BM0 onward) |
| Pure functions used for money, admission and sampling have parity fixtures usable by the simulation harness | S18.* |

The panel's `GitHubApi` interface with an in-memory fake (`test/fakegh.ts`) and its Python/TypeScript parity fixtures (PR§1, PR§7.1) are the pattern being kept: a clean seam, a fake, and shared fixtures [D].

## 4.6 Storage interfaces and the ledger consistency requirement

### 4.6.1 Ports [D]

| Port | Purpose | Consistency and durability requirement |
| --- | --- | --- |
| `TransactionalStore` | System of record for every entity, the ledger, idempotency records, the outbox, scheduler locks, config | ACID transactions; serializable isolation or an equivalent that excludes write skew (4.6.2); durable commit; point-in-time recovery [V: per host] |
| `BlobStore` | Terms copies, uploads, deliverables, manifests | Write-once, content-addressed by `sha256:`; read-after-write for the writer; the hash is re-checked on read; the referencing row commits after the blob exists; an orphan sweeper removes unreferenced blobs; deletable at retention time |
| `EphemeralStore` | Rate-limit counters, login challenges, short holds | Atomic increment with TTL; approximate counts are acceptable only where noted in 4.6.3; never the sole guard of anything that moves credit. MAY be implemented inside the transactional store (an unlogged table) to avoid a second dependency [A] |
| `Clock` | Authoritative time | One source per environment; with a relational store, the transaction's own database clock; skew alarm `ops.clock_skew_alarm_s` |
| `Random` | CSPRNG | OS-level randomness only (S0.6.4) |
| `Scheduler` | Fires jobs (4.8) | Single-flight per job by lock; correctness never depends on it (jobs are idempotent) |
| `SecretStore` | Versioned secrets (`secret.<name>[version]`) | Read at start and on rotation; never logged; names owned by S10.* |
| `LogSink`, `MetricSink`, `AlertSink` | Operational output | Allowlisted fields only (4.11); no third-party sink by default [A] |
| `BackupSink` | Encrypted backup artifacts | At least two independent locations (4.12) |
| `StaticHost` | Publishes built bundles | Atomic switch of a release; content-hashed file names |
| `CheckRunner`, `Mailer` | Isolated checks (4.4.4); optional recovery mail | `Unavailable` is a valid, safe answer |

### 4.6.2 The ledger consistency requirement (exact) [D]

A `TransactionalStore` driver is acceptable for the system of record only if it provides all of LC-1 to LC-9. A driver that cannot is a fake for tests, never a production driver.

| Id | Requirement |
| --- | --- |
| LC-1 Atomic commit | All rows of one `LedgerTransaction` (entries, lot changes, balance projections, chain head, idempotency record, outbox rows) and the domain state change that causes it (for example `Cell.accepted`, `Escrow` state) commit together or not at all |
| LC-2 Isolation | Outcomes equal some serial order for any two transactions that touch a common ledger account or the chain head (serializability for ledger writes). The checks of non-negative balances, lot consumption, monthly mint cap, per-member cap K and grant limits MUST NOT read stale data, so two concurrent `escrow_hold` postings by one member cannot both pass a balance check |
| LC-3 Serialization point | Each ledger has one head row (`seq`, `entry_hash`); every posting locks or conditionally updates it, so the hash chain is built in a single order |
| LC-4 Gapless sequence | `seq` is assigned inside the transaction as head + 1; a rolled-back transaction leaves no gap. Database sequences or auto-increment columns, which skip on rollback, MUST NOT be used for `seq` |
| LC-5 Durability | An acknowledged commit survives restart of the process and loss of power on the primary host. Loss of the whole host loses at most `ops.rpo_s` of acknowledged commits [V: the chosen host's real behavior, tested in the restore drill] |
| LC-6 Append-only | The application's database role can insert and select ledger tables but not update or delete them; a trigger or equivalent also rejects update and delete (defense in depth); tested by migration tests (4.10) |
| LC-7 Idempotent posting | A unique key (`txn_kind` plus the natural key of the cause, or the request's idempotency key) makes a retried posting return the stored result and add no entry |
| LC-8 Snapshot reads | Invariant queries (tiers 2 and 3) read from one consistent snapshot of every table they touch |
| LC-9 One store | Ledger and the job, cell and escrow state live in the same store. Splitting them would need a distributed transaction and is not permitted by this spec |

Retry rule [D]: a serialization failure or deadlock aborts the whole unit of work, which is retried with the same idempotency key up to `ops.txn_retry_max` times with jittered backoff; after that the request fails with `UNAVAILABLE`. Partial effects never survive.

```text
LedgerService.post(ctx, draft):
  BEGIN unit of work at the serializable level
    if idempotency record exists for (principal, key): return stored result        // LC-7
    assert kill switches and launch switches for draft.txn_kind, read now          // 4.9
    head := read and lock ledger head                                              // LC-3
    lock the accounts named in draft in account-id order                           // no deadlock
    for each entry in draft.entries:                                               // S0.8.5 types
        check lot consumption or creation, balance constraints, caps
        entry.seq := head.seq + 1 ;  entry.entry_hash := H(head.entry_hash, canonical(entry))
        insert entry ; update balance projection and lots ; head := entry
    tier-1 checks: legs balance, account-type constraints, lots equal member balance
    insert LedgerTransaction, idempotency record, outbox rows for ledger.entry_committed
    update head row
  COMMIT                                                                           // LC-1
  on serialization failure: retry (ops.txn_retry_max), else UNAVAILABLE
```

Capacity requirement [D]. All ledger writes pass one serialization point (`ISS-43`), so the chosen store must be shown to keep up. Let `A_peak` be the largest number of accepted cells in any hour (measured in Phase 1 [H]; the FD§3.3 inputs are illustrative only) and `e` the measured number of non-payout postings per accepted cell (holds, settlements, expiries). Then `C_peak = A_peak / 3600 x (1 + e)` postings per second, and a driver is acceptable only if its measured sustained serial posting rate is at least `ops.capacity_headroom_ratio x C_peak` in a load test at production-like data volume (BM1 and BM9) [V: engineer, report stored as `LaunchGateItem` evidence under G2]. If it is not, the remedies in order are: batch the `payout` postings of one job into one commit, a faster store or host, and only then a partitioned ledger, which needs S6.* to redefine the global invariants first (`ISS-43`, needs_owner).

### 4.6.3 Consistency by data class [D]

| Data class | Required | Notes |
| --- | --- | --- |
| Ledger, lots, escrow, Reserve, mint-cap counters, grant counters | LC-1 to LC-9 | Per-device, per-day and per-tree grant limits that guard credit are enforced inside the ledger transaction, not in the ephemeral store (PR§4.5 item 3: by code reading, a read-then-write counter can be exceeded under concurrency; not run) |
| Cell, lease, submission, job state | Atomic compare-and-set on `row_version`; one winner per transition | Replaces the panel's git ref create and advisory KV reservation (PR§3.3, PR§3.4) |
| Idempotency records | Unique-key insert atomic with the effect | S0.11.5 |
| Parameters, policy, registry, template versions | Immutable versions; read committed is enough; changes bump `config_epoch` in the same commit | 4.9 |
| Rate-limit counters for sign-up, recovery, API | Approximate; atomic increment preferred; failure mode is stricter, not looser | Counters hold IP hashes only, TTL `retention.ip_hash_ttl_days` |
| One-time codes and challenges | Atomic consume (delete-and-return), never get-then-delete | PR§4.5 item 6 shows the non-atomic form |
| Public counters and ledger page | Eventually consistent, lag at most `public.ledger_lag_s` | Read models rebuilt from the ledger |
| Analytics events | At-least-once, idempotent by `event_id` | Never a source of truth |

### 4.6.4 Invariant checks as scheduled and in-transaction work [D]

The invariants `INV-L<nn>` and their formulas are owned by S6.*. This part fixes how they run:

| Tier | When | Reads | On failure |
| --- | --- | --- | --- |
| 1 | Inside every ledger posting (constant-time checks, 4.6.2 pseudocode) | The touched accounts and the head | The posting aborts with `UNPROCESSABLE`; counter `hamyar_ledger_invariant_violations_total` |
| 2 | Every `ledger.invariant_check_interval_s`: random sample of accounts recomputed from entries, recent range gapless, recent hash chain re-verified | One snapshot | Raise `alarm.ledger_invariant_violated`, emit `ledger.invariant_violated` |
| 3 | Every `ledger.full_recompute_interval_s`: global identities, lots against balances, the full chain from the last verified `seq`, comparison with the last published checkpoint | One snapshot | As tier 2 |
| 4 | Every `ledger.checkpoint_interval_s`: publish `(seq, entry_hash)` to the public ledger page | The head | Stale checkpoint raises `alarm.checkpoint_stale` |

Invariants are registered in an `InvariantRegistry` (id, tier, query or function, expected result) and run under a read-only database role, so a checker defect cannot alter data. Alarm handling and the automatic brake are in 4.11.

### 4.6.5 Database roles (least privilege) [D][A]

| Role | May | May not |
| --- | --- | --- |
| `app_rw` | Read and write entity tables; insert and select ledger and other append-only tables | Update or delete append-only tables; read gold-cell answer columns; run DDL |
| `verify_rw` | As `app_rw` plus read gold-cell answers | Run DDL |
| `checker_ro` | Read everything except secrets-bearing columns, at snapshot isolation | Write anything |
| `analytics_ro` | Read the analytics read models | Read member-linked tables |
| `migrator` | DDL and data migrations, only during a migration run | Be used by the running application |

## 4.7 Event model

### 4.7.1 Rules [D]

1. Every state change in S0.9 emits exactly one event with the name shown on the transition. The event row is written in the same commit as the change (transactional outbox). Rejected guards emit nothing.
2. Events announce committed facts. They are never a transport for money or commands: a payout is posted inline in the transaction that accepts the cell (4.4.3 rule 1), not by an event consumer.
3. The event stream is not the system of record and is not event sourcing. Every projection (analytics, public counters, capacity gauges) can be rebuilt from the ledger and entity tables.
4. Delivery is at-least-once to each consumer, ordered per aggregate by `aggregate.version`, and consumers are idempotent.
5. Payloads carry identifiers, enums, hashes and amounts only; never prompts, outputs, uploads, report text, e-mail, IP-derived values or display names. Content is referenced by blob id and hash.

### 4.7.2 Envelope

```yaml
event_id: evt_01j9z...            # ULID id, S0.6.3
event_name: cell.leased           # S0.9, lowercase dotted
event_version: 1                  # bumped on a breaking payload change; consumers accept N and N-1
occurred_at: 2026-11-12T09:30:00Z # store clock
aggregate: {type: Cell, id: cel_..., version: 7}   # version = row_version after the change
actor: {principal_type: member, id: mem_...}       # admin and system ids too; see 4.11 for logs
causation_id: req_...             # the request or job run that caused it
correlation_id: job_...           # the job or other root, when there is one
policy_version_id: plv_...
config_epoch: 1842                # 4.9: resolves every parameter version in force
payload: {}                       # per-event schema in the repository; CI checks it
```

CI rule [D]: for every transition in S0.9 there is exactly one event schema, and a transition test asserts that one event with that name is written in the same commit.

### 4.7.3 Outbox and relay [D]

- At emit time the writer inserts one outbox row per subscribed asynchronous consumer (fan-out at write, from a static subscription table in code). This avoids the offset-gap problem of cursor polling over late-committing transactions.
- Row: `event_id`, `consumer`, `payload`, `attempts`, `next_attempt_at`, `delivered_at`, `dead_at`. The relay claims due rows with a store-level claim (for example skip-locked selection or a conditional update), delivers, and sets `delivered_at`. Failure backs off up to `ops.outbox_max_attempts`, then sets `dead_at` and raises `alarm.outbox_dead_letter`. Replay of a dead row is an admin action (`AdminAction`).
- The consumer records `(consumer, event_id)` in its own dedupe table inside its own transaction.
- Outbox rows are deleted `ops.outbox_retention_days` after delivery. Infrastructure tables (`outbox`, `idempotency_keys`, `scheduler_locks`, `schema_migrations`, `config_epoch_counter`, consumer dedupe tables) are exempt from the entity rules of S0.7 except naming, and are reported as a convention addition (`ISS-45`).

| Consumer | Subscribes to | Effect | Impact if it lags |
| --- | --- | --- | --- |
| `analytics_projector` | all domain events | Writes `Event` rows through the allowlist projection (S13.*) | Metrics late |
| `public_projection` | `ledger.entry_committed`, `cell.accepted`, `member.created`, `changelog.entry_published` | Updates public read models within `public.counter_refresh_s` and `public.ledger_lag_s` | Public page stale |
| `alarm_evaluator` | `ledger.invariant_violated`, `killswitch.engaged`, `service.review_due`, `template.paused` | Creates `Alarm` rows and calls `AlertSink` | Alert late; the brakes themselves do not depend on it (4.11) |
| `capacity_counters` | `cell.accepted`, `lease.issued`, `member.optin_changed` | Incremental inputs for the capacity forecaster | Forecast uses the last full recompute |
| `admin_feed` | all domain events | Admin tool activity view (pull) | Feed stale |

## 4.8 Background jobs

### 4.8.1 Runner rules [D]

- Jobs are declared in a manifest: name, interval parameter, batch-size parameter, maximum runtime (`ops.job_max_runtime_s`), handler.
- Every handler is state-based and idempotent: it selects what is due now (not what a tick missed), changes it with compare-and-set on `row_version`, and is safe to run twice at once. Missed ticks are never queued; the next run covers everything due.
- The lock in `scheduler_locks` (holder, fencing token, `expires_at` renewed while running, TTL `ops.job_lock_ttl_s`) only avoids wasted work. Safety comes from idempotency, because a lock cannot guarantee exclusivity after expiry.
- Time comes from the `Clock` port (the store clock). Each run logs `sched.run_finished`, updates `hamyar_sched_run_duration_seconds`, and the watchdog raises `alarm.sched_overdue` when a job has not succeeded for `ops.job_overdue_factor` times its interval.
- An operator may trigger a run from the admin tool (`AdminAction`); this calls the same handler.

### 4.8.2 Job table [D]

| Job | Purpose and rule | Interval parameter | Detail |
| --- | --- | --- | --- |
| `lease_reaper` | Lease expiry: leases `active` past `expires_at` become `expired`; their cells requeue (`attempt` + 1) or become `exhausted` at `cell.max_attempts`; late paste-back within `lease.submit_grace_s` is handled by the submission path | `lease.reap_interval_s` | S5.*, S9.* |
| `ttl_sweeper` | Time-driven transitions: quote expiry (`price.quote_ttl_s`), waitlist expiry (`admission.waitlist_ttl_days`), reservation expiry and release, invite expiry (`invite.ttl_days`), referral bonus release (`growth.referral.hold_s`), restriction lift (`trust.restriction_days`), service review timers (`service.review_max_age_days`, `service.review_grace_days`), session purge | `ops.ttl_sweep_interval_s` | S5.* to S10.* |
| `escrow_settler` | Escrow settlement: finds jobs in `settling` or draining `cancelling`, posts the `settle` transaction (levy, refund, closure at exactly zero), and stops jobs past `job.max_overrun_ratio` of their quote with closure reason `overrun_timeout`. Triggered inline when possible, but always also swept, so settlement never depends on an event | `ops.ttl_sweep_interval_s` | S6.* |
| `assembler` | Builds the deliverable and manifest after `job.all_cells_accepted` | `ops.ttl_sweep_interval_s` | S5.*, S9.* |
| `credit_expirer` | Credit expiry: lots past `expires_at` with remainder are moved to the Reserve by `expire` postings, oldest first, batched per member | `credit.expiry_sweep_interval_s` | S6.* |
| `reserve_retirer` | Retires Reserve excess above `reserve.ceiling_credits` when the excess is at least `reserve.retire_min_credits` | `reserve.retire_interval_s` | S6.* |
| `audit_sweeper` | Audits: re-leases audit and third-execution cells not returned, closes `Audit` machines, schedules the third execution on mismatch | `ops.ttl_sweep_interval_s` | S8.* |
| `metric_rollup` | Metric rollups: v per job type over `price.v_window_days` (minimum `price.v_min_sample_cells`), η, claim ratio, mint-cap utilization, concentration, reliability estimates; monthly `MetricSnapshot` per `price.publish_period_days` | `metrics.rollup_interval_s` | S6.*, S13.* |
| `inflation_governor` | If the claim ratio passes `inflation.claim_ratio_threshold_weeks`, lowers `mint.monthly_cap_credits` by `inflation.mint_cap_cut_ratio` as principal `system`, through the config write path with a public change-log entry (a tightening, effective at once) | `metrics.rollup_interval_s` | S6.* |
| `ledger_invariant_checker` | Tier 2 checks (4.6.4) | `ledger.invariant_check_interval_s` | S6.* |
| `ledger_full_recompute` | Tier 3 checks | `ledger.full_recompute_interval_s` | S6.* |
| `ledger_checkpointer` | Tier 4 checkpoint | `ledger.checkpoint_interval_s` | S6.*, S12.* |
| `capacity_forecaster` | Capacity forecast: verified throughput over `admission.forecast_window_days` and active donors over `admission.active_donor_window_days`, times (1 - `admission.forecast_haircut`), per category supply gauges; writes a `capacity_forecasts` row that `quote` reads; then promotes waitlisted jobs that now fit | `admission.forecast_refresh_s` | S6.* |
| `retention_purger` | Applies the retention classes of S0.7: job payloads, IP hashes, sessions, request and ops logs, raw events, moderation data, inactive members (`retention.member_inactive_days`), orphan blobs | `ops.purge_interval_s` | S10.* |
| `backup_runner` | Snapshot, log archiving check, encryption and upload; verifies the last artifact is restorable by checksum | `ops.backup_interval_s` | 4.12 |
| `outbox_relay` | Delivers events (4.7.3) | `ops.outbox_relay_interval_s` | 4.7 |
| `scheduler_watchdog` | Detects overdue jobs, clock skew, stale checkpoints, stale backups | `ops.ttl_sweep_interval_s` | 4.11 |

Template auto-pause on reports (`template.autopause_report_count` within `template.autopause_window_s`) is not a job: it is evaluated inline when a report is filed, so a tightening is not delayed by a sweep [D].

### 4.8.3 Idempotency by job [D][A]

The runner rule of 4.8.1 (state-based, compare-and-set, safe to run twice at once) is made concrete per job. A second or concurrent run must find nothing left to do or return the stored result.

| Job | Idempotency mechanism | Second run |
| --- | --- | --- |
| `lease_reaper` | Compare-and-set `Lease` `active` to `expired` on `row_version`; the cell requeue and `attempt` increment are in the same commit as the winning compare-and-set (`AC-arch-12`) | Loser of the race changes nothing |
| `ttl_sweeper` | Each transition is a compare-and-set from its pending state | Finds no row in that state |
| `escrow_settler` | `settle` posting keyed by (`settle`, escrow id) under LC-7; escrow closed at exactly zero | Returns the stored result; no entry added |
| `assembler` | At most one `Deliverable` per job (unique key on job id) | Finds it and stops |
| `credit_expirer` | `expire` posting keyed by (`expire`, lot id); the lot remainder is read inside the transaction | Remainder is zero; nothing posted |
| `reserve_retirer` | The excess over `reserve.ceiling_credits` is recomputed inside the posting transaction; `retire` keyed by (`retire`, run window) | Excess below `reserve.retire_min_credits`; nothing posted |
| `audit_sweeper` | Compare-and-set on the `Audit` machine; at most one open audit per cell and round | No due audit |
| `metric_rollup`, `capacity_forecaster` | Output rows keyed by (metric or forecast, window end) and recomputed from source tables, so a rerun writes the same values | Same row, same values |
| `inflation_governor` | One automatic cut per rollup window, keyed by the window id in the `ParameterVersion` reason | Finds the version for that window; no second cut |
| `ledger_invariant_checker`, `ledger_full_recompute` | Read-only; `Alarm` deduplicated by `alarm_key`; engaging a kill switch that is already engaged changes nothing | Same alarm row |
| `ledger_checkpointer` | Checkpoint row unique by `seq` | Same row |
| `retention_purger` | Deletes by age and class | Nothing left past age |
| `backup_runner` | Each run writes a new named artifact with a checksum; no shared state | Extra artifact, harmless |
| `outbox_relay` | Store-level claim plus consumer dedupe table (4.7.3) | Consumer ignores a repeated `event_id` |
| `scheduler_watchdog` | Read-only; `Alarm` deduplicated by `alarm_key` | Same alarm row |

The keys named here are assumptions of this part [A] that S5.* and S6.* may refine without changing the rule that every job is safe to repeat.

## 4.9 Configuration management, feature flags, kill switches, launch switches

### 4.9.1 Layers [D]

| Layer | What | Stored in | Changed by | Read path |
| --- | --- | --- | --- | --- |
| Constants (`CON`) | `credit.scale_ucr_per_credit`, `lease.nonce_bytes` and the other constants of S0.10.6 | Code | A spec change and a release | Compiled in |
| Parameters | Everything else in S0.10.6 and S16.* | `Parameter`, `ParameterVersion` (definitions shipped in a manifest in the repository, values in the store) | Admin tool through the config service (4.9.3) | `ConfigSnapshot` |
| Policy, registry, template data | Rules, flags, terms copies, templates | Entity tables (S7.*, S8.*) | Reviewer workflows | Versioned reads |
| Feature flags and experiments | `ff.<area>.<name>`, default off | `FeatureFlag`, `Experiment` | Admin tool | `ConfigSnapshot` |
| Kill switches | `kill.<scope>`, default released | `KillSwitch` | Operator engages; two operators release | Read inside the guarded transaction |
| Launch switches | `launch.members_may_join`, `launch.member_jobs_enabled`, `launch.minting_enabled` | Parameters with a special write path | Only `LaunchGate.applySignedOff` (S14.*) | Read inside the guarded transaction |
| Bootstrap | Origins, store locations, role selection, environment name (4.13.2) | Process environment | Deployment | At start; never changes at runtime |

### 4.9.2 Snapshot and epoch [D][A]

- `config_epoch` is a store-wide integer incremented in the same commit as any change to a parameter, policy version, feature flag or kill switch. It is stamped on every event (4.7.2) and on every job at admission, so the versions in force can be reconstructed with `valueAt(name, epoch)`.
- A `ConfigSnapshot {config_epoch, taken_at, valid_until, parameters, flags, kill_switches, policy_version_id}` is taken once per request or job run and used for the whole of it, so one request never sees two configurations. `valid_until` is the earliest upcoming `effective_from`, so scheduled loosenings take effect on time without a cache flush.
- Snapshots are cached in process for at most `ops.config_cache_ttl_s`. For anything that moves credit, creates a job or issues a lease, the unit of work re-reads the epoch inside the transaction; if it moved, the snapshot is reloaded and the guards re-run. A stale cache can therefore delay a screen hint but never a brake.
- Parameter definitions are generated from the S16.* table into `config/parameters.manifest`. CI fails when a name in S0.10.6 is missing, when code reads a name through anything but the typed accessor, or when a domain module defines a numeric constant that duplicates an `initial configurable default`. Migrations seed new parameters at version 1 with `effective_from` equal to the migration time and never overwrite an existing value (4.10).

### 4.9.3 Parameter write path [D]

```text
applyChange(ctx, name, new_value, effective_from, reason):
  require perm for the parameter's owner role                       // S0.10.5
  validate type, range, enum, and constraints C1..C8                // S0.10.3; failure = VALIDATION_FAILED
  class := tighten | loosen | neutral from tighten_direction        // R10
  if class != tighten: require effective_from >= now + notice_days  // prospective only
  if class == loosen or name in security.two_person_actions: require a second approver
  if name starts with launch.: reject                               // only LaunchGate.applySignedOff may write
  in one unit of work: insert ParameterVersion; insert ChangeLogEntry (public unless security.*);
     insert AdminAction (or system actor); bump config_epoch; emit parameter.changed
  tighten: effective now; the public entry follows within change.tighten_publish_within_s
```

### 4.9.4 Flags, experiments, kill switches [D]

- Evaluation order for an operation: kill switch, then launch switch, then feature flag, then parameter. An unknown flag name evaluates to off, as `unknown` evaluates to `no` (S0.8.3).
- Experiment assignment is deterministic (a keyed hash of experiment id and member id, seed `experiment.assignment_seed_version`), made at most once per member and experiment, and written as an `ExperimentAssignment` row in the same commit as its first use. The mechanism and unit of randomization are owned by S13.*; this part requires only that it is deterministic, logged and independent of the member's behavior.
- Kill switches take effect inside the transaction that would cross them, not through cache invalidation:

| Switch | Enforced at | Effect |
| --- | --- | --- |
| `kill.all_minting` | `LedgerService.post` for `mint` | `KILL_SWITCH_ENGAGED`; Commons cells may still be accepted without credit only as S6.* defines |
| `kill.all_new_jobs` | `createJob`, `submitJob`, `confirmEscrow` | Refused; running jobs continue |
| `kill.template.<id>` | Lease issuance, `submitJob` | Template `paused`; its jobs `suspended`; no lease for its cells |
| `kill.service.<id>` | Lease issuance, `submitJob` | Service `suspended`; cells needing it not shown; in-flight handling per S7.* |
| `kill.member.<id>` | Authentication and lease issuance | Principal refused |

- Engaging is one operator and immediate; releasing needs two operators (`security.two_person_actions`). Every change writes `KillSwitch`, `AdminAction`, an event and an epoch bump.
- Launch switches: `members_may_join` is checked in `createMember` and in `leaseNextCell` (4.16 F1, `AC-bm6-01`), `member_jobs_enabled` in `submitJob` and `confirmEscrow` (`AC-bm7-01`), `minting_enabled` in `post` for `mint`; each refuses with `LAUNCH_GATE_CLOSED`. The only writer is `LaunchGate.applySignedOff`, which re-evaluates the gate rule of S14.* in the same commit. No environment variable, header, role or build flag bypasses it; dev, test and staging pass the same sign-off flow with synthetic administrators and synthetic evidence, and their data is labeled `synthetic` [D].

## 4.10 Migrations

### 4.10.1 Rules [D]

- Migrations are ordered, immutable once released and checksummed; `schema_migrations(version, checksum, applied_at, duration_ms)` records them. The runner takes an exclusive lock and runs as the `migrator` role. Production and staging are forward-only; down scripts exist for dev convenience only. A failed migration is fixed forward or the pre-migration restore point is used (4.12).
- Expand/contract: release N adds nullable or new structures and writes both; N+1 reads the new; N+2 removes the old. The application at versions N and N-1 must both run against schema N, which makes rolling deploys and application rollback safe.
- A migration declares its lock impact; large tables use online index builds and batched backfills of `ops.migration_batch_size` rows, resumable and idempotent. Seeds of parameters, flags and kill switches follow 4.9.2.
- A pre-migration restore point is taken automatically before any production migration.

| Class | Allowed | Extra rule |
| --- | --- | --- |
| Schema expand or contract | Yes | Contract steps only after the expand release is fully deployed |
| Data backfill | Yes | Idempotent, resumable, batched |
| Seed (parameters, flags, kill switches, gate items) | Yes | Never overwrites a value |
| Ledger-touching | Only with a numbered spec change, two-person approval, a full invariant recompute and chain verification before and after, a checkpoint before and after, and forward correcting entries (`reversal`); rows are never edited. Changing `credit.scale_ucr_per_credit` is this class (S0.6.1) | Blocked otherwise |

### 4.10.2 Append-only enforcement [D]

The authoritative list is every S5.* table that has no `updated_at` and no delete path. At minimum: `ledger_entries`, `ledger_transactions`, `parameter_versions`, `policy_versions`, `terms_copies`, `flag_answers`, `admin_actions`, `change_log_entries`, `metric_snapshots`, `calibration_records`, and approved `template_versions`. For each, the migration revokes update and delete from `app_rw` and adds a rejecting trigger or equivalent. A migration test enumerates the list and fails if any table lacks both protections. Permanent tables hold no personal data by construction (S0.7), so retention never needs to edit them.

### 4.10.3 Migration tests [D]

CI applies all migrations to an empty store and to the previous release's schema loaded with synthetic fixtures; runs the contract suite of every port driver; checks the append-only list; runs the full invariant recompute on a fixture ledger before and after; and measures duration against the declared lock impact.

## 4.11 Observability

### 4.11.1 Logs without personal data [D]

- One logging facade, `log.event(name, fields)`. Each event name has an allowlist schema; unknown fields are dropped and counted in `hamyar_log_dropped_fields_total`. Event names follow S0.5 (`<area>.<event>`, the same names as domain events); operational names `http.request_served`, `sched.run_finished`, `outbox.relayed` and `alarm.raised` are convention additions (`ISS-45`).
- Never logged, by construction: raw IP or any value derived from it, user agent, e-mail, display names, prompts, outputs, uploads, report or appeal text, request or response bodies, headers (including `Authorization`), cursors, file names, exception messages that may quote input (only `error.code` and scrubbed frames are kept).
- Request logs carry `request_id`, route template, status, duration, response size, `principal_type`, `auth_scheme`, `config_epoch`. They carry no member id. Domain-event logs carry the aggregate's id (`cel_`, `job_`) and `actor.principal_type`, not `mem_` ids. Reason: logs are the weakest-protected store, so they must not link a member to activity; that link exists only in the system of record under access control [A: if investigators need member ids in logs, that is an owner decision with a retention cost, S3.*].
- Retention: `retention.request_log_days` for request logs, `retention.ops_log_days` for the rest. Logs leave the host only to a `LogSink` the operator controls; a third-party log service is not used by default, because even sanitized logs reveal traffic patterns [A][V: counsel and G1].
- Canary test [D]: fixtures feed a fake IP, e-mail, prompt text and token through every endpoint; the test fails if any canary appears in captured logs, metrics, traces, alert payloads or error bodies (`AC-arch-08`).

### 4.11.2 Metrics [D]

Names follow S0.5 (`hamyar_<area>_<name>_<unit>`). Labels come from closed sets (surface, route template, status class, job type, template id, service id, outcome, job name); never member, job or cell ids. Anything published publicly is suppressed below `analytics.min_cohort_k`.

| Metric | Type | Purpose |
| --- | --- | --- |
| `hamyar_api_requests_total`, `hamyar_api_request_duration_seconds` | counter, histogram | Traffic, latency, error ratio |
| `hamyar_api_rate_limited_total` | counter | Limiter activity by bucket |
| `hamyar_ledger_append_duration_seconds`, `hamyar_ledger_serialization_retries_total` | histogram, counter | Posting throughput against 4.6.2 |
| `hamyar_ledger_invariant_violations_total` | counter | Invariant failures by id and tier |
| `hamyar_ledger_checkpoint_age_seconds`, `hamyar_ledger_chain_verified_seq` | gauge | Tier 3 and 4 health |
| `hamyar_cell_queue_depth_cells` | gauge | Queue by template and service requirement |
| `hamyar_lease_expired_total`, `hamyar_lease_submit_to_accept_seconds` | counter, histogram | Lease health |
| `hamyar_submission_outcomes_total` | counter | Accept and reject mix by outcome |
| `hamyar_verify_gold_fail_total`, `hamyar_verify_audit_mismatch_total` | counter | Verification signals |
| `hamyar_mint_utilization_ratio`, `hamyar_claim_ratio_weeks`, `hamyar_reserve_balance_credits` | gauge | Economy gauges (S6.*) |
| `hamyar_sched_run_duration_seconds`, `hamyar_sched_run_overdue_seconds`, `hamyar_sched_run_failures_total` | histogram, gauge, counter | Job health by job name |
| `hamyar_outbox_lag_seconds`, `hamyar_outbox_dead_total` | gauge, counter | Event delivery |
| `hamyar_clock_skew_seconds`, `hamyar_db_pool_in_use_connections` | gauge | Infrastructure |
| `hamyar_backup_age_seconds`, `hamyar_restore_drill_age_days` | gauge | Recovery readiness |
| `hamyar_config_epoch_count` | gauge | Detects instances on a stale epoch |

### 4.11.3 Alarms [D]

An `Alarm` row has an `alarm_key`, severity (`critical`, `major`, `warning`), the metric and value that fired it, and an acknowledgement (`AdminAction`). Payloads contain no personal data. Alarms deduplicate by key. The admin tool always shows them; an operator-configured `AlertSink` may also deliver them [V: sink choice and its reachability, G1].

| `alarm_key` | Condition | Severity | Automatic response |
| --- | --- | --- | --- |
| `alarm.ledger_invariant_violated` | Any tier 2 or 3 failure, or a chain mismatch | critical | Engage `kill.all_minting` and `kill.all_new_jobs` (below) |
| `alarm.checkpoint_stale` | Checkpoint age over twice `ledger.checkpoint_interval_s` | major | None |
| `alarm.sched_overdue` | A job overdue by `ops.job_overdue_factor` | major | None |
| `alarm.outbox_lag`, `alarm.outbox_dead_letter` | Lag over `ops.outbox_lag_alarm_s`; any dead row | major | None |
| `alarm.clock_skew` | Skew over `ops.clock_skew_alarm_s` | major | None |
| `alarm.error_rate` | 5xx ratio over `ops.alert_error_ratio` within `ops.alert_window_s` | major | None |
| `alarm.backup_stale`, `alarm.restore_drill_overdue` | Backup older than twice `ops.backup_interval_s`; drill older than `ops.restore_drill_interval_days` | major | None |
| `alarm.mint_utilization` | Above `inflation.mint_utilization_alarm` | warning | None |
| `alarm.eta_low`, `alarm.false_accept_high`, `alarm.false_reject_high` | Below `price.eta_alarm_threshold`; above `verify.false_accept_alarm` or `verify.false_reject_alarm` | major | None (pre-registered thresholds, S13.*) |
| `alarm.reserve_empty` | Reserve at or below `grant.reserve_floor_credits` | warning | Grants pause by rule |
| `alarm.secret_rotation_due`, `alarm.service_review_due` | Past `security.secret_rotation_days`; `service.review_due` event | warning | None |

Automatic brake [D][A]: on `alarm.ledger_invariant_violated` the system itself, as principal `system`, engages `kill.all_minting` and `kill.all_new_jobs`; releasing them needs two operators and a passing full recompute. Reason: fail closed on integrity. Risk: a false positive halts the system, which the founders may prefer to decide by hand (S3.*). The brake is performed by the checker's own transaction, not by the event consumer, so it does not depend on the relay.

Request correlation: `request_id` is generated at the edge, echoed in `X-Request-Id`, and passed as `causation_id`. Traces, if used, carry no payload attributes. `/v1/public/health` returns liveness and `build_id` only; detailed readiness is an admin operation (S15.*).

## 4.12 Backup and recovery

### 4.12.1 What is protected [D]

| Data | Method | Notes |
| --- | --- | --- |
| Transactional store | Base snapshot every `ops.backup_interval_s` plus continuous log archiving for point-in-time recovery [V: host support] | Loss bound `ops.rpo_s`; restore time target `ops.rto_s` |
| Blob store | Versioned or replicated copy; blobs are write-once, so copies cannot diverge | Integrity by content hash |
| Configuration manifests, migrations, policy seeds | Source repository | Not secret |
| Secrets | Not in backups; recovered through the custody procedure of S10.* | Two custodians [A] |
| Ephemeral store, caches, logs | Not backed up | Rebuilt or lost by design |

Artifacts are encrypted before they leave the host with a key the backup sink does not hold (`secret.backup_key`, name proposed [A], owned by S10.*), and are stored in at least two independent locations behind `BackupSink`, retained `ops.backup_retention_days`. A deletion in the primary reaches backups only when they age out; whether that satisfies privacy duties is a counsel question [V] (`ISS-47`).

### 4.12.2 Restore procedure with verification gates [D]

1. Restore into an isolated environment to the target time. Never restore over production first.
2. Check `schema_migrations` against the expected release.
3. Run the tier 3 recompute: it must pass.
4. Verify the hash chain from genesis to the restored head.
5. Compare with the last published checkpoint: the restored head must have `seq` at or above the checkpoint's and the same hash at that `seq`. If the head is below it, a rollback occurred: declare a data-loss incident.
6. Production cut-over keeps `kill.all_minting` and `kill.all_new_jobs` engaged until two operators release them.
7. Open leases expire by themselves; submissions lost inside the loss window are re-executed through normal acceptance. The platform never fabricates or edits ledger rows to cover a gap; the incident and the gap are published through the change log (S12.*).
8. If host compromise is suspected, rotate every secret before reopening.

| Scenario | Detection | Response |
| --- | --- | --- |
| Host unreachable or blocked for members | Reachability measurements (4.15), error-rate alarm | Move host through the ports; restore from backup if needed |
| Corruption or operator error | Tier 2 or 3 alarm | Automatic brake, restore procedure |
| Rollback or tampering with the store | Checkpoint comparison, chain verification | Data-loss incident, restore procedure |
| Loss of one backup location | `alarm.backup_stale` | Re-seed from the other |
| Seizure or compelled disclosure of a host | Out of band | S10.* (what the host can see); backups are encrypted |

### 4.12.3 Drills [D]

A restore drill every `ops.restore_drill_interval_days` and before launch (BM9), following 4.12.2 on staging with synthetic data, logged with duration against `ops.rto_s`. A portability drill exports everything to neutral formats (SQL dump, blob manifest, configuration) and imports into a fresh environment on a different host class, proving the ports hold (`AC-arch-10`).

## 4.13 Deployment and environments

### 4.13.1 Environments [D]

| Environment | Purpose | Data | Launch switches | Secrets |
| --- | --- | --- | --- | --- |
| `dev` | Local work | Synthetic; in-memory fakes or a local store; origins may collapse | Off | None real |
| `test` | CI, ephemeral per run | Synthetic fixtures; a real transactional store (not a fake) for contract and ledger tests; deterministic `Clock` and `Random`; no network except the package registry | Off until a test signs off through the real flow | None real |
| `staging` | Production-like rehearsal: migrations, restore and portability drills, load tests, reachability tests | Synthetic only; never a copy of production | Same flow, synthetic administrators | Its own |
| `prod` | Real operation | Real | `false` at every build; flipped only by sign-off (S14.*) | From `SecretStore`; production secrets never exist elsewhere |

Staging and production are built from the same infrastructure description and the same artifacts; only bootstrap settings differ.

### 4.13.2 Bootstrap settings [D]

The only settings outside the parameter table. Everything else is a parameter (4.9).

| Setting | Meaning | Secret |
| --- | --- | --- |
| `HAMYAR_ENV` | `dev`, `test`, `staging`, `prod` | no |
| `HAMYAR_ROLES` | `api`, `jobs` or both | no |
| `HAMYAR_STORE_URL`, `HAMYAR_BLOB_URL`, `HAMYAR_EPHEMERAL_URL` | Store locations and credentials | yes |
| `HAMYAR_PUBLIC_ORIGIN`, `HAMYAR_APP_ORIGIN`, `HAMYAR_API_ORIGIN`, `HAMYAR_ADMIN_ORIGIN`, `HAMYAR_ADMIN_API_ORIGIN` | The five origins (4.3.3) | no |
| `HAMYAR_SECRET_SOURCE` | Where `SecretStore` reads from | no |
| `HAMYAR_BUILD_ID` | Content hash of the build; shown on health | no |

The process refuses to start when `HAMYAR_ENV` is `staging` or `prod` and any origin is local or not HTTPS, when two origins are equal, or when a required setting is missing (fail closed).

### 4.13.3 Pipeline [D]

| Stage | Gate |
| --- | --- |
| Static checks | Types, lint, import-boundary rules, forbidden sinks (4.3.3), pinned dependency lockfile, license and vulnerability scan, secret scan, parameter manifest check (4.9.2) |
| Tests | Unit, property, state-machine, policy, migration (4.10.3), port contract suites, API conformance against S15.*, log canary (`AC-arch-08`) |
| Build | Reproducible server image and static bundles with content hashes; bundle size against the budgets owned by S11.* |
| Staging | Deploy, smoke, end-to-end, reachability probe |
| Production | Manual approval by a second maintainer [A: owner decision if the team is one person, S3.*], pre-migration restore point, rolling deploy (N and N-1 compatible), post-deploy smoke |

Rollback is roll-forward or redeploy of the previous artifact, which is safe because of expand/contract; configuration epochs are never rolled back. No runtime fetch of code or assets from a third party exists; build-time dependencies come from a pinned lockfile and, where feasible, a vendored offline cache [A]. The panel's release script checks that required secret names exist and runs tests before deploy (PR§7.6); that pre-deploy check is kept (4.18).

Rotate-before-exposure [D]: existing secrets of the panel (PR§4, including the fifth, `EXT_TOKEN`, `ISS-48`) are never reused as Hamyar secrets. The pre-exposure checklist item under G4 requires every secret in use to have been issued after the repository or host became reachable to anyone but the founders [V: operator, evidence in `LaunchGateItem`].

## 4.14 Service-adapter interface

### 4.14.1 Purpose and hard limits [D]

A Service-adapter turns one prompt and one registry descriptor into the actions a human takes: copy the prompt, and open the service, with the prompt prefilled only where the registry says that is supported. No provider is hardcoded: every capability below is data recorded by a reviewer [V]. Hard limits (ground rule 3, FD Principle 3):

- It runs in the member's browser, is pure (no network, no storage, no timers), and never reads the chat page, its URL, its DOM, or the clipboard.
- Its only outputs are (a) a clipboard write on the member's tap, (b) a link the member taps to open the service in a new browsing context with `rel="noopener noreferrer"`, and (c) text shown on screen. It keeps no handle to the opened page, posts no message to it, never embeds it in a frame, and never presses Send.
- Paste-back is the member pasting into our own text field with the platform's own paste gesture. The programmatic clipboard-read API is not used.

### 4.14.2 Descriptor (derived by the service registry) [D]

| Field | Type | Source | Meaning |
| --- | --- | --- | --- |
| `service_id` | `svc_` id | Registry | Which service |
| `adapter.supports_prefill` | bool | Reviewer [V: tested on real phones and desktops, G2] | The service opens with a prompt carried in the link |
| `adapter.prefill_url_template` | string or null | Reviewer [V] | HTTPS template with exactly one `{prompt}` placeholder |
| `adapter.max_url_chars` | int or null | Reviewer [V] | Longest accepted URL, counted in characters of the final URL |
| `adapter.copy_only` | bool | Reviewer; forced true when prefill is not supported or `prefilled_link_use` is not `yes` | Copy button only |
| `adapter.open_url` | string or null | Reviewer [V] | Plain HTTPS address that opens the service without a prompt (`ISS-45`) |
| `adapter.clean_chat_hint_key` | copy key | Reviewer | Advice shown with the buttons, for example use a clean chat with memory off (FD§5.5) |
| `mode_allowed` | list | Computed | `[copy_only]` or `[prefill, copy_only]` |

The server computes `mode_allowed`; the client cannot widen it. Rules [D]:

- `unreviewed`, `in_review`, `rejected`, `suspended` and `revoked` services return `copy_only` with no `open_url`: nothing is opened for a service that is not `approved`. An unreviewed entry has every capability false or null (unknown is no).
- `prefill` is allowed only when `supports_prefill` is true, a template and limit are present, and the `prefilled_link_use` flag is `yes` with a saved `TermsCopy`.
- At write time the registry validates a template: scheme `https`; no user information; exactly one `{prompt}`, in the query or fragment and never in the host; no other placeholders. The template is dated registry data; a change is an `AdminAction` and a change-log entry (S7.*).

### 4.14.3 Planning algorithm [D]

```text
plan(prompt_text, d: AdapterDescriptor) -> AdapterPlan:
  actions := [ CopyPrompt(prompt_text) ]                         // always first and always present
  if "prefill" not in d.mode_allowed: return CopyOnly(actions, open_link = d.open_url, reason = not_allowed)
  url := d.prefill_url_template with {prompt} replaced by percent_encode_utf8(prompt_text)
  if length(url) > d.max_url_chars: return CopyOnly(actions, open_link = d.open_url, reason = url_too_long)
  return Prefill(actions + [ OpenLink(url) ])
```

The encoded URL is ASCII, so character count and byte count agree. Mixed-direction and Persian text survives because encoding is over UTF-8; bidi display of the prompt is S11.*. The prompt text reaches the client only inside an active lease (S9.*). A prefilled URL puts the cell prompt, which is S0 or S1 text, into the member's browser history and possibly the provider's logs; this is why `copy_only` is the default and why the card says so [H: whether that matters to members is an interview question, S13.*].

### 4.14.4 What is verified, where it is stored [V]

| Fact | Verified by | Stored in |
| --- | --- | --- |
| Prefill works, template, length limit, per device class | Reviewer with real devices (G2) | `ServiceRegistryEntry` `adapter.*` fields; `CalibrationRecord` for the test run |
| Terms permit prefilled links and copy-and-paste | Reviewer reading the saved terms (G0) | `FlagAnswer` for `prefilled_link_use` and `human_copy_paste_use` |
| Clean-chat advice is accurate for the service | Reviewer | `copy.*` key text, marked `needs_human_and_legal_review` |

Adding a service is therefore data entry plus review; no code release is needed, and the client bundle contains no provider name or URL (`AC-adapter-03`).

## 4.15 Hosting, storage portability and reachability from Iran [V]

### 4.15.1 Decisions [D]

- Hosting and storage are reached only through the ports of 4.6.1; nothing outside a driver names a host product. Moving host is a driver and bootstrap change plus a restore or import (the portability drill, 4.12.3).
- Reachability of every origin from Iran is not known [V]. It is measured, not assumed, and no host is chosen for production before the measurement exists (G2). Result storage: `LaunchGateItem` evidence under G2, with the measurement protocol below.
- The platform has no mandatory third-party runtime dependency. Fonts, scripts and styles are bundled and served from the same origin; no CDN is required (a CDN may be used only as an optional cache in front of a bundle, never as the only copy, and never for the API). The license of any bundled Persian and Latin font must allow self-hosting [V: operator, evidence in `LaunchGateItem`].
- If an origin is unreachable for members, the response is to change the platform's own host. Relays, tunnels, mirrors aimed at evading blocking, and circumvention advice are excluded (4.2.2).
- Low bandwidth: static bundles are content-hashed and cacheable; compression is on; API lists are paginated and small (`api.page_size_*`); no render-blocking third-party request exists; size budgets are owned by S11.* and enforced in the pipeline (4.13.3).
- TLS is required on every origin; OCSP stapling is enabled where the host supports it so clients need not contact a certificate authority's responder [V: host support]. Registrar, DNS provider and certificate authority are dependencies recorded in the G2 hosting checklist.

### 4.15.2 Measurement protocol (G2) [V]

| Step | Detail |
| --- | --- |
| What | For each candidate host and each origin: name resolution, TLS handshake, fetch of the public site bundle, a call to `/v1/public/health`, and a full first-contribution run in staging |
| From where | Several consumer networks and device classes, run by founders and testers who consent; from inside Iran only if that is safe for the tester (G1 decides) |
| What is recorded | Success, timing class, failure stage, network class. No IP address, location or identity of the tester is stored |
| Where stored | `LaunchGateItem` evidence under G2 and `CalibrationRecord` rows of type reachability |
| Decision rule | Pre-registered before the run by the founders (`FND`); a host that fails is not used |

What the host and a network observer can see, and what happens on seizure, is owned by S10.*; this part only guarantees that the architecture lets the host change.

## 4.16 Key flows and transaction boundaries

These show which components act and which writes commit together. States and guards are in S5.*; money rules in S6.*. [D]

**F1. Lease a cell.** Member app calls `leaseNextCell`. One unit of work: read `ConfigSnapshot` and re-check epoch, kill switches and launch switches; select a queued cell whose opt-ins cover it (R8) and whose service is `approved`; compare-and-set `Cell.queued` to `leased`; insert `Lease` with a 128-bit nonce stored as a hash and `expires_at` from the store clock; insert the event rows. Commit. The rendered prompt and nonce are returned once. Two concurrent callers: exactly one commit wins the compare-and-set; the other retries or receives no cell.

**F2. Submit, check, accept, pay.** Member app posts the paste-back with the lease id and nonce and an idempotency key. One unit of work: validate nonce and size; store `Submission` (a replay returns the stored outcome and writes nothing); run inline automatic checks (bounded); decide `accepted`, `rejected` or `flagged_for_audit`; on acceptance, post the `payout` or `mint` transaction through `LedgerService.post` in the same commit; update cell state; insert events. Checks that need the check runner or a second donor make the cell `flagged_for_audit` and finish later in the `audit_sweeper`; the member sees a pending result [D].

**F3. Admit a job.** `submitJob`: policy evaluation (pure) and stamping; template and service checks; `quote` from the stored forecast and the latest v and λ. `confirmEscrow` (separate request, within `price.quote_ttl_s`): one unit of work that re-checks the quote, capacity and kill switches, posts `escrow_hold`, creates the cells, and moves the job to `admitted`. No capacity is promised before this commit.

**F4. Revoke or suspend a service.** An admin action (second approver where required) in one unit of work: change the service state, bump `config_epoch`, engage `kill.service.<id>` if suspending, mark dependent jobs `suspended` or stopped per S7.*, write `AdminAction`, emit events. Because brakes are read inside lease and admission transactions (4.9.4), no new lease is issued after this commit. In-flight leases follow S7.*.

**F5. Settle.** `escrow_settler` finds a `settling` job; one unit of work posts the `settle` transaction (levy, refund) and closes the escrow account at exactly zero, then marks the job `completed` or `failed`. A second run finds nothing to do.

## 4.17 Recommended concrete stack, with alternatives

The choice is driven by two things stated in the brief: the ledger needs strong consistency (4.6.2), and reachability of the host from Iran is unknown [V] (4.15). Statements below about the capabilities of named products are design-level and unchecked; each is [V] against the product's current documentation by the engineer before the choice is frozen (decision memo stored as `LaunchGateItem` evidence under G2).

### 4.17.1 What the ledger forces [D]

| Need | Consequence for the store |
| --- | --- |
| Ledger, escrow, cell state and outbox in one atomic commit (LC-1, LC-9) | One store with multi-row transactions that span all of them |
| No write skew on balances and caps (LC-2) | Serializable isolation, or a single serial writer per ledger |
| One serial chain with gapless `seq` (LC-3, LC-4) | A single serialization point and transactional sequence assignment |
| Invariant queries over all entries (LC-8) | SQL aggregates on a consistent snapshot |
| Point-in-time recovery and encrypted off-host backups (4.12) | Log archiving or equivalent [V: per host] |
| Host can change (4.15) | A widely available, non-proprietary transaction model |

The panel's own storage shows why a weaker store is not enough: it has no database, uses git refs for locks, and an eventually consistent key-value namespace for counters and one-time codes, which its own review records as racy (PR§2, PR§4.5 items 3 and 6).

### 4.17.2 Options compared

| Criterion | A. Conventional server + PostgreSQL | B. Cloudflare Worker + Durable Object (ledger) + D1 | C. Single binary (Go or similar) + SQLite with replication | D. Server + managed PostgreSQL |
| --- | --- | --- | --- | --- |
| Atomic ledger + state + outbox (LC-1, LC-9) | Native | Only if all of it lives in one Durable Object; cross-object transactions are not available [V] | Native (single file) | Native |
| Isolation (LC-2) | Serializable available [V: version], with retry | Serial execution inside one object [V] | Single writer | As A |
| Chain and throughput (LC-3, LC-4) | One head row; rate measured by 4.6.2 | One object is one serial writer: simple, but a hard ceiling and a single location [V] | One writer, simple | As A |
| Backups and PITR | Mature tools; host-independent | Platform features [V] | Replication tools; weaker PITR [V] | Provider feature [V] |
| Reachability from Iran [V] | Chosen after measurement; many hosts possible | Depends on one vendor's network [V] | As A | Depends on provider [V] |
| Portability (4.15) | High | Low: Durable Object API is proprietary; the ports contain it | High | Medium |
| Operations burden | Highest of the four; offset by simplicity of one node plus archive | Lowest | Low | Low to medium |
| Cost for a small team | Low (one small host) | Low to unknown [V] | Lowest | Medium |
| Fit with the owner's panel code and skills | TypeScript runs on any server | Same runtime as the panel (PR§1) | New language | As A |

### 4.17.3 Recommendation [D][A]

| Layer | Choice | Reasons |
| --- | --- | --- |
| System of record | **PostgreSQL**, one primary, point-in-time recovery to an independent location, serializable isolation for ledger postings with bounded retry | Meets LC-1 to LC-9 without proprietary primitives; runs on any host chosen after the reachability test; mature backup, role, trigger and privilege features for 4.6.5 and 4.10.2 |
| Server | **TypeScript (strict) on a current LTS Node.js runtime**, one modular monolith (4.3.2) | The owner already works in TypeScript (PR§1); one language lets the client and server share the domain library (ids, canonical JSON, hashing, `ucr` arithmetic, validation schemas), which removes a class of client-server drift and lets the simulation harness reuse production code |
| Web | Static single-page apps built with Vite, React and TypeScript, logical (direction-neutral) CSS properties for RTL, all assets self-hosted | Reuses the owner's web stack and, if the review passes, panel components (4.18); no runtime third-party code |
| Blob store | An S3-style object API behind `BlobStore`, or the file system of the host with content-addressed names | Smallest dependency that satisfies write-once and integrity checks |
| Ephemeral store | Tables in the same PostgreSQL (4.6.1) | No second stateful dependency |
| Scheduler | In-process runner with database locks (4.8) | No external scheduler to reach or secure |
| Hosting | Not named. One small server or container host chosen after the G2 measurement; the database on the same private network or a managed instance [V] | Hosting is an owner decision (S3.*) |

Phase 1 topology (a configuration of the full topology, not a different design): one `server` instance with both roles, one primary with archived log, optional warm replica, the static bundles on the same host or a static host, no check runner. Full topology: N server instances, a replica, a separate check runner, backups in two locations.

Optional use of Cloudflare Workers is limited to serving the static public bundle behind the `StaticHost` port if the reachability test favors it [V]. No such worker holds a secret or touches the ledger.

### 4.17.4 Alternatives and when to choose them

| Alternative | Choose when | Cost |
| --- | --- | --- |
| B. Worker + Durable Object + D1 | The owner prefers minimal operations and the reachability test shows that vendor's network works from Iran and is acceptable to members [V]; measured posting rate fits one object | The ledger actor must hold all state that changes with money; lock-in; a single serial writer is the ceiling; the `LedgerStore` contract (LC-1 to LC-9) must still be demonstrated by the contract suite |
| C. Single binary + SQLite with replication | Operations must be minimal and the team can accept a single writer node | Weaker recovery tooling; language change |
| D. Server + managed PostgreSQL | The team wants no database administration | Provider reachability and compelled-disclosure exposure to assess [V] |
| Not recommended: a document or key-value store as the ledger | Never | Cannot meet LC-2 and LC-8 without rebuilding transactions |

Whichever is chosen, the contract suites of 4.5 decide acceptance: a driver that fails LC-1 to LC-9 is rejected regardless of its other merits.

## 4.18 Existing panel: keep / wrap / replace

Fact base: `docs/source/panel-review.md` (PR§n), a static reading of `github.com/abbashaji/panel` by the owner's tooling. Nothing was executed, deployed or tested, the clone has one commit, and PR§9 lists what could not be determined (library internals, token scope, live behavior, test status). This table does not assume any behavior beyond what PR lists, and it is not the G4 sign-off: G4 stays open until a human reviews the code (`ISS-49`) [V]. Decision words: **keep** (use the concept or code as is), **wrap** (use it behind a new seam), **replace** (build new; the old part does not carry over), **exclude** (not part of Hamyar).

| Item | Decision | Reason | [V] condition |
| --- | --- | --- | --- |
| Cell concept (independent unit of work with attempts and a needs-split outcome) | keep the concept, replace the implementation | PR§3.1 derives status lazily from git per request and stores nothing; Hamyar needs stored state in a transactional store (4.6). Panel statuses map: `done` to `accepted`, `running` to `leased`, `ready` and `expired` to `queued`, `needs_split` to `exhausted`; `waiting` has no counterpart because Hamyar cells inside a job are independent (FD§2); `needs_human` (a cell whose last commit is a feedback request, PR§3.1) has no counterpart either: Hamyar escalates through `flagged_for_audit`, reports and operator actions | Mapping holds only if PR§3.1 matches the code; confirmed in the G4 review |
| Lease with a time box and attempt counter | keep the concept, replace the implementation | PR§3.2 and PR§3.3: expiry is evaluated only when someone calls and comes from the commit date of a branch tip; there is no scheduler. Hamyar uses a server-side lease with a nonce, store-clock `expires_at` and a reaper (4.8). Lease length is seconds to minutes, not the panel's 60 minutes | G4 review of how expiry was meant to be enforced |
| Fencing (a write must carry the current tip, stale writers get CONFLICT) | keep the concept, replace the implementation | PR§3.3: fast-forward-only updates with `base`. Hamyar's equivalent is compare-and-set on `row_version` plus the lease nonce (F1, F2) | None beyond G4 |
| Claim race resolved by creating a git ref; advisory reservation in key-value storage | replace | PR§3.3 and PR§2.2: the lock is a git ref, the reservation is advisory and eventually consistent. Hamyar needs an atomic transition in the system of record (LC-1, 4.6.3) | None |
| Hand-out order (expired critical first, then priority and chain depth) | keep the idea, replace the rules | PR§3.2: a deterministic ordering function is the right shape (whether its tests pass is not known, PR§9). Hamyar's order is eligibility by opt-in (R8) then first-come within a deadline class (FD§4.8), as a pure function | None |
| Status graph UI (left-to-right dependency graph, status colors and labels) | wrap | PR§1: `web/src/graph` and the status mapping exist; that `PanelState` is built by a pure function over a snapshot is PR§8 opinion, not fact [V]. Reuse behind a new data adapter for the requester's per-cell map and the operator's capacity view; Hamyar cells are independent, so the dependency layout is optional; the member flow is new | Review of Persian right-to-left rendering, accessibility, bundle size and absence of third-party loads; PR§4.5 item 12 records web fonts loaded from third-party hosts, which are removed. If the review fails, replace |
| Bottleneck view (cell with most transitive dependents) | keep the concept, replace the computation | PR§3.5. Hamyar's bottleneck is a capacity one: which template, service class or opt-out category is limiting quotes (FD§5.7 item 8), computed from rollups (4.8, S13.*) | None |
| Release / Hand over (owner revokes a stuck cell, success text, refusal while CI runs, feedback gate) | keep the concept as operator tools, replace the implementation | PR§3.4: an owner action that returns a cell to the queue, fenced and logged. Hamyar: operator revokes a lease (`lease.revoked`), requeues or voids a cell, with a reason, `AdminAction` and two-person rules where configured; a volunteer can decline without penalty (FD§5.5). The CI guard has no counterpart | Panel behavior is read, not run (PR§9) |
| Launcher (`blueprint://` protocol, Windows-only, browser profile selection, fixed prompt template) | replace | PR§6: Windows-only and tied to one provider's prefill URL; FD§10 and Principle 7 require a no-install web flow and Service-adapters (4.14). Its URL validator and fixed-template discipline are a good pattern and are reflected in the descriptor validation of 4.14.2 | Whether the provider prefill behavior it assumes is real is unverified in PR§9 and is irrelevant to Hamyar |
| Auto-send userscript and launcher chat-link record | exclude | PR§6.4 and PR§6.5: the userscript clicks Send and the launcher records chat URLs; ground rule 3 and FD Principle 3 forbid both (`ISS-46`) | None |
| Four secrets (`PANEL_TOKEN`, `ADMIN_TOKEN`, `GITHUB_TOKEN`, `MCP_AUTH_TOKEN`) and the fifth, `EXT_TOKEN` | replace | PR§4: shared passwords, one principal `owner`, a cookie that cannot be revoked, an admin key typed into a page and optionally kept in browser storage (PR§4.5 items 1, 2, 5, 7). Hamyar uses per-member keys and per-admin passkeys (S0.6.4, S0.11.4), no git token at runtime, no MCP surface. All five are rotated before any public exposure and never reused (4.13.3) | Token scopes and the library's behavior are unknown (PR§9) |
| Git as state, key-value store, in-memory caches | replace | PR§2: no database; git branches and commits are the state; the key-value store is advisory. Hamyar's state is the transactional store; the ephemeral store holds only counters and challenges (4.6.3) | None |
| Result path (commits, pull request, CI artifact) | replace | PR§5: no output store of its own. Hamyar returns results by paste-back with a lease nonce (F2, S9.*) | None |
| Per-request GitHub queries for state | replace | PR§8 and PR§3.1: one snapshot query plus per-cell calls will not scale to many members; indexed queries in the store do | None |
| Merge gate pattern (trusted checkout, untrusted code in a job without secrets, merge only the verified commit) | keep as a pattern | PR§7.5 and PR§4.5 item 13: used for Hamyar's own pipeline (4.13.3) and as the model for the check runner (4.4.4) | G4 review of the workflow files |
| Pure state function with a twin and shared fixtures; in-memory fake of the external interface | keep as a pattern | PR§7.1: the practice behind 4.5 | None |
| Cloudflare Worker runtime and static assets hosting | keep as an option | PR§1: usable for the static public bundle or as alternative B (4.17.4), subject to reachability | Reachability from Iran [V] (PR§9) |
| `GitHubApi`-style seam, `redact()` and constant-time compare helpers, bounded request bodies | wrap | PR§8: small reusable helpers; Hamyar uses the pattern for ports and its own logging scrubber (4.11) | Code review only |
| Steward role, self-heal tools, MCP tool surface, kit embedding, `cell_fix` and `publish_plan` | exclude | They exist to run the build of this specification, not the commons; PR§4.5 item 9 shows why they must not face the public | None |

## 4.19 Names, parameters, assumptions and verifications introduced by this part

### 4.19.1 New parameters (convention additions, area `ops` plus one in `admission`) [D]

Owner role `operator`. Every default is an `initial configurable default` replaced by the measurement in the last column; S16.* completes the table without renaming. `ops.*` is a new area for S0.10.5 (`ISS-45`).

| Name | Type | Initial configurable default | Validation | Replaced by |
| --- | --- | --- | --- | --- |
| `ops.rpo_s` | duration_s | 300 | 0..86400 | `OPS`; restore drill on the chosen host |
| `ops.rto_s` | duration_s | 14,400 | 60..604800 | `OPS`; restore drill duration |
| `ops.txn_retry_max` | int | 5 | 0..20 | `OPS` retry counters |
| `ops.capacity_headroom_ratio` | ratio | 5.0 | >= 1 | `OPS`; load test (4.6.2) |
| `ops.clock_skew_alarm_s` | duration_s | 2 | 0..60 | `OPS` |
| `ops.outbox_relay_interval_s` | duration_s | 2 | 1..60 | `OPS` |
| `ops.outbox_max_attempts` | int | 10 | 1..100 | `OPS` |
| `ops.outbox_retention_days` | days | 7 | 1..90 | `OPS` |
| `ops.outbox_lag_alarm_s` | duration_s | 60 | 1..86400 | `OPS` |
| `ops.job_lock_ttl_s` | duration_s | 120 = 4 x `lease.reap_interval_s` | 10..3600 | `OPS` |
| `ops.job_max_runtime_s` | duration_s | 300 | 10..3600; the lock is renewed during a run, so a run may outlast `ops.job_lock_ttl_s` | `OPS` |
| `ops.job_overdue_factor` | ratio | 3.0 | >= 1 | `OPS` |
| `ops.ttl_sweep_interval_s` | duration_s | 60 | 5..3600 | `OPS` |
| `ops.purge_interval_s` | duration_s | 3600 | 60..86400 | `OPS` |
| `ops.backup_interval_s` | duration_s | 86,400 | 3600..604800 | `OPS`; meets `ops.rpo_s` together with log archiving |
| `ops.backup_retention_days` | days | 35 | 1..365 | `CNS` (privacy duties), `OPS` |
| `ops.restore_drill_interval_days` | days | 90 | 7..365 | `OPS` |
| `ops.config_cache_ttl_s` | duration_s | 30 | 1..600 | `OPS` |
| `ops.migration_batch_size` | int | 1000 | 1..100000 | `OPS` |
| `ops.alert_error_ratio` | ratio | 0.05 | 0..1 | `OPS` |
| `ops.alert_window_s` | duration_s | 300 | 30..86400 | `OPS` |
| `admission.forecast_refresh_s` | duration_s | 3600 | 60..86400 | `P1M` forecast error |

Also added: flag `ff.verify.sandboxed_tests` (default off); registry field `adapter.open_url`; `config_epoch` and the envelope fields of 4.7.2; alarm keys of 4.11.3; bootstrap settings of 4.13.2; secret name `secret.backup_key` (proposed, owned by S10.*).

### 4.19.2 Assumptions [A] for S3.* (with the decision that could overturn each)

| Assumption | Overturned by |
| --- | --- |
| Modular monolith with an optional check runner (4.3.2) | A larger team or a host that forces separate deployables |
| TypeScript, PostgreSQL, static SPAs (4.17.3) | Owner stack preference; the alternative-B decision memo |
| Automatic engagement of two kill switches on an invariant violation (4.11.3) | Founders preferring a manual decision |
| Notification-free public site; no unsolicited messages (4.4.1) | A wish for expiry reminders or marketing messages |
| Member ids absent from logs (4.11.1) | Investigators needing them |
| Ephemeral store inside the transactional store (4.6.1) | Load measurements |
| Five distinct origins in staging and production (4.3.3) | Hosting limits |
| Second maintainer approves production deploys (4.13.3) | A one-person team |
| `config_epoch` as the stamp of versions in force (4.9.2) | A better stamping scheme in S5.* |

### 4.19.3 Verifications [V]: what, by whom, where stored

| Claim | Verified by | Stored in |
| --- | --- | --- |
| Reachability of each origin from Iran (4.15.2) | Founders and consenting testers | `LaunchGateItem` evidence under G2; `CalibrationRecord` |
| Serial posting rate of the chosen store meets `C_peak` (4.6.2) | Engineer | `LaunchGateItem` evidence under G2 |
| Durability, point-in-time recovery and replication of the chosen host | Operator, restore drill | `LaunchGateItem` evidence under G2; drill log |
| Capabilities of any named product in 4.17 | Engineer, from current documentation | Decision memo, `LaunchGateItem` evidence under G2 |
| Prefill support, template, length limit, per service and device class (4.14) | Reviewer | `ServiceRegistryEntry` `adapter.*`; `CalibrationRecord` |
| Terms permit prefilled links and copy-and-paste | Reviewer | `FlagAnswer` with `TermsCopy` |
| Font licenses allow self-hosting | Operator | `LaunchGateItem` evidence |
| Backup retention against privacy duties; legal exposure of a host jurisdiction | Counsel | `CNS` memo |
| Check runner design is safe enough to enable | Security reviewer | `LaunchGateItem` evidence under G1 |
| Panel code matches PR and may be reused (4.18) | Human reviewer | `LaunchGateItem` evidence under G4 |
| All existing secrets rotated before exposure | Operator | `LaunchGateItem` evidence under G4 |

## 4.20 Acceptance criteria

Given / When / Then; each is also a test (ids assigned by S18.*).

| Id | Criterion |
| --- | --- |
| `AC-arch-01` | Given a posting whose second entry violates a constraint, when it is committed, then no entry, lot change, head update, idempotency record or outbox row exists |
| `AC-arch-02` | Given a member whose balance covers exactly one hold, when two `escrow_hold` postings run concurrently, then exactly one commits, the other returns `INSUFFICIENT_CREDIT`, and `seq` has no gap |
| `AC-arch-03` | Given postings that roll back at random, when many commit, then the committed `seq` values are consecutive from 1 |
| `AC-arch-04` | Given the application database role, when it issues an update or delete on any append-only table, then the statement is rejected by privilege and by trigger |
| `AC-arch-05` | Given a posting retried with the same idempotency key, when it is replayed, then the stored result is returned and no entry is added |
| `AC-arch-06` | Given instance A holding a cached snapshot and instance B committing `killswitch.engaged` for a template, when A then handles a lease request for that template, then no lease is issued and the error is `KILL_SWITCH_ENGAGED`, without waiting for `ops.config_cache_ttl_s` |
| `AC-arch-07` | Given a fresh build in any environment, when parameters are read, then the three launch switches are `false`; a direct write to `launch.*` is rejected; only `LaunchGate.applySignedOff` with the S14.* rule satisfied flips one |
| `AC-arch-08` | Given canary values for IP, e-mail, prompt text and a token, when every endpoint is exercised, then no canary appears in logs, metrics, traces, alarms or error bodies |
| `AC-arch-09` | Given a seeded corruption of a balance projection, when the tier 2 check runs, then `ledger.invariant_violated` is emitted, an alarm is raised, `kill.all_minting` and `kill.all_new_jobs` are engaged by the checker's transaction, and release requires two operators |
| `AC-arch-10` | Given staging data, when the portability drill exports and imports into a fresh environment on a different host class, then the tier 3 recompute passes and the chain head equals the exported head |
| `AC-arch-11` | Given a backup older than the last published checkpoint, when the restore procedure runs, then step 5 declares a data-loss incident and production stays closed |
| `AC-arch-12` | Given two `lease_reaper` runs at once, when an expired lease is due, then its cell is requeued once with `attempt` increased once |
| `AC-arch-13` | Given a failing consumer, when delivery is attempted `ops.outbox_max_attempts` times, then the row is dead-lettered and `alarm.outbox_dead_letter` is raised, and no ledger entry is affected |
| `AC-arch-14` | Given any emitted event, when inspected, then it carries `config_epoch` and `policy_version_id`, and its name matches the transition in S0.9 |
| `AC-arch-15` | Given a `loosen` parameter change with `effective_from` earlier than now plus its notice, when applied, then it is rejected with `VALIDATION_FAILED` |
| `AC-arch-16` | Given `ff.verify.sandboxed_tests` off, when a template needing `run_tests` is submitted for approval or its cell for leasing, then it is refused and no submitted content is executed anywhere |
| `AC-arch-17` | Given `HAMYAR_ENV` = `prod`, when two origins are equal or one is not HTTPS, then the process refuses to start |
| `AC-adapter-01` | Given a service that is not `approved`, when its descriptor is requested, then `mode_allowed` is `[copy_only]` and `open_url` is absent |
| `AC-adapter-02` | Given `supports_prefill` true and `prefilled_link_use` `unknown`, when the descriptor is computed, then `mode_allowed` is `[copy_only]` |
| `AC-adapter-03` | Given the built member bundle, when scanned, then it contains no provider name or provider URL |
| `AC-adapter-04` | Given any prompt, when `plan` returns a prefill action, then the URL is at most `adapter.max_url_chars` long and its `{prompt}` part percent-decodes to exactly the prompt; otherwise it returns copy-only with reason `url_too_long` |
| `AC-adapter-05` | Given the member bundle, when statically analyzed, then it contains no clipboard-read call, no frame embedding a service, no retained handle to an opened window and no message posted to one |
| `AC-adapter-06` | Given a template with two placeholders, a non-HTTPS scheme, or the placeholder in the host, when a reviewer saves it, then validation rejects it |

## Issues raised

Each resolution is already applied in this file. C-001 consolidates them into S2.* and may record a different resolution. [D]

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-41` | major | prompt | Prompt E requires automatic checks including tests for code-change jobs, and also forbids executing submitted content; running supplied tests executes it | Submitted content is never executed by the server. `run_tests` checks run only in an isolated check runner behind `ff.verify.sandboxed_tests` (off by default); while it is off or unreachable, templates needing it cannot be approved or leased (4.4.4) | proposed |
| `ISS-42` | minor | prompt | Prompt J says the panel repository's code and docs were not read, but `docs/source/panel-review.md` now exists | The review is the fact base for 4.18; every panel decision keeps a [V] condition and G4 stays open until a human review | applied |
| `ISS-43` | major | FD§4.2 | The FD§4.2 invariants are global (total credit in existence), and the hash chain serializes appends, so the ledger has one serialization point; the FD gives no scale | One ledger, one chain; a capacity formula and load test decide the store (4.6.2); partitioning is allowed only after S6.* redefines the global invariants | needs_owner |
| `ISS-44` | minor | FD§4.5, FD§3.2 | `credit.expiry_notice_days` and optional e-mail exist, but nothing says through which channel a member is told | In-app notices only; the public site is notification-free; the platform sends only a message a member explicitly requests, such as recovery (4.4.1) [A] | needs_owner |
| `ISS-45` | minor | none | Convention gaps: parameter area `ops` and the 21 `ops` names in 4.19.1; `admission.forecast_refresh_s`; flag `ff.verify.sandboxed_tests`; field `adapter.open_url`; log events `http.request_served`, `sched.run_finished`, `outbox.relayed`, `alarm.raised`; infrastructure tables exempt from the entity rules (4.7.3); `config_epoch`; alarm keys | Added here; C-001 folds them into S0 and S16.* | proposed |
| `ISS-46` | minor | FD§10 | FD§10 keeps the launcher optional but does not say that its opt-in auto-send userscript and chat-link record (PR§6.4, PR§6.5) must not carry over, while Principle 3 forbids submitting on a volunteer's behalf | Both are excluded from Hamyar (4.2.2, 4.18) | proposed |
| `ISS-47` | major | FD§8.2 risk 5 | The FD does not address backups, which copy pseudonymous data beyond the `retention.*` windows and are a compelled-disclosure surface | Backups encrypted with a key the sink does not hold, at least two locations, retention `ops.backup_retention_days`, purge reaches backups by aging out; legal sufficiency is [V] for counsel (4.12.1) | needs_owner |
| `ISS-48` | minor | FD§10 | FD§10 and prompt I count four secrets; PR§4 finds a fifth, `EXT_TOKEN` (off when unset) | All five are rotated before exposure and never reused (4.13.3) | proposed |
| `ISS-49` | minor | FD§8.3 G4 | G4 requires a repository review; PR is a static, execution-free reading, so treating it as G4 would overstate what is known | 4.18 decisions carry [V] conditions; the G4 `LaunchGateItem` stays open until a human signs off | needs_owner |

Convention additions made by this part (listed so C-001 can fold them back): parameter area `ops` and the names in 4.19.1; `ff.verify.sandboxed_tests`; `adapter.open_url`; log event names `http.request_served`, `sched.run_finished`, `outbox.relayed`, `alarm.raised`; acceptance-criteria areas `arch` and `adapter`; bootstrap settings `HAMYAR_*` (4.13.2); `config_epoch`; `AdapterDescriptor` and `mode_allowed`; ledger consistency requirements `LC-1`..`LC-9`; secret name `secret.backup_key` (proposed for S10.*).
