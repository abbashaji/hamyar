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

## 15.5 Identity endpoints

Decisions behind the shapes [D]: the member keypair and the recovery secret are generated on the device and the server never sees a private key or the recovery secret (FD§3.2 step 1; no signup, no e-mail); the server stores public keys (`MemberKey`); there are no passwords. The recovery key is a 128-bit secret (`identity.recovery_key_bits`) from which the client derives a second Ed25519 keypair; the API only ever carries its public half and signatures [A][V: `SEC`].

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `createIdentityChallenge` | `POST /v1/identity-challenges` | none | X | `RL-BOOT` | 201 | - |
| `createMember` | `POST /v1/members` | none | R | `RL-BOOT` | 201 | `member.created`, `+invite.redeemed` |
| `checkInvite` | `POST /v1/invite-checks` | none | O | `RL-BOOT` | 200 | - |
| `createSession` | `POST /v1/sessions` | none | X | `RL-BOOT` | 201 | - |
| `getSession` | `GET /v1/sessions/{session_id}` (`current` is an alias) | member | - | `RL-READ` | 200 | - |
| `listSessions` | `GET /v1/sessions` | member | - | `RL-READ` | 200 | - |
| `revokeSession` | `DELETE /v1/sessions/{session_id}` (`current` = log out) | member | O | `RL-WRITE` | 204 | - |
| `getMe` | `GET /v1/members/me` | member | - | `RL-READ` | 200 | - |
| `updateMe` | `PATCH /v1/members/me` | member | O | `RL-WRITE` | 200 | - |
| `setEmail` | `PUT /v1/members/me/email` | member | O | `RL-WRITE` | 202 | - |
| `confirmEmail` | `POST /v1/members/me/email/confirmations` | member | O | `RL-WRITE` | 200 | - |
| `removeEmail` | `DELETE /v1/members/me/email` | member | O | `RL-WRITE` | 204 | - |
| `listMemberKeys` | `GET /v1/member-keys` | member | - | `RL-READ` | 200 | - |
| `rotateKey` | `POST /v1/member-keys/rotations` | member | R | `RL-WRITE` | 201 | `member.key_rotated` |
| `revokeMemberKey` | `DELETE /v1/member-keys/{key_id}` | member | R | `RL-WRITE` | 204 | `+member.key_revoked` |
| `recoverMember` | `POST /v1/recoveries` | none | R | `RL-RECOVER` | 201 | `member.recovered` |
| `createDeviceLink` | `POST /v1/device-links` | member | R | `RL-WRITE` | 201 | - |
| `redeemDeviceLink` | `POST /v1/device-links/redemptions` | none | R | `RL-BOOT` | 202 | - |
| `approveDeviceLink` | `POST /v1/device-links/{device_id}/approval` | member | R | `RL-WRITE` | 200 | `member.device_linked` |
| `denyDeviceLink` | `DELETE /v1/device-links/{device_id}` | member | O | `RL-WRITE` | 204 | - |
| `listDevices` | `GET /v1/devices` | member | - | `RL-READ` | 200 | - |
| `revokeDevice` | `DELETE /v1/devices/{device_id}` | member | R | `RL-WRITE` | 204 | `+member.device_revoked` |
| `createInvite` | `POST /v1/invites` | member | R | `RL-WRITE` | 201 | `+invite.created` |
| `listInvites` | `GET /v1/invites` | member | - | `RL-READ` | 200 | - |
| `revokeInvite` | `DELETE /v1/invites/{invite_id}` | member | R | `RL-WRITE` | 204 | `+invite.revoked` |

**Objects**

```
Member   { id: id<mem>, status: enum<member_status>, trust_tier: enum<trust_tier>, locale: enum<locale>,
           digits: enum<digits>, calendar: enum<calendar>, time_zone: text<64>/null,
           email: { state: "none"/"unconfirmed"/"confirmed", masked: text<64>/null },
           email_notifications: { credit_expiry: bool },
           recovery: { cooldown_until: ts/null, recoveries_90d: int },
           security_notices: [ { kind: "key_rotated"/"device_linked"/"recovered"/"recovery_key_rotated", at: ts } ],
           created_at: ts }                                              ETag = row_version
Key      { id: id<mky>, kind: "device"/"recovery", state: "pending"/"active"/"retiring"/"revoked",
           public_key: b64u<32>, created_at: ts, retires_at: ts/null }
Session  { id: id<ses>, created_at: ts, idle_expires_at: ts, expires_at: ts, device_id: id<dev>/null, is_current: bool }
Device   { id: id<dev>, link_state: "pending"/"awaiting_approval"/"linked"/"denied"/"expired"/"revoked",
           created_at: ts, linked_at: ts/null, last_seen_on: date/null }
Invite   { id: id<inv>, state: "active"/"redeemed"/"expired"/"revoked", created_at: ts, expires_at: ts, redeemed_at: ts/null }
```

`trust_tier` is the 0.9.4 state set; the reliability estimate behind it is not exposed by this part [A]. `last_seen_on` is a coarse date, never a timestamp (metadata minimization, FD Principle 8). The key and invite state names are convention additions.

**Schemas** (errors beyond the common set of `S15.9` are listed per operation)

```
createIdentityChallenge  req { purpose: "create"/"session"/"rotate"/"recover"/"device_link", key_id?: id<mky> }
                         201 { challenge: b64u<32>, expires_at: ts }      always returned, even for an unknown key_id
createMember             req { public_key: b64u<32>, recovery_public_key: b64u<32>,
                               proof: b64u<64>, recovery_proof: b64u<64>,   both sign the "create" message over both public keys
                               device_token: b64u<16>, invite_code: text<32>?, locale: enum<locale>? }
                         201 { member: Member, key: Key, recovery_key: Key,
                               session_challenge: { challenge: b64u<32>, expires_at: ts } }
                         err 403 LAUNCH_GATE_CLOSED (switch launch.members_may_join); 409 ALREADY_EXISTS (public_key_exists);
                             422 UNPROCESSABLE (invite_required, invite_unusable); 422 CAP_EXCEEDED (invite_tree_full, invite_tree_depth);
                             429 RATE_LIMITED (details.scope: device, ip_hash, invite_tree)
checkInvite              req { code: text<32> }   200 { usable: bool, reason: null/"unknown"/"expired"/"redeemed"/"revoked" }
createSession            req { challenge: b64u<32>, key_id: id<mky>, signature: b64u<64>, device_token: b64u<16>? }
                         201 { session: Session, token: string, member: Member }       the only place a session token appears
                         err 401 AUTH_INVALID (credentials_invalid, key_pending); 401 AUTH_EXPIRED (challenge_expired)
updateMe                 req (JSON Merge Patch) { locale?, digits?, calendar?, time_zone?: text<64>/null, email_notifications?: { credit_expiry?: bool } }
                         200 Member      time_zone validated against the tz database [V]; never inferred from an IP address
setEmail                 req { email: text<254> }   202 { email: { state: "unconfirmed", masked: text<64> } }
confirmEmail             req { code: text<12> }     200 { email: { state: "confirmed", masked: text<64> } }
rotateKey                req { kind: "device"/"recovery", key_id: id<mky>, challenge: b64u<32>, signature: b64u<64>,
                               new_public_key: b64u<32>, new_key_proof: b64u<64> }
                         201 { key: Key, retired_key: Key/null }        key_id and signature: a fresh signature by an active device key
revokeMemberKey          err 409 STATE_CONFLICT (last_active_key, key_state_invalid)
recoverMember            req { recovery_public_key: b64u<32>, challenge: b64u<32>, recovery_signature: b64u<64>,
                               new_public_key: b64u<32>, new_key_proof: b64u<64>, device_token: b64u<16> }
                         201 { member: Member, key: Key, revoked_key_ids: [id<mky>], session_challenge: { challenge, expires_at } }
                         err 401 AUTH_INVALID (credentials_invalid); 403 FORBIDDEN (recovery_quota); 429 RATE_LIMITED
createDeviceLink         201 { device_id: id<dev>, code: text<32>, expires_at: ts }     the code appears once
redeemDeviceLink         req { code: text<32>, new_public_key: b64u<32>, proof: b64u<64>, device_token: b64u<16> }
                         202 { device_id: id<dev>, link_state: "awaiting_approval", sas: text<8> }
approveDeviceLink        req { sas: text<8> }   200 { device: Device, key: Key }     the member compares sas on both screens
createInvite             201 { invite: Invite, code: text<32> }                          the code appears once
                         err 422 UNPROCESSABLE (invite_requirement_unmet); 422 CAP_EXCEEDED (invite_limit)
```

`getMe`, `listMemberKeys`, `listSessions`, `listDevices` and `listInvites` return the objects above (lists as `Page<T>`, `S15.11`). `listInvites` shows state and `redeemed_at` only: the inviter never learns who redeemed an invite, and the invitee never learns the inviter.

**Behavior and guards**

- **Create (no signup).** `createMember` needs no prior challenge: both proofs are signatures over the domain-separated creation message, which proves possession of both private keys (a mistyped recovery key cannot lock the member out). It returns no token; it returns a ready `session_challenge` so the client signs it and calls `createSession` at once (two round trips after creation, low bandwidth; time to first verified cell is measured, `V1`). A retry with the same `Idempotency-Key` replays the stored body; a new key with a known `public_key` is `409 ALREADY_EXISTS`. [D]
- **Open or invite-only.** `invite.required_to_join` (convention gap, initial configurable default `true` for the closed Phase 1 pilot) decides whether `invite_code` is required. `launch.members_may_join` = `false` refuses every `createMember` with `LAUNCH_GATE_CLOSED`, regardless of invites. Redemption is atomic with creation: the invite, the member, the tree edge and the tree limits (`invite.tree_max_members`, `invite.tree_max_depth`) are checked and written in one transaction, so no unredeemed member row exists when invites are required. `invite_unusable` covers unknown, expired, redeemed and revoked codes alike (no enumeration); `checkInvite` is the only place the four states are distinguished, and only to a holder of the code. [D]
- **Invite issuing.** Allowed when the member is `active`, has at least `invite.min_accepted_cells_to_issue` accepted cells, and has fewer than `invite.max_active_per_member` active invites; `expires_at = created_at + invite.ttl_days x 86,400 s`. A revoked or expired invite can never be redeemed. [D]
- **Sessions.** `createSession` is single-use per challenge; a lost response means a new challenge. The key must be `active` or `retiring`; a `pending` device key (not yet approved) returns `key_pending` only after its signature verified, so the reason cannot be probed. [D]
- **Rotation.** `kind` `device`: the new key becomes `active`, the signing key becomes `retiring` and is `revoked` at `now + identity.key_rotation_grace_s`; sessions of a revoked key end then. `kind` `recovery`: the new recovery key is `pending` and becomes `active` after the grace; during the grace both recovery keys work, so an attacker holding a stolen device session cannot silently replace the recovery key; a `recovery_key_rotated` notice is added to `security_notices`. [D]
- **Revocation.** `revokeMemberKey` revokes a device key at once (a lost phone) and ends its sessions; it cannot revoke the last active device key and cannot revoke a recovery key (rotate it instead). [D]
- **Recovery** (account takeover is the main abuse risk, `S10.*` threat model). Given a valid recovery signature, `recoverMember` in one transaction: revokes every device key and every session; denies every pending device link; registers the new key; sets `recovery.cooldown_until = now + identity.recovery_cooldown_s`; appends a `recovered` notice; emits `member.recovered`. A member may recover at most `identity.recovery_max_per_90d` times in 90 days (checked after the proof, so the quota cannot be used to learn that a member exists). During the cooldown the member may contribute and read but `confirmJob`, `createReservation` and `createJob` with `submit` return `403 FORBIDDEN`, reason `recovery_cooldown`, `details.until`. Residual risk: whoever holds the recovery key can take the account; the platform cannot promise otherwise [V: `SEC`]. [D][A]
- **Device link** (scope A). Old device: `createDeviceLink` creates a `Device` in `link_state` `pending` and a one-time code valid `identity.device_link_code_ttl_s`. New device: `redeemDeviceLink` presents the code and its new public key and gets a short authentication string `sas` (derived from the code and the new key; format owned by `S10.*`); the code is consumed on the first redemption attempt that finds it. Old device: `approveDeviceLink` with the `sas` the member read from the new screen registers the `device` key as `active` and emits `member.device_linked`. A code that is expired, consumed or unknown returns `404 NOT_FOUND` (same body for all three). `denyDeviceLink` ends a pending link; `revokeDevice` revokes every key and session bound to a device. [D]
- **E-mail is optional and never authenticates or recovers.** It receives only the opt-in notices of `email_notifications` (for example the `credit.expiry_notice_days` warning). It is stored only encrypted under an application key plus a keyed hash (0.7: never in clear text), confirmed by a one-time code, and deletable. Whether to ship it at all, and its delivery interface, is decided in `S10.*` and `S4.*` because an e-mail address is a de-anonymization vector for members in a high-risk context [V]. [D][A]

Given / When / Then

- `AC-api-01` Given `launch.members_may_join` is `false`, When any client calls `createMember` with a valid body and invite, Then `403 LAUNCH_GATE_CLOSED` with `details.switch` = `launch.members_may_join` and no row is written.
- `AC-api-03` Given an active member recovered 30 seconds ago, When they call `confirmJob`, Then `403 FORBIDDEN` reason `recovery_cooldown` with `details.until` equal to `cooldown_until`.

## 15.6 Volunteer endpoints

The volunteer flow of FD§3.2 steps 2 to 4 and FD§5.5, with the human pressing Send. Operations marked **active only** return `403 FORBIDDEN` for `suspended` and `banned` members (`S15.4`). [D]

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `listServices` | `GET /v1/services` | member | - | `RL-READ` | 200 | - |
| `listTopicCategories` | `GET /v1/topic-categories` | member | - | `RL-READ` | 200 | - |
| `getOptIns` | `GET /v1/members/me/opt-ins` | member | - | `RL-READ` | 200 | - |
| `replaceOptIns` | `PUT /v1/members/me/opt-ins` | member | O | `RL-WRITE` | 200 | `member.optin_changed` |
| `listOfferedCells` | `GET /v1/cells/offers` | member | - | `RL-READ` | 200 | - |
| `declineOffer` | `POST /v1/cells/{cell_id}/declines` | member | O | `RL-WRITE` | 204 | `+offer.declined` |
| `createLease` (active only) | `POST /v1/cells/{cell_id}/leases` | member | R | `RL-LEASE` | 201 | `cell.leased`, `lease.issued` |
| `getLease` | `GET /v1/leases/{lease_id}` | member | - | `RL-READ` | 200 | - |
| `listLeases` | `GET /v1/leases` | member | - | `RL-READ` | 200 | - |
| `expandLeasePrompt` | `POST /v1/leases/{lease_id}/expansions` | member | O | `RL-WRITE` | 200 | - |
| `issueLeaseNonce` | `POST /v1/leases/{lease_id}/nonces` | member | R | `RL-WRITE` | 201 | - |
| `extendLease` | `POST /v1/leases/{lease_id}/extensions` | member | R | `RL-WRITE` | 200 | - |
| `releaseLease` | `POST /v1/leases/{lease_id}/release` | member | R | `RL-WRITE` | 200 | `lease.released`, `cell.declined` |
| `createReport` (active only) | `POST /v1/reports` | member | R | `RL-REPORT` | 201 | `report.filed` |
| `listReports`, `getReport` | `GET /v1/reports`, `GET /v1/reports/{report_id}` | member | - | `RL-READ` | 200 | - |
| `submitResult` (active only) | `POST /v1/leases/{lease_id}/submission` | member | R | `RL-SUBMIT` | 201 | `submission.received` and the outcome events of 0.9.3 |
| `getSubmission`, `listSubmissions` | `GET /v1/submissions/{submission_id}`, `GET /v1/submissions` | member | - | `RL-READ` | 200 | - |
| `getBalance` | `GET /v1/balance` | member | - | `RL-READ` | 200 | - |
| `listLots` | `GET /v1/balance/lots` | member | - | `RL-READ` | 200 | - |
| `listLedgerEntries` | `GET /v1/balance/entries` | member | - | `RL-READ` | 200 | - |
| `getStarterGrant` | `GET /v1/members/me/starter-grant` | member | - | `RL-READ` | 200 | - |
| `claimStarterGrant` (active only) | `POST /v1/starter-grants` | member | R | `RL-WRITE` | 201 | `ledger.entry_committed` |

### 15.6.1 Services, topics and opt-ins

```
ServiceView  { id: id<svc>, display_name: text<80>, supports_prefill: bool, copy_only: bool, max_url_chars: int/null,
               clean_chat_hint_key: copy_key, advice_copy_keys: [copy_key] }
Topic        { id: id<top>, name_key: copy_key, sensitive: bool, opted_in: bool }
OptIns       { purposes: [enum<purpose>], sensitivities: [enum<sensitivity>], licenses: [enum<license>],
               service_requirements: [enum<service_requirement>], service_ids: [id<svc>], topic_category_ids: [id<top>],
               updated_at: ts }                                                       ETag = row_version
```

- `listServices` returns only registry entries in state `approved` (0.9.6) with `adapter.*` capabilities (0.8.3); `advice_copy_keys` derive from the `info.*` flags (for example `info.provider_trains_on_chats` = `yes` adds a clean-chat advice key). Every value is entered by a reviewer; nothing here names or assumes a provider [V: `G0`, `G2`]. [D]
- `replaceOptIns` replaces the whole object. Defaults for a new member come from `optin.default_purposes`, `optin.default_sensitivities`, `optin.default_licenses`, `optin.default_service_requirements`; every sensitive `Topic` is opted out (`optin.sensitive_topics_default` = `false`). `P2` and `P3` need an explicit value; `S2` and `S3` are never accepted values (`400 VALIDATION_FAILED`, reason `option_not_selectable`); a `service_ids` entry must be an `approved` service. A change takes effect for the next `listOfferedCells` and never retroactively cancels a lease already held (`R9` is about policy, not opt-ins). [D]

### 15.6.2 Offers, leasing, declining

```
CellCard   { task: "run"/"review", purpose: enum<purpose>, license: enum<license>, sensitivity: enum<sensitivity>,
             service_requirement: enum<service_requirement>, pinned_service_ids: [id<svc>],
             template: { id: id<tpl>, version_id: id<tpv>, name: text<80>, job_type: enum<job_type> },
             topic_category_ids: [id<top>], expected_time_s: dur_s, origin: "commons"/"member",
             provenance: { reviewed_on: date, reviewer_count: int, policy_version_id: id<plv> },
             downstream_use_uncontrolled: bool, requires_expansion: bool,
             expansion_reason: null/"first_use_of_template"/"non_default_category" }
Offer      { cell_id: id<cel>, card: CellCard }
Lease      { id: id<lse>, cell_id: id<cel>, state: "active"/"submitted"/"expired"/"released"/"revoked",
             issued_at: ts, expires_at: ts, extensions_used: int, extensions_max: int, submit_grace_until: ts/null }
WorkOrder  { prompt: { text: string, hash: hash, char_count: int }/null, prompt_state: "available"/"expansion_required",
             output: { format: "text"/"json", max_chars: int, max_bytes: int, schema_hint_key: copy_key/null },
             service: { service_id: id<svc>, display_name: text<80>, supports_prefill: bool, open_url: string/null,
                        copy_only: bool, max_url_chars: int/null }/null,
             clean_chat_hint_key: copy_key }
```

`provenance` feeds the card sentence "A stranger asked for this; the text below was reviewed by a reviewer on [date]" (FD§5.5; copy key `copy.cell.provenance_line`, `S11.*`). `origin` tells the volunteer whether it is a Commons job or a member job and nothing about who asked. `downstream_use_uncontrolled` is `true` for `P1` output (FD§5.7 failure mode 3).

**What a volunteer can never learn from the API** [D][A]: `cell_kind` and whether a cell is `primary`, `gold`, `audit`, `third` or `rework`; a `review` cell appears only as `task` = `review` (its gold cells stay hidden); the job, the requester, the other executor of an audit, or any comparison result. Gold and audit cells are therefore indistinguishable from primary cells before submission (`ISS-152`).

```
listOfferedCells(member, filters, cursor):                       order: server priority (S8.*, S9.*), never price or requester
  candidates = cells with state = queued
  keep only cells visible to member under R8:
      cell.purpose in optin.purposes AND cell.sensitivity in optin.sensitivities AND cell.license in optin.licenses
      AND cell.service_requirement in optin.service_requirements
      AND (topics of the cell not sensitive OR in optin.topic_category_ids)
      AND exists s in optin.service_ids that satisfies the requirement (M0: any approved; M1: in pinned set; M2: open-weight entry)
  drop: Commons cells while launch.minting_enabled = false or kill.all_minting is engaged; cells of a paused template or a suspended service;
        cells of the member's own jobs; cells the member already executed or declined; audit cells whose first executor is the member
  drop: everything if member headroom or daily earn cap leaves no room (see createLease quotas)
  window = first `limit` after the cursor ; filters (service_id, template_id, job_type) can only narrow, never widen
```

The list carries card metadata only, never the prompt (limits bulk harvesting of requester text to members who actually take the work; FD§5.5 "can see" holds because decline after viewing the prompt is free). A cell on a page may be leased by someone else before the member acts; that is the normal race, not an error of the list. [D]

```
createLease(member, cell_id, service_id):        req { service_id: id<svc> }
  201 { lease: Lease, cell: { id: id<cel>, card: CellCard }, work: WorkOrder, nonce: b64u<16> }   nonce appears here and in issueLeaseNonce only
  pipeline gates:   member active; launch.minting_enabled for Commons cells; kill switches (template, service)
  visibility:       cell not visible under R8, own-job cell, already-executed cell            -> 404 NOT_FOUND
  service:          service_id not in optin.service_ids or not eligible for the requirement   -> 422 UNPROCESSABLE (service_not_eligible)
  quota:            active leases >= lease.max_active_per_member                              -> 422 CAP_EXCEEDED (active_lease_limit)
                    balance + 1,000,000 ucr x (active leases + 1) > member cap               -> 422 CAP_EXCEEDED (member_credit_cap)
                    earned today + 1,000,000 ucr x (active leases + 1) > mint.per_member_daily_cap_credits -> 422 CAP_EXCEEDED (daily_earn_cap)
  race:             in one transaction: UPDATE cells SET state = 'leased' WHERE id = :id AND state = 'queued'   (exactly one winner)
                    loser                                                                     -> 409 LEASE_CONFLICT (cell_not_queued)
  effect:           Lease(active, expires_at = issued_at + lease.timeout_s); nonce stored as SHA-256 only; events cell.leased, lease.issued
```

The two cap checks at lease time use "potential earnings" so a member cannot hold credit they could not be paid; the member cap is `credit.member_cap_credits` x `trust.cap_multiplier.<tier>`; where `S6.*` places enforcement differently, `S6.*` wins [A]. `getLease` returns the lease and the work order while `state` is `active` (the prompt only when `prompt_state` is `available`) and metadata only afterward; it never returns the nonce.

- **Mandatory expansion** (FD§5.5). When `requires_expansion` is `true`, `createLease` and `getLease` return `prompt: null`, `prompt_state: expansion_required`; `expandLeasePrompt` returns the prompt and records the expansion on the lease, and `submitResult` without it is `409 STATE_CONFLICT`, reason `expansion_required`. The server can prove the prompt was requested, not that it was read ("can see" is guaranteed, "has read" is not). `requires_expansion` is `true` for the member's first lease on a `template_id` and for any non-default category (`optin.sensitive_topics_default`, `P2`, `P3`); `ui.card.expand_required_first_use` is a constant `true`. [D][H: whether this reduces blind pasting is measured by `ui.comprehension_check_rate` experiments, `S13.*`]
- **Adapter.** `work.service` is built server-side from the registry entry. `open_url` is the entry's `adapter.prefill_url_template` with `{prompt}` URL-encoded, present only if `adapter.supports_prefill` is `true`, `prefilled_link_use` is `yes` and the result is at most `adapter.max_url_chars` long; otherwise `open_url` is `null` and `copy_only` is `true`. The URL never contains the lease, nonce, cell id or any member identifier. The member presses Send in the service; the platform never reads that page [D][V: per service, `G0(c)`, `G2`].
- **Lost nonce.** `issueLeaseNonce` mints a new nonce for an `active` lease and invalidates the previous one (a page reload must not strand a lease). `extendLease` adds `lease.extend_s` once per allowed extension (`lease.max_extensions`); beyond it `409 STATE_CONFLICT`, reason `max_extensions_reached`. An expired lease is `410 LEASE_EXPIRED`.
- **Decline is free** (FD§5.5, `lease.decline_cooldown_s` = 0). `releaseLease` takes `{ reason?: enum<decline_reason> }`, ends the lease (`released`), returns the cell to `queued` without raising `attempt`, and excludes that cell from this member's offers. `declineOffer` does the same for a card the member never leased (it records the decline for the demand-quality signal by category, never as a penalty). `decline_reason`: `not_interested`, `too_long`, `service_problem`, `content_concern`, `other` (convention addition). [D]

### 15.6.3 Reports

```
createReport  req { subject_kind: "cell"/"lease"/"template"/"job"/"result", subject_id: id<cel>/id<lse>/id<tpl>/id<job>/id<sub>,
                    category: enum<report_category>, note: text<500>? }
              201 Report { id: id<rpt>, state: "open"/"triaged"/"actioned"/"dismissed", category, created_at: ts }
```

`report_category` (convention addition): `prohibited_content`, `sensitive_data`, `injection_attempt`, `link_or_action_request`, `wrong_declaration`, `abusive_or_unsafe`, `other`. A volunteer may report any card they hold a lease for; a requester may report a `result` of their own job. The reported party never sees the reporter; reports count toward `template.autopause_report_count` within `template.autopause_window_s` (event `template.paused`, `S8.*`); a report never changes the reporter's tier. Limit: `report.max_per_member_per_day` per UTC day (`RL-REPORT`). [D]

### 15.6.4 Submission (paste-back)

```
Submission { id: id<sub>, lease_id: id<lse>, cell_id: id<cel>, received_at: ts, late: bool,
             verdict: "pending"/"accepted"/"rejected"/"under_review", reasons: [string],      reasons are reject.* codes (0.8.4)
             appealable_until: ts/null,
             credit: { amount_ucr: ucr, lot_id: id<lot>, expires_at: ts }/null }
submitResult  req { nonce: b64u<16>, reported_service_id: id<svc>, reported_model: text<80>?,
                    output_text: string?,                          task run: exactly one of output_text / review_result
                    review_result: { rating: "accept"/"reject"/"unsure", criteria: [ { key: text<40>, score: int } ]?, note: text<500>? }? }
              201 { submission: Submission }
```

`verdict` maps the 0.9.3 submission states: `received` and `checks_passed` -> `pending` (an audit or blanket redundancy may still be running; the raw state is not exposed, so sampling is not revealed), `quarantined` -> `under_review` (output with links, code to run or requests for action, `screen.output_url_action`; withheld from results, FD§5.5; the member sees a neutral "under review", not an accusation), `schema_failed`, `checks_failed`, `rejected` -> `rejected` with `reasons`, `accepted` -> `accepted`. `appealable_until = decided_at + appeal.window_days x 86,400 s` (appeals are filed through the sibling file). The `criteria` keys and score ranges of a review cell are defined by its review template (`S8.*`). [D]

- **Natural idempotency (lease_id, nonce).** The first valid submission wins. The same lease, nonce and body again (even with a new `Idempotency-Key`) returns the stored outcome with `Idempotent-Replayed: true`, emits nothing, and credits nothing twice (0.9.3). The same lease and nonce with a different body is `409 STATE_CONFLICT`, reason `submission_exists`. [D]
- **Lease checks.** The nonce is compared first, in constant time; a wrong nonce is `410 LEASE_EXPIRED`, reason `nonce_invalid`, stores nothing, leaves the lease untouched and is counted by the forgery heuristics (`S9.*`). Lease `active`: accepted. Lease `expired` but within `lease.submit_grace_s` and the cell not yet re-leased: accepted with `late: true`. Otherwise `410 LEASE_EXPIRED` with reason `lease_expired`, `lease_released` or `lease_revoked`. [D]
- **Size.** A body or `output_text` above `cell.envelope.max_submission_bytes` is `413 PAYLOAD_TOO_LARGE`, reason `submission_too_large`, stores nothing and keeps the lease active. Within the byte limit but outside the envelope (`cell.envelope.max_output_chars`) the submission is stored and rejected with `reject.length_out_of_bounds`; the cell requeues (FD§3.4). [D]
- **Attestation, not proof.** `reported_service_id` must be one of the member's `optin.service_ids`; it and `reported_model` are recorded as the volunteer's attestation for the manifest (FD§5.6, failure mode 7). The server never asks for, accepts or stores a chat link, screenshot or page content. [D]
- **Processing order** (`S8.*`, `S9.*` own the algorithms): schema and size check; forbidden-content, link and instruction-pattern scan (quarantine); automatic checks; gold comparison; duplicate and timing heuristics against stored data; audit sampling. Cheap checks run before the response; a pending verdict resolves later and `getSubmission` returns the final verdict. Clients poll with backoff; the server may send `Retry-After` on a pending verdict. [D]
- **Payment at acceptance** (`ISS-09`). On `accepted` the same transaction posts the ledger entry: a `mint` for a Commons cell, a `transfer` for a member-job cell, exactly 1,000,000 ucr (0.6.1), creating a `CreditLot` with `expires_at = earned_at + credit.lifetime_days x 86,400 s` under the parameter version at `earned_at` (0.6.2). Nothing in the response reveals the cell kind, an audit, a comparison or another donor's output. [D]
- **Never executed, always escaped.** Submitted text is stored verbatim and returned only as a JSON string with `X-Content-Type-Options: nosniff`; nothing in this API interprets, renders or executes it. [D]

`getSubmission` returns one `Submission`. `listSubmissions` (history) returns `Page<{ submission: Submission, card: { template_name: text<80>, purpose: enum<purpose>, origin: "commons"/"member" } }>`, filters `verdict`, `from`, `to` (`ts`), newest first.

### 15.6.5 Balance, lots, ledger entries, starter grant

```
Balance  { as_of: ts, balance_ucr: ucr, held_ucr: ucr, member_cap_ucr: ucr, headroom_ucr: ucr,
           expiring_soon: { within_days: int, amount_ucr: ucr }, next_expiry: { at: ts, amount_ucr: ucr }/null,
           earn_today: { earned_ucr: ucr, daily_cap_ucr: ucr } }
Lot      { id: id<lot>, origin: "mint"/"grant"/"transfer"/"refund", amount_ucr: ucr, remaining_ucr: ucr,
           earned_at: ts, expires_at: ts, state: "active"/"spent"/"expired" }
Entry    { id: id<lge>, entry_type: enum<ledger_entry_type>, direction: "in"/"out", amount_ucr: ucr,
           txn_kind: enum<ledger_txn_kind>, created_at: ts, related: { kind: "cell"/"job"/"reservation", id: string }/null }
StarterGrant { state: "locked"/"claimable"/"claimed"/"paused", verified_cells: int, required_verified_cells: int,
               amount_ucr: ucr, lifetime_days: int, claimed_at: ts/null, lot_id: id<lot>/null }
claimStarterGrant  req {}   201 { grant: StarterGrant, lot: Lot }
                   err 422 UNPROCESSABLE (grant_requirement_unmet, reserve_floor); 422 CAP_EXCEEDED (grant_per_device, grant_per_tree_day,
                       grant_daily_limit); 409 ALREADY_EXISTS (starter_grant_claimed)
```

- `balance_ucr` is the sum of unexpired lot remainders; `held_ucr` is credit in the member's own open escrows (informational); `member_cap_ucr = credit.member_cap_credits x trust.cap_multiplier.<tier>` in ucr; `headroom_ucr = max(0, member_cap_ucr - balance_ucr)`; `expiring_soon` covers `credit.expiry_notice_days`; `daily_cap_ucr` is `mint.per_member_daily_cap_credits` in ucr. All are computed from the ledger, never cached beyond `as_of`. [D]
- `listLots` is ordered by `expires_at` ascending (the oldest-first spending order, 0.8.5) and filters on `state`; `listLedgerEntries` is newest first and returns only entries on the member's own account, with the related cell, job or reservation of the member but never a counterparty. The public ledger is a public-surface resource (sibling file). [D]
- **Starter grant** (FD§4.6, `ISS-06`). The grant is claimed, not pushed, so the `grant.starter_lifetime_days` clock starts when the member decides. `claimable` requires `grant.required_verified_cells` verified cells. At claim time the server checks `grant.max_per_device`, `grant.max_per_invite_tree_per_day`, `grant.max_per_day` and that the Reserve stays above `grant.reserve_floor_credits` (otherwise `paused`: grants pause, they are never printed). It posts a `grant` entry from the Reserve for `grant.starter_credits` and is non-transferable (`grant.non_transferable`). [D]

## 15.7 Requester endpoints

The wizard of FD§3.2 steps 5 to 8: template choice, data upload and screening, declarations, policy result, price and window quote, escrow confirmation, progress, cancellation, results with manifest, rating, reservations. A member holds the requester capability without a separate account (0.8.2). [D]

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `listTemplates`, `getTemplate` | `GET /v1/templates`, `GET /v1/templates/{template_id}` | member | - | `RL-READ` | 200 | - |
| `createUpload` | `POST /v1/uploads` | member | R | `RL-UPLOAD` | 201 | - |
| `getUpload` | `GET /v1/uploads/{upload_id}` | member | - | `RL-READ` | 200 | - |
| `deleteUpload` | `DELETE /v1/uploads/{upload_id}` | member | O | `RL-WRITE` | 204 | - |
| `createGlossary` | `POST /v1/glossaries` | member | R | `RL-UPLOAD` | 201 | - |
| `getGlossary` | `GET /v1/glossaries/{glossary_id}` | member | - | `RL-READ` | 200 | - |
| `createJob` (active only) | `POST /v1/jobs` | member | R | `RL-WRITE` | 201 | `job.created` (+ `job.submitted`, `job.policy_passed` / `job.policy_rejected`, `job.waitlisted` when `submit` is `true`) |
| `listJobs`, `getJob` | `GET /v1/jobs`, `GET /v1/jobs/{job_id}` | member | - | `RL-READ` | 200 | - |
| `updateJob` | `PATCH /v1/jobs/{job_id}` | member | O | `RL-WRITE` | 200 | - |
| `declareJobMetadata` | `PUT /v1/jobs/{job_id}/declarations` | member | O | `RL-WRITE` | 200 | - |
| `checkJobPolicy` | `POST /v1/jobs/{job_id}/policy-checks` | member | O | `RL-WRITE` | 200 | - |
| `submitJobForScreening` (active only) | `POST /v1/jobs/{job_id}/screenings` | member | R | `RL-WRITE` | 200 / 202 | `job.submitted`, `job.policy_passed` / `job.policy_rejected`, `job.waitlisted` |
| `getJobQuote` | `GET /v1/jobs/{job_id}/quote` | member | - | `RL-READ` | 200 | - |
| `confirmJob` (active only) | `POST /v1/jobs/{job_id}/confirmations` | member | R | `RL-WRITE` | 201 | `job.escrow_confirmed`, `ledger.entry_committed`, `cell.created`, `+reservation.activated` |
| `getJobProgress` | `GET /v1/jobs/{job_id}/progress` | member | - | `RL-READ` | 200 | - |
| `listJobCells` | `GET /v1/jobs/{job_id}/cells` | member | - | `RL-READ` | 200 | - |
| `cancelJob` | `POST /v1/jobs/{job_id}/cancellation` | member | R | `RL-WRITE` | 200 / 202 | `job.cancel_requested`, `job.cancel_settled` |
| `listJobResults` | `GET /v1/jobs/{job_id}/results` | member | - | `RL-READ` | 200 | - |
| `getJobDeliverable`, `getJobDeliverableContent` | `GET /v1/jobs/{job_id}/deliverable`, `GET /v1/jobs/{job_id}/deliverable/content` | member | - | `RL-READ` | 200 | - |
| `getJobManifest` | `GET /v1/jobs/{job_id}/manifest` | member | - | `RL-READ` | 200 | - |
| `rateJob` | `PUT /v1/jobs/{job_id}/rating` | member | O | `RL-WRITE` | 200 | `+job.rated` |
| `createReservation` (active only) | `POST /v1/reservations` | member | R | `RL-WRITE` | 201 | `reservation.held`, `ledger.entry_committed` |
| `listReservations`, `getReservation` | `GET /v1/reservations`, `GET /v1/reservations/{reservation_id}` | member | - | `RL-READ` | 200 | - |
| `cancelReservation` | `POST /v1/reservations/{reservation_id}/cancellation` | member | R | `RL-WRITE` | 200 | `reservation.cancelled` |

### 15.7.1 Templates, uploads, glossaries

```
TemplateView { id: id<tpl>, version_id: id<tpv>, name: text<80>, job_type: enum<job_type>, approved_on: date,
               input_slots: [ { key: text<40>, type: "upload_ref"/"glossary_ref"/"enum"/"text"/"int", required: bool,
                                label_key: copy_key, values: [string]?, max_entries: int? } ],
               output_format: "txt"/"csv"/"jsonl"/"json"/"md", expected_time_s: dur_s,
               envelope: { max_input_chars: int, max_output_chars: int },
               allowed: { purposes: [enum<purpose>], licenses: [enum<license>], sensitivities: [enum<sensitivity>],
                          service_requirements: [enum<service_requirement>] } }
Upload       { id: id<upl>, state: "received"/"attached"/"purged", format: "txt"/"csv"/"jsonl"/"json", size_bytes: int,
               content_hash: hash, unit_estimate: int/null, job_id: id<job>/null, created_at: ts, expires_at: ts,
               screening: { result: "passed"/"flagged", findings: [ { code: string, count: int, lines: [int] } ] } }
Glossary     { id: id<gls>, name: text<80>, source_lang: text<35>, target_lang: text<35>, entry_count: int, created_at: ts }
createUpload   req { format, filename: text<120>?, content: string, content_hash: hash? }       content is UTF-8 text inside JSON
createGlossary req { name: text<80>, source_lang: text<35>, target_lang: text<35>, entries: [ { source: text<200>, target: text<200> } ] }
```

- `listTemplates` returns only `TemplateVersion`s in `review_status` `approved` (0.9.5) whose template is not paused or killed (`kill.template.<tpl_id>`); `allowed` is read from the active `PolicyVersion` allowlist so the wizard never offers a combination the engine will reject. Prompt bodies are not part of this view. Effectiveness of any template is [H] (`S8.*`). [D]
- **Upload size.** The limit applies to the decoded `content` bytes: `job.max_upload_bytes`, else `413 PAYLOAD_TOO_LARGE`, reason `upload_too_large`. The HTTP layer accepts a body of at most `6 x job.max_upload_bytes + api.max_body_bytes` on this route only (JSON escapes one control character as up to 6 bytes). `content_hash`, when sent, must equal the SHA-256 of the decoded bytes. Binary files are not accepted (cells are text). [D]
- **Automatic screening at upload** (non-binding early feedback; the binding screen runs at `submitJobForScreening`). Finding codes, extendable by `S9.*`: `screen.pii_pattern`, `screen.credential_pattern`, `screen.url_present`, `screen.instruction_pattern`. Each finding is handled by its action parameter: `screen.pii_action` (`reject`), `screen.url_action` (`flag_for_review`; any URL counts because `screen.max_urls_per_input` is 0), `screen.output_url_action` is for results (`S15.6.4`). `reject` returns `422 POLICY_REJECTED`, `details.reasons` such as `policy.R2.sensitivity_not_accepted` or `policy.R3.prohibited_content`, `details.findings`, and the content is **not stored** (data minimization); `flag_for_review` stores the upload with `screening.result` = `flagged`. Findings give counts and line numbers, never the matched text. [D]
- **Human screening.** A `flagged` upload, and a share `screen.review_rate_new_requester` (1.0) or `screen.review_rate_established_requester` (0.20) of all inputs, wait for a reviewer after `submitJobForScreening` (job state `screening`, response `202`). [D]
- `deleteUpload` is allowed while the upload is not attached to a job past `draft`; otherwise `409 STATE_CONFLICT`, reason `upload_attached`. Unattached uploads expire after `retention.job_payload_days`. Glossary text goes through the same screening; `glossary_invalid` (`422 UNPROCESSABLE`) covers more entries than the slot's `max_entries`, empty entries, or a language mismatch with the job inputs.

### 15.7.2 Job wizard: create, declare, check, screen, quote, confirm

```
Declarations { purpose: enum<purpose>, license: enum<license>, sensitivity: enum<sensitivity>,
               service_requirement: enum<service_requirement>, pinned_service_ids: [id<svc>]?,          required exactly when M1
               topic_category_ids: [id<top>]?, acknowledgements: [enum<ack>],
               window_preference_s: dur_s? }                                    admission.min_window_s .. admission.max_window_days x 86,400
Job          { id: id<job>, state: enum<job states of 0.9.2>, template: { id: id<tpl>, version_id: id<tpv>, name: text<80> },
               title: text<80>/null, inputs: object, upload_ids: [id<upl>], glossary_id: id<gls>/null,
               declarations: Declarations/null, deadline_class: "standard", cell_count: int/null,
               policy_version_id: id<plv>/null, rejection: { reasons: [string] }/null, quote: Quote/null,
               escrow: { id: id<esc>, held_ucr: ucr }/null, window: { window_s: dur_s, completes_by: ts/null }/null,
               waitlist: { position: int, expires_at: ts }/null, suspension_reason_key: copy_key/null,
               closure_reason: "policy_stopped"/"service_revoked"/"template_retired"/"operator_killed"/"overrun_timeout"/"requester_cancelled"/null,
               created_at: ts, updated_at: ts }                                  ETag = row_version
Quote        { policy_version_id: id<plv>, parameter_versions: { "<parameter name>": int },
               primary_cells: int, v_ppm: ppm, lambda_ppm: ppm, p_ucr: ucr, eta_ppm: ppm,
               primary_pay_ucr: ucr, verification_pool_ucr: ucr, levy_ucr: ucr, escrow_ucr: ucr, verification_pool_cells: int,
               admission: { decision: "admit"/"waitlist", capacity_cells: int, committed_cells: int, phi_ppm: ppm },
               window_s: dur_s, expires_at: ts, quote_hash: hash }
```

`ack` (convention addition): `stranger_reads_input` (required for `S1`), `downstream_use_uncontrolled` (required for `P1`; FD§5.7 failure mode 3). The wizard is the only place a requester states purpose, license and sensitivity, and these are *declared*, never verified (FD§5.7 failure mode 1). `inputs` holds one value per `input_slots.key`, validated against the template version (`400 VALIDATION_FAILED` with `details.fields`).

`Quote` arithmetic is exactly 0.6.1 with N = `primary_cells`: `p_ucr = 1,000,000 + v_ppm + lambda_ppm`; `escrow_ucr = N x p_ucr`; `primary_pay_ucr = N x 1,000,000`; `verification_pool_ucr = N x v_ppm`; `levy_ucr = N x lambda_ppm`; `verification_pool_cells = floor(verification_pool_ucr / 1,000,000)`; `eta_ppm = floor(10^12 / p_ucr)`. `v_ppm` and `lambda_ppm` are the values in force for the job type (`price.v_prior` until `price.v_min_sample_cells`, then the measured value, `S6.*`); `parameter_versions` records the version of every parameter used so the quote is reproducible. `S6.*` owns the admission algorithm; this part only fixes what it returns. [D]

```
createJob   req { template_id: id<tpl>, title: text<80>?, inputs: object?, upload_ids: [id<upl>]?, glossary_id: id<gls>?,
                  declarations: Declarations?, copy_from_job_id: id<job>?, submit: bool? }       submit default false
            201 Job (state draft)        with submit = true: 200-equivalent outcome of submitJobForScreening below, status 201
checkJobPolicy         req {}     200 { result: "allowed"/"rejected", reasons: [string], policy_version_id: id<plv> }   dry run: no state change, no stamp
submitJobForScreening  req {}     200 Job (state quoted or waitlisted)  /  202 Job (state screening: human screening pending)
                                  err 422 POLICY_REJECTED (details.job_id, details.reasons)  -> job state rejected (terminal)
                                      422 CAP_EXCEEDED (waitlist_limit)    -> the job stays draft, nothing stamped
confirmJob  req { quote_hash: hash, reservation_id: id<rsn>? }
            201 { job: Job (state admitted), escrow: { id: id<esc>, held_ucr: ucr }, balance_after_ucr: ucr }
```

- `copy_from_job_id` copies template, inputs, uploads (if not purged), glossary and declarations of one of the member's own jobs into a new draft (for example after `quote_expired`). `updateJob` and `declareJobMetadata` change a job only in state `draft`; otherwise `409 STATE_CONFLICT`, reason `job_state_invalid`.
- **Policy result.** `checkJobPolicy` evaluates `R1`..`R10` in order against the current active `PolicyVersion` and reports every failing rule, not only the first (the engine rejects at the first failure; the dry run lists all so the requester fixes them together). `submitJobForScreening` evaluates for real: `R1` (declarations complete and consistent), `R2`, `R3`, `R4` (the template is a reviewed template), `R5`..`R7` (service flags), stamps `policy_version_id` (`R9`), plans `cell_count` with the template's splitter, then prices and runs admission. Reasons are `policy.<policy_rule_id>.<slug>` (0.8.4) and each carries `details.copy_key` for the `fa` and `en` text (`S11.*`). A rejection is deterministic and is stored with the idempotency key. [D]
- **Admission outcomes.** `admit`: job `quoted`, quote valid until `expires_at = created + price.quote_ttl_s`. `waitlist`: no window up to `admission.max_window_days` fits the capacity rule (committed cells over the window at most `admission.phi` x forecast active capacity), the job becomes `waitlisted` with `waitlist.expires_at` after `admission.waitlist_ttl_days`; at most `admission.waitlist_max_per_member` waitlisted jobs per member (`CAP_EXCEEDED`, `waitlist_limit`, job stays `draft`). The window in the quote is never shorter than `window_preference_s` and never an instant-completion promise (FD Principle 10). [D]
- **Confirm** runs in one transaction. Guards in order: job `quoted` (else `409 job_state_invalid`); `now < quote.expires_at` (else `409 quote_expired`, and the job moves to `quote_expired`); `quote_hash` equals the hash of the current quote (else `409 quote_changed`: a parameter or policy version moved); recovery cooldown (`403`); `admission.max_concurrent_jobs_per_member` (`CAP_EXCEEDED`, `concurrent_jobs`); `cell_count <= admission.max_job_cells` (`CAP_EXCEEDED`, `job_too_large`); capacity re-checked (`422 NO_CAPACITY`, reason `capacity_changed`, the job stays `quoted` and `getJobQuote` returns the re-computed quote); balance at least `escrow_ucr` (`422 INSUFFICIENT_CREDIT`, `details.required_ucr`, `available_ucr`, `short_by_ucr`); `launch.member_jobs_enabled` and `kill.all_new_jobs` are checked at pipeline step 7. Effects: `escrow_hold` oldest-first over the member's lots (0.8.5), `Escrow` opened, one `cel_` per primary cell created `queued`, job `admitted`, parameter and policy versions pinned. With `reservation_id` the escrow comes from the reservation (`escrow_release`) and any price difference is topped up or refunded at confirm. Nothing is posted if any guard fails. [D]
- A job whose quote is not confirmed in time is moved by a timer to `quote_expired` (terminal); the requester creates a copy. A `waitlisted` job is re-quoted by the system (`job.waitlist_released`) and returns to `quoted` with a new `expires_at`; if its waitlist time ends it is `cancelled` (`job.waitlist_expired`).

### 15.7.3 Progress, cancellation, results, manifest, rating

```
JobProgress { job_id: id<job>, state: enum<job states>, as_of: ts,
              cells: { total: int, queued: int, in_progress: int, accepted: int, exhausted: int, cancelled: int, voided: int, suspended: int },
              verification: { pool_cells: int, accepted: int },
              window: { window_s: dur_s, completes_by: ts/null, projected_completes_by: ts/null, overrun_limit_at: ts/null },
              escrow: { held_ucr: ucr, paid_out_ucr: ucr } }
JobCell     { ordinal: int, cell_id: id<cel>, state: "queued"/"in_progress"/"accepted"/"exhausted"/"cancelled"/"voided"/"suspended", attempts: int }
ResultItem  { ordinal: int, cell_id: id<cel>, output_text: string, output_hash: hash, accepted_at: ts,
              verification: { method: enum<verification_method>, outcome: "agreed"/"checked"/"resolved" } }
Deliverable { id: id<dlv>, job_id: id<job>, state: "assembling"/"ready"/"partial"/"purged", format: "txt"/"csv"/"jsonl"/"json"/"md",
              size_bytes: int, content_hash: hash, item_count: int, missing_ordinals: [int], manifest_id: id<mfs>/null,
              created_at: ts, available_until: ts }
Manifest    { id: id<mfs>, job_id: id<job>, deliverable_id: id<dlv>, manifest_version: int, generated_at: ts,
              job: { template: { id: id<tpl>, version_id: id<tpv> }, declarations: Declarations,
                     policy: { profile_id: id<pol>, version_id: id<plv> }, no_training: bool,
                     downstream_use: "uncontrolled"/"requester_only", content_hash: hash },
              cells: [ { ordinal: int, cell_id: id<cel>, input_hash: hash, output_hash: hash,
                         service: { id: id<svc>/null, model_reported: text<80>/null, attested: true },
                         verification: { method: enum<verification_method>, outcome: string }, accepted_at: ts } ],
              manifest_hash: hash }
```

- **Per-cell status map.** `JobCell.state` collapses the 0.9.3 cell states for the requester: `queued` = `queued`; `in_progress` = `leased`, `submitted`, `flagged_for_audit`, `rejected`, `expired`, `overturned`; the others map one to one. Only primary cells are listed (verification cells are visible only as `verification` counts), and no volunteer identity, handle or lease id is ever shown. `listJobCells` is ordered by `ordinal`. [D]
- **Cancel.** `cancelJob` body `{ reason: text<200>? }`. State `draft`, `quoted` or `waitlisted`: `200`, job `cancelled` at once, nothing held. State `admitted`, `running` or `suspended`: `202`, job `cancelling` (unstarted cells voided and refunded, in-flight cells finish under the pinned policy, `job.cancel_settled`), response `{ job, refund_ucr: ucr/null }` with `refund_ucr` known after settlement and visible in `getJob`. Any other state: `409 STATE_CONFLICT`, reason `not_cancellable`. What part of the levy and the pool remains payable on a partial run is `S6.*`. [D]
- **Results.** `listJobResults` (ordered by `ordinal`, `Page<ResultItem>`) and the deliverable are available in `completed` and `failed` (partial) jobs; before that `409 STATE_CONFLICT`, reason `job_state_invalid`. Quarantined and unaccepted cells are never included; a `partial` deliverable lists `missing_ordinals`. `getJobDeliverableContent` returns `{ media_type: string, encoding: "utf-8", content: string, content_hash: hash }` as `application/json` (never a raw file type, so nothing is rendered by a browser; the client saves it). `available_until` is the terminal time plus `retention.job_payload_days`; afterward `state` is `purged` and the content is gone while the hashes in the manifest remain. [D]
- **Manifest** (FD§5.6). Contains the declared purpose, license and sensitivity, the policy profile and version, per-cell input and output hashes, the service and model *as reported by the volunteer* (attested, not proven), the verification method and result, and timestamps. It contains no volunteer handle (0.6.4: requesters never see it) and no member id. `no_training` is a contractual flag (`false` when the requester declared `P1`, `true` otherwise), not a technical control. `manifest_hash` is the SHA-256 of the RFC 8785 canonical JSON of the manifest without that field. [D][A]
- **Rating.** `rateJob` body `{ score: int 1..5, comment: text<500>? }`, allowed in `completed` and `failed`, replaces an earlier rating; response `{ rating: { score, comment, updated_at } }`. A rating feeds template and job-type quality measures only and is never attached to a volunteer, so it cannot be used for retaliation. [D]

### 15.7.4 Reservations (`ff.job.reservations`)

```
Reservation { id: id<rsn>, state: "held"/"activated"/"cancelled"/"expired", target_date: date, template_id: id<tpl>,
              cells: int, price_per_cell_ucr: ucr, escrow_ucr: ucr, free_cancel_until: ts, created_at: ts }
createReservation  req { target_date: date, template_id: id<tpl>, cells: int, dry_run: bool? }
                   201 Reservation   (dry_run true: 200 with the would-be Reservation, nothing held)
cancelReservation  req {}   200 { reservation: Reservation, refund_ucr: ucr, penalty_ucr: ucr }
```

Creation holds `cells x p_ucr` in escrow at booking (FD§4.5 "price is locked"). Limits: `target_date` at most `reservation.max_horizon_days` ahead (`CAP_EXCEEDED`, `reservation_horizon`); at most `reservation.max_active_per_member` held reservations (`reservation_limit`); one date's share of capacity at most `reservation.capacity_share_cap` (`reservation_capacity_share`); a full date is `422 NO_CAPACITY`, reason `date_full`. `free_cancel_until = start of target_date (UTC) - reservation.free_cancel_notice_s`. When the flag is off every reservation endpoint returns `403 FORBIDDEN`, reason `feature_disabled`, `details.flag` = `ff.job.reservations`. A reservation becomes `activated` when `confirmJob` names it, and `expired` (escrow refunded) if its date passes unused. The penalty for cancelling after `free_cancel_until` is not defined in S0 or FD: this API returns `penalty_ucr` as computed by `S6.*` and treats it as `0` until `S6.*` defines it [A][P: `S6.*` decides whether late cancellation costs anything]. [D]

## 15.8 Teams, badges, share card, referral, feature flags

Growth mechanics are experiments behind flags (FD§6; `ff.growth.v1_onboarding_story` .. `ff.growth.v5_referral`); the server decides which mechanics a member sees and logs the assignment (`Experiment`), and never uses a growth mechanic to give anyone a weaker privacy or safety guarantee. All of these count verified cells only, never raw volume. [D][H: each mechanic is a hypothesis with a pre-stated kill threshold, `S13.*`]

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `getFeatures` | `GET /v1/members/me/features` | member | - | `RL-READ` | 200 | - |
| `createTeam` (active only) | `POST /v1/teams` | member | R | `RL-WRITE` | 201 | `+team.created` |
| `listTeams` | `GET /v1/teams` | member | - | `RL-READ` | 200 | - |
| `getTeam` | `GET /v1/teams/{team_id}` | member | - | `RL-READ` | 200 | - |
| `updateTeam` | `PATCH /v1/teams/{team_id}` | member | O | `RL-WRITE` | 200 | - |
| `createTeamJoinCode` | `POST /v1/teams/{team_id}/join-codes` | member | R | `RL-WRITE` | 201 | - |
| `joinTeam` | `POST /v1/teams/{team_id}/memberships` | member | R | `RL-WRITE` | 201 | `+team.joined` |
| `leaveTeam` | `DELETE /v1/teams/{team_id}/memberships/me` | member | O | `RL-WRITE` | 204 | `+team.left` |
| `listTeamMembers` | `GET /v1/teams/{team_id}/members` | member | - | `RL-READ` | 200 | - |
| `listBadges`, `listMyBadges` | `GET /v1/badges`, `GET /v1/members/me/badges` | member | - | `RL-READ` | 200 | - |
| `getShareCard` | `GET /v1/members/me/share-card` | member | - | `RL-READ` | 200 | - |
| `createReferral` (active only) | `POST /v1/referrals` | member | R | `RL-WRITE` | 201 | `+referral.issued` |
| `listReferrals` | `GET /v1/referrals` | member | - | `RL-READ` | 200 | - |
| `revokeReferral` | `DELETE /v1/referrals/{referral_id}` | member | R | `RL-WRITE` | 204 | `+referral.voided` |

```
Features   { flags: { "<ff name>": bool } }                                       only flags that affect the member's screens; no arm names
Team       { id: id<tem>, name: text<40>, listed: bool, member_count: int, verified_cells_30d: int,
             my_membership: { role: "owner"/"member", alias: text<24>, visible: bool }/null, created_at: ts }
createTeam req { name: text<40>, listed: bool?, alias: text<24>? }   201 { team: Team, join_code: text<32> }       the code appears once
joinTeam   req { join_code: text<32>, alias: text<24>?, visible: bool? }   201 { team: Team }
TeamMember { alias: text<24>, verified_cells_30d: int }                         only members with visible = true; plus page.hidden_count
Badge      { id: id<bdg>, name_key: copy_key, criterion_key: copy_key, awarded_at: ts/null }
ShareCard  { generated_at: ts, contains_personal_data: false, verified_cells_total: int, badge_ids: [id<bdg>], referral_code_available: bool }
Referral   { id: id<ref>, state: "issued"/"redeemed"/"activated"/"paid"/"expired"/"voided", created_at: ts, expires_at: ts, bonus_ucr: ucr, paid_at: ts/null, pending_reason: "hold"/"reserve_floor"/null }
createReferral 201 { referral: Referral, code: text<32> }                          the code appears once
```

- **Teams** need `ff.growth.v4_teams` and trust tier at least `team.create_min_tier`; at most `team.max_members` members (`CAP_EXCEEDED`, `team_full`); joining needs the join code and an unexpired `active` member. Aliases are chosen per team, not unique, and are not linked to any other identifier. A member who sets `visible: false` is counted but never listed. `listed: true` allows the team name and its total to appear on public surfaces only while `member_count >= team.min_public_members` (`S12.*`). A team never shows per-member contribution except for `visible` members. [D]
- **Share card** (`ff.growth.v3_share_card`). `getShareCard` is computed on request and returns only a verified-cell total and badges; it contains no member id, no handle, no location, no date of joining and no time series (`contains_personal_data` is always `false`). The client renders the image locally; the server stores no image and no share link, so there is nothing to track or revoke. [D]
- **Referral** (`ff.growth.v5_referral`). A referral is an invite with a bonus attached: `createReferral` also creates the `Invite` (same guards as `createInvite`) and counts toward `growth.referral.max_per_referrer_per_30d` (`CAP_EXCEEDED`, `referral_limit`). Redemption is the `invite_code` of `createMember`; the referral becomes `activated` when the newcomer has `growth.referral.min_newcomer_verified_cells` verified cells, and `paid` after `growth.referral.hold_s`, when both parties receive `growth.referral.bonus_credits` as a `grant` entry from the Reserve; if the Reserve is at `grant.reserve_floor_credits` the state stays `activated` with `pending_reason` `reserve_floor`. The referrer sees counts and states only, never who the newcomer is. Anti-farming limits (`ratelimit.invite_tree_new_members_per_day`, the invite tree caps, `grant.max_per_device`) apply unchanged. [D]
- **Feature flags.** `getFeatures` lets the client render only what the server enabled; a client must not call an endpoint whose flag is off. A call to a disabled mechanic is `403 FORBIDDEN`, reason `feature_disabled`, `details.flag`. [D]
