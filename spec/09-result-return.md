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

## 9.5 What the paste-back form accepts

### 9.5.1 Form contract

The form is part of the volunteer screens (S11.*); this table is the contract that screen must meet. [D]

| Element | Accepts | Refuses |
| --- | --- | --- |
| Result field | One multi-line plain-text field. The paste handler reads only the `text/plain` representation of the clipboard; rich or HTML content is reduced to plain text before it reaches the field | Files, images, drag-dropped attachments, HTML, any second field |
| Paste button (optional) | A tap by the volunteer triggers one clipboard read, if the browser permits it [V: support and permission behavior on the target phones]. Manual paste remains the baseline | Any read without a tap (E3) |
| Service picker | One value from the list of `approved` registry services allowed for this cell (`M0`: any approved; `M1`: the pinned set) | Free-text service names, unapproved or unknown services |
| Model label | Optional free text up to `cell.envelope.max_model_label_chars`, plain text | Markup, newlines |
| Counters | Characters and UTF-8 bytes used against `cell.envelope.max_output_chars` and `cell.envelope.max_submission_bytes`, updated as the volunteer pastes | |
| Local pre-check | The same normalization routine as the server (shared library, 9.7.3) runs in the browser and shows what it would remove or reject. The server result is the only authority | Treating the local result as binding |
| Preview | The volunteer's own pasted text is shown back as inert text with invisible characters revealed (9.8.3). It is escaped like any other output (a donor can paste a self-XSS payload) | Rendering Markdown or HTML |
| After sending | A read-only view of the stored outcome | Editing a persisted submission; a second submission for the same lease |
| Nonce | Held by client code only | Showing, copying or asking the volunteer to type it |

The form never offers a way to send a URL to be fetched, a file to be parsed, or a conversation link (E2, E5). [D]

### 9.5.2 `submitResult` request

`POST /v1/leases/{lease_id}/submission` (S0.11.1). Headers: `Authorization: Bearer <member token>`, `Content-Type: application/json; charset=utf-8`, `Idempotency-Key` (required, S0.11.5). Operation id `submitResult` [A], final in S15.*.

```json
{
  "cell_id": "cel_01j9z6x4k7q2m8v5t3r1w0c9ab",
  "lease_nonce": "Zk3p0yT9aVb1QxF2mC8rLw",
  "output_text": "...the pasted answer...",
  "attestation": { "service_id": "svc_01j9...", "model_label": "optional free text" }
}
```

| Field | Type | Rule |
| --- | --- | --- |
| `cell_id` | string | Matches S0.6.3 with prefix `cel_`; must equal the lease's cell (SC-10) |
| `lease_nonce` | string | `^[A-Za-z0-9_-]{22}$` |
| `output_text` | string | UTF-8, any length at this layer; limits in 9.6; JSON escapes for lone surrogates are rejected at decode |
| `attestation.service_id` | string | `svc_` id; required |
| `attestation.model_label` | string or null | Optional; at most `cell.envelope.max_model_label_chars` code points after NFC; no C0 or C1 controls |
| any other key | | Rejected. Duplicate keys at any depth are rejected, and so are keys named `__proto__`, `constructor` and `prototype` |

### 9.5.3 `submitResult` response

`201 Created` for a new submission, `200 OK` with `Idempotent-Replayed: true` or `"replayed": true` for a replay (9.10). `Cache-Control: no-store`.

```json
{ "submission_id": "sub_01j9...", "lease_id": "lse_01j9...", "cell_id": "cel_01j9...",
  "state": "received", "reject_code": null, "replayed": false,
  "received_at": "2026-11-12T09:30:00Z", "late": false }
```

`state` is one of `received`, `schema_failed`, `checks_failed`, `quarantined` (names from S0.9.3). The synchronous stages of this part end in one of these. Verification (S8.*) runs afterwards and its outcome is read later; the response never carries `cell_kind`, gold status, audit selection, comparator output or reliability. `reject_code` is a `reject.*` value from S0.8.4 or `null`. When the reason is `reject.duplicate_of_other_output`, the response names neither the other cell nor the other donor. [D]

### 9.5.4 `validateSubmission` (dry run)

`POST /v1/leases/{lease_id}/validations` (operation `validateSubmission` [A]). Same body without `attestation`. It runs SC-01..SC-11, SC-12 (state and clock only), SC-16 and the length bounds, and nothing else: no detectors (9.9), no duplicate or timing logic, no gold or audit logic. It persists nothing, does not consume the nonce, and returns `{ "would_state": "ok" | "schema_failed", "reject_code": string|null, "chars": int, "bytes": int, "normalization": {...counts...} }`. It counts against `lease.max_validations` and `ratelimit.member_api_rpm`. Reason for the restriction: the syntactic rules are public by design, whereas running the flag detectors and signals on request would give an attacker an unlimited evasion oracle. [D]

## 9.6 Limits and rate limits

| Limit | Parameter (S0.10.6 unless marked new) | Enforced at | Failure |
| --- | --- | --- | --- |
| Request body bytes | `cell.envelope.max_submission_bytes` | Transport: the body is read as a stream and cut at the limit plus one byte, so an oversized or chunked body is never buffered (SC-02) | `413 PAYLOAD_TOO_LARGE`, `reject.size_exceeded`; nothing persisted |
| Output characters | `cell.envelope.max_output_chars` | After normalization, counted in Unicode code points of the canonical text (SC-16) | `schema_failed`, `reject.length_out_of_bounds` |
| Minimum output | at least one non-whitespace code point | SC-16 | `schema_failed`, `reject.length_out_of_bounds` |
| JSON nesting depth | `cell.envelope.max_json_depth` (new) | Parser (SC-07) | `400 MALFORMED_REQUEST` |
| Model label length | `cell.envelope.max_model_label_chars` (new) | Envelope (SC-08) | `400 VALIDATION_FAILED` |
| Run of combining marks | `screen.max_combining_run` (new) | Normalization | `schema_failed`, `reject.schema_invalid` |
| Gate failures per lease | `lease.max_gate_failures` (new) | Per-lease counter | `429 RATE_LIMITED` |
| Dry runs per lease | `lease.max_validations` (new) | Per-lease counter | `429 RATE_LIMITED` |
| Nonce rotations per lease | `lease.max_nonce_rotations` (new) | Per-lease counter | `422 UNPROCESSABLE` |
| Attempts per cell | `cell.max_attempts` | S5.* (cell machine) | `Cell.exhausted` |

The byte limit applies to the whole request body, so the derived bound is: `max_submission_bytes` is at least `max_output_chars x 3` (UTF-8, at most three bytes per code point in the Persian and Latin range) plus envelope overhead, which is why the default of 32,768 exceeds 18,000 (S0.10.6). Code points outside the Basic Multilingual Plane use four bytes; a submission full of them fails the byte limit before the character limit, which is intended. [D]

**Rate-limit matrix** (key is always the member id or the IP hash, never a raw IP, S0.11.7) [D]

| Scope | Parameter | Applies to | Failure |
| --- | --- | --- | --- |
| Member, all member endpoints | `ratelimit.member_api_rpm` | Every call, including `validateSubmission` | `429 RATE_LIMITED` with `Retry-After` |
| Member, persisted submissions | `ratelimit.member_submissions_per_hour` | Every call that reaches SC-05 on the submit route, so failed attempts count | `429 RATE_LIMITED` |
| Member, leases | `ratelimit.member_leases_per_hour` | `createLease` | `429 RATE_LIMITED` |
| Member, concurrent holds | `lease.max_active_per_member` | `createLease` | `422 CAP_EXCEEDED` |
| Lease | `lease.max_gate_failures`, `lease.max_validations` | Submit and validate | `429 RATE_LIMITED` |
| Unauthenticated callers | `ratelimit.public_rpm` per IP hash | Requests to the submit route with no valid token, so token guessing is throttled | `429 RATE_LIMITED` |

Rate limiting runs before the body is parsed and before any lease lookup (SC-05), so a flood costs one counter increment. Rate-limit responses are identical whether or not the nonce would have matched, so they leak nothing about it. [D]

## 9.7 Normalization and Unicode policy

### 9.7.1 Slot contexts

Every output slot of a template version declares a `slot_context` of `prose` (free natural-language text), `code` (source code or a diff) or `structured` (a value validated against an enum, pattern or schema). A template version cannot be approved unless every output slot declares its context (S8.* requirement raised here [A]). A submission whose template has one `prose` slot is treated as `prose` as a whole; a multi-slot template is split by the template's own output schema (S8.*) and each part is normalized under its slot's context. [D]

### 9.7.2 Character class table

"Strip" removes the character and counts it in the `normalization_report`. "Reject" ends the submission as `schema_failed` with the stated code and stores no text. "Keep" leaves it unchanged. [D]

| # | Class | Code points | `prose` | `code` | `structured` | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | C0 and C1 controls except TAB and LF | U+0000..U+0008, U+000B, U+000C, U+000E..U+001F, U+007F..U+009F | reject `reject.schema_invalid` | same | same | Only corrupt pastes and attacks carry them |
| 2 | Carriage return and separators | U+000D, U+2028, U+2029 | convert to LF | same | same | One newline form; CRLF becomes LF |
| 3 | TAB, LF | U+0009, U+000A | keep | keep | keep | |
| 4 | Bidi embeddings, overrides, isolates | U+202A..U+202E, U+2066..U+2069 | strip | reject `reject.forbidden_content` | reject `reject.forbidden_content` | Visual spoofing of text order ("Trojan Source" style). Direction is applied by markup at display (9.8.3), never by characters in stored text |
| 5 | Implicit direction marks | U+200E, U+200F, U+061C | keep | reject `reject.forbidden_content` | reject `reject.forbidden_content` | Used by Persian typists in prose; invisible and spoofable elsewhere |
| 6 | ZWNJ and ZWJ | U+200C, U+200D | keep | keep, add flag `invisible_in_code` | reject `reject.forbidden_content` | ZWNJ is part of correct Persian orthography; code strings may need it, so it is flagged and revealed at display instead of rejected |
| 7 | Other invisible and format characters | U+200B, U+2060, U+00AD, U+180E, U+2061..U+2064, U+FFF9..U+FFFB, U+FEFF | strip | reject `reject.forbidden_content` | reject `reject.forbidden_content` | Hidden text and identifier tricks. A leading U+FEFF (a paste artifact) is stripped in every context |
| 8 | Tag characters and supplementary variation selectors | U+E0000..U+E007F, U+E0100..U+E01EF | reject `reject.forbidden_content` | same | same | Invisible data smuggling; no legitimate use in a cell output |
| 9 | Variation selectors | U+FE00..U+FE0D strip everywhere; U+FE0E, U+FE0F | keep U+FE0E and U+FE0F | strip | strip | Emoji presentation only |
| 10 | Private use, noncharacters | U+E000..U+F8FF, U+F0000..U+10FFFF, U+FDD0..U+FDEF, U+xFFFE and U+xFFFF of each plane | reject `reject.schema_invalid` | same | same | Not text; unassigned code points are not tested because that depends on the Unicode version in use [V: library version] |
| 11 | Replacement character | U+FFFD | reject `reject.schema_invalid` | same | same | Signals a damaged copy; the donor can paste again |
| 12 | Run of combining marks longer than `screen.max_combining_run` | Mn, Me | reject `reject.schema_invalid` | same | same | Rendering and storage abuse; Persian vowel marks are short runs |
| 13 | Mixed-script token | A token mixing Latin with Cyrillic, Greek or Armenian (UTS #39 restriction level check) | keep, add flag `confusable_token` | reject `reject.forbidden_content` | reject `reject.forbidden_content` | Homoglyph spoofing; in prose it is a signal only |

Unicode noncompliant UTF-8 or unpaired surrogates never reach this table: they are rejected at JSON decode (`400 MALFORMED_REQUEST`, SC-07). [D]

### 9.7.3 Normalization procedure

```
normalizeOutput(raw_text, slot_context) -> (canonical_text | null, report, verdict)
  1  verdict := ok; report := {counts per class, crlf_converted:false, nfc_changed:false, flags:[]}
  2  apply class table rows 2, 4..9 for slot_context   # strip / convert / reject; reject sets verdict and stops
  3  apply rows 1, 10, 11 (reject on first hit)
  4  t := NFC(t); report.nfc_changed := (t differs from the text before this step)
  5  apply row 12 (combining-run check) and row 13 (flag or reject)
  6  trim leading and trailing Unicode White_Space; a trailing newline is not kept
  7  n := count of code points; if n < 1 or n > cell.envelope.max_output_chars -> reject reject.length_out_of_bounds
  8  assert NFC(t) = t and t holds no stripped class        # idempotence guard; failure is a defect, alarm
  9  return (t, report, verdict)
```

The function is pure, deterministic and shared by the server, the dry run and the browser. It is idempotent: `normalizeOutput(normalizeOutput(x)) = normalizeOutput(x)` (`T-prop-901`). Stripping happens before NFC because removing a ZWJ or a format character can change which marks compose. [D]

### 9.7.4 Hashes and the comparison key

| Name | Definition | Use |
| --- | --- | --- |
| `raw_hash` | `sha256:` + SHA-256 over the UTF-8 bytes of `output_text` as decoded from JSON, before any step above | Forensics; proves what arrived; stored even when the text is rejected and not stored |
| `output_hash` | `sha256:` + SHA-256 over the UTF-8 bytes of the canonical text | The `output_hash` of the provenance manifest (FD§5.6) [D]; resolves `ISS-96` |
| `payload_hash` | SHA-256 over the RFC 8785 canonical JSON of `{cell_id, output_text, attestation}` (nonce excluded) | Replay versus conflict (9.10) |
| `ckey` (comparison key) | From the canonical text: NFKC, Unicode default case folding, delete every Cf character and tatweel U+0640, delete Arabic and Persian vowel marks U+064B..U+065F and U+0670, map U+0643 to U+06A9 and U+064A, U+0649 to U+06CC, map digits U+0660..U+0669 and U+06F0..U+06F9 to ASCII `0..9`, map U+060C, U+061B, U+061F to `,` `;` `?`, collapse whitespace runs to one space | Duplicate detection (9.11), flag detection (9.9), comparators in S8.*. Never used for display or storage |
| `dup_key` | SHA-256 over the UTF-8 bytes of `ckey` | Exact-match index |

The `ckey` folding set is a starting point written by the spec author, to be reviewed by a Persian-speaking reviewer before launch [A][V: reviewer name and date stored in the change log]. Its adequacy for real Persian text is a hypothesis [H]; the test is `T-rtl-905`, the kill criterion is any pair of outputs that a reviewer judges identical and that receive different `ckey` values in the first reviewed sample. Storage preserves what the donor typed apart from table 9.7.2: no Yeh, Kaf or digit rewriting is applied to stored text. [D]
