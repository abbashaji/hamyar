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

The `CT3` codes `member.ban`, `audit.accept`, `quarantine.release`, `cell.overturn`, `member.resolve_handle` and `launch.signoff` are proposed additions to the default of `security.two_person_actions` (S0.10.6 lists four names) and are reported in `ISS-118`. [A]

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
