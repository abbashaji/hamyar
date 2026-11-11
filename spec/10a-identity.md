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

## 10.4 Recovery key

### 10.4.1 Format, entropy source, derivation [D]

| Item | Decision | Reason |
| --- | --- | --- |
| Payload | `identity.recovery_key_bits` bits (default 128, validation at least 128, multiple of 8) from the OS CSPRNG (`crypto.getRandomValues`); if that API is absent the client refuses to create an identity, it never falls back to `Math.random` or time | A guessable key defeats the design |
| Checksum | C bits, the first C bits of SHA-256(`hamyar/v1/recovery-checksum` followed by the payload), where C is the smallest value at least 22 that makes (payload bits + C) divisible by 5 | Detects typos locally before any request; for 128 bits C = 22, so an undetected random typo has probability 2^-22, about 2.4 in 10 million |
| Encoding | Crockford base32 (digits and letters without I, L, O, U), groups of 5 characters joined by hyphens, upper case; 128 + 22 = 150 bits = 30 characters = 6 groups | Easy to copy by hand; case-insensitive |
| Example (format only, not a key) | `7M4QX-9PT2D-HZ8E6-K3VBA-0WYN5-R1CGF` | |
| Input normalization | Upper-case; strip spaces and hyphens; map I and L to 1 and O to 0; map Persian and Arabic-Indic digits to Latin digits; reject any other character; verify the checksum on the device | Persian keyboards and digit habits; typos never cost a request |
| Derivation | `seed = HKDF-SHA-256(ikm = payload, salt = 'hamyar/v1/recovery', info = 'ed25519-seed', L = 32)`; the recovery keypair is the Ed25519 keypair of `seed` | High-entropy input needs no slow hash (S0.6.4) |
| Guessing odds | 2^-128 per guess. Exhaustive search at an assumed 10^12 guesses per second (an illustrative upper bound for one very large attacker, not a measurement) takes 2^128 / 10^12 = 3.4 x 10^26 s, about 1.1 x 10^19 years [A] | Why no lockout, KDF or CAPTCHA is needed on the key itself |

Word lists were rejected for Phase 1: a vetted Persian list of 2048 words does not exist in this project and an unvetted one risks ambiguous or offensive words [V]. A QR rendering of the same string is offered for moving the key to another device by camera.

### 10.4.2 Display and offline backup [D]

1. One full-screen step at the end of registration (FD§3.2 step 1), shown in Latin script inside a `dir=ltr`, `unicode-bidi: isolate` block so Persian text around it cannot reorder the characters.
2. Options offered: write it on paper (a print stylesheet renders a card locally); copy to the clipboard (warning: clipboard managers and cloud clipboards); save as a text file (warning: cloud backup of downloads); show a QR code (rendered locally). Not offered: e-mail it, send it to the server, store it in the browser.
3. The key is never sent to the server, never put in a URL, never written to analytics, logs or error reports, and the page that shows it makes no network request while it is open (tested, AC-identity-04).
4. The step is one screen, not a quiz, so the sub-60-second first contribution (FD§6.2 V1) is not blocked; time spent on it is an instrumented measure [H: the step does not lower V1 conversion; test: median step time and landing-to-first-verified-cell conversion in Phase 1; kill criterion: the pre-registered V1 bar is missed because of this step].
5. Optional confirmation: the member retypes the key; the client derives the keypair and signs a `confirm_recovery` challenge; the server sets `recovery_confirmed_at`. Settings nudge until confirmed and never block.

Reason for not forcing a backup: credit is small, capped by K and expires, so the cost of losing an identity is bounded; forced friction costs conversion and teaches people to photograph the key into cloud albums. [D]

### 10.4.3 Verification without storing the secret [D]

The server holds `recovery_pub` only. Verification is a signature over a fresh challenge (purpose `recover` or `confirm_recovery`); the secret never leaves the device, so a database leak yields nothing replayable. The client sends `recovery_pub` (derived on the device) with the signature; an unknown key and a wrong signature return the identical `401 AUTH_INVALID` after identical work (a dummy verification is performed), so there is no enumeration oracle.

### 10.4.4 Rotation of the recovery key [D]

| Case | Rule |
| --- | --- |
| Recovery key never confirmed | Replaceable with a device-key step-up alone; the old key was never proven held |
| Recovery key confirmed | Replacing it needs a device-key step-up AND a signature by the current recovery key, so a thief holding only an unlocked phone cannot lock the owner out |
| Effect | New key `active` and unconfirmed; old key `retiring` for `identity.key_rotation_grace_s`, then `revoked`; a `SecurityNotice` on every device |
| After a recovery (10.8) | The key used is revoked at once and a new one is mandatory in the same request (it was typed on a device that may be hostile) |

## 10.5 Optional e-mail

**Purpose** [D]: generic notices the member opts into (job finished, credit about to expire per `credit.expiry_notice_days`, security notices). Nothing else. **E-mail is never a recovery factor and never a login** (`ISS-102`): a mailbox takeover would otherwise become an identity takeover, and the address links the pseudonym to a person. `identity.email_optional` is true and constant (FD§3.2).

| Aspect | Decision |
| --- | --- |
| Storage | Never clear text (S0.7). `email_ciphertext` = AES-256-GCM with a per-row random nonce under `secret.email_enc_key[version]`; `email_index` = HMAC-SHA-256 of the normalized address under `secret.email_index_key[version]` (one address maps to one member; no address can be looked up without the key) [A] |
| Verification | A one-time code of 8 Crockford base32 characters, stored as SHA-256, valid `identity.email_code_ttl_s`, burned after `identity.code_max_attempts` wrong tries; proves the member controls the address |
| Change and removal | Setting or changing needs a device step-up and is blocked during the recovery cooldown (10.8); removal deletes ciphertext and index at once; the sender integration receives the plain address only at send time |
| Content of mail | Neutral subject, no member id, no handle, no job details, no links carrying tokens; the mail says only that something happened and to open the app |
| Notices default | Off. Each purpose is a separate opt-in in `email_purposes` |
| Decryption access | Only the notification worker holds the decryption key at runtime; no admin screen shows an address (there is no `perm.member.view_email`) |
| Enumeration | Setting an address that another member holds returns the same success-shaped response and sends nothing new [A] |

**Risks, stated plainly** [D]: (1) the mail provider and any relay see the address and the fact that Hamyar wrote to it; (2) an operator, or a seizure that obtains the database and the secret store, can decrypt addresses; (3) an address can be tied to a real person by whoever controls the mailbox provider; (4) delivery to and from Iran-facing mailboxes may be blocked or filtered [V]; (5) phishing mail that imitates Hamyar. Responses: optional and off by default, neutral content, `kill.optional_pii` (10.15) purges every address at once, and `copy.identity.email_optional_notice` tells members to leave the field empty if a link to a real person matters to them.

**Deletion and backups** [D]: a deleted address still exists in backups until they expire. Backup retention is set in `S4.*` and MUST be a published number; a restore re-applies a deletion tombstone list (member id, field, deleted_at) kept for the backup horizon so deleted e-mail does not return [V: the horizon number].
