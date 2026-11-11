# 9. Result return, anti-forgery and abuse defenses

*Spec part 9 · provenance: cell C-010 · written against Founding Document draft v0.1 (FD) and `spec/00-conventions.md` (S0), which fix every name used here. The allowed path of the owning cell is authoritative; S0.13 proposes the file name `spec/09-result-return-abuse.md` [A]. Nothing here has been verified against any provider's terms, any browser, or any law. Persian text in this part is marked `needs_human_and_legal_review`.*

## 9.1 Scope, boundaries and what is excluded

This part specifies the **return path**: how a volunteer's pasted-back text becomes a `Submission`, which checks it passes before anything downstream sees it, and how every byte of it is stored and displayed as inert data. It also specifies the abuse defenses that apply on return (prompt scope E result return and anti-forgery; prompt scope D abuse defenses as they apply to outputs). [D]

| Topic | Decided here | Decided elsewhere (consumed, not redefined) |
| --- | --- | --- |
| Paste-back form and its accepted input | yes | Screens and copy: S11.* |
| Lease nonce lifecycle, submission deadline | yes | `Lease` entity fields and `createLease`: S5.*, S15.* |
| Submit endpoint processing, check order, reject codes | yes | Error model and idempotency: S0.11.3, S0.11.5; operation ids: S15.* |
| Text normalization, character policy, comparison key | yes | Fonts, RTL layout, numerals: S11.* |
| Escaping and display per output context | yes | Admin origin and sessions: S10.* |
| Output flagging and quarantine | yes | Input screening and rules `R1`..`R10`: S7.*; reviewer queue screen: S11.* |
| Duplicate-output and timing signals | yes | Gold, audit, comparator, reliability, member restriction: S8.*, S10.* |
| Attested service and model fields | yes | Service Registry and approval: S7.* |
| Acceptance, minting, payout, settlement | no | S6.*, S8.* |
| Template output schema, automatic checks, `slot_context` values | no (consumed) | S8.* |

**Excluded mechanisms.** The no-automation principle (FD Principle 3) and the no-circumvention principle (FD Principle 9) exclude the following from the return path. If a future feature would need one of them, the feature is excluded, not the principle. [D]

| ID | Excluded mechanism | Why |
| --- | --- | --- |
| E1 | Any browser extension, bookmarklet, script or app that reads the volunteer's chat page or DOM and posts the text | Reads the provider session; FD Principle 3 |
| E2 | Accepting a link to a shared conversation and fetching it | Reads a provider page on the volunteer's behalf, and is a server-side request forgery surface |
| E3 | Clipboard monitoring in the background | The only clipboard read is one the volunteer triggers with a tap on a Paste button (9.5) |
| E4 | Server-side submission using a volunteer's credentials or session | Credentials are never stored (S0.7) |
| E5 | Files, screenshots, images or OCR as a result | Not text; widens the parsing surface |
| E6 | Detecting the service or model from the page | Reads the provider page; the service and model are attested by the volunteer (9.13) |

**Trust boundary** [D]. The donor, the donor's device, the pasted text, the attested fields and every client-supplied identifier are untrusted input. Only server-held state is trusted: lease rows, cell rows, parameter versions and the server clock (S0.6.2). A submission proves that a member holding a valid lease sent this text before the lease deadline. It does not prove that the text came from a model, from the leased prompt, or from the service the donor names (9.11, 9.13, 9.19).

## 9.2 Decisions at a glance

| # | Decision | Reason |
| --- | --- | --- |
| 1 | The nonce is 128 bits, stored only as a SHA-256 hash, delivered once, single use, and expires with the lease | `lease.nonce_bytes` = 16 (S0.6.4); a stateless token cannot be single-use or revocable |
| 2 | Pre-persistence gates (SC-01..SC-16) are retryable inside the lease and consume nothing; the first persisted submission consumes the nonce | Honest paste errors must not burn a cell; abuse probing is bounded by `lease.max_gate_failures` |
| 3 | A dry-run `validateSubmission` runs only syntactic checks | Lets a donor fix a bad paste without revealing gold, audit, duplicate or flag logic |
| 4 | Text is stored in canonical form (NFC, invisible and bidi-control characters handled by a class table); the raw hash is kept for forensics | Display and comparison must not depend on invisible characters |
| 5 | Submitted text is never placed in HTML attributes, URLs, scripts, styles, templates, shell commands, regular-expression sources, file paths or SQL text | The XSS and injection defense is structural, not a sanitizer |
| 6 | Links, code to run and requests for action are quarantined, not accepted | FD§5.5; `screen.output_url_action` default `quarantine` |
| 7 | Duplicate-output and timing detections are signals, except two narrow hard cases | Honest low-entropy agreement and honest fast donors exist (9.11, 9.12) |
| 8 | Service and model are attested fields: stored, escaped, never trusted | FD§5.6, FD§5.7 failure mode 7 |
| 9 | The synchronous response never reveals gold status, audit selection or comparator results | Prevents a donor from learning which cells are checked |
| 10 | Secret response fields (the nonce) are excluded from stored idempotent responses | Keeps the nonce hash-only at rest (`ISS-98`) |

## 9.3 Server-issued identifiers

- `cel_`, `lse_` and `sub_` identifiers are generated on the server only, in the format of S0.6.3. A client never supplies a new identifier; it can only echo one the server gave it. [D]
- An identifier is not a secret and is not a capability. Possession of a `cel_` or `lse_` id grants nothing; every use is authorized by the session principal plus the server-held relation (lease belongs to member, cell belongs to lease). [D]
- A regex-valid identifier that is unknown, belongs to another member, or is not offered to the caller returns `404 NOT_FOUND` with identical bodies, so existence does not leak (S0.11.3). [D]
- A donor can lease a cell only if the server's eligibility check (rule `R8`, opt-ins) offers it at the time of `createLease`. Guessing a `cel_` id does not produce a lease. [D]
- **Gold and audit cells are indistinguishable by identifier and by shape** [D]. A gold, audit, third or review cell instance gets an ordinary `cel_` id minted at the moment it is inserted into a donor's offer, so id order and creation time carry no information about `cell_kind`. The member-facing representation of a cell and of a lease omits `cell_kind` and `attempt`. S8.* owns insertion; this part constrains the representation.
- At most one `active` lease exists per cell (partial unique index, 9.4). A cell id therefore maps to at most one live nonce at any instant. [D]

## 9.4 Lease-bound nonce

### 9.4.1 Generation, storage, delivery

| Aspect | Decision |
| --- | --- |
| Generation | Inside the same database transaction that inserts the `Lease`: `nonce = CSPRNG(lease.nonce_bytes)` bytes, OS CSPRNG only (S0.6.4) |
| Encoding | base64url without padding: `ceil(16 x 8 / 6)` = 22 characters; regex `^[A-Za-z0-9_-]{22}$` |
| Storage | `leases.nonce_hash` = lowercase hex SHA-256 of the 16 bytes. The plaintext nonce is never stored, logged or placed in an event. A high-entropy value needs no slow hash (S0.6.4) |
| Delivery | Exactly once, as `lease_nonce` in the body of the `201` response of `POST /v1/cells/{cell_id}/leases`, with `Cache-Control: no-store`. Never in a URL, never in a header, never returned by any `GET` |
| Use | Sent back inside the JSON body of the submission as `lease_nonce` (never a query string, S0.11.1). The volunteer never reads or types it; client code holds it |
| Redaction | The logger and the error reporter redact by field name `lease_nonce` and by header name `Authorization`. A test asserts that neither appears in any log line (`T-adv-911`) |
| Uniqueness | Unique index on `leases.nonce_hash` as a defense against a defective generator, not against chance (collision probability is 2^-128 per pair) |

### 9.4.2 Binding

The nonce is bound **relationally**: it is a column of one lease row, and that row names one `cell_id`, one `member_id` and one `attempt`. A submission is accepted only if the lease named in the path belongs to the authenticated member, the body repeats the lease's own `cell_id`, and the hash of the body's `lease_nonce` equals `nonce_hash` under constant-time comparison. Cryptographic derivation (an HMAC of the tuple) is rejected: it cannot be revoked, rotated or made single-use without a state row, and the state row exists anyway. [D]

### 9.4.3 Single use, expiry, rotation

- **Single use.** `nonce_consumed_at` is set in the same transaction that inserts the `Submission` (9.14, SC-17). After that, the nonce can only authenticate a replay of the identical payload (9.10). [D]
- **Expiry.** The nonce has no clock of its own. It is valid exactly while the lease is `active` and `now <= grace_until` (9.4.4). Extending the lease moves `grace_until`; so does nothing else. [D]
- **Rotation.** `POST /v1/leases/{lease_id}/nonce-rotations` (operation `rotateLeaseNonce` [A]) issues a new nonce, invalidates the old one in the same transaction, and requires an `Idempotency-Key`. It is allowed only while the lease is `active` and the nonce is unconsumed, at most `lease.max_nonce_rotations` times. It exists because a mobile page may reload between lease and paste-back. [A]
- **Idempotent replay of `createLease` and `rotateLeaseNonce`** returns the stored response with `lease_nonce` set to `null` and `details.nonce_redelivery` = `use_rotation`. The idempotency store never holds a plaintext nonce (`ISS-98`). [D]
- **Failed attempts.** Each gate failure on a lease increments `leases.gate_failures`. When it exceeds `lease.max_gate_failures`, further submit and validate calls on that lease return `429 RATE_LIMITED` until the lease ends. The nonce is not revoked by failures, so a third party cannot lock a donor out (a caller must already be the lease's member, SC-09). [D]

### 9.4.4 Lease deadlines used by the return path

```
leased_at    = lease.created_at                                   (server time)
expires_at   = leased_at + lease.timeout_s + k * lease.extend_s    k = extensions used, k <= lease.max_extensions
grace_until  = expires_at + lease.submit_grace_s
```

With the initial configurable defaults the latest `grace_until` is `1200 + 600 + 120` = 1,920 s after `leased_at` (derived from `lease.timeout_s`, `lease.extend_s`, `lease.max_extensions`, `lease.submit_grace_s`). `expires_at` is the deadline shown to the donor. The reaper acts at `grace_until`, not at `expires_at`: only then does it emit `lease.expired`, `cell.lease_expired` and `cell.requeued`. A submission received after `expires_at` and not after `grace_until` is accepted with `late = true`; `late` carries no penalty and is excluded from timing statistics (9.12). The server decides by comparing `now` with `grace_until` under the row lock, never by waiting for the reaper (`lease.reap_interval_s` bounds only how soon an expired cell is requeued). This keeps the state machines of S0.9.3 unchanged (`ISS-95`). [D]

### 9.4.5 Fields the return path requires

These are requirements on the entities owned by S5.*; names follow S0.7.

| Entity | Field | Type | Note |
| --- | --- | --- | --- |
| `Lease` | `nonce_hash` | text, unique | 9.4.1 |
| `Lease` | `nonce_issued_at`, `nonce_consumed_at` | timestamptz, nullable second | 9.4.3 |
| `Lease` | `nonce_rotations`, `extensions`, `gate_failures`, `validations` | int, default 0 | Counters bounded by the parameters in 9.18 |
| `Lease` | `expires_at`, `grace_until` | timestamptz | 9.4.4 |
| `Lease` | index | partial unique on `(cell_id)` where `state = 'active'` | One live lease per cell |
| `Submission` | `lease_id` | text, unique | One submission per lease |
| `Submission` | field set | see 9.14.3 | Stored by the claim step |

### 9.4.6 What the nonce buys, and what it does not

| Threat | Stopped by the nonce? | Reason |
| --- | --- | --- |
| A member pastes lease B's output into lease A's path, by bug or tampering | Yes | The nonce of B does not match the hash on A (`T-adv-904`) |
| A captured request is sent again later | Yes | Single use; a replay can only return the stored outcome (`T-adv-902`) |
| Someone who learned a `lse_` id from a screenshot or log submits | Yes, in addition to authentication | The id is not a capability; the nonce was never logged |
| An attacker holding a stolen member session token | No | The token already lets the holder lease cells and obtain a nonce; account takeover is S10.* |
| A donor who submits text that no model produced | No | Nothing in the return path proves provenance (9.11, 9.19) |
