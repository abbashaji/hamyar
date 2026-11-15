# FIX-05: apply API reconciliation to 10a identity

*Cell C-076. Source of the edits: `spec/15c-api-reconcile-core.md`, section 'Edits required in citing parts', edits 1 to 14, 19 and 26, plus the ALIAS and REMOVE rows of its verdict table for every path cited in `spec/10a-identity.md`. Only `spec/10a-identity.md` was edited. Lines are those of the file after the edits (the file went from 777 to 776 lines because one table row was dropped in edit 8; every other cited line did not move). Nothing was executed; CI runs the acceptance scripts. No edit needed an owner decision, so no `default-pending` mark is used: none of D-01..D-22 of `docs/audit/FINAL.md` section 4 governs a text changed here.*

## Edits

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| 1a | spec/10a-identity.md:63 | signed message carried `challenge_id`, a zero byte, `nonce` and `context_hash` | carries `challenge`, a zero byte and `context_hash` | applied |
| 1b | spec/10a-identity.md:67 | 13 purposes (`register_device` to `close_account`) | 7 purposes `create`, `session`, `rotate`, `recover`, `device_link`, `step_up`, `confirm_recovery`, with a pointer to S15.B.3.1 and the `Step-Up` header of S15.B.4 | applied |
| 1c | spec/10a-identity.md:69 | `POST /v1/auth-challenges` returns `{challenge_id, nonce, expires_at}`, nonce of 128 bits | `POST /v1/identity-challenges` returns `{challenge, expires_at}`, challenge of 256 bits | applied |
| 2 | spec/10a-identity.md:79-84 | challenge call `auth-challenges` with purpose `register_device`; body fields `device_pub`, `recovery_pub`; `challenge_id`, `device_signature`, `recovery_signature`; purposes `register_device` and `register_recovery` in `sig_input` | `identity-challenges` with purpose `create`; `public_key`, `recovery_public_key`; `challenge`, `proof`, `recovery_proof`; both `sig_input` calls use `create` | applied |
| 3a | spec/10a-identity.md:228-232 | recovery challenge via `auth-challenges`; body `recovery_pub`, `new_device_pub`, `new_recovery_pub`; `challenge_id`; `device_signature`, `new_recovery_signature` | `identity-challenges`; `recovery_public_key`, `new_public_key`, `new_recovery_public_key`; `challenge`; `proof`, `new_recovery_proof`. The name `recovery_signature` (old recovery key) is kept: the 15c map gives no S15 name for it in `recoverMember` | applied |
| 3b | spec/10a-identity.md:712 | `createAuthChallenge` at `POST /v1/auth-challenges` | `createIdentityChallenge` at `POST /v1/identity-challenges` | applied |
| 4a | spec/10a-identity.md:479 | admin sign-in `POST /v1/admin/auth-challenges` returns a bare `challenge`, ttl `identity.challenge_ttl_s` | `POST /v1/admin/auth/challenges` returns `{challenge_id, public_key_options, expires_at}`, ttl `session.admin_stepup_ttl_s` | applied |
| 4b | spec/10a-identity.md:480 | `POST /v1/admin/sessions {assertion}` | `POST /v1/admin/sessions {challenge_id, assertion}` | applied |
| 5 | spec/10a-identity.md:727 | `createAdminAuthChallenge`, `createAdminSession` at `/v1/admin/auth-challenges` | `startAdminLogin`, `createAdminSession` at `/v1/admin/auth/challenges` | applied |
| 6a | spec/10a-identity.md:728 | `createAdminAction` and `createAdminActionApproval` at `/v1/admin/actions` and `/v1/admin/actions/{act_id}/approvals` | one row `approveApproval` at `/v1/admin/approvals/{apv_id}/approvals`; the sentence that a two-person action is started by the concrete operation and answers `202` with an `AdminApproval` is in the Permission cell of that row | applied |
| 6b | spec/10a-identity.md:732 | events `admin_action.proposed`, `.approved`, `.executed`, `.expired` | `admin.approval_requested`, `admin.approval_granted`, `admin.approval_expired`; `admin_action.executed` is kept and annotated as the original operation's own event, because 10.12 still emits it | applied |
| 7a | spec/10a-identity.md:194 | offer created by `POST /v1/device-link-offers` | `POST /v1/device-links` | applied |
| 7b | spec/10a-identity.md:195 | response `{offer_id, link_secret (128 random bits ...` | `{device_id, code (128 random bits ...` | applied |
| 7c | spec/10a-identity.md:722 | `createDeviceLinkOffer`, `createDeviceLinkApproval` at `device-link-offers` | `createDeviceLink`, `approveDeviceLink` at `/v1/device-links` and `/v1/device-links/{device_id}/approval` | applied |
| 8a | spec/10a-identity.md:199 | claim `POST /v1/device-link-offers/{offer_id}/claims {link_secret, device_pub, device_token,` | `POST /v1/device-links/redemptions {code, new_public_key, proof, device_token,` | applied |
| 8b | spec/10a-identity.md:205 | approval `.../{offer_id}/approval signed by A's key` | `POST /v1/device-links/{device_id}/approval {sas}, with the Step-Up header of A's key` | applied |
| 8c | spec/10a-identity.md:723 | `createDeviceLinkClaim` at `.../{dlo_id}/claims` | `redeemDeviceLink` at `/v1/device-links/redemptions` | applied |
| 8d | spec/10a-identity.md:191-192, 201 | offer states open, claimed, approved, cancelled | S15 link states pending, awaiting_approval, linked, denied (expired unchanged), also in the claim step `state awaiting_approval` | applied |
| 8e | spec/10a-identity.md:215 (was 215) | limit table row 'Wrong-secret attempts per offer' with `identity.code_max_attempts` | row dropped; `identity.code_max_attempts` now applies to e-mail codes (10.5) and other codes only | applied |
| 9 | spec/10a-identity.md:221 (cited 222) | key chain returned by `GET /v1/members/me/keys` | `GET /v1/member-keys` | applied |
| 10 | spec/10a-identity.md:167 | rotation `POST /v1/members/me/keys {device_pub, replaces_key_id}` | `POST /v1/member-keys/rotations {kind: 'device', key_id, challenge, signature, new_public_key, new_key_proof}` | applied |
| 11 | spec/10a-identity.md:718 | `listMemberKeys`, `createMemberKey` at `GET`, `POST /v1/members/me/keys` | `listMemberKeys`, `rotateKey` at `GET /v1/member-keys`, `POST /v1/member-keys/rotations` | applied |
| 12 | spec/10a-identity.md:719 | `createKeyRevocation` at `POST /v1/members/me/keys/{mky_id}/revocation` | `revokeMemberKey` at `DELETE /v1/member-keys/{key_id}` | applied |
| 13 | spec/10a-identity.md:720 | `createRecoveryKey`, `createRecoveryConfirmation` at `recovery-keys` and `recovery-confirmations` | `rotateKey` (`kind` `recovery`), `confirmRecoveryKey` at `POST /v1/member-keys/rotations` and `POST /v1/members/me/recovery-confirmations` | applied |
| 14a | spec/10a-identity.md:138 | row 'Recovery key confirmed' ended at 'lock the owner out' | the row ends with a pointer to the `recovery_signature` of `rotateKey`, S15.B.9 | applied |
| 14b | spec/10a-identity.md:139 | effect: new key `active` and unconfirmed, old key `retiring` for the grace period | new key `pending`, `active` after `identity.key_rotation_grace_s`, both work meanwhile; old key `retiring` until then, then `revoked` | applied |
| 19a | spec/10a-identity.md:78 | HKDF label with slashes, recovery | label `hamyar:v1:recovery` | applied |
| 19b | spec/10a-identity.md:110 | checksum domain label with slashes, recovery-checksum | label `hamyar:v1:recovery-checksum` | applied |
| 19c | spec/10a-identity.md:114 | HKDF salt with slashes, recovery | salt `hamyar:v1:recovery` | applied |
| 19d | spec/10a-identity.md:578 (searched whole file) | iphash label expected at about line 578 | not changed. Searched all 776 lines for `iphash` and for `hamyar/v1/`: no iphash label exists; 10.14.2 derives the day key as a separate random key `secret.ip_hash_key[day]` with no HKDF label, and no `/v1/iphash` is cited | skipped-not-found |
| 19e | spec/10a-identity.md:62 | signed-message prefix `utf8('hamyar/v1/')` | `utf8('hamyar:v1:')` | applied |
| 26 | spec/10a-identity.md:592 | export sentence ended 'rows in JSON.' | adds 'one `section` per request (S15.B.5.2)' | applied |

## Verdict-table coverage

Every ALIAS and REMOVE path of `spec/15c-api-reconcile-core.md` section 15.B.2 that 10a cited, and the edit that handled it:

- `/v1/auth-challenges` (ALIAS): edits 1c, 2, 3a, 3b.
- `/v1/admin/auth-challenges` (ALIAS): edits 4a, 5.
- `/v1/admin/actions/{act_id}/approvals` (ALIAS) and `/v1/admin/actions` (removed, 15.B.3.1): edit 6a.
- `/v1/device-link-offers`, `/approval`, `/claims` (ALIAS): edits 7a, 7c, 8a, 8b, 8c.
- `/v1/members/me/keys` (ALIAS): edits 9, 10, 11.
- `/v1/members/me/keys/{key_id}/revocation` (ALIAS): edit 12.
- `/v1/members/me/recovery-keys` (ALIAS): edit 13.
- `/v1/recovery`, `/v1/recovery-checksum` (REMOVE, labels): edits 19a, 19b, 19c.
- `/v1/iphash` (REMOVE, label): not present in 10a any more (19d).
- Kept because the verdict is NEW, and untouched: `/v1/members/me/closure`, `/v1/members/me/export`, `/v1/members/me/recovery-confirmations`, `/v1/members/me/session-revocations`.
- Paths of the verdict table that 10a does not cite (leases, jobs, policy, opt-ins, screening, public endpoints): nothing to do.

## Read-back

After all edits the places were read again from the branch. What is there now:

- 10a:62-63: the signed-message block reads with prefix `hamyar:v1:` and a single `challenge` field before `context_hash`.
- 10a:67: the purpose sentence lists exactly seven purposes and points to S15.B.3.1 and S15.B.4.
- 10a:69: the challenge endpoint is `identity-challenges`, returns `challenge` and `expires_at`, and the value is 256 bits.
- 10a:78-84: the registration block uses `identity-challenges` with purpose `create`, the body fields `public_key` and `recovery_public_key`, and `challenge`, `proof`, `recovery_proof`, both signing the `create` message.
- 10a:110 and 114: the labels read `hamyar:v1:recovery-checksum` and `hamyar:v1:recovery`; 10a:78 holds `hamyar:v1:recovery` too.
- 10a:138-139: the confirmed row ends with the `rotateKey` pointer; the effect row says the new key is `pending` and both keys work meanwhile.
- 10a:167: rotation posts to `/v1/member-keys/rotations` with the `kind`, `key_id`, `challenge`, `signature`, `new_public_key`, `new_key_proof` body.
- 10a:191-192: states read pending, awaiting_approval, linked, expired, denied.
- 10a:194-205: offer creation is `/v1/device-links` returning `device_id` and `code`; redemption is `/v1/device-links/redemptions`; approval is `/v1/device-links/{device_id}/approval` with `{sas}` and the Step-Up header.
- 10a:212-217: the limit table has four rows (lifetime, open offers, offers per day, devices); the wrong-secret row is gone.
- 10a:221: the key chain is returned by `GET /v1/member-keys`.
- 10a:227-232: recovery uses `identity-challenges` with purpose `recover`, `challenge`, `proof (new_dk)` and `new_recovery_proof (new_rk)`.
- 10a:479-480: admin sign-in starts at `/v1/admin/auth/challenges` and `createAdminSession` takes `challenge_id` and `assertion`.
- 10a:592: the export sentence ends with the `section` clause.
- 10a:712-728: the operation table has no `auth-challenges`, `device-link-offers`, `members/me/keys`, `recovery-keys`, `admin/auth-challenges`, `createAdminAction` or `/v1/admin/actions` left; the replaced rows read as in the table above.
- 10a:732: the event list has the three `admin.approval_*` events and `admin_action.executed` with its annotation.

## Residual text not edited

The cell authorizes only the edits listed; these places still use pre-reconciliation vocabulary and are left for the cell that owns them or for the owner. None is a cited path.

- 10a:95 (registration check 4) still names purpose `register_device`; 10a:168 names `rotate_device_key`; 10a:200 names `link_claim`; 10a:206 names `link_approve`.
- 10a:201-203 and 206 still use `offer_id`, `attempts` and `claimed_key_hash`; 10a:192 still says 'attempts exhausted'. The SAS derivation (`offer_id`, `device_pub`) is owned by S10 (15c observation 1).
- 10.2 entity rows `AuthChallenge` (`nonce`) and `DeviceLinkOffer` (`dlo_`, `attempts`) are unchanged.
- 10.12 two-person protocol still speaks of `AdminAction(state proposed ...)` and emits `admin_action.executed`.
- 10.4.2 item 5 and 10.8 still use `recovery_confirmed_at` and `recovery_signature`; 15.B.9 names `Member.recovery.confirmed_at`.
- Edit 19 asks to replace the same labels in every other part; that is outside this cell's allowed paths.

Result: DONE WITH SKIPS
