# 15. API specification, part b: admin, ledger, public and events

*Spec part 15b · owner cell C-021 · continues S15 part a (member surface under `/v1/*`) · binding vocabulary is `S0.*`. Written against Founding Document draft v0.1 (FD). Nothing here is legal advice and nothing here has been verified against any provider's terms or any law; every such dependence is tagged [V] and is configuration data entered by a human reviewer.*

## 15.21 Scope, inherited conventions and table legend

**Covered in this file** [D]: admin authentication and approvals (15.22); Service Registry (15.23); template review (15.24); policy (15.25); parameter editor (15.26); launch gates, launch switches and feature flags (15.27); kill switches (15.28); audit, appeal and report queues, abuse flags and sanctions (15.29); ledger explorer, invariant status and reversal (15.30); capacity dashboard (15.31); pre-registration lock, experiment configuration, calibration records and milestones (15.32); public endpoints (15.33); the event model (15.34); the webhook-free rule (15.35); worked examples (15.36); acceptance criteria (15.37). Member endpoints are part a; a member-surface operation appears here only where a public record is its output (share cards, 15.33.4).

**Section numbers** of this file start at `15.21` so they cannot collide with the headings of part a [A]; `S15.*` references resolve to either file (`ISS-156`).

**Inherited, not restated** [D]: transport and shape (S0 0.11.1), the three surfaces (0.11.2), the error model and its codes (0.11.3), authentication schemes (0.11.4), `Idempotency-Key` (0.11.5), cursor pagination (0.11.6), `ETag` / `If-Match` and rate-limit headers (0.11.7), id formats (0.6.3), integer-string amounts (0.6.1), UTC time (0.6.2). This file adds only what the admin and public surfaces need on top.

### 15.21.1 Endpoint table legend

Every endpoint table uses these columns, the same as part a: `op` (operation id, lowerCamelCase, S0 0.5); `Method path` (path under `/v1`); `Auth` (scheme, permission, markers); `Request` (body or query); `Response` (success status and shape); `Errors` (codes beyond the universal ones); `Idem` (`req` = `Idempotency-Key` required, `opt` = optional, `n/a`); `Page` (`cursor` or `-`); `RL` (rate-limit class, 15.21.2).

| Marker in `Auth` | Meaning |
| --- | --- |
| `none` | No credential (S0 0.11.4) |
| `admin` | Admin bearer token; the `perm.*` name follows |
| `SU` | Step-up required: the body carries `step_up` (15.22.3). A request without a valid one is `401 AUTH_INVALID` with `details.reason` = `step_up_required` or `step_up_invalid` |
| `2P` | Two-person action (15.22.4): the first call answers `202 Accepted` with an `AdminApproval`; the action runs when a second, different admin approves. Only actions named in `security.two_person_actions` are `2P` |

**Universal errors, not repeated in tables** [D]: `MALFORMED_REQUEST`, `VALIDATION_FAILED`, `AUTH_REQUIRED`, `AUTH_INVALID`, `AUTH_EXPIRED`, `FORBIDDEN`, `PAYLOAD_TOO_LARGE`, `UNSUPPORTED_MEDIA_TYPE`, `RATE_LIMITED`, `INTERNAL`, `UNAVAILABLE`. A missing `Idempotency-Key` where `req` is `400 VALIDATION_FAILED`; a reused key with another body is `422 IDEMPOTENCY_KEY_MISMATCH`; a failed `If-Match` is `412 PRECONDITION_FAILED` (all S0 0.11.3 and 0.11.5).

### 15.21.2 Rate-limit classes

All admin classes use one token bucket per admin id sized `ratelimit.admin_api_rpm` (initial configurable default 300 requests per minute, S0 0.10.6); a request spends its `cost`. Public classes use `ratelimit.public_rpm` per IP hash (never a raw IP, S0 0.6.4).

| Class | Applies to | Key | Budget | Cost |
| --- | --- | --- | --- | --- |
| `A-AUTH` | Unauthenticated admin endpoints (challenges, enrollment) | IP hash | `ratelimit.admin_auth_attempts_per_hour` per hour; failures counted; the only consequence is `429`, never a locked account, because a lock would let an attacker deny admins access [D] | 1 |
| `A-R` | Admin reads | admin id | `ratelimit.admin_api_rpm` | 1 |
| `A-W` | Admin writes, previews and heavy scans (ledger ranges, verifications) | admin id | `ratelimit.admin_api_rpm` | `ratelimit.admin_write_cost` (initial configurable default 2) |
| `PUB` | Public reads | IP hash | `ratelimit.public_rpm` | 1 |
| `PUB-V` | Public verification (manifest checks) | IP hash | `ratelimit.public_rpm` | `ratelimit.public_verify_cost` (initial configurable default 5, because a verification hashes a client-supplied document) |

The three new parameters are convention additions (`ISS-154`); each is replaced by the `OPS` measurement (S0 0.10.4).

### 15.21.3 Rules for every admin write [D]

1. **Audit trail.** The same database transaction that changes state inserts one `AdminAction` (`act_`): `admin_id`, `op`, `subject_type`, `subject_id`, `request_hash` (SHA-256 over RFC 8785 canonical JSON of method, path and body without `step_up`, S0 0.6.4), `reason`, `request_id`, `approval_id` (if any), `occurred_at`. If the insert fails, the change fails. No admin write bypasses this.
2. **Reason.** Every admin write that changes non-draft state carries `reason` (string, 1..2000 characters, English or Persian). It is stored, never shown to members.
3. **Reads are logged too** where they expose member-scoped data or cell content: the ledger explorer's member views, member detail, audit and appeal content, calibration of members. Such a read inserts an `AdminAction` of kind `read` [A]. Threat reasoning: insider and operator risk (S10.*).
4. **Idempotency and concurrency.** `Idempotency-Key` is required on every write (S0 0.11.5), except the three unauthenticated challenge and login endpoints of 15.22, whose single-use challenges already make a replay harmless. Mutable resources (service adapter, template drafts, feature flags, experiments, pre-registration drafts, milestones) return `ETag` and require `If-Match` on `PATCH`.
5. **No personal data in or out.** No admin endpoint accepts or returns a raw IP address, an e-mail address, a provider credential or session, or the text of a volunteer's chat page (S0 0.7). Admin views of members use `mem_` ids and aggregates only.
6. **Responses** carry `Cache-Control: no-store` (S0 0.11.7). Errors carry `details.copy_key` only for text an admin sees in the Operator tools (S11.*).
7. **Tighten at once, loosen with notice** (FD§5.4 R10, FD Principle 5) is applied the same way in 15.25, 15.26 and 15.27: a change that makes the system safer takes effect immediately by one admin; a change that makes it more permissive is public, noticed, prospective and two-person.

### 15.21.4 Permission names used in this file [A]

Permission names follow `perm.<area>.<action>` (S0 0.8.2). The permission matrix is owned by S10.*; the default holder below is a proposal that S10.* may change without touching any endpoint.

| Permission | Default holder | Used by |
| --- | --- | --- |
| `perm.admin.manage_users` | operator | 15.22 |
| `perm.approval.read`, `perm.approval.decide` | operator, reviewer | 15.22 (`decide` also needs the permission of the underlying action) |
| `perm.admin_action.read` | operator | 15.22 |
| `perm.service.read` | operator, reviewer | 15.23 |
| `perm.service.record`, `perm.service.review`, `perm.service.revoke` | reviewer | 15.23 |
| `perm.template.read`, `perm.template.author`, `perm.template.review`, `perm.template.retire` | reviewer | 15.24 |
| `perm.policy.read`, `perm.policy.tighten`, `perm.policy.loosen`, `perm.policy.approve_loosen` | reviewer (operator may read) | 15.25 |
| `perm.parameter.read`, `perm.parameter.edit.<owner>` with `<owner>` = `operator`, `reviewer`, `founders` | operator, reviewer, founders (S0 0.10.5) | 15.26 |
| `perm.launch.read`, `perm.launch.evidence`, `perm.launch.signoff`, `perm.launch.switch` | operator | 15.27 |
| `perm.flag.read`, `perm.flag.edit` | operator | 15.27 |
| `perm.killswitch.read`, `perm.killswitch.engage.global`, `perm.killswitch.engage.template`, `perm.killswitch.engage.service`, `perm.killswitch.engage.member`, `perm.killswitch.release` | operator (template, service and member engage also reviewer) | 15.28 |
| `perm.audit.read`, `perm.audit.resolve`, `perm.appeal.read`, `perm.appeal.decide`, `perm.report.read`, `perm.report.triage` | reviewer | 15.29 |
| `perm.alarm.read`, `perm.alarm.ack` | operator, reviewer | 15.29 |
| `perm.member.read_admin`, `perm.member.restrict`, `perm.member.suspend`, `perm.member.ban` | operator, reviewer | 15.29 |
| `perm.ledger.read`, `perm.ledger.read_member`, `perm.ledger.verify`, `perm.ledger.reverse` | operator | 15.30 |
| `perm.capacity.read` | operator | 15.31 |
| `perm.prereg.read`, `perm.prereg.edit`, `perm.prereg.lock`, `perm.experiment.read`, `perm.experiment.edit`, `perm.experiment.run`, `perm.calibration.read`, `perm.calibration.write`, `perm.milestone.edit` | operator (`perm.prereg.edit` and `perm.prereg.lock` founders) | 15.32 |

## 15.22 Admin authentication, sessions, step-up and two-person approvals

### 15.22.1 Mechanism [D][A]

Admin authentication is a WebAuthn passkey per `AdminUser` on a separate origin with its own session store (S0 0.6.4, 0.11.4). No shared password, no e-mail reset, no password-style fallback exists anywhere. The relying-party id is the admin origin. Credentials are requested with `userVerification: required`, discoverable credentials preferred, attestation `none` (no device-model collection, privacy). If S10.* chooses another mechanism, only the two challenge and session operations below change; every other section depends only on the `admin` scheme and on the `step_up` object. Details that S10.* owns: the bootstrap ceremony for the very first operator [V], the credential-loss procedure, and what the admin host can see.

- A session token is 256 bits from the OS CSPRNG, shown once, stored server-side only as a SHA-256 hash (S0 0.6.4). Lifetimes: idle `session.admin_idle_ttl_s` (initial configurable default 1800), absolute `session.admin_abs_ttl_s` (28,800). Tokens travel only in `Authorization: Bearer`; there are no cookies, so there is no CSRF surface.
- Every failure of a login or step-up assertion is the same `401 AUTH_INVALID` with `details.reason` = `assertion_invalid`; the response never says whether the credential, the challenge, the signature or the signature counter was wrong (no oracle).

### 15.22.2 Sessions

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `startAdminLogin` | `POST /v1/admin/auth/challenges` | `none` | `{}` | 201 `{challenge_id, public_key_options, expires_at}`; the challenge lives `session.admin_stepup_ttl_s`, single use | - | opt | - | `A-AUTH` |
| `createAdminSession` | `POST /v1/admin/sessions` | `none` | `{challenge_id, assertion}` (`assertion` = base64url `credential_id`, `client_data_json`, `authenticator_data`, `signature`, `user_handle`) | 201 `{session: {id, token, expires_at, idle_expires_at}, admin: AdminSummary}` | `AUTH_INVALID` | opt | - | `A-AUTH` |
| `getAdminSession` | `GET /v1/admin/sessions/current` | `admin` | - | `{admin: AdminSummary, permissions: [string], session: {id, expires_at, idle_expires_at}}` | - | n/a | - | `A-R` |
| `endAdminSession` | `DELETE /v1/admin/sessions/current` | `admin` | - | 204 | - | req | - | `A-W` |
| `listAdminSessions` | `GET /v1/admin/sessions` | `admin` | own sessions; `?admin_id` needs `perm.admin.manage_users` | list of `{id, created_at, last_used_at, expires_at}` (no tokens) | - | n/a | cursor | `A-R` |
| `revokeAdminSession` | `DELETE /v1/admin/sessions/{ses_id}` | `admin` own, or `perm.admin.manage_users` for another admin | - | 204; takes effect on the next request | `NOT_FOUND` | req | - | `A-W` |

`AdminSummary` = `{adm_id, display_name, roles: [reviewer or operator], is_active, credential_count, created_at}`. `display_name` is a pseudonym the admin chooses; no legal name is collected [D].

### 15.22.3 Step-up [D]

A sensitive operation needs a fresh passkey assertion bound to the exact request, so a stolen bearer token alone cannot make it.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `createStepUpChallenge` | `POST /v1/admin/step-up-challenges` | `admin` | `{op, request_hash}` where `request_hash` is computed by the client exactly as in 15.21.3 rule 1 | 201 `{challenge_id, public_key_options, expires_at}` with `expires_at = now + session.admin_stepup_ttl_s` (initial configurable default 300) | - | opt | - | `A-W` |

The challenge bytes are `SHA-256(canonical({op, method, path, request_hash, nonce}))`, with a 128-bit server nonce. The sensitive call then carries `"step_up": {"challenge_id": "...", "assertion": {...}}`. The server accepts it only if: the challenge is unused and unexpired; it was issued to this same admin; the assertion verifies with a credential of this admin and has the user-verified flag; the stored `request_hash` equals the recomputed hash. The challenge is then burned. Operations marked `SU` are listed per endpoint; in summary, step-up is required for every `2P` action, every launch, kill-switch, service approval and revocation, template review, policy and parameter publication, ledger, ban, pre-registration lock and experiment start operation, and for credential and role changes.

### 15.22.4 Two-person actions and `AdminApproval` [D][A]

The actions in `security.two_person_actions` (initial configurable default `ledger.reversal`, `launch.signoff`, `parameter.loosen`, `killswitch.release`) are extended by this part with `policy.loosen`, `launch.switch_on`, `admin.enroll`, `admin.role_change`, `member.ban` and `preregistration.lock` (`ISS-154`). `launch.signoff` is implemented natively by the gate item (15.27.2) and follows the same rules. Entity `AdminApproval` (`apv_`, permanent; convention addition) holds the pending action.

| Field | Type | Rule |
| --- | --- | --- |
| `apv_id` | id | |
| `action_name` | string | One of `security.two_person_actions` |
| `op`, `method`, `path` | string | The operation that will run |
| `payload` | json | The stored request body, immutable |
| `request_hash` | string | SHA-256 of the canonical request (15.21.3); what the approver's step-up is bound to |
| `required_approvals` | int | Distinct admins needed, the initiator counting as the first; for `ledger.reversal` it is `ledger.reversal_min_approvers` (constant 2); for service approval it is `service.min_approvers`; otherwise 2 |
| `approvals` | list | `{admin_id, decided_at}` |
| `status` | enum | `pending`, `approved`, `rejected`, `withdrawn`, `expired`, `failed` |
| `initiator_admin_id`, `created_at`, `expires_at` | | `expires_at = created_at + security.approval_ttl_s` (initial configurable default 86,400) |
| `result` | json or null | The original operation's response body once executed |

```
initiate(op, body):               # any 2P endpoint
  validate(body) with every guard that can be checked now          # fail fast, 4xx as usual
  require perm(op) and valid step_up(request_hash)
  insert AdminApproval(status=pending, approvals=[initiator], request_hash)
  emit admin.approval_requested
  return 202 { approval }   # Location: /v1/admin/approvals/{apv_id}

approve(apv_id, step_up):
  require status == pending and now < expires_at
  require caller != any approver already listed          # distinct admins
  require caller holds perm(op) approve-side and valid step_up(request_hash of the STORED payload)
  append caller to approvals; emit admin.approval_granted
  if len(approvals) < required_approvals: return 200 { approval }
  BEGIN TRANSACTION
    re-run every guard against CURRENT state                # state may have moved since initiate
    on guard failure: status = failed, emit admin.approval_failed, return 409 STATE_CONFLICT
    execute the operation as the system on behalf of all approvers (one AdminAction row naming them)
    status = approved; result = response body
  COMMIT
  return 200 { approval, result }
```

The approver reads the exact payload and a rendered diff before approving (`getApproval`) and cannot change it; a changed intention is a new initiation. An initiator may withdraw; the approval expires silently after `expires_at` (the event `admin.approval_expired` is emitted by the scheduler).

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listApprovals` | `GET /v1/admin/approvals` | `admin` `perm.approval.read` | `?status`, `?action_name`, `?awaiting_me=true` | list of `AdminApproval` without `payload` | - | n/a | cursor | `A-R` |
| `getApproval` | `GET /v1/admin/approvals/{apv_id}` | `admin` `perm.approval.read` | - | `AdminApproval` with `payload` and `diff` | `NOT_FOUND` | n/a | - | `A-R` |
| `approveApproval` | `POST /v1/admin/approvals/{apv_id}/approvals` | `admin` `SU` `perm.approval.decide` | `{step_up}` | 200 `{approval, result?}` | `FORBIDDEN` (initiator or repeat approver), `STATE_CONFLICT` (`details.reason`: `not_pending`, `expired`, `guard_failed`) | req | - | `A-W` |
| `rejectApproval` | `POST /v1/admin/approvals/{apv_id}/rejections` | `admin` `perm.approval.decide` | `{reason}` | 200 `approval` (`rejected`) | `STATE_CONFLICT` | req | - | `A-W` |
| `withdrawApproval` | `POST /v1/admin/approvals/{apv_id}/withdrawals` | `admin` (initiator only) | `{reason}` | 200 `approval` (`withdrawn`) | `FORBIDDEN`, `STATE_CONFLICT` | req | - | `A-W` |

### 15.22.5 Admin users and credentials [D]

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listAdminUsers` | `GET /v1/admin/users` | `admin` `perm.admin.manage_users` | `?role`, `?is_active` | list of `AdminSummary` | - | n/a | cursor | `A-R` |
| `getAdminUser` | `GET /v1/admin/users/{adm_id}` | `admin` own, or `perm.admin.manage_users` | - | `AdminSummary` | `NOT_FOUND` | n/a | - | `A-R` |
| `createAdminUser` | `POST /v1/admin/users` | `admin` `SU` `2P` `admin.enroll` | `{display_name, roles, reason}` | 202 approval; on approval 201 `{admin: AdminSummary(is_active=false), enrollment_code, expires_at}`; the code (128 bits) is shown once to the approving admin, who hands it over out of band; stored as a hash; lifetime `security.approval_ttl_s` | `ALREADY_EXISTS` | req | - | `A-W` |
| `createCredentialChallenge` | `POST /v1/admin/credential-challenges` | `none` with `{enrollment_code}`, or `admin` `SU` to add a credential to oneself | `{enrollment_code?}` | 201 `{challenge_id, creation_options, expires_at}` | `AUTH_INVALID` | opt | - | `A-AUTH` |
| `registerAdminCredential` | `POST /v1/admin/credentials` | as the challenge | `{challenge_id, attestation, label}` | 201 `{acr_id, label, created_at}`; the first credential activates the user | `AUTH_INVALID`, `STATE_CONFLICT` | req | - | `A-AUTH` |
| `listAdminCredentials` | `GET /v1/admin/users/{adm_id}/credentials` | `admin` own, or `perm.admin.manage_users` | - | list of `{acr_id, label, created_at, last_used_at}`; no key material | - | n/a | cursor | `A-R` |
| `deleteAdminCredential` | `DELETE /v1/admin/credentials/{acr_id}` | `admin` `SU` own, or `perm.admin.manage_users` | - | 204 | `STATE_CONFLICT` (`last_credential` of an active admin) | req | - | `A-W` |
| `changeAdminRoles` | `POST /v1/admin/users/{adm_id}/role-changes` | `admin` `SU` `2P` `admin.role_change` | `{roles, reason}` | 202 approval; on approval 200 `AdminSummary` | `STATE_CONFLICT` (`last_operator`) | req | - | `A-W` |
| `deactivateAdminUser` | `POST /v1/admin/users/{adm_id}/deactivations` | `admin` `SU` `perm.admin.manage_users` | `{reason}` | 200 `AdminSummary` (`is_active=false`); all sessions revoked at once. Single admin, because removing access is tightening (R10) | `STATE_CONFLICT` (`last_operator`: at least two active operators must remain) | req | - | `A-W` |

A lost passkey is handled by another operator through `deactivateAdminUser` and `createAdminUser`; there is no self-service recovery, because a recovery path is the weakest link of any credential system [D]. Each admin SHOULD hold at least two credentials (`credential_count` is shown in the Operator tools) [H: reduces lockouts; measured by the number of re-enrollments per year, `OPS`].

### 15.22.6 Admin action log

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listAdminActions` | `GET /v1/admin/actions` | `admin` `perm.admin_action.read` | `?admin_id`, `?op`, `?subject_type`, `?subject_id`, `?kind` (`write` or `read`), `?from`, `?to` | list of `AdminAction` | - | n/a | cursor | `A-R` |
| `getAdminAction` | `GET /v1/admin/actions/{act_id}` | `admin` `perm.admin_action.read` | - | `AdminAction` | `NOT_FOUND` | n/a | - | `A-R` |

The log is append-only, has no update or delete path and is included in the daily checkpoint scope of S6.* [A]. A reviewer sees only their own actions unless they also hold `perm.admin_action.read`.

## 15.23 Service Registry

Every service is created `unreviewed`, which counts as `no` everywhere (FD§5.3, S0 0.9.6). No endpoint in this file lets a service reach `approved` without a saved `TermsCopy` and recorded flag answers; the guard is `approvalGuard` below. Nothing about any provider is hardcoded: names, URL templates, limits and answers are data typed by a reviewer [V]. The server never fetches a terms page or any URL on its own (no scraping, no server-side request to a reviewer-entered address); a `source_ref` is stored text only.

**Schemas** [D]

| Object | Fields |
| --- | --- |
| `Service` | `svc_id`, `name` (1..120 chars), `state` (S0 0.9.6), `adapter` (below), `latest_terms_copy_id`, `approved_at`, `review_due_at`, `closure_cause` (`kill_switch` or `revoked` or `none`), `row_version`, `created_at` |
| `adapter` | `supports_prefill` (bool), `prefill_url_template` (string with exactly one `{prompt}`, `https` only, or null), `max_url_chars` (int 1..100000 or null), `copy_only` (bool, read-only, computed: true when prefill is unsupported or `prefilled_link_use` is not `yes`), `clean_chat_hint_key` (a `copy.*` key) |
| `TermsCopy` | `tcp_id`, `service_id`, `source_ref` (text, 1..2000), `captured_on` (UTC date, not in the future), `media_type` (`text/html`, `application/pdf`, `text/plain`, `text/markdown`; recorded, never interpreted), `size_bytes`, `sha256`, `status` (`uploading` or `sealed`), `chunk_count`, `captured_by_admin_id`, `created_at` |
| `FlagAnswer` | `fla_id`, `service_id`, `flag_key` (S0 0.8.3), `answer` (`yes`, `no`, `unknown`), `region` (ISO 3166-1 alpha-2 or null), `terms_copy_id`, `quote_ref` (text pointing at the passage, 1..500), `note`, `reviewer_admin_id`, `answered_at` |

`TermsCopy.status` is a convention addition (`ISS-154`); a `sealed` copy is immutable. Adapter changes that enable prefill or change `prefill_url_template` are recorded in the public change log with the host name only [D].

### 15.23.1 Service endpoints

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listServices` | `GET /v1/admin/services` | `admin` `perm.service.read` | `?state`, `?q` (name prefix) | list of `Service` | - | n/a | cursor | `A-R` |
| `getServiceSummary` | `GET /v1/admin/services/summary` | `admin` `perm.service.read` | - | `{counts_by_state: {state: int}, approved_count, review_due_soon: [svc_id]}`; the input of the launch rule (15.27.3) | - | n/a | - | `A-R` |
| `createService` | `POST /v1/admin/services` | `admin` `perm.service.record` | `{name, adapter?, reason}` | 201 `Service` in `unreviewed`; event `service.created` | `ALREADY_EXISTS` (same normalized name) | req | - | `A-W` |
| `getService` | `GET /v1/admin/services/{svc_id}` | `admin` `perm.service.read` | - | `Service`, `ETag` | `NOT_FOUND` | n/a | - | `A-R` |
| `updateServiceAdapter` | `PATCH /v1/admin/services/{svc_id}/adapter` | `admin` `perm.service.record` (`SU` and `service.min_approvers` approvals when it enables prefill or changes the template) | JSON Merge Patch of `adapter`; `If-Match` | 200 `Service` | `VALIDATION_FAILED` (`prefill_requires_flag`: `supports_prefill=true` needs the current `prefilled_link_use` answer `yes` with a sealed copy; template shape; `max_url_chars`), `PRECONDITION_FAILED` | req | - | `A-W` |

An adapter's behavior at run time (what the volunteer's card shows) is derived from this record by the adapter layer of S4.* and S11.*; a `copy_only` service never gets a link.

### 15.23.2 Terms copies (chunked upload) [D]

The API is JSON only (S0 0.11.1) and bodies are capped at `api.max_body_bytes` (1,048,576), but a terms copy may be `service.terms_copy_max_bytes` (5,242,880). Therefore a copy is uploaded in base64 chunks (`ISS-155`):

```
chunk_raw_max_bytes = floor(api.max_body_bytes * 3 / 4) - 1024      # base64 grows data by 4/3; 1024 reserved for the JSON envelope
                    = floor(1,048,576 * 3 / 4) - 1024 = 786,432 - 1,024 = 785,408 bytes   (default configuration)
chunk_count         = ceil(size_bytes / chunk_raw_max_bytes)           # 5,242,880 bytes -> 7 chunks
```

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `createTermsCopy` | `POST /v1/admin/services/{svc_id}/terms-copies` | `admin` `perm.service.record` | `{source_ref, captured_on, media_type, size_bytes, sha256, note?}` | 201 `TermsCopy` (`uploading`) plus `chunk_raw_max_bytes`, `chunk_count` | `VALIDATION_FAILED` (`size_bytes` over `service.terms_copy_max_bytes`), `STATE_CONFLICT` (service `revoked` or `rejected`: start a review first) | req | - | `A-W` |
| `putTermsCopyChunk` | `PUT /v1/admin/terms-copies/{tcp_id}/chunks/{n}` | `admin` `perm.service.record` | `{data_base64}` (`n` from 0) | 200 `{n, bytes, received_count}` | `STATE_CONFLICT` (already sealed), `VALIDATION_FAILED` (chunk too large; `n` out of range), `PAYLOAD_TOO_LARGE` | req | - | `A-W` |
| `sealTermsCopy` | `POST /v1/admin/terms-copies/{tcp_id}/seal` | `admin` `perm.service.record` | `{}` | 200 `TermsCopy` (`sealed`); the server concatenates the chunks, checks the byte count and `sha256` (S0 0.6.4), then freezes the copy; event `service.terms_copy_sealed` | `VALIDATION_FAILED` (`details.reason` = `missing_chunks` or `hash_mismatch`; nothing is sealed) | req | - | `A-W` |
| `listTermsCopies` | `GET /v1/admin/services/{svc_id}/terms-copies` | `admin` `perm.service.read` | - | list of `TermsCopy` | - | n/a | cursor | `A-R` |
| `getTermsCopy` | `GET /v1/admin/terms-copies/{tcp_id}` | `admin` `perm.service.read` | - | `TermsCopy` | `NOT_FOUND` | n/a | - | `A-R` |
| `getTermsCopyChunk` | `GET /v1/admin/terms-copies/{tcp_id}/chunks/{n}` | `admin` `perm.service.read` | - | `{n, data_base64}` | `NOT_FOUND` | n/a | - | `A-R` |

The Operator tools never render a terms copy as live HTML: it is offered as a download or shown as escaped text (S9.* escaping rule applies to all stored external text). An unsealed copy is garbage-collected after `security.approval_ttl_s` seconds of inactivity [A].

### 15.23.3 Flag answers [D]

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `recordFlagAnswers` | `POST /v1/admin/services/{svc_id}/flag-answers` | `admin` `perm.service.record` | `{terms_copy_id, answers: [{flag_key, answer, region?, quote_ref?, note?}], reason}` (1..13 answers, atomic) | 201 `{data: [FlagAnswer]}`; event `service.flags_recorded` | `STATE_CONFLICT` (`details.reason` = `service_not_recordable`: allowed only in `in_review` or `suspended`; `copy_not_sealed`; `copy_other_service`), `VALIDATION_FAILED` (unknown `flag_key`; `region` required for `regional_availability` and forbidden on other keys; a `yes` on a gate flag without `quote_ref`) | req | - | `A-W` |
| `listFlagAnswers` | `GET /v1/admin/services/{svc_id}/flag-answers` | `admin` `perm.service.read` | `?flag_key`, `?region` | full history, newest first | - | n/a | cursor | `A-R` |
| `getEffectiveFlags` | `GET /v1/admin/services/{svc_id}/flags` | `admin` `perm.service.read` | - | `{flags: [{flag_key, region, answer, answered_at, terms_copy_id, source: recorded or default_unknown}], gates_ready: bool, missing: [string]}` | `NOT_FOUND` | n/a | - | `A-R` |

Rules [D]:

1. Answers are append-only. A new answer for the same `(flag_key, region)` supersedes the older one by `answered_at`; the older one stays in history. There is no edit and no delete.
2. A flag with no answer is reported as `unknown` with `source: default_unknown`, and `unknown` is evaluated as `no` everywhere (FD§5.3, S0 0.8.3).
3. A `yes` on any gate flag MUST carry `quote_ref` (where in the saved copy the permission is stated). This keeps `yes` tied to text, not to memory.
4. Gate answers may be recorded only while the service cannot take new jobs (`in_review`, `suspended`). Negative evidence about an `approved` or `review_due` service therefore goes through a kill switch first (15.28: `kill.service.<svc_id>`), then the answers, then resume or revoke. This closes the window in which a service is `approved` while its recorded answers say otherwise [D].
5. The flags are the 13 keys of S0 0.8.3; answers for `info.*` keys never gate anything.

### 15.23.4 Review, approval, rejection, revocation

```
approvalGuard(svc, copy_id):                      # evaluated at request time and again at execution
  require svc.state == in_review
  copy = TermsCopy(copy_id); require copy.service_id == svc.id and copy.status == sealed
  require today_utc - copy.captured_on <= service.review_max_age_days * 1 day       # initial configurable default 90 days
  for key in [third_party_task_use, prohibited_content_compatible]:                 # FD§5.3 minimum
      a = latest FlagAnswer(svc, key, region = null)
      require a != null and a.answer == yes and a.quote_ref != null and a.terms_copy.status == sealed
  if service.min_approvers > 1: require approver != every reviewer_admin_id who recorded those answers
  return ok                                      # else STATE_CONFLICT with details.missing = list of failed clauses
```

Per-purpose and per-region conditions (`R5` to `R7`, `regional_availability`) are not part of approval; they are evaluated per job by the policy engine from the same flags (S7.*). Approval therefore never implies that every purpose is allowed on that service [D].

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `startServiceReview` | `POST /v1/admin/services/{svc_id}/reviews` | `admin` `perm.service.review` | `{reason}` | 201 `{service}` (`in_review`); event `service.review_started` | `STATE_CONFLICT` (state not in `unreviewed`, `rejected`, `review_due`, `revoked`) | req | - | `A-W` |
| `approveService` | `POST /v1/admin/services/{svc_id}/approvals` | `admin` `SU` `perm.service.review` (`2P` when `service.min_approvers` > 1; the key `service.approve` is then added to the two-person set) | `{reviewed_terms_copy_id, reason}` | 200 `Service` (`approved`, `approved_at`, `review_due_at = approved_at + service.review_max_age_days`); event `service.approved`; public change-log entry kind `service` | `STATE_CONFLICT` (`details.missing`: `terms_copy_missing`, `copy_too_old`, `gate_flag_not_yes:<flag_key>`, `quote_ref_missing`, `same_reviewer`) | req | - | `A-W` |
| `rejectService` | `POST /v1/admin/services/{svc_id}/rejections` | `admin` `SU` `perm.service.review` | `{reason, public_text?}` | 200 `Service` (`rejected`); event `service.rejected` | `STATE_CONFLICT` | req | - | `A-W` |
| `revokeService` | `POST /v1/admin/services/{svc_id}/revocations` | `admin` `SU` `perm.service.revoke` | `{reason_code (terms_changed, flag_changed, provider_notice, safety_incident, other), reason, public_text: {fa, en}}` | 200 `{service (revoked), affected: {open_jobs, queued_cells, leased_cells}}` counted at commit; event `service.revoked`; public change-log entry; single admin, because revocation tightens (R10) | `STATE_CONFLICT` (already `revoked`) | req | - | `A-W` |

Suspension and resumption of a service are kill-switch operations (`kill.service.<svc_id>`, 15.28), not separate endpoints, because S0 0.9.6 ties `service.suspended` to a kill switch [D]. `service.review_due` and `service.review_lapsed` are timer events produced by the scheduler (15.34); they have no endpoint. What happens to the in-flight cells and jobs of a revoked service is decided by S7.*; the API's only contribution is the event `service.revoked` and the `affected` counts. A reviewer's revocation reason is internal; `public_text` is what the change log shows (Principle 5).

## 15.24 Template review

A `Template` is the stable identity of a reviewed prompt pattern; a `TemplateVersion` carries the `definition` and the `review_status` of S0 0.9.5. The `definition` format (slots, prompt body, delimiters, output schema, automatic checks, comparator, envelope) is owned by S8.*; this part validates it only against the S8.* schema and treats it as opaque otherwise. Free-form prompts do not exist (R4); a job can only name an `approved` `TemplateVersion`.

**Schemas** [D]: `Template` = `{tpl_id, job_type, name, active_version_id, created_at}`. `TemplateVersion` = `{tpv_id, template_id, version (int from 1), definition, review_status, author_admin_id, required_approvals, approvals: [{admin_id, decided_at}], change_summary, content_hash, row_version, created_at}`. `required_approvals` is fixed when review is requested: `template.min_reviewers_new` (initial configurable default 2) if the template has never had an approved version, else `template.min_reviewers_edit` (1); a later parameter change does not alter a review already in progress [D].

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listTemplates` | `GET /v1/admin/templates` | `admin` `perm.template.read` | `?job_type`, `?review_status` (of the active version) | list of `Template` | - | n/a | cursor | `A-R` |
| `getTemplate` | `GET /v1/admin/templates/{tpl_id}` | `admin` `perm.template.read` | - | `Template` with a version summary list | `NOT_FOUND` | n/a | - | `A-R` |
| `createTemplate` | `POST /v1/admin/templates` | `admin` `perm.template.author` | `{job_type, name, definition, change_summary}` | 201 `{template, version}` (`draft`); event `template.version_created` | `VALIDATION_FAILED` (definition fails the S8.* schema), `ALREADY_EXISTS` | req | - | `A-W` |
| `createTemplateVersion` | `POST /v1/admin/templates/{tpl_id}/versions` | `admin` `perm.template.author` | `{base_version_id, definition, change_summary}` | 201 `TemplateVersion` (`draft`); event `template.version_created` | `STATE_CONFLICT` (a draft or in-review version already exists for this template: one open version at a time) | req | - | `A-W` |
| `listTemplateVersions` | `GET /v1/admin/template-versions` | `admin` `perm.template.read` | `?review_status`, `?template_id`, `?needs_my_review=true` (excludes versions I authored or already reviewed) | list; the review queue | - | n/a | cursor | `A-R` |
| `getTemplateVersion` | `GET /v1/admin/template-versions/{tpv_id}` | `admin` `perm.template.read` | - | `TemplateVersion`, `reviews`, `ETag` | `NOT_FOUND` | n/a | - | `A-R` |
| `updateTemplateDraft` | `PATCH /v1/admin/template-versions/{tpv_id}` | `admin` `perm.template.author` (author only) | Merge Patch of `definition`, `change_summary`; `If-Match` | 200 `TemplateVersion` | `STATE_CONFLICT` (only `draft` or `changes_requested`; an approved version is immutable), `FORBIDDEN`, `PRECONDITION_FAILED` | req | - | `A-W` |
| `requestTemplateReview` | `POST /v1/admin/template-versions/{tpv_id}/review-requests` | `admin` `perm.template.author` | `{}` | 200 `TemplateVersion` (`in_review`); event `template.review_requested`; guard: the definition validates and its declared test vectors pass the S8.* checker | `STATE_CONFLICT`, `VALIDATION_FAILED` | req | - | `A-W` |
| `submitTemplateReview` | `POST /v1/admin/template-versions/{tpv_id}/reviews` | `admin` `SU` `perm.template.review` | `{decision (approve, request_changes, reject), checklist: [{key, passed}], comments, reason}` | 201 `{review, version, review_round}`; used for the first and the second review | `FORBIDDEN` (author, or a reviewer who already reviewed this version), `STATE_CONFLICT` (not `in_review` or `awaiting_second_review`) | req | - | `A-W` |
| `retireTemplateVersion` | `POST /v1/admin/template-versions/{tpv_id}/retirement` | `admin` `SU` `perm.template.retire` | `{reason_code (superseded, defect, policy, other), reason, public_text: {fa, en}}` | 200 `TemplateVersion` (`retired`); event `template.retired`; public change-log entry | `STATE_CONFLICT` | req | - | `A-W` |

**Outcome mapping of `submitTemplateReview`** [D] (event names are those of S0 0.9.5):

| Decision | Condition | New `review_status` | Event |
| --- | --- | --- | --- |
| `approve` | approvals after this one < `required_approvals` | `awaiting_second_review` | `template.first_approved` |
| `approve` | `required_approvals` = 1 | `approved` | `template.first_approved`, then `template.second_approved` is NOT emitted; one event per state change, so a single-approval template emits `template.first_approved` with `payload.final = true` |
| `approve` | approvals after this one = `required_approvals` > 1 | `approved` | `template.second_approved` |
| `request_changes` | any | `changes_requested` (earlier approvals are cleared) | `template.changes_requested` |
| `reject` | any | `rejected` (T) | `template.rejected` |

**Second-reviewer rule** (FD§5.7 failure mode 10) [D]: every approving reviewer is distinct from the author and from every other approving reviewer. There is no override, not even for an operator. When a version is approved, in one transaction: `Template.active_version_id` moves to it, the previously active version becomes `retired` (event `template.retired`, `reason_code` = `superseded`), and a public change-log entry of kind `template` is written. Jobs already admitted keep the version stamped at admission (S5.*).

**Deprecation** has no intermediate state in S0 0.9.5: it is `retireTemplateVersion`. A temporary stop is `template.paused`, which is a kill switch (15.28, `kill.template.<tpl_id>`), applies to the template's active version, and is released only by two admins. A template that collects `template.autopause_report_count` reports inside `template.autopause_window_s` is paused by the system the same way (15.28.3).

## 15.25 Policy: rules, versions, tighten, loosen

Rules `R1` to `R10` are data (S7.*); this part defines the admin operations over them. A `PolicyVersion` is immutable once created and is stamped on jobs at admission and re-checked at acceptance (R9). Nothing here edits a version; every change creates the next one.

**Schemas** [D]

| Object | Fields |
| --- | --- |
| `Policy` | `pol_id`, `name`, `active_version_id`, `scheduled_version_ids` |
| `PolicyVersion` | `plv_id`, `policy_id`, `version` (int from 1), `status` (derived: `scheduled` while `now < effective_from`, `active`, or `superseded`), `change_class` (`tighten`, `loosen`, `neutral`), `effective_from`, `rules` (10 `Rule`), `allowlist` (list of `AllowEntry`), `changelog_entry_id`, `supersedes_id`, `content_hash`, `created_by_admin_id`, `created_at` |
| `Rule` | `rul_id`, `policy_rule_id` (`R1`..`R10`), `slug`, `position` (1..10, the evaluation order of FD§5.4, fixed), `enabled` (bool), `params` (json defined by S7.*), `reason_code` (`policy.<rule>.<slug>`) |
| `AllowEntry` | `purpose`, `license`, `sensitivity`, `service_requirement` (S0 0.8.1), `status` (`allowed` or `locked`); a combination that is not listed is rejected (deny by default, FD§5.1) |

**Change classification** [D]. The server, never the client, classifies a proposed version by diffing it against its base:

```
classify(base, proposed):
  tighter = any of:  rule disabled -> enabled;  allowlist entry removed or allowed -> locked;
            a rule param moved in its declared tightening direction (S7.*)
  looser  = any of:  rule enabled -> disabled;  allowlist entry added or locked -> allowed;
            a rule param moved in its declared loosening direction
  if tighter and looser:  class = mixed   -> refused by both endpoints (split the change)
  elif tighter:           class = tighten
  elif looser:            class = loosen
  else:                   class = neutral -> refused: nothing to publish (UNPROCESSABLE, no_semantic_change)
```

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listPolicies` | `GET /v1/admin/policies` | `admin` `perm.policy.read` | - | list of `Policy` | - | n/a | cursor | `A-R` |
| `getPolicy` | `GET /v1/admin/policies/{pol_id}` | `admin` `perm.policy.read` | - | `Policy` with active and scheduled versions | `NOT_FOUND` | n/a | - | `A-R` |
| `listPolicyVersions` | `GET /v1/admin/policies/{pol_id}/versions` | `admin` `perm.policy.read` | - | list of `PolicyVersion` without `rules` | - | n/a | cursor | `A-R` |
| `getPolicyVersion` | `GET /v1/admin/policy-versions/{plv_id}` | `admin` `perm.policy.read` | - | `PolicyVersion` with `rules` and `allowlist` | `NOT_FOUND` | n/a | - | `A-R` |
| `getPolicyRules` | `GET /v1/admin/policy-versions/{plv_id}/rules` | `admin` `perm.policy.read` | - | `{data: [Rule]}` | `NOT_FOUND` | n/a | - | `A-R` |
| `diffPolicyVersions` | `GET /v1/admin/policy-versions/{plv_id}/diff` | `admin` `perm.policy.read` | `?against={plv_id}` | `{change_class, rule_changes, allowlist_added, allowlist_removed}` | `NOT_FOUND` | n/a | - | `A-R` |
| `previewPolicyChange` | `POST /v1/admin/policies/{pol_id}/previews` | `admin` `perm.policy.read` | `{base_version_id, rules?, allowlist?}` | 200 `{change_class, diff, impact: {jobs_in_flight_affected, cells_queued_affected}, test_table: [{case_id, expected, actual}]}`; no state change | `VALIDATION_FAILED` | opt | - | `A-W` |
| `evaluatePolicyDryRun` | `POST /v1/admin/policy-versions/{plv_id}/evaluations` | `admin` `perm.policy.read` | `{purpose, license, sensitivity, service_requirement, service_id?, template_version_id?}` | 200 `{verdict, first_failing_rule, reasons: ["policy.R2.sensitivity_not_accepted"]}`; creates no job | `VALIDATION_FAILED` | opt | - | `A-W` |
| `tightenPolicy` | `POST /v1/admin/policies/{pol_id}/tightenings` | `admin` `SU` `perm.policy.tighten` | `{base_version_id, rules?, allowlist?, reason}` | 201 `{policy_version (active now), changelog_entry, impact}`; events `policy.version_published`, `policy.version_activated`, `changelog.entry_published` | `UNPROCESSABLE` (`details.reason` = `contains_loosening` with the list, `mixed_change`, `no_semantic_change`), `STATE_CONFLICT` (`base_version_id` is not the newest version) | req | - | `A-W` |
| `loosenPolicy` | `POST /v1/admin/policies/{pol_id}/loosenings` | `admin` `SU` `2P` `policy.loosen` `perm.policy.loosen` (approver `perm.policy.approve_loosen`) | `{base_version_id, rules?, allowlist?, reason, public_text: {fa, en}, effective_from?}` | 202 approval; on approval 201 `{policy_version (scheduled), changelog_entry}`; events `policy.version_published`, `changelog.entry_published`; later `policy.version_activated` | `UNPROCESSABLE` (`contains_tightening`, `mixed_change`, `no_semantic_change`, `public_text_required`), `STATE_CONFLICT` (`notice_too_short` at execution) | req | - | `A-W` |
| `cancelScheduledPolicyVersion` | `POST /v1/admin/policy-versions/{plv_id}/cancellations` | `admin` `SU` `perm.policy.tighten` | `{reason}` | 200 `PolicyVersion` (`superseded` before it ever activated); event `policy.version_cancelled`; one change-log note. Single admin: cancelling a loosening is tightening | `STATE_CONFLICT` (already active) | req | - | `A-W` |

### 15.25.1 Tighten, loosen, changelog (R10) [D]

- **Tighten.** `tightenPolicy` takes effect at once (`policy.tighten_immediate` is the constant `true`). The version is active when the call returns. In the same transaction a `ChangeLogEntry` is created with a machine-generated summary (which rules and allowlist rows changed) and `explanation_due_at = now + change.tighten_publish_within_s` (initial configurable default 86,400). The reviewer adds the human explanation as an `amends` note (`POST /v1/admin/changelog-entries`, below) within that time, otherwise the alarm `changelog.explanation_overdue` is raised (15.29.5). In-flight work is stopped by consumers of `policy.version_activated`: R9 re-checks at acceptance and the job service pauses what no longer passes; the change never makes earlier work legitimate retroactively.
- **Loosen.** `loosenPolicy` needs a stated `reason`, a public `public_text` in `fa` and `en`, and a second admin. At approval the entry is published (this is the "public change-log entry" of R10) and the new version is scheduled with `effective_from = approved_at + policy.loosen_min_notice_days * 86,400 s` (initial configurable default 7 days, never below `change.notice_days_default`). A requested `effective_from` earlier than that is refused at execution as `notice_too_short`; omitting it is the normal use. The version becomes active at `effective_from` through the scheduler (15.34).
- **Why mixed changes are refused** [D]: a loosening that also contains a tightening would delay the tightening by the notice period. Submit the tightening first.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `annotateChangeLog` | `POST /v1/admin/changelog-entries` | `admin` `perm.policy.tighten` or `perm.parameter.edit.<owner>` of the amended entry | `{amends_id, public_text: {fa, en}}` | 201 `ChangeLogEntry` (kind `note`, `amends_id` set); event `changelog.entry_published` | `NOT_FOUND`, `STATE_CONFLICT` (already annotated) | req | - | `A-W` |

Change-log entries are immutable; an annotation is a new entry that points at the one it explains.

## 15.26 Parameter editor

Every number in the system lives in the parameter table (S0 0.10); this is the only write path to it. Constants (S0 0.10.2, the set marked `constant`) and secrets (never parameters) have no write path at all.

**Schemas** [D]: `Parameter` = `{name, area, owner, type, unit, value, tighten_direction (up, down, none), is_public, mutable, version, effective_from, pending: ParameterVersion or null}`. `ParameterVersion` (`pmv_`, immutable in `value` and `effective_from`) = `{pmv_id, parameter_name, version (int), value, effective_from, change_class (tighten, loosen, neutral), reason, calibration_basis, changelog_entry_id, created_by_admin_id, created_at, withdrawn_at}`. `withdrawn_at` is the single write-once column of that entity (`ISS-154`). A reader asks for the value at time `t` and gets the newest non-withdrawn version with `effective_from <= t`.

**Classification** [D]. `tighten_direction` is declared per parameter. A change is `tighten` when it moves the value the way the declared direction says makes the system safer, `loosen` when it moves the other way, `neutral` when the direction is `none` (every enum, bool and text parameter that has no declared order; for an enum whose direction is `up` or `down`, the order of `validation.enum` is the tightening order) [A]. Notice rules:

```
notice_days(p) = p.notice_days                       if the parameter declares one
              or change.notice_days_price            if p.name starts with price., admission. or credit.   # initial configurable default 14
              or change.notice_days_default          otherwise                                             # initial configurable default 7
effective_from(change) = now                                            if class == tighten
                       = max(requested, accepted_at + notice_days * 86,400 s)   otherwise
```

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listParameters` | `GET /v1/admin/parameters` | `admin` `perm.parameter.read` | `?area`, `?owner`, `?mutable`, `?q` | list of `Parameter` | - | n/a | cursor | `A-R` |
| `getParameter` | `GET /v1/admin/parameters/{name}` | `admin` `perm.parameter.read` | - | `Parameter` | `NOT_FOUND` | n/a | - | `A-R` |
| `listParameterVersions` | `GET /v1/admin/parameters/{name}/versions` | `admin` `perm.parameter.read` | - | list of `ParameterVersion`, newest first | `NOT_FOUND` | n/a | cursor | `A-R` |
| `listParameterConstraints` | `GET /v1/admin/parameter-constraints` | `admin` `perm.parameter.read` | - | `{data: [{id: "C1", text_key, satisfied: bool, inputs: {name: value}}]}` for the cross-parameter constraints C1..C8 of S0 0.10.3 evaluated on current values | - | n/a | - | `A-R` |
| `previewParameterChange` | `POST /v1/admin/parameter-changes/previews` | `admin` `perm.parameter.read` | `{name, value}` | 200 `{change_class, notice_days, earliest_effective_from, violations: [{constraint, detail}], warnings: [{code, detail}]}`; no state change | `VALIDATION_FAILED` | opt | - | `A-W` |
| `proposeParameterChange` | `POST /v1/admin/parameter-changes` | `admin` `SU` `perm.parameter.edit.<owner>`; `2P` `parameter.loosen` when the class is `loosen` | `{name, value, expected_version, reason, public_text?: {fa, en}, requested_effective_from?, calibration_basis?}` | tighten: 201 `{parameter_version, changelog_entry}`. Loosen: 202 approval, then 201 at approval. Neutral: 201 with a prospective `effective_from`. Events `parameter.changed`, `changelog.entry_published`; at effective time `parameter.activated` | `UNPROCESSABLE` (`details.reason` = `immutable_constant`, `use_launch_endpoints` for `launch.*`, `not_a_parameter`), `VALIDATION_FAILED` (type, range, enum; `details.constraints` lists violated C-ids), `ALREADY_EXISTS` (a scheduled version for this name exists: withdraw it first), `PRECONDITION_FAILED` (`expected_version` is not the newest) | req | - | `A-W` |
| `withdrawParameterChange` | `POST /v1/admin/parameter-versions/{pmv_id}/withdrawals` | `admin` `SU` `perm.parameter.edit.<owner>` | `{reason}` | 200 `ParameterVersion` with `withdrawn_at` set; event `parameter.change_withdrawn`; a change-log note. Single admin: withdrawing a scheduled loosening is tightening | `STATE_CONFLICT` (`effective_from` already passed) | req | - | `A-W` |

**Rules** [D]

1. **One pending change per parameter.** A scheduled version blocks a second proposal for the same name.
2. **Validation at propose and again at activation.** The value must satisfy `validation` and every cross-parameter constraint C1..C8 against the values that will be in force at `effective_from` (current values plus other scheduled versions). The scheduler (`parameter.activate_due`) re-checks at activation; on a violation it does not activate, raises an alarm (category `ops`, kind `parameter.activation_blocked`) and the version stays scheduled until an operator withdraws or fixes it. C8 (fee against level) is a warning at propose time, because S0 defines it as a margin check [A].
3. **Public by default.** A `loosen` or `neutral` acceptance publishes its `ChangeLogEntry` at acceptance; that publication is the notice. A `tighten` publishes at once with the machine summary and the same `explanation_due_at` as 15.25.1. `public_text` is required for every class where `is_public` is true.
4. **Prospective only** (FD Principle 5): no change ever alters a transaction already posted, a lot already earned, an escrow already held, a quote already issued or a job's stamped values. Services read a value as of the time the thing was created.
5. **`launch.*` parameters** (`launch.min_signoffs`, `launch.required_gate_ids`, `launch.min_approved_services`) and the three switches are changed only by the endpoints of 15.27. Attempting it here is `UNPROCESSABLE` (`use_launch_endpoints`).
6. **Leaving an initial configurable default.** The first change of a parameter away from its `initial configurable default` MUST carry `calibration_basis = {code, ref}`, where `code` is the replacement measurement code of its S0 0.10.4 entry (`CAL`, `FND`, `OPS`, `LEG`) and `ref` points at the evidence: `CAL` needs `calibration_record_ids` (15.32.3) from at least `calibration.min_samples_per_service` accepted samples per approved service in scope; `FND` needs a locked `PreRegistration` id; `LEG` needs a reference text (a counsel sign-off id kept outside the system, never its content) [V]. This keeps a guess from being replaced by another guess.
7. **Owners.** `perm.parameter.edit.<owner>` follows the `owner` column of the parameter (S0 0.10.5). Thresholds owned by `founders` are the only ones an `operator` alone cannot change.

## 15.27 Launch gates, launch switches, feature flags

### 15.27.1 Objects [D]

| Object | Fields |
| --- | --- |
| `LaunchGateItem` (`lgi_`, S0 0.6.3) | `lgi_id`, `gate_id` (`G0`..`G5`, S0 0.8.4), `key` (such as `G0.service_registry`), `title_key` (a `copy.*` key), `state` (`open`, `evidence_attached`, `signed_off`, `reopened`), `required_signoffs` (= `launch.min_signoffs`, copied when evidence is first attached), `evidence`, `signoffs`, `tags` (`V` when the item rests on a [V] item) |
| evidence entry | `{evidence_id, kind (service_review, terms_copy, counsel_ref, threat_model_ref, calibration_ref, measurement_ref, fallback_decision, other), ref (text, 1..500, where it is kept; the content itself is not stored here), sha256?, note, attached_by_admin_id, attached_at}` |
| sign-off | `{admin_id, signed_at, comment}` |

The item list per gate is seeded data (S14.*). Item states and the events `gate.evidence_attached`, `gate.signed_off`, `gate.reopened` are S0 0.9.9.

### 15.27.2 Gate endpoints

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listLaunchGates` | `GET /v1/admin/launch/gates` | `admin` `perm.launch.read` | - | `{data: [{gate_id, state (open, ready_for_signoff, signed_off), items_total, items_signed_off}]}` | - | n/a | - | `A-R` |
| `getLaunchGate` | `GET /v1/admin/launch/gates/{gate_id}` | `admin` `perm.launch.read` | - | gate with its `LaunchGateItem` list | `NOT_FOUND` | n/a | - | `A-R` |
| `getLaunchGateItem` | `GET /v1/admin/launch/gate-items/{lgi_id}` | `admin` `perm.launch.read` | - | `LaunchGateItem` | `NOT_FOUND` | n/a | - | `A-R` |
| `attachGateEvidence` | `POST /v1/admin/launch/gate-items/{lgi_id}/evidence` | `admin` `perm.launch.evidence` | `{kind, ref, sha256?, note}` | 201 `LaunchGateItem` (`evidence_attached`); event `gate.evidence_attached`; for `kind = service_review` the server checks that `ref` is a `svc_` id in state `approved` | `VALIDATION_FAILED`, `STATE_CONFLICT` (already `signed_off`: reopen first) | req | - | `A-W` |
| `signOffGateItem` | `POST /v1/admin/launch/gate-items/{lgi_id}/signoffs` | `admin` `SU` `perm.launch.signoff` | `{comment}` | 201 `LaunchGateItem`; when distinct sign-offs reach `launch.min_signoffs` (initial configurable default 2) the item becomes `signed_off` and the event `gate.signed_off` is emitted once | `FORBIDDEN` (this admin has already signed this item), `STATE_CONFLICT` (not `evidence_attached`; or evidence changed after the first sign-off, in which case all sign-offs were voided and the state is `evidence_attached`) | req | - | `A-W` |
| `reopenGateItem` | `POST /v1/admin/launch/gate-items/{lgi_id}/reopenings` | `admin` `SU` `perm.launch.signoff` | `{reason}` | 200 `LaunchGateItem` (`reopened`); event `gate.reopened`; signoffs voided; single admin, because reopening tightens | `STATE_CONFLICT` | req | - | `A-W` |

The sign-off is the implementation of the `launch.signoff` two-person action: the pending object is the item, every signer passes a step-up bound to the item's current evidence hash, and signers are distinct admins. A gate is `signed_off` when all its `required` items are. Attaching evidence to a `signed_off` item is refused; `reopenGateItem` first [D].

### 15.27.3 Switches [D]

The three switches are `launch.members_may_join`, `launch.member_jobs_enabled` and `launch.minting_enabled` (S0 0.8.4, default `false`; the initial configurable default of a closed system).

```
switchBlockers(sw):                                   # [] means the switch may be turned on
  b = []
  for g in launch.required_gate_ids:                  # initial configurable default [G0, G1, G2, G3]
      if gate(g).state != signed_off: b += gate_not_signed_off:<g>
  if count(Service where state == approved) < launch.min_approved_services          # initial configurable default 1
     and no signed_off evidence of kind fallback_decision on G0:  b += not_enough_approved_services
  if sw == members_may_join and launch.require_locked_preregistration              # convention addition, default true
     and no PreRegistration(scope=phase_1, status=locked):  b += preregistration_not_locked
  if sw in [member_jobs_enabled, minting_enabled] and not members_may_join.value:  b += members_may_join_off
  if sw == minting_enabled and kill.all_minting is engaged:                         b += kill_switch_engaged
  if any open Alarm of category ledger with severity critical:                      b += open_critical_ledger_alarm
  return b
```

The `preregistration_not_locked` clause carries FD§9 ("thresholds pre-registered before day 1") into the rule; S13.* and S14.* may move it into a gate item without changing any endpoint (`ISS-156`) [A].

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `getLaunchStatus` | `GET /v1/admin/launch/status` | `admin` `perm.launch.read` | - | `{switches: {name: {value, changed_at, approval_id}}, gates: {G0: state, ...}, approved_services: {count, min}, preregistration_locked: bool, blockers: {members_may_join: [string], member_jobs_enabled: [string], minting_enabled: [string]}}` | - | n/a | - | `A-R` |
| `changeLaunchSwitch` | `POST /v1/admin/launch/switch-changes` | `admin` `SU` `perm.launch.switch`; `2P` `launch.switch_on` when `value = true` | `{switch, value, reason}` | `value = false`: 200 `{switch}` at once, one operator. `value = true`: 202 approval; at approval the blockers are recomputed; 200 `{switch}` when empty. Events `launch.members_may_join_changed`, `launch.member_jobs_enabled_changed`, `launch.minting_enabled_changed` | `STATE_CONFLICT` (`details.blockers` non-empty), `UNPROCESSABLE` (`no_change`) | req | - | `A-W` |

**Behavior when the rule stops holding** [D]: reopening a required gate item, or dropping below `launch.min_approved_services`, raises a `critical` alarm of category `launch` (kind `launch.rule_broken`); it does not flip a switch by itself, because an automatic flip in the middle of members' sessions is a surprise and the operator already has the immediate `value = false` path and the kill switches (15.28). New work is blocked separately by service and template state.

### 15.27.4 Feature flags

Feature flags (`ff.*`, S0 0.8.5) change behavior, never rules or money. Flags the platform ships: `ff.channel.human_review`, `ff.growth.v1_fast_path`, `ff.growth.v2_live_counter`, `ff.growth.v3_share_card`, `ff.growth.v4_trial_job`, `ff.growth.v5_referral`, `ff.growth.v6_milestones`, `ff.public.ledger_page`, `ff.experiment.expiry_arm`.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listFeatureFlags` | `GET /v1/admin/feature-flags` | `admin` `perm.flag.read` | - | list of `{flag_key, enabled, exposure_ppm, experiment_id, row_version, changed_at}` | - | n/a | - | `A-R` |
| `getFeatureFlag` | `GET /v1/admin/feature-flags/{flag_key}` | `admin` `perm.flag.read` | - | flag, `ETag` | `NOT_FOUND` | n/a | - | `A-R` |
| `updateFeatureFlag` | `PATCH /v1/admin/feature-flags/{flag_key}` | `admin` `SU` `perm.flag.edit` | `{enabled?, exposure_ppm? (0..1,000,000), reason}`; `If-Match` | 200 flag; event `feature_flag.changed`; a public change-log entry of kind `feature_flag` when the flag is member-visible | `STATE_CONFLICT` (`experiment_running`: `exposure_ppm` and `enabled` of a flag bound to a running experiment cannot be changed; stop the experiment), `UNPROCESSABLE` (`prereg_required` for `ff.experiment.expiry_arm`, 15.32.2), `PRECONDITION_FAILED` | req | - | - | `A-W` |

Disabling a flag is tightening and takes effect at once; enabling takes effect at once as well, because a flag is not a rule. A flag is never the only guard of a safety property [D].
