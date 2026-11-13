# 11. Reviewer and operator tools

*Spec part 11c · owner cell C-015 · covers the "Reviewer and Operator tools" bullet of prompt scope F · binding vocabulary is `spec/00-conventions.md` (S0). Written against Founding Document draft v0.1 (FD). Nothing here is legal advice and nothing has been verified against any provider's terms or any law. Facts about the existing Blueprint Panel come only from `docs/source/panel-review.md` (static reading, nothing executed) and stay [V].*

## 11.41 Scope, reading guide and cross-cutting decisions

### 11.41.1 Scope

This part specifies the admin side of Hamyar: twelve tools and three shared screens, each with purpose, roles and permissions, screen blocks, actions with their dangerous-action confirmation (two-person rule where stated), audit events, API names and Given / When / Then criteria. [D]

- State machines are in S0.9 with guards in S5.*..S9.*; this part only calls them. The permission matrix is S10.*; kill-switch effects and the launch rule are S14.*; request and response schemas are S15.*; parameter definitions are S0.10.6 and S16.*. [D]
- Anything this part needs that S0 does not name (entities, parameters, events, fields) is listed in `## Issues raised` as a convention gap and used with the proposed name meanwhile (S0.1). [D]
- Sub-headings of this file are numbered `11.41` upward so they cannot collide with the other S11 files; C-001 renumbers at assembly if they do [A] (`ISS-117`).
- Screen ids: `SCR-rev-nn` (reviewer) and `SCR-ops-nn` (operator); this file owns every `SCR-rev-*` and `SCR-ops-*` id [A]. Acceptance ids: `AC-<area>-<nn>` with the area named per tool. Test fixtures in examples are illustrative inputs, never measurements. [D]

| # | Tool | Section | Roles | Screens |
| --- | --- | --- | --- | --- |
| 1 | Template review queue | 11.45 | `reviewer` | `SCR-rev-01`, `SCR-rev-02` |
| 2 | Service review (flags, terms copies, adapter capabilities) | 11.46 | `reviewer` | `SCR-rev-03`, `SCR-rev-04`, `SCR-rev-05` |
| 3 | Audit queue (audits, quarantine, gold disputes) | 11.47 | `reviewer` | `SCR-rev-06`, `SCR-rev-07` |
| 4 | Appeals | 11.48 | `reviewer` | `SCR-rev-08`, `SCR-rev-09` |
| 5 | Abuse flags and reports | 11.49 | `reviewer`, `operator` | `SCR-rev-10`, `SCR-rev-11` |
| 6 | Ledger explorer and reversal | 11.50 | `operator` (read: `reviewer` for audit context) | `SCR-ops-04`, `SCR-ops-05`, `SCR-ops-06` |
| 7 | Parameter editor | 11.51 | area owner role (S0.10.5) | `SCR-ops-07`, `SCR-ops-08`, `SCR-ops-09` |
| 8 | Capacity dashboard | 11.52 | `operator` | `SCR-ops-10` |
| 9 | Launch-gate checklist | 11.53 | `operator` | `SCR-ops-11`, `SCR-ops-12` |
| 10 | Kill switches | 11.54 | `operator`; `reviewer` for template and service | `SCR-ops-13`, `SCR-ops-14` |
| 11 | Member lookup (minimal data) | 11.55 | `reviewer`, `operator` | `SCR-rev-12` |
| 12 | Release / Hand over (claims, lease release) | 11.56 | `reviewer`, `operator` | `SCR-ops-15`, `SCR-ops-16` |
| shared | Admin home, approvals inbox, audit-trail viewer | 11.43, 11.44 | `reviewer`, `operator` | `SCR-ops-01`, `SCR-ops-02`, `SCR-ops-03` |

### 11.41.2 Cross-cutting decisions

| ID | Decision | Reason |
| --- | --- | --- |
| `AD1` | The admin UI is a separate origin and a separate session store from the member app; its API is `/v1/admin/*` with `auth_scheme` `admin` only. Login is a WebAuthn passkey of an `AdminUser`; there is no shared password, no admin key typed into a page and no admin credential in `localStorage` or a cookie [D][A] | S0.6.4 and S0.11.4; the Panel's single shared password, typed admin key and `bp_owner_key` in `localStorage` are the weaknesses to avoid (panel-review §4.5 items 1, 2, 5) [V] |
| `AD2` | **Direction rule.** An action that makes the platform stricter or safer (pause, revoke, tighten, switch off, reject) needs one admin and takes effect at once. An action that loosens a platform-wide rule, releases a brake, creates credit or releases a withheld result outside automated verification, applies the heaviest member sanction, or discloses an identity link needs two distinct admins [D] | FD§5.4 R10 (tighten at once, loosen with a public entry); FD§5.7 failure mode 10 (reviewer capture); S0.10.3 |
| `AD3` | Every write carries a reason code plus free text of at least `security.admin_reason_min_chars` characters; the text is internal, only the reason code can appear in a public log [D] | Accountability; Principle 5 |
| `AD4` | Four confirmation tiers `CT0`..`CT3` (11.42.2); the tier of every action is fixed in the catalog (11.44.3), not chosen by the client [D] | A dangerous action must be harder than a routine one |
| `AD5` | Every write inserts an `AdminAction` row in the same database transaction as the state change; if the insert fails the change is rolled back. The log is append-only and hash-chained (11.44.2) [D] | Insider risk (prompt I); S0.6.4 |
| `AD6` | Reads of sensitive data are logged too: member lookup, gold answers, submission bodies, handle resolution, member-linked ledger views [D] | A read can leak as much as a write |
| `AD7` | Minimal data: no admin screen shows or stores a raw IP, an e-mail address, a device record, key material, an invite-tree edge outside a farming case, or a volunteer's chat text (S0.7 retention rules; FD Principle 8) [D] | Safety of members in Iran |
| `AD8` | No admin tool exports member-linked data in bulk. Any export (CSV, JSON) contains aggregates only and suppresses cohorts smaller than `analytics.min_cohort_k` [D] | Compelled-disclosure exposure; what is not stored cannot be handed over |
| `AD9` | Fail closed: if fewer distinct eligible admins exist than a two-person action needs, the action is unavailable and the screen says so (`copy.admin.fail_closed_one_admin`); there is no break-glass override [D][A] | A single-person team is an owner decision (`ISS-119`, S3.*) |
| `AD10` | No admin screen stores a provider credential or session, fetches or opens a provider URL on the server, reads a volunteer's chat page or submits anything for a volunteer. A reviewer-entered terms source is text only; the server never requests it (ground rule 3; FD Principle 3) [D] | The human presses Send, always |
| `AD11` | Published or approved records are never edited in place; a correction is a new version or row. There is no soft-delete flag (S0.7) [D] | Public rules, no secret changes (Principle 5) |
| `AD12` | Concurrency: mutable resources carry `ETag` (= `row_version`) and need `If-Match` on write; items that people work on also carry a claim (11.56) [D] | S0.11.7; replaces the Panel's fencing by branch tip `base` (panel-review §3.3) [V] |
| `AD13` | Admin UI locales are `fa` and `en`, full RTL, no third-party CDN or font; admin copy keys are `copy.admin.*` with both texts and the marker `needs_human_and_legal_review` (11.57) [D] | Prompt scope F and I (blocked third-party resources) |

## 11.42 Shell, roles and confirmation tiers

### 11.42.1 Roles

| Role (S0.8.2) | May do (summary; the permission matrix is S10.*) | Never |
| --- | --- | --- |
| `reviewer` | Templates, services, audit queue, appeals, abuse queue, member suspend and restrict, kill switches for one template or one service, minimal member lookup | Ledger reversal, parameter edits in `operator` areas, launch switches, global kill switches |
| `operator` | Ledger explorer, parameters of operator-owned areas, capacity dashboard, launch gates, all kill switches, claim takeover, lease release, member kill switch | Approving their own two-person request; reviewing a template they authored |

One person may hold both roles through one `AdminUser`. A second approver is always a different `AdminUser` and, where the catalog says "operator approver", holds `operator`. Two admin accounts held by one human defeat the rule; admin onboarding is itself a two-person action (S10.*) and the residual risk is stated in S10.* and S19.* [V].

### 11.42.2 Confirmation tiers [D]

| Tier | Used for | What the screen demands |
| --- | --- | --- |
| `CT0` | Reads, claim, comment, preview | Nothing |
| `CT1` | Consequential but reversible or appealable (approve, reject, record a flag answer, decide an appeal) | `BLK-reason`, a summary of what will change, an explicit confirm button that names the action |
| `CT2` | Dangerous single-admin actions (engage a kill switch, revoke, retire, suspend, tighten a parameter, release a lease) | `CT1` plus the `BLK-affected` preview of counts, typing the target id, and a fresh passkey assertion if the last one is older than `session.admin_stepup_s` |
| `CT3` | Two-person actions | `CT2` for the initiator, then an `ApprovalRequest` (11.44.1); the change executes only after a second admin completes their own `CT2` dialog against the identical payload |

### 11.42.3 Shared screen blocks [D]

| Block | Content and rules |
| --- | --- |
| `BLK-header` | Environment label; launch strip (the three `launch.*` switches, each shown as effective = launch switch on AND no matching kill switch engaged); kill strip (count of engaged switches, link to `SCR-ops-13`); session countdown from `session.admin_idle_ttl_s` and `session.admin_abs_ttl_s`; locale, digits and calendar (Jalali and Gregorian, S0.6.2); badge of pending approvals |
| `BLK-list` | Cursor-paged table (S0.11.6), newest first unless stated, filters kept in the URL hash, no total counts, an aging badge per row |
| `BLK-reason` | Reason code select (codes per tool) plus free text with a live counter against `security.admin_reason_min_chars` |
| `BLK-affected` | Dry-run preview from `previewAdminAction` (11.44.4): counts of leases, cells, jobs, submissions, members or services the action would touch, shown before the confirm button becomes active |
| `BLK-diff` | Structured before / after of the record; for parameters also the effective-from schedule |
| `BLK-twoperson` | Initiator, approvers needed and present, payload hash (first 12 hex), expiry countdown, Approve, Reject, Withdraw; each disabled button shows its reason (own request, role missing, not enough admins, expired) |
| `BLK-trail` | Drawer with the `AdminAction` rows for the subject, newest first |
| `BLK-claim` | Holder, time left, Claim, Release, Hand over, Take over (permission-gated, 11.56) |
| `BLK-error` | Maps `error.code` to `details.copy_key` text (S0.11.3); a `412 PRECONDITION_FAILED` offers "reload and reapply", never a silent overwrite |
| `BLK-empty` | Empty states state what feeds the list (for example "nothing is `in_review`"), never a blank page |

### 11.42.4 Admin home (`SCR-ops-01`) [D]

Blocks: `BLK-header`; **My work** (claims I hold, with time left); **Queues** (one row per tool queue: open count, oldest item age, SLA badge using `report.triage_sla_days` and `appeal.reviewer_sla_days`; template and service queues show age only [A]); **Needs second admin** (pending approvals I may decide); **Bottleneck banner** (11.52.3); **Alarms** (`Alarm` rows not acknowledged). Given / When / Then:

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-home-01` | A reviewer without the `operator` role | They open `SCR-ops-01` | Operator-only blocks (ledger alarms, launch strip actions) render read-only or are omitted; no operator API is called (a call would return `403 FORBIDDEN`) |
| `AC-home-02` | A pending approval created by me | I open "Needs second admin" | It is listed under "Waiting for another admin", not under "I can decide" |

## 11.43 Shared screens: approvals inbox and audit-trail viewer

**`SCR-ops-02` Approvals inbox** [D]. Purpose: decide or follow two-person requests. Roles: `reviewer`, `operator`. Blocks: `BLK-header`; tabs "I can decide", "Waiting for another admin", "Closed"; each row is a `BLK-twoperson` card with the action name, subject, reason code, `BLK-diff` of the payload and `BLK-affected` as computed at request time and recomputed now (a difference is highlighted). Actions: `approval.approve`, `approval.reject`, `approval.withdraw` (11.44.3).

**`SCR-ops-03` Audit-trail viewer** [D]. Purpose: read the `AdminAction` log. Roles: `operator` (all rows), `reviewer` (rows of the reviewer areas and their own rows). Blocks: `BLK-list` with filters `action_code`, `admin_user_id`, `subject_type`, `subject_id`, date range (UTC, with local time beside it); row detail with `BLK-diff` of `before_hash` and `after_hash` targets where the record is visible to the viewer; a "Verify chain" button (`verifyAdminActionChain`) that recomputes the hash chain over a chosen range and reports the first break. The viewer has no edit or delete control and no export beyond aggregate counts (`AD8`).

## 11.44 Two-person approvals, the admin action log and the action catalog

### 11.44.1 `ApprovalRequest` [A]

Entity `ApprovalRequest`, table `approval_requests`, prefix `apr_` (unused in S0.7), retention `permanent`, mutable with `row_version`. A `CT3` action endpoint never executes on the initiator's call: it stores the request and returns `202 Accepted` with the `ApprovalRequest`. [D]

| Field | Type | Rule |
| --- | --- | --- |
| `id` | `apr_` id | S0.6.3 |
| `action_code` | text | A `CT3` code from 11.44.3 |
| `subject_type`, `subject_id` | text | The record the action targets (for example `ledger_entry`, `kill_switch`, `launch_gate_item`, `member`) |
| `payload`, `payload_hash` | json, text | The exact parameters of the action; `payload_hash` = `sha256:` over RFC 8785 canonical JSON (S0.6.4). Frozen at creation |
| `initiator_admin_id` | `adm_` id | The requester counts as approval number 1 |
| `required_approvals` | int | Looked up at creation from the rule of the action (11.44.5) and frozen |
| `reason_code`, `reason_text` | text | `AD3` |
| `state` | enum | `pending`, `executed`, `rejected`, `expired`, `withdrawn` |
| `expires_at` | timestamptz | `created_at + security.admin_two_person_pending_ttl_s` seconds (server time) |

```
(none)  --approval.requested-->  pending
pending --approval.executed-->   executed    approvals >= required_approvals and the action's own guards still pass
pending --approval.rejected-->   rejected    any eligible admin, reason required; or system when a guard fails at execution
pending --approval.expired-->    expired     timer
pending --approval.withdrawn-->  withdrawn   initiator only
```

Guards on approve [D]: (1) request is `pending` and not expired; (2) approver is a different `AdminUser` from the initiator and from every earlier approver; (3) approver holds the permission and, if the catalog says so, the `operator` role; (4) the approver's dialog shows the identical `payload_hash` and the approval carries it back (a changed payload is a new request, never an edit); (5) step-up passkey assertion fresher than `session.admin_stepup_s`; (6) at execution all guards of the underlying action are re-evaluated, and if one fails nothing changes, the request becomes `rejected` with actor `system` and reason `precondition_failed`. At most one `pending` request exists per `(action_code, subject_id)`; a second returns `409 ALREADY_EXISTS`. Execution, the `AdminAction` rows and the domain events commit in one transaction (S0.9.1). Counting: `required_approvals` is the number of distinct admins including the initiator, so a value of 2 means the initiator plus one other [D].

### 11.44.2 `AdminAction` log [D]

Append-only, no `updated_at`, no delete path (S0.7). One row per write, per refused write, per logged read and per approval step.

| Field | Rule |
| --- | --- |
| `id` (`act_`), `created_at` | S0.6.3 |
| `principal_type`, `admin_user_id` | `admin` with the `adm_` id, or `system` with null (for timers and automatic pauses) |
| `action_code` | A code from 11.44.3 |
| `subject_type`, `subject_id` | As in `ApprovalRequest`; a member subject is always a `mem_` id and appears only in `member`-scoped codes |
| `approval_request_id` | `apr_` id or null |
| `reason_code`, `reason_text` | Required on writes; absent on plain reads |
| `detail` | json: checklist answers, flag answers, parameter name and version, affected counts; validated per code; never member text, never a raw IP |
| `before_hash`, `after_hash` | `sha256:` of the canonical subject before and after; null for reads |
| `result`, `refusal_code` | `ok` or `refused`; the `error.code` of a refusal (S0.11.3) |
| `request_id` | The `req_` id of the API call |
| `prev_hash`, `entry_hash` | `entry_hash = SHA-256(prev_hash \|\| canonical(row))`; the daily checkpoint hash is stored with the ledger checkpoint (`ledger.checkpoint_interval_s`) [A] |

No field holds an IP address, a user agent, a device fingerprint or a passkey credential id. Action codes are imperative verbs (`template.approve`); domain events are past participles (`template.second_approved`), so the two namespaces never collide. [D]

### 11.44.3 Action catalog [D]

`Dir` is the direction of 11.41 `AD2`: `T` tighten, `L` loosen or release, `C` credit or result creation, `N` neutral, `R` read. `Appr` is the number of distinct admins (11.44.5). The tier column is the default; a `CT3` code listed in `security.two_person_actions` stays two-person, and removing a code from that list is itself a `parameter.loosen`.

| `action_code` | Permission | Tier | Dir | Appr | Domain events emitted |
| --- | --- | --- | --- | --- | --- |
| `claim.acquire` / `claim.release` | `perm.claim.hold` | `CT0` | N | 1 | `workclaim.acquired` / `workclaim.released` |
| `claim.hand_over` | `perm.claim.hold` | `CT1` | N | 1 | `workclaim.handed_over` |
| `claim.take_over` | `perm.claim.take_over` (`operator`) | `CT2` | T | 1 | `workclaim.taken_over` |
| `template.comment` | `perm.template.review` | `CT0` | N | 1 | none |
| `template.request_changes` | `perm.template.review` | `CT1` | N | 1 | `template.changes_requested` |
| `template.approve` | `perm.template.review` | `CT1` | L | `template.min_reviewers_new` or `template.min_reviewers_edit` | `template.first_approved`, `template.second_approved` |
| `template.reject` | `perm.template.review` | `CT1` | T | 1 | `template.rejected` |
| `template.retire` | `perm.template.retire` | `CT2` | T | 1 | `template.retired`, `job.stop_requested` |
| `service.create`, `service.start_review` | `perm.service.review` | `CT1` | N | 1 | `service.created`, `service.review_started` |
| `service.upload_terms_copy`, `service.record_flag`, `service.update_adapter` | `perm.service.review` | `CT1` | N | 1 | none (rows are created) |
| `service.approve` | `perm.service.approve` | `CT1` | L | `service.min_approvers` | `service.approved`, `changelog.entry_published` |
| `service.reject` | `perm.service.review` | `CT1` | T | 1 | `service.rejected` |
| `service.revoke` | `perm.service.revoke` | `CT2` | T | 1 | `service.revoked`, `changelog.entry_published` |
| `audit.reject` / `quarantine.reject` | `perm.audit.decide` | `CT1` | T | 1 | `audit.resolved` and `cell.audit_failed` / `submission.rejected` |
| `audit.accept` / `quarantine.release` | `perm.audit.release` | `CT3` | C | 2 | `audit.resolved` and `cell.audit_passed` / `submission.released_from_quarantine` |
| `gold.view_answer`, `submission.view` | `perm.audit.view_restricted` | `CT1` | R | 1 | none (logged read) |
| `gold.retire` | `perm.audit.decide` | `CT2` | T | 1 | none (convention gap `ISS-117`) |
| `appeal.assign`, `appeal.start_review`, `appeal.reassign`, `appeal.request_second_review` | `perm.appeal.decide` | `CT0` | N | 1 | `appeal.assigned`, `appeal.review_started`, `appeal.reassigned`, `appeal.second_review_requested` |
| `appeal.uphold` | `perm.appeal.decide` | `CT1` | T | 1; `appeal.ban_min_reviewers` for `member_ban` and `template_rejection` | `appeal.upheld` |
| `appeal.overturn` | `perm.appeal.decide` | `CT2` | L | as above | `appeal.overturned` and the remedy events of 11.48.3 |
| `report.triage`, `report.dismiss`, `report.action` | `perm.report.triage` | `CT1` | N | 1 | `report.triaged`, `report.dismissed`, `report.actioned` |
| `member.restrict` | `perm.member.sanction` | `CT2` | T | 1 | `member.restricted` |
| `member.lift_restriction`, `member.reinstate` | `perm.member.sanction` | `CT2` | L | 1 (per-member, appealable, see `AD2`) | `member.restriction_lifted`, `member.reinstated` |
| `member.suspend` | `perm.member.sanction` | `CT2` | T | 1 | `member.suspended` |
| `member.ban` | `perm.member.ban` | `CT3` | T | 2 (`appeal.ban_min_reviewers`) | `member.banned` |
| `job.stop` | `perm.job.stop` | `CT2` | T | 1 | `job.stop_requested` (`closure_reason` `operator_killed`) |
| `cell.void` | `perm.cell.void` | `CT2` | T | 1 | `cell.voided` |
| `cell.overturn` | `perm.cell.overturn` | `CT3` | C | 2 | `cell.overturned`, `ledger.entry_committed` |
| `cell.release` | `perm.cell.release` | `CT2` | T | 1 | `lease.revoked`, `cell.declined` |
| `ledger.reversal` | `perm.ledger.reverse` (`operator`) | `CT3` | C | `ledger.reversal_min_approvers` | `ledger.entry_committed` |
| `alarm.acknowledge` | `perm.alarm.acknowledge` | `CT1` | N | 1 | none |
| `ledger.verify_chain` | `perm.ledger.read` | `CT0` | R | 1 | `ledger.invariants_passed` or `ledger.invariant_violated` |
| `parameter.tighten`, `parameter.neutral`, `parameter.withdraw_pending` | `perm.parameter.edit` (area owner) | `CT2` | T, N, N | 1 | `parameter.changed`, `changelog.entry_published` |
| `parameter.loosen` | `perm.parameter.edit` (area owner) | `CT3` | L | 2 (second `operator` approver) | `parameter.changed`, `changelog.entry_published` |
| `launch.attach_evidence` | `perm.launch.evidence` | `CT1` | N | 1 | `gate.evidence_attached` |
| `launch.signoff` | `perm.launch.signoff` (`operator`) | `CT3` | L | `launch.min_signoffs` | `gate.signed_off`, `launch.members_may_join_changed`, `parameter.changed` |
| `launch.reopen`, `launch.switch_off` | `perm.launch.signoff` | `CT2` | T | 1 | `gate.reopened`; `launch.members_may_join_changed`, `parameter.changed` |
| `killswitch.engage` | `perm.killswitch.engage` (scoped, 11.54) | `CT2` | T | 1 | `killswitch.engaged` and the pause events of 11.54.2 |
| `killswitch.release` | `perm.killswitch.release` | `CT3` | L | 2 | `killswitch.released` and the resume events |
| `member.lookup` | `perm.member.lookup` | `CT1` | R | 1 | none (logged read) |
| `member.resolve_handle` | `perm.member.resolve_handle` (`operator`) | `CT3` | R | 2 | none (logged read) |
| `approval.approve`, `approval.reject`, `approval.withdraw` | per underlying action | `CT2` | n/a | n/a | `approval.executed`, `approval.rejected`, `approval.withdrawn`; `approval.requested` and `approval.expired` (system) |

The `CT3` codes `member.ban`, `audit.accept`, `quarantine.release`, `cell.overturn`, `member.resolve_handle` and `launch.signoff` are proposed additions to the default of `security.two_person_actions` (S0.10.6 lists four names) and are reported in `ISS-117`. [A]

### 11.44.4 Preview and API [D]

Every confirm dialog is driven by one dry-run call, so the screen never computes consequences itself. It changes nothing, returns `tier`, `required_approvals`, `fail_closed` (true when not enough eligible admins exist), validation errors, the `BLK-affected` counts and the `BLK-diff`.

| `op` | Method and path | Permission | Notes |
| --- | --- | --- | --- |
| `previewAdminAction` | `POST /v1/admin/action-previews` | the action's own | Body `{action_code, subject_id, payload}`; no `Idempotency-Key` needed (no write) |
| `listApprovalRequests` / `getApprovalRequest` | `GET /v1/admin/approval-requests[/{apr_id}]` | any admin; rows filtered to what the viewer may decide or started | Filter `state`, `initiated_by_me` |
| `approveApprovalRequest` | `POST /v1/admin/approval-requests/{apr_id}/approvals` | the action's | Body `{payload_hash, reason_code, reason_text}`; `409 STATE_CONFLICT` if not `pending`; `403 FORBIDDEN` for own request |
| `rejectApprovalRequest` / `withdrawApprovalRequest` | `POST .../{apr_id}/rejections`, `.../withdrawals` | as above | Withdraw is initiator only |
| `listAdminActions` / `getAdminAction` | `GET /v1/admin/admin-actions[/{act_id}]` | `perm.audit_trail.read` | Cursor-paged; viewer scope as in `SCR-ops-03` |
| `verifyAdminActionChain` | `POST /v1/admin/admin-action-verifications` | `perm.audit_trail.read` | One verification runs at a time (`429 RATE_LIMITED` otherwise) |

All admin writes need `Idempotency-Key` (S0.11.5) and carry `RateLimit-*` headers against `ratelimit.admin_api_rpm`; repeated refusals of one admin are counted and surfaced to the operator as an `Alarm` (the Panel had no counter on admin-key retries, panel-review §4.5 item 4) [V][A].

### 11.44.5 Where `required_approvals` comes from [D]

| Rule | Source parameter | Mechanism |
| --- | --- | --- |
| New template approval | `template.min_reviewers_new` (default 2), reviewers distinct and not the author | Template machine S0.9.5, not `ApprovalRequest` |
| Edit of an approved template | `template.min_reviewers_edit` | Same |
| Service approval | `service.min_approvers` (default 1; 2 is an owner decision) | Service machine S0.9.6 |
| Ban, and appeal outcomes on bans and template rejections | `appeal.ban_min_reviewers` | Appeal machine S0.9.7 `awaiting_second_review`; a ban itself uses `ApprovalRequest` |
| Ledger reversal | `ledger.reversal_min_approvers` (constant 2) | `ApprovalRequest` |
| Launch sign-off and enabling a switch | `launch.min_signoffs` (default 2) | `ApprovalRequest` |
| Parameter loosen, kill-switch release, audit accept, quarantine release, cell overturn, handle resolution | membership in `security.two_person_actions`; count 2 | `ApprovalRequest` |

### 11.44.6 Acceptance criteria

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-appr-01` | Admin A created a `ledger.reversal` request | A calls `approveApprovalRequest` on it | `403 FORBIDDEN`; an `AdminAction` with `result` `refused` is written; the request stays `pending` |
| `AC-appr-02` | A pending request with `payload_hash` H | B approves with a hash other than H | `409 STATE_CONFLICT`; nothing executes; B's dialog must reload the payload |
| `AC-appr-03` | A pending request older than `security.admin_two_person_pending_ttl_s` | The timer runs | `approval.expired` is emitted by actor `system`; a later approval returns `409 STATE_CONFLICT` |
| `AC-appr-04` | Only one active `AdminUser` holds `operator` | They open a `killswitch.release` dialog | `previewAdminAction` returns `fail_closed` true; the confirm button stays disabled and shows `copy.admin.fail_closed_one_admin` |
| `AC-appr-05` | Between request and second approval the target entry was already reversed | B approves | Execution fails its guard, the request becomes `rejected` by `system` with `precondition_failed`, no ledger entry is written |
| `AC-trail-01` | An action whose state change succeeds but whose `AdminAction` insert fails | The transaction commits | It does not: both roll back and the client gets `503 UNAVAILABLE` |
| `AC-trail-02` | An `AdminAction` row edited directly in the database | `verifyAdminActionChain` runs over its day | The result names the first row whose `entry_hash` no longer matches |

## 11.45 Tool 1: Template review queue

**Purpose.** Move each `TemplateVersion` through the machine of S0.9.5 with published criteria, a second-reviewer rule for new templates and no way to approve one's own work (FD§5.7 failure mode 10). [D]
**Roles and permissions.** `reviewer`: `perm.template.review`, `perm.template.retire`. Guard on every approval: the approver is not the author and is distinct from earlier approvers of that version. Pausing a template is a kill switch (11.54).

**`SCR-rev-01` Queue.** `BLK-list`, oldest first (the one exception to newest-first, so nothing starves). Columns: template name, version, `new` or `edit`, state, approvals `n / required`, age, claim holder, and for approved templates the report count inside `template.autopause_window_s` against `template.autopause_report_count`. Filters: state (`in_review`, `awaiting_second_review`, `changes_requested`, `approved`, `paused`), `job_type`, unclaimed, claimed by me.

**`SCR-rev-02` Review screen.** [D]

| Block | Content |
| --- | --- |
| A Header | `tpv_` id, state, author (`adm_` short id), `BLK-claim`, `BLK-trail` |
| B Diff | `BLK-diff` against the previous approved version: prompt body, data slots, delimiters, output schema, automatic checks, comparator, envelope |
| C Render | The prompt exactly as the volunteer card will show it, with sample data inside the delimiters, escaped; length against `cell.envelope.max_input_chars`; a bidirectional preview with Persian and Latin sample data (S0.6.2 locale rules) |
| D Machine checks | `runTemplateChecks`: schema compiles, checks are deterministic, comparator present, expected output within `cell.envelope.max_output_chars`, `lease.timeout_s >= cell.envelope.expected_time_s` (constraint `C3`). Findings are `blocking` or `advisory`; a blocking finding disables Approve and has no override |
| E Injection and scope lint | Rules of S9.*: links, instruction-like phrases, any slot that could carry a URL or file, any step beyond copy, press Send, return text (`R3`). Same blocking / advisory split |
| F Checklist | The published review criteria, versioned data owned by S8.* [A]; each item ticked by the reviewer; answers stored in the `AdminAction.detail` of the approval |
| G Profile | Purposes, sensitivities, licenses and service requirements the template declares; a warning when it leaves the two active Phase 1 profiles of FD§5.7 failure mode 5 |
| H Effectiveness | A fixed label "effectiveness is a hypothesis [H]"; the screen has no field for an accuracy claim |

**Actions.** `claim.acquire`; `template.comment` (internal text); `template.request_changes` (at least one itemized change, each pointing at a block); `template.approve` (all checklist items ticked, no blocking finding, distinct non-author reviewers; the summary says whether this is approval `n` of `template.min_reviewers_new` or `template.min_reviewers_edit` and that a public change-log entry will follow, an entry owned by S8.* [A]); `template.reject` (reason code, appealable); `template.retire` (`CT2`, preview of jobs that receive `job.stop_requested` with `closure_reason` `template_retired`). A successful approval releases the reviewer's claim so a second reviewer can claim the item.

**Audit events.** `AdminAction` codes `template.*` and `claim.*`; domain events `template.first_approved`, `template.second_approved`, `template.changes_requested`, `template.rejected`, `template.retired`, `template.paused`, `template.resumed`.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `listTemplateVersions` | `GET /v1/admin/template-versions` | Filters above; `ETag` per row |
| `getTemplateVersion` | `GET /v1/admin/template-versions/{tpv_id}` | Includes diff base and lint results |
| `runTemplateChecks` | `POST /v1/admin/template-versions/{tpv_id}/check-runs` | Deterministic, no side effects; result hash is stored in the approval `detail` |
| `createTemplateVersionComment` | `POST .../{tpv_id}/comments` | `CT0` |
| `requestTemplateChanges` | `POST .../{tpv_id}/change-requests` | `If-Match` |
| `approveTemplateVersion` / `rejectTemplateVersion` | `POST .../{tpv_id}/approvals`, `.../rejections` | `If-Match`; `409 STATE_CONFLICT` if another admin holds the claim |
| `retireTemplateVersion` | `POST .../{tpv_id}/retirements` | `CT2` |

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-tplq-01` | A version authored by admin A in `in_review` | A calls `approveTemplateVersion` | `403 FORBIDDEN` and a refused `AdminAction` |
| `AC-tplq-02` | A new template with `template.min_reviewers_new` = 2 (fixture) | Reviewer B approves, then B approves again | The first call moves it to `awaiting_second_review`; the second returns `409 STATE_CONFLICT`; reviewer C's approval then yields `approved` and a second `AdminAction` |
| `AC-tplq-03` | A version whose lint reports a blocking finding | A reviewer opens Approve | The button is disabled; the API returns `422 UNPROCESSABLE` with `details.fields` naming the finding |
| `AC-tplq-04` | Two reviewers open the same version, one saves a change request first | The second submits with a stale `If-Match` | `412 PRECONDITION_FAILED`; no state change |
| `AC-tplq-05` | A change request with no items | Submitted | `400 VALIDATION_FAILED` |
| `AC-tplq-06` | An approved template with live jobs | A reviewer retires it | The preview lists the jobs; after confirm each receives `job.stop_requested` with `closure_reason` `template_retired` |
| `AC-tplq-07` | A claim older than `ui.admin_claim_ttl_s` | Another reviewer opens the item | The claim shows as expired and can be acquired without takeover |

## 11.46 Tool 2: Service review

**Purpose.** Record what a service's terms permit as dated yes / no / unknown answers against a saved copy of those terms, and approve or revoke the service. Every service starts `unreviewed`, which counts as no; no job can be created for a service until a reviewer has recorded the gate flags with a saved copy (prompt; S0.9.6). All facts are entered by a human and are [V]; nothing is hardcoded. [D]
**Roles and permissions.** `reviewer`: `perm.service.review`, `perm.service.approve`, `perm.service.revoke`. Approval needs `service.min_approvers` distinct reviewers (default 1; 2 is an owner decision, `ISS-119`).

**`SCR-rev-03` Registry list.** Columns: name, `svc_` id, state (a badge "unreviewed counts as no"), last approval date, days to `review_due` (from `service.review_max_age_days`), grace countdown for `review_due` (`service.review_grace_days`), one square per gate flag (yes, no, unknown shown as no), adapter mode (prefill or copy-only), live counts of cells attested to the service and of jobs pinned to it (`M1`). Action: `service.create` (name; state `unreviewed`).

**`SCR-rev-04` Entry screen.** [D]

| Block | Content and rules |
| --- | --- |
| A Header | Name, state timeline, `BLK-claim`, `BLK-trail` |
| B Terms copies | Table of `TermsCopy`: `document_kind` (`terms`, `usage_policy`, `written_permission`) [A], reviewer-entered `captured_on` date, `source_ref` (free text, a URL or a description), size, `sha256:` hash, uploader, `created_at`. Upload: file bytes up to `service.terms_copy_max_bytes`, hash computed on the server, copy immutable and never deleted (a new copy supersedes). `source_ref` is text only; the server never requests it (`AD10`). Text copies render escaped; other types are download-only with `nosniff` from the sandbox origin; two text copies can be compared with `BLK-diff`, otherwise only hashes are compared |
| C Flag matrix | One row per `flag_key` of S0.8.3 (nine gate flags, four `info.*` flags in a separate "advice, never gates" block). Shows the effective answer (newest `FlagAnswer` per flag and region), its date, reviewer short id, terms copy, a short locator (where in the copy; a pointer, not a quotation), and a "stale" marker when a newer copy of the same `document_kind` exists. `regional_availability` expands into one row per region code (ISO 3166-1 alpha-2) the reviewer adds. Helper text under `unknown`: `copy.admin.unknown_is_no` |
| D Adapter capabilities | `adapter.supports_prefill`, `adapter.prefill_url_template`, `adapter.max_url_chars`, `adapter.clean_chat_hint_key`; `adapter.copy_only` is shown read-only and derived (true unless `supports_prefill` and the effective `prefilled_link_use` is `yes`). Validation: the template contains exactly one `{prompt}` and the `https` scheme; `max_url_chars` is a positive integer. A preview substitutes a sample prompt of a chosen length into the template locally and reports its length against `max_url_chars`; no request leaves the browser or the server. Real phone behavior is G2 and is [V]. There is no field for a credential, cookie or session, by design |
| E Readiness | Computed checklist: `third_party_task_use` and `prohibited_content_compatible` are `yes` with a saved copy (hard requirement, S0.8.3); what the other flags unlock (`commercial_use_of_output` for `P2`, `training_use_of_output` for `P3`, `open_publication_of_output` for `P1` licenses under `R7`, `prefilled_link_use` for prefill); warnings for `no` or `unknown` on `human_copy_paste_use`, `access_pooling_or_crediting` and `regional_availability`, each needing a written rationale at approval [A] |
| F History | Every `FlagAnswer` and copy upload, newest first |

**Record answer dialog** (`CT1`): answer `yes`, `no` or `unknown`; terms copy (required for `yes` and `no` on gate flags, optional for `unknown`); locator; note; region for `regional_availability`; `answered_on` date. Saving creates a new `FlagAnswer` row; earlier rows are never edited.

**`SCR-rev-05` Approve, reject, revoke.** Approve (`CT1`): the readiness block frozen as a summary, the rationale for warnings, `n of service.min_approvers`; effects: state `approved`, the review clock starts, a public `ChangeLogEntry` names the service and date, never the reviewer [A]. Revoke (`CT2`): `BLK-affected` shows cells in flight and `M1` jobs, handled per S7.* after `service.revoked`. A service in `review_due` blocks new jobs at once and lets in-flight cells continue until the grace period ends, when the system emits `service.review_lapsed` (actor `system`). Re-review: `service.start_review` is available from `unreviewed`, `rejected`, `review_due` and `revoked` only (S0.9.6); an early re-review of an approved service has no transition, see `ISS-118`.

**Audit events.** `service.*` codes of 11.44.3; domain events `service.created`, `service.review_started`, `service.approved`, `service.rejected`, `service.revoked`, `service.review_due`, `service.review_lapsed`, `service.suspended`, `service.resumed`, `changelog.entry_published`.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `listServices`, `createService`, `getService` | `GET`, `POST /v1/admin/services`, `GET .../{svc_id}` | `ETag` on the entry |
| `startServiceReview` | `POST /v1/admin/services/{svc_id}/reviews` | |
| `uploadTermsCopy` | `POST /v1/admin/services/{svc_id}/terms-copies` | JSON with the bytes as base64; body limit `ceil(4 * service.terms_copy_max_bytes / 3) + 4096` bytes, derived because base64 adds one third [A] (`ISS-117`) |
| `listTermsCopies`, `getTermsCopy`, `getTermsCopyContent` | `GET .../terms-copies`, `GET /v1/admin/terms-copies/{tcp_id}[/content]` | Content is returned as JSON `{content_base64, hash}` |
| `recordFlagAnswer`, `listFlagAnswers` | `POST`, `GET .../{svc_id}/flag-answers` | Append-only |
| `updateServiceAdapter` | `PATCH /v1/admin/services/{svc_id}/adapter` | JSON Merge Patch, `If-Match` |
| `approveService`, `rejectService`, `revokeService` | `POST .../{svc_id}/approvals`, `.../rejections`, `.../revocations` | `revokeService` is `CT2` |

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-svc-01` | A new entry | Created | State `unreviewed`; Approve is disabled; S7.* refuses job creation for it |
| `AC-svc-02` | `third_party_task_use` is `unknown` | Approve is called | `422 UNPROCESSABLE`, `details.fields` names the flag; unknown is treated as no |
| `AC-svc-03` | A gate flag answered `yes` with no terms copy | `recordFlagAnswer` is called | `422 UNPROCESSABLE` with `copy_key` `copy.admin.terms_copy_required` |
| `AC-svc-04` | A file one byte over `service.terms_copy_max_bytes` | Uploaded | `413 PAYLOAD_TOO_LARGE`; a file within the limit is stored and its returned hash equals SHA-256 of the uploaded bytes |
| `AC-svc-05` | A flag with answers `yes` (earlier) and `no` (later) | The matrix loads | The effective answer is `no`, both rows remain in the history, no row was edited |
| `AC-svc-06` | `adapter.supports_prefill` true while `prefilled_link_use` is `unknown` | The adapter is read by the volunteer app | `adapter.copy_only` is true |
| `AC-svc-07` | A template with two `{prompt}` or an `http` scheme | Saved | `400 VALIDATION_FAILED` |
| `AC-svc-08` | Egress from the admin service blocked | A copy with a `source_ref` URL is saved | It succeeds; no outbound request was attempted |
| `AC-svc-09` | `service.min_approvers` = 2 (fixture) | One reviewer approves | The state stays `in_review`, the approval is recorded; a distinct second reviewer's approval moves it to `approved` |

## 11.47 Tool 3: Audit queue

**Purpose.** Give a human the cases automation cannot settle: audits that stay inconclusive after the third execution (S0.9.8 `Audit`), submissions withheld in quarantine (S0.9.3), and disputes about hidden gold cells. The queue never decides what a comparator can decide. [D]
**Roles and permissions.** `reviewer`: `perm.audit.decide`, `perm.audit.release`, `perm.audit.view_restricted`.

**`SCR-rev-06` Queue.** `BLK-list`, oldest first. Columns: item kind, `job_type`, template, age, claim holder, "pending second reviewer" badge. Kinds: `audit_inconclusive` (an `Audit` in `third_pending` or `mismatched` that the comparator cannot resolve), `quarantine` (a `Submission` in `quarantined`), `gold_dispute` (a `Report` against a gold cell, or a gold cell failed by an unusual share of executors), `anomaly` (duplicate-output or timing flags that S9.* routes to a human). Items whose job payload was purged (`retention.job_payload_days`) close as `Audit.cancelled` and leave the queue [A].

**`SCR-rev-07` Item screen.** [D]

| Block | Content and rules |
| --- | --- |
| A Header | Kind, ids, `BLK-claim`, `BLK-trail` |
| B Cell context | The card as volunteers saw it: purpose, license, sensitivity, service requirement, template and version, `cell_kind`, attempt, policy version stamp |
| C Evidence | Inputs and the two or three outputs side by side with comparator result and automatic-check results. All text is escaped and inert: markup is shown as characters, links are plain text and not clickable, nothing is executed (S9.* rules). Opening the block writes one `submission.view` read per item and session |
| D Executors | Shown as "executor 1, 2, 3" with a reliability band; never a `mem_` or `vol_` id (`AD7`) |
| E Quarantine findings | Highlighted spans for links, code to run and requests for action, with the rule that fired |
| F Gold | The gold answer is hidden until the reviewer asks for it (`gold.view_answer`, reason required, logged). Messages sent to a donor never contain a gold answer, so a gold cell is not burned by a dispute |
| G Decision | The outcomes of the table below |

| Kind | Outcome | Action code and tier | Effect |
| --- | --- | --- | --- |
| `audit_inconclusive` | Pass | `audit.accept` `CT3` | `cell.audit_passed`, cell `accepted`, payout or mint per S6.* |
| `audit_inconclusive` | Fail | `audit.reject` `CT1` | `cell.audit_failed`, reason `reject.audit_mismatch` |
| `quarantine` | Release | `quarantine.release` `CT3` | `submission.released_from_quarantine` |
| `quarantine` | Reject | `quarantine.reject` `CT1` | `submission.rejected`, reason `reject.forbidden_content` |
| `gold_dispute` | Gold is defective | `gold.retire` `CT2` | Gold cell leaves the library; reliability observations that used it are recomputed by S8.* |
| `gold_dispute` | Gold is fine | `report.dismiss` `CT1` | Report `dismissed` |
| `anomaly` | Confirm or clear | `audit.reject` or `audit.accept` | As above |

Two-person handling: an `audit.accept` or `quarantine.release` creates an `ApprovalRequest`; the item shows "pending second reviewer" and cannot be decided by anyone else until the request is executed, rejected or withdrawn, after which it returns to the queue. The direction rule (`AD2`) applies because both outcomes create credit or release a withheld result, the point where reviewer capture pays (FD§5.7 failure mode 10). [D]

**Reviewer re-check [H].** A share `verify.reviewer_recheck_rate` of decided items is re-presented, blind to the earlier decision, to a different reviewer; a disagreement raises an `Alarm` of kind `abuse.reviewer_disagreement`. Test: disagreement rate in Phase 1 against a threshold recorded in a `PreRegistration`; kill criterion: no disagreement signal over the pilot means the parameter is set to 0 by `FND`. A reviewer is a separate pseudonymous `AdminUser` and cannot be linked to a member, so reviewing one's own cells is not detectable here; the re-check and the two-person rule reduce it, they do not remove it [V].

**Audit events.** Codes `audit.*`, `quarantine.*`, `gold.*`, `submission.view`; domain events `audit.resolved`, `cell.audit_passed`, `cell.audit_failed`, `submission.rejected`, `submission.released_from_quarantine`.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `listAuditQueueItems`, `getAuditQueueItem` | `GET /v1/admin/audit-queue-items[/{id}]` | Metadata only; ids are the underlying `aud_`, `sub_` or `rpt_` ids |
| `getAuditQueueItemEvidence` | `GET .../{id}/evidence` | Logged read (`submission.view`) |
| `createGoldView` | `POST .../{id}/gold-views` | Reason required; logged read (`gold.view_answer`) |
| `decideAuditQueueItem` | `POST .../{id}/decisions` | Body `{outcome, reason_code, reason_text}`; `202` with an `ApprovalRequest` for `CT3` outcomes |

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-auditq-01` | An open item | The evidence is fetched | One `submission.view` `AdminAction` exists with the reviewer and item ids |
| `AC-auditq-02` | An `audit_inconclusive` item | Reviewer A chooses Pass | `202` with an `ApprovalRequest`; the cell stays `flagged_for_audit`; A cannot approve it; reviewer B's approval executes `cell.audit_passed` |
| `AC-auditq-03` | A submission containing `<script>alert(1)</script>` and a URL | Rendered in block C | Shown as literal characters; the URL is not a link; no script runs |
| `AC-auditq-04` | An item with outcome Fail | A single reviewer confirms | The cell becomes `rejected` with `reject.audit_mismatch` and no second admin is needed |
| `AC-auditq-05` | A gold dispute | The reviewer asks for the gold answer without a reason | `400 VALIDATION_FAILED`; with a reason the view is logged and the donor-facing message omits the answer |
| `AC-auditq-06` | `verify.reviewer_recheck_rate` = 1.0 (fixture) | Reviewer A decides | The item is re-queued blind for reviewer B; if B disagrees an `Alarm` `abuse.reviewer_disagreement` exists |
| `AC-auditq-07` | An item whose payload was purged | The retention job runs | `audit.cancelled` is emitted and the item leaves the queue |

## 11.48 Tool 4: Appeals

**Purpose.** Decide challenges to rejections, suspensions, bans, job and template rejections and report outcomes, with a reviewer who did not make the decision and a second reviewer where the harm is highest (S0.9.7; prompt I). Filing is a member or requester action; this tool only works the queue. [D]
**Roles and permissions.** `reviewer`: `perm.appeal.decide`.

**`SCR-rev-08` Queue.** Oldest first. Columns: `appeal_kind`, filed date, state, assignee, age with an overdue badge after `appeal.reviewer_sla_days` (a published target), "needs second reviewer" badge. Filters: kind, state, mine.

**`SCR-rev-09` Detail.** [D]

| Block | Content |
| --- | --- |
| A Header | `apl_` id, kind, state timeline, days between decision and filing against `appeal.window_days` (informational; late filings were refused at the API) |
| B Original decision | Type, reason code (`reject.*`, `policy.<rule>.<slug>` or a report outcome), decider (`system` or `adm_` short id), time, policy and parameter versions in force |
| C Appellant statement | Escaped text, bounded by `api.max_body_bytes`, no attachments |
| D Evidence by kind | `cell_rejection`: submission, check results, audit comparison, executors anonymised. `member_suspension` and `member_ban`: the reports and flags that led to the sanction and counts, never member-written content. `job_rejection`: the policy evaluation trace with the failing rule and the declarations. `template_rejection`: the version and review comments. `report_outcome`: the report and the action taken |
| E Decision | Uphold or overturn, reason code, consequence preview from the server |

**Guards.** Assignment refuses the admin who made, triaged or reviewed the original decision (`appeal.reassigned` is the conflict-of-interest path, reason code `conflict_of_interest`). One appeal per decision (`appeal.max_per_decision`). For `member_ban` and `template_rejection` the decision needs `appeal.ban_min_reviewers` distinct reviewers: the first moves the appeal to `awaiting_second_review`. If the reviewers disagree, a further distinct reviewer breaks the tie; with no further reviewer available the original decision stands [A] (`ISS-118`).

**Remedies on overturn** [A]. Terminal states are never revived; a remedy creates a successor object.

| Kind | Remedy applied by the server after `appeal.overturned` |
| --- | --- |
| `cell_rejection` | If the cell is still unaccepted the submission is reinstated; if another attempt was already accepted no second credit is created and the reliability record is corrected. Any further compensation is an owner decision (`ISS-119`) |
| `member_suspension` | `member.reinstated` (status `active`) |
| `member_ban` | `member.reinstated` from `banned`, a transition S0.9.4 lacks (`ISS-118`) |
| `job_rejection` | No revival of the `rejected` job; the requester is told to submit again; no credit moved because escrow is held only at admission |
| `template_rejection` | A new `draft` `TemplateVersion` cloned from the rejected one and linked to the appeal enters the normal review (S0.9.5) |
| `report_outcome` | A new `Report` linked to the old one is opened for triage |

The appellant receives a reason code rendered as copy, never reviewer notes.

**Audit events.** Codes `appeal.*`; domain events `appeal.assigned`, `appeal.review_started`, `appeal.reassigned`, `appeal.second_review_requested`, `appeal.upheld`, `appeal.overturned`, plus the remedy events.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `listAppeals`, `getAppeal` | `GET /v1/admin/appeals[/{apl_id}]` | `ETag` |
| `assignAppeal`, `reassignAppeal` | `POST .../{apl_id}/assignments`, `.../reassignments` | Conflict guard |
| `startAppealReview` | `POST .../{apl_id}/reviews` | |
| `requestAppealSecondReview` | `POST .../{apl_id}/second-reviews` | |
| `decideAppeal` | `POST .../{apl_id}/decisions` | `{outcome, reason_code, reason_text}`; `If-Match` |

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-appl-01` | A suspension decided by admin A | A is assigned the appeal | `403 FORBIDDEN`; another reviewer can be assigned |
| `AC-appl-02` | A `member_ban` appeal, `appeal.ban_min_reviewers` = 2 (fixture) | Reviewer B overturns | State `awaiting_second_review`, status still `banned`; C's agreeing decision yields `overturned` and `member.reinstated` |
| `AC-appl-03` | B overturns and C upholds, and no third reviewer exists | C decides | The appeal is `upheld` and the ban stands |
| `AC-appl-04` | A `template_rejection` overturned | Executed | The rejected version is unchanged and a new `draft` version linked to the appeal exists |
| `AC-appl-05` | An appeal older than `appeal.reviewer_sla_days` | The queue loads | The overdue badge shows; nothing is auto-decided |
| `AC-appl-06` | An appellant statement containing markup | Rendered | Escaped literal text |

## 11.49 Tool 5: Abuse flags and reports

**Purpose.** Triage reports from volunteers and requesters and system abuse flags, and take proportionate, logged, appealable action. [D]
**Roles and permissions.** `reviewer`: `perm.report.triage`, `perm.member.sanction`, `perm.member.ban`, `perm.cell.void`, `perm.cell.overturn`, `perm.job.stop`; `operator` holds the same plus `perm.cell.release`.

**`SCR-rev-10` Queue.** Rows come from `Report` (S0.9.8) and from `Alarm` rows whose kind starts with `abuse.` (for example `abuse.grant_farming`, `abuse.invite_tree`, `abuse.referral_farming`, `abuse.timing_anomaly`, `abuse.duplicate_output`, `abuse.injection_attempt`; the list is owned by S9.* and S10.* [A]). Reports on the same subject collapse into one row with a count. Columns: source, category (an opaque enum owned by S10.*), subject kind, count, age with a badge after `report.triage_sla_days`, severity (set at triage), "auto-paused" badge. Oldest first.

**`SCR-rev-11` Item screen.** [D]

| Block | Content and rules |
| --- | --- |
| A Header | Source, category, `BLK-claim`, `BLK-trail` |
| B Subject | Minimal summary of the subject; for a member subject the `SCR-rev-12` view opened with this item as its context (11.55) |
| C Evidence | The reported cell or submission (escaped, inert), report texts. The reporter is shown only as "member, tier" or "requester"; no admin screen or API exposes a reporter's id (`AD7`) |
| D Related | Other open items on the same subject; for templates, the report count in the last `template.autopause_window_s` against `template.autopause_report_count` |
| E Action ladder | Dismiss; triage; `killswitch.engage` on a template or service; `job.stop`; `cell.void`; `cell.overturn` (bundle of cells, one `ApprovalRequest`); `member.restrict`; `member.suspend`; `member.ban`. Nothing is automatic and the ladder is a menu, not a sequence. Closing the item with an action records the `AdminAction` ids in `report.action` (`actioned`); with none, `report.dismiss` |

When reports on a template reach `template.autopause_report_count` inside `template.autopause_window_s` the system engages `kill.template.<tpl_id>` with actor `system`; releasing it is two-person (11.54). A member sanction is appealable (`appeal_kind` `member_suspension` or `member_ban`) and the member sees only a reason code. Takedown of an already delivered or published deliverable is outside this tool and is named as an open item for S10.* and S12.* [V].

**Context rule.** Every action whose subject is a member needs a `context` `{kind, id}` naming an open report, appeal or alarm that links to that member; otherwise `422 UNPROCESSABLE`. This keeps member ids out of free browsing (`AD7`).

**Audit events.** Codes `report.*`, `member.*`, `job.stop`, `cell.*`; domain events `report.triaged`, `report.actioned`, `report.dismissed`, `member.restricted`, `member.suspended`, `member.banned`, `member.reinstated`, `member.restriction_lifted`, `cell.voided`, `cell.overturned`, `job.stop_requested`.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `listAbuseItems`, `getAbuseItem` | `GET /v1/admin/abuse-items[/{id}]` | `id` is an `rpt_` or `alm_` id |
| `triageAbuseItem`, `dismissAbuseItem`, `recordAbuseItemAction` | `POST .../{id}/triages`, `.../dismissals`, `.../actions` | `If-Match` |
| `restrictMember`, `suspendMember`, `banMember`, `reinstateMember`, `liftMemberRestriction` | `POST /v1/admin/members/{mem_id}/restrictions`, `.../suspensions`, `.../bans`, `.../reinstatements`, `.../restriction-lifts` | Body carries `context`; `banMember` returns `202` |
| `stopJob` | `POST /v1/admin/jobs/{job_id}/stop-requests` | `CT2` |
| `voidCell` | `POST /v1/admin/cells/{cel_id}/voidings` | `CT2` |
| `createCellOverturn` | `POST /v1/admin/cell-overturns` | Body `{cell_ids, reason}`; `202` |

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-abuse-01` | `template.autopause_report_count` = 3 (fixture) and three reports on one template inside the window | The third arrives | The queue shows one row with count 3 and a `killswitch.engaged` for `kill.template.<id>` with principal `system` exists |
| `AC-abuse-02` | A `suspendMember` call with no `context` | Sent | `422 UNPROCESSABLE`; a refused `AdminAction` is written |
| `AC-abuse-03` | A ban initiated by reviewer A | A confirms | `202`, member status unchanged; the ban executes only after distinct admin B approves |
| `AC-abuse-04` | Any response of the abuse and appeal APIs | Checked against the schema | No field contains a reporter's `mem_` or `vol_` id |
| `AC-abuse-05` | A `createCellOverturn` for accepted cells | Approved by a second admin | For each cell `cell.overturned`, a ledger `reversal` and a `rework` cell (S0 `ISS-05`) exist, or the whole request is rejected by the guard of 11.50.3 |
| `AC-abuse-06` | An item older than `report.triage_sla_days` | The queue loads | The overdue badge shows |

## 11.50 Tool 6: Ledger explorer and reversal

**Purpose.** Let an operator read the ledger exactly as stored, see invariant and hash-chain status, acknowledge alarms, and request a reversal. The explorer cannot edit, insert or delete anything; the only write path to the ledger from any admin screen is the two-person reversal (S0.8.5). [D]
**Roles and permissions.** `operator`: `perm.ledger.read`, `perm.ledger.reverse`, `perm.alarm.acknowledge`. `reviewer`: read-only views of entries and transactions reached through an open appeal, report or alarm (a `context`, 11.55).

**`SCR-ops-04` Explorer.** [D]

| Block | Content and rules |
| --- | --- |
| A Account list | `ledger_account_type`, `lac_` id, balance as a base-10 integer string in `ucr` with the credit value rounded down beside it (S0.6.1), the constraint of the type (`member` >= 0, `escrow` >= 0 and zero when closed, `reserve` >= 0, `issuance` <= 0 and equal to minus cumulative mint, `retired` >= 0 and equal to cumulative retired). A totals row shows the sum of all balances, which must be exactly 0 |
| B Entries | Filters: entry type, transaction kind, account type, `job_id`, `txn_id`, date range, amount range. No search by `mem_` id and no listing of one member's entries without a `context` (`AD7`); member accounts appear as `lac_` ids |
| C Lots | Credit lots of an account (`lot_` id, amount, `earned_at`, `expires_at`), only with a `context` |

**`SCR-ops-05` Entry and transaction detail.** Debit and credit accounts, type, amount, `seq`, `prev_hash`, `entry_hash` with a recompute button, the owning transaction and its sibling entries, lots consumed or created, the policy and parameter versions stamped, linked job and cell, whether the entry has been reversed. There is no edit control. The "Request reversal" button opens the flow below.

**`SCR-ops-06` Invariants and checkpoints.** One row per `INV-L<nn>` (definitions owned by S6.*): last result, last check time (sampled every `ledger.invariant_check_interval_s`, full recompute every `ledger.full_recompute_interval_s`), linked alarm. Daily checkpoint hashes (`ledger.checkpoint_interval_s`) are listed beside the hash shown on the public ledger page (`ff.public.ledger_page`) so a mismatch is visible. "Run verification now" starts a chain check or a full recompute (`InvariantCheck` row); one runs at a time. Acknowledging an `Alarm` records who and why but never clears a violation: the row stays red until a later check passes (`ledger.invariants_passed`).

### 11.50.3 Reversal flow [D]

1. From an entry or transaction the operator opens the dialog and supplies a `context` (a cell overturn, an appeal or an alarm), a reason code (`fraud_finding`, `appeal_overturn`, `system_error`, `duplicate_posting`, `other`) [A] and text.
2. `previewAdminAction` returns the mirror entries (`entry_type` `reversal`, same amount, accounts swapped), the lot effects, the resulting balances and these guards: (a) the target is not itself a `reversal` and not already reversed (`STATE_CONFLICT`); (b) no account would break its constraint, given `ledger.allow_negative_balance` = false; a member who already spent the credit makes the preview return `would_overdraw` and the request is refused with `422 UNPROCESSABLE` (what then happens to the loss is an owner decision, `ISS-119`; the screen offers `kill.member.<mem_id>` to stop further spending, 11.54).
3. The operator confirms at `CT3`; an `ApprovalRequest` with `required_approvals` = `ledger.reversal_min_approvers` (constant 2) is created.
4. A second `operator` repeats the preview against the current state and approves. Execution posts one `LedgerTransaction` of kind `reversal`, emits `ledger.entry_committed`, runs the per-commit invariant check and writes the `AdminAction` rows in the same transaction.

The original entry is never edited (S0.7 forbids it); both stay visible and linked.

**Audit events.** Codes `ledger.reversal`, `alarm.acknowledge`, `ledger.verify_chain`, and logged reads of member-linked views (`member.lookup`); domain events `ledger.entry_committed`, `ledger.invariants_passed`, `ledger.invariant_violated`, `approval.*`.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `listLedgerAccounts`, `getLedgerAccount` | `GET /v1/admin/ledger-accounts[/{lac_id}]` | Member accounts need `context` |
| `listLedgerEntries`, `getLedgerEntry` | `GET /v1/admin/ledger-entries[/{lge_id}]` | Amounts as integer strings |
| `listLedgerTransactions`, `getLedgerTransaction` | `GET /v1/admin/ledger-transactions[/{txn_id}]` | |
| `listCreditLots` | `GET /v1/admin/ledger-accounts/{lac_id}/credit-lots` | `context` required |
| `listInvariantChecks` | `GET /v1/admin/invariant-checks` | |
| `createLedgerVerification` | `POST /v1/admin/ledger-verifications` | Body `{kind: chain or invariants}`; one at a time |
| `listLedgerCheckpoints` | `GET /v1/admin/ledger-checkpoints` | |
| `createLedgerReversal` | `POST /v1/admin/ledger-reversals` | `202` with an `ApprovalRequest` |
| `listAlarms`, `acknowledgeAlarm` | `GET /v1/admin/alarms`, `POST .../{alm_id}/acknowledgements` | |

No `PUT`, `PATCH` or `DELETE` route exists on any ledger resource.

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-ledgerx-01` | Any ledger resource | `PATCH` or `DELETE` is sent | `404 NOT_FOUND`; no route exists |
| `AC-ledgerx-02` | A mint entry of 1,000,000 `ucr` whose credit is unspent (fixture) | Operator A requests a reversal and operator B approves | One `reversal` transaction posts the mirror entry, `ledger.entry_committed` and `ledger.invariants_passed` follow, and the original entry is unchanged |
| `AC-ledgerx-03` | The same entry after the member spent the credit | A requests a reversal | `422 UNPROCESSABLE` with `would_overdraw`; no `ApprovalRequest` is created |
| `AC-ledgerx-04` | An entry that is already a `reversal` | A requests a reversal | `409 STATE_CONFLICT` |
| `AC-ledgerx-05` | A request for a member's account without `context` | Sent | `422 UNPROCESSABLE`; a refused `AdminAction` is written |
| `AC-ledgerx-06` | An open `ledger.invariant_violated` | An operator acknowledges the alarm | The alarm shows acknowledged and the invariant row stays red until a passing check runs |
| `AC-ledgerx-07` | A seeded edit of one entry (the BM1 corruption test) | `createLedgerVerification` runs | The first broken `seq` is named and `ledger.invariant_violated` is raised |
| `AC-ledgerx-08` | A balance of 9007199254740993 `ucr` | Displayed | Shown exactly, as a string, never through a JavaScript number |

## 11.51 Tool 7: Parameter editor

**Purpose.** Change configuration parameters with versioning, prospective effect, advance notice and a public change log, so credit and rules are never altered secretly (FD Principle 5; FD§4.9). [D]
**Roles and permissions.** `perm.parameter.read` for any admin; `perm.parameter.edit` only for the owner role of the area (S0.10.5). Areas owned by `founders` need two distinct `operator` approvers whatever the direction [A]; `launch.*` areas always need two approvers (S0.10.5); a parameter referenced by a locked `PreRegistration` is read-only (`STATE_CONFLICT`, lock owned by S13.*).

**`SCR-ops-07` List.** Filters: area, owner, public, has pending version, locked, constants. Columns: name, type, current value (a `ratio` shown as a decimal from ppm, `credits` as whole credits, durations with the raw `_s` value beside), version, `effective_from`, a badge for a pending future version, default and difference from default, `calibration_source`.

**`SCR-ops-08` Detail and propose.** [D]

| Block | Content |
| --- | --- |
| A Definition | Every field of S0.10.3: type, unit, validation, default, `tighten_direction`, `notice_days`, owner, `calibration_source`, `public`, `introduced_in`. Constants (`CON`, not mutable) show "changed only by a spec change" and no form |
| B Timeline | Every `ParameterVersion`: value, `effective_from`, change class, public log link, admin short id (never shown publicly) |
| C Form | New value typed by parameter type. A `ratio` is entered as a decimal string and converted to integer ppm without floating point; more than six decimals is `VALIDATION_FAILED`. Reason code and text (`AD3`); a public rationale text for the change log, `fa` and `en`; `evidence_ref` (a `CalibrationRecord`, `MetricSnapshot` or `PreRegistration` id) required when the first `calibration_source` is `CAL`, `P1M` or `DEM`, and for `CAL` the referenced records must number at least `calibration.min_samples_per_service` per service (guard) |
| D Result of `previewAdminAction` | `change_class` from `tighten_direction`: `up` means a higher value tightens, `down` a lower value, `none` always `neutral`. `effective_from`: for `tighten` now; otherwise `now + notice_days * 86,400 s`, where `notice_days` is the parameter's own, defaulting to `change.notice_days_price` for `price.*`, `admission.*` and `credit.*` and to `change.notice_days_default` elsewhere. Approvals needed, and the local time of the effective instant beside UTC |
| E Constraints | Named constraints `C1`..`C8` that include this parameter with the current values of their other members. Evaluation is over the timeline: at every effective instant among all pending versions the full set must satisfy `C1`..`C7`; `C8` is a warning that needs a ticked acknowledgement |
| F Scope notice | "Jobs, lots and leases keep the version they were created under where the spec says so" (S0.10.3), listing the stamped objects the parameter affects |

**Change sets.** Parameters that constraints couple (for example `credit.lifetime_days` and `credit.lifetime_days_accelerated`, constraint `C4`) are edited together: one request lists several `{name, value}` items, is validated as a whole on the timeline, needs one `ApprovalRequest` if any item needs two approvers, and writes one public change-log group. Items keep their own `effective_from`; a tighten item is not delayed by a loosen item. The item count is bounded only by `api.max_body_bytes`. [D]

**Special cases** [D]: the three `launch` switches are read-only here and link to `SCR-ops-12`; `security.*` parameters are not public, so no public entry is written and the screen says so; `security.two_person_actions` accepts only action codes of 11.44.3, adding a code is a tighten and removing one is a loosen; `parameter.changed` is emitted when a version is accepted and carries `effective_from`, consumers apply it at that instant, and no second event is emitted [A].

**`SCR-ops-09` Pending and change log.** Pending versions with a countdown and `Withdraw` (`parameter.withdraw_pending`, `CT2`: a withdrawal is a retraction, so a new `ChangeLogEntry` references the original, which stays); published entries; a tracker of tighten entries due within `change.tighten_publish_within_s` that raises an `Alarm` of kind `ops.changelog_overdue` when late.

**Audit events.** Codes `parameter.*`; domain events `parameter.changed`, `changelog.entry_published`.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `listParameters`, `getParameter` | `GET /v1/admin/parameters[/{name}]` | `ETag`; `name` is the dotted key |
| `listParameterVersions` | `GET /v1/admin/parameters/{name}/versions` | |
| `createParameterChangeSet` | `POST /v1/admin/parameter-change-sets` | `201` when executed (tighten, neutral), `202` when an `ApprovalRequest` is needed; `If-Match` per item |
| `withdrawParameterVersion` | `POST /v1/admin/parameter-versions/{pmv_id}/withdrawals` | `CT2` |
| `listChangeLogEntries` | `GET /v1/admin/change-log-entries` | Includes non-public entries |

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-param-01` | `verify.audit_rate_s` 0.10 with `tighten_direction` `up` | Raised to 0.20 | Class `tighten`, effective now, one approver, a public entry due within `change.tighten_publish_within_s`, event `parameter.changed` |
| `AC-param-02` | `admission.phi` 0.50 with `tighten_direction` `down` | Raised to 0.60 | Class `loosen`, `effective_from` = now + `change.notice_days_price` days, `202` with an `ApprovalRequest`; a quote created before that instant uses 0.50 |
| `AC-param-03` | `verify.audit_rate_s` above `verify.audit_rate_max` | Submitted | `400 VALIDATION_FAILED`, `details.fields` names `C2` |
| `AC-param-04` | `credit.lifetime_days_accelerated` raised above `credit.lifetime_days` | Alone, then as a change set that raises `credit.lifetime_days` first | Alone: `VALIDATION_FAILED` (`C4`); as a set: accepted because every effective instant satisfies `C4` |
| `AC-param-05` | A constant such as `credit.scale_ucr_per_credit` | An edit is attempted | `403 FORBIDDEN` with `copy.admin.constant_not_editable`; no form is shown |
| `AC-param-06` | `launch.members_may_join` | An edit is attempted here | `403 FORBIDDEN`; the screen links to `SCR-ops-12` |
| `AC-param-07` | A stale `ETag` | The edit is submitted | `412 PRECONDITION_FAILED` |
| `AC-param-08` | A ratio typed with seven decimals | Submitted | `400 VALIDATION_FAILED` |
| `AC-param-09` | A `security.*` parameter tightened | Executed | An `AdminAction` exists and no public `ChangeLogEntry` is written |
| `AC-param-10` | A pending loosen version | An operator withdraws it | The version is withdrawn, a retraction entry references the original entry, nothing is deleted |
| `AC-param-11` | A threshold in a locked `PreRegistration` | An edit is attempted | `409 STATE_CONFLICT` |
| `AC-param-12` | A `CAL` replacement with fewer than `calibration.min_samples_per_service` records per service (fixture 29 against 30) | Submitted | `422 UNPROCESSABLE` |

## 11.52 Tool 8: Capacity dashboard

**Purpose.** Show the operator, in one read-only screen, whether supply, demand and the credit economy are inside their declared limits, so decisions on parameters or kill switches rest on measured numbers (Principle 10). It shows aggregates only. [D]
**Roles and permissions.** `operator`: `perm.capacity.read`. A `reviewer` call returns `403 FORBIDDEN`.

### 11.52.1 `SCR-ops-10` tiles [D]

Every tile shows its value, the time it was computed, and the parameter it is compared with. Rollup tiles come from `MetricSnapshot` (`metrics.rollup_interval_s`) and are marked stale when older than that interval; live tiles refresh every `ui.capacity_dashboard_refresh_s`. Breakdowns by category, template or service suppress any cohort smaller than `analytics.min_cohort_k`, showing "fewer than k" instead of a number (`AD8`).

| Tile | Definition (formulas as in S0.6.1; algorithms owned by S6.*) | Compared with |
| --- | --- | --- |
| Active donors | Distinct donors with at least one accepted cell in the last `admission.active_donor_window_days` | |
| Verified throughput | Accepted cells per UTC day, trailing `inflation.throughput_window_days` | |
| Forecast capacity | `floor(active_donors * cells_per_donor_per_day * window_days * phi_ppm * (1 - haircut) / 10^6)` for the quoted window; inputs and the S6.* output are both shown [A] | `admission.phi`, `admission.forecast_haircut`, `admission.forecast_window_days` |
| Committed and headroom | Committed cells (admitted jobs plus reservations in the window) and forecast capacity minus committed | |
| Quote versus actual | For completed jobs, completion time divided by quoted window, and the share finished inside the quote | Phase 1 decision rule (a), FD§9 |
| Queue depth | Queued cells by template, service requirement, purpose and sensitivity; age of the oldest | |
| Supply gauge | Eligible active donors per opt-in category (R8), the gauge that feeds the quote (FD§5.7 failure mode 8) | |
| Waitlist and reservations | Waitlisted jobs and oldest age; reservation share of the `phi` capacity of each day | `admission.waitlist_ttl_days`, `reservation.capacity_share_cap` |
| Lease health | Active leases, expiry rate, decline rate, submission lag, reaper lag | `lease.timeout_s`, `lease.reap_interval_s` |
| Verification | v over `price.v_window_days` (shown only above `price.v_min_sample_cells` cells), effective `g` and `s`, false-accept and false-reject estimates, review-queue ages | `verify.false_accept_alarm`, `verify.false_reject_alarm` |
| Economy | `p_ucr`, `eta_ppm = floor(10^12 / p_ucr)`, claim ratio (unexpired credit divided by verified weekly throughput), mint utilization (minted this UTC month divided by `mint.monthly_cap_credits`), Reserve balance against its ceiling and floor, expiry inflow | `price.eta_alarm_threshold`, `inflation.claim_ratio_threshold_weeks`, `inflation.mint_utilization_alarm`, `reserve.ceiling_credits`, `grant.reserve_floor_credits` |
| Concentration | Share of accepted cells from the top 10 percent of donors (a Phase 1 measure, FD§9) | |
| Alarms and switches | Open `Alarm` rows, engaged kill switches, effective launch state | |

A breach turns the tile red and raises an `Alarm`; each tile links to the parameter in `SCR-ops-08` and to the matching kill switch with the tile as `context`. The dashboard changes nothing itself. Worked fixture (the FD§3.3 inputs, not measurements): 40 active donors, 8 cells per donor per day, a 2-day window, `phi` 500,000 ppm and haircut 0 give capacity `floor(40 * 8 * 2 * 500,000 / 10^6)` = 320 cells; committed 264 cells (S0.6.1) leave a headroom of 56 cells.

### 11.52.3 Bottleneck banner (carried over from the Panel concept) [D][A]

The Panel highlights the not-done item with the most dependents (panel-review §3.5; FD§10) [V]. Here the banner names the open admin item that blocks the most work:

```
candidates = open TemplateVersion (in_review | awaiting_second_review | changes_requested)
           + Service (unreviewed | in_review | review_due) that jobs or the backlog wait for
           + ApprovalRequest (pending) + LaunchGateItem (not signed_off, required by launch.required_gate_ids)
blocked(c) = count of waitlisted or draft jobs, Commons backlog entries and launch switches
             that cannot move only because c is open
bottleneck = argmax over candidates with blocked > 0; ties broken by oldest
show: name, blocked count, age, link to its screen
```

**API.** `getCapacityDashboard` `GET /v1/admin/capacity-dashboard`; `listMetricSnapshots` `GET /v1/admin/metric-snapshots?kind=`; `getBottleneck` `GET /v1/admin/bottleneck`. Audit: reads are not logged individually; alarms are `Alarm` rows.

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-capdash-01` | 40 donors, 8 cells per donor per day, 2-day window, `phi` 500,000 ppm, haircut 0, committed 264 (fixtures) | The tiles load | Capacity 320 and headroom 56 are shown |
| `AC-capdash-02` | A category with fewer than `analytics.min_cohort_k` eligible donors | The supply gauge loads | It shows "fewer than k", not a number |
| `AC-capdash-03` | Mint utilization at or above `inflation.mint_utilization_alarm` | The rollup runs | The tile is red and an `Alarm` exists |
| `AC-capdash-04` | A rollup older than `metrics.rollup_interval_s` | The dashboard loads | The tile carries a stale badge and its computed time |
| `AC-capdash-05` | A reviewer principal | `getCapacityDashboard` is called | `403 FORBIDDEN` |
| `AC-capdash-06` | A template awaiting review that blocks 3 backlog entries and a service that blocks 5 waitlisted jobs | `getBottleneck` is called | The service is named with blocked count 5 |

## 11.53 Tool 9: Launch-gate checklist

**Purpose.** Make BUILDING separate from LAUNCHING: the three `launch.*` switches stay off until the gates G0..G5 that `launch.required_gate_ids` names are signed off by distinct admins with evidence (prompt; FD§8.3). Gate content, the exit rule and the switch rule are owned by S14.*; this part specifies the screens and actions. [D]
**Roles and permissions.** `operator`: `perm.launch.evidence`, `perm.launch.signoff`. Reads for `reviewer`.

**`SCR-ops-11` Checklist.** One card per gate G0..G5 listing its `LaunchGateItem` lines (data owned by S14.*, for example the G0 questions (a)..(k) of FD§8.3). Each line shows state (`open`, `evidence_attached`, `signed_off`, `reopened`), evidence list, sign-offs `n / launch.min_signoffs` and a "required" badge when the gate is in `launch.required_gate_ids` (default G0 and G1). Evidence kinds: a text note; a saved file (bytes with `sha256:` hash, bounded by `api.max_body_bytes` after base64 [A]); a reference to an existing record (`svc_`, `tcp_`, `cal_`, `prr_`). Counsel's answers and the G1 threat-model decision are attached as evidence and are [V]; the tool records them and draws no legal conclusion. The G0 card also shows the number of `approved` services against `launch.min_approved_services` and a link to `SCR-rev-03`; a documented fallback (FD§8.3 fallbacks i to iv) is an evidence kind `fallback_decision` on G0 [A].

**`SCR-ops-12` Sign-off and enable.** [D]

| Block | Content |
| --- | --- |
| A Switches | `launch.members_may_join`, `launch.member_jobs_enabled`, `launch.minting_enabled`: stored value and effective state. Effective = stored value AND no engaged kill switch of the matching scope (`kill.all_new_jobs` for jobs, `kill.all_minting` for minting; there is none for joining) |
| B Rule | One row per requirement, each pass or fail with its source: every gate in `launch.required_gate_ids` signed off with at least `launch.min_signoffs` distinct admins; at least `launch.min_approved_services` approved services or a signed-off fallback; G0 and G1 always required (validation of the parameter); for minting, no open `ledger.invariant_violated` [A]. Any further clause S14.* adds appears as another row |
| C Request | Choose gate items to sign off and, optionally, switches to enable, plus reason; `CT3` |

A `launch.signoff` request is the only way to turn a switch on: the initiator's request is sign-off 1, further distinct admins approve until `launch.min_signoffs` is reached, then, in one transaction, the items become `signed_off` (`gate.signed_off`), the rule is re-evaluated, and if it passes the chosen switches are set (`launch.members_may_join_changed` for joining, `parameter.changed` for the other two). If the rule fails at that moment nothing changes and the request is rejected by `system` (`precondition_failed`). Turning a switch off is `launch.switch_off`: one admin, `CT2`, immediate. Reopening a gate (`launch.reopen`, `CT2`, one admin, reason required) makes the rule fail; switches already on stay on until an admin switches them off, the header shows a red banner and an `Alarm` of kind `launch.rule_failing` is raised; an automatic switch-off is for S14.* to decide (`ISS-118`). With fewer eligible `operator` admins than `launch.min_signoffs` the request is unavailable (`AD9`).

**Audit events.** Codes `launch.*`; domain events `gate.evidence_attached`, `gate.signed_off`, `gate.reopened`, `launch.members_may_join_changed`, `parameter.changed`, `approval.*`.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `listLaunchGates`, `getLaunchGateItem` | `GET /v1/admin/launch-gates`, `GET /v1/admin/launch-gate-items/{lgi_id}` | Gates with items and evidence |
| `createLaunchGateEvidence` | `POST /v1/admin/launch-gate-items/{lgi_id}/evidence` | `CT1`; `If-Match` |
| `createLaunchGateReopening` | `POST .../{lgi_id}/reopenings` | `CT2` |
| `createLaunchSignoff` | `POST /v1/admin/launch-signoffs` | Body `{gate_item_ids, enable_switches, reason}`; `202` |
| `createLaunchSwitchOff` | `POST /v1/admin/launch-switch-offs` | `CT2` |
| `getLaunchStatus` | `GET /v1/admin/launch-status` | Rule rows and effective states; feeds `BLK-header` |

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-gate-01` | A fresh install | `getLaunchStatus` is called | All three switches are false and every rule row that depends on a gate fails |
| `AC-gate-02` | G1 is `open` | A sign-off request enables `launch.members_may_join` and is approved | Execution is rejected (`precondition_failed`); the switch stays false |
| `AC-gate-03` | `launch.min_signoffs` = 2 (fixture), all required gates have evidence | Admin A requests, A tries to approve, B approves | A's approval is refused; B's executes: items `signed_off`, the chosen switch true, `launch.members_may_join_changed` emitted |
| `AC-gate-04` | A pending request, then the only approved service is revoked | B approves | The rule fails at execution, the request is `rejected` by `system`, switches unchanged |
| `AC-gate-05` | `launch.members_may_join` is on and G1 is reopened | The reopening executes | An `Alarm` `launch.rule_failing` exists and the header banner is red; the switch stays on until `launch.switch_off` by one admin takes effect at once |
| `AC-gate-06` | G0 has zero approved services and a signed-off fallback evidence | The rule is evaluated | The service clause passes through the fallback |
| `AC-gate-07` | One active `operator` | The sign-off dialog opens | `fail_closed` is true and the button is disabled |
| `AC-gate-08` | `kill.all_minting` engaged and `launch.minting_enabled` true | The switches block loads | Effective minting shows off |

## 11.54 Tool 10: Kill switches

**Purpose.** Stop a template, a service, a member, all minting or all new jobs at once, with a logged reason, and bring work back only with a second admin (`AD2`). [D]

### 11.54.1 Switches, who may press them [D]

| Switch (S0.10.6) | Engage (one admin, `CT2`) | Release (two admins, `CT3`) | Published |
| --- | --- | --- | --- |
| `kill.all_minting` | `operator` | two admins holding `perm.killswitch.release` for global scope (`operator`) | Public entry within `change.tighten_publish_within_s` |
| `kill.all_new_jobs` | `operator` | as above | as above |
| `kill.template.<tpl_id>` | `operator` or `reviewer`; also the system on `template.autopause_report_count` reports inside `template.autopause_window_s` | two admins holding `reviewer` or `operator` | as above |
| `kill.service.<svc_id>` | `operator` or `reviewer` | as above | as above |
| `kill.member.<mem_id>` | `operator`, with a `context` (11.55) | two `operator` admins | Never; counted only in the aggregate incident measure, so a member is never named or hinted at [A] |

The system may also engage a switch (for example S6.* or S14.* automation on `ledger.invariant_violated`); the board shows actor `system` and the same release rule applies [A]. Reason codes: `ledger_integrity`, `abuse_wave`, `policy_or_legal_concern`, `provider_notice`, `safety_incident`, `operational`, `drill` [A]; only the code appears in a public entry, never the free text.

### 11.54.2 Effects (names only; S14.* owns the full rules) [A]

| Switch | While engaged | On release |
| --- | --- | --- |
| `kill.all_minting` | `mint` postings are refused with `503 KILL_SWITCH_ENGAGED`; effective `launch.minting_enabled` shows off; how Commons cells awaiting acceptance are held is defined by S14.*; transfers of member jobs are unaffected | Minting resumes; nothing is back-posted by the tool |
| `kill.all_new_jobs` | Creating or admitting a job is refused with `KILL_SWITCH_ENGAGED`; jobs in flight and Commons cells in the queue continue | Creation resumes |
| `kill.template.<id>` | `template.paused`; jobs on it get `job.paused`; their queued and leased cells get `cell.paused`, a lease being revoked first (`lease.revoked`); new jobs on it are refused | `template.resumed`, `job.resumed`, `cell.resumed` |
| `kill.service.<id>` | `service.suspended`; jobs pinned to it (`M1`) get `job.paused`; handling of cells attested to it follows S7.* | `service.resumed` only when the cause was this switch (S0.9.6) |
| `kill.member.<id>` | The member's leases are revoked without penalty (`lease.revoked`); new leases, submissions and escrow holds are refused with `KILL_SWITCH_ENGAGED`; status stays `active` (this is not `member.suspended`); balance and ledger are untouched | Normal operation |

**`SCR-ops-13` Board.** The two global switches as large toggles, then a list of engaged and recently released template, service and member switches: state, since, by (`adm_` short id or `system`), reason code, duration, live affected counts, history drawer. Member rows (with `mem_` and context ids) are visible to `operator` only. `BLK-header` always shows the engaged count. All other admins receive an in-tool notice at the moment of every engagement.

**`SCR-ops-14` Engage and release dialogs.** Engage (`CT2`): scope, reason code and text, `BLK-affected` from the preview (leases, cells, jobs, submissions that will pause), type the switch key, step-up passkey if older than `session.admin_stepup_s`, copy `copy.admin.killswitch_engage_warning`. Release (`CT3`): the preview of what resumes, reason, copy `copy.admin.killswitch_release_warning`, then the second admin's own `CT2` dialog; fail closed with fewer than two eligible admins. Engaging an already engaged switch returns `409 STATE_CONFLICT`.

**Audit trail.** Every engage and release writes an `AdminAction` (`killswitch.engage`, `killswitch.release`) with reason code and text, the approving admins, the preview counts and the resulting domain events, and a `KillSwitch` state-history row; `SCR-ops-03` and the switch's history drawer read them.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `listKillSwitches`, `getKillSwitch` | `GET /v1/admin/kill-switches[/{key}]` | `key` is the dotted switch name |
| `createKillSwitchEngagement` | `POST /v1/admin/kill-switch-engagements` | Body `{switch, reason_code, reason_text, context?}`; `CT2` |
| `createKillSwitchRelease` | `POST /v1/admin/kill-switch-releases` | `202` with an `ApprovalRequest` |
| `listKillSwitchHistory` | `GET /v1/admin/kill-switches/{key}/history` | |

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-kill-01` | A reviewer | Engages `kill.template.<id>` | Allowed; the template is `paused`, its jobs `suspended`, their cells `suspended` with leases `revoked`; one `AdminAction` and `killswitch.engaged` exist |
| `AC-kill-02` | A reviewer | Engages `kill.all_minting` | `403 FORBIDDEN` and a refused `AdminAction` |
| `AC-kill-03` | An engage dialog | The typed key does not match, or the reason is shorter than `security.admin_reason_min_chars` | The confirm button stays disabled; the API returns `400 VALIDATION_FAILED` |
| `AC-kill-04` | An engaged switch | The engager requests release and approves their own request | The approval is refused; a distinct second admin's approval releases it |
| `AC-kill-05` | One eligible admin | The release dialog opens | `fail_closed` true; nothing can be released |
| `AC-kill-06` | `kill.all_minting` engaged | A Commons cell reaches acceptance | No `mint` entry is written; the caller sees `503 KILL_SWITCH_ENGAGED` |
| `AC-kill-07` | `kill.all_new_jobs` engaged | A job is created, and a running job settles | Creation returns `KILL_SWITCH_ENGAGED`; the running job completes normally |
| `AC-kill-08` | Reports reach `template.autopause_report_count` (fixture 3) | The third arrives | The switch is engaged by principal `system`; releasing it needs two admins |
| `AC-kill-09` | A template switch and a member switch engaged | The public change log is read | The template entry (reason code only) is present within `change.tighten_publish_within_s`; no entry exists for the member switch |
| `AC-kill-10` | The preview counts before engaging | The switch is engaged | The counts of paused objects equal the preview |

## 11.55 Tool 11: Member lookup (minimal data)

**Purpose.** Show a reviewer or operator the least about one member that a report, appeal or alarm needs, and make every look accountable. The design assumes an insider, a compelled-disclosure request and a seized admin laptop are all possible (prompt I; FD Principle 8). [D]
**Roles and permissions.** `reviewer` and `operator`: `perm.member.lookup`. `operator`: `perm.member.resolve_handle` (two-person).

### 11.55.1 Entry and limits [D]

| Limit | Rule |
| --- | --- |
| No search | No screen or API searches or lists members. `SCR-rev-12` opens only from a "View member" button inside a report, appeal, alarm, abuse item or ledger view, which passes that object as `context` |
| Context linkage | The server checks that the member is linked to the context object (open, or an appeal inside its window); otherwise `422 UNPROCESSABLE` |
| Reason | `CT1`: reason code pre-filled from the context, free text of at least `security.admin_reason_min_chars` |
| Rate | At most `ratelimit.admin_member_lookups_per_day` views per admin per UTC day; beyond it `429 RATE_LIMITED` and an `Alarm` of kind `abuse.admin_lookup_rate` for operators |
| Logging | Each view is an `AdminAction` `member.lookup` with the `mem_` id and the context ids (`AD6`); operators can review who looked at whom in `SCR-ops-03` |
| No persistence | `Cache-Control: no-store`; the view has no print, copy-all or export control (`AD8`) |

### 11.55.2 `SCR-rev-12` What is shown and what never is [D]

| Shown | Never shown by any admin screen or API |
| --- | --- |
| `mem_` id; `status`; `trust_tier` (and the tier before a restriction) | Raw IP, IP hash, e-mail or its hash, device records or hashes, public keys, recovery data, location (S0.7, S0.6.4) |
| Account age in whole days | Exact creation time |
| Accepted and rejected cell counts; a reliability band (low, medium, high from the `trust.*` thresholds) | Cell, prompt or output text beyond the single item in the context |
| Open reports against the member (count), sanction history (type, date, reason code), appeals (kind, outcome) | The reporter's identity; the `vol_` handle; opt-in and team details; balances (use the ledger explorer with a context) |
| Inside a farming context only (`abuse.invite_tree`, `abuse.grant_farming`, `abuse.referral_farming`): invite-tree size, depth and the member's parent and children as `mem_` ids within that subtree; the number of members sharing one device record | The device record itself or any identifier that links members outside the context |

The screen states "only minimal data is shown and every view is logged" (`copy.admin.member_minimal_view`).

### 11.55.3 Handle resolution [D][A]

`member.resolve_handle` turns a `vol_` handle (for example from a provenance manifest in a dispute) into a `mem_` id. It is operator-only, `CT3`, needs a `context` and a reason, and the id is shown once to the initiator after execution. The server keeps no handle-to-member table: it recomputes `HMAC-SHA-256(secret.volunteer_handle_key[version], mem_id)` over members for the handle's key version, so resolution works only while that key version is retained; destroying an old version makes its handles permanently unresolvable (S0.6.4; retention decided in S10.*) [V]. The tool never shows a name, an IP or an e-mail because the platform stores none; what else exists is whatever S10.* records, and the platform cannot promise more than that. A legal request is answered outside the tool, and the tool offers no export of member data.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `createMemberView` | `POST /v1/admin/member-views` | Body `{member_id, context:{kind, id}, reason_code, reason_text}`; a POST because it writes a log row; `Cache-Control: no-store` |
| `createHandleResolution` | `POST /v1/admin/handle-resolutions` | Body `{handle, context, reason}`; `202` with an `ApprovalRequest` |

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-lookup-01` | The admin route table | Any `GET` list or search of members is requested | `404 NOT_FOUND`; no such route exists |
| `AC-lookup-02` | A context object that does not link to the member | `createMemberView` is called | `422 UNPROCESSABLE`; a refused `AdminAction` is written |
| `AC-lookup-03` | A valid lookup | The response is checked against an allow-list schema | It contains none of the denied fields of 11.55.2 |
| `AC-lookup-04` | `ratelimit.admin_member_lookups_per_day` = 3 (fixture) | An admin makes a fourth lookup in one UTC day | `429 RATE_LIMITED` and an `Alarm` for operators |
| `AC-lookup-05` | Any successful lookup | The audit trail is read | One `member.lookup` row names the admin, the `mem_` id and the context ids |
| `AC-lookup-06` | A farming context | The view loads | Tree size, depth and device-sharing count appear; no device identifier appears |
| `AC-lookup-07` | A handle resolution requested by operator A | A approves their own request | `403 FORBIDDEN`; with operator B's approval the `mem_` id is shown once and one `AdminAction` exists |
| `AC-lookup-08` | The key version of the handle has been destroyed | Resolution executes | `422 UNPROCESSABLE` with `handle_unresolvable` |

## 11.56 Tool 12: Release / Hand over

**Purpose.** Carry over the Panel's Release and Hand over for stuck work: a reviewer or operator who is gone must not block a queue item, and a member's stuck lease must not block a cell. [D]

### 11.56.1 What carries over and what does not (panel-review facts, all [V]) [D]

| Panel behavior (panel-review section) | Hamyar equivalent | Decision |
| --- | --- | --- |
| Lock by branch with the tip's commit date as heartbeat, expiry evaluated lazily when someone asks (§3.1 to 3.3) | `WorkClaim` with `expires_at`, renewed by every write; expired by a server timer every `lease.reap_interval_s` | Keep the concept, replace the mechanism: the Panel has no active enforcer |
| Agent Release: empty commit, expired at once, served first (§3.4) | `claim.release`: the item returns to the queue and sorts first ("released first, then oldest") | Keep |
| Owner Release / Hand over: takeover with handoff (§3.4) | `claim.hand_over` (holder to a named admin or to the pool) and `claim.take_over` (operator, forced) | Keep |
| `CI_RUNNING` refusal while a workflow for the cell is active (§3.4) | Refusal while the holder has an unfinished two-person request on the item (`approval_pending`), or, for a cell lease, while the lease is `submitted` | Keep the idea |
| `NEEDS_HUMAN` and `clear_feedback` (§3.4) | No equivalent; the state machines already have `changes_requested` | Not carried |
| Fencing by `base` (branch tip) and fast-forward-only writes (§3.3) | `ETag` and `If-Match`, plus the claim-holder check (`AD12`) | Replace |
| Advisory reservation in KV with a self-declared `who`, ten-minute TTL, eventually consistent (§2.2, §3.4, §4.5 item 1) | Not carried: a claim is authoritative, keyed by `AdminUser`, in the primary database | Replace |
| One shared panel password plus an admin key typed per action and optionally kept in the browser (§4.1, §4.2, §4.5 items 1, 5) | Passkeys and step-up (`AD1`, `CT2`) | Replace |
| Bottleneck highlight (§3.5) | Bottleneck banner (11.52.3) | Keep, re-scoped |

### 11.56.2 `WorkClaim` [A]

Entity `WorkClaim`, table `work_claims`, prefix `clm_`, retention `moderation`. Fields: `subject_type` (`template_version`, `service`, `report`, `alarm`, `appeal`, `audit_item`), `subject_id`, `admin_user_id`, `acquired_at`, `expires_at` (= last renewal + `ui.admin_claim_ttl_s`), `ended_at`, `end_kind` (`released`, `handed_over`, `expired`, `taken_over`, `completed`), `handed_to_admin_id`. A partial unique index on `(subject_type, subject_id) WHERE ended_at IS NULL` gives exactly one active claim per item, so two simultaneous claims cannot both succeed. Events `workclaim.acquired`, `workclaim.released`, `workclaim.handed_over`, `workclaim.taken_over`, `workclaim.expired`. A write to a claimed item by anyone but the holder is `409 STATE_CONFLICT` with `details.reason` `claim_held`; the second reviewer of a two-reviewer flow claims after the first has finished (11.45). For appeals, handing over is the state machine's `appeal.reassigned` with the conflict guard of 11.48.

**Rules.** Hand over needs a target holding the item's permission, else `403`; it is a single step, the target sees it in "My work" and may release. Take over (`perm.claim.take_over`, `CT2`) names a reason, is refused while `approval_pending` (the other admin must first reject or withdraw that request), and tells the former holder with `copy.admin.claim_taken_over`.

**`SCR-ops-15` Work board.** "My work" and, for operators, "All claims": item, type, holder, time left, state, with Release, Hand over and Take over; queue order is released first, then oldest.

### 11.56.3 Lease release for member-held cells [D][A]

`SCR-ops-16` Lease inspector (operator): lists active leases by `cel_` id, job or template with template, attested service, age and time left, and no member id. `cell.release` (`CT2`, `perm.cell.release`) is allowed only for a lease in state `active`: it emits `lease.revoked`, and the cell returns to `queued` through the existing `leased --cell.declined--> queued` transition, recorded with actor `admin` and reason `operator_release`, so there is no penalty to the member (FD§5.5; no new event, `ISS-118`). An optional `requeue_at_front` puts the cell at the head of its template queue for its next lease [A]. A revoked lease gets no `lease.submit_grace_s`: a late paste-back is rejected with `reject.lease_expired`. A lease in `submitted` returns `409 STATE_CONFLICT`. Release is per cell; a larger stop is a kill switch (11.54), not a bulk release.

| `op` | Method and path | Notes |
| --- | --- | --- |
| `listWorkClaims` | `GET /v1/admin/work-claims` | Filters `mine`, `subject_type`, `active` |
| `createWorkClaim` | `POST /v1/admin/work-claims` | Body `{subject_type, subject_id}` |
| `createWorkClaimRelease`, `createWorkClaimHandover`, `createWorkClaimTakeover` | `POST /v1/admin/work-claims/{clm_id}/releases`, `.../handovers`, `.../takeovers` | Takeover is `CT2` |
| `listLeases` | `GET /v1/admin/leases` | Operator; response has no member id |
| `createLeaseRelease` | `POST /v1/admin/leases/{lse_id}/releases` | Body `{reason_code, reason_text, requeue_at_front}`; `CT2` |

| AC | Given | When | Then |
| --- | --- | --- | --- |
| `AC-claim-01` | Two reviewers claim one item at the same instant | Both calls run | Exactly one returns `201`; the other `409 STATE_CONFLICT` |
| `AC-claim-02` | A claim with no write for `ui.admin_claim_ttl_s` | The timer runs | `workclaim.expired` is emitted and the item sorts first in its queue |
| `AC-claim-03` | An item claimed by A | Reviewer B writes to it | `409 STATE_CONFLICT`, `details.reason` `claim_held` |
| `AC-claim-04` | A hand over to an admin without the permission | Sent | `403 FORBIDDEN` |
| `AC-claim-05` | The holder has a pending approval on the item | An operator takes over | `409 STATE_CONFLICT`, `approval_pending`; after the request is rejected the takeover succeeds and the former holder sees `copy.admin.claim_taken_over` |
| `AC-claim-06` | An `active` lease | An operator releases it | `lease.revoked`, cell `queued`, reliability of the member unchanged, event actor `admin` |
| `AC-claim-07` | A lease in `submitted` | An operator releases it | `409 STATE_CONFLICT` |
| `AC-claim-08` | A release with `requeue_at_front` | The next lease in that template queue is issued | It is that cell |
| `AC-claim-09` | `listLeases` | The response is checked against its schema | It contains no `mem_` or `vol_` id |

## 11.57 Admin copy keys (Persian and English)

Admin screens use the `copy.admin.*` keys below; each has `fa` and `en` text and is marked `needs_human_and_legal_review` (S0.5). Persian is written right to left with the zero-width non-joiner where the language needs it. Copy says "declared" and never "guaranteed" (FD Principle 11). [D]

| Key | `fa` | `en` | Marker |
| --- | --- | --- | --- |
| `copy.admin.danger_confirm_title` | تأیید اقدام حساس | Confirm a sensitive action | `needs_human_and_legal_review` |
| `copy.admin.reason_prompt` | دلیل را بنویسید؛ این متن در گزارش ممیزی ثبت می‌شود. | State the reason. It is saved in the audit log. | `needs_human_and_legal_review` |
| `copy.admin.type_to_confirm` | برای ادامه، شناسهٔ هدف را تایپ کنید. | Type the target id to continue. | `needs_human_and_legal_review` |
| `copy.admin.two_person_waiting` | این اقدام برای اجرا به تأیید مدیر دیگری نیاز دارد. | This action needs a second admin before it runs. | `needs_human_and_legal_review` |
| `copy.admin.two_person_own_request` | تأیید درخواست خودتان ممکن نیست. | You cannot approve your own request. | `needs_human_and_legal_review` |
| `copy.admin.fail_closed_one_admin` | برای این اقدام دست‌کم دو مدیر فعال با دسترسی لازم وجود ندارد. | This action needs at least two active admins with the required permission. | `needs_human_and_legal_review` |
| `copy.admin.unknown_is_no` | پاسخ «نامشخص» مانند «خیر» محسوب می‌شود. | “Unknown” counts as “no”. | `needs_human_and_legal_review` |
| `copy.admin.terms_copy_required` | بدون نسخهٔ ذخیره‌شدهٔ شرایط، ثبت یا تأیید این پاسخ ممکن نیست. | This answer cannot be recorded or approved without a saved copy of the terms. | `needs_human_and_legal_review` |
| `copy.admin.declared_notice` | بررسی‌ها بر پایهٔ اظهارها و بازبینی‌های ثبت‌شده است و تضمین نیست. | Reviews rest on recorded declarations and checks; they are not guarantees. | `needs_human_and_legal_review` |
| `copy.admin.tighten_now` | این تغییر فوراً اعمال می‌شود و ثبت عمومی آن ظرف مهلت اعلام‌شده منتشر خواهد شد. | This change takes effect immediately; its public log entry follows within the declared period. | `needs_human_and_legal_review` |
| `copy.admin.loosen_notice` | این تغییر قاعده را آسان‌تر می‌کند؛ پیش از اجرا در گزارش تغییرات عمومی اعلام می‌شود و فقط از زمان اعلام‌شده اجرا می‌شود. | This change loosens a rule. It is announced in the public change log and takes effect only at the declared time. | `needs_human_and_legal_review` |
| `copy.admin.constant_not_editable` | این مقدار ثابت است و فقط با تغییر مشخصات قابل تغییر است. | This value is a constant and changes only through a specification change. | `needs_human_and_legal_review` |
| `copy.admin.killswitch_engage_warning` | با فعال‌کردن این کلید قطع اضطراری، کار در جریان متوقف می‌شود. | Engaging this kill switch pauses work in flight. | `needs_human_and_legal_review` |
| `copy.admin.killswitch_release_warning` | آزادسازی کلید قطع اضطراری به تأیید مدیر دومی نیاز دارد. | Releasing a kill switch needs a second admin. | `needs_human_and_legal_review` |
| `copy.admin.member_minimal_view` | فقط کمترین داده نمایش داده می‌شود و هر مشاهده ثبت می‌شود. | Only the minimum data is shown and every view is logged. | `needs_human_and_legal_review` |
| `copy.admin.claim_taken_over` | این مورد از شما به مدیر دیگری منتقل شد. | This item was taken over by another admin. | `needs_human_and_legal_review` |
| `copy.admin.launch_blocked` | تا امضای همهٔ دروازه‌های لازم، پذیرش عضو و کارهای اعضا فعال نمی‌شود. | Member admission and member jobs stay off until the required gates are signed off. | `needs_human_and_legal_review` |

## 11.58 Parameters added by this part (convention gaps)

S0.10.6 says names are stable and S16.* completes the table. This part needs the parameters below; each default is an `initial configurable default` and each area and owner already exists in S0.10.5. [D][A]

| Name | Type | Initial configurable default | Validation | Owner | Replaced by |
| --- | --- | --- | --- | --- | --- |
| `session.admin_stepup_s` | duration_s | 300 | 30..3600; at most `session.admin_idle_ttl_s` | `operator` | `SEC` |
| `security.admin_two_person_pending_ttl_s` | duration_s | 86,400 | 600..604800 | `operator` | `SEC` |
| `security.admin_reason_min_chars` | int | 20 | 1..500 | `operator` | `SEC` |
| `ratelimit.admin_member_lookups_per_day` | int | 30 | 1..1000 | `operator` | `SEC`, `OPS` |
| `ui.admin_claim_ttl_s` | duration_s | 1800, the initial value of `session.admin_idle_ttl_s`, so a claim does not outlive an idle session | 60..86400 | `operator` | `OPS` |
| `ui.capacity_dashboard_refresh_s` | duration_s | 60, the initial value of `public.counter_refresh_s` | 5..3600 | `operator` | `OPS` |
| `verify.reviewer_recheck_rate` | ratio | 0.10 | 0..1 [H] | `operator` | `P1M` disagreement rate between first and re-check reviewers |

The `security.two_person_actions` default grows from four names to nine: `ledger.reversal`, `launch.signoff`, `parameter.loosen`, `killswitch.release` (S0.10.6) plus `member.ban`, `audit.accept`, `quarantine.release`, `cell.overturn`, `member.resolve_handle`; the list therefore adds five new names (`ISS-117`).

## 11.59 Dependencies on other parts and open [V] items

| Item | Owner part | What this part needs | Tag |
| --- | --- | --- | --- |
| Permission matrix and admin authentication (WebAuthn, onboarding of a second admin, session revocation) | S10.* | Every `perm.*` name of 11.44.3 mapped to `reviewer` or `operator`; the two-admin onboarding rule | [A] |
| Kill-switch effects and the launch rule | S14.* | Full effects of 11.54.2; the exact switch rule of 11.53; whether a reopened gate switches members off | [A] |
| Reversal of credit already spent; compensation for a wrongly rejected cell | S6.* | An owner-approved rule; until then the tool refuses (`would_overdraw`) | [V] |
| Review checklist, lint rules, in-flight handling after retire or revoke | S8.*, S9.*, S7.* | Data and rules this part displays | [A] |
| Report categories, takedown of delivered deliverables, retention of handle-key versions | S10.*, S12.* | Opaque category enum; a withdrawal action for deliverables; key-version retention | [V] |
| Metric snapshots and capacity forecast algorithm | S13.*, S6.* | The data behind the tiles of 11.52.1 | [A] |
| All `op` names and schemas of 11.44..11.56 | S15.* | Fold into the API specification with the same ids | [D] |
| Passkey support on reviewers' devices and reachability of the admin origin for reviewers in Iran | S10.*, S19.* | Test on real devices and networks | [V] |

## Issues raised

This file is the third file of part 11, so it uses the issue sub-block `ISS-117`..`ISS-119` (S0.4) [A]. Each resolution is already applied inside the file; C-001 consolidates and may record a different one.

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-117` | minor | prompt | Convention gaps used by the admin tools: (a) entities `ApprovalRequest` (`apr_`) and `WorkClaim` (`clm_`); (b) `TermsCopy.document_kind` (`terms`, `usage_policy`, `written_permission`), needed to store the usage policy and written permission of FD§8.3 G0(i) and (k); (c) no retirement marker or event for a `GoldCell`; (d) events `approval.*` and `workclaim.*`; (e) the seven parameters of 11.58; (f) `security.two_person_actions` default lacks `member.ban`, `audit.accept`, `quarantine.release`, `cell.overturn`, `member.resolve_handle`; (g) the action codes of 11.44.3 and the reason-code lists; (h) sub-headings `11.41` upward to avoid collisions with other S11 files; (i) the terms-copy upload body (derived from `service.terms_copy_max_bytes`) exceeds `api.max_body_bytes`, so it gets its own limit; (j) `Alarm` kinds `abuse.*`, `launch.rule_failing`, `ops.changelog_overdue`; (k) a transient `requeue_at_front` flag on a released `Cell` | Used as proposed in this file; C-001 and C-022 fold them into S0 and S16 | proposed |
| `ISS-118` | major | FD§5.3, FD§3.4, FD§8.3 | State machines of S0.9 lack transitions the tools need: (a) a `banned` member has no exit, so an overturned ban appeal cannot be applied; (b) nothing moves a rejected cell to accepted after an overturned `cell_rejection` appeal; (c) `awaiting_second_review` has no rule for split votes; (d) an approved service cannot be re-reviewed early (`review_started` only leaves `unreviewed`, `rejected`, `review_due`, `revoked`); (e) an operator lease release has no event; (f) the launch rule can fail after a gate is reopened while the switches stay on | (a) add `banned --member.reinstated--> active` on an overturned appeal only; (b) add `rejected --cell.reinstated--> accepted` when no other attempt was accepted, otherwise correct the reliability record and create no second credit (11.48.3); (c) a further distinct reviewer breaks a tie, else the original decision stands (11.48); (d) add `approved|suspended --service.review_started--> in_review`; (e) reuse `cell.declined` with actor `admin` and reason `operator_release` (11.56.3); (f) raise `launch.rule_failing` and require an explicit `launch.switch_off`, automatic switch-off left to S14.* (11.53) | proposed |
| `ISS-119` | major | FD§5.7, FD§4.2, prompt | Decisions only the owner can make: (a) with fewer than two admins every two-person action is unavailable (`AD9`), and `ledger.reversal_min_approvers` is a constant 2; (b) `service.min_approvers` 1 or 2; (c) credit already spent cannot be reversed under `ledger.allow_negative_balance` = false, and a wrongly rejected cell whose work was paid to another attempt has no compensation rule; (d) whether a service approval needs a notice period like a loosening (applied: a public entry at approval time, no notice); (e) who counts as "founders" for parameters owned by `founders` (applied: two distinct `operator` approvers) | Applied as stated in each section; listed for S3.* | needs_owner |
