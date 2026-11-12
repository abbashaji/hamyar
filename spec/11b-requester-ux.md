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
