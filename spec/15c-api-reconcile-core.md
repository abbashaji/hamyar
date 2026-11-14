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

### 15.B.3.3 Removals and non-endpoints

| Cited path | Verdict and reason | What the citing part does instead |
| --- | --- | --- |
| `/v1/iphash` (10a:578) | REMOVE. The text is the HKDF salt label `'hamyar/v1/iphash'` of the daily IP-hash key, not an endpoint. There is no endpoint that returns, accepts or computes an IP hash: the hash is made once in edge middleware and never leaves the server (S15.1 guarantees; S0 0.6.4). A path-shaped label also trips the path check | Rename the label to `'hamyar:v1:iphash'`, the colon form of the S15 message prefix (Edit 19). Any later cell that keeps the old label must keep it identical wherever it recurs [A] |
| `/v1/recovery` (10a:78, 10a:114) | REMOVE. The text is the HKDF salt label `'hamyar/v1/recovery'` of the recovery seed derivation, not an endpoint (the recovery endpoint is `recoverMember`, `POST /v1/recoveries`) | Rename to `'hamyar:v1:recovery'` (Edit 19) |
| `/v1/recovery-checksum` (10a:110) | REMOVE. The text is the checksum domain label `hamyar/v1/recovery-checksum`, not an endpoint | Rename to `hamyar:v1:recovery-checksum` (Edit 19) |
| `/v1/leases/{lease_id}/validations` | REMOVE. No citing line was found, so the intent is inferred; both plausible intents are served by existing operations. (a) A pre-submit validation of the pasted output: the work order already carries `output.max_chars`, `output.max_bytes` and `output.format` (`WorkOrder`, S15.6.2), so the client checks locally and `submitResult` stores a failing text as a rejection without credit (`reject.length_out_of_bounds`). A server-side dry run would let a volunteer probe the automatic checks and gold comparison, which breaks the indistinguishability of cell kinds (`AC-api-08`) and would make the server read output text that is never stored. (b) A lease-liveness check: `getLease` returns `state`, `expires_at` and `submit_grace_until`, and `issueLeaseNonce` recovers a lost nonce | The citing part replaces the call by a local check against the work order (a) or by `getLease` (b) |

## 15.B.4 Member step-up (X5) for S15 operations

10a (10.13) requires a fresh device-key signature for sensitive member actions; S15a has it only inside `rotateKey` and `recoverMember` and cannot carry it on `DELETE` or body-less `POST` rows. S15b already defines the admin equivalent (15.22.3). This section is the member equivalent, additive to S15a [D][A].

```
Step-Up: <key_id>.<challenge>.<signature>        key_id: id<mky> of an active or retiring device key of the caller; challenge: b64u<32>; signature: b64u<64>
challenge       = createIdentityChallenge { purpose: "step_up", key_id }          single use, valid identity.challenge_ttl_s
request_hash    = "sha256:" + hex(SHA-256(RFC 8785 canonical JSON of { "method": "<M>", "path": "<path as sent>", "body": <body or null> }))
message         = "hamyar:v1:step_up:" + challenge + ":" + request_hash
signature       = Ed25519(device_private_key, message)
```

- **Where checked.** Pipeline step 7 (gates, S15.4), as the first gate, after the idempotency lookup, so a replay of a stored success does not need a second challenge. The challenge is burned by the first verification attempt that finds it. A `pending` key cannot step up.
- **Failure.** Header absent: `401 AUTH_INVALID`, `details.reason` = `step_up_required`. Any other failure (unknown key, key of another member, wrong signature, burned or expired challenge, hash mismatch): the same `401 AUTH_INVALID`, `details.reason` = `step_up_invalid`, after the same work (no oracle). These two reasons already exist for admins (S15b 15.21.1); this section reuses them for `member`. Not stored under the `Idempotency-Key` (step 7 outcomes before step 8 are not stored).
- **Bound to the request.** A stolen bearer token cannot make a sensitive call without the device key, and a captured `Step-Up` header cannot be replayed on another path or body.
- **Secrets.** The header carries no secret that outlives the challenge; access logs never record it (S15.3 rule 5).

| S15a operation | `Step-Up` | Reason |
| --- | --- | --- |
| `createDeviceLink`, `approveDeviceLink` | required | 10a 10.7: adding a device is account control |
| `revokeMemberKey` | required | `DELETE` cannot carry a body proof |
| `setEmail`, `removeEmail` | required | an e-mail address is a de-anonymization vector (S15.5) |
| `revokeAllSessions`, `closeMember`, `confirmRecoveryKey` | required | 15.B.5 |
| `rotateKey` | not needed | its own `signature` and `new_key_proof` are fresher than a header |
| `recoverMember`, `redeemDeviceLink`, `createMember`, `createSession` | not applicable | auth `none`; they carry their own proofs |
| `revokeSession` (one id, including `current`), `createInvite`, `exportMe` and every read | not required | no new access is granted |

## 15.B.5 New member operations

All four are `member`, share the S15.3 request rules and S15.9 error catalogue, and use class `RL-WRITE` unless stated.

### 15.B.5.1 `closeMember`

| Field | Definition |
| --- | --- |
| Method and path | `POST /v1/members/me/closure` |
| Auth | `member`, active only (`suspended` and `banned` members get `403 FORBIDDEN`, reasons `member_suspended`, `member_banned`: closure would erase the subject of a possible appeal), `Step-Up` required |
| Request | `{ acknowledge_forfeit_ucr: ucr, acknowledge_public_records: bool }`; `acknowledge_public_records` must be `true`; `acknowledge_forfeit_ucr` must equal the current `balance_ucr` |
| Response | `200 { closed_at: ts, forfeited_ucr: ucr }` |
| Errors | `400 VALIDATION_FAILED`; `401 AUTH_INVALID` (`step_up_required`, `step_up_invalid`); `403 FORBIDDEN` (`member_suspended`, `member_banned`, `recovery_cooldown`, `details.until`); `409 STATE_CONFLICT` (`open_work` with `details.counts` = `{open_jobs, pending_submissions}`: a job holding escrow or a submission with verdict `pending` blocks closure; `balance_changed` with `details.balance_ucr`) |
| Idempotency-Key | `R`. Natural idempotency: closure is terminal. After success the session is dead, so a replay returns `401 AUTH_INVALID`, reason `credentials_invalid` (closed members cannot authenticate, S15.4); a client that received no response and then gets that `401` treats the closure as done [A] |
| Pagination | none |
| Rate-limit class | `RL-WRITE` |
| Events | `member.closed` with `cause` = `member`, in the same transaction (S0 0.9; S15b 15.34.3) |
| Effects | One transaction: active leases released (cells back to `queued`, `attempt` unchanged); jobs in `draft`, `quoted` or `waitlisted` cancelled; every session revoked; the rows of 10a 10.14.3 deleted; the `Member` row reduced to its opaque `mem_` id. Ledger and provenance rows stay (permanent, no personal data). Remaining credit is not paid out or transferred and its lots lapse under the usual expiry rule; the copy says so and that closure does not rewrite the public ledger [A][V: counsel review of the forfeiture and closure copy `copy.identity.close_forfeit_notice`] |
| Given/When/Then | Given an active member with balance `3000000` ucr, no open jobs and no pending submission, When they call `closeMember` with `acknowledge_forfeit_ucr` `"3000000"` and a valid `Step-Up`, Then `200`, exactly one `member.closed` event exists, and every later request with their token is `401`; the same call with `"2000000"` is `409 balance_changed` and changes nothing |

### 15.B.5.2 `getMemberExport`

| Field | Definition |
| --- | --- |
| Method and path | `GET /v1/members/me/export?section=<section>&limit=&cursor=` |
| Auth | `member` (any status, so a suspended member can still take their data) |
| Request | `section` required, one of the table below; `limit`, `cursor` as S15.11 |
| Response | `200 { section, schema_version: 1, generated_at: ts, data: <object or [T]>, page?: { next_cursor, limit } }`; object sections have no `page` |
| Errors | `400 VALIDATION_FAILED` (`field_invalid` for an unknown `section`; `cursor_invalid`, `cursor_expired`, `limit_out_of_range`) |
| Idempotency-Key | `-` (safe read) |
| Pagination | cursor, in the order of the underlying list operation |
| Rate-limit class | `RL-WRITE` bucket, cost `ratelimit.write_weight`, because one call can read a full page of history [A] |
| Events | none |
| Given/When/Then | Given a member with ledger history, When every section is requested and paged to the end, Then the union contains only rows of that member, contains no session token, nonce, invite code, device-link code or join code, no other member's `mem_` id, no IP address and no e-mail address except the masked own one |

| `section` | Same objects as | Note |
| --- | --- | --- |
| `profile` | `getMe` (`Member`) | object |
| `opt_ins` | `getOptIns` | object |
| `keys`, `devices`, `sessions`, `invites` | `listMemberKeys`, `listDevices`, `listSessions`, `listInvites` | public keys only; no tokens or codes |
| `leases`, `submissions` | `listLeases`, `listSubmissions` | verdicts and hashes, never output text |
| `lots`, `ledger_entries` | `listLots`, `listLedgerEntries` | own account only |
| `jobs`, `reports`, `teams`, `referrals` | `listJobs`, `listReports`, `listTeams`, `listReferrals` | own rows |

Uploads and deliverable content are not exported: they are purged under `retention.job_payload_days` and, while present, fetched with `getJobDeliverableContent`. The export is the member's own data under the same minimization as the rest of the API, not a second, wider read path [D].

### 15.B.5.3 `revokeAllSessions`

| Field | Definition |
| --- | --- |
| Method and path | `POST /v1/members/me/session-revocations` |
| Auth | `member`, any status (a suspended member may revoke sessions, S15.4), `Step-Up` required |
| Request | `{ keep_current?: bool }`, default `false` |
| Response | `200 { revoked_count: int }` |
| Errors | `401 AUTH_INVALID` (`step_up_required`, `step_up_invalid`) |
| Idempotency-Key | `R`; natural idempotency: revocation is monotonic, a repeat with `keep_current` true returns `revoked_count` 0 |
| Pagination | none |
| Rate-limit class | `RL-WRITE` |
| Events | none (the single-session `revokeSession` emits none either). It revokes sessions only; device keys stay valid, and a lost device is handled by `revokeMemberKey` or `revokeDevice` |
| Given/When/Then | Given a member with three live sessions, When one of them calls `revokeAllSessions` with `keep_current` `true` and a valid `Step-Up`, Then `200` with `revoked_count` 2, the other two tokens answer `401 AUTH_INVALID` on their next request and the caller's token still works |

### 15.B.5.4 `confirmRecoveryKey`

| Field | Definition |
| --- | --- |
| Method and path | `POST /v1/members/me/recovery-confirmations` |
| Auth | `member`, `Step-Up` required |
| Request | `{ key_id: id<mky>, challenge: b64u<32>, signature: b64u<64> }`; `challenge` from `createIdentityChallenge` with `purpose` = `confirm_recovery`; `signature` by the recovery key over `"hamyar:v1:confirm_recovery:" + challenge + ":" + key_id` (layout owned by S10, S15.4) |
| Response | `200 { recovery: { confirmed_at: ts } }` |
| Errors | `401 AUTH_INVALID` (`credentials_invalid` for an unknown key, a key that is not this member's recovery key, or a wrong signature, after the same work; `step_up_required`, `step_up_invalid`); `401 AUTH_EXPIRED` (`challenge_expired`); `409 STATE_CONFLICT` (`key_state_invalid`: the recovery key is not `active`) |
| Idempotency-Key | `R`; natural idempotency: an already confirmed key returns the stored `confirmed_at` and emits nothing |
| Pagination | none |
| Rate-limit class | `RL-WRITE` |
| Events | `+member.recovery_confirmed` (convention gap, listed in 15.B.9) |
| Effects | Sets `Member.recovery.confirmed_at`. It proves the member holds the recovery secret without using it; the secret never leaves the device (10a 10.4.3). Confirmation never blocks anything; it changes `rotateKey` of the recovery key (15.B.9) |
| Given/When/Then | Given an active recovery key, When the member signs a fresh `confirm_recovery` challenge with it and calls this operation, Then `200` with `confirmed_at`, one `member.recovery_confirmed` event, and a second identical call (new challenge) returns the same `confirmed_at` and no second event |

## 15.B.6 New job operation: `requestJobQuote`

S15a returns a quote from `submitJobForScreening` and reads it with `getJobQuote`; the only way to change the window is to copy the job. 06b (6.28) defines a requester counter-offer (a later or earlier window) that S15 lacks, and the copy route loses the job's stamp and its place. This operation adds it [D].

| Field | Definition |
| --- | --- |
| op | `requestJobQuote` |
| Method and path | `POST /v1/jobs/{job_id}/quotes` |
| Auth | `member` (the requester of the job; another member's job is `404 NOT_FOUND`) |
| Request | `{ requested_window_s?: dur_s }`, within `admission.min_window_s` .. `admission.max_window_days` x 86,400 (`400 VALIDATION_FAILED`, code `range`); omitted means the job's `window_preference_s` |
| Response | `200 Job` (S15.7.2) with a new `quote`: same arithmetic as S15.7.2, new `quote_hash` and `expires_at = now + price.quote_ttl_s`. The window is never shorter than `requested_window_s` and never an instant-completion promise (FD Principle 10); if no window up to `admission.max_window_days` fits, the job becomes `waitlisted` exactly as in `submitJobForScreening` |
| Errors | `409 STATE_CONFLICT` (`job_state_invalid`: only a `quoted` job can be re-quoted; a `waitlisted` job is re-quoted by the system); `422 CAP_EXCEEDED` (`waitlist_limit`: the re-quote would waitlist the job and the member is at `admission.waitlist_max_per_member`; the job stays `quoted` with its old quote); `422 POLICY_REJECTED` (`details.reasons` = `policy.R9.policy_version_stale` when the stamped policy no longer passes; job unchanged); `403 LAUNCH_GATE_CLOSED` (`launch.member_jobs_enabled`); `503 KILL_SWITCH_ENGAGED` (`kill.all_new_jobs`, `kill.template.<tpl_id>`) |
| Idempotency-Key | `R`. Natural idempotency: the same `requested_window_s` while the current quote is unexpired returns the current quote unchanged |
| Pagination | none |
| Rate-limit class | `RL-WRITE` |
| Events | none while the job stays `quoted` (a new `Quote` version is not a state change); `job.waitlisted` when it becomes `waitlisted`. The superseded quote can no longer be confirmed: `confirmJob` with its hash is `409 STATE_CONFLICT`, reason `quote_changed` |
| Given/When/Then | Given a `quoted` job with a 172,800 s window, When the requester calls `requestJobQuote` with `requested_window_s` 345,600, Then `200` with a new quote whose `window_s` is at least 345,600 and whose `quote_hash` differs, and `confirmJob` with the old hash is `409 quote_changed` |

## 15.B.7 New admin operations: the human screening queue

07 (7.12.4, 7.15.4) names `listScreeningQueue` and `decideScreening`; S15a says a `flagged` upload, and a share `screen.review_rate_new_requester` or `screen.review_rate_established_requester` of all inputs, wait for a reviewer after `submitJobForScreening` (job state `screening`, `202`), but S15b has no queue to drain it. Without it a job in `screening` can never leave that state, so the operations are NEW and belong to S15b's admin surface [D].

```
ScreeningItem { job_id: id<job>, state: "pending"/"decided", held_at: ts, due_at: ts,
                hold_reasons: [ "flagged_input"/"sampled_review" ],
                template: { id: id<tpl>, version_id: id<tpv>, name: text<80>, job_type: enum<job_type> },
                cell_count: int, declarations: Declarations,
                findings: [ { code: string, count: int, lines: [int] } ],      codes of S15.7.1; counts and line numbers, never matched text
                decision: { decision: "pass"/"reject", decided_at: ts }/null }
```

`due_at = held_at + screen.review_sla_s` (the parameter 07 already uses for its queue alarm). No item carries a `mem_` id, a handle or any requester attribute: the reviewer judges the content and the declarations, not the person (FD§5.7 failure mode 10). Permissions are proposals for S10 [A]: `perm.screening.read` (list, item) and `perm.screening.decide` (content, decision); default holder: reviewer.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listScreeningQueue` | `GET /v1/admin/screening` | `admin` `perm.screening.read` | `?state` (default `pending`), `?job_type`, `?overdue=true` | list of `ScreeningItem` without `declarations` and `findings`, oldest `held_at` first | - | n/a | cursor | `A-R` |
| `getScreeningItem` | `GET /v1/admin/screening/{job_id}` | `admin` `perm.screening.read` | - | `ScreeningItem` | `NOT_FOUND` | n/a | - | `A-R` |
| `getScreeningContent` | `GET /v1/admin/screening/{job_id}/content` | `admin` `perm.screening.decide` | - | `{ inputs: object, uploads: [{ upload_id, content: string }], glossary: { entries: [{source, target}] }/null }`; strings are data, escaped by the client (S9.* rule); logged as a read `AdminAction` (S15b 15.21.3 rule 3) | `NOT_FOUND` | n/a | - | `A-W` |
| `decideScreening` | `POST /v1/admin/screening/{job_id}/decision` | `admin` `perm.screening.decide` | `{ decision: "pass"/"reject", prohibited_category?: text<40>, reason: text<2000> }`; `prohibited_category` only with `reject` | 200 `{ item: ScreeningItem, job_state: "quoted"/"waitlisted"/"draft"/"rejected" }` | `STATE_CONFLICT` (`not_pending`), `NOT_FOUND`, `VALIDATION_FAILED` | req | - | `A-W` |

**Behavior of `decideScreening`** [D]. `pass`: the job continues exactly as after an automatic pass: price, admission, then `quoted` or `waitlisted` (events `job.policy_passed`, `job.waitlisted`). If the pass would waitlist the job while the member is at `admission.waitlist_max_per_member`, the decision is recorded, the job returns to `draft`, nothing is stamped and the inbox shows `copy.job.waitlist_limit` (the same outcome as `CAP_EXCEEDED` `waitlist_limit` in S15.7.2). `reject`: the job is `rejected` (terminal) with reason `policy.R3.reviewer_rejected`, or `policy.R3.prohibited_category` when `prohibited_category` is given (event `job.policy_rejected`); a rejection tightens, so one reviewer suffices. `reason` is stored, never shown to the member; the member sees only the `copy_key` of the reason code. One `AdminAction` is written in the same transaction, and a failed insert fails the decision (S15b 15.21.3 rule 1). A decision is final for the job; a mistaken `pass` is corrected by the kill switches and policy tools of S15b, not by editing a decision. Idempotency: `req`; a repeat with the same body returns the stored result, a second decision with another body is `409 not_pending`.

**Given/When/Then** [D]. Given a job in `screening` held 100 s ago with a flagged upload, When a reviewer with `perm.screening.decide` reads the content and calls `decideScreening` with `reject` and `prohibited_category` `"malware"`, Then the job is `rejected` with `policy.R3.prohibited_category`, `job.policy_rejected` is emitted once, two `AdminAction` rows exist (one `read`, one `write`), and a reviewer who holds only `perm.screening.read` gets `403 FORBIDDEN` on the content call and no `read` row.

## 15.B.8 New public operations

Public means `auth` `none`, no cookies, no identifier, class `PUB`, the rules of S15b 15.33.1 (`ETag`, `If-None-Match`, `Cache-Control: public, max-age` at most `public.counter_refresh_s`, CORS without credentials, small-number suppression as `null` with `suppressed: true`), and no feature flag: policy, capacity and health are always on [D].

### 15.B.8.1 `getPublicPolicy`

| Field | Definition |
| --- | --- |
| Method and path | `GET /v1/public/policy` (cited as `GET /v1/policy` in 07 and `GET /v1/policy-versions/current` in 11b; public endpoints live under `/v1/public/*`, S0 0.11.2) |
| Auth | `none` |
| Request | none |
| Response | `200 { as_of: ts, data: [ { policy: { id: id<pol>, name: text<80> }, active: PolicyVersionPublic, scheduled: [PolicyVersionPublic] } ] }` |
| Errors | universal only |
| Idempotency-Key | `-` |
| Pagination | none (a handful of policy profiles) |
| Rate-limit class | `PUB` |
| Events | none |
| Given/When/Then | Given an active version 5 and a scheduled loosening version 6 whose notice period has not ended, When anyone calls the endpoint, Then `active.version` is 5, `scheduled` holds version 6 with its `effective_from`, the allowlist rows carry `allowed` or `locked`, no rule carries its `params`, and there is no `Set-Cookie` |

```
PolicyVersionPublic { id: id<plv>, version: int, change_class: "tighten"/"loosen"/"neutral", effective_from: ts, content_hash: hash,
                      changelog_entry_id: id<chg>/null,
                      rules: [ { policy_rule_id: "R1".."R10", slug: text<40>, enabled: bool, summary_key: copy_key } ],
                      allowlist: [ { purpose, license, sensitivity, service_requirement: enums of S0 0.8.1, status: "allowed"/"locked" } ] }
```

Rule `params` are not published here: several are screening thresholds that help an attacker tune an input just under a limit, and every parameter S0 marks public is already served by `listPublicParameters`. The allowlist is what the requester wizard needs (it replaces `getPolicyProfile` of 11b), and the history of versions is the public change log, not this endpoint [D].

### 15.B.8.2 `getPublicCapacity`

| Field | Definition |
| --- | --- |
| Method and path | `GET /v1/public/capacity` |
| Auth | `none` |
| Request | none |
| Response | `200 { as_of: ts, categories: [ { category_key: text<40>, eligible_donors: int/null, forecast_cells_per_day: int/null, committed_share_ppm: ppm/null, suppressed: bool } ] }`; one entry per `category_key` of S6 (6.25) and one with `category_key` = `ALL` |
| Errors | universal only |
| Idempotency-Key | `-` |
| Pagination | none |
| Rate-limit class | `PUB` |
| Events | none |
| Suppression | With `n` eligible donors and `k` = `analytics.min_cohort_k`: `n >= k` gives `eligible_donors = floor(n / k) x k` (a bucket, never the exact count) and the two other figures; `n < k` gives all three `null` and `suppressed` `true`. No member id, handle or location appears. 06b's string `"<k"` is replaced by `null` with `suppressed: true`, the one suppression form of S15b, so clients parse one shape [D] |
| Given/When/Then | Given a category with 7 eligible donors and `analytics.min_cohort_k` 10, When anyone calls the endpoint, Then that category has `eligible_donors` `null`, `forecast_cells_per_day` `null`, `committed_share_ppm` `null` and `suppressed` `true`; with 23 donors `eligible_donors` is 20 |

The exact figures, the history and the forecast error stay in the admin `getCapacitySnapshot` and `listCapacityDays`; the category forecast itself is S6's [A].

### 15.B.8.3 `getPublicHealth`

| Field | Definition |
| --- | --- |
| Method and path | `GET /v1/public/health` |
| Auth | `none` |
| Request | none |
| Response | `200 { status: "ok", build_id: text<64>, api_revision: int, as_of: ts }`; `build_id` is an opaque release identifier chosen by the build (04.11) [A]; `api_revision` equals the `Api-Revision` header (S15.13) |
| Errors | none from the application; an unreachable host is the edge's failure, outside the API |
| Idempotency-Key | `-` |
| Pagination | none |
| Rate-limit class | `PUB` |
| Events | none |
| Semantics | Liveness only: answering means the process serves requests. It does not touch the transactional store (readiness is read from `getLedgerHead`, `getCapacitySnapshot` and `listAlarms` of S15b, see Edit 24). `Cache-Control: no-store` (a probe must not be answered by a cache); CORS allows any origin without credentials so the static front end and the G2 reachability measurement (04.15.2) can call it from another origin |
| Given/When/Then | Given a healthy deployment, When a client without credentials calls it, Then `200` with exactly the four keys above, no `Set-Cookie`, `Cache-Control: no-store`, and no IP address appears in any log line it produced (`AC-privacy-01`) |

S15b 15.33.1 rule 9 says `/v1/health` "is defined in part a and BM0"; part a defines no health endpoint and BM0 serves `/v1/public/health` (S0 0.12). This section is the definition; the path `/v1/health` does not exist (Edit 25) [D].

## 15.B.9 Additive overlay of S15a and S15b objects

Each item is additive in the sense of S15.13 and is needed by an alias or a new operation above; this file is authoritative until the owner of S15a or S15b merges it. None renames anything [D].

| Object or operation | Addition | Needed by |
| --- | --- | --- |
| `createIdentityChallenge.purpose` | two more values: `step_up`, `confirm_recovery` | 15.B.4, `confirmRecoveryKey` |
| `Key` | `authorized_by_key_id: id<mky>/null`, `authorization_signature: b64u<64>/null`, `alg: "ed25519"` (the first two keys are self-signed, keys added by recovery are signed by the recovery key, 10a 10.7) | key chain on `listMemberKeys` |
| `Member.recovery` | `confirmed_at: ts/null` | `confirmRecoveryKey` |
| `rotateKey` request | optional `recovery_signature: b64u<64>`, by the current active recovery key over the same message as `signature` (same challenge, subject `new_public_key`); required when `kind` = `recovery` and `recovery.confirmed_at` is not null (`400 VALIDATION_FAILED`, reason `missing_field`); wrong: `401 AUTH_INVALID`, `credentials_invalid` | recovery-key rotation |
| `recoverMember` request and response | request adds required `new_recovery_public_key: b64u<32>` and `new_recovery_proof: b64u<64>`; response adds `recovery_key: Key`; the recovery key that was just typed is revoked in the same transaction. Found while reading 10a:228: S15a leaves the typed recovery key `active` after a recovery, although it was entered on a device that may be hostile; 10a 10.4.4 already requires the replacement and the cost is one more field [D] | recovery safety |
| `createMember`, `redeemDeviceLink`, `recoverMember` requests | optional `platform_class: text<24>`, `key_storage: text<24>` (values owned by S10; they become S0 enums when S10 fixes them); `Device` gains `platform_class: text<24>/null`, shown only to the approving device | 10a registration and linking |
| Field-name map, 10a to S15a | `device_pub` to `public_key` (`createMember`) or `new_public_key` (`rotateKey`, `redeemDeviceLink`, `recoverMember`); `recovery_pub` to `recovery_public_key`; `device_signature` to `proof`; `recovery_signature` of `createMember` to `recovery_proof`; `new_device_pub` to `new_public_key`; `challenge_id` to `challenge`; `link_secret` to `code`; `offer_id` to `device_id` | every 10a pseudocode block |
| `listSupplyGauges` | optional filter `topic_category_id` and bucket field `topic_category_id: id<top>/null` (07's optin axis) | 07 gauge |
| S15.4 pipeline step 7 | first gate: `Step-Up` check of 15.B.4 for the operations listed there | member step-up |
| Error reasons (append-only, `details.reason`) | `STATE_CONFLICT`: `open_work`, `balance_changed`; `AUTH_INVALID`: `step_up_required`, `step_up_invalid` on member routes | 15.B.4, `closeMember` |
| Events | `+member.recovery_confirmed` (producer `identity_svc`, consumer `analytics`) | `confirmRecoveryKey` |
| Permissions (S10 owns the matrix) | `perm.screening.read`, `perm.screening.decide` | 15.B.7 |
| Copy keys | `copy.identity.close_forfeit_notice`, `copy.job.waitlist_limit` (text owned by S11) | `closeMember`, `decideScreening` |
| S15b 15.33.1 rule 6 | the always-on public endpoints now include policy, capacity and health | 15.B.8 |

No new parameter name is introduced by this file; every limit named above (`screen.review_sla_s`, `analytics.min_cohort_k`, `public.counter_refresh_s`, `ratelimit.write_weight`, `admission.waitlist_max_per_member`, `admission.min_window_s`, `admission.max_window_days`, `price.quote_ttl_s`, `identity.challenge_ttl_s`, `identity.key_rotation_grace_s`, `retention.job_payload_days`) is already used by S15a, S15b, 06b or 07 and is to be confirmed against S0 0.10 and S16* by `check_params` [A].
