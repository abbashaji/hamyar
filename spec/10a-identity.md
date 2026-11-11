# 10. Identity, access, sessions and privacy

*Spec part 10, file 10a · prompt scope A (identity and access) and the privacy and member-safety half of scope I · vocabulary is `spec/00-conventions.md` (`S0.*`) · source of truth is the Founding Document draft v0.1 (`FD`). Nothing here is legal advice. No provider, host, browser, authenticator or law has been checked; each dependence on such a fact is tagged [V].*

## 10.1 Scope, stance and reading guide

- **Covered here** [D]: anonymous local identity, recovery key, optional e-mail, key rotation, device linking, account recovery, device identification and rate limits, vouched invitations and invite trees, roles and the permission matrix, admin authentication, sessions, the logging and retention table with exact IP handling, what observers, hosts and operators can see, seizure and subpoena behavior, and what the platform cannot promise. Reason: prompt scope A and the privacy half of scope I.
- **Covered elsewhere in `S10.*`** [A]: the threat-model table (`THR-nn`), the secrets inventory and rotation procedure, hosting and reachability, and the report, takedown, ban and appeal process. This file states only the hooks it needs from them (10.18).
- **Numbering** [A]: this file owns `S10.1`..`S10.19`; any other S10 file starts at `S10.20` (`ISS-101`).
- **Reading rules** [D]: parameters are named exactly as in `S0.10`; the few this file adds are in 10.18 and reported as convention gaps. Field lists are the identity-relevant columns only; `S5.*` owns full schemas and wins on column names, this file wins on meaning (`ISS-101`). Reason: S0.1.

**Design commitments**, binding on every later part and tested in 10.17: [D]

| # | Commitment | Reason |
| --- | --- | --- |
| IC1 | No password exists for any principal, member or admin | Nothing to phish, reuse or leak; prompt scope A |
| IC2 | The server stores public keys and verifiers only; it never holds a secret that lets it sign as a member | A database copy cannot be replayed as a login |
| IC3 | No provider credential, provider session or chat page is collected, stored or linked to an identity; the service and model on a cell are volunteer-attested, not proven | Ground rule 3; FD Principle 3; FD§5.6 |
| IC4 | Every stored identity item has a row in the 10.14 table; anything not in that table is not collected | FD Principle 8 |
| IC5 | Deny by default: a permission, parameter or switch that is absent or unknown evaluates to denied | FD§5.3 (unknown is treated as no) |
| IC6 | Fraud is resisted with economics (credit only from verified work, caps, invitations, rate limits), not with identity | FD§0.1 item 6 |
| IC7 | Member safety outranks growth: when an anti-farming measure would endanger members it is dropped or weakened and the residual abuse is accepted and monitored | FD Principle 8 |
| IC8 | The platform promises minimization and says `declared`; it never promises anonymity and never says `guaranteed` | FD Principles 8 and 11 |

## 10.2 Identity model and what the server stores

A `Member` is a pseudonym: one row plus public keys. One person may hold several members; Hamyar neither forbids nor links them, except through the device token (10.9). A `member` principal holds both the `donor` and `requester` capabilities (S0.8.2). An `AdminUser` is a different principal type with no foreign key to `Member` (10.12). [D] Reason: separation limits what a compromised admin account reveals about member activity.

| Entity (prefix) | Identity-relevant fields | Retention class (S0.7) | Note |
| --- | --- | --- | --- |
| `Member` (`mem_`) | `status`, `trust_tier`, `tier_before_restriction`, `created_at`, `last_active_on` (UTC date only), `registration_device_id`, `invite_tree_id`, `invited_by_member_id` (nullable), `invite_depth`, `recovery_confirmed_at`, `recovery_cooldown_until`, `email_ciphertext`, `email_index`, `email_verified_at`, `email_purposes`, `locale`, `digits`, `calendar`, `row_version` | `member_bound` | No name, phone or clear e-mail; activity is a date, not a time |
| `MemberKey` (`mky_`) | `member_id`, `device_id` (null for recovery), `kind` (`device`, `recovery`), `alg` (`ed25519`), `public_key` (32 bytes), `state` (`active`, `retiring`, `revoked`), `not_after`, `revoked_reason`, `authorized_by_key_id`, `authorization_signature`, `key_storage` (`hardware_backed`, `software`, `unknown`; self-reported), `created_at` | `member_bound` | Each key addition carries the signature that authorized it (10.7) |
| `Device` (`dev_`) | `token_hash`, `platform_class` (`ios`, `android`, `desktop`, `other`), `first_seen_on` (date), `registrations_count`, `grants_issued`, `state` (`active`, `blocked`) | `member_bound` plus grant-memory residue (10.9) | Random token, never derived from hardware |
| `Session` (`ses_`) | `principal_type`, `member_id` or `admin_user_id`, `key_id`, `token_hash`, `created_at`, `last_used_at`, `idle_expires_at`, `abs_expires_at`, `step_up_at`, `state` | `short` | Hash of the token only (10.13) |
| `AuthChallenge` (`chl_`) [A] | `purpose`, `nonce`, `audience`, `expires_at`, `used_at` | `short` | Deleted on use or expiry |
| `DeviceLinkOffer` (`dlo_`) [A] | `member_id`, `secret_hash`, `state`, `attempts`, `claimed_key_hash`, `expires_at` | `short` | 10.7 |
| `RecoveryRequest` (`rcv_`) [A] | `recovery_key_id`, `outcome`, `created_at`, `completed_at` | `member_bound`, rows older than 90 days deleted (the window in `identity.recovery_max_per_90d`) | No IP, no device data |
| `SecurityNotice` (`snt_`) [A] | `member_id`, `kind`, `created_at`, `seen_at` | `member_bound`, deleted `retention.session_days` after `created_at` | Shown on every device at next sign-in |
| `Invite` (`inv_`) | `kind` (`seed`, `member`), `code_hash`, `inviter_member_id`, `invitee_member_id`, `invite_tree_id`, `state`, `expires_at`, `redeemed_at` | `member_bound` plus edge-clearing rule (10.10) | Code stored as SHA-256 only |
| `AdminUser` (`adm_`) | `label` (pseudonym), `roles` (subset of `reviewer`, `operator`), `state` (`active`, `locked`, `disabled`), `declared_member_ids` (optional, 10.11) | `permanent` | No e-mail, no password |
| `AdminCredential` (`acr_`) | `admin_user_id`, `credential_id`, `public_key`, `sign_count`, `transports`, `label`, `state` (`pending`, `active`, `locked`, `revoked`), `last_used_on` | `permanent` | WebAuthn, 10.12 |
| `AdminAction` (`act_`) | `admin_user_id`, `action`, `target_ref`, `params_hash`, `proposed_by`, `approved_by`, `outcome`, `request_id`, `created_at` | `permanent` | Hash-chained like the ledger [A] |

**Never stored, by design** [D]: names, phone numbers, passwords, clear-text e-mail, raw IP addresses, hardware or advertising identifiers, browser fingerprints, precise or coarse location, provider credentials or sessions, volunteers' chat pages, private keys and the recovery key. Reason: IC3, IC4.

## 10.3 Anonymous local identity: key generation, registration, proof of possession

### 10.3.1 Key material [D]

| Key | Algorithm | Generated | Kept on the device | Kept on the server |
| --- | --- | --- | --- | --- |
| Device key | Ed25519 (S0.6.4) | In the browser at first use | WebCrypto `CryptoKey` with `extractable = false` in IndexedDB where the browser supports Ed25519 [V: support on the target phones]; otherwise a bundled audited Ed25519 implementation with the seed in IndexedDB and `key_storage` = `software` [V] | `MemberKey.public_key` |
| Recovery key | Ed25519 keypair derived from the recovery secret (10.4) | Same moment | Never stored; shown once | `MemberKey.public_key`, `kind` = `recovery` |
| Device token | 128-bit CSPRNG value | First visit | IndexedDB; random, not derived from hardware | `Device.token_hash` = SHA-256 of the token |
| Session token | 256-bit CSPRNG value | Server | IndexedDB, never a cookie (S0.11.4) | SHA-256 only |

Browser storage can be evicted (storage pressure, per-site caps) [V]. The client asks for persistent storage where available. Losing the device key loses that device's identity; the member recovers with the recovery key (10.8). WebCrypto keys are not generally hardware-backed [V], so `key_storage` is informational and never trusted for a decision.

### 10.3.2 Signed message format and challenges [D]

```
sig_input = utf8('hamyar/v1/') || purpose || 0x00 || audience || 0x00
         || challenge_id || 0x00 || nonce || 0x00 || context_hash
context_hash = SHA-256( RFC8785_canonical_json(request_body) )     # S0.6.4
```

`purpose` is one of `register_device`, `register_recovery`, `session`, `step_up`, `rotate_device_key`, `rotate_recovery_key`, `link_claim`, `link_approve`, `recover`, `confirm_recovery`, `revoke_key`, `set_email`, `close_account`. `audience` is the member origin string. One signature therefore authorizes exactly one purpose, one origin and one request body, and cannot be replayed on another site or for another action. Reason: removes cross-protocol and cross-site replay.

`POST /v1/auth-challenges` (auth `none`, rate limited by IP hash) returns `{challenge_id, nonce, expires_at}`. The nonce is 128 random bits, valid `identity.challenge_ttl_s` seconds, single use (marked used in the same transaction as the action it authorizes). Challenges are issued to anyone for any purpose and never reveal whether a key or member exists. [D]

### 10.3.3 Registration (pseudocode) [D]

```
client:
  token = loadOrCreate(device_token)                 # 128-bit CSPRNG, IndexedDB
  dk    = generateKey(Ed25519, extractable=false if supported)
  rs    = csprng(identity.recovery_key_bits / 8)     # recovery secret, never sent
  rk    = Ed25519_from_seed( HKDF-SHA-256(rs, 'hamyar/v1/recovery', 'ed25519-seed', 32) )
  ch    = POST /v1/auth-challenges {purpose: 'register_device'}
  body  = {invite_code?, device_pub, recovery_pub, device_token: token,
           platform_class, key_storage, locale}
  POST /v1/members  body + {challenge_id,
         device_signature:   sign(dk, sig_input('register_device',   ch, ctx(body))),
         recovery_signature: sign(rk, sig_input('register_recovery', ch, ctx(body)))}
  -> show recovery key screen (10.4) before leaving onboarding
```

Server checks, in this order; the first failure stops the request: [D]

| # | Check | Failure |
| --- | --- | --- |
| 1 | `launch.members_may_join` is true | `403 LAUNCH_GATE_CLOSED` |
| 2 | Rate limits of 10.9 (device token, IP hash, invite tree) | `429 RATE_LIMITED` |
| 3 | Both public keys are valid 32-byte Ed25519 points and differ from each other | `400 VALIDATION_FAILED` |
| 4 | Challenge exists, unused, unexpired, `purpose` = `register_device`, audience matches | `401 AUTH_EXPIRED` or `AUTH_INVALID` |
| 5 | Both signatures verify over the same `context_hash` (proof of possession of both private keys: a typo or bug cannot register a recovery key nobody holds) | `401 AUTH_INVALID` |
| 6 | If `identity.registration_mode` = `invite_only`: code hash matches an `Invite` in state `active`, unexpired, its tree not frozen, tree size below `invite.tree_max_members`, depth at most `invite.tree_max_depth` | `422 UNPROCESSABLE` with one uniform `copy.invite.invalid` for unknown, expired or used codes; `422 CAP_EXCEEDED` for a full tree |
| 7 | One transaction: insert `Member` (`status` `active`, `trust_tier` `new`), two `MemberKey` rows (`authorized_by_key_id` = the key itself), upsert `Device`, redeem the `Invite`, mark the challenge used, emit `member.created` | `409 STATE_CONFLICT` on a lost race |
| 8 | Issue a session (10.13) and return `{member_id, key_id, session}` | |

`Idempotency-Key` is REQUIRED on registration [A]: a lost response would otherwise leave an identity whose recovery key the person never saw. In `open` mode (no invite) the new member is the root of a new tree whose `invite_tree_id` is a fresh opaque `inv_` ULID with no `Invite` row. The member's ledger account is created by `S6.*` on `member.created`. [D]
