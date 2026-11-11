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
- Launch switches: `members_may_join` is checked in `createMember`, `member_jobs_enabled` in `submitJob`, `minting_enabled` in `post` for `mint`; each refuses with `LAUNCH_GATE_CLOSED`. The only writer is `LaunchGate.applySignedOff`, which re-evaluates the gate rule of S14.* in the same commit. No environment variable, header, role or build flag bypasses it; dev, test and staging pass the same sign-off flow with synthetic administrators and synthetic evidence, and their data is labeled `synthetic` [D].

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
