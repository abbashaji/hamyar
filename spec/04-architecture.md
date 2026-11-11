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
| Ledger, lots, escrow, Reserve, mint-cap counters, grant counters | LC-1 to LC-9 | Per-device, per-day and per-tree grant limits that guard credit are enforced inside the ledger transaction, not in the ephemeral store (PR§4.5 item 3 shows a read-then-write counter exceeded under concurrency) |
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
