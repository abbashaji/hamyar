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
