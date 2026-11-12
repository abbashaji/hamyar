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

## 10.6 Key rotation

`MemberKey` states: `active`, `retiring`, `revoked`. Events: `member.key_rotated` (a successor was added, the old key moves to `retiring`), `member.key_revoked` [A] (any move to `revoked`). Signature algorithm changes are treated as rotation (the `alg` column exists for this). Rotation never changes `mem_` id, balances, trust tier or the recovery key. [D]

```
planned rotation of device key K_old -> K_new            # step-up required (10.13)
  client: generate K_new; persist it locally as 'pending' BEFORE sending anything
  POST /v1/members/me/keys {device_pub: K_new.pub, replaces_key_id: K_old.id}
        signed by K_old (purpose rotate_device_key) AND by K_new (proof of possession)
  server: txn { K_new = MemberKey(active, authorized_by = K_old);
                K_old.state = retiring, K_old.not_after = now + identity.key_rotation_grace_s;
                SecurityNotice; emit member.key_rotated }
  client: authenticates once with K_new (purpose session) -> 'confirmed'
  server: on that first K_new session: K_old.state = revoked, its sessions revoked, emit member.key_revoked
          if never confirmed: sweep revokes K_old at not_after
```

Why a grace period: a lost response or a crash between the two sides must not lock a device out; the retry window is `identity.key_rotation_grace_s` (default 604,800 s = 7 days, `SEC`). Only the old key of the same device is affected; other linked devices keep their own keys. [D]

| Case | Rule |
| --- | --- |
| Compromise of a device key (lost or stolen phone) | `revoke_key` from another device or by recovery: immediate `revoked`, no grace, sessions bound to it die at once |
| Limits | At most `identity.max_devices_per_member` active or retiring device keys; at most one pending rotation per key |
| Recovery key | Rules in 10.4.4 |
| Server-side secrets | Rotation of `secret.*` is in the secrets part of `S10.*`; nothing in this part needs a member to act when a server secret rotates |

## 10.7 Device linking

Purpose: add a second device (new phone, desktop) to the same member without moving any private key. Every device holds its own keypair; no key export, no identity file and no session copying exists, because an exportable identity is a theft target. [D]

```
Offer states: open --claim--> claimed --approval--> approved (T)
              open|claimed --ttl--> expired (T);  open|claimed --cancel or attempts exhausted--> cancelled (T)

A (signed in, step-up):  POST /v1/device-link-offers
    -> {offer_id, link_secret (128 random bits, QR and 26-character Crockford text),
        expires_at = now + identity.device_link_code_ttl_s}
    server stores SHA-256(link_secret) only
B (new device, no session): generate device key and device token;
    POST /v1/device-link-offers/{offer_id}/claims {link_secret, device_pub, device_token,
        platform_class, key_storage}  signed by B's key (purpose link_claim)
    server: constant-time compare of the secret hash; attempts += 1; state claimed;
            claimed_key_hash = SHA-256(device_pub); only the first valid claim wins
    B and A both display  sas = (first 4 bytes of SHA-256(offer_id || device_pub) as uint32) mod 1,000,000, 6 digits
A: shows platform_class and the 6 digits; the person confirms they match B's screen;
    POST /v1/device-link-offers/{offer_id}/approval signed by A's key
        (purpose link_approve, context_hash covers offer_id and claimed_key_hash)
server: txn { MemberKey(device, active, authorized_by_key_id = A.key, authorization_signature);
              upsert Device; SecurityNotice to all devices; emit member.device_linked }
B: next step is an ordinary session by challenge (10.13); B inherits nothing
```

| Limit | Value | Reason |
| --- | --- | --- |
| Offer lifetime | `identity.device_link_code_ttl_s` (300 s) | A shoulder-surfed or photographed QR dies quickly |
| Wrong-secret attempts per offer | `identity.code_max_attempts`, then `cancelled` | Online guessing of a 128-bit secret is already infeasible; this bounds noise |
| Open offers per member | 1 | No stacking |
| Offers per member per day | `ratelimit.device_link_offers_per_day` | Spam and probing |
| Devices per member | `identity.max_devices_per_member` | Bounds one member running many parallel contributors; rate limits are per member anyway (10.9) |

The 6-digit SAS (short authentication string) lets the person check that the key that claimed is the key their new device generated. It is not a secret and adds 10^-6 per-try assurance only; the real protection is single-claim: if an attacker claims first, the real device's claim fails visibly and the person cancels. [D]

**Key chain** [D]: every `MemberKey` row stores the key that authorized it and that key's signature (the first two keys are self-signed at registration; keys added by recovery are signed by the recovery key). `GET /v1/members/me/keys` returns the chain; the client verifies it and warns on any key without a valid authorization. A server job re-verifies every active key and raises the alarm `identity.key_chain_invalid` (metric `hamyar_identity_key_chain_invalid_total`) on any row whose signature does not verify, which detects a key row inserted directly into the database. Limit, stated honestly: the server can still deny service, observe metadata and act inside its own ledger; the chain makes unauthorized key additions detectable by the member's clients, it does not make the operator powerless [H: detection works; test: `T-adv` seeded forged row].

## 10.8 Account recovery and its abuse risks

```
client (new device, no session): person types the recovery key; normalize; verify checksum locally
  ch   = POST /v1/auth-challenges {purpose: 'recover'}
  new_dk, new_rs -> new_rk generated as in 10.3.3
  body = {recovery_pub, new_device_pub, new_recovery_pub, device_token, platform_class, key_storage}
  POST /v1/recoveries body + {challenge_id, recovery_signature (old recovery key),
        device_signature (new_dk), new_recovery_signature (new_rk)}
server:
  1. rate limits: ratelimit.recovery_attempts_per_day per IP hash and per device token
  2. verify challenge and all three signatures; find MemberKey(kind recovery, state active|retiring)
     by public_key; unknown key and bad signature give the same 401 AUTH_INVALID
  3. count completed RecoveryRequest of this member in the last 90 days;
     if >= identity.recovery_max_per_90d: 422 CAP_EXCEEDED, details.copy_key copy.identity.recovery_limit
  4. txn { revoke all MemberKeys of the member (reason 'recovery') and all sessions;
           insert new device key and new recovery key (authorized_by = the old recovery key);
           recovery_cooldown_until = now + identity.recovery_cooldown_s;
           recovery_confirmed_at = null; RecoveryRequest(completed); SecurityNotice; emit member.recovered }
  5. return a session for the new device key
```

Status is never changed by recovery: a `suspended` or `banned` member stays so, `trust_tier` and `restricted` carry over, and a `closed` member cannot recover because closing deletes the keys (10.14). [D] Reason: recovery must not be a reset button.

**Cooldown** (`identity.recovery_cooldown_s`, default 86,400 s) [D]: while `recovery_cooldown_until` is in the future the member can lease, submit, view balance and file appeals, but cannot create jobs, hold escrow, book reservations, change or add e-mail, or issue invites. Reason: a thief who just recovered cannot cash out stolen credit before the owner can notice.

A device whose key was revoked by recovery gets `401 AUTH_INVALID` with `details.reason` = `key_revoked_by_recovery` and shows `copy.identity.recovered_elsewhere`. There is no contest or arbitration process [D]: Hamyar has no identity evidence with which to decide between two claimants, so any rule would be a coin flip an attacker could game.

| # | Risk | Attack | Mitigation | Residual |
| --- | --- | --- | --- | --- |
| 1 | Takeover with a stolen recovery key (paper found, photo in cloud album, shoulder-surf) | Attacker recovers and revokes the owner | Cooldown; cap of `identity.recovery_max_per_90d`; value bounded by K and expiry; notice on revoked devices | Takeover succeeds; the owner loses the pseudonym and its credit, at most K credits |
| 2 | Phishing of the key | Fake site asks for the key | The key is never asked for by any Hamyar message, chat or support channel; recovery screen shows the exact origin; signatures bind `audience` but cannot stop a typed key | Human error; copy `copy.identity.recovery_phishing_warning` |
| 3 | Guessing | Online or offline search of the key space | 2^-128 per guess; `ratelimit.recovery_attempts_per_day`; no per-account lockout | Negligible |
| 4 | Enumeration of members | Probe recovery or challenges for existing keys | Uniform responses and equal work (10.4.3) | None known |
| 5 | Lockout denial of service | Spam failed recoveries to lock a victim | There is no lockout: the target is not named and limits key on IP hash and device token | Attacker can only exhaust their own budget |
| 6 | Farming by repeated recovery: reset limits | Recover to get fresh per-session or per-device counters | Counters are keyed by member id and persist across keys; recovery is capped per 90 days | None |
| 7 | Farming by repeated recovery: launder standing | Recover to shed a ban, restriction or low tier | Recovery never changes status or tier (above) | New identity instead: handled by invites and device limits (10.9, 10.10) |
| 8 | Farming by repeated recovery: second starter grant | Recover and claim again | `grant.max_per_device` and one grant per member; recovery creates no grant | None |
| 9 | Account renting or selling | Hand the recovery key to a buyer | Cannot be detected without identity; caps bound the value | Accepted, monitored via anomalies |
| 10 | Operator social engineering | Someone asks support to restore access | No operator or reviewer permission can restore or reassign a key (matrix, 10.11) | Members who lose everything start over |
| 11 | Insider writes a key row into the database | DBA inserts a `MemberKey` | Key-chain verification job and client verification (10.7) | A DBA can still disrupt service |

## 10.9 Device identification and rate limits

### 10.9.1 What a 'device' is, and the privacy tradeoff [D]

A `Device` is one browser profile that holds a random 128-bit device token (10.3.1). It is identified by `SHA-256(token)` and nothing else. No fingerprint is computed. Candidate signals:

| Signal | Used? | Privacy cost | Cost to evade | Decision |
| --- | --- | --- | --- | --- |
| Device keypair (after registration) | Sessions, linking, key chain | None beyond the key | One new key, free | Not a pre-registration limiter (the key does not exist yet) |
| Device token (random, client-held) | Pre-registration and grant limits | Links identities created in one browser profile | Clear site data, free | Used; a speed bump for honest accidents and lazy farming only |
| IP hash (10.14.2) | Daily and per-minute counters | Daily-rotating keyed hash, kept at most `retention.ip_hash_ttl_days` | New network or VPN, cheap | Used as one coarse signal, never alone, never to ban |
| `platform_class` (4 values) | Stored | About 2 bits | n/a | Compatibility and reachability statistics only |
| Canvas, audio, font, screen, full User-Agent fingerprint | No | High entropy, stable, trackable across sites | Moderate | Rejected: it would make every honest member trackable |
| Hardware ids, IMEI, MAC, advertising id | No | Very high | n/a | Not available to the web; rejected |
| Phone number, SMS code, national id | No | Ties the pseudonym to a SIM or person (FD Principle 8) [V] | n/a | Rejected |
| Third-party CAPTCHA or device-reputation service | No | Third-party tracking; may be blocked in Iran [V] | n/a | Rejected (`analytics.third_party_trackers` is false) |
| Proof of work on registration | No | None | Low for bots, high for low-end phones | Rejected for Phase 1 [H: bots outpace people]; revisit with `OPS` data |
| Verified work before benefit (first verified cell before the starter grant, FD§4.6) | Yes | None | Real effort per identity | The defence that carries the weight (IC6) |

**Tradeoff, stated plainly:** weak device identity means an adversary evades device and IP limits at near-zero cost. What bounds farming is economics (a verified cell before any grant, caps, expiry) and vouching (10.10). A stronger device identifier would protect the platform slightly more and every honest member much less, so it is not used (IC7). The server can link two identities created from the same browser profile through the device token; members who want separate pseudonyms use separate browser profiles, and the settings screen offers 'forget this device', which replaces the token. [D]

**Grant memory** [D]: when a member closes, the `Device` row is deleted unless `grants_issued` is above zero; then only `{token_hash, grants_issued}` remains for `retention.member_inactive_days`, then it is deleted. Reason: `grant.max_per_device` is a lifetime limit, so it needs memory, and a hash of a random token tied to nothing else costs little privacy (`ISS-103`).

### 10.9.2 Limits [D]

| Scope | Key | Limit (parameter) | Window | Store | On exceed |
| --- | --- | --- | --- | --- | --- |
| Public reads, challenge creation | IP hash | `ratelimit.public_rpm` | minute | volatile counters | 429 |
| Failed authentications | IP hash | `ratelimit.auth_failures_per_hour` [A] | hour | volatile | 429 |
| New members | device token | `ratelimit.device_new_members_per_day` | UTC day | volatile | 429 |
| New members | IP hash | `ratelimit.ip_hash_new_members_per_day` | UTC day | volatile | 429 |
| New members | invite tree | `ratelimit.invite_tree_new_members_per_day` | UTC day | counted from `Member.created_at` | 429 |
| Recovery attempts | IP hash and device token, separately | `ratelimit.recovery_attempts_per_day` | UTC day | volatile | 429 |
| Device-link offers | member | `ratelimit.device_link_offers_per_day` [A] | UTC day | volatile | 429 |
| Leases, submissions, API | member | `ratelimit.member_leases_per_hour`, `ratelimit.member_submissions_per_hour`, `ratelimit.member_api_rpm` | hour, hour, minute | volatile | 429 |
| Admin API | admin user | `ratelimit.admin_api_rpm` | minute | volatile | 429 |
| Starter grant | device, tree, day | `grant.max_per_device`, `grant.max_per_invite_tree_per_day`, `grant.max_per_day` | lifetime, UTC day, UTC day | database | grant paused, not rejected (`S6.*`) |
| Invitations | member, tree | `invite.*` (10.10) | n/a | database | `CAP_EXCEEDED` |

```
allow(scope, key, limit, window_s):                  # fixed window aligned to the wall clock / UTC day
  w = floor(now / window_s); k = 'rl:' + scope + ':' + key + ':' + w
  n = store.incr(k, ttl = window_s + 5)              # the TTL is the window, so a counter cannot outlive it
  return n <= limit
request check: peek every applicable counter first; increment all only when every one passes,
  so a denial by one scope does not burn the others.  A small race overshoot is accepted.
```

Failure policy [D]: if the counter store is unavailable, registration, recovery, link and challenge endpoints fail closed (`503 UNAVAILABLE`, `Retry-After`); authenticated member endpoints fail open to a per-process in-memory limiter. Reason: bootstrap endpoints are where abuse enters, and a store outage must not stop contributors already signed in.

Responses [D]: `429 RATE_LIMITED` with `Retry-After` and the headers of S0.11.7; `details.copy_key` is the generic `copy.ratelimit.try_later`; the scope is named only in a member's own limits, never to anonymous callers (it would help tune an attack). The label of `hamyar_ratelimit_denied_total` is the scope, a fixed small set, never an id. IP-hash limits delay; they never ban, flag or reduce standing, because many honest members may share one address (carrier-grade NAT, shared connections) [V: how many members share an address is unknown; `ratelimit.ip_hash_new_members_per_day` is an initial configurable default replaced by `OPS` and `SEC` measurement].

## 10.10 Vouched invitations and invite trees

`Invite` states: `active`, `redeemed` (T), `expired` (T), `revoked` (T). Events [A]: `invite.issued`, `invite.redeemed`, `invite.expired`, `invite.revoked`, `invite.strike_recorded`, `invite.tree_frozen`, `invite.tree_unfrozen`. In `invite_only` mode (`identity.registration_mode`, default) every registration needs an invite; the platform never sends invites (no e-mail or phone numbers are collected for it). [D]

**Issuing rules** (all must hold, else `422 CAP_EXCEEDED` or `403 FORBIDDEN`): [D]

| Rule | Parameter |
| --- | --- |
| Member `status` is `active`, `trust_tier` is not `restricted`, not in recovery cooldown, not inside an issuing suspension | `trust.*`, `identity.recovery_cooldown_s` |
| At least this many accepted cells (verified work, not time) | `invite.min_accepted_cells_to_issue` |
| Active invites below | `invite.max_active_per_member` |
| Tree members plus outstanding invites below | `invite.tree_max_members` |
| Invitee depth (inviter depth + 1) at most | `invite.tree_max_depth` |
| The tree is not frozen | strike rules below |

The invite is a 128-bit random code carried in a link fragment, `https://<member-origin>/join#<code>`; a fragment is not sent in the request line or in `Referer` (`Referrer-Policy: no-referrer` is set as well) and the client posts it in the body. Only `SHA-256(code)` is stored. Single use, expires `invite.ttl_days` after issue, revocable by the issuer until redeemed. Operators issue `kind` = `seed` invites (no inviter, depth 0, a new `invite_tree_id` equal to the seed invite's own id) under two-person approval (`invite.seed_issue`, 10.12); seeds are how the Phase 1 members arrive (FD§9). Invites never carry a bonus by themselves; a `Referral` (`S12.*`) may be attached when `ff.growth.v5_referral` is on. [D]

**Visibility and the social-graph risk** [D]: a vouching graph shows who knows whom, which can expose people if one pseudonym is unmasked. So: an inviter sees counts and the state of their own invites, never who redeemed one; an invitee is told they were invited, never by whom; only operators (`perm.invite.view_tree_edges`, logged) see edges. `invited_by_member_id` is cleared `invite.accountability_days` after the invitee's `created_at` [A], leaving only the opaque `invite_tree_id`. If either side is banned inside that window the edge is kept for `retention.moderation_days` after resolution. Cost: after the window accountability is tree-level only.

**Accountability when a descendant is banned** (every step appealable through the ban process in `S10.*`) [D]

| Event | Effect | Deliberately not done |
| --- | --- | --- |
| A member is banned with a reason class of `credit_farming`, `forgery` or `sybil` (set by the reviewer ruling) and the edge still exists | The direct inviter gets one strike (`Invite.strike_recorded_at`) | No strike for other ban reasons; no strike for ancestors beyond the direct inviter |
| Strikes inside `invite.strike_window_days` reach `invite.strikes_to_revoke_issuing` | Issuing is suspended for `invite.strike_window_days`; the inviter's active invites are revoked | Credit, status, tier and all other rights are untouched |
| Bans inside one tree within `invite.strike_window_days` reach `invite.tree_freeze_ban_threshold` | Tree frozen: no new registrations or invites from it, its starter grants and referral bonuses are held; operator review; unfreeze by an operator, logged | Existing members are not restricted |
| Descendants of a member banned for `sybil` or `credit_farming` | Their pending starter grants are held until a reviewer clears them | No automatic ban, no sampling change |

Reason for no automatic ban cascade: an attacker could join through a victim's invite, misbehave, and punish the victim. Strikes touch only the right to invite, need a reviewer ruling, and can be appealed. [D]

**Anti-farming** [D]

| Vector | Control |
| --- | --- |
| Invite link posted publicly | Single use, `invite.ttl_days`, per-member and per-tree quotas, `ratelimit.invite_tree_new_members_per_day` |
| Mass identities from one tree | `invite.tree_max_members`, depth cap, freeze rule; starter grant only after a verified cell and capped by `grant.max_per_invite_tree_per_day` and `grant.max_per_day` |
| Self-invite with a second identity | Same device token as the inviter, or same IP hash on the same day, does not block (families share devices) but holds the invitee's starter grant and any referral bonus for review (`growth.referral.hold_s` for bonuses) |
| Invite rings and cycles | Impossible: a member has exactly one inviter and invites only create new members |
| Hidden privilege | No per-member quota overrides exist; changes are global parameters with a change log |

Exposure bound from grants, derived from defaults: per tree per day `grant.max_per_invite_tree_per_day x grant.starter_credits` = 2 x 3 = 6 credits; platform-wide per day `grant.max_per_day x grant.starter_credits` = 20 x 3 = 60 credits, each requiring a verified cell and funded from the Reserve, never minted. [D]

## 10.11 Roles and permission matrix

Roles are the `role` enum of S0.8.2. A `member` principal holds the `donor` and `requester` capabilities together; an `AdminUser` holds `reviewer`, `operator` or both and gets the union. The matrix shows what each role alone grants. Human review cells (FD§6.4 channel 2) are member work, not the `reviewer` role. [D]

Legend: `Y` allowed when the conditions hold; `2P` allowed only with two-person approval (X9); `-` denied. Permission names follow `perm.<area>.<action>`; `S15.*` maps every API operation to exactly one permission here. [D]

| Permission | anon | donor | requester | reviewer | operator | system | Conditions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `perm.public.read_surfaces` | Y | Y | Y | Y | Y | Y | rate limits |
| `perm.identity.create_challenge` | Y | - | - | - | - | - | rate limits |
| `perm.identity.create_member` | Y | - | - | - | - | - | X1, invite (10.10) |
| `perm.identity.start_session` | Y | - | - | - | - | - | signature (10.13) |
| `perm.identity.start_recovery` | Y | - | - | - | - | - | 10.8 |
| `perm.identity.view_own` | - | Y | Y | - | - | - | X7 |
| `perm.identity.manage_keys` | - | Y | Y | - | - | - | X5, X7 |
| `perm.identity.link_device` | - | Y | Y | - | - | - | X3, X5 |
| `perm.identity.set_email` | - | Y | Y | - | - | - | X3, X4, X5 |
| `perm.identity.close_account` | - | Y | Y | - | - | - | X5 |
| `perm.identity.export_own_data` | - | Y | Y | - | - | - | X7 |
| `perm.session.revoke_own` | - | Y | Y | - | - | - | X7 |
| `perm.invite.issue` | - | Y | Y | - | - | - | X3, X4, X6, quotas |
| `perm.invite.revoke_own` | - | Y | Y | - | - | - | X7 |
| `perm.cell.lease` | - | Y | - | - | - | - | X3 |
| `perm.cell.submit` | - | Y | - | - | - | - | X3, own lease |
| `perm.cell.decline` | - | Y | - | - | - | - | X3, own lease |
| `perm.review_cell.execute` | - | Y | - | - | - | - | X3, X10 |
| `perm.optin.manage` | - | Y | - | - | - | - | X7 |
| `perm.team.manage` | - | Y | - | - | - | - | X3, `ff.growth.v4_teams` |
| `perm.job.create` | - | - | Y | - | - | - | X2, X3, X4 |
| `perm.job.view_own` | - | - | Y | - | - | - | X7 |
| `perm.job.cancel_own` | - | - | Y | - | - | - | X3, X7 |
| `perm.deliverable.download_own` | - | - | Y | - | - | - | X7 |
| `perm.reservation.create` | - | - | Y | - | - | - | X2, X3, X4, `ff.job.reservations` |
| `perm.balance.view_own` | - | Y | Y | - | - | - | X7 |
| `perm.report.file` | - | Y | Y | - | - | - | X7, `report.max_per_member_per_day` |
| `perm.appeal.file` | - | Y | Y | - | - | - | X7, allowed while suspended or banned, inside `appeal.window_days` |
| `perm.template.author` | - | - | - | Y | - | - | X8 |
| `perm.template.review` | - | - | - | Y | - | - | X8, X11 |
| `perm.template.pause` | - | - | - | Y | Y | - | X8 |
| `perm.service.review` | - | - | - | Y | - | - | X8 |
| `perm.policy.edit` | - | - | - | Y | - | - | X8; loosening is `parameter.loosen` |
| `perm.appeal.decide` | - | - | - | Y | - | - | X8, X11; bans need `appeal.ban_min_reviewers` |
| `perm.report.triage` | - | - | - | Y | - | - | X8 |
| `perm.gold.manage` | - | - | - | Y | - | - | X8; gold answers are visible to reviewers only |
| `perm.audit.view_queue` | - | - | - | Y | - | - | X8 |
| `perm.member.view_basic` | - | - | - | Y | Y | - | X8; id, tier, status, counts; never keys or e-mail |
| `perm.member.suspend` | - | - | - | Y | Y | - | X8, reason required |
| `perm.member.ban` | - | - | - | 2P | 2P | - | X8, X9 |
| `perm.member.reinstate` | - | - | - | Y | - | - | X8, X11 |
| `perm.invite.view_tree_summary` | - | - | - | Y | Y | - | X8; counts only |
| `perm.invite.freeze_tree` | - | - | - | Y | Y | - | X8 |
| `perm.invite.view_tree_edges` | - | - | - | - | Y | - | X8; every read is an `AdminAction` |
| `perm.invite.unfreeze_tree` | - | - | - | - | Y | - | X8 |
| `perm.invite.seed_issue` | - | - | - | - | 2P | - | X8, X9 |
| `perm.parameter.edit` | - | - | - | Y | Y | - | X8; only the owner role of the area (S0.10.5) |
| `perm.parameter.loosen` | - | - | - | 2P | 2P | - | X8, X9; covers policy-rule loosening (R10) |
| `perm.killswitch.engage` | - | - | - | Y | Y | - | X8; reviewers only for template, service and member scopes |
| `perm.killswitch.release` | - | - | - | 2P | 2P | - | X8, X9 |
| `perm.launch.signoff` | - | - | - | - | 2P | - | X8, X9; `S14.*` may extend |
| `perm.ledger.explore` | - | - | - | Y | Y | - | X8; read-only |
| `perm.ledger.reverse` | - | - | - | - | 2P | - | X8, X9 |
| `perm.capacity.view` | - | - | - | Y | Y | - | X8 |
| `perm.adminaction.view` | - | - | - | - | Y | - | X8 |
| `perm.admin.role_grant` | - | - | - | - | 2P | - | X8, X9 |
| `perm.admin.credential_add` | - | - | - | - | 2P | - | X8, X9 |
| `perm.admin.credential_lock` | - | - | - | Y | Y | - | X8; emergency lock of another admin, one admin suffices |
| `perm.admin.credential_unlock` | - | - | - | - | 2P | - | X8, X9 |
| `perm.disclosure.release` | - | - | - | - | 2P | - | X8, X9, counsel sign-off [V] |
| `perm.identity.purge_optional_pii` | - | - | - | - | Y | - | X8; engages `kill.optional_pii` (10.15) |
| `perm.system.run_background_jobs` | - | - | - | - | - | Y | sweeps, retention purge, key-chain check, invite expiry |

**Conditions** [D]

| Id | Condition |
| --- | --- |
| X1 | `launch.members_may_join` is true (else `403 LAUNCH_GATE_CLOSED`) |
| X2 | `launch.member_jobs_enabled` is true |
| X3 | Member `status` is `active` and no `kill.member.<id>` is engaged. A `suspended` or `banned` member keeps only the permissions without X3: view own identity, export, revoke own sessions, view balance, file appeals, close account |
| X4 | Not in the recovery cooldown (10.8) |
| X5 | Step-up: a fresh signature by the session's key no older than `session.step_up_max_age_s` |
| X6 | `trust_tier` is not `restricted` |
| X7 | Object-level check: the object belongs to the calling principal; the member id comes from the session, never from the path or body; a foreign object returns `404 NOT_FOUND` (S0.11.3) |
| X8 | Admin session on the admin origin; writes also need a WebAuthn step-up inside `session.step_up_max_age_s` |
| X9 | Two-person approval by a different `AdminUser` (10.12) |
| X10 | `ff.channel.human_review` is on |
| X11 | Conflict-of-interest exclusion: not the author, not the original decider, and not an admin whose `declared_member_ids` include a party |

**Rules** [D]

1. Deny by default (IC5): a (principal, permission) pair not listed is denied, and a test enumerates every pair (AC-access-01). The matrix is versioned configuration shipped with the code and changed only by a reviewed migration, never from an admin screen; reason: privilege changes are rare and must be reviewed like code.
2. Separation of powers: reviewers cannot change operator-owned parameters, launch switches or the ledger; operators cannot approve templates or services. Reason: reviewer capture and insider risk (FD§5.7 failure mode 10). An `AdminUser` holding both roles gets the union, but a second approver must always be a different `AdminUser`.
3. Deliberately absent permissions: no principal can read e-mail addresses, private keys or recovery keys, restore or reassign a member's keys, read a provider credential, or read a volunteer's chat page. Operators cannot create members.
4. Members who are also admins hold two unlinked principals; `AdminUser.declared_member_ids` is optional, used only by assignment logic to apply X11, and shown only to the admin concerned and to operators approving `admin.role_grant`. Without it X11 rests on honesty [V: process].
5. One person alone cannot satisfy X9. With a single admin, two-person actions (including launch sign-off) cannot run and there is no bypass; whether to add a second person is an owner decision (`S3.*`, `ISS-102`).

## 10.12 Admin authentication

**Decision** [D]: admins (`AdminUser`, roles `reviewer` and `operator`) authenticate with **WebAuthn passkeys** on a **separate origin**, with **two-person approval** for dangerous actions. No shared password, no password at all, no TOTP seed, no SMS, no e-mail link, no third-party single sign-on exists for admins. Reason: WebAuthn signs a challenge that is bound to the exact origin, so a look-alike site cannot harvest a usable login; the server stores only public keys, so a database leak contains nothing to replay; it needs no call to any third party, which matters for reachability from Iran [V: WebAuthn support and reachability of the admin origin from where each admin sits].

| Alternative | Rejected because |
| --- | --- |
| One shared admin token (the existing panel's model, FD§10) | A shared secret has no individual accountability and one leak is total; prompt scope A forbids it |
| Per-admin password | Phishable, reusable, needs a slow hash and a reset path |
| TOTP | The shared seed lives on the server and the code is phishable |
| SMS or e-mail codes | SIM swap, mailbox takeover, ties admins to a phone or provider |
| Third-party SSO | External dependency, possible blocking, a tracker of admin activity |
| Client TLS certificates | Hard to issue, rotate and recover for a small volunteer team |

| WebAuthn setting | Value | Reason |
| --- | --- | --- |
| Relying party id and origin | The admin host only, for example `admin.<domain>`, never the member origin; exact origin match is checked server-side | A passkey made for the admin site cannot sign in anywhere else; a separate origin also separates storage and CORS (S0.11.4) |
| `userVerification` | `required` | The authenticator checks a PIN or biometric locally; a stolen unlocked key is not enough |
| `residentKey` | `preferred` (discoverable credentials allow usernameless sign-in) | Fewer typed identifiers |
| `attestation` | `none` | No authenticator model data is collected; the cost is that hardware binding cannot be proven by the server |
| Algorithms | EdDSA (-8) and ES256 (-7) | Broad support [V] |
| Authenticator advice | Operators SHOULD hold at least one roaming hardware security key; synced platform passkeys depend on a vendor cloud account whose availability and terms for admins in some countries are [V] | Whether to require hardware keys (attestation `direct` plus an allowlist) is an owner decision (`S3.*`) |
| Credentials per admin | At least `security.admin_min_credentials` active (a primary and an offline backup) | A lost authenticator must not lock an admin out |

```
sign-in:  POST /v1/admin/auth-challenges  -> {challenge (32 random bytes, single use, ttl identity.challenge_ttl_s)}
          POST /v1/admin/sessions {assertion}
  server: exact origin and rpIdHash match; UP and UV flags set; signature valid for the stored public key;
          challenge matches and is unused; if sign_count is non-zero it must be greater than the stored one,
          else the credential is locked, the alarm admin.credential_cloned is raised and no session is issued;
          create session (scheme admin), emit admin.signed_in
```

**Enrollment** [D]: the first `AdminUser` is created by a bootstrap command run by whoever holds infrastructure access (the trust root): it prints a single-use 128-bit enrollment code valid `identity.device_link_code_ttl_s`. After that, every new admin or new credential needs two-person approval (`admin.role_grant`, `admin.credential_add`): admin A proposes, admin B approves with a payload-bound assertion, the system issues an enrollment code that A hands over out of band, and the new person registers a passkey at the admin origin. The last active `operator` can never be disabled or locked by the system (the request is refused). Credentials are `pending` until the second approval.

**Two-person protocol** [D]

```
propose:  AdminAction(state proposed, action, target_ref, params_hash = SHA-256(canonical params),
          proposed_by = P, expires_at = now + security.two_person_ttl_s)      # needs X8
approve:  admin Q (Q != P, required role, X8) completes a WebAuthn assertion whose challenge =
          SHA-256(action_id || params_hash || nonce), so the assertion itself attests approval of that exact payload
execute:  only after approval and before expiry; parameters cannot change after proposal;
          outcome and both admin ids are written to AdminAction; emit admin_action.executed
```

The set of two-person actions is `security.two_person_actions`. This part defines the action names and proposes the initial default below (`ISS-102`): `ledger.reversal`, `launch.signoff`, `parameter.loosen`, `killswitch.release` (from S0.10.6), plus [A] `member.ban`, `invite.seed_issue`, `admin.role_grant`, `admin.credential_add`, `admin.credential_unlock`, `disclosure.release`. Locking a credential is deliberately single-admin (an emergency brake: `perm.admin.credential_lock`); unlocking is two-person. Two accounts held by one human cannot be detected by software; distinct humans per approval is a process rule [V: operating procedure]. Every `AdminAction` records who, what, target, payload hash, outcome and `request_id`; rows are append-only and hash-chained like the ledger [A].

Admin surface hardening [D]: strict Content-Security-Policy with no third-party script, font or frame; the token is held in page memory only, so a reload requires a new assertion; `ratelimit.admin_api_rpm`; CORS allows only the admin origin; a member token sent to an admin route is `AUTH_INVALID` and counted (S0.11.4).

## 10.13 Session handling

| Aspect | Member session | Admin session |
| --- | --- | --- |
| Token | Opaque 256-bit CSPRNG value, base64url, sent as `Authorization: Bearer`; no cookie, no JWT, so no CSRF surface and no claims to forge | Same |
| Storage | Server: SHA-256 of the token in `Session`; device: IndexedDB | Server: same; page memory only |
| Issued by | A signed challenge with an active `MemberKey` (purpose `session`) or by registration or recovery | WebAuthn assertion (10.12) |
| Idle TTL | `session.member_idle_ttl_s` (2,592,000 s = 30 days) | `session.admin_idle_ttl_s` (1,800 s) |
| Absolute TTL | `session.member_abs_ttl_s` (7,776,000 s = 90 days) | `session.admin_abs_ttl_s` (28,800 s) |
| Step-up | A fresh signature (purpose `step_up`) sets `step_up_at`; valid `session.step_up_max_age_s` | Same with a new assertion |
| Binding | To one `key_id`; one active session per key | To one credential |

**Rotation** [D]: a session is never extended in place beyond its absolute TTL. The client re-authenticates silently by signing a fresh challenge (no user action), which issues a new token and atomically revokes the previous session of the same key; clients do this on `AUTH_EXPIRED` and before the idle limit, and coordinate between tabs with the Web Locks API where available [V]. Short TTLs are therefore a security setting, not a usability cost. Tokens are also re-issued on step-up, key rotation and recovery. `last_used_at` is written at most once per `session.touch_min_interval_s`, to avoid a write per request.

**Validation** (every request) [D]

```
h = SHA-256(token); s = sessions.get(h)                         # constant-time compare on the hash
reject AUTH_INVALID  if s is null, s.state != active, or s.principal_type != endpoint auth_scheme
reject AUTH_EXPIRED  if now > s.abs_expires_at or now > s.idle_expires_at
reject AUTH_INVALID  if the bound key is revoked, or retiring and past not_after
reject FORBIDDEN     if the permission or a condition X3..X8 fails (10.11)
then: touch last_used_at (rate-limited); idle_expires_at = last_used_at + idle TTL, never past abs_expires_at
```

**Revocation** [D]: (1) 'log out' revokes the current session; (2) 'log out everywhere' revokes all sessions of the member (`POST /v1/members/me/session-revocations`, step-up); (3) revoking or rotating a key revokes the sessions bound to it; (4) recovery revokes all; (5) `member.banned` revokes all sessions at once and `member.suspended` or an engaged `kill.member.<id>` blocks X3 permissions on the next request; (6) locking an admin credential revokes that admin's sessions and raises an alarm. Revoked and expired rows are deleted by the retention sweep every `retention.sweep_interval_s`; a row never outlives `retention.session_days` (constraint C9 [A]: `session.member_abs_ttl_s <= retention.session_days x 86,400`).

**Considered and rejected** [D]: per-request signatures binding the token to the device key (DPoP style). They cost CPU and battery on low-end phones and add little against the main threat, a script injected into the page, which can ask a non-extractable key to sign. The defences are a strict Content-Security-Policy, no third-party scripts, escaping of all submitted text (`S9.*`), step-up for sensitive actions and short admin lifetimes.

## 10.14 Logging, IP handling and retention

### 10.14.1 What is and is not collected [D]

Retention values are parameters of `S0.10.6` (`retention.*`); `member_bound`, `job_bound`, `moderation`, `short`, `ops` and `permanent` are the classes of S0.7.

| Data item | Collected? | Form and place | Retention | Rationale |
| --- | --- | --- | --- | --- |
| Raw IP address | No | Held in memory for the length of one request and passed once to the IP hasher; never logged, never in an error, metric, trace or database row | None (`retention.raw_ip_stored` = false, constant) | FD Principle 8 |
| IP hash | Short-lived | Rate-limit counter keys in a volatile store (10.14.2) | At most `retention.ip_hash_ttl_days` (1); each counter dies with its window | Coarse abuse limits (10.9) |
| Country, city, ASN from the IP | No | No GeoIP lookup on any member endpoint | None | Location is never collected or inferred (`public.location_display` = `never`) |
| User-Agent, Accept-Language, other headers | No | Only `platform_class` (4 values) is derived once at registration; the raw header is dropped; language is the member's own setting | `platform_class`: `member_bound` | Compatibility statistics at about 2 bits |
| Referer | No | `Referrer-Policy: no-referrer` on every response | None | Invite links and pages must not leak |
| Request log line | Yes, minimal | `request_id`, route template, method, status class, latency, response size bucket, `principal_type`, `actor_day_hash` = HMAC(daily key, member id) | `retention.request_log_days` (7) | Debugging; the daily hash lets a day's requests be followed without a standing identifier |
| Request and response bodies, `Authorization` header | No | Stripped before any logger; submitted text lives only in its domain row | None in logs | Prompts and outputs are job data, not log data |
| Session | Yes | SHA-256 of the token, state, expiry (10.13) | `short`, at most `retention.session_days` (90) | Authentication |
| Public keys, key chain | Yes | `MemberKey` | `member_bound` | Authentication, tamper evidence |
| Private keys, recovery key | Never reach the server | Device only | n/a | IC2 |
| Device token | Yes, hashed | `Device.token_hash` | `member_bound`, then grant-memory residue for `retention.member_inactive_days` (10.9.1) | Lifetime grant limit |
| E-mail | Optional | Ciphertext plus keyed index (10.5) | `member_bound`; deleted on removal, closure or `kill.optional_pii` | Notices only |
| Activity time | Date only | `Member.last_active_on` | `member_bound`; inactivity of `retention.member_inactive_days` (365) closes the member | Inactivity closure |
| Precise timestamps on leases, submissions, ledger entries | Yes | Domain rows | Their own class (`job_bound`, `permanent`) | Required for leases and the ledger; public and member-facing surfaces coarsen them (`S12.*`) because time of day can reveal a time zone |
| Cell and job content | Yes | `job_bound` | Payload fields purged `retention.job_payload_days` (30) after a terminal state; hashes stay | Delivery, audit, provenance |
| Volunteer's provider account, credentials, session, chat page | Never | n/a | n/a | Ground rule 3; IC3 |
| Volunteer-attested service and model | Yes | Provenance fields | `job_bound` | Audit, labelled attested not proven (FD§5.6) |
| Analytics events | Yes, no personal data | `Event`; no cookies, no third-party tracker; cohorts below `analytics.min_cohort_k` suppressed | `retention.event_raw_days` (30), then aggregates | FD§9 measures with minimal retention |
| Operational telemetry and errors | Yes, scrubbed | No IP, no body, no token; no third-party error tracker | `retention.ops_log_days` (30) | Operations |
| Failed-authentication and denial counters | Counts only | Volatile counters by IP hash; metric by scope | Window; metrics `ops` | Abuse limits |
| Security notices | Yes | `SecurityNotice` | `retention.session_days` | Member awareness (10.6 to 10.8) |
| Recovery requests | Yes | `RecoveryRequest`, no IP | 90 days | Recovery cap |
| Invite edges | Yes | `Invite`, `Member.invited_by_member_id` | Edge cleared `invite.accountability_days` after joining; kept `retention.moderation_days` after resolution if a party is banned | Accountability (10.10) |
| Reports and appeals | Yes | `Report`, `Appeal` | `moderation`: `retention.moderation_days` (180), then counts | Safety process |
| Admin actions | Yes | `AdminAction` with `adm_` ids only | `permanent` | Accountability of operators |
| Admin credentials | Yes | Public key, sign count, label | `permanent` while the admin exists | WebAuthn |
| Legal requests received | Yes | Count, date, outcome, no content | `permanent` | Transparency report, if lawful [V] |
| Backups | Yes | Encrypted snapshots of the above | Set in `S4.*` as a published number; restores re-apply deletion tombstones | Recovery of service [V] |
| DNS, TLS and connection metadata at the host or CDN | Outside this system | Whatever the host keeps | Unknown [V] | Stated in 10.15 and the member notice |

### 10.14.2 Exact IP handling [D]

```
IpHasher.hash(ip):                       # runs once, in edge middleware, before routing and logging
  addr = parse(ip)
  if addr is IPv6: addr = addr masked to its /64 prefix       # one household can hold a /64; IPv4 stays /32
  day   = utc_date(now)                                       # epoch label
  k_day = HKDF-SHA-256(ikm = secret.ip_hash_key[version], salt = 'hamyar/v1/iphash', info = day, L = 32)
  return base64url( HMAC-SHA-256(k_day, addr_bytes)[0:16] )   # 128-bit truncated hash
  # the variable 'ip' is discarded; k_day is never stored; the logger has no access to the raw value
```

1. **The same address hashes differently each UTC day**, so counters cannot be joined across days even by someone holding the hash store; per-minute, per-hour and per-day limits only need equality within a day. [D]
2. **Counters live in a volatile store** behind the `CounterStore` interface; not in the relational database, not in backups, never written with a TTL longer than the window; if the chosen engine snapshots to disk, the snapshot must expire with the same bound [V: engine behavior]. [A]
3. **`retention.ip_hash_ttl_days`** is the ceiling on any IP-hash-bearing record. Setting it to 0 turns off the daily IP limits (only per-minute limits remain) and leaves registration limited by device token and tree; this is the lever for emergency minimization (10.15.4).
4. **Residual risk, stated plainly:** the IPv4 space has only 2^32 addresses, so anyone who holds both the hashes and `secret.ip_hash_key` can recover the addresses by enumeration. The key therefore lives in the secrets store, separate from the counter store, and is rotated per `security.secret_rotation_days`; hashes expire within a day.
5. **Deployment requirement** [V]: the reverse proxy, CDN or platform MUST NOT write client IPs to access logs, and the trusted header that carries the client address must be one only the platform can set. Where the host cannot disable its own logging, that fact MUST be recorded in the G1 threat model and in the member notice (the host then sees what 10.15.1 says).
6. A test sends a sentinel address and asserts it appears in no database dump, log line, metric, trace or backup fixture (AC-privacy-01).

### 10.14.3 Closure, export, deletion [D]

`member.closed` (member-initiated, or after `retention.member_inactive_days`) deletes `MemberKey`, `Device` (except grant memory), `Session`, e-mail, `SecurityNotice`, `OptIn` and invite edges, and reduces the `Member` row to the opaque `mem_` id, as S0.7 requires. Ledger and provenance rows are `permanent` by design and contain no personal data; provenance carries `vol_` handles, not `mem_` ids (S0.6.4). Closure is irreversible and cannot be recovered. `GET /v1/members/me/export` returns the member's own rows in JSON. The interface states that closure does not rewrite the public ledger or published provenance.

## 10.15 Member safety in a high-risk context

The launch audience includes people in Iran for whom participation may carry personal risk (FD§8.2 risk 5). The threat model itself is a G1 deliverable [V]; this section fixes the design commitments that part must test. [D]

### 10.15.1 What each party can see

| Party | Can see | Cannot see | Residual risk and response |
| --- | --- | --- | --- |
| Local network observer, ISP | That the device connects to Hamyar's addresses, traffic volume and timing; the host name unless encrypted client hello is used [V] | Request contents (TLS) | Use of the site cannot be hidden. Hamyar does not provide or advise circumvention (FD Principle 9). The notice says so |
| Hosting or edge provider | If it terminates TLS: plaintext requests, tokens, submitted text and client IPs at its layer | Keys it does not hold (private keys, recovery keys) | Treated as trusted-but-not-blind; storage and hosting sit behind interfaces so they can move (`S4.*`); reachability from Iran is [V] |
| Database or storage provider | Everything in the database, including ciphertext, hashes, pseudonymous ids | Clear e-mail without the secret store; any IP older than the counter window | Separate secrets store; minimal columns (10.2) |
| Operator or admin (insider) | Pseudonymous rows within their permissions (10.11); invite edges (operators only) | E-mail (not exposed), keys, provider data, volunteer chat pages | Two-person actions, `AdminAction` log, separation of powers |
| Other members | A donor sees the cell text; a requester sees the output | Requesters never see `vol_` handles or `mem_` ids; donors never see requester ids | Provenance salted-hash handle (S0.6.4) |
| The volunteer's own AI provider | The prompt and the answer, inside the volunteer's own account | Hamyar identity or keys | Outside Hamyar's control; the cell card says so; clean-chat advice (FD§5.5) |
| E-mail sender or mailbox provider | The address and that Hamyar wrote | Anything beyond the neutral notice | 10.5 |
| Browser or phone vendor, extensions, cloud sync | Whatever is on the device, including the key store and clipboard | n/a | Warnings at key display; panic wipe (10.15.4) |

### 10.15.2 Seizure and compelled disclosure

| Scenario | What exists to hand over | What does not exist | Design response |
| --- | --- | --- | --- |
| Database seized | Pseudonymous members, public keys, ledger and job rows, content within `retention.job_payload_days`, request logs for `retention.request_log_days`, invite edges inside the accountability window, e-mail ciphertext | Names, phones, clear e-mail, raw IPs, passwords, private and recovery keys, provider credentials | Minimal columns, short retention |
| Database plus secrets store seized | The above plus decryptable e-mail addresses and IP hashes that can be enumerated back to addresses | Keys on devices | Keep the stores separate; `kill.optional_pii` (10.15.4) |
| Order naming a member id | Their rows, keys, balances, activity dates, submissions in retention | The identity behind the pseudonym | Disclosure is two-person (`disclosure.release`) with counsel sign-off [V], recorded as a count |
| Order for the invite graph | Edges inside the accountability window; tree membership afterwards | Edges older than `invite.accountability_days` | Edge clearing (10.10) |
| Member's device seized, unlocked | The active session and device key: full control until revoked | The recovery key (never stored on the device) | Panic wipe; remote revoke from another device or by recovery |
| Recovery paper seized | Control of the identity | n/a | Cooldown; keep it private; accepted residual risk |
| Admin's device or authenticator seized | One credential | The second approver | Emergency credential lock by any admin; short admin sessions |

What Hamyar commits to: hold less, decrypt less, log the disclosure, publish counts where the law allows [V]. It does not commit to resist a lawful order; whether and how to respond is counsel's decision [V].

### 10.15.3 No location, no mandatory identity [D]

No location is collected, inferred or displayed by default (`public.location_display` = `never`); no GeoIP is used (10.14.1); teams are opt-in and hidden below `team.min_public_members`; share cards carry no personal data (`S12.*`). No real name, photo, phone, e-mail or social account is ever required; a member needs only a browser. Geo-blocking for sanctions or export-control reasons would need IP geolocation, which contradicts this section: it is a question for counsel and an owner decision (`S3.*`) [V], and until decided no geo lookup exists.

### 10.15.4 Safety features [D]

| Feature | Behavior |
| --- | --- |
| Panic wipe | One tap on any screen deletes the device key, device token, session, caches and local settings, then tries to revoke the device key on the server (local deletion happens first and does not wait for the network) |
| Quick exit | A button on every screen that navigates to a neutral page and replaces the history entry where the browser permits [V] |
| `kill.optional_pii` [A] | Operator action (`perm.identity.purge_optional_pii`): one admin engages, two-person releases (`killswitch.release`). Immediately: refuse new e-mail addresses, delete every e-mail ciphertext and index, set the effective `retention.ip_hash_ttl_days` to 0, set the effective `retention.request_log_days` to 0 and delete existing request logs, stop recording `actor_day_hash` |
| Notices | The six `copy.*` keys below, all marked `needs_human_and_legal_review` |

| Copy key | en | fa |
| --- | --- | --- |
| `copy.privacy.pseudonymity_notice` | Hamyar does not ask for your name, phone number or e-mail. Your identity is a key stored on this device. This reduces what we hold about you; it does not make you anonymous: your internet provider can see that you connect to this site, and anyone who gets your device or recovery key can act as you. | همیار نام، شماره تلفن یا ایمیل شما را نمی‌خواهد. هویت شما کلیدی است که روی همین دستگاه نگه‌داری می‌شود. این کار اطلاعاتی را که ما از شما داریم کم می‌کند، اما شما را ناشناس نمی‌کند: ارائه‌دهندهٔ اینترنت شما می‌تواند ببیند که به این سایت وصل می‌شوید، و هر کس به دستگاه یا کلید بازیابی شما دست یابد می‌تواند به‌جای شما عمل کند. |
| `copy.privacy.no_promise_notice` | We declare that we collect the minimum needed and do not store your IP address. We cannot promise that nobody can see that you use Hamyar, or that your data can never be taken from our servers. | ما اعلام می‌کنیم که کمترین اطلاعات لازم را جمع می‌کنیم و نشانی IP شما را ذخیره نمی‌کنیم. نمی‌توانیم قول بدهیم که هیچ‌کس نتواند ببیند شما از همیار استفاده می‌کنید، یا اطلاعات هرگز از سرورهای ما گرفته نشود. |
| `copy.identity.recovery_key_notice` | This recovery key is the only way to get your identity back if you lose this device. Write it down and keep it somewhere private. We never see it and cannot restore it for you. Anyone who has it can take over your identity. Hamyar will never ask you for it. | این کلید بازیابی تنها راه برگرداندن هویت شما در صورت از دست رفتن این دستگاه است. آن را روی کاغذ بنویسید و جایی خصوصی نگه دارید. ما هرگز آن را نمی‌بینیم و نمی‌توانیم آن را برای شما بازیابی کنیم. هر کس آن را داشته باشد می‌تواند هویت شما را در اختیار بگیرد. همیار هرگز آن را از شما نمی‌خواهد. |
| `copy.identity.email_optional_notice` | E-mail is optional. If you add one, we store it encrypted and use it only for the notices you choose. It cannot be used to recover your identity. An e-mail address can link you to a real person; if that matters to you, leave it empty. | ایمیل اختیاری است. اگر آن را اضافه کنید، به‌صورت رمزگذاری‌شده نگه‌داری می‌شود و فقط برای اعلان‌هایی که خودتان برمی‌گزینید به کار می‌رود. با ایمیل نمی‌توان هویت را بازیابی کرد. نشانی ایمیل می‌تواند شما را به یک شخص واقعی پیوند دهد؛ اگر این برایتان مهم است، آن را خالی بگذارید. |
| `copy.identity.wipe_device_confirm` | Remove this identity from this device? Without your recovery key you will not be able to get it back. | این هویت از این دستگاه حذف شود؟ بدون کلید بازیابی نمی‌توانید آن را پس بگیرید. |
| `copy.identity.recovery_phishing_warning` | Enter your recovery key only on the exact address shown here, and never in a chat, e-mail or message. | کلید بازیابی را فقط در همین نشانی وب‌سایت وارد کنید و هرگز آن را در گفتگو، ایمیل یا پیام وارد نکنید. |

## 10.16 What the platform can NOT promise

The member-facing wording uses `declared` and never `guaranteed` (IC8). Stated plainly, Hamyar cannot promise that: [D]

1. Anyone is anonymous. A network observer, the host and the member's own devices can reveal that a person uses Hamyar.
2. Use of Hamyar is safe or lawful for a given person in a given country. Terms of services, sanctions and local law are [V] and are not decided by this product.
3. The host, edge or network will keep Hamyar reachable, or that it is reachable from Iran [V].
4. Data cannot be taken from the servers by a compromise, an insider or a lawful or unlawful order. Hamyar can only hold less, keep it for less time and separate what it keeps.
5. A lost recovery key or a lost device can be fixed. No operator can restore or reassign an identity.
6. A stolen recovery key or an unlocked stolen device cannot be used against the owner, beyond the limits of the cooldown and caps.
7. IP hashes are irreversible. They are keyed and short-lived, but enumerable by whoever holds the key and the hashes (10.14.2).
8. The vouching graph, once exposed, will not harm the people in it. It is minimized and cleared, not erased from every backup.
9. A volunteer's provider account is safe. Hamyar never touches it and cannot see what the provider does with a prompt.
10. Fake accounts and credit farming are prevented. They are bounded and monitored (10.9, 10.10); a patient adversary with many cheap identities is accepted residual risk.
11. Backups, deleted e-mail and closed accounts vanish at once. Backups expire on their schedule (10.5, 10.14.3).
12. Counsel, regulators or providers will accept the design. Every such question stays [V].

## 10.17 Acceptance criteria

Given / When / Then; each criterion becomes a test in the layer shown (S0.5; `S18.*` owns the harness). [D]

| Id | Given | When | Then | Layer |
| --- | --- | --- | --- | --- |
| AC-identity-01 | `launch.members_may_join` is true and a valid invite | A client registers with both signatures | One `Member` (`new`, `active`), two `MemberKey`, one `Device`, invite `redeemed`, a session returned, `member.created` emitted | e2e |
| AC-identity-02 | `launch.members_may_join` is false | A client registers | `403 LAUNCH_GATE_CLOSED` and no row is written | policy |
| AC-identity-03 | A registration whose recovery signature was made by a different key | It is submitted | `401 AUTH_INVALID`, no member created | adv |
| AC-identity-04 | The recovery key screen is open | Network activity is recorded | No request is made while it is shown, and the key appears in no request, log or event afterwards | e2e |
| AC-identity-05 | A member with a confirmed recovery key | A new device recovers with the correct key | All old keys and sessions are revoked, new device and recovery keys exist, `recovery_cooldown_until` is set, `member.recovered` emitted, status and tier unchanged | e2e |
| AC-identity-06 | A member inside the recovery cooldown | They create a job, change e-mail or issue an invite | `403 FORBIDDEN` (X4); leasing and submitting still work | policy |
| AC-identity-07 | A member with `identity.recovery_max_per_90d` completed recoveries in 90 days | They recover again | `422 CAP_EXCEEDED`, nothing changes | adv |
| AC-identity-08 | An unknown recovery key and a known key with a bad signature | Both are submitted | The two responses are identical in status and body and equal in work | adv |
| AC-identity-09 | A device key rotation whose response was lost | The client retries inside `identity.key_rotation_grace_s` | It succeeds; after `not_after` an unconfirmed old key is `revoked` | fsm |
| AC-identity-10 | An open device-link offer | Two devices claim it, then the first is approved; later a sixth device is offered | Only the first claim wins; the key chain records `authorized_by_key_id`; the sixth is refused at `identity.max_devices_per_member` | adv |
| AC-identity-11 | A recovery key typed with one wrong character | The client normalizes it | The checksum fails on the device, no request is sent, no recovery attempt is counted | unit |
| AC-identity-12 | An address already held by another member | A member sets it | The response is identical to a fresh address and nothing is sent to the holder; removal deletes ciphertext and index at once | adv |
| AC-invite-01 | One active invite | Two clients redeem it at once | One succeeds, the other gets `409 STATE_CONFLICT` | adv |
| AC-invite-02 | A member with `invite.max_active_per_member` active invites | They issue another | `422 CAP_EXCEEDED` | policy |
| AC-invite-03 | A direct inviter with one strike | A second member they invited is banned for `sybil` | Issuing is suspended and active invites revoked; status, tier and credit are unchanged | fsm |
| AC-invite-04 | A tree with `invite.tree_freeze_ban_threshold` bans in the window | Anyone registers with an invite of that tree | Refused; its pending starter grants are held | policy |
| AC-invite-05 | An invite edge older than `invite.accountability_days` with no ban | The sweep runs | `invited_by_member_id` is null and `invite_tree_id` remains | unit |
| AC-access-01 | The permission matrix and the API operation table | A test enumerates every (principal, permission) pair | Every pair not marked `Y` or `2P` is denied | policy |
| AC-access-02 | Members A and B | A requests B's job by id | `404 NOT_FOUND` | adv |
| AC-access-03 | A `suspended` member | They lease a cell, then file an appeal | The lease is `403 FORBIDDEN`; the appeal is accepted | policy |
| AC-access-04 | A reviewer-only admin | They edit an operator-owned parameter | `403 FORBIDDEN` | policy |
| AC-admin-01 | A valid member token | It is sent to `/v1/admin/*` | `401 AUTH_INVALID`, counted by the limiter | adv |
| AC-admin-02 | A proposed two-person action | The proposer approves it; or the payload changes after approval | Refused; an approval covers only its `params_hash` | adv |
| AC-admin-03 | A passkey whose `sign_count` goes backwards | It signs in | No session, the credential is `locked`, `admin.credential_cloned` raised | adv |
| AC-admin-04 | One active operator | A request locks or disables that operator | Refused (last operator rule) | policy |
| AC-session-01 | A session past its idle or absolute TTL | It is used | `401 AUTH_EXPIRED` | unit |
| AC-session-02 | A device key with live sessions | The key is revoked | The sessions are refused on the next request | fsm |
| AC-session-03 | A database dump after sign-in | It is searched for the token | Only its SHA-256 appears | adv |
| AC-session-04 | An active session of a key | The client signs in again with that key | The previous session of that key is revoked | fsm |
| AC-privacy-01 | A request from a sentinel IP address | Dumps, logs, metrics, traces and backup fixtures are searched | The sentinel appears nowhere (`retention.raw_ip_stored` = false) | inj |
| AC-privacy-02 | The same IP on two UTC days | `IpHasher.hash` runs | The two hashes differ | unit |
| AC-privacy-03 | `kill.optional_pii` is engaged | The action completes | E-mail ciphertexts and request logs are deleted, new addresses are refused, IP-hash TTL is 0 | e2e |
| AC-privacy-04 | Any request with a body and an `Authorization` header | The request log line is read | It holds none of the body, header, IP or token | inj |

## 10.18 Events, interfaces, parameters, hooks

### 10.18.1 Operations required by this part

Names and paths are proposals for `S15.*`, which is authoritative; methods and prefixes follow S0.11. `Idem` marks a required `Idempotency-Key`. [A]

| `op` | Request | Auth | Permission | Idem |
| --- | --- | --- | --- | --- |
| `createAuthChallenge` | `POST /v1/auth-challenges` | none | `perm.identity.create_challenge` | no |
| `createMember` | `POST /v1/members` | none | `perm.identity.create_member` | yes |
| `createSession` | `POST /v1/sessions` | none | `perm.identity.start_session` | no |
| `deleteSession` | `DELETE /v1/sessions/{ses_id}` | member | `perm.session.revoke_own` | no |
| `createSessionRevocation` | `POST /v1/members/me/session-revocations` | member (X5) | `perm.session.revoke_own` | yes |
| `getMe`, `exportMe` | `GET /v1/members/me`, `GET /v1/members/me/export` | member | `perm.identity.view_own`, `perm.identity.export_own_data` | no |
| `listMemberKeys`, `createMemberKey` | `GET`, `POST /v1/members/me/keys` | member (X5 for POST) | `perm.identity.manage_keys` | POST yes |
| `createKeyRevocation` | `POST /v1/members/me/keys/{mky_id}/revocation` | member (X5) | `perm.identity.manage_keys` | yes |
| `createRecoveryKey`, `createRecoveryConfirmation` | `POST /v1/members/me/recovery-keys`, `POST /v1/members/me/recovery-confirmations` | member (X5) | `perm.identity.manage_keys` | yes |
| `createRecovery` | `POST /v1/recoveries` | none | `perm.identity.start_recovery` | yes |
| `createDeviceLinkOffer`, `createDeviceLinkApproval` | `POST /v1/device-link-offers`, `POST /v1/device-link-offers/{dlo_id}/approval` | member (X5) | `perm.identity.link_device` | yes |
| `createDeviceLinkClaim` | `POST /v1/device-link-offers/{dlo_id}/claims` | none | `perm.identity.link_device` (by secret) | no |
| `putMemberEmail`, `deleteMemberEmail` | `PUT`, `DELETE /v1/members/me/email` | member (X5) | `perm.identity.set_email` | yes |
| `closeMember` | `POST /v1/members/me/closure` | member (X5) | `perm.identity.close_account` | yes |
| `createInvite`, `deleteInvite` | `POST /v1/invites`, `DELETE /v1/invites/{inv_id}` | member | `perm.invite.issue`, `perm.invite.revoke_own` | yes |
| `createAdminAuthChallenge`, `createAdminSession` | `POST /v1/admin/auth-challenges`, `POST /v1/admin/sessions` | none | none (WebAuthn) | no |
| `createAdminAction`, `createAdminActionApproval` | `POST /v1/admin/actions`, `POST /v1/admin/actions/{act_id}/approvals` | admin | by action (10.11) | yes |

### 10.18.2 Events and metrics [A]

Events (S0.5 format, stored in the outbox): `member.created`, `member.key_rotated`, `member.key_revoked`, `member.device_linked`, `member.recovered`, `member.recovery_confirmed`, `member.email_set`, `member.email_removed`, `member.closed`, `invite.issued`, `invite.redeemed`, `invite.expired`, `invite.revoked`, `invite.strike_recorded`, `invite.tree_frozen`, `invite.tree_unfrozen`, `session.issued`, `session.revoked`, `device_link.offered`, `device_link.claimed`, `device_link.approved`, `device_link.cancelled`, `device_link.expired`, `admin.signed_in`, `admin.credential_added`, `admin.credential_locked`, `admin_action.proposed`, `admin_action.approved`, `admin_action.executed`, `admin_action.expired`. Events carry `actor` as principal type plus opaque id and never an IP, key or token.

Metrics (no id or IP in any label): `hamyar_identity_registrations_total`, `hamyar_identity_recoveries_total`, `hamyar_identity_recovery_failures_total`, `hamyar_identity_key_chain_invalid_total`, `hamyar_ratelimit_denied_total` (label: scope), `hamyar_session_revocations_total`, `hamyar_admin_pending_approvals_total`. Alarms (`Alarm`): `identity.key_chain_invalid`, `admin.credential_cloned`, a spike in `hamyar_identity_recovery_failures_total`.

### 10.18.3 Parameters this part adds [A]

All are initial configurable defaults, owned by the `operator` role (S0.10.5), public except none (they are not `security.*` secrets), and reported as convention gaps for `S16.*` to complete.

| Name | Type | Initial configurable default | Validation | Replaced by |
| --- | --- | --- | --- | --- |
| `identity.registration_mode` | enum | `invite_only` | `invite_only`, `open` | `FND` |
| `identity.challenge_ttl_s` | duration_s | 60 | 10..600 | `SEC` |
| `identity.max_devices_per_member` | int | 5 | 1..20 | `OPS` |
| `identity.code_max_attempts` | int | 5 | 1..20 | `SEC` |
| `identity.email_code_ttl_s` | duration_s | 900 | 60..3600 | `SEC` |
| `ratelimit.device_link_offers_per_day` | int | 5 | 1..100 | `OPS` |
| `ratelimit.auth_failures_per_hour` | int | 20 per IP hash | 1..1000 | `OPS` |
| `invite.accountability_days` | days | 90 | 1..365 | `SEC` |
| `invite.strike_window_days` | days | 90 | 1..365 | `OPS` |
| `invite.strikes_to_revoke_issuing` | int | 2 | 1..20 | `OPS` |
| `invite.tree_freeze_ban_threshold` | int | 3 | 1..100 | `OPS` |
| `session.step_up_max_age_s` | duration_s | 300 | 30..3600 | `SEC` |
| `session.touch_min_interval_s` | duration_s | 300 | 10..86400 | `OPS` |
| `security.two_person_ttl_s` | duration_s | 86,400 | 600..604800 | `SEC` |
| `security.admin_min_credentials` | int | 2 | 1..5 | `SEC` |
| `retention.sweep_interval_s` | duration_s | 3600 | 60..86400 | `OPS` |

New cross-parameter constraint `C9` [A]: `session.member_abs_ttl_s <= retention.session_days x 86,400`. Changed default (`ISS-102`): `security.two_person_actions` starts as the four of S0.10.6 plus `member.ban`, `invite.seed_issue`, `admin.role_grant`, `admin.credential_add`, `admin.credential_unlock`, `disclosure.release`. Because members cannot be hurt by a tightening, every parameter above follows R10 (tighten at once, loosen with notice).

### 10.18.4 Hooks this part needs from other S10 files [A]

1. Secrets inventory: add `secret.email_enc_key`, `secret.email_index_key` (new) next to `secret.volunteer_handle_key` and `secret.ip_hash_key`; all rotate per `security.secret_rotation_days` and before any public exposure (`security.rotate_before_public_exposure`); a rotation of `secret.email_enc_key` re-encrypts addresses without member action.
2. Threat model: rows for account takeover, de-anonymization, compelled disclosure, fake accounts and invite-tree abuse, insider and operator risk, reviewer capture and DoS must cite 10.8 to 10.15 as their mitigations and keep the residual risks of 10.16.
3. Ban process: define the `reason class` values `credit_farming`, `forgery`, `sybil` used in 10.10, the two-person ban, the appeal path and the effect of `member.banned` on sessions (10.13).
4. Hosting: the requirements of 10.14.2 item 5 (no client IP in host logs; trusted client-address header) and the reachability checks marked [V].

## Issues raised

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-101` | minor | prompt | `S10` is split over several files, so `S10.<m>` numbers can collide, and this file lists identity-relevant columns while `S5.*` owns full schemas | This file owns `S10.1`..`S10.19`, other S10 files start at `S10.20`; `S5.*` wins on column names, this file on meaning; any mismatch is reported at assembly | proposed |
| `ISS-102` | major | FD§3.2, FD§8.3 | The FD makes e-mail optional without saying what it is for, names no account recovery besides the key, and names no admin approval mechanism; a one-person Phase 1 team cannot meet two-person approval | E-mail is for opt-in notices only and never a recovery or login factor; recovery is by key only and no operator can restore access; `security.two_person_actions` is extended (10.12); at least two distinct admins are required before any two-person action, including launch sign-off, can run | needs_owner |
| `ISS-103` | minor | FD§4.6 | `S0.7` gives `Device` the retention class `short` and calls it a keyed-hash record, but `grant.max_per_device` is a lifetime limit and the token is a 128-bit random value that needs only SHA-256 | `Device` is `member_bound` with a residue of `{token_hash, grants_issued}` kept `retention.member_inactive_days` after closure (10.9.1); the hash is plain SHA-256 | proposed |

Convention additions made by this part (not issues, listed so `S0.*` can fold them back): entities `AuthChallenge` (`chl_`), `DeviceLinkOffer` (`dlo_`), `RecoveryRequest` (`rcv_`), `SecurityNotice` (`snt_`); `Invite` states and the events in 10.18.2; `MemberKey` states and the `kind` values; the kill switch `kill.optional_pii`; secrets `secret.email_enc_key` and `secret.email_index_key`; the parameters of 10.18.3 and constraint `C9`; the permission names of 10.11 and the conditions `X1`..`X11`; the copy keys of 10.15.4 and `copy.invite.invalid`, `copy.ratelimit.try_later`, `copy.identity.recovery_limit`, `copy.identity.recovery_typo`, `copy.identity.recovered_elsewhere`.
