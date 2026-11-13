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

- **Tighten.** `tightenPolicy` takes effect at once (`policy.tighten_immediate` is the constant `true`). The version is active when the call returns. In the same transaction a `ChangeLogEntry` is created with a machine-generated summary (which rules and allowlist rows changed) and `explanation_due_at = now + change.tighten_publish_within_s` (initial configurable default 86,400). The reviewer adds the human explanation as an `amends` note (`POST /v1/admin/changelog-entries`, below) within that time, otherwise the alarm `changelog.explanation_overdue` is raised (15.29.4). In-flight work is stopped by consumers of `policy.version_activated`: R9 re-checks at acceptance and the job service pauses what no longer passes; the change never makes earlier work legitimate retroactively.
- **Loosen.** `loosenPolicy` needs a stated `reason`, a public `public_text` in `fa` and `en`, and a second admin. At approval the entry is published (this is the "public change-log entry" of R10) and the new version is scheduled with `effective_from = approved_at + policy.loosen_min_notice_days * 86,400 s` (initial configurable default 7 days, never below `change.notice_days_default`). A requested `effective_from` earlier than that is refused at execution as `notice_too_short`; omitting it is the normal use. The version becomes active at `effective_from` through the scheduler (15.34).
- **Why mixed changes are refused** [D]: a loosening that also contains a tightening would delay the tightening by the notice period. Submit the tightening first.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `annotateChangeLog` | `POST /v1/admin/changelog-entries` | `admin` `perm.policy.tighten` or `perm.parameter.edit.<owner>` of the amended entry | `{amends_id, public_text: {fa, en}}` | 201 `ChangeLogEntry` (kind `note`, `amends_id` set); event `changelog.entry_published` | `NOT_FOUND`, `STATE_CONFLICT` (already annotated) | req | - | `A-W` |

Change-log entries are immutable; an annotation is a new entry that points at the one it explains.

## 15.26 Parameter editor

Every number in the system lives in the parameter table (S0 0.10); this is the only write path to it. Constants (S0 0.10.2, the set marked `constant`) and secrets (never parameters) have no write path at all.

**Schemas** [D]: `Parameter` = `{name, area, owner, type, unit, value, tighten_direction (up, down, none), public, mutable, version, effective_from, pending: ParameterVersion or null}`. `ParameterVersion` (`pmv_`, immutable in `value` and `effective_from`) = `{pmv_id, parameter_name, version (int), value, effective_from, change_class (tighten, loosen, neutral), reason, calibration_source, changelog_entry_id, created_by_admin_id, created_at, withdrawn_at}`. `withdrawn_at` is the single write-once column of that entity (`ISS-154`). A reader asks for the value at time `t` and gets the newest non-withdrawn version with `effective_from <= t`.

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
| `proposeParameterChange` | `POST /v1/admin/parameter-changes` | `admin` `SU` `perm.parameter.edit.<owner>`; `2P` `parameter.loosen` when the class is `loosen` | `{name, value, expected_version, reason, public_text?: {fa, en}, requested_effective_from?, calibration_source?}` | tighten: 201 `{parameter_version, changelog_entry}`. Loosen: 202 approval, then 201 at approval. Neutral: 201 with a prospective `effective_from`. Events `parameter.changed`, `changelog.entry_published`; at effective time `parameter.activated` | `UNPROCESSABLE` (`details.reason` = `immutable_constant`, `use_launch_endpoints` for `launch.*`, `not_a_parameter`), `VALIDATION_FAILED` (type, range, enum; `details.constraints` lists violated C-ids), `ALREADY_EXISTS` (a scheduled version for this name exists: withdraw it first), `PRECONDITION_FAILED` (`expected_version` is not the newest) | req | - | `A-W` |
| `withdrawParameterChange` | `POST /v1/admin/parameter-versions/{pmv_id}/withdrawals` | `admin` `SU` `perm.parameter.edit.<owner>` | `{reason}` | 200 `ParameterVersion` with `withdrawn_at` set; event `parameter.change_withdrawn`; a change-log note. Single admin: withdrawing a scheduled loosening is tightening | `STATE_CONFLICT` (`effective_from` already passed) | req | - | `A-W` |

**Rules** [D]

1. **One pending change per parameter.** A scheduled version blocks a second proposal for the same name.
2. **Validation at propose and again at activation.** The value must satisfy `validation` and every cross-parameter constraint C1..C8 against the values that will be in force at `effective_from` (current values plus other scheduled versions). The scheduler (`parameter.activate_due`) re-checks at activation; on a violation it does not activate, raises an alarm (category `ops`, kind `parameter.activation_blocked`) and the version stays scheduled until an operator withdraws or fixes it. C8 (fee against level) is a warning at propose time, because S0 defines it as a margin check [A].
3. **Public by default.** A `loosen` or `neutral` acceptance publishes its `ChangeLogEntry` at acceptance; that publication is the notice. A `tighten` publishes at once with the machine summary and the same `explanation_due_at` as 15.25.1. `public_text` is required for every class where `public` is true.
4. **Prospective only** (FD Principle 5): no change ever alters a transaction already posted, a lot already earned, an escrow already held, a quote already issued or a job's stamped values. Services read a value as of the time the thing was created.
5. **`launch.*` parameters** (`launch.min_signoffs`, `launch.required_gate_ids`, `launch.min_approved_services`) and the three switches are changed only by the endpoints of 15.27. Attempting it here is `UNPROCESSABLE` (`use_launch_endpoints`).
6. **Leaving an initial configurable default.** The first change of a parameter away from its `initial configurable default` MUST carry `calibration_source = {code, ref, calibration_record_ids?}`, where `code` is the measurement code of the parameter's own "Replaced by" entry in S0 0.10.6 (one of `CAL`, `P1M`, `DEM`, `FND`, `CNS`, `SEC`, `TEC`, `OPS`; `CON` parameters are not editable) and `ref` points at the evidence: `CAL` needs `calibration_record_ids` (15.32.3) with at least `calibration.min_samples_per_service` (initial configurable default 30) completed cells for each approved service in scope; `FND` needs the id of a locked `PreRegistration`; `CNS` needs a reference text (a counsel sign-off id kept outside the system, never its content) [V]; `P1M`, `DEM`, `SEC`, `TEC` and `OPS` need a reference to the measurement or decision record. This is the `calibration_source` field of S0 0.10.3 made mandatory on the first change. This keeps a guess from being replaced by another guess.
7. **Owners.** `perm.parameter.edit.<owner>` follows the `owner` column of the parameter (S0 0.10.5). Thresholds owned by `founders` are the only ones an `operator` alone cannot change.

## 15.27 Launch gates, launch switches, feature flags

### 15.27.1 Objects [D]

| Object | Fields |
| --- | --- |
| `LaunchGateItem` (`lgi_`, S0 0.6.3) | `lgi_id`, `gate_id` (`G0`..`G5`, FD§8.3), `key` (such as `G0.service_registry`), `title_key` (a `copy.*` key), `state` (`open`, `evidence_attached`, `signed_off`, `reopened`), `required_signoffs` (= `launch.min_signoffs`, copied when evidence is first attached), `evidence`, `signoffs`, `tags` (`V` when the item rests on a [V] item) |
| evidence entry | `{evidence_id, kind (service_review, terms_copy, counsel_ref, threat_model_ref, calibration_ref, measurement_ref, fallback_decision, other), ref (text, 1..500, where it is kept; the content itself is not stored here), sha256?, note, attached_by_admin_id, attached_at}` |
| sign-off | `{admin_id, signed_at, comment}` |

The item list per gate is seeded data (S14.*). Item states and the events `gate.evidence_attached`, `gate.signed_off`, `gate.reopened` are S0 0.9.8.

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

The three switches are `launch.members_may_join`, `launch.member_jobs_enabled` and `launch.minting_enabled` (parameters of S0 0.10.6 Table C, default `false`, "only settable when the gate rule in S14.* passes"). A switch change writes a `ParameterVersion` in the usual way, effective at once (the gate rule, not a notice period, is the safeguard for turning on) [A], one `AdminAction`, a public change-log entry of kind `launch_switch`, and the event named below. The generic parameter endpoint refuses these names (15.26 rule 5).

```
switchBlockers(sw):                                   # [] means the switch may be turned on
  b = []
  for g in launch.required_gate_ids:                  # initial configurable default [G0, G1]
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

Feature flags (`ff.*`, entity `FeatureFlag`, `ffl_`, S0 0.10.6) change behavior, never rules or money. Flags the platform ships: `ff.channel.human_review`, `ff.growth.v1_fast_path`, `ff.growth.v2_live_counter`, `ff.growth.v3_share_card`, `ff.growth.v4_teams`, `ff.growth.v5_referral`, `ff.growth.v6_milestones`, `ff.job.reservations`, `ff.public.ledger_page`, `ff.experiment.expiry_arm`.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listFeatureFlags` | `GET /v1/admin/feature-flags` | `admin` `perm.flag.read` | - | list of `{flag_key, enabled, exposure_ppm, experiment_id, row_version, changed_at}` | - | n/a | - | `A-R` |
| `getFeatureFlag` | `GET /v1/admin/feature-flags/{flag_key}` | `admin` `perm.flag.read` | - | flag, `ETag` | `NOT_FOUND` | n/a | - | `A-R` |
| `updateFeatureFlag` | `PATCH /v1/admin/feature-flags/{flag_key}` | `admin` `SU` `perm.flag.edit` | `{enabled?, exposure_ppm? (0..1,000,000), reason}`; `If-Match` | 200 flag; event `feature_flag.changed`; a public change-log entry of kind `feature_flag` when the flag is member-visible | `STATE_CONFLICT` (`experiment_running`: `exposure_ppm` and `enabled` of a flag bound to a running experiment cannot be changed; stop the experiment), `UNPROCESSABLE` (`prereg_required` for `ff.experiment.expiry_arm`, 15.32.2), `PRECONDITION_FAILED` | req | - | - | `A-W` |

Disabling a flag is tightening and takes effect at once; enabling takes effect at once as well, because a flag is not a rule. A flag is never the only guard of a safety property [D].

## 15.28 Kill switches

A kill switch is the fast, reversible brake (S0 0.9.8). Engaging is tightening: one admin, at once. Releasing is loosening: two admins. A `KillSwitch` row (`ksw_`, permanent) is one state change of one switch; the current state is the newest row, and the five scopes below are the only keys [D].

### 15.28.1 Switch keys and API-visible effects [D]

| Key | Created | Effect visible through the API while engaged | Events produced and consumed |
| --- | --- | --- | --- |
| `kill.all_minting` | seeded, `released` | Operations that would post a `mint` (cell acceptance, grants that mint) answer `503 KILL_SWITCH_ENGAGED` or are held by the ledger service until release (the holding rule is S6.*, `ISS-156`); no new Commons cell leases are issued | `killswitch.engaged`; ledger service stops minting postings |
| `kill.all_new_jobs` | seeded, `released` | `createJob`, quote acceptance, waitlist release and reservation activation answer `503 KILL_SWITCH_ENGAGED`; jobs already running continue | `killswitch.engaged`; job service stops admitting |
| `kill.template.<tpl_id>` | on first engage | New jobs naming the template are refused; its queued cells are paused (`cell.paused`), its leases revoked (`lease.revoked`), its running jobs paused (`job.paused`) | `template.paused` (S0 0.9.5) and the job and cell events listed |
| `kill.service.<svc_id>` | on first engage | The service is shown as blocked in adapters; jobs requiring it are refused; its pinned cells are paused | `service.suspended` (S0 0.9.6) and the job and cell events |
| `kill.member.<mem_id>` | on first engage | That member's leases, submissions, job creation and invitations answer `403 FORBIDDEN` with `details.copy_key = copy.member.account_frozen` (not 503: a retry would be misleading); reads and appeals still work | `killswitch.engaged`; lease service revokes the member's active leases. The member's `status` is NOT changed; use 15.29.6 for sanctions |

The in-flight handling of each cascade is owned by S7.* and S8.*; this table lists only what a client and an operator can observe. A member-scoped switch is never published; the other four are published in the change log with their `public_text` [D].

### 15.28.2 Endpoints

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listKillSwitches` | `GET /v1/admin/kill-switches` | `admin` `perm.killswitch.read` | `?scope` (`all`, `template`, `service`, `member`), `?state` | list of `{switch_key, state, changed_at, reason_code}` (the two global keys always present; scoped keys only if ever touched) | - | n/a | cursor | `A-R` |
| `getKillSwitch` | `GET /v1/admin/kill-switches/{switch_key}` | `admin` `perm.killswitch.read` | - | `{switch_key, state, engaged_by, engaged_at, reason_code, reason, linked_report_id, linked_alarm_id, release_approval_id}` | `NOT_FOUND` (unknown scope id) | n/a | - | `A-R` |
| `listKillSwitchHistory` | `GET /v1/admin/kill-switches/{switch_key}/history` | `admin` `perm.killswitch.read` | - | list of `KillSwitch` rows, newest first | - | n/a | cursor | `A-R` |
| `engageKillSwitch` | `POST /v1/admin/kill-switches/{switch_key}/engagements` | `admin` `SU` `perm.killswitch.engage.<scope>` | `{reason_code (safety_incident, integrity_violation, provider_notice, policy_defect, abuse, capacity, other), reason, public_text?: {fa, en}, linked_report_id?, linked_alarm_id?}` | 201 `{switch, effects: {jobs_paused, cells_paused, leases_revoked}}` counted at commit; event `killswitch.engaged` | `STATE_CONFLICT` (`already_engaged`), `VALIDATION_FAILED` (`public_text` required for the four published scopes), `NOT_FOUND` (the template, service or member does not exist) | req | - | `A-W` |
| `releaseKillSwitch` | `POST /v1/admin/kill-switches/{switch_key}/releases` | `admin` `SU` `2P` `killswitch.release` `perm.killswitch.release` | `{reason, verification: [{check, passed}], public_text?}` | 202 approval; on approval 200 `{switch}`; event `killswitch.released`, then `template.resumed` or `service.resumed` as applicable | `STATE_CONFLICT` (`not_engaged`; `release_guard_failed` with `details.missing`) | req | - | `A-W` |

### 15.28.3 Release guards and automatic engagement [D][A]

```
releaseGuard(key):                         # evaluated at initiate and again at approval
  kill.service.<id>:  approvalGuard-minus-state(service)     # flags still yes, sealed copy younger than service.review_max_age_days
                      and service.closure_cause == kill_switch   # a revoked service is never resumed (S0 0.9.6)
  kill.template.<id>: active version still review_status == approved (or paused)
  kill.all_minting:   latest full-recompute invariant run passed after engage time
                      and no open critical Alarm of category ledger
  kill.all_new_jobs:  no open critical Alarm of category capacity or ledger
  kill.member.<id>:   linked reports and alarms of that member are acknowledged
```

The system itself engages switches in two cases and records `actor.principal_type = system` [A]: (1) a template that gets `template.autopause_report_count` reports within `template.autopause_window_s` (initial configurable default 5 within 3,600 s) is paused with `reason_code = abuse`; (2) a critical ledger invariant violation (`ledger.invariant_violated`, 15.30.2) engages `kill.all_minting` and `kill.all_new_jobs`. Releasing either always needs two admins. Case (2) is a proposal that S6.* and S14.* must confirm (`ISS-156`).

## 15.29 Queues, alarms, abuse flags, sanctions

### 15.29.1 Audit queue

Audits compare an independent re-execution with the first (S0 0.9.4). The comparator runs automatically; a human decides only what it cannot.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listAudits` | `GET /v1/admin/audits` | `admin` `perm.audit.read` | `?state`, `?template_version_id`, `?stalled=true` | list of `{aud_id, cell_id, state, comparator_verdict, created_at}` | - | n/a | cursor | `A-R` |
| `getAudit` | `GET /v1/admin/audits/{aud_id}` | `admin` `perm.audit.read` | - | `{aud_id, cell_id, state, comparator: {method, verdict, score_ppm}, executions: [{submission_id, output_hash, is_third}]}` (no content) | `NOT_FOUND` | n/a | - | `A-R` |
| `getAuditContent` | `GET /v1/admin/audits/{aud_id}/content` | `admin` `perm.audit.resolve` | - | `{input, outputs: [string]}`; logged as a read action (15.21.3); strings are data, escaped by the client | `NOT_FOUND` | n/a | - | `A-W` |
| `resolveAudit` | `POST /v1/admin/audits/{aud_id}/resolutions` | `admin` `SU` `perm.audit.resolve` | `{verdict (first_correct, second_correct, both_acceptable, neither), rationale}` | 200 `{audit}`; event `audit.resolved`, then the cell events of S0 0.9.3 | `STATE_CONFLICT` (the comparator or the third execution can still decide; a human decides only `mismatched` or `third_pending` audits that neither the comparator nor a third execution could settle, S8.* [A]) | req | - | `A-W` |
| `cancelAudit` | `POST /v1/admin/audits/{aud_id}/cancellations` | `admin` `SU` `perm.audit.resolve` | `{reason}` | 200 `{audit}`; event `audit.cancelled` | `STATE_CONFLICT` | req | - | `A-W` |

There is no endpoint that marks an audit passed without a verdict from the comparator, a third execution or `resolveAudit` with a rationale [D].

### 15.29.2 Appeals queue

`due_at = filed_at + appeal.reviewer_sla_days * 86,400 s` (initial configurable default 7 days); the queue sorts overdue first.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listAppeals` | `GET /v1/admin/appeals` | `admin` `perm.appeal.read` | `?state`, `?kind`, `?assigned_to=me`, `?overdue=true` | list of `{apl_id, kind, state, filed_at, due_at, assigned_admin_id}` | - | n/a | cursor | `A-R` |
| `getAppeal` | `GET /v1/admin/appeals/{apl_id}` | `admin` `perm.appeal.read` | - | appeal with `subject_ref`, the member's text (length bounded by S10.*), prior decisions; logged as a read action | `NOT_FOUND` | n/a | - | `A-R` |
| `assignAppeal` | `POST /v1/admin/appeals/{apl_id}/assignments` | `admin` `perm.appeal.decide` | `{admin_id?}` (default: caller) | 200 appeal; event `appeal.assigned` (or `appeal.reassigned` when already assigned) | `FORBIDDEN` (the assignee made the decision under appeal) | req | - | `A-W` |
| `startAppealReview` | `POST /v1/admin/appeals/{apl_id}/review-starts` | `admin` `perm.appeal.decide` | `{}` | 200 appeal (`in_review`); event `appeal.review_started` | `STATE_CONFLICT` | req | - | `A-W` |
| `requestSecondAppealReview` | `POST /v1/admin/appeals/{apl_id}/second-review-requests` | `admin` `perm.appeal.decide` | `{reason}` | 200 appeal; event `appeal.second_review_requested` | `STATE_CONFLICT` | req | - | `A-W` |
| `decideAppeal` | `POST /v1/admin/appeals/{apl_id}/decisions` | `admin` `SU` `perm.appeal.decide` | `{decision (upheld, overturned), rationale, member_message_copy_key}` | 201 `{decision, appeal}`; final decision emits `appeal.upheld` or `appeal.overturned` | `FORBIDDEN` (made the original decision, or already decided this appeal), `STATE_CONFLICT` | req | - | `A-W` |

For appeal kinds `member_ban` and `template_rejection`, a decision is final only when `appeal.ban_min_reviewers` distinct reviewers (initial configurable default 2) recorded the same decision; if the first two differ, a third distinct reviewer breaks the tie [A]. The consequences of `appeal.overturned` (restoring a status, re-crediting an accepted cell, re-opening a template) are carried out by the consumers named in 15.34 under S8.* and S10.*; this API only records the decision and emits the event.

### 15.29.3 Reports queue

`due_at = filed_at + report.triage_sla_days * 86,400 s` (initial configurable default 3).

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listReports` | `GET /v1/admin/reports` | `admin` `perm.report.read` | `?state`, `?overdue=true` | list of `{rpt_id, category, state, filed_at, due_at}` | - | n/a | cursor | `A-R` |
| `getReport` | `GET /v1/admin/reports/{rpt_id}` | `admin` `perm.report.read` | - | report with its subject reference and reporter text (no reporter identity beyond the pseudonymous `mem_id`) | `NOT_FOUND` | n/a | - | `A-R` |
| `triageReport` | `POST /v1/admin/reports/{rpt_id}/triages` | `admin` `perm.report.triage` | `{note}` | 200 report; event `report.triaged` | `STATE_CONFLICT` | req | - | `A-W` |
| `closeReport` | `POST /v1/admin/reports/{rpt_id}/outcomes` | `admin` `SU` `perm.report.triage` | `{outcome (actioned, dismissed), linked_admin_action_ids: [act_id], note, reporter_message_copy_key}` | 200 report; event `report.actioned` or `report.dismissed` | `VALIDATION_FAILED` (`actioned` needs at least one linked action) | req | - | `A-W` |

The actions themselves (engage a kill switch, retire a template, sanction a member) are ordinary calls of 15.28, 15.24 and 15.29.6; the report records which actions it led to [D].

### 15.29.4 Alarms and abuse flags

An abuse flag is an `Alarm` (`alm_`) with `category = abuse`; there is one resource, not two [D]. `Alarm` = `{alm_id, category (abuse, ledger, capacity, launch, ops, security), kind, severity (info, warning, critical), subject_ref: {type, id}, state (open, acknowledged), raised_at, acknowledged_by, acknowledged_at, details}`. `details` never contains personal data; it holds counts, thresholds and ids.

| Kind (category) | Raised when | Parameter |
| --- | --- | --- |
| `farming.device_limit` (abuse) | more accounts than allowed share one device attestation | `grant.max_per_device` |
| `farming.invite_tree` (abuse) | an invite tree exceeds depth or size, or its members behave in lock-step | `invite.tree_max_depth`, `invite.tree_max_members` |
| `farming.referral` (abuse) | referrals per referrer exceed the cap | `growth.referral.max_per_referrer_per_30d` |
| `integrity.duplicate_output` (abuse) | identical or near-identical outputs across many cells of one member | `verify.duplicate_similarity_threshold` |
| `integrity.timing_anomaly` (abuse) | many submissions faster than the minimum plausible time | `verify.timing_min_s` |
| `injection.output_flagged` (abuse) | outputs carry instruction-like text that the input screens would reject | `screen.*` |
| `template.report_burst` (abuse) | the autopause threshold of 15.28.3 was hit | `template.autopause_*` |
| `changelog.explanation_overdue` (ops) | no explanation note was added before `explanation_due_at` | `change.tighten_publish_within_s` |
| `parameter.activation_blocked` (ops) | a scheduled parameter version failed validation at activation | C1..C8 |
| `launch.rule_broken` (launch) | a signed-off item was reopened or the approved-service floor was crossed | `launch.*` |
| `ledger.invariant_violated` (ledger) | an invariant check failed | S6.* |

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listAlarms` | `GET /v1/admin/alarms` | `admin` `perm.alarm.read` | `?category`, `?severity`, `?state`, `?subject_id` | list of `Alarm` | - | n/a | cursor | `A-R` |
| `getAlarm` | `GET /v1/admin/alarms/{alm_id}` | `admin` `perm.alarm.read` | - | `Alarm` | `NOT_FOUND` | n/a | - | `A-R` |
| `acknowledgeAlarm` | `POST /v1/admin/alarms/{alm_id}/acknowledgements` | `admin` `perm.alarm.ack` | `{note}` | 200 `Alarm` (`acknowledged`); event `alarm.acknowledged` | `STATE_CONFLICT` | req | - | `A-W` |

Acknowledging an alarm does not fix its cause; a critical `ledger` or `launch` alarm still blocks the switches of 15.27.3 until the cause is cleared and the next check passes [D].

### 15.29.5 Member view for admins [D]

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listMembersAdmin` | `GET /v1/admin/members` | `admin` `perm.member.read_admin` | `?status`, `?trust_tier`, `?has_open_report=true`; no search by name, e-mail or handle (there are none) | list of `{mem_id, status, trust_tier, created_on}` | - | n/a | cursor | `A-R` |
| `getMemberAdmin` | `GET /v1/admin/members/{mem_id}` | `admin` `perm.member.read_admin` | - | `{mem_id, status, trust_tier, created_on, accepted_cells, reliability_ppm, open_reports, open_appeals, restriction, invite_tree: {root_mem_id, size, depth}}`; no devices, no keys, no balance (the ledger explorer has it); logged as a read action | `NOT_FOUND` | n/a | - | `A-R` |
| `getInviteTree` | `GET /v1/admin/members/{mem_id}/invite-tree` | `admin` `perm.member.read_admin` | - | `{root_mem_id, size, depth, status_counts, members: [{mem_id, status, depth}]}` | `NOT_FOUND` | n/a | cursor | `A-R` |

### 15.29.6 Restrictions, suspensions, bans [D]

Statuses and events are S0 0.9.1. Each action is a separate noun so every one has one audit row and one event. The member sees the outcome through a notice in the member inbox (part a), chosen from `reason_copy_key`, a fixed `copy.*` key; no free text reaches the member.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `restrictMember` | `POST /v1/admin/members/{mem_id}/restrictions` | `admin` `SU` `perm.member.restrict` | `{reason_code, reason, reason_copy_key, linked_ids: [], ends_at?}` | 200 member (tier `restricted`); event `member.restricted` | `STATE_CONFLICT` | req | - | `A-W` |
| `liftMemberRestriction` | `POST /v1/admin/members/{mem_id}/restriction-lifts` | `admin` `SU` `perm.member.restrict` | `{reason}` | 200 member (tier restored to `tier_before_restriction`); event `member.restriction_lifted` | `STATE_CONFLICT` | req | - | `A-W` |
| `suspendMember` | `POST /v1/admin/members/{mem_id}/suspensions` | `admin` `SU` `perm.member.suspend` | `{reason_code, reason, reason_copy_key, linked_ids: [], ends_at?}` | 200 member (`suspended`); event `member.suspended`; active leases revoked | `STATE_CONFLICT` | req | - | `A-W` |
| `reinstateMember` | `POST /v1/admin/members/{mem_id}/reinstatements` | `admin` `SU` `perm.member.suspend` | `{reason}` | 200 member (`active`); event `member.reinstated` | `STATE_CONFLICT` | req | - | `A-W` |
| `banMember` | `POST /v1/admin/members/{mem_id}/bans` | `admin` `SU` `2P` `member.ban` `perm.member.ban` | `{reason_code, reason, reason_copy_key, linked_ids: [at least one report, alarm or audit id]}` | 202 approval; on approval 200 member (`banned`); event `member.banned`; sessions and leases revoked | `VALIDATION_FAILED` (no linked evidence), `STATE_CONFLICT` | req | - | `A-W` |
| `restrictInviteTree` | `POST /v1/admin/members/{mem_id}/invite-tree/restrictions` | `admin` `SU` `perm.member.restrict` | `{reason_code, reason, reason_copy_key, linked_ids: [], member_ids?: [mem_id]}` (default: the whole tree, at most `invite.tree_max_members`) | 200 `{restricted: [mem_id]}`; one `member.restricted` event per member, one audit row naming the tree | `STATE_CONFLICT` | req | - | `A-W` |

A ban stays appealable (`appeal.*`); the balance of a banned member is not touched by this API, and expiry continues as for any account (S10.*). A ban is two-person because a capture of one reviewer account would otherwise be enough to expel any member (FD§5.7 failure mode 10) [D].

## 15.30 Ledger explorer, invariant status, reversal

The explorer is read-only. The only write path from the admin API to the ledger is the two-person reversal of 15.30.3, which posts new entries and edits nothing [D]. Amounts are integer strings in micro-credits (S0 0.6.1); `seq` is the global monotonic entry number; every entry carries `prev_hash` and `entry_hash` (S0 0.6.4).

### 15.30.1 Read endpoints

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `getLedgerHead` | `GET /v1/admin/ledger/head` | `admin` `perm.ledger.read` | - | `{seq, entry_hash, last_checkpoint: {date, seq, hash}, invariants_status}` | - | n/a | - | `A-R` |
| `listLedgerAccounts` | `GET /v1/admin/ledger/accounts` | `admin` `perm.ledger.read`; `?member_id` needs `perm.ledger.read_member` and is logged | `?type` (the account types of S0 0.8.5), `?member_id` | list of `{lac_id, type, owner_ref, balance_ucr}` | - | n/a | cursor | `A-R` |
| `getLedgerAccount` | `GET /v1/admin/ledger/accounts/{lac_id}` | `admin` `perm.ledger.read` | - | `{lac_id, type, owner_ref, balance_ucr, lots: {count, remaining_ucr, expiring_soon_ucr (within `credit.expiry_notice_days`)}}` | `NOT_FOUND` | n/a | - | `A-R` |
| `listAccountEntries` | `GET /v1/admin/ledger/accounts/{lac_id}/entries` | `admin` `perm.ledger.read` | `?from_seq`, `?to_seq`, `?entry_type`, `?order` (`desc` default, `asc`) | list of `LedgerEntry` | `NOT_FOUND` | n/a | cursor | `A-W` |
| `listLedgerEntries` | `GET /v1/admin/ledger/entries` | `admin` `perm.ledger.read` | `?from_seq`, `?to_seq`, `?entry_type`, `?txn_kind`, `?from`, `?to`, `?order` | list of `LedgerEntry`; at most `api.page_size_max` per page, scan by `seq` cursor | `VALIDATION_FAILED` (range wider than 31 days or 1,000,000 seq values: narrow it) [A] | n/a | cursor | `A-W` |
| `getLedgerEntry` | `GET /v1/admin/ledger/entries/{lge_id}` | `admin` `perm.ledger.read` | - | `LedgerEntry` | `NOT_FOUND` | n/a | - | `A-R` |
| `getLedgerTransaction` | `GET /v1/admin/ledger/transactions/{txn_id}` | `admin` `perm.ledger.read` | - | `{txn_id, txn_kind, entries: [LedgerEntry], balanced: bool, reverses_txn_id}` | `NOT_FOUND` | n/a | - | `A-R` |
| `listLots` | `GET /v1/admin/ledger/lots` | `admin` `perm.ledger.read_member` | `?member_id`, `?expiring_before` | list of `{lot_id, member_id, original_ucr, remaining_ucr, earned_at, expires_at, source_entry_id}` | - | n/a | cursor | `A-R` |
| `listLedgerCheckpoints` | `GET /v1/admin/ledger/checkpoints` | `admin` `perm.ledger.read` | `?from`, `?to` | list of `{date, seq, entry_hash, checkpoint_hash, signed: bool}` | - | n/a | cursor | `A-R` |

`LedgerEntry` = `{lge_id, seq, txn_id, txn_kind, entry_type, debit_account_id, credit_account_id, amount_ucr, lot_effects: [{lot_id, delta_ucr}], reverses_entry_id, parameter_epoch, occurred_at, prev_hash, entry_hash}`. `parameter_epoch` is the `config_epoch` of 15.34.1 at posting time.

### 15.30.2 Invariants and hash-chain checks

The invariants `INV-L*` are defined by S6.*; this API exposes their status and lets an operator run them on demand. `InvariantCheck` (`ivc_`, S0 0.6.3) rows are produced by the scheduler and by `runInvariant`.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listInvariants` | `GET /v1/admin/ledger/invariants` | `admin` `perm.ledger.read` | - | `{data: [{inv_id, title_key, mode (per_commit, sampled, full_recompute), last_check: {ivc_id, result (pass, fail, error), ran_at, duration_ms}, last_pass_at, consecutive_failures}]}` | - | n/a | - | `A-R` |
| `getInvariant` | `GET /v1/admin/ledger/invariants/{inv_id}` | `admin` `perm.ledger.read` | - | invariant with its statement (`copy.*` key) and last result | `NOT_FOUND` | n/a | - | `A-R` |
| `listInvariantChecks` | `GET /v1/admin/ledger/invariants/{inv_id}/checks` | `admin` `perm.ledger.read` | `?result` | list of `InvariantCheck` | `NOT_FOUND` | n/a | cursor | `A-R` |
| `runInvariant` | `POST /v1/admin/ledger/invariants/{inv_id}/runs` | `admin` `perm.ledger.verify` | `{mode (sampled, full)}` | 202 `{ivc_id, state: running}`; poll `getInvariantCheck`; a failure emits `ledger.invariant_violated` and raises a critical alarm | `STATE_CONFLICT` (a run of this invariant is already running) | req | - | `A-W` |
| `getInvariantCheck` | `GET /v1/admin/ledger/invariant-checks/{ivc_id}` | `admin` `perm.ledger.read` | - | `InvariantCheck` with `details` (ids only) | `NOT_FOUND` | n/a | - | `A-R` |
| `startHashChainVerification` | `POST /v1/admin/ledger/verifications` | `admin` `perm.ledger.verify` | `{from_seq, to_seq}` | 202 `{ivc_id, state: running}`; recomputes every `entry_hash` in the range from the canonical entry bytes and the previous hash | `VALIDATION_FAILED` (range over 1,000,000 seq values) | req | - | `A-W` |

A hash-chain result is `{ok: bool, entries_checked, first_bad_seq?}`; `ok = false` is a critical `ledger` alarm and, per 15.28.3, a freeze [D][A].

### 15.30.3 Reversal (the only write)

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `reverseLedgerEntry` | `POST /v1/admin/ledger/reversals` | `admin` `SU` `2P` `ledger.reversal` `perm.ledger.reverse` | `{entry_id or txn_id, reason_code, reason, linked_ids: []}` | 202 approval (`required_approvals` = `ledger.reversal_min_approvers` = 2, a constant); on approval 201 `{txn_id, entries}`; events `ledger.entry_committed` per posted entry | `STATE_CONFLICT` (`already_reversed`; `would_overdraw_lot`: the reversal would drive a lot or an account below zero where S0 forbids it; `outside_policy`), `VALIDATION_FAILED` | req | - | `A-W` |

A reversal posts new mirror entries in a transaction of kind `reversal` whose entries carry `reverses_entry_id`; the original entries are never altered or deleted. Reversals do not recreate expired lots; whatever S6.* rules for such cases is what the ledger service enforces, and this API passes its `STATE_CONFLICT` through [A].

## 15.31 Capacity dashboard

The figures are computed by the admission and forecast services (S6.*); this part fixes only how they are exposed. All ratios are integers in ppm (parts per million); all counts are integers; no float appears in a payload [D].

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `getCapacitySnapshot` | `GET /v1/admin/capacity` | `admin` `perm.capacity.read` | - | `{as_of, active_donors, forecast: {redeemable_cells, committed_cells, phi_ppm, headroom_cells}, claim_ratio_ppm, mint: {month_utc, minted_ucr, cap_ucr, utilization_ppm}, v_by_job_type: [{job_type, v_ppm, sample_cells}], eta_ppm, reserve: {balance_ucr, ceiling_ucr}, waitlist: {count}, reservations: {active, capacity_share_ppm}, concentration: {top_decile_share_ppm}}` | - | n/a | - | `A-R` |
| `listCapacityDays` | `GET /v1/admin/capacity/days` | `admin` `perm.capacity.read` | `?from`, `?to` (UTC dates, at most 90 days) | list of `{date, forecast_cells, committed_cells, reserved_cells, cap_cells}`, ascending by date | `VALIDATION_FAILED` | n/a | cursor | `A-R` |
| `listSupplyGauges` | `GET /v1/admin/capacity/supply-gauges` | `admin` `perm.capacity.read` | `?purpose`, `?sensitivity`, `?license`, `?service_id` | list of `{purpose, sensitivity, license, service_id, donors, suppressed}`; a bucket with fewer than `analytics.min_cohort_k` donors is returned as `donors: null, suppressed: true` | - | n/a | cursor | `A-R` |

Supply gauges show which kinds of work have too few opted-in donors for the demand (the supply gauges of FD§5.7 failure mode 8); small buckets are suppressed so the dashboard cannot be used to single out individuals [D].

## 15.32 Pre-registration, experiments, calibration, milestones

### 15.32.1 Pre-registration lock [D]

A `PreRegistration` (`prr_`, permanent) fixes the thresholds and decision rules before the data exist (FD§9). `PreRegistration` = `{prr_id, scope (phase_0, phase_1, phase_2, experiment), title, thresholds: [{measure_key, comparator (gte, lte, gt, lt), threshold, unit, window_days}], decision_rules: [{rule_key, text: {fa, en}, if: [measure_key], then (continue, stop, pivot)}], linked_experiment_ids, status (draft, locked), locked_at, content_hash, supersedes_id, post_launch (bool, computed), row_version, created_at}`. `status` and `content_hash` are convention additions (`ISS-154`). `measure_key` values come from the S13.* catalogue of measures (FD§9); this part checks the format `^[a-z][a-z0-9_]*$` and asks the S13.* catalogue whether the key exists.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listPreRegistrations` | `GET /v1/admin/pre-registrations` | `admin` `perm.prereg.read` | `?scope`, `?status` | list | - | n/a | cursor | `A-R` |
| `getPreRegistration` | `GET /v1/admin/pre-registrations/{prr_id}` | `admin` `perm.prereg.read` | - | `PreRegistration`, `ETag` | `NOT_FOUND` | n/a | - | `A-R` |
| `createPreRegistration` | `POST /v1/admin/pre-registrations` | `admin` `perm.prereg.edit` | `{scope, title, thresholds, decision_rules, linked_experiment_ids?, supersedes_id?}` | 201 `PreRegistration` (`draft`) | `VALIDATION_FAILED` (unknown `measure_key`) | req | - | `A-W` |
| `updatePreRegistration` | `PATCH /v1/admin/pre-registrations/{prr_id}` | `admin` `perm.prereg.edit` | Merge Patch; `If-Match` | 200 `PreRegistration` | `STATE_CONFLICT` (`locked`), `PRECONDITION_FAILED` | req | - | `A-W` |
| `lockPreRegistration` | `POST /v1/admin/pre-registrations/{prr_id}/lock` | `admin` `SU` `2P` `preregistration.lock` `perm.prereg.lock` | `{reason}` | 202 approval; on approval 200 `PreRegistration` (`locked`, `locked_at`, `content_hash`); event `preregistration.locked`; a public change-log entry of kind `preregistration_lock` that carries the hash and the content | `STATE_CONFLICT` (already locked) | req | - | `A-W` |

`content_hash` = SHA-256 over the RFC 8785 canonical JSON of `{scope, title, thresholds, decision_rules, linked_experiment_ids}`. After the lock the row is immutable at the database level. A change after the lock is a new `PreRegistration` with `supersedes_id`; the old one stays, and a new one created after `launch.members_may_join` first became true is shown with `post_launch = true` in the public view, so a changed threshold is visible as changed [D].

### 15.32.2 Experiments [D]

An `Experiment` (`exp_`) = `{exp_id, key, flag_key, hypothesis, arms: [{arm_key, fraction_ppm, config}], fraction_source (null or a parameter name), metrics: [measure_key], prereg_id, status (draft, running, stopped), assignment_seed_version, started_at, stopped_at, row_version}`. Arm fractions sum to exactly 1,000,000. The arm of a given member is a deterministic, logged function of the member id and the seed version (assignment mechanism S13.*); the API never lets an admin pick a member's arm. `status` and `fraction_source` are convention additions (`ISS-154`).

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listExperiments` | `GET /v1/admin/experiments` | `admin` `perm.experiment.read` | `?status` | list | - | n/a | cursor | `A-R` |
| `getExperiment` | `GET /v1/admin/experiments/{exp_id}` | `admin` `perm.experiment.read` | - | `Experiment`, `ETag` | `NOT_FOUND` | n/a | - | `A-R` |
| `createExperiment` | `POST /v1/admin/experiments` | `admin` `perm.experiment.edit` | `{key, flag_key, hypothesis, arms, fraction_source?, metrics, prereg_id?}` | 201 `Experiment` (`draft`) | `VALIDATION_FAILED` (fractions do not sum; the flag is not experiment-capable), `ALREADY_EXISTS` (the flag is already bound) | req | - | `A-W` |
| `updateExperiment` | `PATCH /v1/admin/experiments/{exp_id}` | `admin` `perm.experiment.edit` | Merge Patch; `If-Match` | 200 `Experiment` | `STATE_CONFLICT` (not `draft`) | req | - | `A-W` |
| `startExperiment` | `POST /v1/admin/experiments/{exp_id}/starts` | `admin` `SU` `perm.experiment.run` | `{reason}` | 200 `Experiment` (`running`, arms frozen, `assignment_seed_version` recorded; when `fraction_source` is set the parameter's value at this moment becomes the arm fraction); event `experiment.started` | `UNPROCESSABLE` (`prereg_not_locked`: `prereg_id` must name a locked `PreRegistration` that lists this experiment), `STATE_CONFLICT` | req | - | `A-W` |
| `stopExperiment` | `POST /v1/admin/experiments/{exp_id}/stops` | `admin` `SU` `perm.experiment.run` | `{reason}` | 200 `Experiment` (`stopped`); event `experiment.stopped`; assignments stay frozen | `STATE_CONFLICT` | req | - | `A-W` |
| `getExperimentSummary` | `GET /v1/admin/experiments/{exp_id}/summary` | `admin` `perm.experiment.read` | - | `{arms: [{arm_key, members, exposures}], metrics: [{measure_key, by_arm}]}`; any cell smaller than `analytics.min_cohort_k` is `null` | `NOT_FOUND` | n/a | - | `A-R` |
| `checkExperimentAssignment` | `POST /v1/admin/experiments/{exp_id}/assignment-checks` | `admin` `perm.experiment.read` | `{member_id}` | 200 `{arm_key, matches_logged: bool}`; logged as a read action | `NOT_FOUND` | opt | - | `A-W` |

There is no endpoint that lists which member is in which arm; a per-member view exists only through `checkExperimentAssignment`, one member at a time and logged [D]. `ff.experiment.expiry_arm` takes the treatment arm fraction from `experiment.expiry_arm.fraction` (initial configurable default 500,000 ppm, replaced by the `FND` pre-registration) so the parameter editor stays the single place where it changes.

### 15.32.3 Calibration records [D]

Phase 0 replaces guessed defaults with measurements typed in by a human working through each service's own interface (FD§6). The platform never reads a volunteer's account, never drives a service, and stores only the numbers below.

`CalibrationRecord` (`cal_`, permanent) = `{cal_id, service_id, template_version_id?, observed_on (UTC date), observer_admin_id, cells_attempted, cells_completed, limit_reached (bool), seconds_per_cell: [int] (1..200 values), refusals, failures, copy_paste_errors, check_passes, corrects_id?, note, created_at}`. Corrections are new records with `corrects_id`; nothing is edited.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listCalibrationRecords` | `GET /v1/admin/calibration-records` | `admin` `perm.calibration.read` | `?service_id`, `?from`, `?to` | list | - | n/a | cursor | `A-R` |
| `getCalibrationRecord` | `GET /v1/admin/calibration-records/{cal_id}` | `admin` `perm.calibration.read` | - | `CalibrationRecord` | `NOT_FOUND` | n/a | - | `A-R` |
| `createCalibrationRecord` | `POST /v1/admin/calibration-records` | `admin` `perm.calibration.write` | `{service_id, template_version_id?, observed_on, cells_attempted, cells_completed, limit_reached, seconds_per_cell, refusals, failures, copy_paste_errors, check_passes, corrects_id?, note?}` | 201 `CalibrationRecord`; event `calibration.recorded` | `VALIDATION_FAILED` (`cells_completed` > `cells_attempted`; any count negative) | req | - | `A-W` |
| `getCalibrationSummary` | `GET /v1/admin/calibration/summary` | `admin` `perm.calibration.read` | `?service_id` (default: all) | per service `{n_cells, days, cells_per_day: {min, median, max}, seconds_per_cell: {p50, p95}, refusal_ppm, failure_ppm, copy_paste_error_ppm, check_pass_ppm, meets_min_samples (n_cells >= calibration.min_samples_per_service), informs: [parameter names]}` | `VALIDATION_FAILED` | n/a | - | `A-R` |

`informs` is a fixed mapping: `seconds_per_cell.p50` informs `cell.envelope.expected_time_s`; `p95` informs `lease.timeout_s`; the low end informs `verify.timing_min_s`; `cells_per_day` informs `lease.max_active_per_member` and `mint.monthly_cap_credits`; `copy_paste_error_ppm` and `check_pass_ppm` inform `verify.*` thresholds [A]. The summary suggests no number; a person decides and enters it through `proposeParameterChange` with `calibration_source` (15.26 rule 6). Percentiles use the nearest-rank method on the pooled `seconds_per_cell` values [D].

### 15.32.4 Milestones [D]

A `Milestone` (`mls_`; convention addition, `ISS-154`) is a public marker tied to a real output (FD V6): `{mls_id, key, title: {fa, en}, criterion: {kind (verified_cells_total or manual), threshold?}, output_ref: {title, url (text, never fetched), license, sha256?}, status (draft, published), reached_at, published_at, row_version}`.

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `listMilestones` | `GET /v1/admin/milestones` | `admin` `perm.milestone.edit` | `?status` | list | - | n/a | cursor | `A-R` |
| `createMilestone` | `POST /v1/admin/milestones` | `admin` `perm.milestone.edit` | `{key, title, criterion, output_ref?}` | 201 `Milestone` (`draft`) | `ALREADY_EXISTS` | req | - | `A-W` |
| `updateMilestone` | `PATCH /v1/admin/milestones/{mls_id}` | `admin` `perm.milestone.edit` | Merge Patch; `If-Match` | 200 `Milestone` | `STATE_CONFLICT` (`published`) | req | - | `A-W` |
| `publishMilestone` | `POST /v1/admin/milestones/{mls_id}/publications` | `admin` `SU` `perm.milestone.edit` | `{reason}` | 200 `Milestone` (`published`); event `milestone.published` | `UNPROCESSABLE` (`output_ref_required`: no milestone is published without an output it points at; `criterion_not_reached` for `verified_cells_total` below its threshold) | req | - | `A-W` |

## 15.33 Public endpoints

Public endpoints are read-only except the verification `POST`. They are the code behind Principle 5 and Principle 11 of the FD: rules, parameters, changes, the ledger's totals and the provenance check are visible to anyone, and the visible record contains no personal data [D].

### 15.33.1 Rules common to all public endpoints [D]

1. **Auth:** `none`. No cookies are set or read, no identifier is issued, and responses carry no `Set-Cookie`. Requests are counted per IP hash only for rate limiting (S0 0.6.4); the hash is not stored with any response data.
2. **Caching:** `Cache-Control: public, max-age=N` with `N` at most `public.counter_refresh_s` (initial configurable default 60), plus `ETag` and `If-None-Match` with `304` (S0 0.11.7). Every body has `as_of` (UTC).
3. **CORS:** `GET` endpoints allow any origin without credentials, so a third party can embed or audit them. `POST` verification endpoints allow the same.
4. **Ledger lag:** every ledger-derived number is computed from entries with `occurred_at <= now - public.ledger_lag_s` (initial configurable default 300). It never shows the current head, so a viewer cannot correlate a public figure with one specific live transaction.
5. **Small-number suppression:** a count below `analytics.min_cohort_k` (initial configurable default 10) is `null` with `suppressed: true`.
6. **Feature flags:** `ff.growth.v2_live_counter`, `ff.public.ledger_page`, `ff.growth.v3_share_card` and `ff.growth.v6_milestones` gate their endpoints; when off the answer is `404 NOT_FOUND`. Parameters, change log, metrics, pre-registrations and manifest verification are always on.
7. **Language:** responses are language-neutral data and `copy.*` keys; texts the admin wrote carry `{fa, en}` and the client picks (S11.*).
8. **Rate limits:** `PUB`, except verification (`PUB-V`).
9. **Health** of the service itself (`/v1/health`) is defined in part a and BM0, not here.

### 15.33.2 Endpoint table

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `getPublicCounter` | `GET /v1/public/counter` | `none` | - | `{as_of, verified_cells_total, verified_cells_utc_day, members_active_today}`; `members_active_today` = members with at least one accepted cell in the current UTC day, `null` when below `analytics.min_cohort_k` | `NOT_FOUND` (flag off) | n/a | - | `PUB` |
| `getPublicLedgerSummary` | `GET /v1/public/ledger/summary` | `none` | - | see 15.33.3 | `NOT_FOUND` (flag off) | n/a | - | `PUB` |
| `listPublicLedgerCheckpoints` | `GET /v1/public/ledger/checkpoints` | `none` | `?from`, `?to` | list of `{date, seq, checkpoint_hash}` | `NOT_FOUND` (flag off) | n/a | cursor | `PUB` |
| `listPublicLedgerDaily` | `GET /v1/public/ledger/daily` | `none` | `?from`, `?to` (at most 366 days) | list of `{date, by_entry_type: [{entry_type, count, amount_ucr}]}` ascending by date | `NOT_FOUND` (flag off) | n/a | cursor | `PUB` |
| `listPublicParameters` | `GET /v1/public/parameters` | `none` | `?area` | list of `{name, area, unit, value, version, effective_from, scheduled: {value, effective_from} or null}` for every parameter with `is_public = true` | - | n/a | cursor | `PUB` |
| `getPublicParameter` | `GET /v1/public/parameters/{name}` | `none` | - | same shape for one parameter | `NOT_FOUND` | n/a | - | `PUB` |
| `listPublicParameterVersions` | `GET /v1/public/parameters/{name}/versions` | `none` | - | `{version, value, effective_from, change_class, changelog_entry_id}` newest first, withdrawn versions marked | `NOT_FOUND` | n/a | cursor | `PUB` |
| `getPublicMetrics` | `GET /v1/public/metrics` | `none` | - | the latest published `MetricSnapshot`, see 15.33.4 | - | n/a | - | `PUB` |
| `listPublicMetricSnapshots` | `GET /v1/public/metrics/snapshots` | `none` | `?from`, `?to` | list of `MetricSnapshot`, newest first | - | n/a | cursor | `PUB` |
| `listPublicChangeLog` | `GET /v1/public/change-log` | `none` | `?kind`, `?area`, `?from`, `?to` | list of `ChangeLogEntry`, newest first | - | n/a | cursor | `PUB` |
| `getPublicChangeLogEntry` | `GET /v1/public/change-log/{chg_id}` | `none` | - | `ChangeLogEntry` | `NOT_FOUND` | n/a | - | `PUB` |
| `listPublicMilestones` | `GET /v1/public/milestones` | `none` | - | list of published `Milestone` (no admin fields) | `NOT_FOUND` (flag off) | n/a | cursor | `PUB` |
| `getPublicShareCard` | `GET /v1/public/share-cards/{token}` | `none` | - | share card data, see 15.33.5 | `NOT_FOUND` (unknown, revoked or flag off; indistinguishable) | n/a | - | `PUB` |
| `verifyManifest` | `POST /v1/public/manifest-verifications` | `none` | `{manifest, deliverable_sha256?}` | 200 verdict, see 15.33.6 | `PAYLOAD_TOO_LARGE`, `VALIDATION_FAILED` | opt | - | `PUB-V` |
| `lookupManifestHash` | `GET /v1/public/manifest-hashes/{sha256_hex}` | `none` | - | verdict and a limited record, see 15.33.6 | `VALIDATION_FAILED` (not 64 hex characters) | n/a | - | `PUB-V` |
| `listPublicPreRegistrations` | `GET /v1/public/pre-registrations` | `none` | `?scope` | list of locked `PreRegistration` with `content_hash`, `locked_at`, `post_launch` | - | n/a | cursor | `PUB` |
| `getPublicPreRegistration` | `GET /v1/public/pre-registrations/{prr_id}` | `none` | - | one locked `PreRegistration` | `NOT_FOUND` (draft or unknown) | n/a | - | `PUB` |

`ChangeLogEntry` (`chg_`, S0 0.6.3) = `{chg_id, kind (parameter, policy, template, service, kill_switch, launch_switch, feature_flag, preregistration_lock, milestone, note), change_class (tighten, loosen, neutral), subject {type, id_or_name}, summary_key, public_text {fa, en}, before, after, effective_from, notice_until, amends_id, explanation_due_at, published_at}`. `before` and `after` are present only for parameters and flags. Entries are immutable. Kinds `kill_switch` appear for the four published scopes only; a member-scoped switch never appears [D]. `kind` values `kill_switch`, `launch_switch`, `feature_flag`, `preregistration_lock`, `milestone`, `note` extend the list of S0 and are convention additions (`ISS-154`).

### 15.33.3 Ledger summary [D]

```
{ "as_of": "2026-12-01T10:00:00Z",
  "ledger_head": { "seq": "18422", "entry_hash": "sha256:..." },
  "totals": { "minted_ucr": "...", "granted_ucr": "...", "levied_ucr": "...", "expired_ucr": "...", "retired_ucr": "..." },
  "balances": { "reserve_ucr": "...", "escrow_open_ucr": "...", "members_total_ucr": "...", "issuance_ucr": "-...", "retired_ucr": "..." },
  "reserve_ceiling_ucr": "...",
  "identity_check": { "sum_of_all_balances_ucr": "0" },
  "invariants": { "status": "ok", "last_full_recompute_at": "..." },
  "last_checkpoint": { "date": "2026-11-30", "seq": "18100", "checkpoint_hash": "sha256:..." } }
```

`ledger_head.seq` is the head at `as_of` (after the lag), not the live head. `identity_check` exists because the ledger is double-entry: signed balances of all accounts sum to zero (issuance holds the negative of everything minted; S0 0.8.5). `invariants.status` is `ok`, `violated` or `unknown`. The page shows aggregates and the daily checkpoint hashes only; it does not list individual entries or any member account, because a public feed of member-account movements with timestamps would be linkable to the people behind them. This is a decision and a trade-off: third parties can verify checkpoints and totals but cannot recompute the hash chain of member entries themselves (`ISS-155`) [D].

### 15.33.4 Metrics snapshot [D]

`MetricSnapshot` (`mts_`) is published every `price.publish_period_days` (initial configurable default 30): `{mts_id, period_start, period_end, published_at, v_by_job_type: [{job_type, v_ppm, verification_cells, accepted_primary_cells}], eta_ppm, claim_ratio_ppm, price_by_job_type: [{job_type, credits_per_cell_ucr}], quality: {false_accept_estimate_ppm, false_reject_estimate_ppm, gold_cells, audited_cells}, parameter_versions: [{name, version}]}`. An estimate with fewer than `analytics.min_cohort_k` underlying cells is `null`. The public record shows how the verification overhead `v`, the haircut `eta` and the claim ratio actually behaved, so the price formula (S6.*) can be re-derived from published numbers [D].

### 15.33.5 Share card [D]

A share card is a frozen, anonymous, revocable summary a member can post anywhere (V3). The member operations are specified here because the public record is their output (`ISS-156`):

| op | Method path | Auth | Request | Response | Errors | Idem | Page | RL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `createShareCard` | `POST /v1/share-cards` | `member` | `{include_badge: bool, locale (fa or en)}` | 201 `{shc_id, token, url_path, card}`; the `token` (128 bits, CSPRNG, base64url) is shown once and stored only as a SHA-256 hash; event `sharecard.created`; `403 FORBIDDEN` when `ff.growth.v3_share_card` is off or the member is not `active` | `RATE_LIMITED` (at most `growth.share_card_max_active` live cards per member [A]) | req | - | member class of part a |
| `listMyShareCards` | `GET /v1/share-cards` | `member` | - | list of `{shc_id, created_month, status}` (never the token) | - | n/a | cursor | member class of part a |
| `revokeShareCard` | `DELETE /v1/share-cards/{shc_id}` | `member` | - | 204; the public URL answers `404` from then on; event `sharecard.revoked` | `NOT_FOUND` | req | - | member class of part a |

`getPublicShareCard` returns `{card: {cells_verified, badge_key, issued_month, locale}, as_of}`. `cells_verified` is the count at creation, `issued_month` is `YYYY-MM` (no day, no time), `badge_key` is a key of S0 0.8 or null. There is no name, handle, `mem_` id, service, topic, region or time of day in the card, and the card never changes after creation. No image is rendered on the server: the client draws the picture from this data, so there is no server-side rendering, no font fetching and no third-party request [D]. A view emits an analytics event `sharecard.viewed` carrying only the card's `shc_id` and a UTC date, so conversion from card to first cell (V3) can be counted per card without identifying a viewer or the member [A].

### 15.33.6 Provenance manifest verification [D][P]

The provenance manifest travels with every export (FD§5.6; S0 0.6.3 `mfs_`). It records, per output, the job, the template version, the policy version, the cell and verification outcomes, the volunteer-attested service and region (attested, not proven), and a license and no-training flag. The export form omits the volunteer handle (requesters never see it) [A]; verification works on the export form (`ISS-156`).

- `verifyManifest` recomputes `manifest_hash = SHA-256(RFC 8785 canonical JSON of manifest)` and looks it up. Optionally `deliverable_sha256` is compared with the deliverable hash recorded in the manifest.
- `lookupManifestHash` is the same lookup for someone who has only the hash.

Response of both: `{verdict (match, mismatch, unknown), manifest_hash, recorded: {issued_on (UTC date), job_type, license, purpose, no_training, policy_version_number} or null, differences: [json_pointer], deliverable_check: {checked, matches} , limits_copy_key}`.

| Verdict | Meaning | `recorded` | `differences` |
| --- | --- | --- | --- |
| `match` | The hash equals a stored manifest hash | present | empty |
| `mismatch` | The submitted manifest names a stored `mfs_` id but its hash differs | `null` | JSON pointers of differing fields only, never the stored values |
| `unknown` | No stored manifest has this hash and the manifest names none we hold | `null` | empty |

`lookupManifestHash` can only answer `match` or `unknown`. `limits_copy_key` points at fixed text that MUST be shown next to any positive result (S11.*): a match proves that the document equals what the platform recorded; it does not prove which service or model produced the work (that is volunteer-attested), it is not a legal certificate, and the no-training flag is a contractual statement, not a technical lock (FD§5.6, Principle 3). Size is capped by `api.max_body_bytes`; the check never calls any other server [D].

## 15.34 Event model

A domain event records one state change. This section lists them all with payload, producer and consumers, consistent with the names of S0 0.9. Component names are the ones this file uses; S4.* owns the deployment and may rename them without changing an event (`ISS-156`) [A].

### 15.34.1 Envelope and delivery [D]

Every event has this envelope; the catalog below lists only the payload.

| Field | Type | Rule |
| --- | --- | --- |
| `event_id` | id | `evt_` + ULID [A]; the idempotency key of every consumer |
| `name` | string | `<entity>.<past_participle>` (S0 0.9.1) |
| `event_version` | int | Starts at 1; a payload change that removes or renames a field increments it, an added optional field does not |
| `occurred_at` | timestamp | UTC, set by the producer inside the transaction |
| `actor` | object | `{principal_type (anonymous, member, admin, system), id}`; `id` is an opaque `mem_`, `adm_` or component name; never a name or address |
| `aggregate_type`, `aggregate_id`, `aggregate_seq` | string, id, int | The entity that changed and its per-aggregate sequence number (starts at 1, no gaps) |
| `policy_version_id` | id or null | The policy in force at that moment |
| `config_epoch` | int | A global counter that increments every time a `ParameterVersion` becomes effective or a `PolicyVersion` becomes active; together with the history tables it answers "which parameter values were in force" without copying all of them into every event (convention addition, `ISS-154`) |
| `request_id` | id or null | The `req_` that caused it, if any |

- **Outbox** (S0 0.9.1): the event row is written in the same database transaction as the state change; a relay publishes it afterwards. A state change without its event, or an event without its state change, cannot exist.
- **Delivery** is at least once. Consumers are idempotent on `event_id`. Order is guaranteed only per aggregate (by `aggregate_seq`); no consumer may assume order across aggregates. An event never carries personal data, message text, prompts, outputs or terms-page content, only ids, enums, counts, hashes and parameter names.
- **Rejections are not events.** A request refused by a guard changes nothing and emits nothing (S0 0.9.1). The `AdminAction` log, not the event log, records refused admin attempts only when they fail for authorization reasons [A].
- **Replay.** A new consumer is rebuilt by replaying the outbox from `aggregate_seq` 1; no consumer reads another consumer's table.

**Components** [A]: `api` (request handlers), `job_svc`, `cell_svc` (cells, leases, submissions), `verify_svc` (checks, audits, reliability), `ledger_svc`, `policy_svc`, `registry_svc` (services, terms copies, flags), `template_svc`, `identity_svc` (members, sessions, appeals, reports), `config_svc` (parameters, change log, launch, kill switches, flags, pre-registrations, experiments), `admin_svc` (admins, approvals, action log), `scheduler` (timers), `metrics_svc`, `public_proj` (public read models and caches), `inbox_proj` (member inbox), `analytics` (aggregate counters, no personal data).

### 15.34.2 Catalog: job, cell, lease, submission

| Event | Payload (besides envelope) | Producer | Consumers |
| --- | --- | --- | --- |
| `job.created` | `job_id`, `requester_member_id`, `job_type`, `template_version_id` | `job_svc` | `analytics` |
| `job.submitted` | `job_id`, `size_cells` | `job_svc` | `policy_svc` |
| `job.policy_rejected` | `job_id`, `reason_codes` | `policy_svc` | `inbox_proj`, `analytics` |
| `job.policy_passed` | `job_id`, `policy_version_id`, `quote_id` | `policy_svc` | `job_svc` |
| `job.quote_expired` | `job_id`, `quote_id` | `scheduler` | `inbox_proj` |
| `job.waitlisted` | `job_id`, `waitlist_entry_id`, `position` | `job_svc` | `inbox_proj`, `metrics_svc` |
| `job.waitlist_released` | `job_id`, `waitlist_entry_id` | `scheduler` | `job_svc`, `inbox_proj` |
| `job.waitlist_expired` | `job_id`, `waitlist_entry_id` | `scheduler` | `inbox_proj` |
| `job.escrow_confirmed` | `job_id`, `escrow_id`, `amount_ucr` | `ledger_svc` | `job_svc`, `cell_svc` |
| `job.started` | `job_id`, `first_cell_id` | `cell_svc` | `metrics_svc` |
| `job.paused` | `job_id`, `cause (kill_switch, template, service, policy_tightening)`, `ref_id` | `job_svc` | `cell_svc`, `inbox_proj` |
| `job.resumed` | `job_id` | `job_svc` | `cell_svc` |
| `job.all_cells_accepted` | `job_id`, `cells_total` | `cell_svc` | `job_svc` |
| `job.assembled` | `job_id`, `deliverable_id`, `manifest_id` | `job_svc` | `ledger_svc`, `public_proj` |
| `job.stop_requested` | `job_id`, `closure_reason (policy_stopped, service_revoked, template_retired, operator_killed, overrun_timeout)` | `job_svc`, `config_svc` | `cell_svc`, `ledger_svc` |
| `job.settled` | `job_id`, `levy_ucr`, `refund_ucr` | `ledger_svc` | `job_svc`, `inbox_proj`, `metrics_svc` |
| `job.settled_partial` | `job_id`, `accepted_cells`, `refund_ucr` | `ledger_svc` | `job_svc`, `inbox_proj`, `metrics_svc` |
| `job.cancel_requested` | `job_id` | `job_svc` | `cell_svc`, `ledger_svc` |
| `job.cancel_settled` | `job_id`, `refund_ucr` | `ledger_svc` | `job_svc`, `inbox_proj` |
| `cell.created` | `cell_id`, `job_id`, `kind`, `attempt` | `cell_svc` | `verify_svc` |
| `cell.leased` | `cell_id`, `lease_id`, `member_id` | `cell_svc` | `metrics_svc` |
| `cell.submitted` | `cell_id`, `submission_id` | `cell_svc` | `verify_svc` |
| `cell.lease_expired` | `cell_id`, `lease_id` | `scheduler` | `cell_svc` |
| `cell.declined` | `cell_id`, `lease_id` | `cell_svc` | `metrics_svc` |
| `cell.checks_passed` | `cell_id`, `submission_id`, `method` | `verify_svc` | `cell_svc`, `ledger_svc` |
| `cell.flagged_for_audit` | `cell_id`, `audit_id`, `reason` | `verify_svc` | `verify_svc` |
| `cell.checks_failed` | `cell_id`, `submission_id`, `reject_reason` | `verify_svc` | `cell_svc`, `identity_svc` |
| `cell.audit_passed` | `cell_id`, `audit_id` | `verify_svc` | `ledger_svc`, `cell_svc` |
| `cell.audit_failed` | `cell_id`, `audit_id` | `verify_svc` | `cell_svc`, `identity_svc` |
| `cell.requeued` | `cell_id`, `attempt` | `cell_svc` | `metrics_svc` |
| `cell.attempts_exhausted` | `cell_id`, `job_id` | `cell_svc` | `job_svc` |
| `cell.paused`, `cell.resumed` | `cell_id`, `cause` | `cell_svc` | `metrics_svc` |
| `cell.cancelled` | `cell_id`, `job_id` | `cell_svc` | `ledger_svc` |
| `cell.voided` | `cell_id`, `cause (service_revoked, policy_stop, integrity_finding)` | `cell_svc` | `ledger_svc`, `job_svc` |
| `cell.overturned` | `cell_id`, `via (appeal, fraud_finding)`, `rework_cell_id` | `verify_svc` | `ledger_svc`, `cell_svc` |
| `lease.issued`, `lease.submission_received`, `lease.expired`, `lease.released`, `lease.revoked` | `lease_id`, `cell_id`, `member_id` | `cell_svc` | `metrics_svc` (`lease.revoked` also `inbox_proj`) |
| `submission.received`, `submission.schema_failed`, `submission.checks_passed`, `submission.checks_failed`, `submission.quarantined`, `submission.accepted`, `submission.rejected`, `submission.released_from_quarantine` | `submission_id`, `cell_id`, `reason_code?` | `cell_svc`, `verify_svc` | `verify_svc`, `inbox_proj` (rejections), `metrics_svc` |

### 15.34.3 Catalog: member, template, service, appeal, audit, escrow, reservation, report

| Event | Payload (besides envelope) | Producer | Consumers |
| --- | --- | --- | --- |
| `member.created` | `member_id`, `invite_id?` | `identity_svc` | `ledger_svc`, `analytics` |
| `member.tier_promoted`, `member.tier_demoted` | `member_id`, `from_tier`, `to_tier` | `identity_svc` | `verify_svc`, `inbox_proj` |
| `member.restricted`, `member.restriction_lifted` | `member_id`, `reason_code`, `action_id` | `admin_svc` or `identity_svc` (automatic on `trust.restrict_after_gold_fails`) | `verify_svc`, `inbox_proj` |
| `member.suspended`, `member.reinstated`, `member.banned` | `member_id`, `reason_code`, `action_id`, `approval_id?` | `admin_svc` | `cell_svc` (revoke leases), `identity_svc` (revoke sessions), `inbox_proj` |
| `member.closed` | `member_id`, `cause (member, inactivity)` | `identity_svc` | `ledger_svc` |
| `member.key_rotated`, `member.device_linked`, `member.recovered`, `member.optin_changed` | `member_id` | `identity_svc` | `analytics` (`member.optin_changed` also `cell_svc`) |
| `template.version_created` | `template_id`, `template_version_id`, `version` | `template_svc` | `analytics` |
| `template.review_requested` | `template_version_id`, `required_approvals` | `template_svc` | `inbox_proj` (reviewers) |
| `template.first_approved` | `template_version_id`, `admin_id`, `final (bool)` | `template_svc` | `public_proj` when `final` |
| `template.second_approved` | `template_version_id`, `admin_id` | `template_svc` | `public_proj`, `job_svc` |
| `template.changes_requested`, `template.rejected` | `template_version_id`, `admin_id`, `review_id` | `template_svc` | `inbox_proj` |
| `template.paused`, `template.resumed` | `template_id`, `switch_key` | `config_svc` | `job_svc`, `cell_svc`, `public_proj` |
| `template.retired` | `template_version_id`, `reason_code` | `template_svc` | `job_svc`, `public_proj` |
| `service.created` | `service_id` | `registry_svc` | `analytics` |
| `service.terms_copy_sealed` | `service_id`, `terms_copy_id`, `sha256` | `registry_svc` | (audit only) |
| `service.flags_recorded` | `service_id`, `terms_copy_id`, `flag_keys` | `registry_svc` | (audit only) |
| `service.review_started`, `service.rejected` | `service_id` | `registry_svc` | `public_proj` |
| `service.approved` | `service_id`, `terms_copy_id`, `approved_by` | `registry_svc` | `public_proj`, `policy_svc`, `config_svc` (launch rule) |
| `service.review_due`, `service.review_lapsed` | `service_id` | `scheduler` | `registry_svc`, `job_svc` |
| `service.suspended`, `service.resumed` | `service_id`, `switch_key` | `config_svc` | `job_svc`, `cell_svc`, `public_proj` |
| `service.revoked` | `service_id`, `reason_code`, `affected_open_jobs` | `registry_svc` | `job_svc`, `cell_svc`, `ledger_svc`, `public_proj`, `config_svc` |
| `appeal.filed` | `appeal_id`, `kind`, `subject_ref` | `identity_svc` | `inbox_proj` (reviewers) |
| `appeal.assigned`, `appeal.reassigned`, `appeal.review_started`, `appeal.second_review_requested` | `appeal_id`, `admin_id` | `admin_svc` | (audit only) |
| `appeal.upheld`, `appeal.overturned` | `appeal_id`, `kind`, `subject_ref`, `decision_count` | `admin_svc` | `identity_svc`, `verify_svc`, `template_svc`, `ledger_svc` (per `kind`), `inbox_proj` |
| `appeal.withdrawn` | `appeal_id` | `identity_svc` | (audit only) |
| `audit.created`, `audit.second_submitted`, `audit.matched`, `audit.mismatched`, `audit.third_requested`, `audit.third_submitted` | `audit_id`, `cell_id` | `verify_svc` | `verify_svc`, `metrics_svc` |
| `audit.resolved`, `audit.cancelled` | `audit_id`, `cell_id`, `verdict?`, `actor` | `verify_svc` or `admin_svc` | `cell_svc`, `ledger_svc`, `identity_svc` |
| `escrow.opened`, `escrow.settling_started`, `escrow.closed` | `escrow_id`, `job_id` or `reservation_id` | `ledger_svc` | `job_svc` |
| `reservation.held`, `reservation.activated`, `reservation.cancelled`, `reservation.expired` | `reservation_id`, `member_id`, `window_start` | `job_svc` | `ledger_svc`, `metrics_svc` |
| `report.filed` | `report_id`, `category`, `subject_ref` | `identity_svc` | `config_svc` (template autopause counter) |
| `report.triaged`, `report.actioned`, `report.dismissed` | `report_id`, `action_ids?` | `admin_svc` | `inbox_proj` |

### 15.34.4 Catalog: ledger, configuration, launch, kill switches

| Event | Payload (besides envelope) | Producer | Consumers |
| --- | --- | --- | --- |
| `ledger.entry_committed` | `entry_id`, `seq`, `txn_id`, `entry_type`, `amount_ucr`, `entry_hash` | `ledger_svc` | `public_proj`, `metrics_svc` |
| `ledger.invariants_passed` | `check_ids`, `ran_at` | `ledger_svc` | `public_proj`, `config_svc` (launch rule) |
| `ledger.invariant_violated` | `check_id`, `invariant_id`, `severity` | `ledger_svc` | `config_svc` (freeze per 15.28.3), `admin_svc` (alarm) |
| `parameter.changed` | `parameter_name`, `parameter_version_id`, `version`, `change_class`, `effective_from`, `changelog_entry_id` | `config_svc` | `public_proj`, `analytics` |
| `parameter.activated` | `parameter_name`, `parameter_version_id`, `config_epoch` | `scheduler` | every component that caches parameters |
| `parameter.change_withdrawn` | `parameter_name`, `parameter_version_id` | `config_svc` | `public_proj` |
| `policy.version_published` | `policy_id`, `policy_version_id`, `version`, `change_class`, `effective_from` | `policy_svc` | `public_proj` |
| `policy.version_activated` | `policy_id`, `policy_version_id`, `change_class` | `policy_svc` (at once for `tighten`, `scheduler` for `loosen`) | `job_svc` (R9 pause), `cell_svc`, `public_proj` |
| `policy.version_cancelled` | `policy_version_id` | `policy_svc` | `public_proj` |
| `changelog.entry_published` | `changelog_entry_id`, `kind`, `change_class`, `subject` | `config_svc` | `public_proj`, `admin_svc` (explanation timer) |
| `feature_flag.changed` | `flag_key`, `enabled`, `exposure_ppm` | `config_svc` | `public_proj`, `analytics` |
| `launch.members_may_join_changed`, `launch.member_jobs_enabled_changed`, `launch.minting_enabled_changed` | `value`, `approval_id?` | `config_svc` | `identity_svc`, `job_svc`, `ledger_svc`, `public_proj` |
| `gate.evidence_attached`, `gate.signed_off`, `gate.reopened` | `item_id`, `gate_id`, `admin_id?` | `config_svc` | `admin_svc` (launch status; `gate.reopened` raises the `launch.rule_broken` alarm when a switch is on) |
| `killswitch.engaged` | `switch_key`, `reason_code`, `linked_alarm_id?` | `config_svc` | per 15.28.1 |
| `killswitch.released` | `switch_key`, `approval_id` | `config_svc` | per 15.28.1 |
| `preregistration.locked` | `prereg_id`, `content_hash`, `approval_id` | `config_svc` | `public_proj` |
| `experiment.started`, `experiment.stopped` | `experiment_id`, `flag_key`, `seed_version` | `config_svc` | `analytics`, `identity_svc` (assignments) |
| `calibration.recorded` | `calibration_id`, `service_id` | `admin_svc` | (audit only) |
| `milestone.published` | `milestone_id`, `key` | `config_svc` | `public_proj` |
| `sharecard.created`, `sharecard.revoked` | `share_card_id` (not the token) | `api` | `public_proj` |
| `sharecard.viewed` | `share_card_id`, `date` | `public_proj` | `analytics` |
| `alarm.raised` | `alarm_id`, `category`, `kind`, `severity` | any component | `admin_svc` |
| `alarm.acknowledged` | `alarm_id`, `admin_id` | `admin_svc` | (audit only) |

### 15.34.5 Catalog: admin and timers

| Event | Payload (besides envelope) | Producer | Consumers |
| --- | --- | --- | --- |
| `admin.session_started`, `admin.session_ended` | `admin_id`, `session_id` | `admin_svc` | `analytics` (counts only) |
| `admin.step_up_verified` | `admin_id`, `op` | `admin_svc` | (audit only) |
| `admin.user_enrolled`, `admin.user_deactivated`, `admin.roles_changed`, `admin.credential_added`, `admin.credential_removed` | `admin_id`, `by_admin_id` | `admin_svc` | (audit only) |
| `admin.approval_requested`, `admin.approval_granted`, `admin.approval_rejected`, `admin.approval_withdrawn`, `admin.approval_expired`, `admin.approval_failed` | `approval_id`, `action_name`, `admin_id?` | `admin_svc`, `scheduler` for `expired` | `inbox_proj` (the other admins) |

Timers are produced by the `scheduler` and are events like any other: `quote_expired`, `waitlist_released`, `waitlist_expired`, `lease_expired`, `service.review_due`, `service.review_lapsed`, `parameter.activated`, `policy.version_activated` (for `loosen`), `admin.approval_expired`, the daily ledger checkpoint, the lot-expiry `expire` postings and `reserve` `retire` postings (S6.*). Names listed here that are not in S0 0.9 (`service.terms_copy_sealed`, `service.flags_recorded`, `policy.version_activated`, `policy.version_cancelled`, `parameter.activated`, `parameter.change_withdrawn`, `feature_flag.changed`, `launch.member_jobs_enabled_changed`, `launch.minting_enabled_changed`, `preregistration.locked`, `experiment.started`, `experiment.stopped`, `calibration.recorded`, `milestone.published`, `sharecard.*`, `alarm.*`, `admin.*`) are convention additions (`ISS-154`).

## 15.35 Webhook-free by design [D]

Hamyar sends nothing to its volunteers, requesters or any third party on its own initiative.

- **No webhooks, no callbacks, no push, no e-mail or SMS to members, no server-sent streams.** Clients poll with `ETag` / `If-None-Match` (S0 0.11.7). The member inbox (part a) is a read model fed by `inbox_proj`; reading it is a pull.
- **No outbound request to any address a user or admin typed.** A service's URL template, a milestone's `output_ref.url`, a terms copy's `source_ref` and every other address are stored text. The server does not fetch them, so there is no server-side request forgery surface and no way to make the platform scrape a provider.
- **Why:** a volunteer's identity must not leak to a requester or provider through a callback URL (S0 0.7); a webhook sender is also an unbounded outbound-abuse surface for a tiny team. Operators are alerted through the Operator tools, which read `Alarm` (15.29.4) and the metrics of S4.*, not through messages the platform sends.
- **Third-party consumers of public data** use the public endpoints (15.33), which are cacheable and need no registration.
- If a later phase needs outbound notification, it is a new scope with its own threat model, not an extension of this file [A].

## 15.36 Worked examples

Illustrative values only: the service, the terms text, the counts and every flag answer below are placeholders about a hypothetical service and are not facts about any provider [V]. Ids use the format of S0 0.6.3. Headers other than `Idempotency-Key` are omitted.

### 15.36.1 Record flags, seal a terms copy, approve a service

```
POST /v1/admin/services/svc_01j9z6x4k7q2m8v5t3r1w0c9ab/reviews
Idempotency-Key: 7d5c1f0e-1a2b-4c3d-8e9f-0a1b2c3d4e5f
{ "reason": "first review" }
-> 201 { "svc_id": "svc_01j9z6x4k7q2m8v5t3r1w0c9ab", "state": "in_review", ... }

POST /v1/admin/services/svc_01j9z6x4k7q2m8v5t3r1w0c9ab/terms-copies
{ "source_ref": "terms page as read by reviewer on 2026-12-02 (placeholder)", "captured_on": "2026-12-02",
  "media_type": "text/plain", "size_bytes": 48213,
  "sha256": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08" }
-> 201 { "tcp_id": "tcp_01j9z6x5a2b3c4d5e6f7g8h9jk", "status": "uploading", "chunk_raw_max_bytes": 785408, "chunk_count": 1, ... }

PUT  /v1/admin/terms-copies/tcp_01j9z6x5a2b3c4d5e6f7g8h9jk/chunks/0     { "data_base64": "..." }   -> 200 { "n": 0, "bytes": 48213, "received_count": 1 }
POST /v1/admin/terms-copies/tcp_01j9z6x5a2b3c4d5e6f7g8h9jk/seal         {}                          -> 200 { ..., "status": "sealed" }

POST /v1/admin/services/svc_01j9z6x4k7q2m8v5t3r1w0c9ab/flag-answers
{ "terms_copy_id": "tcp_01j9z6x5a2b3c4d5e6f7g8h9jk", "reason": "read the saved copy",
  "answers": [
    { "flag_key": "third_party_task_use", "answer": "yes", "quote_ref": "saved copy, section 4, paragraph 2 (placeholder)" },
    { "flag_key": "prohibited_content_compatible", "answer": "yes", "quote_ref": "saved copy, section 7 (placeholder)" },
    { "flag_key": "prefilled_link_use", "answer": "unknown" } ] }
-> 201 { "data": [ { "fla_id": "fla_...", "flag_key": "third_party_task_use", "answer": "yes", ... }, ... ] }

GET /v1/admin/services/svc_01j9z6x4k7q2m8v5t3r1w0c9ab/flags
-> 200 { "flags": [ ..., { "flag_key": "human_copy_paste_use", "answer": "unknown", "source": "default_unknown" } ],
         "gates_ready": true, "missing": [] }
```

`gates_ready` is true because approval needs only the two gate flags of FD§5.3; `prefilled_link_use` stays `unknown`, so the adapter is `copy_only` (no link). Approving:

```
POST /v1/admin/services/svc_01j9z6x4k7q2m8v5t3r1w0c9ab/approvals
{ "reviewed_terms_copy_id": "tcp_01j9z6x5a2b3c4d5e6f7g8h9jk", "reason": "gate flags recorded with quotes", "step_up": { "challenge_id": "...", "assertion": { ... } } }
-> 200 { "state": "approved", "approved_at": "2026-12-02T09:14:03Z", "review_due_at": "2027-03-02T09:14:03Z", "adapter": { "copy_only": true, ... } }
```

The same call before the second gate answer was recorded fails and changes nothing:

```
-> 409 { "error": { "code": "STATE_CONFLICT", "message": "approval guard failed",
         "details": { "reason": "approval_guard_failed", "missing": ["gate_flag_not_yes:prohibited_content_compatible"] },
         "request_id": "req_01j9z6y0a1b2c3d4e5f6g7h8jk" } }
```

### 15.36.2 Tighten a policy at once; try to loosen with the wrong endpoint; loosen with notice

```
POST /v1/admin/policies/pol_01j9z2c3d4e5f6g7h8j9k0m1n2/tightenings
{ "base_version_id": "plv_01j9z4a5b6c7d8e9f0g1h2j3k4", "reason": "sensitive-looking inputs slipped through; lock the S1 + M0 pairing for P1",
  "allowlist": [ { "purpose": "P1", "license": "L2", "sensitivity": "S1", "service_requirement": "M0", "status": "locked" } ],
  "step_up": { ... } }
-> 201 { "policy_version": { "plv_id": "plv_01j9z8e9f0g1h2j3k4m5n6p7q8", "version": 5, "change_class": "tighten", "status": "active",
                           "effective_from": "2026-12-02T10:00:00Z" },
         "changelog_entry": { "chg_id": "chg_01j9z8f1g2h3j4k5m6n7p8q9r0", "explanation_due_at": "2026-12-03T10:00:00Z" },
         "impact": { "jobs_in_flight_affected": 2, "cells_queued_affected": 61 } }     # counts are illustrative
```

The event `policy.version_activated` follows; the job service pauses what no longer passes (R9). The reviewer then posts the human explanation with `annotateChangeLog` before `explanation_due_at`.

Sending a change that also unlocks a row to the same endpoint is refused:

```
-> 422 { "error": { "code": "UNPROCESSABLE", "message": "change contains loosening",
         "details": { "reason": "contains_loosening", "loosening": ["allowlist:P1/L2/S0/M1 locked->allowed"] }, "request_id": "req_..." } }
```

The loosening goes to `POST .../loosenings` alone, with `public_text` in `fa` and `en`. The answer is `202` with an `AdminApproval` (`action_name: policy.loosen`). When a second reviewer approves with a step-up bound to the stored payload, the version is created as `scheduled` with `effective_from = approved_at + 7 days` and the change-log entry is published at that moment, so the public notice period starts at approval and not at the proposal.

### 15.36.3 Engage a template kill switch, see the effect, release it with two admins

```
POST /v1/admin/kill-switches/kill.template.tpl_01j9z3k4m5n6p7q8r9s0t1v2w3/engagements
{ "reason_code": "abuse", "reason": "5 reports in 20 minutes: outputs asking volunteers to open links",
  "public_text": { "fa": "...", "en": "Template paused while we review reports." }, "linked_report_id": "rpt_01j9z6d7e8f9g0h1j2k3m4n5p6", "step_up": { ... } }
-> 201 { "switch": { "switch_key": "kill.template.tpl_01j9z3k4m5n6p7q8r9s0t1v2w3", "state": "engaged" },
         "effects": { "jobs_paused": 3, "cells_paused": 44, "leases_revoked": 7 } }          # counts are illustrative
```

From now on a member creating a job with that template gets:

```
-> 503 { "error": { "code": "KILL_SWITCH_ENGAGED", "message": "template paused", "details": { "copy_key": "copy.template.paused" }, "request_id": "req_..." } }
```

Release needs a second admin and a verification checklist:

```
POST /v1/admin/kill-switches/kill.template.tpl_01j9z3k4m5n6p7q8r9s0t1v2w3/releases
{ "reason": "template text fixed in new version; reports closed", "verification": [ { "check": "active version still approved", "passed": true } ], "step_up": { ... } }
-> 202 { "apv_id": "apv_01j9z7a1b2c3d4e5f6g7h8j9km", "action_name": "killswitch.release", "status": "pending", "required_approvals": 2, "expires_at": "2026-12-03T11:30:00Z" }

POST /v1/admin/approvals/apv_01j9z7a1b2c3d4e5f6g7h8j9km/approvals          # a different admin, step-up bound to the stored payload
-> 200 { "approval": { "status": "approved" }, "result": { "switch": { "state": "released" } } }
```

Events in order: `killswitch.engaged`, `template.paused`, `job.paused`, `cell.paused`, `lease.revoked`; later `killswitch.released`, `template.resumed`, `job.resumed`, `cell.resumed`.

## 15.37 Acceptance criteria

Ids follow `AC-<area>-<nn>` (S17.* may renumber). "Given" always includes a freshly migrated system with all `launch.*` switches false (S0 0.12 ordering rule 3).

| id | Given | When | Then |
| --- | --- | --- | --- |
| `AC-admin-01` | A service `in_review` with no sealed terms copy | `approveService` is called | `409 STATE_CONFLICT`, `details.missing` contains `terms_copy_missing`; the state is unchanged; one failed attempt is not an event |
| `AC-admin-02` | A service whose `prohibited_content_compatible` is `unknown` | `approveService` is called | `409`, `details.missing` contains `gate_flag_not_yes:prohibited_content_compatible` (unknown evaluates as no) |
| `AC-admin-03` | An `in_review` service and a sealed copy | `recordFlagAnswers` sends a `yes` on a gate flag without `quote_ref` | `400 VALIDATION_FAILED`; no answer is stored |
| `AC-admin-04` | A terms copy declared with a `sha256` that does not match the chunks | `sealTermsCopy` is called | `400 VALIDATION_FAILED` `hash_mismatch`; the copy stays `uploading`; nothing is sealed |
| `AC-admin-05` | `service.terms_copy_max_bytes` = 5,242,880 and `api.max_body_bytes` = 1,048,576 | A 5,242,880-byte copy is created and uploaded | `chunk_count` = 7, `chunk_raw_max_bytes` = 785,408, every chunk request is under `api.max_body_bytes`, `seal` succeeds; a declared 5,242,881 bytes is `400` |
| `AC-admin-06` | A template version authored by admin A | A calls `submitTemplateReview` with `approve` | `403 FORBIDDEN`; no review is stored |
| `AC-admin-07` | A new template (`template.min_reviewers_new` = 2) | Two different non-author reviewers approve | After the first: `awaiting_second_review`, event `template.first_approved`; after the second: `approved`, `template.second_approved`; the same reviewer approving twice is `403` |
| `AC-admin-08` | An active policy version | `tightenPolicy` with a tightening-only diff | `201`; the version is active before the response; `policy.version_published`, `policy.version_activated`, `changelog.entry_published` are emitted; `explanation_due_at` = now + `change.tighten_publish_within_s` |
| `AC-admin-09` | A diff that tightens one row and loosens another | Sent to `tightenPolicy` or to `loosenPolicy` | `422 UNPROCESSABLE` (`contains_loosening` or `contains_tightening`); nothing is stored |
| `AC-admin-10` | A loosening approved at time T | The version is read before and after `T + policy.loosen_min_notice_days` | Status `scheduled` with `effective_from` >= T + 7 days; the public change-log entry exists from T; the version becomes `active` only at `effective_from` |
| `AC-admin-11` | The parameter `price.levy_lambda` raised | `proposeParameterChange` | Class `loosen` (per its declared direction), `202` approval; after approval `effective_from` >= approval time + 14 days (`change.notice_days_price`) |
| `AC-admin-12` | A `constant` parameter, or a `launch.*` name | `proposeParameterChange` | `422 UNPROCESSABLE` with `immutable_constant` or `use_launch_endpoints` |
| `AC-admin-13` | A parameter still at its initial configurable default | The first change is sent without `calibration_source` | `400 VALIDATION_FAILED`; with `code = CAL` and fewer than `calibration.min_samples_per_service` completed cells for an approved service in scope it is `400`; with enough it succeeds |
| `AC-admin-14` | A credit lot earned under `credit.lifetime_days` = 60 | The parameter is changed to 90 and becomes effective | The existing lot keeps its original expiry; only lots created after `effective_from` use 90 |
| `AC-admin-15` | A `2P` action initiated by admin A | A calls `approveApproval`; then B approves with a step-up bound to another payload | Both `403` or `401 AUTH_INVALID` (`step_up_invalid`); B with the correct step-up executes it; the action runs once |
| `AC-admin-16` | A pending approval whose guard no longer holds at approval time | The approver approves | `409 STATE_CONFLICT`, `approval.status = failed`, nothing executed |
| `AC-admin-17` | `launch.required_gate_ids` = G0, G1, with G1 not signed off | `changeLaunchSwitch` for `members_may_join` with `true` | `409`, `details.blockers` lists `gate_not_signed_off:G1`; the switch stays false; the same call with `false` is accepted at once |
| `AC-admin-18` | A gate item with one sign-off and `launch.min_signoffs` = 2 | The same admin signs again; then new evidence is attached; then a second admin signs | `403`; the first sign-off is voided by the evidence; the second admin's sign-off leaves the item `evidence_attached` (1 of 2) |
| `AC-admin-19` | An engaged `kill.service.<svc_id>` whose cause was a kill switch | `releaseKillSwitch` while a gate flag is no longer `yes` | `409 release_guard_failed`; a revoked service can never be released |
| `AC-admin-20` | The ledger explorer | Any non-`GET` request to `/v1/admin/ledger/*` other than the runs, verifications and reversals | `404` or `405`; there is no endpoint that creates, edits or deletes an entry |
| `AC-admin-21` | A posted entry E | `reverseLedgerEntry` by one admin, then approval by a second | After the first: `202` and no posting; after the second: mirror entries with `reverses_entry_id = E`, E itself unchanged, `ledger.entry_committed` per new entry |
| `AC-admin-22` | A member with no linked report, alarm or audit | `banMember` | `400 VALIDATION_FAILED`; with a link it is `202` and needs a second admin |
| `AC-admin-23` | Any admin write | The transaction that writes the `AdminAction` row is forced to fail | The state change is rolled back; no event is emitted |
| `AC-admin-24` | An admin reads member detail, ledger lots of a member or audit content | The read completes | One `AdminAction` of kind `read` exists for it |
| `AC-admin-25` | An experiment with no locked pre-registration that lists it | `startExperiment` | `422 prereg_not_locked`; after locking (two admins) it starts; a locked pre-registration cannot be updated (`409`) |
| `AC-admin-26` | A milestone without `output_ref` | `publishMilestone` | `422 output_ref_required` |
| `AC-admin-27` | A login with a wrong signature, an unknown credential and an expired challenge | Three `createAdminSession` calls | The same `401` body for all three; a replayed valid assertion fails because the challenge is burned |
| `AC-admin-28` | The two sensitive calls `engageKillSwitch` and `proposeParameterChange` | Called with a bearer token and no `step_up` | `401 AUTH_INVALID`, `details.reason = step_up_required` |
| `AC-public-01` | `ff.growth.v2_live_counter` off | `GET /v1/public/counter` | `404 NOT_FOUND`; with the flag on and fewer than `analytics.min_cohort_k` active members, `members_active_today` is `null` |
| `AC-public-02` | Entries posted 100 s ago and `public.ledger_lag_s` = 300 | `GET /v1/public/ledger/summary` | Those entries are not in the figures; `identity_check.sum_of_all_balances_ucr` is `"0"`; no member account or entry list appears |
| `AC-public-03` | Parameters with `public` false (for example `security.*`) | `GET /v1/public/parameters` | They are absent; scheduled values appear under `scheduled` with their `effective_from` |
| `AC-public-04` | A published change-log entry | An admin wants to correct it | There is no edit; `annotateChangeLog` creates a new entry with `amends_id` |
| `AC-public-05` | A share card revoked by its member | `GET /v1/public/share-cards/{token}` for it and for a random token | Both `404` with the same body; a live card shows only `cells_verified`, `badge_key`, `issued_month`, `locale` |
| `AC-public-06` | A stored manifest | `verifyManifest` with the exact export, with one changed field, and with an unknown manifest | `match` with `recorded`; `mismatch` with JSON pointers only; `unknown`; every positive result carries `limits_copy_key`; the server makes no outbound request |
| `AC-public-07` | Any public endpoint | A request is made | No `Set-Cookie`; `Cache-Control: public, max-age` <= `public.counter_refresh_s`; `ETag` and `304` work |
| `AC-event-01` | A state change and a forced crash after the database commit | The relay restarts | The event is published exactly once or at least once, never lost; a consumer replay with the same `event_id` has no second effect |
| `AC-event-02` | A request refused by a guard | Any of the above refusals | No event is stored; no state changes |
| `AC-event-03` | Every event in 15.34 | Its payload is inspected | It contains only ids, enums, counts, hashes and parameter names; no personal data, prompt, output or terms text |

## Issues raised

Problems and gaps found while writing this part. Each resolution is already applied in this file; `C-001` consolidates them into S2.* and may record a different resolution. [D]

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-154` | major | FD§5.4 R10, FD§5.7 failure mode 10, FD§9 | S0 lacks names this part needs: (1) entities `AdminApproval` (`apv_`), `ShareCard` (`shc_`) and `Milestone` (`mls_`); (2) fields `TermsCopy.status`, `ParameterVersion.withdrawn_at`, `PreRegistration.status` and `content_hash`, `Experiment.status` and `fraction_source`; (3) `ChangeLogEntry.kind` values `kill_switch`, `launch_switch`, `feature_flag`, `preregistration_lock`, `milestone`, `note` and the field `amends_id`; (4) parameters `ratelimit.admin_write_cost` (int, initial configurable default 2), `ratelimit.admin_auth_attempts_per_hour` (10), `ratelimit.public_verify_cost` (5), `session.admin_stepup_ttl_s` (300), `security.approval_ttl_s` (86,400), `launch.require_locked_preregistration` (bool, true), `growth.share_card_max_active` (3), all owned by the areas of 0.10.5; (5) names added to `security.two_person_actions`: `policy.loosen`, `launch.switch_on`, `admin.enroll`, `admin.role_change`, `member.ban`, `preregistration.lock` and, when `service.min_approvers` > 1, `service.approve`; (6) the events listed at the end of 15.34.5 and the envelope field `config_epoch`; (7) `ff.growth.v4_teams` and `ff.job.reservations` exist in S0 but not in part-a examples | All applied as written in 15.21 to 15.34. `C-027` or the next convention edit should fold them into 0.7 to 0.10 without renaming | proposed |
| `ISS-155` | major | FD§5.3, FD§5.6, Principle 5 | Three transport and privacy decisions conflict with a literal reading of S0 or the FD: (1) the API is JSON only with `api.max_body_bytes` = 1,048,576, yet `service.terms_copy_max_bytes` = 5,242,880 and uploads "use `job.max_upload_bytes`" only for requester data; (2) S0 0.11.5 requires `Idempotency-Key` on every admin write, but replaying a stored login or credential response would store a session token or credential options; (3) Principle 5 makes the ledger public, but a per-entry public feed would let timing link a public movement to a member | (1) Terms copies are uploaded as base64 chunks of at most `floor(api.max_body_bytes * 3 / 4) - 1024` raw bytes and sealed by hash (15.23.2). (2) The three unauthenticated admin endpoints (`startAdminLogin`, `createAdminSession`, `createCredentialChallenge`) take the key as optional; every challenge is single use (15.21.3, 15.22). (3) The public ledger shows lagged aggregates, daily checkpoint hashes and an identity check, not per-entry data; third parties verify totals and checkpoints, and the full hash chain only by an auditor with admin read access (15.33.3) | proposed |
| `ISS-156` | minor | FD§5.6, FD§8.3, FD§9 | Dependencies on parts this cell could not read: (1) part a (15a) section numbers, and whether it already defines share-card member operations; (2) S4.* component names and outbox row; (3) S10.* permission matrix, admin bootstrap and credential-loss procedure; (4) S6.* rule for deferred mint postings under `kill.all_minting` and for freezing on a critical invariant violation; (5) S13.* and S14.* placement of the "pre-registration locked" clause of the launch rule; (6) S5.*/S9.* export form of the manifest (volunteer handle omitted) and its hash; (7) S8.* template `definition` schema and S7.* rule `params` | Each is written as an [A] assumption with the smallest possible surface: section numbers start at 15.21; share-card operations are specified once, here (15.33.5), and part a should reference them; component names and `event_id` format are marked [A]; permission names are proposals; the freeze, the launch-rule clause and the manifest export form are isolated in 15.28.3, 15.27.3 and 15.33.6 so an owner can change them without touching any endpoint | proposed |

Convention additions made by this part are listed in `ISS-154`; no other entity, enum or error code was invented. Error codes used are those of S0 0.11.3; `details.reason` values (for example `step_up_required`, `contains_loosening`, `notice_too_short`) are new vocabulary inside `details` and do not add a `code` [D].
