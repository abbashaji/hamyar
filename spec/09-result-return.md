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

Invalid UTF-8 and unpaired surrogates never reach this table: they are rejected at JSON decode (`400 MALFORMED_REQUEST`, SC-07). [D]

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

## 9.8 Escaping, display and the rule that submitted content is never executed

### 9.8.1 Output contexts

Submitted text (`output_text`, `model_label`, and anything derived from them) is **data in every context**. The defense is structural: submitted text is placed only where the platform's escaping layer treats it as a value, and a list of places it must never go is enforced by tests. [D]

| Context | Rule | Test |
| --- | --- | --- |
| HTML text node (volunteer, requester, reviewer, operator screens) | Rendered only through the front-end framework's default text binding (escaping by construction). No `innerHTML`, `dangerouslySetInnerHTML`, `document.write`, `insertAdjacentHTML` or equivalent anywhere in the code base; a lint rule fails the build on them | `T-inj-901`, `T-inj-902` |
| HTML attribute, `href`, `src`, `style`, `id`, `class`, `name`, `srcdoc`, event handler | Submitted text is never placed in them, not even escaped. Tooltips and labels use fixed copy keys | `T-inj-903` |
| JavaScript string, JSON embedded in a page, `<script>`, `<style>`, `<template>` | Never. Data reaches the page through the JSON API only | `T-inj-904` |
| JSON API response | Produced by the serializer (no string concatenation), `Content-Type: application/json; charset=utf-8`, `X-Content-Type-Options: nosniff` | `T-inj-905` |
| Markdown | **Not rendered.** Outputs are shown as plain text with preserved line breaks. Rendering Markdown or HTML from a submission needs a new decision with a reviewed sanitizer and a security sign-off (`SEC`) | `T-inj-906` |
| CSV export (requester deliverable) | RFC 4180 quoting. Any cell whose first character other than whitespace and Cf characters, after the normalization of 9.7, is `=`, `+`, `-`, `@`, TAB or CR is prefixed with an apostrophe-style guard character `'` inside the quoted field, so a spreadsheet does not read it as a formula | `T-inj-907` |
| JSON, JSONL export | Serializer output; no string concatenation | `T-inj-905` |
| Markdown export (if S15.* offers it) | Output goes inside a fenced code block whose fence is longer than the longest run of backticks in the text; never as live Markdown | `T-inj-908` |
| Plain-text export | UTF-8, LF newlines, `Content-Disposition: attachment`, `X-Content-Type-Options: nosniff` | `T-inj-909` |
| File names of exports | Generated from ids and the date only; never from submitted text | `T-inj-909` |
| Log lines and error messages | Content is never logged; ids, hashes, sizes and codes are. If an error must show a fragment, it is at most 40 code points, JSON-escaped, with all controls rendered as `\uXXXX` | `T-adv-911`, `T-inj-910` |
| Provenance manifest (FD§5.6) | JSON from the serializer; `attested_service_id` and `attested_model_label` carry the key prefix `attested_` so no reader mistakes them for verified fields | `T-inj-905` |
| Admin tools (separate origin, S10.*) | Same rules, plus the reveal-invisibles view on by default and a banner "submitted content" on every panel that shows it | `T-inj-911` |
| E-mail | Submitted content is never placed in an e-mail (e-mail is optional and recovery-only, S0.10.6) | `T-inj-912` |

**Response headers and CSP** [D][V: browser support on the target phones, especially Trusted Types]. Every HTML response carries `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; require-trusted-types-for 'script'`, plus `X-Content-Type-Options: nosniff` and `Referrer-Policy: no-referrer`. There are no inline scripts and no third-party script, style or font hosts (prompt scope I: no mandatory third-party dependency). The directive values are initial design values, not configuration in the parameter table; changing one is a spec change reviewed under `SEC`.

### 9.8.2 Never executing submitted content

The platform never interprets submitted text as anything but data. The following are forbidden in the API process, the workers and the admin tier, and each has an adversarial test. [D]

| Forbidden | Instead | Test |
| --- | --- | --- |
| `eval`, dynamic `import`, `Function` constructors, shell, `exec`, with submitted text in any argument | Not needed | `T-inj-913` |
| Interpolating submitted text into a template engine source (server-side template injection, for example `{{7*7}}`, `${...}`) | Submitted text is bound to a data slot only; the template source is fixed code | `T-inj-914` |
| SQL text built from submitted text | Parameterized statements only; a static check fails the build on string-built SQL | `T-inj-915` |
| Deserializing submitted text with any format that can instantiate objects (YAML tags, pickle, Java serialization) | JSON only, with the limits of 9.6 | `T-inj-916` |
| XML or archive parsing with entity expansion, external entities, or unbounded decompression | Not accepted as a format in any slot context (a template may specify JSON, CSV or plain text; S8.*) | `T-inj-917` |
| Fetching any URL found in submitted text (previews, thumbnails, link checkers) | URLs are inert text; the server never makes an outbound request because of content (no server-side request forgery surface) | `T-inj-918` |
| Building a file path, command or regular-expression source from submitted text | Regular expressions come only from reviewed template data and run on a linear-time engine or with a time limit [V: engine choice, S4.*]; submitted text is only ever the subject string | `T-inj-919` |
| Treating submitted text as markup for a downstream tool without its escaping layer | Each export format has its rule in 9.8.1 | `T-inj-907` |

**Code submitted as a result.** For a `code_change_tests` job the submitted code is the deliverable. It is stored and shown as inert text and is never run by the web, API or admin tier. The FD's automatic "unit tests" check (FD§4.4) would run it; that is the one place where execution is needed, so it is confined to an isolated runner that is a separate component: no network, no secrets, no shared file system, hard CPU, memory, process and wall-clock limits, ephemeral per run, and only a pass or fail verdict plus a truncated log (treated as submitted content, 9.8.1) comes back. Until that runner is built and signed off under `SEC` [V], the check returns `verification_outcome` = `inconclusive` and the cell is sent to audit, and the template `code_change_tests` cannot be approved for use (`ISS-91`). [D][A]

### 9.8.3 Mixed-direction text (Persian and English together)

Stored text has no direction characters (9.7.2 rows 4 and 5, prose strips embeddings and keeps only implicit marks), so direction is a display decision. [D]

| Display situation | Rule |
| --- | --- |
| A block of output text | The container carries `dir="auto"` and CSS `unicode-bidi: plaintext`, so each paragraph takes its direction from its first strong character, never from the page locale |
| An inline fragment of submitted text inside interface text (a model label, a short excerpt in a table) | Wrapped in `<bdi>` (or `unicode-bidi: isolate` with `dir="auto"`) so it cannot reorder the surrounding label or number |
| Code and diffs | `dir="ltr"`, `unicode-bidi: isolate`, monospace stack, never auto direction |
| Numbers, dates, ids next to Persian text | Wrapped in an isolating element; digits follow the member's `digits` setting only for interface text, never for submitted text, which is shown as stored |
| Fonts | A system font stack that covers Arabic-script Persian letters and ZWNJ, with a local fallback; no mandatory remote font (prompt scope I). The stack is set in S11.* |
| Reveal-invisibles view | A toggle that renders ZWNJ, ZWJ, direction marks, NBSP and any retained format character as a visible marker such as `⟦U+200C⟧`; on by default for `code` slots and in the admin tools |
| Truncation | Excerpts cut on a grapheme-cluster boundary, never inside a combining sequence or a surrogate pair |

## 9.9 Output flagging and quarantine

FD§5.5: outputs containing links, code to run or requests for action are flagged instead of shown as results. This section makes that a pipeline stage. [D]

### 9.9.1 Flag classes and detectors

Detectors run on `ckey` (so fullwidth letters, stripped invisibles and case tricks do not evade them) and on the canonical text. Patterns are **data**, stored and versioned with the policy data (S7.*) so that tightening is immediate and loosening needs a change-log entry (`R10`); this file fixes the classes and the mechanism, not the pattern list. The examples below are illustrative, not exhaustive, and the Persian examples need human review. [D][A]

| Class | Name | What it detects | Illustrative examples | Default action |
| --- | --- | --- | --- | --- |
| L | Link | A URL scheme (`scheme://`), `www.` prefix, `mailto:`, `javascript:`, `data:` pseudo-schemes, Markdown link syntax `](`, HTML tags `<a`, `<img`, `<script`, IP literals, obfuscations such as `hxxp`, `[.]`, `(dot)`, and a bare domain-shaped token whose suffix is in the reviewer-maintained public-suffix list [V: list source and update owner] | `https://example.test/x`, `hxxps://a[.]b` | `screen.output_url_action` (`quarantine`), allowed count `screen.output_max_urls` (0) |
| C | Code to run | Fenced code blocks in a `prose` slot, shell prompt lines (`$ `, `# ` followed by a command), pipe-to-shell shapes, package-manager or download commands, script tags | a fenced block with an install command | `screen.output_code_action` (`quarantine`) |
| A | Request for action | Second-person imperatives aimed at the reader or at an assistant: open, click, download, install, log in, send, reply with; phrases that address an AI system ("ignore previous instructions", "you must", role markers such as `system:`) | English forms above; Persian forms such as «دانلود کنید», «کلیک کنید», «نصب کنید», «وارد شوید», «دستورهای قبلی را نادیده بگیر» `needs_human_and_legal_review` | `screen.output_request_action` (`quarantine`) |

A template may declare, per output slot, an **exemption list** of classes that are legitimate there (for example class C in the code slot of `code_change_tests`, or class L in a slot whose schema type is `url`). Exemptions are part of the reviewed template version (S8.*), never granted per submission, and never cover class A. Detector hits are recorded as `flags` on the Submission with the class letter and a hit count, never the matched text. [D]

Detectors are heuristics. They produce false positives (a legitimate translation that contains the word "download") and false negatives (any paraphrase or encoding not in the pattern data). The false-positive cost is reviewer time, measured as the share of quarantined submissions that a reviewer releases; the false-negative rate is unknown and is estimated only through reviewer sampling of unflagged outputs (S8.*) [H]. This stage reduces the risk; it does not remove it. [D]

### 9.9.2 Quarantine lifecycle

```
Submission.received --submission.quarantined--> Submission.quarantined      (Cell: submitted --cell.flagged_for_audit--> flagged_for_audit)
Submission.quarantined --submission.released_from_quarantine--> back into the S8.* pipeline at its verification stage
Submission.quarantined --submission.rejected--> Submission.rejected         reason reject.forbidden_content (Cell: --cell.audit_failed--> rejected)
```

| Rule | Decision |
| --- | --- |
| Who decides | A `reviewer` (S0.8.2) in the admin tool, on the admin origin, with the reveal-invisibles view on. The decision is an `AdminAction` and an event |
| Visibility while quarantined | The text is hidden from the requester, from other donors, from audit and human-review cells, from deliverable assembly and from every public surface. Only reviewers see it |
| Release | The submission returns to verification as if it had just passed this stage; it still faces gold, audit and automatic checks (S8.*). A release does not accept the cell |
| Reject | The donor sees `reject.forbidden_content`. A reviewer who finds an attack (an injection attempt) records a `Report` against the member (S10.*); a reviewer who finds an honest false positive releases it and may propose a pattern change (loosening needs a change-log entry, `R10`) |
| Effect on donor reliability | A quarantine rejection is a reliability observation only if the reviewer marks it `deliberate`; otherwise it has none (a false positive must not lower an honest donor's tier) [A] |
| Credit | None while quarantined; minting or payout happens only at acceptance (S6.*, S8.*) |
| Age-out | A submission unreviewed for `screen.quarantine_max_age_days` ends as `submission.rejected` with `reject.forbidden_content`, flagged `no_reliability_effect`; its cell is requeued. The queue age is a metric and an alarm (9.17) so reviewer capacity is visible before age-out happens (`ISS-92`) |
| Template pause | `template.autopause_report_count` reports on one template inside `template.autopause_window_s` pauses it (S0.10.6); a spike of quarantines on one template is an input to that decision |

Release and reject decisions on quarantined text are made by one reviewer and sampled by a second as part of the reviewer-capture control in S10.* [A].

## 9.10 Duplicate-submission handling: idempotent resubmit versus conflicting resubmit

Three layers apply in this order: the `Idempotency-Key` layer of S0.11.5, natural idempotency on `(lease_id, nonce)`, and the unique index on `submissions.lease_id`. [D]

| # | Situation | Outcome | Emits |
| --- | --- | --- | --- |
| 1 | Same `Idempotency-Key`, same body (network retry) | Stored status and body replayed with `Idempotent-Replayed: true`; no processing | nothing |
| 2 | Same key, different body | `422 IDEMPOTENCY_KEY_MISMATCH` | nothing |
| 3 | Same key while the first call is running | `409 IDEMPOTENCY_IN_PROGRESS` with `Retry-After` | nothing |
| 4 | New key, same lease, nonce matches, `payload_hash` equal to the stored one | **Idempotent resubmit**: `200`, the stored outcome, `"replayed": true` | nothing (S0.9.3) |
| 5 | New key, same lease, nonce matches, `payload_hash` different | **Conflicting resubmit**: `409 STATE_CONFLICT`, `details.reason` = `conflicting_resubmission`, `details.stored_submission_id`. The stored submission is untouched; the conflict is counted and recorded as signal `signal.conflicting_resubmit` | nothing (a guard rejection is not an event, S0.9.1) |
| 6 | Lease already `submitted`, nonce does not match | `403 FORBIDDEN`, `reject.nonce_invalid`; the stored outcome is not revealed | nothing |
| 7 | Two first submissions for one lease arrive together (double tap, two tabs) | The row lock on the lease serializes them: one persists, the other re-reads and becomes case 4 or case 5 | one set of events |
| 8 | Lease `released`, `expired` or `revoked`, or `now` past `grace_until` | `410 LEASE_EXPIRED`, `reject.lease_expired`, `details.reason` = the lease state or `past_grace` | nothing |
| 9 | The cell was requeued and re-leased; the previous lease holder submits late | The old lease is `expired`, so case 8; a new lease has its own nonce and its own submission | nothing |
| 10 | The same text under different leases or cells | Not a duplicate submission; handled by 9.11 | per 9.11 |

**Guarantees** (exact, per S0.1 and prompt scope B) [D]

| # | Guarantee |
| --- | --- |
| G1 | At most one `Submission` per `Lease` (unique index), so at most one submission per cell attempt |
| G2 | `nonce_consumed_at` is set if and only if a `Submission` row was persisted, in the same transaction |
| G3 | Submit versus lease expiry is serialized by the lease row lock: exactly one of "submission persisted" and "lease expired" happens; both never do |
| G4 | The three events of one claim (`submission.received`, `lease.submission_received`, `cell.submitted`) are written to the outbox in the same transaction as the state change (S4.*), so a committed submission always has its events and an uncommitted one has none |
| G5 | A replay never changes state, never emits and never extends any deadline |

**Not guaranteed** [D]: that the client receives the response (it can retry safely under cases 1 and 4), the order of submissions across different leases, or that a late submission within grace beats a requeue the reaper already performed (after `grace_until` the lease is `expired` and wins).

## 9.11 Detecting another donor's output pasted as one's own

### 9.11.1 What is being detected

| Kind | Pattern | Evidence | Treatment |
| --- | --- | --- | --- |
| D1 | Same cell, two donors (blanket redundancy, audit second or third execution): outputs equal or near-equal | `dup_key` equal or estimated similarity at least `verify.duplicate_similarity_threshold`, for outputs of at least `verify.duplicate_min_chars` code points | Signal only: both submissions get flag `duplicate_same_cell`, the cell is `flagged_for_audit`, and the pair is passed to the link analysis of S10.* (shared device group, invite tree, same hour). It is never rejected on similarity alone |
| D2 | One donor, two cells with different inputs, equal or near-equal outputs | Same test, restricted to `ckey` outputs of at least `verify.duplicate_min_chars` code points | `reject.duplicate_of_other_output` (hard), because an honest run on a different input rarely returns the same long text [H] |
| D3 | Two donors, two cells with different `input_hash`, same `template_version_id`, equal or near-equal outputs | Same test | The later submission is rejected with `reject.duplicate_of_other_output`; the earlier one is flagged `duplicate_source` for audit (it may be the victim of a leak) |
| D4 | Output equals or nearly equals the cell's own input or prompt (the donor pasted the question back) | Similarity to the cell input | Recorded as `similarity_to_input_ppm` for the automatic checks of S8.*; no reject code here |

The hard cases D2 and D3 apply only to slots whose `slot_context` is `prose` or `code` and whose text reaches the minimum length; short, enumerated or schema-constrained outputs (a class label, a one-word answer) are exactly where honest agreement is expected, so they are excluded from all four kinds. [D]

### 9.11.2 Method

```
fingerprint(ckey):
  shingles := set of character 5-grams of ckey (length verify.duplicate_shingle_chars)
  sig      := MinHash over shingles with verify.duplicate_minhash_perms permutations
  bands    := split sig into b bands of r rows;  b * r = verify.duplicate_minhash_perms
  store (submission_id, dup_key, sig, band_hashes[b], template_version_id, input_hash, member_id, cell_id, received_at)
candidates(new):  rows sharing at least one band hash AND template_version_id AND received_at within verify.duplicate_window_days
similarity(a,b) = fraction of equal sig positions           (an unbiased estimate of the Jaccard similarity of the shingle sets)
verdict:  dup_key equal  OR  similarity >= verify.duplicate_similarity_threshold
```

Character 5-grams are used instead of word tokens because Persian text mixes spaces and ZWNJ unpredictably, and `ckey` already removes ZWNJ. [A][H] With the initial configurable defaults 128 permutations, 32 bands of 4 rows, the probability that a pair with true similarity `s` becomes a candidate is `1 - (1 - s^4)^32`; at `s` = 0.95 this is `1 - (1 - 0.8145)^32`, which is above `1 - 10^-20`, so a genuine near-duplicate is effectively never missed at retrieval; the final decision uses the full signature, not the band match. [D] The candidate window and the index live and die with the job payload: fingerprints are payload-derived and are purged with `retention.job_payload_days` (S0.7, `job_bound`). [D]

### 9.11.3 Limits, stated plainly

- Similarity cannot detect a paraphrase of another donor's output, a copy of another donor's output that was lightly edited below the threshold, or a copy rendered into a different language. [D]
- Honest runs of the same prompt on the same service at low sampling temperature can legitimately produce identical or near-identical text; whether this happens often enough to matter is unknown and is measured in Phase 1 (`P1M`) as the rate of D1 flags that audits later confirm as honest [H]. Until measured, D1 is a signal and nothing more.
- A donor can obtain a valid-looking output from a model and still not have run the leased prompt, or can run it and alter the answer. The nonce binds the submission to the lease, not the text to the prompt. The only protection against low-effort or fabricated outputs is verification (gold, audit, automatic checks: S8.*), which estimates quality with stated error rates, not provenance. [D]
- A donor with two accounts can run one execution per account. Detection of that is link analysis (device, invite tree, timing), which is probabilistic and belongs to S10.*. [D]
- Published Commons outputs are public by design (`P1`). To prevent copying a published answer into a re-issued audit of the same cell, no output of a job is published or made visible to anyone outside the review queue before the job's cells have reached `accepted` (assembly follows `job.all_cells_accepted`, S0.9.2). [D]
- Sybil copies across leases are not prevented by hashing alone; the economic defense is that rejected cells earn nothing and the sampling floor never reaches zero (FD§4.4). [P]

## 9.12 Timing anomalies

Only server times are used: `leased_at` is `Lease.created_at` and `received_at` is the server time at SC-17. The client reports no durations (a client-reported duration is a forgeable field, so the schema has none). `lease_to_submit_s = received_at - leased_at`. [D]

| Signal | Rule | Action |
| --- | --- | --- |
| `signal.timing_below_floor` | `lease_to_submit_s < verify.timing_min_s` | Hard: `checks_failed`, `reject.timing_anomaly` (SC-18). The floor is meant to catch no-effort submissions that cannot include reading, sending, waiting for a model and copying back |
| `signal.timing_soft_fast` | Once the template version has at least `calibration.min_samples_per_service` verified submissions, `lease_to_submit_s < verify.timing_soft_ratio x median(lease_to_submit_s)` of those submissions | Flag; the cell is `flagged_for_audit` (a guaranteed audit), no rejection |
| `signal.timing_regular` | The coefficient of variation of the last `verify.timing_regular_window_obs` values of `lease_to_submit_s` for one member is below `verify.timing_regular_cv` | Flag on the member for S8.* and S10.* (consistent with scripted submission, which the platform forbids as a use but cannot see); no per-submission rejection |
| `late` | `received_at > expires_at` and `<= grace_until` | Recorded; excluded from the distribution; no penalty |

The distribution is collected per `template_version_id` as the histogram metric `hamyar_submission_lease_to_submit_seconds` over verified submissions only, so the statistic is not poisoned by unverified or rejected ones. Its purpose is dual: it feeds the soft signal, and it is the Phase 0 measurement `CAL` that replaces the initial `verify.timing_min_s` and `lease.timeout_s` (S0.10.4). [D]

**Limits** [D]
- No fast-path floor is derived from data yet. `verify.timing_min_s` is an initial configurable default and is expected to move after `CAL` (`ISS-97`); a floor set too high rejects honest practiced donors, so it errs low.
- Honest fast submissions exist (a short cell on a fast service, a donor with several tabs open): that is why only the floor is a hard rule and everything else is a signal. [H]
- Distributions depend on template, cell size, service speed and the donor's connection; they are estimated per template version, not globally, and are not valid across a template change.
- A script that waits a plausible random time defeats every timing rule. Timing detects carelessness and crude automation, not a determined adversary.
- Simulation output (S18.*) is not evidence about the real distribution. [D]

## 9.13 Attested service and model fields

| Field | Rule |
| --- | --- |
| `attestation.service_id` | Required. Must be an `approved` registry service (S0.9.6) that this cell may use: for `M0` any approved service; for `M1` one of the pinned ones; for `M2` an entry the registry marks open-weight with a checked license. Otherwise the call fails at SC-15 with `422 UNPROCESSABLE`, `reject.attestation_invalid`, before anything is persisted, so the donor can correct it. The check is re-run at acceptance together with `R9` (S7.*) |
| `attestation.model_label` | Optional free text, display-only, at most `cell.envelope.max_model_label_chars` code points, normalized with the `prose` rules except that no newline is allowed. It is never matched against anything and never used to gate; it is escaped on every display (9.8.1) |
| Meaning | A volunteer's own statement. It is stored as `attested_service_id` and `attested_model_label`, shown in manifests under those names, and described to requesters as "declared by the volunteer, not verified" (FD§5.6; FD§5.7 failure mode 7) [P] |
| Use | Registry membership check (above), audit and incident analysis, and aggregate statistics per service (for calibration, `CAL`). Not proof of anything: a donor can name any permitted service. The platform cannot check which service produced a text, because it never reads the provider page (E1, E6) |
| Consequence of a false attestation | None is detectable from the text itself. A pattern of attestations that audits contradict (for example systematically different outputs for the same claimed service) is an input to reliability review by a human, not an automatic penalty [H] |
| Copy | `copy.submit.attestation_note` (9.15) |

## 9.14 Submit endpoint processing

### 9.14.1 Pseudocode: every check in order

Checks are evaluated strictly in this order and the first failure ends the request. `SC-nn` ids are stable and used by the tests. [D]

```
submitResult(req, lease_id):

  # ---- Stage T: transport and identity (nothing persisted) ----
  SC-01  if media_type(req) != application/json            -> 415 UNSUPPORTED_MEDIA_TYPE
  SC-02  body := read_stream(req, cap = cell.envelope.max_submission_bytes)
         if cap exceeded (stream cut at cap + 1 byte)      -> 413 PAYLOAD_TOO_LARGE      [reject.size_exceeded]
  SC-03  p := authenticate(req, scheme = member)
         missing -> 401 AUTH_REQUIRED; wrong scheme or invalid -> 401 AUTH_INVALID (counted); expired -> 401 AUTH_EXPIRED
  SC-04  if p.status != active                             -> 403 FORBIDDEN
         if kill.member.<p.id> engaged                     -> 503 KILL_SWITCH_ENGAGED
  SC-05  if over ratelimit.member_api_rpm or ratelimit.member_submissions_per_hour
                                                           -> 429 RATE_LIMITED (Retry-After)
  SC-06  k := header Idempotency-Key; missing or not ^[A-Za-z0-9_-]{16,64}$ -> 400 VALIDATION_FAILED
         lookup(p.id, POST, path, k, sha256(canonical(body)))
           stored            -> replay stored response (Idempotent-Replayed: true)
           body differs      -> 422 IDEMPOTENCY_KEY_MISMATCH
           running           -> 409 IDEMPOTENCY_IN_PROGRESS
  SC-07  doc := parse_strict_json(body)                     # UTF-8 only, no duplicate keys, depth <= cell.envelope.max_json_depth,
         malformed                                         -> 400 MALFORMED_REQUEST      # no __proto__/constructor/prototype keys
  SC-08  validate_envelope(doc)                             # exact keys, types, id regexes, nonce regex, label length
         invalid                                           -> 400 VALIDATION_FAILED (details.fields)

  # ---- Stage L: lease and nonce (read only; failures here are retryable inside the lease) ----
  SC-09  l := load_lease(lease_id)
         missing or l.member_id != p.id                     -> 404 NOT_FOUND
         if l.gate_failures > lease.max_gate_failures       -> 429 RATE_LIMITED
  SC-10  if doc.cell_id != l.cell_id: l.gate_failures += 1   -> 403 FORBIDDEN              [reject.nonce_invalid]
  SC-11  if !ct_equal(sha256(b64url_decode(doc.lease_nonce)), l.nonce_hash):
                                  l.gate_failures += 1      -> 403 FORBIDDEN              [reject.nonce_invalid]
  SC-12  if l.state == submitted                            -> go to SC-13
         if l.state in {expired, released, revoked}         -> 410 LEASE_EXPIRED          [reject.lease_expired]
         if now() > l.grace_until                           -> 410 LEASE_EXPIRED          [reject.lease_expired] (details.reason = past_grace)
         late := now() > l.expires_at
  SC-13  (only when l.state == submitted, nonce already consumed)
         s := stored submission of l
         if payload_hash(doc) == s.payload_hash             -> 200 replay of s outcome (replayed = true), emit nothing
         else                                               -> 409 STATE_CONFLICT (details.reason = conflicting_resubmission); signal.conflicting_resubmit
  SC-14  c := load_cell(l.cell_id)
         if c.state != leased or c.attempt != l.attempt     -> 409 STATE_CONFLICT; alarm hamyar_submission_invariant_violations_total
  SC-15  if !service_permitted(doc.attestation.service_id, c): l.gate_failures += 1
                                                            -> 422 UNPROCESSABLE           [reject.attestation_invalid]

  # ---- Stage N: content normalization (pure function, in memory) ----
  SC-16  (text, report, verdict) := normalizeOutput(doc.output_text, c.slot_context)       # 9.7.3
         # verdict is ok or a reject code: reject.schema_invalid | reject.forbidden_content | reject.length_out_of_bounds

  # ---- Stage C: atomic claim (the only point that consumes the nonce) ----
  SC-17  BEGIN; lock lease then cell (fixed lock order, same as the reaper)
         re-check l.state == active, l.nonce_consumed_at IS NULL, now() <= l.grace_until, c.state == leased, c.attempt == l.attempt
           race lost (state moved)                          -> ROLLBACK; re-run from SC-12 on the fresh row (becomes 410 or SC-13)
         INSERT submission (state = received if verdict ok else schema_failed;
                            output_text stored only when verdict ok; raw_hash always)      # unique(lease_id) is the last guard
         UPDATE lease SET state = submitted, nonce_consumed_at = now()
         UPDATE cell  SET state = submitted        (if verdict not ok: then checks_failed -> rejected, requeue per S5.*)
         INSERT outbox events (9.14.4); COMMIT
         if verdict not ok                                  -> respond 201 state = schema_failed [verdict code]; STOP

  # ---- Stage V: abuse checks on the persisted submission (synchronous, deterministic) ----
  SC-18  if lease_to_submit_s < verify.timing_min_s         -> checks_failed [reject.timing_anomaly]; STOP
  SC-19  if duplicate hard case D2 or D3 (9.11)             -> checks_failed [reject.duplicate_of_other_output]; STOP
  SC-20  hits := run_detectors(ckey, text, slot exemptions)  # classes L, C, A (9.9)
         if any hit whose action is quarantine              -> quarantined; STOP (cell flagged_for_audit)
  SC-21  record soft signals in flags: timing_soft_fast, duplicate_same_cell, duplicate_source, confusable_token,
         invisible_in_code, bidi_stripped, late; set force_audit if timing_soft_fast or duplicate_same_cell
  SC-22  enqueue verify_submission(submission_id, force_audit)   # S8.* continues: automatic checks, gold, audit sampling
         respond 201 state = received
```

On any path that ends in `STOP` above, the response is built from stored state; the response body of 9.5.3 is the same on every path. [D]

### 9.14.2 Check table

| Check | Condition | HTTP and `code` | `details.reject_code` | Persists a `Submission` | Consumes nonce | Counts toward |
| --- | --- | --- | --- | --- | --- | --- |
| SC-01 | Not JSON | 415 `UNSUPPORTED_MEDIA_TYPE` | none | no | no | rate limit |
| SC-02 | Body over `cell.envelope.max_submission_bytes` | 413 `PAYLOAD_TOO_LARGE` | `reject.size_exceeded` | no | no | rate limit |
| SC-03 | Missing, invalid or expired token; token of another scheme | 401 `AUTH_REQUIRED`, `AUTH_INVALID`, `AUTH_EXPIRED` | none | no | no | rate limit per IP hash |
| SC-04 | Member not `active`; `kill.member.<id>` engaged | 403 `FORBIDDEN`; 503 `KILL_SWITCH_ENGAGED` | none | no | no | |
| SC-05 | Rate limit exceeded | 429 `RATE_LIMITED` | none | no | no | |
| SC-06 | Bad key; key reuse with another body; call in flight | 400 `VALIDATION_FAILED`; 422 `IDEMPOTENCY_KEY_MISMATCH`; 409 `IDEMPOTENCY_IN_PROGRESS` | none | no | no | |
| SC-07 | Malformed JSON, invalid UTF-8, duplicate or reserved keys, depth | 400 `MALFORMED_REQUEST` | none | no | no | |
| SC-08 | Envelope schema violation | 400 `VALIDATION_FAILED` | none | no | no | |
| SC-09 | Lease unknown or not the caller's | 404 `NOT_FOUND` | none | no | no | |
| SC-09 | `gate_failures` above `lease.max_gate_failures` | 429 `RATE_LIMITED` | none | no | no | |
| SC-10 | Body `cell_id` is not the lease's cell | 403 `FORBIDDEN` | `reject.nonce_invalid` | no | no | `gate_failures`, `signal.forgery_attempt` |
| SC-11 | Nonce hash mismatch | 403 `FORBIDDEN` | `reject.nonce_invalid` | no | no | `gate_failures`, `signal.forgery_attempt` |
| SC-12 | Lease ended or past `grace_until` | 410 `LEASE_EXPIRED` | `reject.lease_expired` | no | no | |
| SC-13 | Replay of identical payload / different payload | 200 replay / 409 `STATE_CONFLICT` | none | no (already exists) | already consumed | `signal.conflicting_resubmit` for the 409 |
| SC-14 | Cell not `leased` for this attempt | 409 `STATE_CONFLICT` | none | no | no | invariant alarm |
| SC-15 | Attested service not permitted for the cell | 422 `UNPROCESSABLE` | `reject.attestation_invalid` | no | no | `gate_failures` |
| SC-16 | Control or forbidden character, replacement character, private use, combining run, or length out of bounds | 201 with `state` = `schema_failed` | `reject.schema_invalid`, `reject.forbidden_content`, `reject.length_out_of_bounds` | yes, text not stored | yes | cell attempt (S5.*), anomaly signal |
| SC-18 | Below the timing floor | 201 with `state` = `checks_failed` | `reject.timing_anomaly` | yes | yes | anomaly signal |
| SC-19 | Duplicate of another output (hard cases) | 201 with `state` = `checks_failed` | `reject.duplicate_of_other_output` | yes | yes | anomaly signal |
| SC-20 | Link, code to run or request for action | 201 with `state` = `quarantined` | none (reason shown through `copy.submit.flagged_withheld`) | yes | yes | reviewer queue |
| SC-22 | Passed the stages of this part | 201 with `state` = `received` | none | yes | yes | |

SC-17 has no external code of its own: its failure modes are the race outcomes already listed (410, replay or conflict). Gate failures at SC-01..SC-15 never consume a cell attempt and never change cell state; the donor can correct the problem and retry inside the lease. A failure at SC-16 or later burns one attempt of the cell (`cell.max_attempts`), which is why the dry run of 9.5.4 exists (`ISS-94`). [D]

### 9.14.3 Stored fields of `Submission` (requirements on S5.*)

| Field | Type | Note |
| --- | --- | --- |
| `id`, `lease_id` (unique), `cell_id`, `member_id`, `attempt` | ids, int | `sub_` id server-generated |
| `state`, `reject_code` | text | Values from S0.9.3 and S0.8.4 |
| `received_at`, `late`, `lease_to_submit_s` | timestamptz, bool, int | Server times; seconds, floored |
| `slot_context` | text | `prose`, `code`, `structured` per slot |
| `output_text` | text, nullable | Canonical text; null when rejected at SC-16 or after purge |
| `output_hash`, `raw_hash`, `payload_hash`, `dup_key` | text | 9.7.4; hashes survive the purge |
| `output_chars`, `output_bytes` | int | Of the canonical text |
| `normalization_report` | json | Counts per class only, never the removed text |
| `flags` | json | List of `{class, hits}` and signal names, never matched text |
| `attested_service_id`, `attested_model_label` | text | 9.13 |

A separate table `submission_fingerprints` [A] holds the MinHash signature and band hashes (9.11.2). Retention is `job_bound`: `output_text`, `normalization_report`, `attested_model_label` and the fingerprints are purged `retention.job_payload_days` after the job reaches a terminal state; hashes, codes, flags and ids stay (S0.7). Indexes: unique `(lease_id)`; `(cell_id, attempt)`; `(dup_key)`; band-hash lookup on `submission_fingerprints`; partial `(received_at)` where `state = 'quarantined'` for the reviewer queue; `(member_id, received_at)` for the timing signals. [D]

### 9.14.4 Events emitted by outcome

Event names are those of S0.9.3, all written to the outbox in the claim transaction or, for the later stages, in their own transaction. A gate rejection emits no domain event; it writes one ops log line `submission.gate_rejected` with the check id and code, and increments `hamyar_submission_gate_rejections_total` [A]. [D]

| Outcome | Events |
| --- | --- |
| Gate rejection (SC-01..SC-15) | none |
| Claim succeeded | `submission.received`, `lease.submission_received`, `cell.submitted` |
| `schema_failed` (SC-16) | the three above, then `submission.schema_failed`, `cell.checks_failed` |
| `checks_failed` (SC-18, SC-19) | the three above, then `submission.checks_failed`, `cell.checks_failed` |
| `quarantined` (SC-20) | the three above, then `submission.quarantined`, `cell.flagged_for_audit` |
| Reaper at `grace_until` | `lease.expired`, `cell.lease_expired`, then `cell.requeued` |
| Replay | none |

## 9.15 Copy keys for the return path

Copy intent and texts for the paste-back form. Every key has `fa` and `en` and the marker `needs_human_and_legal_review`. Promises use "declared", never "guaranteed" (S0.2). Full screens are in S11.*. [D]

| Key | Shown when | `en` | `fa` |
| --- | --- | --- | --- |
| `copy.submit.too_long` | `reject.size_exceeded`, `reject.length_out_of_bounds` | The pasted text is longer than this task allows. Copy only the answer, not the whole chat. | متن چسبانده‌شده از حد مجاز این کار بلندتر است. فقط پاسخ را کپی کنید، نه کل گفتگو را. |
| `copy.submit.damaged_text` | `reject.schema_invalid` | The pasted text looks damaged. Please copy the answer again and paste it. | متن چسبانده‌شده آسیب‌دیده به نظر می‌رسد. لطفاً پاسخ را دوباره کپی و چسبانده کنید. |
| `copy.submit.hidden_characters_removed` | Row 4, 7 or 9 of 9.7.2 stripped something | Invisible formatting characters were removed from your text. | نویسه‌های قالب‌بندی نامرئی از متن شما حذف شد. |
| `copy.submit.lease_expired` | `reject.lease_expired` | This cell's time has run out and it went back to the queue. Nothing is lost; you can take another. | زمان این سلول تمام شد و به صف برگشت. چیزی از دست نرفته؛ می‌توانید سلول دیگری بردارید. |
| `copy.submit.flagged_withheld` | `state` = `quarantined` | Your answer contains a link, code to run, or a request. It is held for review and is not counted yet. | پاسخ شما شامل پیوند، کد برای اجرا یا درخواست است. برای بررسی نگه داشته شد و هنوز شمرده نمی‌شود. |
| `copy.submit.replayed` | Replay (9.10 case 4) | Already received. Showing the earlier result. | قبلاً دریافت شد. نتیجهٔ پیشین نمایش داده می‌شود. |
| `copy.submit.attestation_note` | Beside the service picker | The service and model you name are recorded as your own statement; they are declared, not verified. | سرویس و مدلی که اعلام می‌کنید به‌عنوان اظهار خودتان ثبت می‌شود؛ اعلام‌شده است، نه تأییدشده. |
| `copy.submit.service_not_allowed` | `reject.attestation_invalid` | This task cannot be done with that service. Please choose one from the list. | این کار با آن سرویس قابل انجام نیست. لطفاً یکی از فهرست را انتخاب کنید. |
| `copy.submit.not_counted_duplicate` | `reject.duplicate_of_other_output` | This answer matches another submission and was not counted. | این پاسخ با ارسال دیگری مطابقت دارد و شمرده نشد. |
| `copy.submit.too_fast` | `reject.timing_anomaly` | This was sent faster than the task can be done. It was not counted; you can try again. | این پاسخ سریع‌تر از زمان لازم برای انجام کار ارسال شد. شمرده نشد؛ می‌توانید دوباره تلاش کنید. |

## 9.16 Abuse through paste-back: test list and acceptance criteria

Test ids follow S0.5 (`T-<layer>-<nn>`). This part uses numbers 901 and up in each layer so that S18.* can add its own without collision [A]. Display-layer tests seed the stored text directly into storage, bypassing SC-16 and SC-20, so the escaping defense is tested independently of the detectors (defense in depth). [D]

### 9.16.1 Injection and XSS test list

The payloads are illustrative; the suite also runs a maintained public injection corpus [V: corpus choice and license], and every payload is run through the paste-back form, the API, every export and every screen that shows submitted text.

| ID | Class | Example payload | Surface | Expected |
| --- | --- | --- | --- | --- |
| `T-inj-901` | Script tag in a text node | `<script>alert(1)</script>` | Requester result view, reviewer queue, volunteer history | Shown as literal text; no `script` element created from it; no CSP violation report |
| `T-inj-902` | Event-handler markup | `<img src=x onerror=alert(1)>` | Same | Literal text; no `img` element |
| `T-inj-903` | Attribute breakout | `" onmouseover="alert(1)` as `model_label` | Every place a model label appears | Literal text inside `<bdi>`; a static test proves no code path binds submitted text to an attribute |
| `T-inj-904` | Script-context breakout | `</script><script>alert(1)</script>` | Any page that could embed JSON | No page embeds submitted data; the data arrives only through the JSON API |
| `T-inj-905` | Serializer escaping | `"`, `\`, U+2028, `</script>`, lone surrogate escapes | JSON API, manifest, JSONL export | Valid JSON; the parsed value equals the canonical text; `nosniff` present; lone surrogates rejected at SC-07 |
| `T-inj-906` | Markdown and link syntax | `[x](javascript:alert(1))`, `![i](http://x/y.png)` | All screens | Literal text; no `a` or `img` element; the image is never fetched |
| `T-inj-907` | Spreadsheet formula | `=HYPERLINK("http://x","a")`, `+1+1`, `-2+3`, `@SUM(1)`, a TAB or U+200F before `=` | CSV export | Every such field carries the guard prefix; no field starts with a formula trigger once whitespace and Cf characters are skipped |
| `T-inj-908` | Fence and heading injection | Text with ``` fences, `~~~`, `# heading`, `[l](u)` | Markdown export | Inside a fence longer than any backtick run in the text; rendering the export yields one code block and nothing else |
| `T-inj-909` | Header and file-name injection | `../../etc/passwd`, `CON`, U+202E, CRLF in the text | Plain-text and every other export | File name from ids and date only; `Content-Disposition: attachment`; no header contains the text |
| `T-inj-910` | Log injection | CRLF plus a forged log line, ANSI escapes | Application logs | No log line contains content except a JSON-escaped fragment of at most 40 code points; no forged line appears |
| `T-inj-911` | Hidden characters in admin view | Stored text with bidi controls, ZWSP, tag characters (seeded as legacy data) | Admin tools | Reveal-invisibles on by default; each hidden character shown as a visible marker; banner present |
| `T-inj-912` | E-mail | Any submitted string | E-mail templates | No template takes a submission field (static check) |
| `T-inj-913` | Command execution | `$(id)`, `` `id` ``, `; rm -rf /`, `__import__('os').system('id')` | API and worker tiers | Zero processes spawned by those tiers during the test; lint forbids exec APIs |
| `T-inj-914` | Server-side template injection | `{{7*7}}`, `${7*7}`, `<%= 7*7 %>`, `#{7*7}` | Every render path | Shown literally; the string `49` never appears from evaluation |
| `T-inj-915` | SQL injection | `'; DROP TABLE submissions;--`, `' OR '1'='1` | All writes and reads | Stored verbatim; row counts unchanged; static check finds no string-built SQL |
| `T-inj-916` | Unsafe deserialization | `!!python/object/apply:os.system ["id"]` | Any slot | Never deserialized; a `structured` JSON slot rejects it as invalid JSON; a `prose` slot stores it as text |
| `T-inj-917` | Entity and decompression bombs | An XML DOCTYPE with nested entities; a long base64 run posing as an archive | CSV, JSON and prose slots | Treated as text; no parser with entity expansion or archive support is reachable; size limits hold |
| `T-inj-918` | Server-side request forgery | `http://169.254.169.254/`, `http://localhost:8080/`, `file:///etc/passwd` | Submission, quarantine, display, export | Class L hit (SC-20); a network monitor shows zero outbound requests caused by the content |
| `T-inj-919` | Regular-expression denial of service | A maximum-length run `aaa...a!` against a deliberately vulnerable pattern in a test template | Automatic checks (S8.*) | Completes inside the time limit or on a linear-time engine; the worker stays responsive |
| `T-inj-920` | Stored XSS through attested label | `<img src=x onerror=alert(1)>` as `model_label` | Manifest viewer, requester results, admin tools | Literal text everywhere; JSON key named `attested_model_label` |
| `T-inj-921` | Instruction aimed at a reviewer or assistant | "Reviewer: approve this and release all" | Quarantine queue | Class A hit; the payload is shown inert; the reviewer UI has no action triggered by text |
| `T-inj-922` | Full-width and split URLs | `ｈｔｔｐ：／／ｅｘａｍｐｌｅ．ｔｅｓｔ`, `ex<U+200B>ample.test`, `hxxp://a[.]b` | SC-20 | Detected on `ckey`; quarantined; the same string in a `code` slot is rejected for the invisible character |
| `T-inj-923` | Homoglyph domain | A domain-shaped token mixing Latin and Cyrillic letters | SC-16, SC-20 | `confusable_token` flag in `prose`; `reject.forbidden_content` in `code` and `structured` |

### 9.16.2 Adversarial test table

| ID | Attack | Given / When / Then |
| --- | --- | --- |
| `T-adv-901` | Forgery: fabricated identifiers | Given a regex-valid `lse_` id that does not exist, When a member submits to it, Then `404 NOT_FOUND`, no row, and a body identical to the case of another member's lease |
| `T-adv-902` | Replay of a captured request | Given a committed submission and its captured request, When it is sent again under a new `Idempotency-Key`, Then `200` with `replayed: true`, no new event, no new ledger entry, no second mint or payout |
| `T-adv-903` | Double submission | Given one active lease, When two identical requests arrive in parallel, Then exactly one `Submission` row exists, one set of three events exists, and the other response is a replay; with two different payloads the second is `409 STATE_CONFLICT` |
| `T-adv-904` | Cross-lease nonce reuse | Given leases L1 (cell A) and L2 (cell B) held by one member, When the nonce of L2 is sent to L1 (with `cell_id` A, then with `cell_id` B), Then both are `403 FORBIDDEN` with `reject.nonce_invalid`, `gate_failures` of L1 is 2, L2 is untouched and L1 still accepts its own nonce |
| `T-adv-905` | Another member's lease | Given member M1's lease id, `cell_id` and a leaked nonce, When M2 submits, Then `404 NOT_FOUND` identical to `T-adv-901` |
| `T-adv-906` | Expired lease and grace | Given `now` after `expires_at` and before `grace_until`, Then `201` with `late: true`; given `now` after `grace_until`, Then `410 LEASE_EXPIRED`, no row, the cell not `submitted` |
| `T-adv-907` | Boundary race | Given a submission and the reaper at `grace_until`, When every interleaving of their steps is explored by a deterministic scheduler, Then in each one exactly one of "submission persisted" and "lease expired" occurred (guarantee G3) |
| `T-adv-908` | Oversize | Given a body of `cell.envelope.max_submission_bytes + 1` bytes (also as chunked transfer, also made of 4-byte code points), Then `413` and the server never buffered more than the cap plus one byte; given an output of `max_output_chars + 1` ASCII characters inside the byte limit, Then `201` with `schema_failed`, `reject.length_out_of_bounds` |
| `T-adv-909` | JSON abuse | Duplicate keys, `__proto__`, depth above `cell.envelope.max_json_depth`, a very large key count | `400 MALFORMED_REQUEST`; no row |
| `T-adv-910` | Unknown field smuggling | A body adding `cell_kind`, `state`, `late` or `client_elapsed_ms` | `400 VALIDATION_FAILED`; nothing is read from them |
| `T-adv-911` | Secret hygiene | After a full scripted run with a known nonce and token | Search of logs, traces, error reports, outbox events and the idempotency store finds neither the plaintext `lease_nonce` nor the bearer token |
| `T-adv-912` | Rate limit | Submit attempts beyond `ratelimit.member_submissions_per_hour` | `429 RATE_LIMITED` with `Retry-After` and `RateLimit-*` headers; identical responses for a correct and an incorrect nonce at that point |
| `T-adv-913` | Gate-failure budget | `lease.max_gate_failures + 1` wrong nonces, then the right one | `429 RATE_LIMITED`; the lease is not revoked; the budget resets only with a new lease |
| `T-adv-914` | Gold indistinguishability | Equal submissions on a gold cell and a normal cell | Response bodies identical in shape; no `cell_kind`; response-time distributions not separable by a two-sample test at the chosen significance [H] |
| `T-adv-915` | Quarantine evasion | Full-width, ZWSP-split and `hxxp` URLs in `prose` | Detected on `ckey`; quarantined |
| `T-adv-916` | Duplicate handling | Two donors, same long output on one audited cell; one donor reusing an output across two cells; two donors giving the same short class label | First: both flagged, none rejected; second: `reject.duplicate_of_other_output`; third: no flag |
| `T-adv-917` | Timing floor | Submission `verify.timing_min_s - 1` seconds after `leased_at` | `checks_failed`, `reject.timing_anomaly` |
| `T-adv-918` | Attestation abuse | Unapproved service; service outside the `M1` pinned set; label with newline or controls; label `<script>` | 422, 422, 400, and stored escaped respectively; the nonce unconsumed in the first three |
| `T-adv-919` | Wrong scheme | An admin token on the submit route | `401 AUTH_INVALID`, counted by the rate limiter |
| `T-adv-920` | Media type | `text/plain` body; a non-UTF-8 charset declaration | `415 UNSUPPORTED_MEDIA_TYPE` |
| `T-adv-921` | Idempotency | Same key with a changed body; same key while in flight | `422 IDEMPOTENCY_KEY_MISMATCH`; `409 IDEMPOTENCY_IN_PROGRESS` |
| `T-adv-922` | Kill switches | Engage `kill.template.<id>` while a lease is active; engage `kill.member.<id>` | Submit returns `410` (lease revoked first); then `503 KILL_SWITCH_ENGAGED` |
| `T-adv-923` | Conflicting resubmit | Second payload on a consumed lease | `409`, stored submission unchanged, `signal.conflicting_resubmit` recorded |
| `T-adv-924` | Purge | After `retention.job_payload_days` | `output_text` is null; hashes remain; a replay still returns the stored outcome without text |

### 9.16.3 RTL, Persian and property tests

| ID | Case | Expected |
| --- | --- | --- |
| `T-rtl-901` | ZWNJ in «می‌روم» inside a `prose` slot | Preserved in storage and display; same `output_hash` on round trip; `ckey` removes it |
| `T-rtl-902` | U+202A..U+202E and U+2066..U+2069 in `prose`; the same in `code` and `structured` | Stripped with counts in `normalization_report`; `reject.forbidden_content` in the other two |
| `T-rtl-903` | Persian sentence containing an English product name, Latin digits and a short token | Every output block has `dir="auto"`; every inline fragment of submitted text sits in `<bdi>`; visual order checked against golden screenshots on the target browser set [V] |
| `T-rtl-904` | Persian digits ۱۲۳ and Arabic-Indic digits ١٢٣ in `prose` | Stored unchanged; `ckey` maps both to `123`; display never converts digits of submitted text, whatever the member's `digits` setting |
| `T-rtl-905` | Pairs differing only by Arabic or Persian Yeh and Kaf, ZWNJ presence, tatweel, vowel marks, digit script | Equal `ckey` and `dup_key`; the labelled pair set is written by a Persian-speaking reviewer [V] |
| `T-rtl-906` | Arabic presentation forms (U+FB50..U+FDFF, U+FE70..U+FEFF) from a pasted PDF | Stored as typed after NFC; `ckey` maps them to base letters |
| `T-rtl-907` | A letter followed by more than `screen.max_combining_run` combining marks; the same with two marks | `reject.schema_invalid`; accepted |
| `T-rtl-908` | Excerpt truncation inside a combining sequence, a surrogate pair and a ZWJ emoji sequence | Cut only on grapheme-cluster boundaries |
| `T-rtl-909` | ZWNJ and ZWJ in a `code` slot | Kept with flag `invisible_in_code`; shown as visible markers |
| `T-rtl-910` | Leading U+FEFF; U+FEFF mid-text in `prose` and in `code` | Leading one stripped everywhere; mid-text stripped in `prose`, `reject.forbidden_content` in `code` |
| `T-rtl-911` | A hidden instruction spelled in tag characters U+E0000..U+E007F | `reject.forbidden_content` in every context |
| `T-rtl-912` | `ex<U+200B>ample` and a Persian word split by U+200B | Stripped in `prose`; equal `ckey` to the unsplit form |
| `T-prop-901` | Normalization is idempotent | For generated strings over the whole Unicode range, `normalizeOutput(normalizeOutput(x)) = normalizeOutput(x)` |
| `T-prop-902` | No stripped class survives | For the same generator, a canonical text contains no code point of the stripped or rejected classes of 9.7.2 for its context |
| `T-prop-903` | Payload hash is order-independent | `payload_hash` is equal for every key order of the same body (RFC 8785) |
| `T-prop-904` | Single use | For any interleaving of N submit calls on one lease, at most one `Submission` exists, and `nonce_consumed_at` is set if and only if it exists |

### 9.16.4 Acceptance criteria

| ID | Given / When / Then |
| --- | --- |
| `AC-submit-01` | Given an `active` lease inside `expires_at` and the correct nonce, When a normal text is submitted, Then `201` with `state` = `received`, the lease is `submitted`, `nonce_consumed_at` is set, and the events `submission.received`, `lease.submission_received`, `cell.submitted` exist once |
| `AC-submit-02` | Given `now` between `expires_at` and `grace_until`, When the donor submits, Then `201` with `late` = true and no penalty is recorded |
| `AC-submit-03` | Given `now` after `grace_until`, When the donor submits, Then `410 LEASE_EXPIRED`, no `Submission`, and the cell is requeued by the reaper |
| `AC-submit-04` | Given a wrong nonce, When the donor submits, Then `403` with `reject.nonce_invalid`, the lease stays `active`, and a retry with the right nonce gives `201` |
| `AC-submit-05` | Given a consumed lease, When the same payload arrives again, Then `200` with `replayed` = true, no event is emitted and the ledger is unchanged |
| `AC-submit-06` | Given a consumed lease, When a different payload arrives, Then `409 STATE_CONFLICT` with `conflicting_resubmission` and the stored submission is unchanged |
| `AC-submit-07` | Given a body over `cell.envelope.max_submission_bytes`, When submitted, Then `413` and nothing is persisted |
| `AC-submit-08` | Given a `prose` text containing U+200B and U+202E, When submitted, Then the canonical text lacks both, `normalization_report` counts them, and the same in a `code` slot ends as `schema_failed` with `reject.forbidden_content` |
| `AC-submit-09` | Given a `prose` output with a URL and no exemption, When submitted, Then `state` = `quarantined`, the text is invisible to the requester, a reviewer's release resumes verification and a reviewer's rejection ends it with `reject.forbidden_content` |
| `AC-submit-10` | Given a donor who reuses a long output on a second cell with a different input, When submitted, Then `checks_failed` with `reject.duplicate_of_other_output` |
| `AC-submit-11` | Given `lease_to_submit_s` below `verify.timing_min_s`, When submitted, Then `checks_failed` with `reject.timing_anomaly` |
| `AC-submit-12` | Given an attested service outside the cell's allowed set, When submitted, Then `422` with `reject.attestation_invalid`, nothing persisted and the nonce unconsumed |
| `AC-submit-13` | Given a lease whose nonce was rotated, When the old nonce is sent, Then `403`; the new one gives `201`; a replay of `createLease` returns `lease_nonce` = null |
| `AC-submit-14` | Given a gold cell and a normal cell, When each is submitted, Then the two responses have the same fields and no field reveals the kind |
| `AC-submit-15` | Given stored text `<script>alert(1)</script>`, When any screen or export shows it, Then it appears as literal text and no script runs |
| `AC-submit-16` | Given the dry run, When `validateSubmission` is called, Then nothing is persisted, the nonce is unconsumed and `lease.validations` is incremented |

## 9.17 Observability, logging and alarms

Metric names follow S0.5 (`hamyar_<area>_<name>_<unit>`). No label carries content, a nonce or an identifier of a member. [D]

| Metric | Kind | Labels | Use |
| --- | --- | --- | --- |
| `hamyar_submission_received_total` | counter | `state`, `template_version_id` | Volume and outcome mix |
| `hamyar_submission_gate_rejections_total` | counter | `check_id`, `code` | Gate failures (SC-01..SC-15); a spike of SC-10 or SC-11 is a forgery or client-defect signal |
| `hamyar_submission_replays_total` | counter | none | Idempotent resubmits (9.10 case 4) |
| `hamyar_submission_conflicting_resubmissions_total` | counter | none | Case 5; non-zero rates need explanation |
| `hamyar_submission_quarantined_total` | counter | `flag_class` | Reviewer load; compared with the share released |
| `hamyar_submission_quarantine_age_seconds` | gauge | none | Age of the oldest unreviewed quarantine (alarm before `screen.quarantine_max_age_days`) |
| `hamyar_submission_duplicate_signals_total` | counter | `kind` (`d1`..`d3`) | 9.11 |
| `hamyar_submission_timing_signals_total` | counter | `kind` | 9.12 |
| `hamyar_submission_lease_to_submit_seconds` | histogram | `template_version_id` | Verified submissions only; the `CAL` distribution |
| `hamyar_submission_normalization_changes_total` | counter | `class` | Which character classes donors actually hit (tunes 9.7 with data) |
| `hamyar_submission_invariant_violations_total` | counter | `invariant` | Must stay zero: SC-14 failures, a stripped class found in canonical text, a second submission for one lease |

**Alarms** (entity `Alarm`, S0.7) [D]: any increment of `hamyar_submission_invariant_violations_total`; a sustained rise of SC-11 failures across many members; quarantine age above half of `screen.quarantine_max_age_days`; a template whose quarantine share exceeds the others by a margin set by the operator (feeds `template.autopause_report_count`).

**Never logged, never in an event, never in a metric label** [D]: `output_text`, `model_label`, the plaintext `lease_nonce`, bearer tokens, the removed characters of a normalization, matched detector text, raw IP addresses (S0.6.4). Logged: ids, hashes, sizes, check ids, reject codes, flag classes and counts.

## 9.18 Parameters used and added

Every default is an `initial configurable default`, replaced by the measurement in the last column (S0.10.4). Used parameters keep the definitions of S0.10.6; added parameters are reported as convention additions (below) and are completed by S16.* without renaming. [D]

**Used (defined in S0.10.6)**

| Name | Initial configurable default | Use here |
| --- | --- | --- |
| `cell.envelope.max_output_chars` | 6000 | 9.6, 9.7.3 |
| `cell.envelope.max_submission_bytes` | 32,768 | 9.6 |
| `cell.max_attempts` | 5 | 9.14.2 |
| `lease.timeout_s`, `lease.extend_s`, `lease.max_extensions`, `lease.submit_grace_s` | 1200, 600, 1, 120 | 9.4.4 |
| `lease.nonce_bytes` | 16 (constant) | 9.4.1 |
| `lease.reap_interval_s`, `lease.max_active_per_member` | 30, 3 | 9.4.4, 9.6 |
| `ratelimit.member_api_rpm`, `ratelimit.member_submissions_per_hour`, `ratelimit.member_leases_per_hour`, `ratelimit.public_rpm` | 120, 60, 30, 60 per IP hash | 9.6 |
| `verify.timing_min_s` | 5 | 9.12 |
| `verify.duplicate_similarity_threshold` | 0.95 | 9.11 |
| `screen.output_url_action` | `quarantine` | 9.9 |
| `calibration.min_samples_per_service` | 30 | 9.12 |
| `api.idempotency_ttl_s` | 86,400 | 9.10 |
| `retention.job_payload_days` | 30 | 9.14.3 |
| `template.autopause_report_count`, `template.autopause_window_s` | 5, 3600 | 9.9.2 |

**Added by this part** [A]

| Name | Type | Initial configurable default | Validation | Replaced by |
| --- | --- | --- | --- | --- |
| `cell.envelope.max_json_depth` | int | 16 | 2..64 | `TEC` parser limits on real devices |
| `cell.envelope.max_model_label_chars` | int | 80 | 1..200 | `CAL` labels donors actually type |
| `lease.max_gate_failures` | int | 5 | 1..100 | `OPS` observed honest retry counts |
| `lease.max_validations` | int | 10 | 0..100 | `CAL` copy-paste error rate |
| `lease.max_nonce_rotations` | int | 2 | 0..10 | `OPS` reload frequency on phones |
| `screen.max_combining_run` | int | 8 | 1..64 | `P1M` reviewed Persian sample |
| `screen.output_code_action` | enum | `quarantine` | `reject`, `flag_for_review`, `quarantine` | `P1M` incident log and release ratio |
| `screen.output_request_action` | enum | `quarantine` | same | `P1M` |
| `screen.output_max_urls` | int | 0 | 0..100 | `P1M` |
| `screen.quarantine_max_age_days` | days | 7 | 1..60 | `OPS` reviewer capacity |
| `verify.duplicate_min_chars` | int | 80 | 1..10000 | `P1M` rate of honest short agreement |
| `verify.duplicate_shingle_chars` | int | 5 | 2..20 | `P1M` |
| `verify.duplicate_minhash_perms` | int | 128 | multiple of 4 (S9-C2) | `OPS` index cost |
| `verify.duplicate_window_days` | days | 14 | 1..90 | `P1M` |
| `verify.timing_soft_ratio` | ratio | 0.25 | 0..1 | `CAL` |
| `verify.timing_regular_window_obs` | int | 20 | 5..1000 | `P1M` |
| `verify.timing_regular_cv` | ratio | 0.05 [H] | 0..1 | `P1M` |

The LSH layout uses 4 rows per band, so `bands = verify.duplicate_minhash_perms / 4` (32 at the default). Named cross-parameter constraints added (to be folded into S0.10.3): `S9-C1` `cell.envelope.max_submission_bytes >= 3 x cell.envelope.max_output_chars`; `S9-C2` `verify.duplicate_minhash_perms` is a multiple of 4; `S9-C3` `lease.max_validations >= 0` and `lease.max_gate_failures >= 1`. [A]

## 9.19 What this part cannot promise

Stated plainly, because FD Principle 11 forbids claiming more than can be shown. [D]

1. **Provenance.** A valid submission shows that a member with a live lease sent text in time. It does not show that any model produced the text, that the leased prompt was used, or that the named service was used (E1, E6, 9.13).
2. **Relayed or paraphrased copies and multiple accounts.** Similarity detection misses paraphrase, translation and light edits, and cannot see that two accounts are one person. Link analysis is probabilistic (9.11.3).
3. **Who pressed Send.** The platform automates only its own side and cannot see the volunteer's side. Timing regularity is a weak signal of scripting, not proof; a patient script defeats it (9.12).
4. **Detector coverage.** Classes L, C and A are heuristics with false positives and unknown false negatives; reviewer sampling estimates the second, imperfectly [H] (9.9.1).
5. **Freedom from XSS and injection.** The defense is structural and tested, not proven; browser features such as Trusted Types are [V] on the target phones, and a defect in any one escaping point is possible (9.8).
6. **The donor's own exposure.** The platform cannot stop a service's memory or connectors from acting on what the donor pastes into it (FD§5.5 injection note) or an attacker's content that reaches the donor through a cell input; that is addressed in S7.* and S11.* and remains a residual risk [H].
7. **Account takeover.** A stolen session token allows submission as that member; the nonce does not prevent it (9.4.6, S10.*).
8. **Calibrated thresholds.** Every timing, duplicate and size default is an initial configurable default, not a measurement, and simulation output is not evidence about people (S0.2 rule 3).
9. **Reviewer capacity.** Quarantine moves risk to a reviewer queue; if it is not staffed, cells age out and honest donors wait (`ISS-92`).

User-facing text about this stage says submissions are "checked" and results are "declared" by the volunteer, never "verified" or "guaranteed" unless an S8.* method actually verified them. [D]

## Issues raised

Problems and gaps found while specifying the return path. Each resolution is already applied in this file; C-001 consolidates them into S2.* and may record a different resolution. [D]

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-91` | major | FD§4.4, prompt | The FD's automatic "unit tests" check for code changes runs submitted code, which contradicts the rule that submitted content is never executed | Web, API and admin tiers never execute content; the one execution need is confined to an isolated, network-less, resource-limited, ephemeral runner returning only pass or fail and a truncated log. Until it is built and signed off under `SEC` [V], the check is `inconclusive`, the cell goes to audit, and `code_change_tests` cannot be approved (9.8.2) | proposed |
| `ISS-92` | major | FD§5.5 | The FD says outputs with links, code to run or requests for action are "flagged instead of shown" but defines no owner, queue, decision or deadline, so a flagged cell could wait forever and its donor's credit stay blocked | A quarantine lifecycle: reviewer decision (release or reject), hidden from everyone else, no reliability effect unless marked deliberate, age-out after `screen.quarantine_max_age_days`, queue-age metric and alarm (9.9.2, 9.17) | proposed |
| `ISS-93` | major | prompt scope E, FD§4.4 | "Detection of copy-paste of another donor's output" cannot separate collusion from honest agreement: honest runs of a deterministic task produce equal short outputs, and published Commons outputs are copyable | Similarity is a signal, with two narrow hard cases (cross-cell reuse of long text) and exclusions for short or schema-constrained outputs; no output is visible before its cells are accepted; limits stated (9.11) | proposed |
| `ISS-94` | minor | FD§3.4, S0.9.3 | A schema failure ends the attempt and burns one of `cell.max_attempts`, so an honest paste error or a griefing donor can exhaust a cell | A dry run `validateSubmission` with the syntactic checks only, the same normalization routine in the browser, and gate failures that consume nothing; the copy-paste error rate is measured under `CAL` and `cell.max_attempts` tuned [H] (9.5.4, 9.14.2) | proposed |
| `ISS-95` | minor | FD§3.4, S0.9.3 | S0.9.3 requeues an expired lease "at once", while `lease.submit_grace_s` accepts a late paste-back | The reaper acts at `grace_until = expires_at + lease.submit_grace_s`; `expires_at` stays the donor-facing deadline; state machines unchanged (9.4.4) | applied |
| `ISS-96` | minor | FD§5.6 | "Input and output hashes" do not say whether the hash covers what arrived or what is stored, and the two differ after normalization | `raw_hash` over the received string, `output_hash` over the canonical text; the manifest uses `output_hash` (9.7.4) | applied |
| `ISS-97` | minor | prompt scope E | A "minimum plausible time" cannot be derived before Phase 0, so a hard timing rule risks rejecting honest practiced donors | One hard floor, `verify.timing_min_s`, kept low and replaced by `CAL`; everything else is a flag, active only after `calibration.min_samples_per_service` samples (9.12) | proposed |
| `ISS-98` | major | prompt, S0.11.5 | S0.11.5 replays the stored response of an idempotent call, which for `createLease` would re-serve the plaintext nonce and force the idempotency store to hold secrets, contradicting hash-only storage | Secret response fields are not stored; replay returns `lease_nonce` = null with `details.nonce_redelivery` = `use_rotation`; `rotateLeaseNonce` recovers a lost nonce (9.4.3) | proposed |

**Convention additions made by this part** (not issues; listed so C-001 can fold them back) [A]

- `reject.attestation_invalid` added to the cell rejection reason list of S0.8.4 (9.13).
- Operations `submitResult`, `validateSubmission`, `rotateLeaseNonce` and their paths (9.3, 9.5); response fields `lease_nonce`, `details.reject_code`, `details.reason`, `details.nonce_redelivery`, `details.stored_submission_id`.
- Entity field requirements on `Lease` and `Submission`, and the table `submission_fingerprints` (9.4.5, 9.14.3).
- The 17 added parameters and constraints `S9-C1`..`S9-C3` (9.18).
- Signal names `signal.forgery_attempt`, `signal.conflicting_resubmit`, `signal.timing_below_floor`, `signal.timing_soft_fast`, `signal.timing_regular`; flag names in 9.9 and in SC-21 of 9.14.1; ops log event `submission.gate_rejected`; metrics of 9.17.
- `slot_context` (`prose`, `code`, `structured`) as a required declaration of every template output slot (S8.*), and the template output exemption list for flag classes (9.7.1, 9.9.1).
- Test ids numbered from 901 in each layer, and acceptance-criteria area `submit` (9.16).
- File name: the owner cell writes `spec/09-result-return.md`, whereas S0.13 lists `spec/09-result-return-abuse.md`.
