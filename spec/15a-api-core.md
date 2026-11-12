# 15. API specification (part a: identity, volunteer work, requester jobs, community)

*Spec part 15, first of the S15 files · owner cell C-020 · binding on the API implementation, the web client and the API conformance tests. Written against `spec/00-conventions.md` (S0) and Founding Document draft v0.1 (FD). Nothing here has been verified against any provider's terms or any law; every provider-dependent value is configuration data entered by a reviewer [V].*

## 15.1 Scope, inheritance and how to read this part

**Scope.** This file specifies the member surface (`auth_scheme` `member`) and the anonymous bootstrap endpoints (`auth_scheme` `none`, outside `/v1/public/*`) of S0 0.11.2: identity (`S15.5`), volunteer work (`S15.6`), requester jobs (`S15.7`), teams, share card, referral (`S15.8`), plus the rules that every surface shares: error catalogue (`S15.9`), idempotency per endpoint (`S15.10`), pagination (`S15.11`), rate-limit classes (`S15.12`), versioning (`S15.13`). The sibling S15 file owns `/v1/admin/*`, `/v1/public/*`, member-facing appeals and the event and webhook interfaces [A]. This file occupies `S15.1`..`S15.19`; the sibling starts at `S15.20` (`ISS-153`). [D]

**Inheritance.** S0 0.11.1 to 0.11.7 (transport, surfaces, error model, authentication, `Idempotency-Key`, cursors, concurrency and rate-limit headers) are binding and are not restated except where this part makes them concrete. Where this part and S0 disagree, S0 wins and the disagreement is an issue, never a silent variant. Names (entities, ids, enums, states, events, parameters) are used exactly as in S0. [D]

**Operation tables.** Every endpoint has one row; `op` ids are lowerCamelCase (0.5) and are the keys of the generated OpenAPI 3.1 document that `BM0` conformance tests check (`S17.*`) [A].

| Column | Meaning |
| --- | --- |
| `op` | Operation id |
| Method and path | Path under `/v1`; `{x_id}` is an id of the prefix in 0.7 |
| Auth | `none` or `member` (0.8.2) |
| Idem | `R` `Idempotency-Key` required (missing: `400 VALIDATION_FAILED`, reason `idempotency_key_missing`); `O` optional, honored if sent; `-` safe read, no key; `X` key ignored and never stored (the operation is single-use by construction) |
| RL | Rate-limit class, `S15.12` |
| OK | Success status |
| Events | Events of S0 0.9 emitted in the same transaction; `+name` is an event this part proposes (convention gap list in `## Issues raised`) |

**API-level guarantees that follow from the ground rules** [D]

- No endpoint accepts or returns a provider credential, cookie, session, chat link or chat-page content. The only provider-facing artifact is an optional `open_url` that a human opens and in which a human presses Send (FD Principle 3; prompt ground rule 3).
- No response carries another member's `mem_` id, any `vol_` handle toward a requester, an IP address or an e-mail address other than the caller's own, masked (0.6.3, 0.6.4).
- Every operation that moves credit or creates a job, lease, submission, report or grant requires `Idempotency-Key`, and also has natural idempotency underneath (0.11.5).
- Every user-facing promise in a field name or copy key says "declared", never "guaranteed" (FD Principle 11).
- Three launch switches (`launch.members_may_join`, `launch.member_jobs_enabled`, `launch.minting_enabled`) default to `false` and are enforced in the request pipeline (`S15.4`), not in clients.

## 15.2 Notation: types and schema shorthand

| Shorthand | Meaning |
| --- | --- |
| `id<pfx>` | Identifier `<pfx>_<ulid>` (0.6.3), for example `id<job>` |
| `ucr` | Integer string, base 10, no leading zeros, 0..9223372036854775807 (0.6.1); field names end `_ucr` |
| `ppm` | Integer 0..2^53-1, 1.0 = 1,000,000; field names end `_ppm` |
| `ts` | RFC 3339 UTC with `Z`, whole seconds (0.6.2); `date` is `YYYY-MM-DD`, Gregorian, UTC day; `dur_s` is integer seconds |
| `hash` | `sha256:` followed by 64 lowercase hex characters (0.6.4) |
| `b64u<n>` | Base64url without padding that decodes to exactly n bytes |
| `text<n>` | String of at most n Unicode code points, valid UTF-8, no NUL, stored verbatim: no normalization, bidirectional controls kept (display isolates them; `S9.*`) |
| `enum<name>` | A value of the S0 0.8 enum of that name |
| `copy_key` | `copy.<area>.<key>` (0.5); the client renders `fa` or `en` text |
| `T?` / `T/null` | Optional field / nullable field |
| `[T]` | Array |
| `Page<T>` | `{ data: [T], page: { next_cursor: string/null, limit: int } }` (0.11.1) |

Schema blocks list `field: type`. A response object named in the text (for example `Member`) is the same object everywhere it appears. Every `2xx` body is the resource itself (0.11.1). Unknown enum values in a response MUST be treated by clients as "unknown" and never crash the client (`S15.13`). [D]

## 15.3 Common request and response rules

**Request headers** [D]

| Header | Rule |
| --- | --- |
| `Authorization` | `Bearer <token>` on `member` endpoints only (`S15.4`) |
| `Content-Type` | `application/json; charset=utf-8` on every request with a body; otherwise `415 UNSUPPORTED_MEDIA_TYPE` |
| `Idempotency-Key` | 16 to 64 characters `^[A-Za-z0-9_-]+$` (0.11.5); client-generated (ULID or random UUID) |
| `If-Match` | An `ETag` from a previous read; optional on member resources, mismatch is `412 PRECONDITION_FAILED` |
| `Accept-Encoding` | `gzip` and `br` accepted for responses (low bandwidth, FD§10); request bodies are never compressed [A] |
| `Origin` | Must be on the configured front-end allow-list; the API never reflects an arbitrary origin and sends no `Access-Control-Allow-Credentials` (no cookies) [D] |

**Response headers** [D]

| Header | Rule |
| --- | --- |
| `X-Request-Id` | Always; equals `error.request_id`; format `req_<ulid>` |
| `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` | On every rate-limited route (0.11.7); `Retry-After` also on `429` and on `503` when known |
| `Idempotent-Replayed: true` | On a replayed stored response (0.11.5) |
| `ETag` | On resources that accept `If-Match` |
| `Location` | On `201`: the canonical path of the created resource |
| `Cache-Control: no-store` | Every authenticated response (0.11.7) |
| `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Strict-Transport-Security` | Every response |
| `Api-Revision`, `Deprecation`, `Sunset`, `Link` | Versioning, `S15.13` |

**Rules** [D]

1. **Strict requests.** An unknown field, a duplicate JSON key, a wrong type, or a number where an `ucr` string is required is `400 VALIDATION_FAILED`. The response lists every field error at once in `details.fields` as `{path, code, message}` with `code` in `required`, `type`, `format`, `range`, `length`, `enum`, `unknown_field`, `not_allowed`. Responses are lenient: clients ignore unknown fields (0.11.1).
2. **Not found, not forbidden.** A resource that belongs to another member, or that is not visible to the caller under the opt-in rule `R8`, is `404 NOT_FOUND`. Existence is never confirmed by a different status or message. An unknown route or method is `404 NOT_FOUND`, reason `route_not_found`.
3. **Server time only.** No request field carries a client clock value that the server trusts; client-reported timings are not accepted at all (timing anomalies are computed from `issued_at` and `received_at`, `S9.*`).
4. **Money and ratios** are `*_ucr` strings and `*_ppm` integers; the display decimal is a client concern (0.6.1).
5. **Logs.** Access logs record the route template, method, status, duration, `request_id`, principal type, rate-limit class and `error.code` only. They never record request or response bodies, tokens, nonces, codes, keys, submitted text, uploaded content, IP addresses or e-mail addresses (`retention.request_log_days`; `S10.*` owns the full list).
6. **Secrets in responses** appear exactly once, at creation, and are listed in `S15.10` (session token, lease nonce, invite code, device-link code, team join code).
7. **Reachability.** The API host and the front-end origin are configuration, never constants in client code; reachability of the host from Iran is [V] (`G2`).

## 15.4 Authentication, sessions and the request pipeline

**Schemes** (0.11.4) [D]

| Scheme | Credential | Notes |
| --- | --- | --- |
| `member` | `Authorization: Bearer <token>`; token is 256 bits from the OS CSPRNG, base64url (43 characters), opaque; the server stores only its SHA-256 (0.6.4) | Obtained only from `createSession`. Never in a URL, query, body or cookie. An admin token here is `401 AUTH_INVALID`, reason `wrong_scheme` |
| `none` | nothing | `createIdentityChallenge`, `createMember`, `checkInvite`, `createSession`, `recoverMember`, `redeemDeviceLink` only; each is rate-limited per IP hash and per device hash |

**Challenge and signature (API view)** [D][A]

```
challenge = POST /v1/identity-challenges { purpose }      purpose in create, session, rotate, recover, device_link
message   = "hamyar:v1:" + purpose + ":" + challenge + ":" + subject      subject: key id or public key
signature = Ed25519(private_key, message)
```

A challenge is 256 random bits, stored only as SHA-256, bound to its purpose, single-use, and valid for `identity.challenge_ttl_s`. Verification is constant-time and an unknown key, a revoked key and a wrong signature all return the same `401 AUTH_INVALID`, reason `credentials_invalid` (no key enumeration). The exact byte layout, the recovery-key derivation and every cryptographic parameter are owned by `S10.*`; where `S10.*` differs in detail it wins and the field names here stay [A][V: crypto review before launch, `SEC`].

**Session lifecycle** [D]

- Lifetimes: idle `session.member_idle_ttl_s`, absolute `session.member_abs_ttl_s`; idle expiry slides on use (coalesced writes). Expiry returns `401 AUTH_EXPIRED`, reason `session_idle_expired` or `session_absolute_expired`.
- At most `session.max_active_per_member` live sessions per member (convention gap); the oldest idle one is revoked when exceeded.
- A session ends when: the member logs out; its key is revoked or its rotation grace (`identity.key_rotation_grace_s`) ends; the member recovers (all sessions); the member is `closed`; `kill.member.<mem_id>` is engaged.
- `suspended` and `banned` members can still authenticate, read their own data, revoke sessions and (sibling file) file appeals; every operation marked **active only** below returns `403 FORBIDDEN`, reason `member_suspended` or `member_banned`. `closed` members cannot authenticate (`credentials_invalid`).

**Pipeline order** [D]. When several errors apply, the lowest step wins; this order is part of the contract and is tested (`AC-api-02`).

```
 1 parse        body over limit -> 413; media type -> 415; JSON syntax -> 400 MALFORMED_REQUEST
 2 route        unknown route -> 404 NOT_FOUND (route_not_found)
 3 ratelimit-1  by IP hash (and device hash on bootstrap routes) -> 429 RATE_LIMITED
 4 authenticate wrong scheme or bad token -> 401; expired -> 401 AUTH_EXPIRED
 5 ratelimit-2  by member id, classes of S15.12 -> 429 RATE_LIMITED
 6 idempotency  key required but missing -> 400; lookup (scope, key):
                  same body hash  -> replay stored 2xx or deterministic 4xx, Idempotent-Replayed: true
                  other body hash -> 422 IDEMPOTENCY_KEY_MISMATCH
                  still running  -> 409 IDEMPOTENCY_IN_PROGRESS (+ Retry-After)
 7 gates        launch.* switch -> 403 LAUNCH_GATE_CLOSED; kill switch -> 503 KILL_SWITCH_ENGAGED;
                member status and recovery cooldown -> 403 FORBIDDEN
 8 validate     schema, enums, sizes -> 400 VALIDATION_FAILED / 413
 9 resolve      absent, not owned or not visible -> 404 NOT_FOUND
10 precondition If-Match -> 412 PRECONDITION_FAILED
11 guards       state machine and business rules -> 409 / 410 / 422
12 execute      ONE database transaction: state change + ledger postings + outbox events (S4.*)
                + the idempotency record. A crash leaves all of it or none of it.
13 respond      headers of 15.3, 2xx
```

Replays are counted as requests at step 5 but do not pay the write weight (`ratelimit.write_weight`). Steps 8 to 11 outcomes that are deterministic `4xx` are stored with the key; `5xx` outcomes are not (0.11.5).
