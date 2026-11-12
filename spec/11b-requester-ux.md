# 11. Requester experience screens (part 11b)

*Spec part 11, file 11b (requester). Binding vocabulary: `spec/00-conventions.md` (S0.*). The Founding Document draft v0.1 is cited as FD§N. Nothing here is legal advice and nothing is verified against any provider's terms or any law. Every Persian string in this file needs human and legal review before use (marker `needs_human_and_legal_review`, S0.5).*

**Placement.** S11 is split over several files (sub-block rule, S0.4). This file owns the requester screens `SCR-req-01`..`SCR-req-18`, the copy keys `copy.req.*`, the acceptance criteria `AC-req-nn` and the issues `ISS-114`..`ISS-116`. Volunteer, reviewer and operator screens live in sibling files and are not repeated here. Heading numbers start at `11.31` so they cannot collide with sibling files [A] (`ISS-114`).

## 11.31 Scope, coverage and reading guide

Coverage of the requester items of prompt scope F (every item is a decision, table, schema, pseudocode or Given/When/Then below):

| Prompt scope F requester item | Section | Screens |
| --- | --- | --- |
| Job creation wizard: template choice | 11.35, 11.36 | `SCR-req-02` |
| Data upload and screening, with the screening result display | 11.36 | `SCR-req-03`, `SCR-req-04` |
| Metadata declarations with plain-language P/L/S/M explanations | 11.36, 11.44 | `SCR-req-05` |
| Policy result with reason codes | 11.36, 11.43 | `SCR-req-06` |
| Price and window quote showing the p = 1 + v + lambda breakdown | 11.37 | `SCR-req-07` |
| Escrow confirmation and the 'downstream use uncontrolled' notice for open licenses | 11.36, 11.45 | `SCR-req-08` |
| Job progress with a per-cell status map (panel status-graph and bottleneck ideas, [V]) | 11.39, 11.48 | `SCR-req-12`, `SCR-req-13` |
| Cancellation and refund display | 11.40 | `SCR-req-14`, `SCR-req-15` |
| Waitlist and reservation screens | 11.38 | `SCR-req-09`..`SCR-req-11` |
| Results download with provenance manifest, including the manifest JSON schema | 11.41, 11.42 | `SCR-req-16` |
| Rating of the outcome | 11.41 | `SCR-req-17` |
| Requester-visible rejection reasons in EN and FA | 11.43 | `SCR-req-06`, `SCR-req-18` |
| Copy for policy, privacy and risk notices in FA and EN | 11.45 | all |
| Persian first: RTL, numerals, Jalali and Gregorian, mixed direction, accessibility, low bandwidth | 11.33, 11.46 | all |
| Home of the requester area (entry to all of the above) | 11.36 | `SCR-req-01` |

**Owned elsewhere (this file only states which fields it needs from them).**

| Topic | Owner | What 11b consumes |
| --- | --- | --- |
| Price formula, escrow postings, refund and settlement rules, admission algorithm, reservations rules | S6.* | `quote`, `escrow`, `window`, `receipt`, `reservation.terms` fields (11.34) |
| Policy evaluator, allowlist, license options, reason-code semantics | S7.* | `getPolicyProfile`, `rejection.reasons` |
| Template format, data slots, splitter, output formats | S8.* | `template.input_slots`, `cell_count`, `deliverable.files` |
| Input screening rules, quarantine, output flagging | S9.* | `upload.screen_status`, `findings`, `withheld_for_review` |
| Identity, session, recovery, rate limits | S10.* | auth failures, `identity.recovery_cooldown_s` |
| API paths and schemas | S15.* | operation ids in 11.34 are the contract; paths there are proposals [A] |

## 11.32 Requester decisions

Each row is a decision [D] that every requester screen obeys.

| ID | Decision | Reason |
| --- | --- | --- |
| `RD-01` | The client displays server values and never computes a price, a window, a refund, a policy outcome or a deadline. The only client arithmetic is display conversion of integers (11.33.3), done with arbitrary-precision integers, never floating point. [D] | Ledger amounts are exact integers (S0.6.1); two implementations of the price would drift. |
| `RD-02` | User-facing promises say "declared", never "guaranteed"; a quoted window is never presented as instant completion. [D] | FD Principle 11 and Principle 10. |
| `RD-03` | The wizard may use the active allowlist (`getPolicyProfile`) to grey out and explain combinations, but the server decision is final and a hint is never a promise. [D] | Policy is data and can change at any time (`R9`, `R10`). |
| `RD-04` | The wizard is a server-side draft (`Job.draft`). The browser keeps only in-memory state and the current step name; no uploaded text, glossary or result is written to browser storage. [D] | Shared devices and member safety (FD Principle 8); S0.7 retention classes. |
| `RD-05` | Declaring `S2` or `S3` honestly is not punished: the job is not accepted, the reason is shown, nothing is charged. Only false declarations found later fall under abuse handling (S10.*). [D] | An honest answer must be the easy path (FD§5.7 failure mode 1). |
| `RD-06` | The price breakdown (`v`, `lambda`, `p`, `eta`) is always shown and always says whether `v` is measured or the prior. [D] | Verification cost is shown, not hidden (FD§4.3). |
| `RD-07` | Escrow confirmation is the only requester action that spends credit; it is an explicit button bound to the hash of the quote the person saw; initial focus is on the summary, not on the button. [D] | Prevents accidental spend and price drift. |
| `RD-08` | A requester never sees a volunteer identity, a `vol_` handle, a gold cell, or any timing finer than the granularity in 11.42. [D] | FD§5.6, S0.6.4, member safety. |
| `RD-09` | For licenses `L1` and `L2` the notice "downstream use uncontrolled" is shown on the declarations step, requires acknowledgement on escrow confirmation, and is repeated on the results screen and in the manifest. [D] | FD§5.7 failure mode 3: "the card and the job form must say so". |
| `RD-10` | No result is shown before assembly or partial settlement. [D] | A cell can be overturned (`cell.overturned`); showing then retracting output would mislead. |
| `RD-11` | A `rejected`, `quote_expired` or `cancelled` job is terminal. "Fix and resubmit" creates a new job that copies declarations and uploads (`createJob` with `copy_from_job_id`). [D] | Keeps the Job machine of S0.9.2 unchanged. |
| `RD-12` | No requester screen mentions, suggests or enables bypassing a regional or technical restriction or a service's terms. [D] | FD Principle 9, prompt ground rule 3. |
| `RD-13` | Every state a requester must act on is reachable by polling the app; notification channels are optional extras (in-app, plus e-mail only if the member gave one, `identity.email_optional`). No push service is required. [D][A] | No mandatory third-party dependency; low bandwidth; S10.* decides channels. |
| `RD-14` | Everything that originates from volunteers or uploads (outputs, file names, glossary terms, reported model names) is untrusted text: rendered with text-only APIs, never as HTML or Markdown, never auto-linked, never executed; mixed-direction text is isolated (11.46). [D] | FD§10 item 4, prompt scope E. |
| `RD-15` | Numbers in copy are placeholders (`{n}`) bound to parameter values or server fields, never literals. [D] | S0.2 writing rule 2. |

## 11.33 Shared contracts

### 11.33.1 Per-screen format [D]

Every screen below uses these rows: **Purpose**, **Entry conditions**, **Blocks** (top to bottom), **States**, **Actions** (with the API operation id from 11.34), **Copy intent** (copy keys, 11.43-11.45), **Accessibility**, and **Given/When/Then** (`AC-req-nn`). The states `loading`, `error_retry`, `offline`, `auth_required`, `gate_closed`, `kill_switch`, `rate_limited` and `member_blocked` are global (11.33.2) and are not repeated; a screen lists only its own states.

### 11.33.2 Global states [D]

| State | Trigger | Behaviour |
| --- | --- | --- |
| `loading` | request in flight | Text placeholder with the screen title already visible; announced politely to assistive technology; no spinner-only content |
| `error_retry` | network failure, `INTERNAL`, `UNAVAILABLE` | Entered data is kept in memory; a Retry button re-sends with the same `Idempotency-Key` (11.33.4); `Retry-After` honored |
| `offline` | no connectivity | Banner; read-only view of the last loaded data of this visit; no write is attempted |
| `auth_required` | `AUTH_REQUIRED`, `AUTH_INVALID`, `AUTH_EXPIRED` | Hand off to member session restore (S10.*); return to the same screen and step afterwards |
| `gate_closed` | `403 LAUNCH_GATE_CLOSED` (`launch.member_jobs_enabled` is false) | Whole requester area shows `copy.req.err_gate_closed`; no form is rendered; nothing is charged |
| `kill_switch` | `503 KILL_SWITCH_ENGAGED` (`kill.all_new_jobs`, `kill.template.<tpl_id>`, `kill.service.<svc_id>`) | Creation actions disabled with `copy.req.err_kill_switch`; existing jobs stay readable |
| `rate_limited` | `429 RATE_LIMITED` | Disabled action with a countdown from `Retry-After`; never auto-repeats faster than allowed |
| `member_blocked` | `403 FORBIDDEN`, `member_status` `suspended` or `banned`, or `identity.recovery_cooldown_s` not elapsed | Read-only; shows the reason class and, for a cooldown, the end time in local time |

### 11.33.3 Display rules [D]

| Item | Rule |
| --- | --- |
| Amounts | Wire format is an integer string of `ucr`. Display `whole = ucr div 1,000,000` and `frac = ucr mod 1,000,000`. Summary lines show `ui.credit_display_decimals` decimals; balances round down, prices and escrow round up (S0.6.1); detail views show the exact value with up to 6 decimals, trailing zeros trimmed |
| Ratios | Wire format is integer `*_ppm`. Display three decimals (`ui.ratio_display_decimals`), half-up; the detail view shows the exact ppm. Example: `eta_ppm` 869,565 shows 0.870 |
| Dates and times | RFC 3339 UTC on the wire; shown in the device time zone or the zone chosen in settings (S0.6.2); every deadline shows the local time next to any UTC day boundary; detail views show Jalali and Gregorian together (`i18n.dual_calendar_detail`) |
| Digits | `fa` locale uses Persian numerals by default `i18n.digits_default_fa`, switchable to Latin; stored copy contains Latin placeholders only |
| Identifiers | `job_` ids are shown shortened (last 8 characters) with a copy button; the full id is in the detail view; never parsed for meaning (S0.6.3) |
| Hashes | Shown as the first 12 hex characters with a copy button for the full value |

### 11.33.4 Idempotency and retry rule [D]

```
for every write action (S0.11.5 requires a key on job, escrow, report, appeal writes):
  action_key = new_ulid()                      # matches ^[A-Za-z0-9_-]{16,64}$
  loop:
    resp = send(method, path, body, header Idempotency-Key = action_key)
    if network_error or status >= 500: retry with the SAME key and the SAME body (jittered exponential backoff,
                                       honors Retry-After and RateLimit-Remaining; schedule is client-side, not specified)
    if 409 IDEMPOTENCY_IN_PROGRESS:    wait Retry-After, retry with the SAME key
    if 422 IDEMPOTENCY_KEY_MISMATCH:   client bug; stop; show copy.req.err_internal; never retry
    else:                              stop (2xx and deterministic 4xx are stored and replayed by the server)
  if the person changes any field after a failed attempt: action_key = new_ulid()
```

The key lives in memory for the duration of one user action. A double tap on Confirm therefore sends the same key twice and the server replays the stored response (`Idempotent-Replayed: true`), so credit cannot be spent twice (S0.11.5, natural idempotency of `escrow_hold`).

## 11.34 API operations used by the requester screens

Operation ids (lowerCamelCase, S0.5) are the contract between the screens and S15.*; the paths are proposals in the shapes of S0.11 [A]. Every write carries an `Idempotency-Key` (S0.11.5). Every response is `Cache-Control: no-store`. Amount fields are integer strings, ratio fields are `*_ppm` integers. Operations marked `+` are convention additions (11.49).

| Operation id | Method and path (proposal) | Used by |
| --- | --- | --- |
| `listJobs` | `GET /v1/jobs?state=&cursor=&limit=` | 01 |
| `getBalance` | `GET /v1/members/me/balance` (`balance_ucr`, `cap_ucr`, `member_status`, `cooldown_ends_at`) | 01, 07, 08 |
| `listCreditLots` | `GET /v1/members/me/credit-lots` (`lot_id`, `amount_ucr`, `expires_at`) | 07, 08, 15 |
| `listTemplates` | `GET /v1/templates?job_type=` (approved versions only) | 02 |
| `getTemplate` | `GET /v1/templates/{template_id}` | 02, 03 |
| `getPolicyProfile` | `GET /v1/policy-versions/current` (allowlist, phase locks, `license_options`) | 05 |
| `listServices` | `GET /v1/services?state=approved` (`service_id`, display names) | 05 |
| `createJob` | `POST /v1/jobs` body `{template_id, copy_from_job_id?}` -> `Job` in `draft` | 02, 06, 18 |
| `getJob` | `GET /v1/jobs/{job_id}` | all |
| `patchJob` | `PATCH /v1/jobs/{job_id}` (JSON Merge Patch, `If-Match` = `row_version`) | 05 |
| `createUpload` | `POST /v1/jobs/{job_id}/uploads` JSON body `{file_name, encoding, content}`; `encoding` is `utf8` or `base64`; size limit `job.max_upload_bytes` | 03 |
| `getUpload` | `GET /v1/uploads/{upload_id}` | 03, 04 |
| `deleteUpload` | `DELETE /v1/uploads/{upload_id}` | 03 |
| `requestUploadReview`+ | `POST /v1/uploads/{upload_id}/review-requests` body `{note?}` | 04 |
| `createGlossary` | `POST /v1/jobs/{job_id}/glossaries` body `{entries:[{source,target}]}` | 03 |
| `previewCells`+ | `GET /v1/jobs/{job_id}/cell-preview` (up to three sample cells exactly as a volunteer sees them) | 03, 05 |
| `submitJob` | `POST /v1/jobs/{job_id}/submission` -> `202`, Job `screening` (or already `quoted` / `rejected` when screening finished synchronously) | 05 |
| `getQuote` | `GET /v1/jobs/{job_id}/quote` | 07, 08 |
| `createWaitlistEntry` | `POST /v1/jobs/{job_id}/waitlist-entries` | 07 |
| `getWaitlistEntry` | `GET /v1/waitlist-entries/{waitlist_entry_id}` | 09 |
| `deleteWaitlistEntry` | `DELETE /v1/waitlist-entries/{waitlist_entry_id}` | 09 |
| `confirmEscrow` | `POST /v1/jobs/{job_id}/escrow-confirmation` body `{quote_hash, acknowledgements:[string]}` | 08 |
| `getReservationAvailability`+ | `GET /v1/reservations/availability?from=&to=&cells=&job_type=` | 10 |
| `createReservation` | `POST /v1/reservations` | 10 |
| `listReservations` / `getReservation` | `GET /v1/reservations`, `GET /v1/reservations/{reservation_id}` | 01, 11 |
| `cancelReservation` | `POST /v1/reservations/{reservation_id}/cancellation` | 11 |
| `activateReservation` | `POST /v1/reservations/{reservation_id}/activation` body `{job_id}` | 11 |
| `getJobProgress`+ | `GET /v1/jobs/{job_id}/progress` (ETag, conditional `If-None-Match`) | 12 |
| `listJobCells` / `getJobCell` | `GET /v1/jobs/{job_id}/cells`, `GET /v1/jobs/{job_id}/cells/{cell_id}` (primary cells only) | 13 |
| `getCancellationPreview`+ | `GET /v1/jobs/{job_id}/cancellation-preview` | 14 |
| `cancelJob` | `POST /v1/jobs/{job_id}/cancellation` | 14 |
| `getSettlementReceipt`+ | `GET /v1/jobs/{job_id}/receipt` | 15 |
| `getDeliverable` | `GET /v1/jobs/{job_id}/deliverable` | 16 |
| `downloadDeliverableFile` | `GET /v1/deliverables/{deliverable_id}/files/{file_name}` (bytes via `fetch` with the Bearer header; no query-string secrets, S0.11.1) | 16 |
| `getManifest` | `GET /v1/jobs/{job_id}/manifest?profile=requester` | 16 |
| `createJobRating`+ / `getJobRating`+ | `POST` and `GET /v1/jobs/{job_id}/rating` | 17 |
| `createAppeal` / `getAppeal` | `POST /v1/appeals` with `appeal_kind` = `job_rejection`; `GET /v1/appeals/{appeal_id}` | 18 |
| `createReport` | `POST /v1/reports` | 13, 16 |

### 11.34.1 Response shapes the screens depend on [A]

Only fields the screens read are listed; unknown fields are ignored (S0.11.1). `*_ucr` are strings.

```json
// Job view (getJob)
{ "id": "job_01j9...", "state": "quoted", "row_version": 7,
  "template": { "template_id": "tpl_...", "template_version_id": "tpv_...", "job_type": "translation_glossary",
                "display_name": { "fa": "...", "en": "..." } },
  "declarations": { "purpose": "P1", "license": "L2", "license_spdx_id": null, "sensitivity": "S0",
                    "service_requirement": "M0", "pinned_service_ids": [] },
  "cell_count": 240, "upload_ids": ["upl_..."], "glossary_id": "gls_...",
  "policy": { "policy_version_id": "plv_...", "stamped_at": "2026-11-12T09:30:00Z" },
  "rejection": null,   // or { "reasons": ["policy.R2.sensitivity_not_accepted"], "decided_at": "...", "appeal": { "allowed_until": "...", "appeal_id": null } }
  "quote_expires_at": "2026-11-12T10:00:00Z", "pause_reason": null, "closure_reason": null,
  "created_at": "...", "updated_at": "..." }

// Upload view (getUpload)
{ "id": "upl_...", "file_name": "chapter1.txt", "bytes": 18233, "content_hash": "sha256:...",
  "screen_status": "flagged_for_review",          // pending | passed | flagged_for_review | rejected
  "cell_count": 240, "chars_available_per_cell": 3100, "cells_over_envelope": [],
  "findings": [ { "kind": "url_present", "severity": "review", "locations": [ { "row": 12, "start": 40, "end": 71 } ] } ] }

// Quote (getQuote)  -- shown on SCR-req-07 and SCR-req-08
{ "job_id": "job_...", "quote_hash": "sha256:...", "quote_expires_at": "...",
  "cells_primary": 240,
  "price": { "v_ppm": 100000, "v_source": "prior", "v_window_days": 28, "v_sample_cells": 0,
             "lambda_ppm": 50000, "p_ucr": "1150000", "eta_ppm": 869565 },
  "escrow": { "total_ucr": "276000000", "primary_pay_ucr": "240000000", "verification_pool_ucr": "24000000",
              "levy_ucr": "12000000", "verification_cells": 24 },
  "balance": { "before_ucr": "300000000", "after_ucr": "24000000",
               "lots_consumed": [ { "lot_id": "lot_...", "amount_ucr": "100000000", "expires_at": "..." } ] },
  "window": { "status": "available", "window_s": 172800, "deadline_at": "...", "latest_stop_at": "...", "supply_level": "normal" },
  "alternatives": ["waitlist", "reservation"],            // offered only when window.status is unavailable
  "versions": { "policy_version_id": "plv_..." } }

// Progress (getJobProgress)
{ "job_id": "job_...", "version": 42, "state": "running", "cells_primary": 240,
  "counts": { "waiting": 150, "retrying": 3, "in_progress": 20, "checking": 5, "double_checking": 2, "done": 58, "paused": 0, "stopped": 0, "failed": 0, "redo": 2 },
  "map": "dddd...",                 // exactly cells_primary characters, one status code per cell (11.39.2)
  "attempts": { "17": 3 },        // only cells whose attempt is above 1; key = cell index
  "withheld_for_review": 0,
  "verification": { "pool_cells": 24, "used_cells": 9 },
  "timing": { "admitted_at": "...", "deadline_at": "...", "latest_stop_at": "...", "on_track": "unknown" },
  "bottleneck": { "kind": "awaiting_volunteer", "cells": 150, "since": "..." },
  "pause_reason": null, "closure_reason": null }

// Settlement receipt and cancellation preview (same shape; kind = preview | receipt)
{ "job_id": "job_...", "kind": "receipt", "held_ucr": "276000000",
  "paid_to_volunteers_ucr": "264000000", "levy_ucr": "12000000",
  "refund": { "total_ucr": "0", "unstarted_primary_ucr": "0", "unspent_verification_ucr": "0", "unearned_levy_ucr": "0" },
  "cells": { "primary_accepted": 240, "verification_accepted": 24, "in_flight": 0 },
  "transactions": [ { "txn_id": "txn_...", "txn_kind": "settle" } ],
  "restored_lots": [ { "lot_id": "lot_...", "amount_ucr": "0", "expires_at": "...", "already_expired": false } ] }

// Deliverable (getDeliverable)
{ "id": "dlv_...", "job_id": "job_...", "manifest_id": "mfs_...", "completeness": "complete",
  "available_until": "...", "files": [ { "name": "output-001.txt", "media_type": "text/plain", "bytes": 91234, "hash": "sha256:..." } ] }
```

**Which codes the requester screens must handle** (messages in 11.43): `400 VALIDATION_FAILED` (with `details.fields`), `401` family, `403 FORBIDDEN | LAUNCH_GATE_CLOSED`, `404 NOT_FOUND`, `409 STATE_CONFLICT | ALREADY_EXISTS | IDEMPOTENCY_IN_PROGRESS`, `412 PRECONDITION_FAILED`, `413 PAYLOAD_TOO_LARGE`, `422 POLICY_REJECTED | INSUFFICIENT_CREDIT | CAP_EXCEEDED | NO_CAPACITY | UNPROCESSABLE | IDEMPOTENCY_KEY_MISMATCH`, `429 RATE_LIMITED`, `500/503 INTERNAL | UNAVAILABLE | KILL_SWITCH_ENGAGED`. Where one code has several causes the cause is `details.reason` (values in 11.43.2) [A].

## 11.35 Wizard architecture

### 11.35.1 Steps, Job states and events [D]

The wizard has seven steps. The Job is created when the first step is completed and stays in `draft` until the person presses Check my request. Two different screenings exist and must not be confused: **upload screening** (automatic checks on one `Upload`, during `draft`, S9.*) and **job screening** (`Job.screening`: policy rules `R1`..`R7` over the declarations plus the upload result, plus a reviewer for sampled or flagged inputs, `screen.review_rate_*`). [D]

| Step | Screen | Job state while on it | Server events (S0.9) |
| --- | --- | --- | --- |
| 1 Template | `SCR-req-02` | `draft` (created on choosing) | `job.created` |
| 2 Data | `SCR-req-03` | `draft` | `upload.accepted`+ or `upload.screen_failed`+ (11.49) |
| 3 Data check result | `SCR-req-04` | `draft` | `upload.screen_passed`+, `upload.screen_flagged`+, `upload.screen_rejected`+ |
| 4 Declarations and Check my request | `SCR-req-05` | `draft`, then `screening` | `job.submitted` |
| 5 Policy result | `SCR-req-06` | `screening`, then `rejected` or `quoted` | `job.policy_rejected` or `job.policy_passed` |
| 6 Price and window | `SCR-req-07` | `quoted` (or `waitlisted`) | `job.quote_expired`, `job.waitlisted`, `job.waitlist_released` |
| 7 Escrow confirmation | `SCR-req-08` | `quoted`, then `admitted` | `job.escrow_confirmed` |

An abandoned draft is cancelled by the system after `job.draft_ttl_days` with the existing event `job.cancel_requested` (actor type `system`); its uploads are purged under the `job_bound` class (S0.7). [A][D]

### 11.35.2 Resume and navigation [D]

```
function resume_screen(job):            # derived from server state only, so reload, a second tab and a lost session resume correctly
  switch job.state:
    draft:           if no upload with screen_status in (passed, flagged_for_review): return SCR-req-03 or SCR-req-04
                     else: return SCR-req-05
    screening:       return SCR-req-06 (waiting view)
    rejected:        return SCR-req-06 (rejected view)
    quoted:          return SCR-req-07
    quote_expired:   return SCR-req-07 (expired view)
    waitlisted:      return SCR-req-09
    admitted | running | suspended | assembling | settling | cancelling: return SCR-req-12
    completed | failed:  return SCR-req-16 (and SCR-req-15 for the receipt)
    cancelled:       return SCR-req-15
```

- Back is available only inside `draft`. Changing the template after an upload exists asks for confirmation and deletes the uploads and glossary, because the slots differ (`deleteUpload`). [D]
- Declarations are read-only after `job.submitted`. To change them the person uses Fix and resubmit (a new job, RD-11). [D]
- Two tabs: a write with a stale `row_version` returns `412 PRECONDITION_FAILED`; the screen reloads the job and shows `copy.req.err_stale`. [D]

### 11.35.3 Job-fit check shown during the wizard (FD§2) [D]

| FD§2 condition | Evaluated by | Shown where | Failure behaviour |
| --- | --- | --- | --- |
| (1) Splits into independent cells | server splitter (S8.*): `cell_count`, `cells_over_envelope` | `SCR-req-03` | Cells over `cell.envelope.max_input_chars` are listed by index; the person edits or splits the file; `Continue` disabled while any remain |
| (2) Data is `S0` or `S1` | the declaration and upload screening | `SCR-req-04`, `SCR-req-05` | `R2` reject, honestly declared (RD-05) |
| (3) Each cell has an automatic or sampled check | template (S8.*) | `SCR-req-02` card line "How results are checked" | Not shown for templates without a check (such templates cannot be approved) |
| (4) The requester accepts a queue window of hours to days | requester acknowledgement | `SCR-req-07` text, not a checkbox | The quote states the window; cancelling is free before escrow |
| (5) Each cell fits one Send | server: `chars_available_per_cell` against the envelope | `SCR-req-03` | As (1) |

The fit check is advice with reasons, never a score. [D]

## 11.36 Entry and wizard screens

### SCR-req-01 Requests home

| Row | Content |
| --- | --- |
| Purpose | One place to see credit, drafts, active and finished requests, and to start a new request or reservation |
| Entry conditions | Authenticated member (`auth_scheme` `member`); `launch.member_jobs_enabled` true, otherwise global state `gate_closed` |
| Blocks | (1) Balance card: `balance_ucr` (rounded down), the soonest expiry among `listCreditLots` with its local date, and the cap `cap_ucr`. (2) Primary button New request. (3) Collapsible "What can I request?" holding the five job-fit conditions of 11.35.3. (4) Needs attention: quotes ready or about to expire, a waitlist place released, a rejection whose appeal window is open, results not yet downloaded or rated. (5) In progress, then Finished (cursor-paged, 11.33). (6) Drafts with their expiry date (`job.draft_ttl_days`). (7) Reservations (only when `ff.job.reservations` is on) |
| States | `first_visit` (no jobs: shows the explainer instead of lists), `no_credit` (balance below one cell price: New request stays enabled to browse, but the page says how credit is earned and links to the volunteer area), `at_job_cap` (`admission.max_concurrent_jobs_per_member` reached: New request disabled with the reason) |
| Actions | `listJobs`, `getBalance`, `listCreditLots`, `listReservations`; New request opens `SCR-req-02` |
| Copy intent | Calm and factual; never urges to spend; says credit expires and shows when; wording "request" and "contribute", never "deposit" or "withdraw" (FD§0.1 item 13). Keys: `copy.req.home_title`, `copy.req.home_first_visit`, `copy.req.home_no_credit`, `copy.req.home_job_cap` |
| Accessibility | One `h1`; lists are real lists; every job row is one link whose accessible name is title + state label + date; the Needs attention region is `aria-live="polite"`, never assertive; state is never colour alone |

- **AC-req-01** Given a member with a draft, a `running` job and a `completed` unrated job, When the page loads, Then the draft appears under Drafts with its expiry, the running job under In progress, and the completed job under Needs attention with a Rate action.
- **AC-req-02** Given `admission.max_concurrent_jobs_per_member` = 2 and two non-terminal jobs, When the page loads, Then New request is disabled and the reason names the limit by its configured value, not a literal.
- **AC-req-03** Given `launch.member_jobs_enabled` is false, When any requester route is opened, Then `copy.req.err_gate_closed` is shown, no form is rendered and no write request is sent.

### SCR-req-02 Template choice (wizard step 1)

| Row | Content |
| --- | --- |
| Purpose | Choose a reviewed template. There is no free-form prompt box: prompts come only from reviewed templates (`R4`) |
| Entry conditions | New request pressed; no `kill.all_new_jobs`; the list comes from `listTemplates` and only contains approved versions |
| Blocks | One-line reason for templates (`copy.req.why_templates`). One card per template: name, job type, one-sentence description, "What you provide" (from `input_slots`), "How results are checked" (FD§2 condition 3), envelope facts (`cell.envelope.max_input_chars`, `cell.envelope.expected_time_s`), "Reviewed on {date}" and the effectiveness note [H] `copy.req.template_effect_note`. A job-type filter when more than one type is listed |
| States | `no_templates` (`copy.req.templates_empty`; nothing else is offered, no text box), `template_paused` (card disabled, `kill.template.<tpl_id>`) |
| Actions | Choose -> `createJob` (new `Idempotency-Key`); Back to home |
| Copy intent | Explain what the template does in the requester's terms; say plainly that no template is shown to work for every text and that results are verified, not guaranteed |
| Accessibility | Cards are a single-select list with visible focus; each card's name is the accessible name; the description is `aria-describedby` |

- **AC-req-04** Given two approved templates, When the person chooses one, Then exactly one `createJob` is sent with that `template_id` and one `Idempotency-Key`, the Job is `draft` and step 2 opens.
- **AC-req-05** Given `listTemplates` returns an empty `data` list, When the screen renders, Then `copy.req.templates_empty` is shown and no input accepting free text is rendered.
- **AC-req-06** Given `kill.template.<tpl_id>` is engaged, When the list renders, Then that card is disabled and states the pause, and the other cards stay usable.

### SCR-req-03 Data upload (wizard step 2)

| Row | Content |
| --- | --- |
| Purpose | Supply the data and the template's other inputs, and show how the server will split it |
| Entry conditions | Job in `draft` with a template |
| Blocks | (1) One input block per `template.input_slots[]`; supported slot kinds [A, S8.* owns]: `file_rows` (file or pasted text, UTF-8), `glossary` (term pairs; becomes a `Glossary`), `option` (one of a list), `text_short`, `file_archive`. (2) Limits in words: `job.max_upload_bytes`, `admission.max_job_cells`, `cell.envelope.max_input_chars`. (3) Split summary after processing: `cell_count`, `chars_available_per_cell` (envelope minus template overhead minus glossary share), the list `cells_over_envelope` by index. (4) "Preview what a volunteer will see" (collapsed): up to three sample cards from `previewCells` showing the fixed card (purpose, license, sensitivity, service, template, expected time) and the full wrapped prompt as inert text. (5) Notices `copy.req.notice_stranger_reads` and `copy.req.notice_retention`. (6) Continue |
| States | `choosing`, `uploading` (text progress), `processing` (`screen_status` `pending`), `too_large`, `too_many_cells` (more cells than `admission.max_job_cells`), `over_envelope`, `ready` |
| Actions | `createUpload` (JSON body, `utf8` or `base64`), `deleteUpload` (Replace), `createGlossary`, `previewCells`. A file larger than `job.max_upload_bytes` is stopped on the device before sending; the server's `413 PAYLOAD_TOO_LARGE` is still handled |
| Copy intent | Be specific about limits and why; say that a stranger reads each piece inside their own AI account; say how long text is kept and that hashes and the manifest remain (S0.7 `job_bound`) |
| Accessibility | File input and paste area both labelled; drag-and-drop is never the only route; progress is text plus `role="progressbar"`; pasted and previewed text uses `dir="auto"` with bidi isolation (11.46); the over-envelope list is a table with row index and size |

- **AC-req-07** Given a file of `job.max_upload_bytes` + 1 bytes, When it is chosen, Then no request is sent, `copy.req.err_too_large` is shown with the limit, and the previous upload (if any) is untouched.
- **AC-req-08** Given the splitter returns `cell_count` above `admission.max_job_cells`, When processing ends, Then Continue is disabled and the message states the maximum and the current count; the person can shorten the file or split the request.
- **AC-req-09** Given the connection drops during `createUpload`, When the person presses Retry, Then the same `Idempotency-Key` and body are sent and exactly one `Upload` exists afterwards.
- **AC-req-10** Given three cells exceed the envelope, When processing ends, Then the three indices and their sizes are listed and Continue stays disabled until `cells_over_envelope` is empty.

### SCR-req-04 Data check result: the screening result display (wizard step 3)

| Row | Content |
| --- | --- |
| Purpose | Show the outcome of upload screening in plain language, with where each finding is, without echoing the sensitive text; let the person fix, re-upload, or ask a reviewer to look |
| Entry conditions | An `Upload` exists; the screen polls `getUpload` while `screen_status` is `pending` (`ui.requester.progress_poll_s`) |
| Blocks | Status banner (one of four, below); a findings list (kind, severity, location as row and character range, what to do); counts per kind; the line `copy.req.notice_screening_limits` (screening reduces risk, it does not remove it); actions |
| States | `pending`: busy text, no promise of speed. `passed`: Continue enabled. `flagged_for_review`: Continue enabled; the page says a reviewer will look before the request is accepted. `rejected`: Continue disabled; findings of severity `reject` are listed first |
| Actions | Replace file (`deleteUpload` then `createUpload`); Edit and upload again; Ask a reviewer to look (`requestUploadReview`, limited to `screen.requester_review_requests_per_day`; moves `rejected` to `flagged_for_review` only if a reviewer so decides); Continue |
| Copy intent | Say what was found and where, never the detected text itself (the sensitive text would be reprinted on the screen and in screenshots); say what the person can change; never reveal detection thresholds or which exact check fired for prohibited content (it would teach evasion) |
| Accessibility | Banner has `role="status"`; findings are a table with row/column headers; locations are readable text ("row 12, characters 40 to 71"), not only highlighted spans; no colour-only severity |

Finding kinds the screen can display (detection is owned by S9.*; the set is a display contract [A]; an unknown kind uses `other`):

| `kind` | Default action | Copy key | EN | FA |
| --- | --- | --- | --- | --- |
| `pii_pattern` | `screen.pii_action` (default `reject`) | `copy.req.finding_pii` | Text that looks like personal data of a person (for example an identity number, a phone number or an e-mail address) was found at the places listed. Hamyar cannot accept personal data. Remove or replace it and upload again. | در جاهای فهرست‌شده متنی یافت شد که شبیه اطلاعات شخصی افراد است (مثلاً شمارهٔ شناسایی، شمارهٔ تلفن یا نشانی ایمیل). همیار اطلاعات شخصی را نمی‌پذیرد. آن را حذف یا جایگزین کنید و دوباره بارگذاری کنید. |
| `url_present` | `screen.url_action` (default `flag_for_review`), counted against `screen.max_urls_per_input` | `copy.req.finding_url` | A link was found. Links are not allowed in requests, because volunteers only copy, press Send and return text. A reviewer may look at this input. | پیوند (لینک) یافت شد. پیوند در درخواست‌ها مجاز نیست؛ چون داوطلب فقط متن را کپی می‌کند، ارسال را می‌زند و پاسخ را برمی‌گرداند. ممکن است یک بازبین این ورودی را ببیند. |
| `instruction_pattern` | `flag_for_review` | `copy.req.finding_instruction` | Text that reads like an instruction to a person or to a chat assistant was found. If it is part of your material, a reviewer will check it. | متنی یافت شد که شبیه دستور به یک فرد یا دستیار گفت‌وگو است. اگر بخشی از متن شماست، یک بازبین آن را بررسی می‌کند. |
| `hidden_characters` | `info` (normalised by the splitter) | `copy.req.finding_hidden` | Invisible direction or formatting characters were found and will be normalised so the text displays the same for everyone. | نویسه‌های نامرئی جهت‌نما یا قالب‌بندی یافت شد و برای نمایش یکسان متن، یکدست‌سازی می‌شود. |
| `over_envelope` | block | `copy.req.finding_over_envelope` | Some pieces are longer than one volunteer message can hold. Split or shorten them. | بعضی بخش‌ها از ظرفیت یک پیام داوطلب بلندترند. آن‌ها را تقسیم یا کوتاه کنید. |
| `encoding_invalid` | `reject` | `copy.req.finding_encoding` | The file is not valid UTF-8 text. | فایل متن معتبر UTF-8 نیست. |
| `row_schema_invalid` | `reject` | `copy.req.finding_rows` | Some rows do not match what this template expects. | بعضی ردیف‌ها با آنچه این قالب انتظار دارد نمی‌خوانند. |
| `other` | as returned | `copy.req.finding_other` | Something in this input needs attention. | چیزی در این ورودی نیاز به توجه دارد. |

- **AC-req-11** Given `screen.pii_action` = `reject` and an upload with a `pii_pattern` finding at row 12, When the result displays, Then Continue is disabled, the finding shows "row 12" and a character range, and no snippet of the detected text appears anywhere in the page or its accessible tree.
- **AC-req-12** Given `screen_status` = `flagged_for_review` because of `url_present`, When Continue is pressed, Then the wizard proceeds to declarations and the page states that a reviewer will look before acceptance.
- **AC-req-13** Given `screen_status` = `pending`, When the tab is hidden, Then polling stops, and it refreshes once when the tab becomes visible again.
- **AC-req-14** Given `requestUploadReview` was already used `screen.requester_review_requests_per_day` times today, When the person presses Ask a reviewer, Then the action is disabled with the reset time in local time.

### SCR-req-05 Declarations (wizard step 4)

| Row | Content |
| --- | --- |
| Purpose | Collect the four mandatory declarations (purpose, license, sensitivity, service requirement; FD§5.2) in plain language, then submit the job for checking |
| Entry conditions | Job `draft`; at least one upload with `screen_status` `passed` or `flagged_for_review` |
| Blocks | Four option groups in this order: Purpose `P0`..`P3`, License `L0`..`L3`, Sensitivity `S0`..`S3`, Service `M0`..`M2`. Each option shows its code, a short name and the plain-language explanation of 11.44 (what it means, what it allows, what it does not). Options the active allowlist locks are shown disabled with the reason `copy.req.locked_phase` or `copy.req.locked_unreviewed` (for `P2`, `P3`, `L3`, `M2` in Phases 1-2; the data comes from `getPolicyProfile`, RD-03). Under License `L1`/`L2`: an optional `license_spdx_id` chosen from `license_options` [V counsel], and the downstream notice (11.45). Under Sensitivity `S1`: a required tick "I accept that a stranger will read this". Under Service `M1`: a list from `listServices`. A live volunteer-card preview (`previewCells`) updates with the choices. A read-only summary and the notices `copy.req.notice_declared`, `copy.req.notice_screening_limits`. Button Check my request |
| States | `incomplete` (groups missing; the button is disabled and names them, which is the client form of `R1`), `combination_hint` (the allowlist says the combination is not accepted now: an inline explanation with the reason code; the button stays enabled because the server decides, RD-03), `s2_s3_chosen` (the definition is shown and the page says it will not be accepted now; the choice is allowed so that an honest answer is recorded and explained, RD-05) |
| Actions | `getPolicyProfile`, `listServices`, `patchJob` (merge patch with `If-Match`), `previewCells`, `submitJob` (Check my request) |
| Copy intent | Explain each code by its consequence for the requester, not by legal categories; always say "declared"; never imply that a declaration is verified or that output use can be controlled downstream |
| Accessibility | Each group is a `fieldset` with a `legend`; options are radio buttons whose accessible description is the explanation; disabled options remain focusable and announce their reason; no information is carried only by the code letter |

- **AC-req-15** Given no purpose is chosen, When the page renders, Then Check my request is disabled and the missing group names are listed.
- **AC-req-16** Given the active allowlist locks `P2` and `P3`, When the page renders, Then both options are disabled, focusable and announce their reason.
- **AC-req-17** Given the person chooses `L2`, When the choice is made, Then the downstream-use notice appears on this step before submission.
- **AC-req-18** Given the person chooses `S1`, When the acknowledgement tick is empty, Then Check my request stays disabled.
- **AC-req-19** Given a valid set of declarations, When Check my request is pressed, Then one `patchJob` and one `submitJob` are sent with their own `Idempotency-Key`, the Job becomes `screening` and `SCR-req-06` opens.

### SCR-req-06 Policy result (wizard step 5)

| Row | Content |
| --- | --- |
| Purpose | Show whether the request was accepted by the policy engine and, if not, exactly why, in the requester's language, with what can be changed |
| Entry conditions | Job `screening`, `rejected` or just `quoted`; polled with `getJob` while `screening` |
| Blocks | `waiting`: text that the check may include a reviewer for sampled or flagged inputs (`screen.review_rate_new_requester`, `screen.review_rate_established_requester`), no time promise. `passed`: the policy version stamped (short `plv_` id and date), a list of `R1`..`R7` each marked checked, plus plain notes for `R8` (volunteers see a request only if their opt-ins cover it), `R9` (the version is stamped now and re-checked when each result is accepted) and `R10` (rules can tighten at once; they loosen only with a public entry); button Continue to quote. `rejected`: the ordered `reasons` (11.43.1), each with its change advice; nothing was charged; buttons Fix and resubmit (`createJob` with `copy_from_job_id`) and Ask for a human review (`SCR-req-18`, shown while `rejection.appeal.allowed_until` is in the future) |
| States | `waiting`, `passed`, `rejected` |
| Actions | `getJob`, `createJob`, `createAppeal` (via `SCR-req-18`) |
| Copy intent | A rejection is information, not blame; every reason has its own sentence and its own next step; no legal conclusions; no reveal of which exact detector fired for `R3` |
| Accessibility | The result region is `aria-live="polite"` and receives focus once when the state changes to `passed` or `rejected`; reasons are an ordered list with the code as a visually secondary, copyable string |

- **AC-req-20** Given the job is `rejected` with `policy.R2.sensitivity_not_accepted`, When the page renders, Then the `R2` sentence in the active locale is shown, the code is shown as secondary text, no charge is mentioned as made, and Fix and resubmit is offered.
- **AC-req-21** Given `rejection.appeal.allowed_until` is in the past, When the page renders, Then Ask for a human review is absent and the page states that the window (`appeal.window_days`) has ended.
- **AC-req-22** Given the job is `screening` for longer than the page was open, When the state becomes `quoted`, Then polling stops, focus moves to the result heading and Continue to quote is enabled.

### SCR-req-07 Price and window quote (wizard step 6)

| Row | Content |
| --- | --- |
| Purpose | Show what the request costs, how the price is made, and when it will be done, before any credit is held |
| Entry conditions | Job `quoted` (a live quote), `waitlisted` re-quoted by `job.waitlist_released`, or `quote_expired` |
| Blocks | (1) The p line: `p = 1 + v + lambda` written with this quote's numbers, e.g. "1 + 0.10 + 0.05 = 1.15 credits per cell"; each term has a one-line meaning (11.37). (2) Whether `v` is `measured` over the trailing `price.v_window_days` days from `v_sample_cells` cells, or the `prior` (`price.v_prior`) because fewer than `price.v_min_sample_cells` cells exist. (3) Escrow breakdown: volunteer pay, verification pool (and the number of verification cells it buys), reserve levy, total. (4) Round-trip efficiency `eta`. (5) Balance before and after, and which credit lots are used (oldest first) with their expiry. (6) The window: quoted duration, `deadline_at` (local time, both calendars in detail), the latest automatic stop `latest_stop_at` derived by the server from `job.max_overrun_ratio`, and the supply gauge for this kind of request when present. (7) A live countdown to `quote_expires_at` (`price.quote_ttl_s`). (8) Notices `copy.req.notice_no_instant`, `copy.req.notice_credit_not_money` |
| States | `available`, `unavailable` (the window cannot be honoured now: alternatives `waitlist` and `reservation` are offered, S0.9.2 `job.waitlisted`), `expired` (read-only; Fix and resubmit), `v_prior` (the `v` line is labelled estimated), `insufficient_credit` (balance below `escrow.total_ucr`: shows the shortfall and `floor(balance / p)` cells the person could request now) |
| Actions | Continue to confirm (opens `SCR-req-08`), Refresh quote (`getQuote`), Join waitlist (`createWaitlistEntry`), Book a reservation (`SCR-req-10`), Cancel this request (`cancelJob`; no credit is held so nothing is refunded) |
| Copy intent | Show cost as a sum the person can check; show verification cost as a cost, not hidden; call the window a quote based on measured capacity; never "within X hours guaranteed" |
| Accessibility | The breakdown is a real table; the countdown is announced at coarse intervals only (not every second); amounts are read with units ("credits") |

- **AC-req-23** Given the FD§3.3 inputs (`v_ppm` 100000, `lambda_ppm` 50000, N = 240, balance 300 credits), When the quote renders, Then it shows p = 1.15, total 276, volunteer pay 240, verification pool 24 buying 24 verification cells, levy 12, balance after 24, `eta` 0.870 and a 2-day window as returned by the server (these are the FD's illustrative inputs, not measurements).
- **AC-req-24** Given `v_source` is `prior`, When the quote renders, Then the `v` line is labelled "estimated, not yet measured" and shows `price.v_prior` as its value.
- **AC-req-25** Given `window.status` is `unavailable`, When the quote renders, Then Continue to confirm is absent and Join waitlist and Book a reservation are offered; with `ff.job.reservations` off only the waitlist is offered.
- **AC-req-26** Given balance 100 credits and `p_ucr` 1,150,000, When `escrow.total_ucr` exceeds the balance, Then the screen shows the shortfall and the affordable cell count 86 (`floor(100,000,000 / 1,150,000)`), and Continue is disabled.

### SCR-req-08 Escrow confirmation (wizard step 7)

| Row | Content |
| --- | --- |
| Purpose | The single, explicit act that holds credit and admits the job |
| Entry conditions | Job `quoted`, `window.status` `available`, quote not expired, balance sufficient |
| Blocks | A summary (template, `cell_count`, declarations in words, window, total to hold, balance after) in a region that receives initial focus. Required acknowledgements, each a separate tick with its own text: `window_is_quote` (always) and `downstream_use_uncontrolled` (only when the license is `L1` or `L2`, RD-09). The notices `copy.req.notice_declared` and `copy.req.notice_credit_not_money`. Button "Confirm and hold {total} credits" |
| States | `ready`, `submitting`, `conflict_quote_changed` (`409 STATE_CONFLICT`, `details.reason` `quote_changed`: reloads the quote and returns to `SCR-req-07`), `conflict_policy_changed` (`details.reason` `policy_version_changed`: the quote is void, Fix and resubmit is offered, nothing was charged), `insufficient_credit`, `at_job_cap` (`CAP_EXCEEDED`, `details.cap` `concurrent_jobs`) |
| Actions | `confirmEscrow` with `{quote_hash, acknowledgements}` and one `Idempotency-Key` (11.33.4) |
| Copy intent | Say exactly what happens: credit is held now, volunteers are paid per accepted cell, unspent credit returns, results arrive in the quoted window or in part; the button states the amount |
| Accessibility | Ticks are native checkboxes; the button's accessible name contains the amount; the result (`admitted`) is announced and focus moves to the progress heading |

- **AC-req-27** Given a license of `L2`, When the acknowledgement `downstream_use_uncontrolled` is not ticked, Then the Confirm button is disabled; given license `L0` the tick is not rendered and is not sent.
- **AC-req-28** Given the person double-taps Confirm, When both requests carry the same `Idempotency-Key`, Then exactly one `escrow_hold` exists, the second response is a replay, and the screen shows one admitted job.
- **AC-req-29** Given the quote changed since it was shown (different `quote_hash`), When Confirm is pressed, Then the server answers `409 STATE_CONFLICT` with `details.reason` `quote_changed`, no credit moves, and the new quote is shown for a fresh decision.
- **AC-req-30** Given the active policy version changed after the quote, When Confirm is pressed, Then the job is not admitted, `copy.req.err_policy_changed` is shown and Fix and resubmit is offered.

## 11.37 Quote and escrow as displayed

The numbers come from the server (RD-01). The client may check that the quote is internally consistent before enabling Confirm; this is an integrity check, not a second price calculation.

```
function quote_is_consistent(q):                      # all arithmetic on arbitrary-precision integers
  N = q.cells_primary
  return q.price.p_ucr           == 1_000_000 + q.price.v_ppm + q.price.lambda_ppm          # S0.6.1
     and q.escrow.primary_pay_ucr        == N * 1_000_000
     and q.escrow.verification_pool_ucr  == N * q.price.v_ppm
     and q.escrow.levy_ucr               == N * q.price.lambda_ppm
     and q.escrow.total_ucr              == N * q.price.p_ucr
     and q.escrow.total_ucr              == primary_pay + verification_pool + levy
     and q.escrow.verification_cells     == floor(q.escrow.verification_pool_ucr / 1_000_000)
     and q.balance.after_ucr             == q.balance.before_ucr - q.escrow.total_ucr
# if false: Confirm stays disabled, copy.req.err_quote_inconsistent is shown, and the quote_hash is attached to an automatic createReport

function affordable_cells(balance_ucr, p_ucr): return floor(balance_ucr / p_ucr)           # shown when balance is short
```

Worked example (FD§3.3 inputs; reproduces S0.6.1; illustrative, not measured):

| Quote field | Value | Derivation |
| --- | --- | --- |
| `p_ucr` | 1,150,000 (shown 1.15) | 1,000,000 + 100,000 + 50,000 |
| `escrow.total_ucr` | 276,000,000 (276 credits) | 240 x 1,150,000 |
| `primary_pay_ucr` / `verification_pool_ucr` / `levy_ucr` | 240,000,000 / 24,000,000 / 12,000,000 | 240 x 1,000,000; 240 x 100,000; 240 x 50,000 |
| `verification_cells` | 24 | `floor(24,000,000 / 1,000,000)` |
| `balance.after_ucr` | 24,000,000 (24 credits) | 300,000,000 - 276,000,000 |
| `eta_ppm` | 869,565 (shown 0.870) | `floor(10^12 / 1,150,000)` |
| Window | 2 days as returned by admission (S6.*) | The client does not compute it; the FD§3.3 capacity arithmetic (320 cells >= 264 committed) is S6.* |

Labels (copy keys; every row carries `needs_human_and_legal_review`):

| Key | EN | FA |
| --- | --- | --- |
| `copy.req.quote_p_line` | Price per cell = 1 + verification + reserve levy | قیمت هر سلول = ۱ + هزینهٔ راست‌آزمایی + عوارض ذخیره |
| `copy.req.quote_volunteer_pay` | Credit paid to volunteers for the cells themselves | اعتباری که به ازای انجام خود سلول‌ها به داوطلبان پرداخت می‌شود |
| `copy.req.quote_verification` | Checking: extra cells that verify and redo work | راست‌آزمایی: سلول‌های اضافی برای بررسی و تکرار کار |
| `copy.req.quote_levy` | Reserve levy: goes to the public Commons Reserve | عوارض ذخیره: به ذخیرهٔ عمومی مشترک می‌رود |
| `copy.req.quote_total` | Total credit held now | جمع اعتباری که همین الان نگه‌داشته می‌شود |
| `copy.req.quote_eta` | Round-trip efficiency: cells you can request per cell you contribute | بازدهی رفت‌وبرگشت: به ازای هر سلول مشارکت، چند سلول می‌توانید درخواست کنید |
| `copy.req.quote_v_measured` | Measured over the last {days} days from {cells} cells | اندازه‌گیری‌شده در {days} روز گذشته از {cells} سلول |
| `copy.req.quote_v_prior` | Estimated, not yet measured | برآوردی؛ هنوز اندازه‌گیری نشده |
| `copy.req.quote_window` | Quoted window (not a promise of instant completion) | بازهٔ زمانی اعلام‌شده (نه وعدهٔ انجام فوری) |

## 11.38 Waitlist and reservation screens

### SCR-req-09 Waitlist

| Row | Content |
| --- | --- |
| Purpose | Show a requester whose window cannot be honoured now where they stand and what happens next |
| Entry conditions | Job `waitlisted` (a `WaitlistEntry` exists) |
| Blocks | Position (`position`, first-come within the deadline class, FD§4.8), the date the place lapses (`admission.waitlist_ttl_days`), the supply gauge for the request kind, a plain statement that **no credit is held while waiting**, what happens on release (the job is re-quoted and the person has `admission.waitlist_claim_ttl_s` to confirm), and the alternative Book a reservation |
| States | `waiting`; `released` (banner and link to `SCR-req-07`, with the claim countdown); `expired` (`job.waitlist_expired`: the job is `cancelled`, nothing was held); `left` |
| Actions | `getWaitlistEntry` (polled), `deleteWaitlistEntry` (Leave the waitlist), open `SCR-req-10` |
| Copy intent | Honest about uncertainty: position can change; no estimate of a date is invented; the person may leave at any time at no cost |
| Accessibility | Position and lapse date are plain text; the released banner is `role="alert"` only when the person is on the page, otherwise it waits on the home screen under Needs attention |

- **AC-req-31** Given a `waitlisted` job, When the page loads, Then it shows the position, the lapse date in local time, and the statement that no credit is held.
- **AC-req-32** Given `job.waitlist_released` occurs, When the person opens the app, Then the home screen lists the job under Needs attention with the remaining claim time, and `SCR-req-07` shows the new quote with `quote_expires_at` set by `admission.waitlist_claim_ttl_s`.
- **AC-req-33** Given `admission.waitlist_max_per_member` is 1 and an entry exists, When the person joins a second waitlist, Then `422 CAP_EXCEEDED` with `details.cap` `waitlist_entries` is answered and `copy.req.err_cap_waitlist` is shown.

### SCR-req-10 Reservation booking

| Row | Content |
| --- | --- |
| Purpose | Book capacity for a future date (exam week, a deadline) with credit held at booking (FD§4.8) [H: flattens bursts] |
| Entry conditions | `ff.job.reservations` on; fewer than `reservation.max_active_per_member` active reservations; entered from home, the quote, or the waitlist |
| Blocks | Job type, number of cells, date within `reservation.max_horizon_days`; a calendar with Jalali and Gregorian shown together where `i18n.dual_calendar_detail` is true, each day marked available or not from `getReservationAvailability` (days at the share cap `reservation.capacity_share_cap` are unavailable); the four declarations in compact form (a reservation is policy-checked at booking and again at activation, `R9`); the hold: `escrow_ucr` as the server computes it; the terms object: free cancellation until a stated time (`reservation.free_cancel_notice_s` before the start), what applies after it, and what happens if the reservation is not activated; the sentence that the final job still passes screening and policy when activated |
| States | `no_availability` (no day offered; says so), `policy_rejected` (reasons as in 11.43.1), `insufficient_credit`, `at_reservation_cap` |
| Actions | `getReservationAvailability`, `createReservation` |
| Copy intent | Present a reservation as a hold with a date and conditions, never as a guarantee of completion; show every term the server returns, and for an enum value the client does not know show the generic line `copy.req.reservation_terms_generic` rather than guessing [V S6] |
| Accessibility | The calendar is operable by keyboard and has a list alternative ("available dates"); unavailable days state a reason, not only a style |

- **AC-req-34** Given `reservation.max_horizon_days` = 30, When a date 31 days ahead is chosen, Then it cannot be selected and the list alternative omits it.
- **AC-req-35** Given the booking passes, When Book is pressed, Then one `createReservation` is sent with its `Idempotency-Key`, the Reservation is `held`, `escrow_hold` is posted once, and `SCR-req-11` opens.
- **AC-req-36** Given the declared combination is not allowed by the active allowlist, When Book is pressed, Then `422 POLICY_REJECTED` shows the reasons and nothing is held.

### SCR-req-11 Reservation detail

| Row | Content |
| --- | --- |
| Purpose | Show a booking, let the requester activate it with a real job, or cancel it |
| Entry conditions | A `Reservation` of this member |
| Blocks | State (`held`, `activated`, `cancelled`, `expired`) with its date; booked cells and date; the held amount; the terms object; the cancellation terms in force now (`free_until` and `fee_ucr_if_cancelled_now`, both server values); when `held` and the start has arrived or is near: Create the job now |
| States | `held`, `activated` (links to the job), `cancelled` (refund shown as in `SCR-req-15`), `expired` (`reservation.expired`: refund shown) |
| Actions | `getReservation`, `cancelReservation`, Create the job now: starts the wizard with the reservation attached (`createJob` with `reservation_id` [A]); on `SCR-req-08` the button reads "Use my reserved credit" and calls `activateReservation` with `{job_id}` instead of `confirmEscrow`; no new hold is made (`escrow_release`, S0.8.5) |
| Copy intent | One place that shows what is held, until when, and what each choice costs |
| Accessibility | Terms in a definition list; the cancel confirmation names the exact amount returned |

- **AC-req-37** Given a `held` reservation cancelled before `free_until`, When the person confirms, Then the receipt shows the returned amount equal to the held amount, and the restored credit lots show their original expiry (`ISS-07`).
- **AC-req-38** Given a `held` reservation whose job has more cells than were booked, When `activateReservation` is sent, Then `422 CAP_EXCEEDED` with `details.cap` `reservation_cells` is shown and the reservation stays `held`.
- **AC-req-39** Given the reservation reached `expired`, When the page loads, Then the state, the date and the refund shown are those returned by the server, with no client-side computation.
