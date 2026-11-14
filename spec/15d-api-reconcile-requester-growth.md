# 15.C API reconciliation (requester, copy and growth)

*Spec part 15, third S15 file · owner cell C-038 · reconciles the `/v1` paths that the requester screens (part 11b) and the public and growth part (part 12) cite and that `spec/15a-api-core.md` (S15a) and `spec/15b-api-admin.md` (S15b) do not define. S15a and S15b are canonical: where a citing part and S15 disagree, S15 wins unless a capability is genuinely missing, in which case this file defines it in the S15 table format. Nothing here has been verified against any provider's terms or any law; every provider-dependent value stays configuration data entered by a reviewer [V].*

## 15.C.1 Scope, method and legend

**What was read** [A]. S15a and S15b in full; 11b lines 108-160 (the operation table of 11b section 11.34); part 12 lines 22-46 (surface inventory), 270-420 (share cards, teams, referral), 458-474 and 504-518 (flags and exposure). A cited path without a line number was located in the same tables. Part 11d was not read, because the cell names no 11d line; whoever applies the edits below searches 11d for the same strings [A]. The cited paths use the path-parameter names of the citing part; normalized (`{}`) they are the paths of the cell.

**Decision classes** [D]

| Class | Meaning |
| --- | --- |
| ALIAS | The cited path means an existing S15 endpoint. The row gives that endpoint and every difference the citing part must absorb. |
| NEW | A real capability that S15 lacks. Defined in 15.C.4 in the S15 operation-table format, under the guards of 15.C.3. |
| REMOVE | The cited use should not exist (duplicate, or a capability S15 deliberately does not have). The row says what the citing part does instead. |

**Critical reading, not polite reading** [D]. Several citing-part proposals are not merely differently named: some would break a ground rule or contradict a canonical S15 decision (base64 uploads, a requester choosing to join a waitlist, a requester note to a reviewer, a per-member share token). Those are called out in the rows and in 15.C.7. Where this file found a contradiction inside S15 itself, it does not resolve it silently: it lists it in 15.C.7 for the whole-API consistency cell.

**Result** [D]. 29 paths: 18 ALIAS, 9 NEW (11 operations), 2 REMOVE.

## 15.C.2 Decision table

Column `Cited at` is `part:line` where the cell gave a line; `12.9.2 table` is the operation table of 12.9.2, whose row line was not given to this cell. Operation ids of S15 are used exactly; new operation ids reuse the id the citing part proposed.

| # | Cited path | Cited at | Decision | S15 endpoint or new operation | Difference, or what the citing part must do |
| --- | --- | --- | --- | --- | --- |
| 1 | `/v1/appeals` | 11b:151 | NEW | `createAppeal`, `listAppeals` (15.C.4.1) | S15a 15.1 says member-facing appeals live in the sibling file, and S15b only has the admin queue `/v1/admin/appeals`: the member side was never defined. 11b body field `appeal_kind` becomes `kind`. |
| 2 | `/v1/appeals/{appeal_id}` | 11b:151 | NEW | `getAppeal`, `withdrawAppeal` (15.C.4.1) | Same gap. `withdrawAppeal` is added because S15b already emits `appeal.withdrawn`. |
| 3 | `/v1/deliverables/{deliverable_id}/files/{file_name}` | 11b:148 | ALIAS | `getJobDeliverableContent` `GET /v1/jobs/{job_id}/deliverable/content` | One text file per deliverable (`Deliverable.format`); the answer is JSON `{media_type, encoding, content, content_hash}`, never raw bytes, so a browser never renders it; the client saves it under a name it builds. No `file_name` segment and no `deliverable_id` in the path. Only in `completed` or `failed` jobs until `available_until`. |
| 4 | `/v1/experiment-exposures` | 12:38, 12:511 | NEW | `recordExperimentExposure` (15.C.4.2) | Request carries `surface_key` only; `assignment_id` is dropped because no S15 response exposes assignment ids. |
| 5 | `/v1/flags` | 12:38, 12:466 | ALIAS | `getFeatures` `GET /v1/members/me/features` | Returns `{flags: {name: bool}}`, no arm names; the 'effective variants' of 12.11 collapse to booleans. Assignment stays lazy and logged: evaluating a flag bound to a `running` experiment writes the deterministic assignment, which is the one side effect of this GET and the only place assignment is created. Multi-arm mechanics are an open point (15.C.7). |
| 6 | `/v1/jobs/{job_id}/cancellation-preview` | 11b:144 | NEW | `getCancellationPreview` (15.C.4.3) | S15 reveals the refund only after settlement, and `Job` has no refund field; a client must not recompute refund rules (S6 owns them). |
| 7 | `/v1/jobs/{job_id}/cell-preview` | 11b:130 | NEW | `previewCells` (15.C.4.4) | Cells exist only after `confirmJob`; the preview renders up to three cells from template, inputs and uploads without creating anything. Never a service, `open_url`, lease or nonce. |
| 8 | `/v1/jobs/{job_id}/cells/{cell_id}` | 11b:143 | ALIAS | `listJobCells` | S15 has no single-cell read. `JobCell` `{ordinal, cell_id, state, attempts}` is everything a requester may see (no volunteer, lease or nonce data). Screen 13 filters the page; outputs of accepted cells come from `listJobResults` by the same `ordinal`. `getJobCell` is dropped. |
| 9 | `/v1/jobs/{job_id}/escrow-confirmation` | 11b:136 | ALIAS | `confirmJob` `POST /v1/jobs/{job_id}/confirmations` | Body is `{quote_hash, reservation_id?}`. The 11b field `acknowledgements` is an unknown field (`400`): acknowledgements are declared earlier in `Declarations.acknowledgements`; a confirm-time checkbox is client-side only. Answer `{job, escrow, balance_after_ucr}`; errors `409 quote_expired`, `quote_changed`, `422 INSUFFICIENT_CREDIT`, `NO_CAPACITY`. |
| 10 | `/v1/jobs/{job_id}/glossaries` | 11b:129 | ALIAS | `createGlossary` `POST /v1/glossaries` | A glossary is a member-level resource, not nested under a job. Body `{name, source_lang, target_lang, entries}` (11b omits the first three); attached through `glossary_id` on `createJob` or `updateJob`; class `RL-UPLOAD`; same screening as uploads; `422 UNPROCESSABLE` reason `glossary_invalid`. |
| 11 | `/v1/jobs/{job_id}/receipt` | 11b:146 | NEW | `getSettlementReceipt` (15.C.4.5) | S15 has the events `job.settled` and `job.cancel_settled` but no requester read of what was paid, levied and refunded. |
| 12 | `/v1/jobs/{job_id}/submission` | 11b:131 | ALIAS | `submitJobForScreening` `POST /v1/jobs/{job_id}/screenings` | Outcomes: `200` Job `quoted` or `waitlisted`; `202` Job `screening` (human screening). A policy rejection is `422 POLICY_REJECTED` with `details.job_id` and `details.reasons`, job `rejected`: 11b expects 'already `rejected`' in a success body, so the screen must treat `422` as the rejection and read the job. `Idempotency-Key` required. |
| 13 | `/v1/jobs/{job_id}/uploads` | 11b:125 | ALIAS | `createUpload` `POST /v1/uploads` | Uploads are member-owned and attached by `upload_ids` on `createJob` or `updateJob`. Body `{format, filename?, content, content_hash?}`, `format` in `txt`, `csv`, `jsonl`, `json`; `content` is UTF-8 text inside JSON. `encoding: base64` and binary content are refused (cells are text, S15a 15.7.1): the client transcodes legacy encodings before sending. `file_name` is `filename`. Limit `job.max_upload_bytes` on decoded bytes. |
| 14 | `/v1/jobs/{job_id}/waitlist-entries` | 11b:133 | REMOVE | none | S15 never asks the requester to join a waitlist: `submitJobForScreening` makes the job `waitlisted` when admission decides `waitlist` (`Job.waitlist` `{position, expires_at}`, event `job.waitlisted`). Screen 07 shows the `waitlisted` state it gets back instead of a 'join' button; a requester who will not wait cancels (row 29). |
| 15 | `/v1/members/me/balance` | 11b:116 | ALIAS | `getBalance` `GET /v1/balance` | `cap_ucr` is `member_cap_ucr`; also `held_ucr`, `headroom_ucr`, `expiring_soon`, `next_expiry`, `earn_today`. `member_status` and `cooldown_ends_at` are not in `Balance`: read `getMe` (`status`, `recovery.cooldown_until`). |
| 16 | `/v1/members/me/credit-lots` | 11b:117 | ALIAS | `listLots` `GET /v1/balance/lots` | `Page<Lot>` ordered by `expires_at` ascending, filter `state`; `lot_id` is `id`; adds `remaining_ucr`, `origin`, `earned_at`, `state`. Operation id `listCreditLots` becomes `listLots`. |
| 17 | `/v1/policy-versions/current` | 11b:120 | ALIAS (composite) | `getTemplate` and `checkJobPolicy` | No member endpoint returns the allowlist or phase locks (`/v1/admin/policy-versions/{plv_id}` is admin only). The wizard (screen 05) takes the offered values from `getTemplate` `allowed` (purposes, licenses, sensitivities, service requirements, read from the active allowlist) and the joint verdict from `checkJobPolicy` (dry run, every failing rule, `policy_version_id`). `license_options` is `allowed.licenses`. Phase locks are not shown to requesters. |
| 18 | `/v1/public/experiments` | 12:34 | NEW | `listPublicExperiments` (15.C.4.7) | S15b publishes locked pre-registrations but no experiment list. |
| 19 | `/v1/public/ledger-checkpoints` | 12:29 | ALIAS | `listPublicLedgerCheckpoints` `GET /v1/public/ledger/checkpoints` | Segment `ledger/checkpoints`. Item `{date, seq, checkpoint_hash}`, query `from`, `to`; flag `ff.public.ledger_page`, `404` when off. |
| 20 | `/v1/public/ledger-checkpoints/{checkpoint_date}` | 12:29 | ALIAS | `listPublicLedgerCheckpoints` with `from` = `to` = the date | No by-date resource: one item or an empty page. The immutable by-date cache entry of 12 is not offered; the list answer carries `ETag` and `304`. |
| 21 | `/v1/public/ledger-flows` | 12:29 | ALIAS | `listPublicLedgerDaily` `GET /v1/public/ledger/daily` | Item `{date, by_entry_type: [{entry_type, count, amount_ucr}]}`, at most 366 days, figures lagged by `public.ledger_lag_s`. A 'flow' is one `entry_type` per day [A]; part 12 must not need per-account or per-entry flows, which S15b 15.33.3 withholds on purpose. |
| 22 | `/v1/public/teams` | 12:33 | NEW | `listPublicTeams` (15.C.4.8) | S15a says a listed team's name and total may appear on public surfaces but S15b has no public teams endpoint. |
| 23 | `/v1/reservations/availability` | 11b:137 | NEW | `getReservationAvailability` (15.C.4.6) | S15a only has `createReservation` with `dry_run` for one date; a calendar would need one write-weight call per date. Query uses `template_id` (as `createReservation` does), not `job_type`. |
| 24 | `/v1/reservations/{reservation_id}/activation` | 11b:141 | ALIAS | `confirmJob` with `reservation_id` | No separate call: `confirmJob` activates the reservation (event `+reservation.activated`), takes the escrow from it and tops up or refunds the price difference. The reservation must be `held`, the caller's and not past `target_date`, otherwise `409 STATE_CONFLICT` reason `reservation_state_invalid` [A]. |
| 25 | `/v1/share-cards/preview` | 12:35 | ALIAS | `getShareCard` `GET /v1/members/me/share-card` | Returns `{generated_at, contains_personal_data: false, verified_cells_total, badge_ids, referral_code_available}`. The 12.8.2 payload fields `cells_verified_total`, `badges` (member-selected), `locale`, `digits`, `landing_url`, `card_version` map as follows: the member selects badges client-side from `badge_ids`; `locale` and `digits` come from `getMe`; `landing_url` and `card_version` are client constants. `referral_code_available` must not be rendered (12.10.1: a referral link never goes on a card). The server stores nothing and mints no token; S15b 15.33.5 contradicts this (15.C.7). |
| 26 | `/v1/team-memberships/{membership_id}` | 12.9.2 table | ALIAS | `leaveTeam` `DELETE /v1/teams/{team_id}/memberships/me` | The membership id is never exposed; `204`; `Idempotency-Key` optional and honored if sent (12 says required). The row stays with `left_at` set, as 12.9.2 says. |
| 27 | `/v1/teams/{team_id}/reports` | 12.9.2 table | ALIAS (extends `createReport`) | `createReport` `POST /v1/reports` with `subject_kind` = `team`, `subject_id` = `id<tem>` | S15a's `subject_kind` list has no `team`. Adding it is additive in `v1` (S15a 15.13) once the S0 enum is edited (15.C.7, edit S1). The reporter must belong to the team or see it in the public list; category `abusive_or_unsafe` or `prohibited_content`; the reported party never sees the reporter. |
| 28 | `/v1/uploads/{upload_id}/review-requests` | 11b:128 | REMOVE | none | S15a 15.7.1: a `flagged` upload, and a share of all inputs, go to a reviewer automatically after `submitJobForScreening` (job `screening`, `202`). Screen 04 shows the finding codes and counts of `Upload.screening` and offers `deleteUpload` or 'submit for screening'. There is no requester note to a reviewer: no such channel exists, and requester free text in the reviewer UI is an injection surface [A]. |
| 29 | `/v1/waitlist-entries/{waitlist_entry_id}` | 11b:134, 11b:135 | ALIAS | `getJob`; `cancelJob` | `getJob` returns `waitlist` `{position, expires_at}`; the `waitlist_entry_id` in S15b events is internal. Leaving the waitlist is `cancelJob` `POST /v1/jobs/{job_id}/cancellation` in state `waitlisted`: `200`, job `cancelled` at once, terminal, nothing held. To try again the requester uses `copy_from_job_id`. |

## 15.C.3 Rules shared by every new operation [D]

1. **Member and admin stay apart.** Every new member operation has `auth_scheme` `member`; the two public operations are `none` under `/v1/public/*`; none touches `/v1/admin/*`, and an admin token on a member route stays `401 AUTH_INVALID`, reason `wrong_scheme` (S15a 15.4).
2. **No provider page, no credential.** No new operation accepts or returns a provider credential, cookie, session, chat link or chat-page content, and none reads a volunteer's page. `previewCells` shows only the text a requester supplied, wrapped by the template; it never shows a service, an `open_url`, a lease or a nonce.
3. **Writes are idempotent.** Every new write has `Idempotency-Key` `R` and names its natural idempotency underneath (S15a 15.10 rules apply: a deterministic `4xx` is stored, `5xx` and `429` are not).
4. **Minimal data.** A response carries only what its screen reads. No new response carries another member's `mem_` id, a `vol_` handle toward a requester, an IP address or an e-mail address (S15a 15.1). Public responses follow S15b 15.33.1 (no cookies, `PUB` rate class, `ETag`, `as_of`, small-number suppression below `analytics.min_cohort_k`).
5. **Errors.** Only codes of the S15a 15.9 catalogue. New `details.reason` values (additive in `v1`, S15a 15.13): `appeal_exists`, `appeal_window_closed`, `not_appealable`, `appeal_decided`, `job_incomplete`. No new `code`.
6. **Table format** is that of S15a: `Idem` is `R` required, `O` optional, `-` safe read; `RL` is a class of S15a 15.12 or S15b 15.21.2; `+name` in `Events` is an event proposed here (not in S0 0.9 or the S15b catalogue).
7. **Declared, not guaranteed.** A figure that is an estimate (cancellation refund, availability) is named an estimate and carries a copy key that says so; no field name promises an outcome (FD Principle 11).

## 15.C.4 New operations

### 15.C.4.1 Member appeals (rows 1 and 2)

S15b already has the admin queue (15.29.2), the events `appeal.filed`, `appeal.withdrawn`, `appeal.upheld`, `appeal.overturned` and the id prefix `apl_`. What is missing is the member side. A `suspended` or `banned` member may use all four operations (S15a 15.4: they can still file appeals). They are not marked active only. [D]

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `createAppeal` | `POST /v1/appeals` | member | R | `RL-WRITE` | 201 | `appeal.filed` |
| `listAppeals` | `GET /v1/appeals` | member | - | `RL-READ` | 200 | - |
| `getAppeal` | `GET /v1/appeals/{appeal_id}` | member | - | `RL-READ` | 200 | - |
| `withdrawAppeal` | `POST /v1/appeals/{appeal_id}/withdrawals` | member | R | `RL-WRITE` | 200 | `appeal.withdrawn` |

```
Appeal        { id: id<apl>, kind: enum<appeal_kind>, subject: { kind: "submission"/"job"/"member", id: id<sub>/id<job>/null },
                state: "filed"/"in_review"/"decided"/"withdrawn", outcome: "upheld"/"overturned"/null,
                outcome_copy_key: copy_key/null, statement: text<500>/null, filed_at: ts, decided_at: ts/null }
createAppeal  req { kind: "submission_rejection"/"job_rejection"/"member_ban", subject_id: id<sub>/id<job>/null, statement: text<500>? }
              201 { appeal: Appeal }       Location: /v1/appeals/{appeal_id}
listAppeals   Page<Appeal>, newest first, filters state, kind (S15a 15.11 order rule)
withdrawAppeal req {}   200 { appeal: Appeal }
```

| `kind` | `subject_id` | Guard at filing | Window |
| --- | --- | --- | --- |
| `submission_rejection` | `id<sub>` of the caller's own submission | `verdict` is `rejected` | now at most `Submission.appealable_until` (= `decided_at` + `appeal.window_days` x 86,400 s, S15a 15.6.4) |
| `job_rejection` | `id<job>` of the caller's own job | job `state` is `rejected` | `appeal.window_days` x 86,400 s after `Job.updated_at`, which no longer changes in a terminal state [A] |
| `member_ban` | null | the caller's `status` is `banned` | none while banned (S15b 15.29.6: a ban stays appealable) |

- **Mapping to the admin queue.** `state`: `filed` covers `appeal.filed`, `appeal.assigned` and `appeal.reassigned`; `in_review` covers `appeal.review_started` and `appeal.second_review_requested`; `decided` carries `outcome` from `appeal.upheld` or `appeal.overturned`, issued only when the final-decision rule of S15b 15.29.2 is met (two matching reviewers for `member_ban`); `withdrawn` from `withdrawAppeal`. `outcome_copy_key` is the `member_message_copy_key` the reviewer chose, so no free text reaches the member (S15b 15.29.6). [D]
- **No deadline is returned.** The reviewer `due_at` (`appeal.reviewer_sla_days`) is an internal target; returning it would be a promise (FD Principle 11). Copy says a reviewer will look at it. [D][A]
- **Statement.** `statement` is plain text, stored verbatim and shown to reviewers only as an escaped string (S9.*). It never contains a prompt or output unless the member pastes one; the platform does not add any. [D]
- **Visibility.** A subject that is not the caller's own is `404 NOT_FOUND` (S15a 15.3 rule 2). `template_rejection` is not fileable here: template authors are admin users (S15b 15.24) (15.C.7). [D]
- **Withdraw.** Only in `filed` or `in_review`; otherwise `409 STATE_CONFLICT` reason `appeal_decided`. A withdrawn appeal frees the subject for one new appeal inside the window. [A]
- **Errors.** `createAppeal`: `404 NOT_FOUND`; `409 ALREADY_EXISTS` reason `appeal_exists` (one non-withdrawn appeal per subject; also the natural idempotency, so a double click never files two); `409 STATE_CONFLICT` reason `appeal_window_closed` or `not_appealable`; `400 VALIDATION_FAILED` when `kind` and `subject_id` do not fit (`subject_id` required except for `member_ban`). Reads: `404 NOT_FOUND`.

Given / When / Then

- `AC-api-C01` Given a submission rejected two days ago whose `appealable_until` is in the future, When its owner calls `createAppeal` with `kind` `submission_rejection` and its `subject_id`, Then `201`, `state` `filed`, one `appeal.filed` event; the same call with the same key replays the stored body; a new key gives `409 ALREADY_EXISTS` reason `appeal_exists`; after `appealable_until` a new subject of the same kind gives `409 STATE_CONFLICT` reason `appeal_window_closed`.
- `AC-api-C02` Given a banned member, When they call `createAppeal` with `kind` `member_ban` and `subject_id` null, Then `201`, and every other operation of S15a that is active only still answers `403 FORBIDDEN`.

### 15.C.4.2 Experiment exposure (row 4)

12.11.5 needs the client to say that a member reached the decision point of a variant. The server finds the member's own assignment; the client never names an assignment or an arm. [D]

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `recordExperimentExposure` | `POST /v1/experiment-exposures` | member | R | `RL-WRITE` | 204 | `+experiment.exposed` |

```
recordExperimentExposure  req { surface_key: text<40> }        204, no body
```

- **Behavior.** The server maps `surface_key` to the flag of the mechanic (the surface keys are listed per mechanic in 12.12) and looks for the caller's assignment to the `running` experiment bound to that flag. If it exists the exposure is recorded once per (assignment, `surface_key`) and `experiment.exposed` is emitted; if it does not exist (flag off, no running experiment, member ineligible) nothing is recorded and the answer is the same `204`, so the endpoint cannot be used to learn whether an experiment runs or which arm the member holds. An unknown `surface_key` is `400 VALIDATION_FAILED` reason `field_invalid`, `details.fields[0].path` = `surface_key`; the keys are client constants, not secrets. [D]
- **Identical for every arm.** The call is made by the client for the control arm exactly as for the treatment arm (12.11.5). The event payload holds `experiment_id`, `surface_key` and the assignment id, never a member id beyond the envelope `actor`. [D]
- **Natural idempotency.** UNIQUE (assignment, `surface_key`); a repeat with a new key is `204` with no second event. [D]
- **Not active only.** A restricted member is eligible per 12.11; a `suspended` or `banned` member is ineligible, so nothing is recorded. [A]

Given / When / Then

- `AC-api-C03` Given a member assigned to the control arm of a running experiment, When the client posts the exposure twice with different keys, Then both answers are `204` and exactly one `experiment.exposed` exists; for a member with no assignment the answer is the same `204` and no row or event exists.

### 15.C.4.3 Cancellation preview (row 6)

S15a 15.7.3 says `cancelJob` refunds unstarted cells and that the refund is known only after settlement, and S6.* alone decides what part of the levy and the verification pool stays payable on a partial run. A client that guessed the refund would duplicate S6.* rules, so the preview is a server read that runs the same settlement function in dry-run mode. [D][A]

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `getCancellationPreview` | `GET /v1/jobs/{job_id}/cancellation-preview` | member | - | `RL-READ` | 200 | - |

```
CancellationPreview { job_id: id<job>, state: enum<job states of 0.9.2>, as_of: ts,
                      cancellable: bool, reason: null/"not_cancellable",
                      outcome: "immediate"/"settling"/null,
                      cells: { unstarted: int, in_flight: int, accepted: int },
                      escrow: { held_ucr: ucr, paid_out_ucr: ucr },
                      refund_estimate: { lower_ucr: ucr, upper_ucr: ucr }/null, basis_copy_key: copy_key }
```

- `outcome` is `immediate` in `draft`, `quoted` and `waitlisted` (`200`, nothing held, `refund_estimate` null) and `settling` in `admitted`, `running` and `suspended` (`202` on cancel). In any other state `cancellable` is `false` and `reason` is `not_cancellable`; the preview answers `200`, not `409`, because it is a read. [D]
- `cells.unstarted` is `queued` plus `suspended`, `in_flight` is `in_progress`, `accepted` as in `JobProgress` (S15a 15.7.3). `escrow` repeats `JobProgress.escrow`. [D]
- `refund_estimate` comes from the S6.* settlement function run on current state. This part defines no arithmetic; it fixes one invariant: 0 <= `lower_ucr` <= `upper_ucr` <= `escrow.held_ucr` - `escrow.paid_out_ucr`. The figure is an estimate, not a promise: in-flight cells may still be accepted or fail before settlement, and the amount that counts is the one in `getSettlementReceipt`. `basis_copy_key` points at the fixed text that says so. [D][A][P: `S6.*` defines the function and may return null when it cannot bound the refund]
- Owner only; another member's job is `404 NOT_FOUND`. The preview changes nothing and takes no `Idempotency-Key`. [D]

Given / When / Then

- `AC-api-C04` Given a `running` job with 240 primary cells of which 100 are `queued`, 20 `in_progress` and 120 `accepted`, When its owner calls `getCancellationPreview`, Then `cancellable` is `true`, `outcome` `settling`, `cells` is `{unstarted: 100, in_flight: 20, accepted: 120}`, `refund_estimate.upper_ucr` does not exceed `escrow.held_ucr` - `escrow.paid_out_ucr`, no event is emitted and nothing is posted; for a `completed` job `cancellable` is `false` with `reason` `not_cancellable`.

### 15.C.4.4 Cell preview (row 7)

A requester who pastes a wrong column is told only after a rejection or a bad result. A preview of three cells rendered by the template lets the wizard (screens 03 and 05) catch that before escrow. Cells and leases do not exist before `confirmJob`, so this is a pure render. [D][A]

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `previewCells` | `GET /v1/jobs/{job_id}/cell-preview` | member | - | `RL-READ` | 200 | - |

```
CellPreview { job_id: id<job>, as_of: ts, planned_cells: int,
              samples: [ { ordinal: int, prompt: { text: string, char_count: int, hash: hash },
                           output: { format: "text"/"json", max_chars: int, max_bytes: int } } ],      0..3 items
              findings: [ { code: string, count: int } ] }
```

- **Allowed states:** `draft`, `screening`, `quoted`, `waitlisted`. After `confirmJob` the cells exist and this is `409 STATE_CONFLICT` reason `job_state_invalid`. Missing required `inputs` or no attached upload is `422 UNPROCESSABLE` reason `job_incomplete`. [D]
- **Selection is deterministic:** the first, the middle (floor of half) and the last ordinal that the template splitter plans, so a repeated call returns the same bytes and an `ETag` works. `planned_cells` is the splitter output, read only and not stamped on the job; the stamped `cell_count` is still set by `submitJobForScreening`. [D]
- **As rendered by the same template function** as the volunteer work order: wrapper, delimiters, instruction text. The random delimiter token differs from the one a real cell gets, so the hash differs; the field `hash` is therefore a preview hash, not a cell hash. The preview carries no `service`, `open_url`, lease or nonce, and no volunteer ever sees a preview. [D]
- **Content stays the requester's own.** The text is the requester's own uploaded data inside the reviewed template; `findings` repeats `Upload.screening` counts only, never matched text (S15a 15.7.1). Not stored by the preview, never logged (S15a 15.3 rule 5), `Cache-Control: no-store`. [D]
- **Cost.** The render uses the splitter on up to `job.max_upload_bytes`; it shares `RL-READ`, and S12.* of the rate parameters may give it its own class if measurement shows abuse [A][H].

Given / When / Then

- `AC-api-C05` Given a `draft` job with an upload that the splitter plans as 240 cells, When its owner calls `previewCells` twice, Then both answers hold exactly three samples with ordinals 1, 120 and 240 and equal bodies, `planned_cells` is 240, and no `Cell`, `Lease` or ledger row exists; after `confirmJob` the same call is `409 job_state_invalid`.

### 15.C.4.5 Settlement receipt (row 11)

S15a promises a refund 'visible in `getJob`' (15.7.3), but the `Job` object has no refund field; the requester has no way to see what was paid out, levied and returned. [D]

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `getSettlementReceipt` | `GET /v1/jobs/{job_id}/receipt` | member | - | `RL-READ` | 200 | - |

```
Receipt { job_id: id<job>, state: enum<job states of 0.9.2>, settled_at: ts, escrow_ucr: ucr, refund_ucr: ucr,
          lines: [ { kind: "primary_pay"/"verification_pay"/"levy"/"refund", amount_ucr: ucr, cells: int/null } ] }
```

- **When:** only after settlement, that is in `completed`, `failed` (partial) and `cancelled` jobs whose escrow is `closed` (events `job.settled`, `job.settled_partial`, `job.cancel_settled`, `escrow.closed`). Before that, and for a job that never held escrow (`rejected`, `quote_expired`, `cancelled` from `draft`, `quoted` or `waitlisted`): `409 STATE_CONFLICT` reason `job_state_invalid`, `details.state`. [D]
- **Identity:** the ledger closes the escrow account to zero, so `escrow_ucr` equals the sum of all `lines` including `refund`, and `refund_ucr` equals the `refund` line (0 if absent). This is checkable by the client and by a test. [D]
- **Line kinds belong to S6.*;** an unknown kind is rendered by a client as 'other'. The receipt names no volunteer, no lease, no counterparty and no other job. [D][A][P: `S6.*` decides whether unused verification pool is a `refund` or another line]
- Owner only (`404 NOT_FOUND` otherwise); safe read; the same numbers appear on the member's own ledger entries (S15a 15.6.5) without a counterparty. [D]

Given / When / Then

- `AC-api-C06` Given a `completed` job whose escrow was 276,000,000 ucr, When its owner calls `getSettlementReceipt`, Then the sum of `lines[].amount_ucr` is `276000000`, `refund_ucr` matches the `refund` line, and for a `running` job the answer is `409 STATE_CONFLICT` reason `job_state_invalid`.
