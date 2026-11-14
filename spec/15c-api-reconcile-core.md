# 15.B API reconciliation (core: identity, leases, jobs, policy, result return)

*Spec part 15c, third file of S15 · owner cell C-037 · audit of the parts 04, 06b, 07, 10a and 11b against `15a-api-core.md` (S15a) and `15b-api-admin.md` (S15b). Written against `spec/00-conventions.md` (S0). Nothing here has been verified against any provider's terms or any law; every provider-dependent value stays configuration data entered by a reviewer [V].*

## 15.B.1 Method, verdicts and rules

**Method** [D]. Each `/v1` path cited by a part but not defined by S15a or S15b was read in its citing context (about 12 lines around the citation) and compared with the nearest S15 operation. S15 is canonical (ground rule of the audit round): a citing part never wins by existing first. Existing S15 ids, paths, parameter names, states and error codes are not renamed anywhere in this file. Where this file adds a field, a reason or a purpose to an S15 object it does so additively (S15.13: new optional request fields, new response fields and new `details.reason` values stay in `v1`) and says so in 15.B.9.

| Verdict | Meaning | What the citing part must do |
| --- | --- | --- |
| ALIAS | The cited path means an existing S15 operation | Replace the cited path (and, where listed, the shape) by the S15 one |
| NEW | S15 has no equivalent and the capability is wanted | Keep the operation; it is defined in this file (15.B.5 to 15.B.8) and is part of S15 from here on |
| REMOVE | The cited use is not an endpoint, duplicates one, or must not exist | Replace as stated in 15.B.3 |

**Rules every NEW operation obeys** [D]. (1) Member and admin auth stay separate: no endpoint accepts both schemes, and an admin token on a member route is `401 AUTH_INVALID`, reason `wrong_scheme` (S15.4). (2) No endpoint reads a volunteer's provider page, stores a provider credential or session, or accepts a chat link (ground rule 2; S15.1). (3) Every state-changing operation has natural idempotency underneath and takes `Idempotency-Key` as stated in its card. (4) Minimal data: responses carry no other member's `mem_` id, no `vol_` handle toward a requester, no IP address and no e-mail address except the caller's own, masked. (5) New `details.reason` strings are append-only vocabulary under existing S0 0.11.3 codes; no new top-level error code is invented. (6) No new parameter name is introduced: every limit below reuses a parameter that S0, S15a or S15b already names. (7) A cited path is kept for a NEW operation unless it breaks an S15 surface rule (public endpoints live under `/v1/public/*`).

## 15.B.2 Verdict table (every cited path)

| Cited path | Verdict | S15 operation or this file's operation |
| --- | --- | --- |
| `/v1/admin/actions/{act_id}/approvals` | ALIAS | `approveApproval` |
| `/v1/admin/auth-challenges` | ALIAS | `startAdminLogin` |
| `/v1/admin/screening` | NEW | `listScreeningQueue` (15.B.7) |
| `/v1/admin/screening/{job_id}/decision` | NEW | `decideScreening` (15.B.7) |
| `/v1/admin/supply-gauge` | ALIAS | `listSupplyGauges` |
| `/v1/auth-challenges` | ALIAS | `createIdentityChallenge` |
| `/v1/device-link-offers` | ALIAS | `createDeviceLink` |
| `/v1/device-link-offers/{offer_id}/approval` | ALIAS | `approveDeviceLink` |
| `/v1/device-link-offers/{offer_id}/claims` | ALIAS | `redeemDeviceLink` |
| `/v1/iphash` | REMOVE | not an endpoint: a hash-derivation label |
| `/v1/jobs/{job_id}/confirmation` | ALIAS | `confirmJob` |
| `/v1/jobs/{job_id}/quotes` | NEW | `requestJobQuote` (15.B.6) |
| `/v1/leases/{lease_id}/extension` | ALIAS | `extendLease` |
| `/v1/leases/{lease_id}/nonce-rotations` | ALIAS | `issueLeaseNonce` |
| `/v1/leases/{lease_id}/validations` | REMOVE | no such capability (15.B.3) |
| `/v1/me/opt-ins` | ALIAS | `getOptIns`, `replaceOptIns` |
| `/v1/members/me/closure` | NEW | `closeMember` (15.B.5) |
| `/v1/members/me/export` | NEW | `getMemberExport` (15.B.5) |
| `/v1/members/me/keys` | ALIAS | `listMemberKeys` (GET), `rotateKey` (POST) |
| `/v1/members/me/keys/{key_id}/revocation` | ALIAS | `revokeMemberKey` |
| `/v1/members/me/recovery-confirmations` | NEW | `confirmRecoveryKey` (15.B.5) |
| `/v1/members/me/recovery-keys` | ALIAS | `rotateKey` with `kind` = `recovery` |
| `/v1/members/me/session-revocations` | NEW | `revokeAllSessions` (15.B.5) |
| `/v1/policy` | NEW | `getPublicPolicy` at `/v1/public/policy` (15.B.8) |
| `/v1/policy-previews` | ALIAS | `checkJobPolicy` |
| `/v1/public/capacity` | NEW | `getPublicCapacity` (15.B.8) |
| `/v1/public/health` | NEW | `getPublicHealth` (15.B.8) |
| `/v1/recovery` | REMOVE | not an endpoint: a key-derivation label |
| `/v1/recovery-checksum` | REMOVE | not an endpoint: a checksum label |

## 15.B.3 Aliases: cited path, S15 endpoint, difference

Every difference below is resolved in favor of S15 unless the row says that S15 gains an additive field (15.B.9). "Edit" refers to the numbered list at the end of this file.

### 15.B.3.1 Identity

| Cited path | S15 endpoint | Difference and resolution |
| --- | --- | --- |
| `POST /v1/auth-challenges` (10a:69, 10a:79, 10a:228) | `createIdentityChallenge`, `POST /v1/identity-challenges`, auth `none`, `RL-BOOT` | 10a returns `{challenge_id, nonce, expires_at}` and has 13 purposes bound to `audience` and `context_hash`; S15 returns `{challenge, expires_at}` (one 256-bit single-use value) and 5 purposes. Resolution [D]: S15 shape wins; the pair `challenge_id` + `nonce` collapses to the single `challenge`; the byte layout of the signed message stays owned by S10 (S15.4) and may bind origin and body hash, but the field names are S15's. Purposes map as `register_device`, `register_recovery` to `create`; `session` to `session`; `rotate_device_key`, `rotate_recovery_key` to `rotate`; `link_claim` to `device_link`; `recover` to `recover`. `step_up`, `revoke_key`, `set_email`, `close_account`, `link_approve` become the single purpose `step_up` and `confirm_recovery` stays `confirm_recovery`: both are additive purposes (15.B.4, 15.B.9). Edits 1 to 3 |
| `POST /v1/admin/auth-challenges` (10a:479, 10a:727) | `startAdminLogin`, `POST /v1/admin/auth/challenges`, auth `none`, `A-AUTH` | Path differs by one segment. 10a returns a bare `{challenge}` valid `identity.challenge_ttl_s`; S15b returns `{challenge_id, public_key_options, expires_at}` valid `session.admin_stepup_ttl_s`, and `createAdminSession` takes `{challenge_id, assertion}`. S15b wins (WebAuthn needs `public_key_options`). Edits 4, 5 |
| `POST /v1/admin/actions/{act_id}/approvals` | `approveApproval`, `POST /v1/admin/approvals/{apv_id}/approvals`, `admin` `SU` `perm.approval.decide`, `A-W` | 10a models a generic proposed action (`act_`, `POST /v1/admin/actions`, events `admin_action.*`). S15b has no generic propose endpoint: a two-person action is started by the concrete operation (for example `banMember`) which answers `202` with an `AdminApproval` (`apv_`); `act_` is the audit row (`AdminAction`). So `approvals` is an alias of `approveApproval`, and `POST /v1/admin/actions` has no equivalent and is REMOVED (a generic "propose anything" endpoint would bypass the per-operation guards of 15.22.4). Events `admin_action.proposed`, `.approved`, `.executed`, `.expired` map to `admin.approval_requested`, `admin.approval_granted`, the original operation's own event, `admin.approval_expired`. Edit 6 |
| `POST /v1/device-link-offers` (10a:194, 10a:199, 10a:205, 10a:722) | `createDeviceLink`, `POST /v1/device-links`, `member`, `R`, `RL-WRITE` | 10a `offer_id` (`dlo_`) is S15 `device_id` (`dev_`); 10a `link_secret` (128 bits, 26-character Crockford) is S15 `code` (`text<32>`, shown once). Offer states map `open` to `pending`, `claimed` to `awaiting_approval`, `approved` to `linked`, `cancelled` to `denied`, `expired` to `expired`. Step-up: 10a requires it; S15a is silent; this file adds it (15.B.4, table row `createDeviceLink`). One open offer per member and `ratelimit.device_link_offers_per_day` are guards of S10, not of the path. Edits 7, 8 |
| `POST /v1/device-link-offers/{offer_id}/claims` (10a:199, 10a:723) | `redeemDeviceLink`, `POST /v1/device-links/redemptions`, auth `none`, `R`, `RL-BOOT` | S15 addresses the offer by the code alone, not by id, so a wrong-secret attempt cannot be counted per offer (10a `identity.code_max_attempts`); the code is consumed by the first redemption that finds it and an unknown, expired or consumed code is the same `404 NOT_FOUND`. Guessing a 128-bit secret is infeasible and `RL-BOOT` bounds noise per IP hash and device hash [D]. 10a sends `platform_class` and `key_storage`; S15 is strict about unknown fields, so both become optional request fields (15.B.9). Edit 8 |
| `POST /v1/device-link-offers/{offer_id}/approval` (10a:205, 10a:722) | `approveDeviceLink`, `POST /v1/device-links/{device_id}/approval`, `member`, `R`, `RL-WRITE` | 10a binds the approval to a signature over `offer_id` and `claimed_key_hash`; S15 takes `{sas}`. The `Step-Up` header (15.B.4) signs the request hash, which covers the path (`device_id`) and the body (`sas`); the SAS is derived from the code and the new key, so the claimed key is covered. No further field is needed. Edit 8 |
| `GET /v1/members/me/keys` (10a:222, 10a:718) | `listMemberKeys`, `GET /v1/member-keys`, `member`, `RL-READ`, `Page<Key>` | 10a returns the key chain (each key with the key that authorized it and that signature, 10.7); S15 `Key` has neither. `Key` gains `authorized_by_key_id`, `authorization_signature` and `alg` (15.B.9). Edits 9, 11 |
| `POST /v1/members/me/keys` (10a:167, 10a:718) | `rotateKey`, `POST /v1/member-keys/rotations`, `member`, `R`, `RL-WRITE` | 10a body `{device_pub, replaces_key_id}` signed by the old key and by the new key; S15 body `{kind, key_id, challenge, signature, new_public_key, new_key_proof}` is the same two proofs with a fresh challenge. The state outcome is identical (new key `active`, old key `retiring` for `identity.key_rotation_grace_s`). The signature already is a step-up, so the `Step-Up` header is not also required on this operation. Edits 10, 11 |
| `POST /v1/members/me/keys/{key_id}/revocation` (10a:719) | `revokeMemberKey`, `DELETE /v1/member-keys/{key_id}`, `member`, `R`, `RL-WRITE` | Same effect (revoke now, end bound sessions, refuse the last active device key). S15 uses `DELETE` with no body, which cannot carry a signature; the 10a requirement of a step-up is met by the `Step-Up` header (15.B.4). Edit 12 |
| `POST /v1/members/me/recovery-keys` (10a:720) | `rotateKey` with `kind` = `recovery` | 10a 10.4.4: replace the recovery key by a device-key step-up, and when the old recovery key was ever confirmed also by a signature of that key; the new key is `active` at once. S15: the new recovery key is `pending` and becomes `active` after `identity.key_rotation_grace_s`, both work during the grace, and the signature is that of an active device key. Resolution [D]: S15's `pending` timing wins (a stolen unlocked phone must not silently replace the recovery key, S15.5); `rotateKey` gains an optional `recovery_signature` that is required when `recovery.confirmed_at` is not null, which carries the 10a rule "confirmed: also sign with the current recovery key" (15.B.9). Edits 13, 14 |
| `GET /v1/members/me/opt-ins`, `PUT /v1/members/me/opt-ins` (07:1065, `/v1/me/opt-ins`) | `getOptIns`, `replaceOptIns`, `GET`, `PUT /v1/members/me/opt-ins`, `member`, `RL-READ` and `RL-WRITE`, `ETag` = `row_version` | Prefix only (`/me/` versus `/members/me/`). 07 calls the write `setOptIns`; the S15 op id is `replaceOptIns`. 07 says "grants need the acknowledgement": S15 rule is that `P2` and `P3` need an explicit value and that `S2` and `S3` are never accepted (`400 VALIDATION_FAILED`, reason `option_not_selectable`); an explicit value is the acknowledgement. Edit 15 |

### 15.B.3.2 Leases, jobs, policy, admin

| Cited path | S15 endpoint | Difference and resolution |
| --- | --- | --- |
| `POST /v1/leases/{lease_id}/extension` | `extendLease`, `POST /v1/leases/{lease_id}/extensions`, `member`, `R`, `RL-WRITE` | Plural segment only. Wherever cited, replace |
| `POST /v1/leases/{lease_id}/nonce-rotations` | `issueLeaseNonce`, `POST /v1/leases/{lease_id}/nonces`, `member`, `R`, `RL-WRITE` | Same meaning (a lost nonce is re-issued and the previous one invalidated, S15.6.2). Wherever cited, replace |
| `POST /v1/jobs/{job_id}/confirmation` (06b:523) | `confirmJob`, `POST /v1/jobs/{job_id}/confirmations`, `member`, `R`, `RL-WRITE` | Plural segment. 06b body `{quote_seq}`; S15 body `{quote_hash, reservation_id?}` (the quote is identified by `quote_hash`; S15 `Quote` has no sequence number). Errors agree (`422 NO_CAPACITY` with `details.requote`, `422 INSUFFICIENT_CREDIT`, `409 STATE_CONFLICT` for `quote_expired` and `quote_changed`). Edit 18 |
| `POST /v1/policy-previews` (07:1062) | `checkJobPolicy`, `POST /v1/jobs/{job_id}/policy-checks`, `member`, `O`, `RL-WRITE` | 07 describes a dry run with no state change that returns the first failing rule. S15 is the same dry run but job-bound (the declarations live on a `draft` job; `createJob` is cheap and idempotent) and reports every failing rule, not only the first; the real evaluation at `submitJobForScreening` still rejects at the first failure (S15.7.2). Not to be confused with the admin `previewPolicyChange`. Edit 16 |
| `GET /v1/admin/supply-gauge` (07:1070) | `listSupplyGauges`, `GET /v1/admin/capacity/supply-gauges`, `admin` `perm.capacity.read`, `A-R`, cursor | 07 and 06b say the admin view shows exact counts; S15b suppresses any bucket below `analytics.min_cohort_k` donors (`donors: null`, `suppressed: true`) even for admins, so the dashboard cannot single out a donor. S15b wins; exact totals remain in `getCapacitySnapshot` (`active_donors`). 06b's `category_key` (and `ALL`) is not an S15b field: S15b buckets are the cross product of `purpose`, `sensitivity`, `license`, `service_id`; `topic_category_id` is added as an optional filter and bucket field (15.B.9). Edit 17 |

## 15.B.4 Removals and non-endpoints

| Cited path | Verdict and reason | What the citing part does instead |
| --- | --- | --- |
| `/v1/iphash` (10a:578) | REMOVE. The text is the HKDF salt label `'hamyar/v1/iphash'` of the daily IP-hash key, not an endpoint. There is no endpoint that returns, accepts or computes an IP hash: the hash is made once in edge middleware and never leaves the server (S15.1 guarantees; S0 0.6.4). A path-shaped label also trips the path check | Rename the label to `'hamyar:v1:iphash'`, the colon form of the S15 message prefix (Edit 19). Any later cell that keeps the old label must keep it identical wherever it recurs [A] |
| `/v1/recovery` (10a:78, 10a:114) | REMOVE. The text is the HKDF salt label `'hamyar/v1/recovery'` of the recovery seed derivation, not an endpoint (the recovery endpoint is `recoverMember`, `POST /v1/recoveries`) | Rename to `'hamyar:v1:recovery'` (Edit 19) |
| `/v1/recovery-checksum` (10a:110) | REMOVE. The text is the checksum domain label `hamyar/v1/recovery-checksum`, not an endpoint | Rename to `hamyar:v1:recovery-checksum` (Edit 19) |
| `/v1/leases/{lease_id}/validations` | REMOVE. No citing line was found, so the intent is inferred; both plausible intents are served by existing operations. (a) A pre-submit validation of the pasted output: the work order already carries `output.max_chars`, `output.max_bytes` and `output.format` (`WorkOrder`, S15.6.2), so the client checks locally and `submitResult` stores a failing text as a rejection without credit (`reject.length_out_of_bounds`). A server-side dry run would let a volunteer probe the automatic checks and gold comparison, which breaks the indistinguishability of cell kinds (`AC-api-08`) and would make the server read output text that is never stored. (b) A lease-liveness check: `getLease` returns `state`, `expires_at` and `submit_grace_until`, and `issueLeaseNonce` recovers a lost nonce | The citing part replaces the call by a local check against the work order (a) or by `getLease` (b) |
