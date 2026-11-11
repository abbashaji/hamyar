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
