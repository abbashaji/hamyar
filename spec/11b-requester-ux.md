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

## 11.39 Job progress screens

### 11.39.1 Status vocabulary [D]

The requester sees two vocabularies: the job state (S0.9.2, 15 states) and a per-cell status derived from the `Cell` state (S0.9.3). Both are fixed lists so the map, the counts and the copy always agree.

| Job state | EN label | FA label | Requester actions |
| --- | --- | --- | --- |
| `draft` | Draft | پیش‌نویس | Continue, Delete (`job.cancel_requested`) |
| `screening` | Being checked | در حال بررسی | Wait |
| `rejected` | Not accepted | پذیرفته نشد | Fix and resubmit, Ask for review |
| `quoted` | Quote ready | قیمت و بازه اعلام شد | Continue, Cancel |
| `quote_expired` | Quote expired | قیمت منقضی شد | Fix and resubmit |
| `waitlisted` | On the waitlist | در فهرست انتظار | Leave the waitlist |
| `admitted` | Queued | در صف اجرا | View progress, Cancel |
| `running` | In progress | در حال اجرا | View progress, Cancel |
| `suspended` | Paused | موقتاً متوقف | View progress, Cancel |
| `assembling` | Putting results together | در حال آماده‌سازی نتایج | Wait |
| `settling` | Settling credit | در حال تسویهٔ اعتبار | Wait |
| `completed` | Completed | تکمیل شد | Results, Receipt, Rate |
| `cancelling` | Cancelling | در حال لغو | View progress |
| `cancelled` | Cancelled | لغو شد | Receipt (when credit was held) |
| `failed` | Ended incomplete | ناتمام ماند | Partial results, Receipt, Rate |

| Code | Cell status | Derived from `Cell` state | EN | FA | Shape (never colour alone) |
| --- | --- | --- | --- | --- | --- |
| `w` | `waiting` | `queued`, attempt 1 | Waiting for a volunteer | در انتظار داوطلب | hollow circle |
| `r` | `retrying` | `queued`, attempt above 1 (after `rejected` or `expired`) | Trying again | تلاش دوباره | hollow circle with arrow |
| `p` | `in_progress` | `leased` | With a volunteer | در دست اجرا | half-filled circle |
| `c` | `checking` | `submitted` | Being checked | در حال بررسی | filled circle with dot |
| `d` | `double_checking` | `flagged_for_audit` | Being double-checked | بررسی دوباره | double ring |
| `a` | `done` | `accepted` | Done | انجام شد | filled circle with tick |
| `s` | `paused` | `suspended` | Paused | متوقف | two bars |
| `x` | `stopped` | `cancelled`, `voided` | Stopped | بسته شد | square with cross |
| `f` | `failed` | `exhausted` (`cell.max_attempts` reached) | Could not be completed | انجام نشد | triangle with bar |
| `o` | `redo` | `overturned` (a `rework` cell takes over) | Being redone | در حال تکرار | circular arrow |

One index shows its latest effective cell: after `cell.overturned` the index shows `o` until the `rework` cell is accepted, then `a` (`ISS-05`). Gold cells are never indexed (RD-08). Statuses `c` and `d` never reveal who or why. [D]

Pause and stop causes (`pause_reason` values are convention additions [A]; `closure_reason` is S0.9.2):

| Value | Copy key | EN | FA |
| --- | --- | --- | --- |
| `kill_switch` | `copy.req.pause_kill` | The operators paused work for a moment. Your credit stays held and the request may continue when work resumes. | مدیران پلتفرم کار را موقتاً متوقف کرده‌اند. اعتبار شما همچنان نگه‌داشته می‌ماند و ممکن است با ازسرگیری کار ادامه یابد. |
| `template_paused` | `copy.req.pause_template` | The template used by this request was paused for review. | قالبِ این درخواست برای بازبینی موقتاً متوقف شده است. |
| `service_paused` | `copy.req.pause_service` | A service this request depends on was paused. | سرویسی که این درخواست به آن وابسته است موقتاً متوقف شده است. |
| `policy_tightened` | `copy.req.pause_policy` | A rule was tightened and this request is being re-checked. | یکی از قواعد سخت‌تر شده و این درخواست دوباره بررسی می‌شود. |
| `policy_stopped` | `copy.req.close_policy` | This request was stopped because a rule changed. Finished results are kept; unspent credit returns to you. | این درخواست به‌دلیل تغییر یک قاعده متوقف شد. نتایج انجام‌شده حفظ می‌شود و اعتبار مصرف‌نشده به شما برمی‌گردد. |
| `service_revoked` | `copy.req.close_service` | A service this request depends on is no longer approved. Finished results are kept; unspent credit returns to you. | سرویسی که این درخواست به آن وابسته بود دیگر تأیید نشده است. نتایج انجام‌شده حفظ می‌شود و اعتبار مصرف‌نشده به شما برمی‌گردد. |
| `template_retired` | `copy.req.close_template` | The template of this request was retired. Finished results are kept; unspent credit returns to you. | قالبِ این درخواست بازنشسته شد. نتایج انجام‌شده حفظ می‌شود و اعتبار مصرف‌نشده به شما برمی‌گردد. |
| `operator_killed` | `copy.req.close_operator` | The operators stopped this request. Finished results are kept; unspent credit returns to you. | مدیران پلتفرم این درخواست را متوقف کردند. نتایج انجام‌شده حفظ می‌شود و اعتبار مصرف‌نشده به شما برمی‌گردد. |
| `overrun_timeout` | `copy.req.close_overrun` | This request reached its latest stop time ({stop}) before every cell was finished. Finished results are kept; unspent credit returns to you. | این درخواست پیش از پایان همهٔ سلول‌ها به آخرین زمان توقف ({stop}) رسید. نتایج انجام‌شده حفظ می‌شود و اعتبار مصرف‌نشده به شما برمی‌گردد. |

### 11.39.2 Map encoding, bottleneck and on-track rules [D][A]

The progress response carries the map as one string of exactly `cells_primary` characters (code letters above, index order) plus an `attempts` object for indices whose attempt is above 1. Size is N bytes of map (derived: one character per cell), so 300 cells need about 300 bytes before the other fields; this suits low bandwidth and lets one request refresh the whole screen. The server builds it from `Cell` rows of `cell_kind` `primary` and their `rework` successors only.

```
function bottleneck(cells, now):                    # server side (S6.*/S8.* own the data); this file owns the display contract
  open = [c for c in cells if c.status not in (done, stopped, failed)]
  if open is empty: return null
  kind_of = { waiting: awaiting_volunteer, retrying: retrying, in_progress: in_progress,
              checking: awaiting_check, double_checking: awaiting_second_check, paused: paused }
  groups  = group open by kind_of[c.status]
  top     = group with the largest size; ties: oldest state_since, then the order above
  at_risk = [c for c in open if c.attempt >= cell.max_attempts - 1]      # one more failure exhausts it and fails the job
  return { kind: top.kind, cells: size(top), since: min(state_since of top), at_risk_cells: size(at_risk) }

function show_bottleneck_banner(progress):          # a neutral summary is always shown; the banner is the highlighted form
  return progress.timing.on_track == behind or progress.bottleneck.kind in (retrying, paused) or progress.bottleneck.at_risk_cells > 0

function on_track(job, now):                         # initial linear baseline, replaceable by an S6.* forecast; hypothesis [H]
  if job.done == 0: return unknown
  elapsed = (now - admitted_at) / (deadline_at - admitted_at)
  return on_track if job.done / job.cells_primary >= elapsed else behind
```

The linear baseline is crude because volunteer supply arrives in daily batches; whether `behind` predicts a missed quote is measured in Phase 1 (`P1M`, FD§9 "time to complete a large job versus quote") [H]. This borrows the panel's bottleneck idea (a banner naming the one thing holding work up) and its fixed status vocabulary, not its dependency graph: primary cells are independent, so there is nothing to lay out as a graph (11.48) [V].

### SCR-req-12 Job progress

| Row | Content |
| --- | --- |
| Purpose | Show where the request stands: overall progress, the per-cell status map, what is holding it up, and what the requester can do |
| Entry conditions | Job in `admitted`, `running`, `suspended`, `assembling`, `settling` or `cancelling` (terminal jobs redirect to `SCR-req-16` or `SCR-req-15`) |
| Blocks | (1) Header: job state label, template, `cell_count`, `deadline_at` in local time and `latest_stop_at`. (2) Summary: "{done} of {n} done" as text plus a bar, and `on_track` in words. (3) Status map: a grid of N tiles in index order, direction following the page direction (index 1 at the start edge), a row label every ten tiles, the legend of 11.39.1; a List view toggle shows the same data as a table. (4) Counts per status. (5) Bottleneck summary or banner (11.39.2). (6) Checking counters: "verification and redo cells used: {used} of {pool}" (gold cells are not distinguished) and "{n} results are held for a reviewer" from `withheld_for_review` (outputs with links, code or requests for action are withheld, FD§5.5). (7) Pause or closure banner with the copy of 11.39.1. (8) Actions |
| States | `queued_only` (`admitted`, no cell leased yet), `running`, `behind` (banner), `suspended`, `closing` (`settling` or `cancelling`), `stale` (last update older than twice `ui.requester.progress_poll_s`: the page says so and shows the update time) |
| Actions | Open a cell (`SCR-req-13`), Cancel this request (`SCR-req-14`), Refresh now, Report a problem (`createReport`). Polling `getJobProgress` every `ui.requester.progress_poll_s` with `If-None-Match`; polling stops while the tab is hidden and when the job is terminal |
| Copy intent | Calm and specific about the cause of delay; never blame volunteers; never promise a faster finish; say what the person can do (wait, cancel) |
| Accessibility | The map is a `role="grid"` with roving tabindex, arrow keys that follow the visual direction, and each tile named "cell 17, {status label}"; the List view is the default for screen-reader users who toggle it and its choice is remembered in memory only; counts are real text; updates are announced at most once per poll and only when a status count changes; `prefers-reduced-motion` removes tile transitions |

- **AC-req-40** Given `cells_primary` 240 and a `map` of 240 characters, When the page renders, Then 240 tiles appear in index order with shape and label per code; given a `map` whose length differs from `cells_primary`, Then the page shows `error_retry` and renders no partial map.
- **AC-req-41** Given an unchanged progress `ETag`, When the poll runs, Then a `304` leaves the DOM untouched; given the tab is hidden, Then no poll is sent until it is visible again.
- **AC-req-42** Given `on_track` = `behind` and the largest group is `awaiting_volunteer` with 150 cells, When the page renders, Then the banner says most remaining cells are waiting for volunteers and shows `at_risk_cells` when above zero.
- **AC-req-43** Given `pause_reason` = `kill_switch`, When the page renders, Then the paused banner shows `copy.req.pause_kill`, Cancel stays available and the credit is stated as still held.
- **AC-req-44** Given the page direction is RTL, When the map renders, Then index 1 is at the right edge, arrow-key navigation moves visually, and the legend uses shapes, not colour alone.

### SCR-req-13 Cell sheet

| Row | Content |
| --- | --- |
| Purpose | Explain one tile without exposing anyone or showing output early (RD-08, RD-10); the analogue of the panel's inspector [V] |
| Entry conditions | A tile chosen on `SCR-req-12` |
| Blocks | Index; status with label and shape; "attempt {n} of {max}" (`cell.max_attempts`); time in this state rounded to whole hours; "at risk" tag when the bottleneck rule marks it; an attempt list with outcome classes only (`not returned in time` for `lease_expired`, `did not pass the checks` for every other `reject.*` reason, `held for a reviewer` for a quarantined submission); for `double_checking` the line "another volunteer is double-checking this cell" |
| States | `ready`, `not_found` (the cell no longer maps to this job) |
| Actions | `getJobCell`; Report a problem with this cell (`createReport`); Close |
| Copy intent | Explain what the status means and what will happen next; keep outcome classes coarse so the sheet does not teach anyone how to beat verification |
| Accessibility | Opens as a dialog that returns focus to its tile; Escape closes it; the attempt list is an ordered list |

- **AC-req-45** Given a cell on attempt 3 with `cell.max_attempts` 5, When the sheet opens, Then it shows "attempt 3 of 5" from the parameter value, an "at risk" tag, and no volunteer identifier, no `vol_` handle and no output text anywhere in the response or the page.

## 11.40 Cancellation and refund screens

### SCR-req-14 Cancel a request

| Row | Content |
| --- | --- |
| Purpose | Let the requester stop a request, showing before they confirm exactly what is kept, paid and returned |
| Entry conditions | Cancel pressed on `SCR-req-12` (job `admitted`, `running` or `suspended`, escrow held) or on `SCR-req-07`, `SCR-req-09`, `SCR-req-01` (job `quoted`, `waitlisted` or `draft`, nothing held) |
| Blocks | With escrow: (1) what happens, in order: finished results are kept and can be downloaded as a partial result; cells already with volunteers are allowed to finish, and the ones that are accepted are paid; cells not started are cancelled; (2) the preview table from `getCancellationPreview`: held, paid to volunteers, reserve levy, refund with its three parts, and the equation "paid + levy + refund = held"; (3) the note that returned credit keeps its original expiry dates (`ISS-07`); (4) "This cannot be undone" and a Confirm cancellation button. Without escrow: one sentence that nothing was held, and Confirm |
| States | `no_escrow`, `preview_ready`, `cancelling` (after confirmation: `Job.cancelling`, shows the count of cells still `in_flight` and links to the receipt when `cancelled`), `too_late` (`409 STATE_CONFLICT`: the job reached `settling` or a terminal state; the page shows the new state instead) |
| Actions | `getCancellationPreview`, `cancelJob` (new `Idempotency-Key`; sends `job.cancel_requested`) |
| Copy intent | Cancelling is a normal, penalty-free choice; the numbers shown are a preview and the receipt is final; nothing blames the requester |
| Accessibility | Confirmation is a dialog with the amounts in text; focus starts on its heading; the destructive button is not the default action |

- **AC-req-46** Given 240 cells held at 276 credits with 100 primary and 9 verification cells accepted (illustrative), When the preview renders, Then it shows paid 109, levy 5, refund 162 made of 140 unstarted primary pay, 15 unspent verification pool and 7 unearned levy, and the equation 109 + 5 + 162 = 276 holds.
- **AC-req-47** Given a job in `draft`, `quoted` or `waitlisted`, When the person confirms, Then the job becomes `cancelled`, no refund table is shown, and the page says nothing was held.
- **AC-req-48** Given the job moved to `settling` while the dialog was open, When Confirm is pressed, Then `409 STATE_CONFLICT` is answered, no state changes, and the page shows the current state.

### SCR-req-15 Settlement receipt and refund display

| Row | Content |
| --- | --- |
| Purpose | One final, checkable account of where the held credit went, for completed, ended-incomplete and cancelled jobs, and for reservations that were cancelled or expired |
| Entry conditions | Job `completed`, `failed` or `cancelled` with an escrow, or a `Reservation` `cancelled` or `expired`; the receipt exists only after the escrow is `closed` (S0.9.8) |
| Blocks | (1) Held amount. (2) Paid to volunteers, with the counts of accepted primary and verification cells. (3) Reserve levy. (4) Refund with its three parts: unstarted primary pay, unspent verification pool, unearned levy; a refund smaller than one cell can include the pool remainder left by rounding (`ISS-04`). (5) The check line: paid + levy + refund = held, with a tick only when the integers match exactly. (6) Restored credit lots with their original expiry dates; for a lot already past expiry the line `copy.req.receipt_lot_expired` says it moves to the Reserve at the next sweep (`credit.expiry_sweep_interval_s`, `ISS-07`). (7) Receipt entries: `txn_` ids with their kinds (`settle`, `cancel`, `reservation_activate`). (8) Finish time against the quote as a signed number of seconds provided by the server, shown in words. (9) Links to results and rating |
| States | `ready`, `pending` (escrow not yet `closed`; the page polls and says settlement is in progress), `inconsistent` (the equality fails: the check line turns into an error, no amounts are presented as final, an automatic `createReport` carries the `job_id`) |
| Actions | `getSettlementReceipt`, Download results (`SCR-req-16`), Rate (`SCR-req-17`) |
| Copy intent | Show the identity so the person can audit it themselves; no jargon about ledger types; say that credit is not money and expires |
| Accessibility | The equation is also written as a sentence; amounts are in a table with row headers; a tick has the text "matches" |

- **AC-req-49** Given the FD§3.3 job completed (illustrative), When the receipt renders, Then held 276, paid 264 (240 primary + 24 verification), levy 12, refund 0 and the check line shows a tick.
- **AC-req-50** Given a receipt where `paid + levy + refund` differs from `held`, When it renders, Then the check line shows an error, the figures are labelled "not final", and one `createReport` is sent.
- **AC-req-51** Given a restored lot with `already_expired` true, When the receipt renders, Then `copy.req.receipt_lot_expired` is shown for that lot.

## 11.41 Results and rating screens

### SCR-req-16 Results download with provenance manifest

| Row | Content |
| --- | --- |
| Purpose | Deliver the assembled output and its provenance manifest, make integrity checkable on the device, and say plainly what the provenance does and does not show |
| Entry conditions | Job `completed` (a complete `Deliverable`) or `failed` or `cancelled` with accepted cells (a partial `Deliverable`, `completeness` `partial`, ISS-115) |
| Blocks | (1) Completeness banner; for a partial result the missing cell indices. (2) For licenses `L1` and `L2` the notice "downstream use uncontrolled" (11.45). (3) The declared no-training flag in words, marked as contractual and not technically enforced (`copy.req.notice_no_training`). (4) The untrusted-output notice (`copy.req.notice_untrusted_output`). (5) The files list from `getDeliverable`: name, media type, size, short hash, Download, and an integrity mark after download. (6) A text preview of the first `ui.requester.preview_chars` characters of a chosen text file, rendered inert (RD-14). (7) The manifest panel: Download manifest, Verify, and a plain-language summary (template and version, policy version, declared purpose, license and sensitivity, how many cells were verified by which method, which services volunteers reported using, with `copy.req.notice_service_attested`). (8) "Available until {date}" from `available_until` (terminal state plus `retention.job_payload_days`); after that the files are deleted and the manifest with its hashes stays (S0.7). (9) Rate this result, Report a problem |
| States | `ready`, `partial`, `withheld_present` (some outputs are held for a reviewer and not in the files; the count is shown), `purged` (past `available_until`: no download buttons; manifest only), `hash_mismatch` (a downloaded file's SHA-256 differs from the listed hash: the file is kept, marked untrusted, and Report a problem is prefilled) |
| Actions | `getDeliverable`, `downloadDeliverableFile` (`fetch` with the Bearer header; the bytes are saved from a `Blob`; the SHA-256 is computed on the device with the platform crypto API and compared with `files[].hash`; where the API is missing the page says integrity could not be checked), `getManifest`, `createReport` |
| Copy intent | Results come from strangers using AI services and are verified by sampling, not guaranteed correct; the manifest records what was declared and attested; hashes show the file is unchanged since assembly, not that its content is true |
| Accessibility | Preview text has `dir="auto"` and bidi isolation; the preview is a labelled region with a copy button; download buttons say the file name and size; after a download an `aria-live` message says whether the hash matched |

- **AC-req-52** Given a downloaded file whose SHA-256 equals `files[].hash`, When the download ends, Then the file shows "matches the manifest"; given a mismatch, Then it shows a warning, keeps the file and offers Report a problem.
- **AC-req-53** Given a partial deliverable with cells 17 and 18 missing, When the page renders, Then it states "partial", lists indices 17 and 18, and the manifest summary shows `completeness` `partial`.
- **AC-req-54** Given the job's terminal date plus `retention.job_payload_days` has passed, When the page loads, Then no Download button for result files is rendered, the manifest remains downloadable and the page says files were deleted by the retention rule.
- **AC-req-55** Given an output text containing `<script>alert(1)</script>` and a right-to-left override character, When the preview renders, Then the text is shown literally, nothing executes, no link is created and the override cannot reorder surrounding interface text.
- **AC-req-56** Given license `L2`, When the page renders, Then "downstream use uncontrolled" appears above the files list and in the manifest summary.

### SCR-req-17 Rate the outcome

| Row | Content |
| --- | --- |
| Purpose | Collect the requester's judgement of the outcome as a quality signal, without turning it into a verification method or a penalty |
| Entry conditions | Job `completed`, or `failed` or `cancelled` with accepted cells; within `ui.requester.rating_window_days` of the terminal state; no rating exists yet (one rating per job) |
| Blocks | Outcome: Good / Mixed / Poor (`outcome_rating`: `good`, `mixed`, `poor`). Optional tags: `accuracy`, `format`, `completeness`, `speed_vs_quote`, `other`. Optional comment up to `ui.requester.rating_comment_max_chars`. Optional "these cells look wrong": pick up to `ui.requester.rating_flag_cells_max` cell indices. A statement of use: the rating changes nobody's credit, is never shown to volunteers with the requester's name, and may lead to closer checks of the cells flagged; in aggregate it helps judge templates. The objective figure "finished {x} before or after the quoted deadline" is shown but is recorded by the system, not by the rating |
| States | `open`, `submitted` (read-only), `window_closed`, `not_eligible` |
| Actions | `createJobRating`, `getJobRating` |
| Copy intent | Short and optional; makes clear that a low rating is allowed and safe; never asks for personal details |
| Accessibility | Three outcomes are radio buttons with text labels and icons; the cell picker accepts typed indices and shows the chosen list as text |

Outcome and tag copy (rows carry `needs_human_and_legal_review`):

| Value | EN | FA |
| --- | --- | --- |
| `good` | Good | خوب |
| `mixed` | Mixed | متوسط |
| `poor` | Poor | ضعیف |
| `accuracy` | Accuracy | دقت |
| `format` | Output format | قالب خروجی |
| `completeness` | Completeness | کامل بون |
| `speed_vs_quote` | Time compared with the quote | زمان نسبت به بازهٔ اعلام‌شده |
| `other` | Something else | موارد دیگر |

- **AC-req-57** Given a `completed` job inside the rating window, When the person submits Good with tag `accuracy`, Then one `createJobRating` creates a `JobRating`, the screen becomes read-only and no cell state or ledger entry changes.
- **AC-req-58** Given a rating already exists, When a second submission is sent, Then `409 ALREADY_EXISTS` is answered and the stored rating is shown.
- **AC-req-59** Given `ui.requester.rating_flag_cells_max` cells are already picked, When another index is added, Then the picker refuses it and states the limit by its configured value.
- **AC-req-60** Given the rating window has passed, When the page loads, Then the form is absent and the page states that the window ended.

## 11.42 Provenance manifest (requester profile)

The manifest is the `Manifest` entity (`mfs_`, S0.7) attached to one `Deliverable`. It records FD§5.6 provenance in a form a requester can publish beside the output without exposing anyone. Hashing and encoding follow S0.6: content hashes are `sha256:<hex>` over raw bytes; the manifest hash is SHA-256 over RFC 8785 canonical JSON; ids are `<prefix>_<ulid>`; timestamps are RFC 3339 UTC. [D]

### 11.42.1 Field decisions [D][A]

| FD§5.6 item | Manifest field | Note |
| --- | --- | --- |
| Job and cell ids | `job_id`, `cells[].cell_id` | Opaque ids (S0.6.3); no member id appears |
| Template and version | `template.*` | Version is the immutable `TemplateVersion` |
| Input and output hashes | `input.input_hash`, `cells[].input_hash`, `cells[].output_hash`, `files[].hash` | Show integrity since assembly, not truth |
| Declared purpose, license, sensitivity | `declared.*` | `declared.enforcement` is the constant `declared_not_technically_enforced` |
| Policy profile and version | `policy.*`, `cells[].policy_version_id_at_acceptance` | Stamped at admission, re-checked at acceptance (`R9`) |
| Service and model as reported by the volunteer | `cells[].service` | `attestation` is the constant `volunteer_reported`: attested, not proven (FD§5.7 failure mode 7); `reported_model` is untrusted text of at most 80 characters |
| Verification method and result | `cells[].verification`, `verification_summary` | Gold cells are hidden and never listed; the summary counts them inside `verification_cells_run` |
| Timestamps | `generated_at`, `policy.stamped_at`, `cells[].accepted_at` | Per-cell times are rounded down to `job.manifest_time_granularity_s` so they cannot single out a volunteer's session (RD-08) |
| Salted-hash volunteer id | **not in this profile** | FD§5.6 says requesters never see it, yet also says exports carry the manifest; resolved by two profiles, `ISS-116`. The `internal` profile (admin only, S10.*) adds `cells[].volunteer_handle` (`vol_<32 hex>`, S0.6.4) and exact timestamps |
| License and no-training flag | `declared.license`, `declared.no_training_declared`, `declared.downstream_use_uncontrolled` | `no_training_declared` is true when the declared purpose is not `P3`; it is contractual, not technically enforced; `downstream_use_uncontrolled` is true for `L1` and `L2` |

A manifest is immutable. If a delivered cell is later overturned (`cell.overturned`), the platform builds a new `Deliverable` and `Manifest` whose `supersedes` names the old `mfs_` id; the old files stay downloadable until `available_until`. [A]

### 11.42.2 JSON Schema (draft 2020-12), version 1

Clients validate only the required fields and ignore unknown ones (S0.11.1). `S2` and `S3` never reach a manifest in Phases 1-2 (`R2`); widening the enum is a schema version change.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:hamyar:schema:manifest:requester:1",
  "title": "Hamyar provenance manifest, requester profile, version 1",
  "type": "object",
  "required": ["manifest_version", "manifest_id", "profile", "job_id", "deliverable_id", "generated_at", "completeness",
               "declared", "template", "policy", "input", "cells", "verification_summary", "files", "missing_cells",
               "supersedes", "manifest_hash", "signature"],
  "properties": {
    "manifest_version": { "const": 1 },
    "manifest_id":    { "type": "string", "pattern": "^mfs_[0-9a-hjkmnp-tv-z]{26}$" },
    "profile":        { "const": "requester" },
    "job_id":         { "type": "string", "pattern": "^job_[0-9a-hjkmnp-tv-z]{26}$" },
    "deliverable_id": { "type": "string", "pattern": "^dlv_[0-9a-hjkmnp-tv-z]{26}$" },
    "generated_at":   { "type": "string", "format": "date-time" },
    "completeness":   { "enum": ["complete", "partial"] },
    "supersedes":     { "type": ["string", "null"], "pattern": "^mfs_[0-9a-hjkmnp-tv-z]{26}$" },
    "declared": {
      "type": "object",
      "required": ["purpose", "license", "sensitivity", "service_requirement", "no_training_declared",
                   "downstream_use_uncontrolled", "enforcement"],
      "properties": {
        "purpose":     { "enum": ["P0", "P1", "P2", "P3"] },
        "license":     { "type": "object", "required": ["code", "spdx_id"],
                         "properties": { "code": { "enum": ["L0", "L1", "L2", "L3"] },
                                         "spdx_id": { "type": ["string", "null"], "maxLength": 64 } } },
        "sensitivity": { "enum": ["S0", "S1"] },
        "service_requirement": { "enum": ["M0", "M1", "M2"] },
        "no_training_declared":        { "type": "boolean" },
        "downstream_use_uncontrolled": { "type": "boolean" },
        "enforcement": { "const": "declared_not_technically_enforced" }
      }
    },
    "template": { "type": "object", "required": ["template_id", "template_version_id", "job_type"],
      "properties": { "template_id": { "type": "string", "pattern": "^tpl_[0-9a-hjkmnp-tv-z]{26}$" },
                      "template_version_id": { "type": "string", "pattern": "^tpv_[0-9a-hjkmnp-tv-z]{26}$" },
                      "job_type": { "type": "string", "pattern": "^[a-z][a-z0-9_]*$" } } },
    "policy": { "type": "object", "required": ["policy_id", "policy_version_id", "stamped_at"],
      "properties": { "policy_id": { "type": "string", "pattern": "^pol_[0-9a-hjkmnp-tv-z]{26}$" },
                      "policy_version_id": { "type": "string", "pattern": "^plv_[0-9a-hjkmnp-tv-z]{26}$" },
                      "stamped_at": { "type": "string", "format": "date-time" } } },
    "input": { "type": "object", "required": ["input_hash", "glossary_hash", "cell_count_primary"],
      "properties": { "input_hash": { "$ref": "#/$defs/sha256" },
                      "glossary_hash": { "oneOf": [ { "$ref": "#/$defs/sha256" }, { "type": "null" } ] },
                      "cell_count_primary": { "type": "integer", "minimum": 1 } } },
    "cells": { "type": "array", "items": { "type": "object",
      "required": ["cell_id", "index", "input_hash", "output_hash", "attempts", "accepted_at", "service", "verification",
                   "policy_version_id_at_acceptance"],
      "properties": {
        "cell_id": { "type": "string", "pattern": "^cel_[0-9a-hjkmnp-tv-z]{26}$" },
        "index": { "type": "integer", "minimum": 1 },
        "input_hash": { "$ref": "#/$defs/sha256" },
        "output_hash": { "$ref": "#/$defs/sha256" },
        "attempts": { "type": "integer", "minimum": 1 },
        "accepted_at": { "type": "string", "format": "date-time" },
        "policy_version_id_at_acceptance": { "type": "string", "pattern": "^plv_[0-9a-hjkmnp-tv-z]{26}$" },
        "service": { "type": "object", "required": ["service_id", "reported_model", "attestation"],
          "properties": { "service_id": { "type": "string", "pattern": "^svc_[0-9a-hjkmnp-tv-z]{26}$" },
                          "reported_model": { "type": ["string", "null"], "maxLength": 80 },
                          "attestation": { "const": "volunteer_reported" } } },
        "verification": { "type": "array", "minItems": 1, "items": { "type": "object", "required": ["method", "outcome"],
          "properties": { "method": { "enum": ["auto_check", "audit_second", "audit_third", "human_review", "blanket_redundancy"] },
                          "outcome": { "const": "pass" } } } }
      } } },
    "verification_summary": { "type": "object",
      "required": ["automatic_checks_passed", "cells_audited", "audit_mismatches", "third_executions", "human_reviews", "verification_cells_run"],
      "additionalProperties": { "type": "integer", "minimum": 0 } },
    "files": { "type": "array", "items": { "type": "object", "required": ["name", "media_type", "bytes", "hash"],
      "properties": { "name": { "type": "string", "pattern": "^[A-Za-z0-9._-]{1,100}$" },
                      "media_type": { "type": "string" }, "bytes": { "type": "integer", "minimum": 0 },
                      "hash": { "$ref": "#/$defs/sha256" } } } },
    "missing_cells": { "type": "array", "items": { "type": "integer", "minimum": 1 }, "uniqueItems": true },
    "manifest_hash": { "$ref": "#/$defs/sha256" },
    "signature": { "oneOf": [ { "type": "null" },
      { "type": "object", "required": ["alg", "key_id", "value"],
        "properties": { "alg": { "const": "Ed25519" }, "key_id": { "type": "string" }, "value": { "type": "string" } } } ] }
  },
  "$defs": { "sha256": { "type": "string", "pattern": "^sha256:[0-9a-f]{64}$" } }
}
```

The `signature` field is optional in value (`null` allowed) because a platform signing key is a new secret that S10.* must name and the owner must decide on (S3.*) [A][V]. Without it the manifest gives integrity (hashes) but not authenticity of origin; the interface says so (`copy.req.notice_manifest_limits`).

Example instance (two cells; hashes abbreviated with `...` for reading; a real value is `sha256:` plus 64 hex characters; every value is illustrative):

```json
{ "manifest_version": 1, "manifest_id": "mfs_01j9z6x4k7q2m8v5t3r1w0c9ab", "profile": "requester",
  "job_id": "job_01j9z6x4k7q2m8v5t3r1w0c9ac", "deliverable_id": "dlv_01j9z6x4k7q2m8v5t3r1w0c9ad",
  "generated_at": "2026-11-14T09:00:00Z", "completeness": "complete", "supersedes": null,
  "declared": { "purpose": "P1", "license": { "code": "L2", "spdx_id": null }, "sensitivity": "S0", "service_requirement": "M0",
                "no_training_declared": true, "downstream_use_uncontrolled": true, "enforcement": "declared_not_technically_enforced" },
  "template": { "template_id": "tpl_...", "template_version_id": "tpv_...", "job_type": "translation_glossary" },
  "policy": { "policy_id": "pol_...", "policy_version_id": "plv_...", "stamped_at": "2026-11-12T09:30:00Z" },
  "input": { "input_hash": "sha256:...", "glossary_hash": "sha256:...", "cell_count_primary": 2 },
  "cells": [ { "cell_id": "cel_...", "index": 1, "input_hash": "sha256:...", "output_hash": "sha256:...", "attempts": 1,
               "accepted_at": "2026-11-13T14:00:00Z", "policy_version_id_at_acceptance": "plv_...",
               "service": { "service_id": "svc_...", "reported_model": "as typed by the volunteer", "attestation": "volunteer_reported" },
               "verification": [ { "method": "auto_check", "outcome": "pass" } ] },
             { "cell_id": "cel_...", "index": 2, "input_hash": "sha256:...", "output_hash": "sha256:...", "attempts": 2,
               "accepted_at": "2026-11-13T16:00:00Z", "policy_version_id_at_acceptance": "plv_...",
               "service": { "service_id": "svc_...", "reported_model": null, "attestation": "volunteer_reported" },
               "verification": [ { "method": "auto_check", "outcome": "pass" }, { "method": "audit_second", "outcome": "pass" } ] } ],
  "verification_summary": { "automatic_checks_passed": 2, "cells_audited": 1, "audit_mismatches": 0, "third_executions": 0,
                            "human_reviews": 0, "verification_cells_run": 1 },
  "files": [ { "name": "output-001.txt", "media_type": "text/plain", "bytes": 4096, "hash": "sha256:..." } ],
  "missing_cells": [], "manifest_hash": "sha256:...", "signature": null }
```

### 11.42.3 Verification on the device [D]

```
function verify_manifest(manifest_bytes, downloaded_files):         # runs in the browser; no server call
  m = parse_json(manifest_bytes)
  ok_shape = has_required_fields(m, schema_v1) and m.manifest_version == 1
  body     = m without the keys manifest_hash and signature
  expected = "sha256:" + hex(SHA256(RFC8785_canonical(body)))       # S0.6.4: one canonicalizer for the whole system
  ok_hash  = (expected == m.manifest_hash)
  for f in m.files: ok_file[f.name] = f.name in downloaded_files and "sha256:" + hex(SHA256(downloaded_files[f.name])) == f.hash
  idx      = [c.index for c in m.cells] + m.missing_cells
  ok_cells = unique(idx) and sorted(idx) == [1 .. m.input.cell_count_primary]
             and (m.completeness == complete implies m.missing_cells is empty)
  ok_sig   = "not_signed" if m.signature is null else verify_ed25519(m.signature.value, expected, public_key(m.signature.key_id))
  return { ok_shape, ok_hash, ok_file, ok_cells, ok_sig }          # shown as a checklist, each line with its meaning
```

The public key set for `signature.key_id` would be published on the public parameters page (S12.*) [A][V]. A failed line never hides the file; it states what could not be confirmed.

- **AC-req-61** Given a manifest whose `cells` and `missing_cells` indices cover 1..N exactly once, When Verify runs, Then `ok_cells` is true; given an index missing or repeated, Then it is false and the checklist names the index.
- **AC-req-62** Given a manifest body altered by one character, When Verify runs, Then `ok_hash` is false and the page states that the manifest does not match its recorded hash.
- **AC-req-63** Given the requester profile, When the manifest is parsed, Then no key named `volunteer_handle` exists at any depth and no `accepted_at` has a finer granularity than `job.manifest_time_granularity_s`.

## 11.43 Rejection reasons, errors and appeal

All rows of 11.43 to 11.45 carry the marker `needs_human_and_legal_review` (S0.5). Placeholders in braces are filled from parameters or server fields (RD-15). No row states a legal conclusion; wording about what terms "permit" refers to the reviewed Service Registry flags, where `unknown` counts as `no` (S0.8.3).

### 11.43.1 Requester-visible policy rejection reasons [D]

Reasons arrive as `policy.<policy_rule_id>.<slug>` (S0.8.4) in `rejection.reasons` (a `Job` in `rejected`) or `details.reasons` (`422 POLICY_REJECTED`). Reasons are shown in the order received. `R10` is a change workflow, not a job rejection: it has no requester copy and appears only in the public change log.

| Code | Copy key | EN (reason, then what to change) | FA |
| --- | --- | --- | --- |
| `policy.R1.metadata_missing_or_inconsistent` | `copy.req.reason_r1` | Some declarations are missing or do not fit together, for example a purpose and a license that are not allowed together. Complete all four declarations and check the combination. | بعضی از اعلام‌ها ناقص است یا با هم سازگار نیست؛ برای نمونه هدف و مجوزی که با هم مجاز نیستند. هر چهار اعلام را کامل کنید و ترکیب آن‌ها را بررسی کنید. |
| `policy.R2.sensitivity_not_accepted` | `copy.req.reason_r2` | This request was declared, or found by the checks, to contain sensitive material or personal data of other people. In this phase Hamyar accepts only public (S0) or private but non-sensitive (S1) material. Remove that material, or do not use Hamyar for this job. | این درخواست حاوی مطالب حساس یا اطلاعات شخصِی دیگران اعلام شده یا بررسی‌ها چنین نشانه‌ای یافته‌اند. همیار در این مرحله فقط مطالب عمومی (S0) یا خصوصیِ غیرحساس (S1) را می‌پذیرد. آن مطالب را حذف کنید، یا برای این کار از همیار استفاده نکنید. |
| `policy.R3.prohibited_content` | `copy.req.reason_r3` | The request touches content Hamyar does not accept, or asks volunteers to do more than copy text, press Send and return text. We do not say which check applied. Change the request so that it only needs text to be returned. | این درخواست به محتوایی مربوط است که همیار نمی‌پذیرد، یا از داوطلب بیش از کپی متن، زدن ارسال و بازگرداندن متن می‌خواهد. نمی‌گوییم کدام بررسی اعمال شد. درخواست را طوری تغییر دهید که فقط بازگرداندن متن لازم باشد. |
| `policy.R4.template_required` | `copy.req.reason_r4` | Requests can only be made from reviewed templates. Choose a template; writing your own prompt is not available. | درخواست‌ها فقط از روی قالب‌های بازبینی‌شده ثبت می‌شوند. یک قالب انتخاب کنید؛ نوشتن دستور دلخواه ممکن نیست. |
| `policy.R5.commercial_needs_flag` | `copy.req.reason_r5` | Commercial use of results needs a service whose reviewed terms permit commercial use of outputs. None is available now, so this purpose cannot be accepted. | استفادهٔ تجاری از نتایج به سرویسی نیاز دارد که شرایط بازبینی‌شدهٔ آن این کار را مجاز کرده باشد. اکنون چنین سرویسی در دسترس نیست و این هدف پذیرفته نمی‌شود. |
| `policy.R6.training_needs_m2_or_flag` | `copy.req.reason_r6` | Using results to train or build other models needs an open-weight model with a checked license, or a service whose reviewed terms permit it, and only for public material. That is not available for this request. | استفاده از نتایج برای آموزش یا ساخت مدل‌های دیگر به مدلی با وزن‌های باز و مجوز بررسی‌شده، یا سرویسی که شرایط بازبینی‌شدهٔ آن اجازه دهد، و فقط برای مطالب عمومی نیاز دارد. این برای درخواست شما در دسترس نیست. |
| `policy.R7.license_exceeds_service_flags` | `copy.req.reason_r7` | The license you chose is wider than what the reviewed terms of the available services permit. Choose a narrower license, or a different service requirement. | مجوزی که انتخاب کرده‌اید گسترده‌تر از چیزی است که شرایط بازبینی‌شدهٔ سرویس‌های در دسترس اجازه می‌دهد. مجوز محدودتری انتخاب کنید یا الزام سرویس را تغییر دهید. |
| `policy.R8.volunteer_optin_mismatch` (not a rejection) | `copy.req.note_r8` | Few volunteers currently accept this kind of request, so the window may be longer. | اکنون داوطلبان کمی این نوع درخواست را می‌پذیرند، پس ممکن است بازهٔ زمانی بلندتر شود. |
| `policy.R9.policy_version_stale` | `copy.req.err_policy_changed` | The rules changed after your request was checked. Check it again; nothing was charged. | پس از بررسی درخواست شما، قواعد تغییر کرد. دوباره بررسی کنید؛ هیچ اعتباری کسر نشده است. |

For an unknown code the screen shows `copy.req.reason_unknown` (EN "This request was not accepted. The code below identifies the reason.", FA «This request...» is replaced by: «این درخواست پذیرفته نشد. کد زیر دلیل آن را مشخص می‌کند.») and still shows the code.

### 11.43.2 Errors and conditions [D]

`details.reason` and `details.cap` values are convention additions [A] (11.49).

| Condition | Copy key | EN | FA |
| --- | --- | --- | --- |
| `403 LAUNCH_GATE_CLOSED` | `copy.req.err_gate_closed` | Requests are not open yet. Nothing has been charged. | ثبت درخواست هنوز باز نشده است. هیچ اعتباری کسر نشده است. |
| `503 KILL_SWITCH_ENGAGED` | `copy.req.err_kill_switch` | New requests are paused by the operators. Try again later. Requests already running are not changed unless they show a pause. | ثبت درخواست جدید را مدیران پلتفرم موقتاً متوقف کرده‌اند. بعداً دوباره امتحان کنید. درخواست‌های در حال اجرا تغییر نمی‌کنند، مگر آنکه توقف نشان دهند. |
| `422 INSUFFICIENT_CREDIT` | `copy.req.err_insufficient_credit` | You need {needed} credits and have {have}. You can request up to {affordable} cells now. | به {needed} اعتبار نیاز دارید و {have} اعتبار دارید. اکنون می‌توانید تا {affordable} سلول درخواست کنید. |
| `422 CAP_EXCEEDED`, `cap` = `concurrent_jobs` | `copy.req.err_cap_jobs` | You already have the maximum number of active requests ({max}). Wait for one to finish or cancel one. | شما هم‌اکنون بیشترین تعداد درخواست فعال ({max}) را دارید. منتظر پایان یکی بمانید یا یکی را لغو کنید. |
| `CAP_EXCEEDED`, `cap` = `job_cells` | `copy.req.err_cap_cells` | A request can have at most {max} cells; this one has {n}. | هر درخواست حداکثر {max} سلول دارد؛ این درخواست {n} سلول دارد. |
| `CAP_EXCEEDED`, `cap` = `waitlist_entries` | `copy.req.err_cap_waitlist` | You can be on at most {max} waitlist(s) at a time. | هم‌زمان می‌توانید در حداکثر {max} فهرست انتظار باشید. |
| `CAP_EXCEEDED`, `cap` = `reservations` | `copy.req.err_cap_reservations` | You already have the maximum number of reservations ({max}). | شما هم‌اکنون بیشترین تعداد رزرو ({max}) را دارید. |
| `CAP_EXCEEDED`, `cap` = `reservation_cells` | `copy.req.err_cap_reservation_cells` | This request has more cells than your reservation covers ({max}). | این درخواست سلول بیشتری از مقدار پوشش رزرو شما ({max}) دارد. |
| `422 NO_CAPACITY` | `copy.req.err_no_capacity` | There is no capacity for this request within the longest window now. You can join the waitlist or book a reservation. | اکنون برای این درخواست در بلندترین بازهٔ ممکن ظرفیتی نیست. می‌توانید در فهرست انتظار بمانید یا رزرو کنید. |
| `422 UNPROCESSABLE`, `reason` = `no_approved_service` | `copy.req.err_no_service` | No approved service is available for this request right now. Nothing has been charged. | اکنون برای این درخواست سرویس تأییدشده‌ای در دسترس نیست. هیچ اعتباری کسر نشده است. |
| `413 PAYLOAD_TOO_LARGE` | `copy.req.err_too_large` | The file is larger than the limit ({max}). | حجم فایل از حد مجاز ({max}) بیشتر است. |
| `400 VALIDATION_FAILED` | `copy.req.err_validation` | Please check the marked fields. | لطفاً بخش‌های مشخص‌شده را بررسی کنید. |
| `429 RATE_LIMITED` | `copy.req.err_rate_limited` | Too many attempts. Try again in {wait}. | تلاش‌ها زیاد بوده است. {wait} دیگر دوباره امتحان کنید. |
| `409 STATE_CONFLICT`, `reason` = `quote_changed` | `copy.req.err_quote_changed` | The price or window changed. Please review the new quote; nothing was charged. | قیمت یا بازهٔ زمانی تغییر کرد. لطفاً قیمت جدید را بررسی کنید؛ هیچ اعتباری کسر نشده است. |
| `STATE_CONFLICT`, other reasons | `copy.req.err_state` | This request changed in the meantime. The current state is shown. | وضعیت این درخواست میان این مدت تغییر کرده است. وضعیت فعلی نمایش داده می‌شود. |
| `412 PRECONDITION_FAILED` | `copy.req.err_stale` | This page was out of date and has been reloaded. | این صفحه قدیمی بود و دوباره بارگذاری شد. |
| Quote expired (`Job.quote_expired`) | `copy.req.err_quote_expired` | The quote expired. Nothing was held. Start again from this request. | قیمت منقضی شد. اعتباری نگه‌داشته نشد. از همین درخواست دوباره شروع کنید. |
| `member_blocked`: `403 FORBIDDEN` | `copy.req.err_member_blocked` | Your account cannot start requests right now. | حساب شما اکنون نمی‌تواند درخواست جدید شروع کند. |
| `member_blocked`: recovery cooldown | `copy.req.err_recovery_cooldown` | After an identity is recovered, requests and spending wait until {time}. | پس از بازیابی هویت، ثبت درخواست و مصرف اعتبار تا {time} ممکن نیست. |
| `500/503 INTERNAL`, `UNAVAILABLE` | `copy.req.err_internal` | Something went wrong on our side. Your data is kept; try again. | مشکلی از سمت ما پیش آمد. اطلاعات شما حفظ شده است؛ دوباره امتحان کنید. |
| Quote fails `quote_is_consistent` | `copy.req.err_quote_inconsistent` | The numbers in this quote do not add up, so confirmation is disabled. A report was sent. | اعداد این قیمت با هم نمی‌خواند، پس تأیید غیرفعال شد. گزارشی ارسال شد. |
| Receipt fails the equality | `copy.req.err_receipt_inconsistent` | These figures do not add up and are not final. A report was sent. | این ارقام با هم نمی‌خوانند و نهایی نیستند. گزارشی ارسال شد. |

### SCR-req-18 Ask for a human review (appeal of a job rejection)

| Row | Content |
| --- | --- |
| Purpose | Let a requester challenge a `rejected` job once, within the appeal window (`appeal_kind` `job_rejection`, S0.9.7) |
| Entry conditions | Job `rejected`; `rejection.appeal.allowed_until` in the future; fewer than `appeal.max_per_decision` appeals filed for this decision |
| Blocks | The recorded reasons; a note field up to `ui.requester.appeal_note_max_chars` ("why do you think this is wrong"); a statement that a reviewer who did not make the decision will look, that the target time is `appeal.reviewer_sla_days` days and is a target, not a promise, and that the decision can be upheld or overturned; Send. After filing: the appeal state in words (`filed`, `assigned`, `in_review`, `awaiting_second_review`, `upheld`, `overturned`, `withdrawn`) |
| States | `open`, `filed` (read-only, polled with `getAppeal`), `window_closed`, `already_filed`, `overturned` (banner and Continue: Fix and resubmit creates a copy whose screening records the appeal id; how the reversal is applied to the copy is S7.* and S10.* [V]) |
| Actions | `createAppeal` with `{appeal_kind: "job_rejection", job_id, note}`, `getAppeal` |
| Copy intent | A request for a second pair of eyes, not a fight; no promise of outcome; no new sensitive material should be pasted into the note (say so) |
| Accessibility | The note field has a counter with the limit as text; the status is `role="status"` |

Appeal state labels (`copy.req.appeal_<state>`): `filed` Filed / ثبت شد; `assigned` Assigned to a reviewer / به بازبین سپرده شد; `in_review` Being reviewed / در حال بررسی; `awaiting_second_review` Waiting for a second review / در انتظار بررسی دوم; `upheld` Decision upheld / تصمیم تأیید شد; `overturned` Decision overturned / تصمیم لغو شد; `withdrawn` Withdrawn / پس گرفته شد.

- **AC-req-64** Given a `rejected` job inside the window, When the person files with a note, Then one `createAppeal` with `appeal_kind` `job_rejection` is sent with its `Idempotency-Key`, an `Appeal` in `filed` is shown, and the form becomes read-only.
- **AC-req-65** Given an appeal already filed for this decision and `appeal.max_per_decision` = 1, When the page loads, Then no second form is offered and the existing appeal's state is shown.
- **AC-req-66** Given the appeal is `overturned`, When the person presses Continue, Then a new job is created with `copy_from_job_id`, no credit has moved, and the wizard resumes at the step the server returns.
