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
