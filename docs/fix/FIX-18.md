# FIX-18: one name set across identity, safety and entities

Cell C-089. Source: `docs/audit/A04.md` findings 19 and 18 (via `docs/audit/FINAL.md` section 5.1, FIX-18). Nothing was executed; acceptance is run by CI. Line numbers are the lines read in this cell after the edits (10a, 10b); for 05a they are counted from a verified line and approximate.

## Choices and reasons

- **Secrets.** `spec/00-conventions.md` 0.6.4 and 0.10.1 name no e-mail secret, so the rule falls to 10b. 10b names `secret.email_encryption_key`: chosen (10a `secret.email_enc_key` renamed; 05a already used it). 10b names no e-mail index key at all; 10a says `secret.email_index_key`, 05a says `secret.email_lookup_key`. Chosen: `secret.email_lookup_key`, because 05a is canonical for the entity columns and its column is `email_lookup_hash`. 10a was renamed, and 10b inventory B received the missing row so that the three files name the same e-mail secrets (an addition, needed for `g1.secrets_inventory_complete`).
- **Entities.** `S0.7` and `S0.9` give names, tables, prefixes and retention for `MemberKey`, `Session`, `AdminUser`, `AdminCredential`, `AdminAction` but no columns or states, so 05a (5.2.5, 5.6.2 to 5.6.10) is canonical and 10a was edited to match. `MemberKey`: `purpose` (`auth`, `recovery`), `algorithm`, `status` (`active`, `rotated`, `revoked`); 10a `retiring` means the same as 05a `rotated` (old key still valid until `not_after`). `Session`: no `state` column, `revoked_at` and `revoked_reason`, `credential_id` for admin sessions. `AdminUser`: `status` (`invited`, `active`, `disabled`). `AdminCredential`: `status`, `last_used_at`. `AdminAction`: `subject_type`, `subject_id`, `subject_hash`, `approves_action_id`.
- Heading numbers `10.11`..`10.19` of 10b were not renumbered (FIX-21 does that). No default-pending decision (D-01..D-22) applied to any edit.

## Edits

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| 1 e-mail encryption key name | spec/10a-identity.md:148 | `secret.email_enc_key[version]` | `secret.email_encryption_key[version]` | applied |
| 2 e-mail index key name | spec/10a-identity.md:148 | `secret.email_index_key[version]` | `secret.email_lookup_key[version]` | applied |
| 3 hook 1 secret names | spec/10a-identity.md:763 | add `secret.email_enc_key`, `secret.email_index_key` | add `secret.email_encryption_key`, `secret.email_lookup_key` | applied |
| 4 hook 1 rotation sentence | spec/10a-identity.md:763 | rotation of `secret.email_enc_key` | rotation of `secret.email_encryption_key` | applied |
| 5 convention additions, secrets | spec/10a-identity.md:776 | `secret.email_enc_key` and `secret.email_index_key` | `secret.email_encryption_key` and `secret.email_lookup_key` | applied |
| 6 inventory B row for the lookup key | spec/10b-safety.md:319 | no e-mail lookup key row | row `secret.email_lookup_key` added after the encryption key row | applied |
| 7 assumptions table | spec/10b-safety.md:685 | lists `secret.email_encryption_key` only | also lists `secret.email_lookup_key` | applied |
| 8 MemberKey row | spec/10a-identity.md:32 | `kind` (`device`, `recovery`), `alg`, `state` (`active`, `retiring`, `revoked`) | `purpose` (`auth`, `recovery`), `algorithm`, `status` (`active`, `rotated`, `revoked`) | applied |
| 9 key table, recovery key | spec/10a-identity.md:53 | `kind` = `recovery` | `purpose` = `recovery` | applied |
| 10 rotation states and event | spec/10a-identity.md:162 | `MemberKey` states, old key moves to `retiring` | `MemberKey` `status` values, old key moves to `rotated` | applied |
| 11 algorithm column | spec/10a-identity.md:162 | the `alg` column | the `algorithm` column | applied |
| 12 rotation pseudocode | spec/10a-identity.md:170 | `K_old.state = retiring` | `K_old.status = rotated` | applied |
| 13 rotation pseudocode | spec/10a-identity.md:173 | `K_old.state = revoked` | `K_old.status = revoked` | applied |
| 14 recovery key rotation, effect | spec/10a-identity.md:139 | old key `retiring` | old key `rotated` | applied |
| 15 device link transaction | spec/10a-identity.md:207 | `MemberKey(device, active, ...)` | `MemberKey(auth, active, ...)` | applied |
| 16 recovery lookup | spec/10a-identity.md:234 | `MemberKey(kind recovery, state active or retiring)` | `MemberKey(purpose recovery, status active or rotated)` | applied |
| 17 session validation, bound key | spec/10a-identity.md:524 | bound key revoked, or `retiring` past `not_after` | bound key revoked, or `rotated` past `not_after` | applied |
| 18 convention additions, MemberKey | spec/10a-identity.md:776 | `MemberKey` states and the `kind` values | `MemberKey` `status` and `purpose` values (named as in `S5.2.5`) | applied |
| 19 AdminUser row | spec/10a-identity.md:40 | `state` (`active`, `locked`, `disabled`) | `status` (`invited`, `active`, `disabled`) | applied |
| 20 AdminCredential row, column names | spec/10a-identity.md:41 | `state`, `last_used_on` | `status`, `last_used_at` | applied |
| 21 Session row | spec/10a-identity.md:34 | `key_id`, `state` | `key_id` (member) or `credential_id` (admin), `revoked_at`, `revoked_reason` | applied |
| 22 session validation | spec/10a-identity.md:522 | `s.state != active` | `s.revoked_at is not null` | applied |
| 23 AdminAction row | spec/10a-identity.md:42 | `target_ref`, `params_hash`, `proposed_by`, `approved_by` | `subject_type`, `subject_id`, `subject_hash`, `approves_action_id`, `principal_type`; `outcome` kept | applied |
| 24 two-person protocol, propose step | spec/10a-identity.md:492 | `target_ref`, `proposed_by = P` | `subject_type` and `subject_id`, `admin_user_id = P`; `params_hash` stored as `subject_hash` | applied |
| 25 AdminCredential status values | spec/10a-identity.md:41 (and 10.12, AC-admin-03) | `pending`, `active`, `locked`, `revoked` | unchanged: 05a 5.6.9 allows `active`, `revoked` only (5.2.5); 10a needs `pending` (second approval) and `locked` (clone, emergency lock). Extending the 05a enum or changing 10.12 is a design decision with no default in FINAL section 4 | skipped-needs-owner |
| 26 AdminUser `locked` in text | spec/10a-identity.md:10.12 enrollment paragraph, AC-admin-04 (no line read) | refusal to disable or lock the last operator | unchanged: 05a `admin_status` has no `locked`; whether this means the user or the credential is not decided | skipped-needs-owner |
| 27 AdminAction proposal state | spec/10a-identity.md:10.12 (propose step, bootstrap fallback) vs spec/05a-entities.md:499-509 | `state proposed`, `expires_at`, `outcome`, `proposed_by = system:bootstrap` | unchanged: 05a 5.6.10 has no state, expiry, outcome or proposer column and treats AdminAction as the approval record, while 10a 10.18.1 and S15 use an `AdminApproval` entity | skipped-needs-owner |
| 28 columns 05a lacks | spec/05a-entities.md:381-388, 5.6.4 | `MemberKey` has no `authorized_by_key_id`, `authorization_signature`, `key_storage`, `revoked_reason`; `Session` has no `step_up_at` | unchanged: adding columns is not a rename; 10a keeps them as written | skipped-needs-owner |
| 29 device hash key | spec/10b-safety.md:313, spec/05a-entities.md:135 vs 10a 10.9.1 | `secret.device_hash_key` listed in 10b and 05a, not in 10a (10a: plain SHA-256, ISS-103) | unchanged: keyed or unkeyed device hash is the Device decision of FIX-17 and ISS-103 | skipped-needs-owner |
| 30 entities outside this cell's list | spec/10a-identity.md:31, 33, 39 vs 05a 5.6.1, 5.6.3, 5.6.5 | `Member.email_index`, `Device.state`, `Invite.state` (`active`) | unchanged: not in the authorized list (05a: `email_lookup_hash`, `status`, `issued`) | skipped-needs-owner |

## Read-back

- spec/10a-identity.md:32 now shows `purpose`, `algorithm` and a `status` list ending in `rotated`, `revoked`; no `kind`, `alg`, `state`, `retiring` remain in that row. Line 34 (Session) shows `credential_id` and `revoked_at`. Line 40 (AdminUser) shows `invited`. Line 41 shows `status` and `last_used_at` with the values `pending`, `locked` still present. Line 42 shows `subject_hash` and `approves_action_id`.
- spec/10a-identity.md:53, 139, 162, 170, 173, 207, 234 and 524 now say `purpose`, `rotated`, `status`, `auth` and `purpose recovery` as in rows 8 to 17; the rotation pseudocode reads `K_old.status = rotated` and later `K_old.status = revoked`. Line 139 still says the new key is `pending` and `active` after the grace time (a 15c edit, not this cell). Line 522 reads `s.revoked_at is not null`. Line 492 reads `subject_type and subject_id`.
- spec/10a-identity.md:148 names `secret.email_encryption_key[version]` and `secret.email_lookup_key[version]`; line 763 and line 776 name the same two; `secret.email_enc_key` and `secret.email_index_key` no longer appear in the places edited. The 10.2 Member row (line 31) and the 10.5 text still call the column `email_index` (row 30).
- spec/10b-safety.md:318 and 319 are the encryption key row and the new lookup key row, in the order encryption then lookup; line 685 lists both. 10b still marks `secret.device_hash_key` as an inventory row (line 313).
- spec/05a-entities.md was read and not edited: 5.3.3 (about lines 135 to 137) names `secret.device_hash_key[v]`, `secret.email_lookup_key[v]` and `secret.email_encryption_key[v]`; line 385 `status` of `key_status`; line 471 `invited`, `active`, `disabled`; line 488 `status` of `credential_status`; line 506 `approves_action_id`.
- Secret names now equal in all three files: `secret.email_encryption_key`, `secret.email_lookup_key`, `secret.volunteer_handle_key`, `secret.ip_hash_key`. Still different: `secret.device_hash_key` (10b and 05a only, row 29). `secret.log_actor_key` appears only in 10b (10a calls it the daily key, no conflict). The remaining 10b inventory names are not mentioned in 10a or 05a.

Result: DONE WITH SKIPS
