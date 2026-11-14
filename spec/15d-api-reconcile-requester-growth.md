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
- **Cost.** The render uses the splitter on up to `job.max_upload_bytes`; it shares `RL-READ`; a class of its own is a rate-limit parameter decision (S16.*) if measurement shows abuse [A][H].

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

### 15.C.4.6 Reservation availability (row 23)

[D][A] Screen 10 shows a calendar. `createReservation` with `dry_run` answers for one date and spends a write-weight request each time (S15a 15.12), so a range read is needed. It applies exactly the guards of `createReservation` and reveals no capacity figure: the capacity dashboard (S15b 15.31) is admin only.

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `getReservationAvailability` | `GET /v1/reservations/availability` | member | - | `RL-READ` | 200 | - |

```
query   from: date, to: date, template_id: id<tpl>, cells: int
200     { as_of: ts, data: [ { date: date, bookable: bool,
                               reason: null/"date_full"/"reservation_capacity_share"/"reservation_horizon"/"reservation_limit",
                               price_per_cell_ucr: ucr/null, free_cancel_until: ts/null } ],
          page: { next_cursor: null, limit: int } }
```

- One entry per UTC date from `from` to `to`, ascending. `reason` repeats the `details.reason` that `createReservation` would return (`CAP_EXCEEDED` for the three limits, `NO_CAPACITY` for `date_full`), so one set of copy keys serves both. `price_per_cell_ucr` and `free_cancel_until` are the values `createReservation` would lock, present only when `bookable` is `true`. The list is bounded by `reservation.max_horizon_days`, so `next_cursor` is always null; the `Page` shape is kept for clients. [D]
- `from` must not be before today (UTC), `to` not before `from`, the range at most `reservation.max_horizon_days` days, `cells` an integer from 1 to `admission.max_job_cells`, `template_id` an approved, unpaused template: else `400 VALIDATION_FAILED` (`range`). A date past the horizon inside a wider request is not returned; asking for one is the `400`. [D]
- `bookable` is an estimate at `as_of`, not a hold: `createReservation` can still answer `NO_CAPACITY` (the normal race, as for offered cells in S15a 15.11). Copy says so. [D]
- With `ff.job.reservations` off: `403 FORBIDDEN` reason `feature_disabled`, `details.flag` = `ff.job.reservations` (S15a 15.7.4). Not active only; a member at `reservation.max_active_per_member` gets `reservation_limit` on every date. [D]

Given / When / Then

- `AC-api-C07` Given `ff.job.reservations` on and one date at the capacity share limit, When a member asks for a three-day range, Then three entries come back in date order, the full date has `bookable` `false` and `reason` `date_full`, the others carry `price_per_cell_ucr`, and no hold or ledger row is created; with the flag off the answer is `403 FORBIDDEN` reason `feature_disabled`.

### 15.C.4.7 Public experiments (row 18)

[D][A] S15b 15.32.2 requires a locked pre-registration before an experiment can start, and 15.33.2 already publishes locked pre-registrations. A public page can therefore list experiments that have started without disclosing anything that is not already public. No per-member arm and no cohort count appears.

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `listPublicExperiments` | `GET /v1/public/experiments` | none | - | `PUB` | 200 | - |

```
PublicExperiment { key: text<64>, hypothesis: text<500>, status: "running"/"stopped", started_on: date, stopped_on: date/null,
                   arms: [ { arm_key: text<40>, fraction_ppm: ppm } ], metrics: [ text<64> ],
                   preregistration: { id: id<prr>, content_hash: hash, locked_at: ts } }
response        Page<PublicExperiment>, as_of: ts          newest start first, filter status
```

- Only `running` and `stopped` experiments appear; `draft` experiments and the `flag_key`, `fraction_source` and arm `config` of S15b do not. `metrics` are the `measure_key` values of the experiment. `preregistration` is never null because starting requires it. [D]
- No flag gate: the page is served whenever the API is up (12.1.2 says none). Common public rules apply: no cookies, `Cache-Control: public, max-age` at most `public.counter_refresh_s`, `ETag` and `304`, `PUB` class (S15b 15.33.1). [D]
- Whether a running experiment may be disclosed before it ends is a design decision for `S13.*`; this endpoint publishes at `startExperiment`, in line with the public pre-registration. [A][V: `S13.*` owner confirms]

Given / When / Then

- `AC-api-C08` Given one `draft`, one `running` and one `stopped` experiment, When an anonymous caller lists `/v1/public/experiments`, Then two items are returned, none contains `flag_key`, `config` or any member count, and each carries the `content_hash` of its locked pre-registration; no `Set-Cookie` is sent.

### 15.C.4.8 Public teams (row 22)

[D][A] S15a 15.8 says a listed team's name and total may appear on public surfaces and S15b 15.33.1 rule 6 gates the public endpoints by flag, but no public teams endpoint exists. Part 12.9.2 decides the content: totals only, no member list, no alias in Phase 1, a place only if `public.location_display` is `opt_in`.

| op | Method and path | Auth | Idem | RL | OK | Events |
| --- | --- | --- | --- | --- | --- | --- |
| `listPublicTeams` | `GET /v1/public/teams` | none | - | `PUB` | 200 | - |

```
PublicTeam { id: id<tem>, name: text<40>, member_count: int, group_label: text<40>/null,
             score: { week_start: date, week: int, all_time: int } }
response   Page<PublicTeam>, as_of: ts          ordered by name ascending, never by score
```

- **Who is listed:** teams that are `listed` (S15a: `listed` = true, 12: `join_mode` = `listed`), `active`, and have at least `team.min_public_members` active members; a team that drops below falls out at once. The threshold in force is the larger of `team.min_public_members` and `analytics.min_cohort_k`, so a public total can never single out a small group. [D][A]
- **Score** is the accepted verified cells of the team's members inside their membership intervals: the current UTC calendar week (Monday 00:00 UTC, `week_start`) and all time (12.9.2). Cells that are later overturned lower it. Figures are lagged by `public.ledger_lag_s` like every public ledger-derived number. [D]
- **Order is by name, not by score.** A public ranking of groups is competitive pressure on members in a high-risk context and is not asked for by FD; part 12 may override with a reason. [A]
- `group_label` is present only when `public.location_display` is `opt_in` and the creator typed one; otherwise null. The platform never infers or verifies it. The `id<tem>` lets a viewer report the team (row 27); it links to no member. [D]
- With `ff.growth.v4_teams` off: `404 NOT_FOUND`. No member id, alias or per-member contribution ever appears. [D]

Given / When / Then

- `AC-api-C09` Given three teams of which one is `listed` and active with `team.min_public_members` members, one `listed` with one member fewer and one private, When an anonymous caller lists `/v1/public/teams`, Then only the first is returned, with `name`, `member_count`, `score` and no member data; with `ff.growth.v4_teams` off the answer is `404 NOT_FOUND`.

## 15.C.5 Ground-rule check [D]

| Rule | Result for this file |
| --- | --- |
| No invented provider facts (GR 1) | No provider, URL parameter, limit or price is named. `previewCells` and `getReservationAvailability` return values computed from configuration; availability copy says it is an estimate [V]. |
| No automation of a volunteer's account (GR 2) | No new operation touches a volunteer's page, credentials or session. Rows 13 and 28 close two inputs that could widen that surface (base64 binary files, free-text requester notes); row 14 keeps waitlisting a server decision, not a requester action against a provider. |
| Evidence tags and numbers (GR 3, 4) | Every decision carries a tag. The only numbers are inherited parameters (`appeal.window_days`, `reservation.max_horizon_days`, `admission.max_job_cells`, `team.min_public_members`, `analytics.min_cohort_k`, `public.ledger_lag_s`, `public.counter_refresh_s`) and the three-sample rule of `previewCells` (first, middle, last: a shape, not a tuned value). No parameter is added. |
| Declared, not guaranteed (GR 5) | `refund_estimate`, `bookable` and the appeal outcome carry copy keys that say estimate or decision; no deadline is returned for appeals. |
| Member and admin auth separated | All new member operations are `member`; the public ones are `none`; no admin route is added or reused. |
| Idempotent writes | `createAppeal`, `withdrawAppeal`, `recordExperimentExposure` have `Idempotency-Key` `R` and natural idempotency; the other new operations are reads. |
| Minimal data | See 15.C.3 rule 4; public teams and experiments show no member data, no count below the cohort threshold, no arm per member. |

## 15.C.6 Convention additions made by this file [A]

- **Operations (11):** `createAppeal`, `listAppeals`, `getAppeal`, `withdrawAppeal`, `recordExperimentExposure`, `getCancellationPreview`, `previewCells`, `getSettlementReceipt`, `getReservationAvailability`, `listPublicExperiments`, `listPublicTeams`. They are S15 operations and belong in the generated OpenAPI document and the contract tests (`BM0`).
- **Event:** `+experiment.exposed` (also `experiment.assigned`, named by part 12 and absent from the S15b catalogue).
- **`details.reason` values:** `appeal_exists` (`ALREADY_EXISTS`), `appeal_window_closed`, `not_appealable`, `appeal_decided` (`STATE_CONFLICT`), `job_incomplete` (`UNPROCESSABLE`).
- **Enum values:** `appeal_kind` as accepted by members: `submission_rejection`, `job_rejection`, `member_ban`. The enum name and the full value set must be checked against S0, which this cell did not read [V].
- **Copy keys:** `copy.api_error.<code>[.<reason>]` for the new reasons; one fixed text each for the cancellation estimate basis and the availability estimate (areas `job` and `reservation`, `S11.*`).

## 15.C.7 Open points for the whole-API consistency cell [D][A]

These are contradictions or gaps that this reconciliation exposed and that it cannot settle inside its own file. Each names the files that must change and a proposed resolution. The suggested edits in the canonical files are labeled S1 to S6.

| # | Where | Finding | Proposed resolution |
| --- | --- | --- | --- |
| O1 | S15b 15.33.5 against S15a 15.8 and part 12.8 | S15b defines per-member share-card tokens, a public `/v1/public/share-cards/{token}`, `createShareCard`, `listMyShareCards`, `revokeShareCard`, the events `sharecard.*` and the cap `growth.share_card_max_active`. S15a says the server stores no image and no share link, and 12.8.1 and 12.8.3 forbid any per-member token because it would link a pseudonym to a public post (FD Principle 8). The two cannot both stand. | Keep the no-token design of S15a and 12.8 unless the owner decides otherwise under the G1 threat model; then remove 15.33.5 and the `sharecard.*` events, or, if tokens are chosen, rewrite 12.8 and S15a `getShareCard`. Row 25 follows the no-token design. |
| O2 | S15a 15.8 against 12.9.2 | S15a has `listTeamMembers`, per-team `alias` and `visible`; 12.9.2 says a team page shows no member list and no alias in Phase 1. | Follow the stricter 12.9.2 for Phase 1: hide `listTeamMembers` and the alias fields behind the Phase 2 'full teams' flag, or state in S15a that they stay off until the G1 threat model covers them. |
| O3 | S15a `Team.verified_cells_30d` against 12.9.2 | S15a counts 30 days; 12 scores the current UTC week and all time. `listPublicTeams` follows 12. | Align the member `Team` object to `score` `{week_start, week, all_time}` or define why both exist. |
| O4 | S15b 15.29 against 12.9.1 | 12 has `team.locked`, `team.unlocked`, `team.disbanded` after reports; S15b has no admin endpoint, permission or event owner for them, so a reported team cannot be locked. | Add `lockTeam`, `unlockTeam` (single admin for lock, tightening) to S15b with `perm.report.triage` or a `perm.team.*` permission; the report outcome links to the action. |
| O5 | S15a `createReport` | `subject_kind` `result` takes an `id<sub>`, which a requester never receives (`ResultItem` has `cell_id`, no submission id). 11b screens 13 and 16 report results. | Accept `id<cel>` for `subject_kind` `result` when the caller owns the job. |
| O6 | S15a 15.7.3 `cancelJob` | The text says `refund_ucr` is visible in `getJob`; `Job` has no such field. | Point the text at `getSettlementReceipt` (this file) or add the field. |
| O7 | S15a 15.7.3 `rateJob` | `PUT` only; 11b screen 17 must show an earlier rating and no read exists. | Add `rating` to `Job` (additive) or a `GET /v1/jobs/{job_id}/rating`; 11b rows `createJobRating`, `getJobRating` use `POST` and `GET` on a path that S15 defines with `PUT`. |
| O8 | S15b 15.34.3 `appeal.overturned` | Consumers lack `job_svc`, so a `job_rejection` appeal has no effect owner; `template_rejection` is listed as a kind but members cannot file it. | Add `job_svc` as consumer and define what overturning a terminal `rejected` job does (a fast-tracked copy is the proposal); decide who files `template_rejection` for an author. |
| O9 | S15a 15.3 rule 1 | Strict requests are defined for body fields; 11b sends query parameters that S15 does not define (`listServices ?state=approved`, `getManifest ?profile=requester`). | State whether an unknown query parameter is `400 VALIDATION_FAILED` reason `unknown_field`; the edits for 11b:121 and 11b:149 below drop these two. |
| O10 | S15a `Features` against 12.11 | `flags` are booleans without arm names, yet 12.11.1 returns `a.arm_key`, and 12.11.5 says members see their own arm on a settings screen. No S15 operation shows that arm. | Check the mechanics of 12.12 for any with more than two arms or arm-specific client behavior; if any exists, add an optional `variants` map to `Features` (additive), and add a member read of own arms or drop the settings display. |
| O11 | S15b 15.21.2 and S15a 15.12 | The `RL-READ` class gives `previewCells` the cost of a cheap read although it renders text. | Decide a class in S16.* if measurement requires one. |
| O12 | `scripts/check_refs.py` | The script counts a `/v1/` path as defined if it appears anywhere in `spec/15*.md`, including the cited paths in the decision table of this file. It passes even if a REMOVE row is never applied, and it ignores methods and query strings. | After the edits below are applied, run it with this file excluded, and compare methods and queries by hand; the edits listed below include a method mismatch on a defined path (11b:150) and operation-id mismatches (11b:124, 11b:132, 11b:147, 11b:149). |
| O13 | S15a 15.13 last bullet | 'An endpoint not in a table does not exist' refers to the operation tables 'of this part'. | Say S15a, S15b and 15.C together, so the contract suite covers the eleven new operations. |
| O14 | S15a `confirmJob` | The guards do not say what a `reservation_id` must satisfy; row 24 assumes `held`, owned by the caller, not past `target_date`, and a template match. | Copy the guard into S15a 15.7.2 (S2 below). |
| O15 | Part 11d | Not read: the cell names no 11d line, but `check_refs.py` is run for it. | The cell that applies the edits searches 11d for every string in the decision table. |

**Suggested edits in canonical files** (not citing parts; for the consistency cell)

- **S1** S0 enum for report subjects and S15a 15.6.3 `createReport`: add `"team"` with `subject_id: id<tem>`; a reporter must belong to the team or see it in the public list.
- **S2** S15a 15.7.2 `confirmJob` guards: with `reservation_id`, the reservation must be `held`, the caller's, not past `target_date`, and match template and cell count, else `409 STATE_CONFLICT` reason `reservation_state_invalid`.
- **S3** S15a 15.13 and 15.1: the S15 operation tables include this file.
- **S4** S15a 15.9: append the five new `details.reason` values of 15.C.6 to their code rows.
- **S5** S15b 15.34: add `experiment.assigned` and `experiment.exposed`; add `job_svc` as consumer of `appeal.overturned`.
- **S6** S15a 15.7.3 and `Job`: refund text (O6) and rating read-back (O7).

## Edits required in citing parts

For a later cell to apply [D]. Each block is one edit: a line number in the citing part (as given, or computed from the cited anchors 11b:116, 117, 120, 137, 151, which are consistent with the row order of the table), the old text and the new text. In 11b the old text is the whole table row; the applier matches the row, not the number, if the file has moved. Operation ids in 11b are the contract between screens and S15 (11b 11.34), so op-id mismatches on already defined paths are corrected here too, although a path-only check does not see them. Rows not listed (11b:115, 118, 119, 122, 123, 126, 127, 130, 138 to 140, 142, 144, 146, 152) already match S15 or the new operations of 15.C.4.

### Part 11b, requester screens (spec/11b-requester-ux.md, table 11.34)

```
11b:116
- | `getBalance` | `GET /v1/members/me/balance` (`balance_ucr`, `cap_ucr`, `member_status`, `cooldown_ends_at`) | 01, 07, 08 |
+ | `getBalance` | `GET /v1/balance` (`balance_ucr`, `member_cap_ucr`, `headroom_ucr`, `held_ucr`); `status` and `recovery.cooldown_until` come from `getMe` `GET /v1/members/me` | 01, 07, 08 |

11b:117
- | `listCreditLots` | `GET /v1/members/me/credit-lots` (`lot_id`, `amount_ucr`, `expires_at`) | 07, 08, 15 |
+ | `listLots` | `GET /v1/balance/lots` (`id`, `amount_ucr`, `remaining_ucr`, `expires_at`; `Page`, oldest expiry first) | 07, 08, 15 |

11b:120
- | `getPolicyProfile` | `GET /v1/policy-versions/current` (allowlist, phase locks, `license_options`) | 05 |
+ | `getTemplate`, `checkJobPolicy` | `GET /v1/templates/{template_id}` field `allowed`; `POST /v1/jobs/{job_id}/policy-checks` (dry run, `policy_version_id`) | 05 |

11b:121
- | `listServices` | `GET /v1/services?state=approved` (`service_id`, display names) | 05 |
+ | `listServices` | `GET /v1/services` (approved entries only, no query) (`id`, `display_name`) | 05 |

11b:124
- | `patchJob` | `PATCH /v1/jobs/{job_id}` (JSON Merge Patch, `If-Match` = `row_version`) | 05 |
+ | `updateJob` | `PATCH /v1/jobs/{job_id}` (JSON Merge Patch, `If-Match` = `row_version`) | 05 |

11b:125
- | `createUpload` | `POST /v1/jobs/{job_id}/uploads` JSON body `{file_name, encoding, content}`; `encoding` is `utf8` or `base64`; size limit `job.max_upload_bytes` | 03 |
+ | `createUpload` | `POST /v1/uploads` JSON body `{format, filename?, content, content_hash?}`, UTF-8 text only (no base64); attached by `upload_ids` on `createJob` or `updateJob`; size limit `job.max_upload_bytes` | 03 |

11b:128
- | `requestUploadReview`+ | `POST /v1/uploads/{upload_id}/review-requests` body `{note?}` | 04 |
+ (row removed: a flagged upload goes to a human reviewer automatically after `submitJobForScreening`)

11b:129
- | `createGlossary` | `POST /v1/jobs/{job_id}/glossaries` body `{entries:[{source,target}]}` | 03 |
+ | `createGlossary` | `POST /v1/glossaries` body `{name, source_lang, target_lang, entries:[{source,target}]}`; attached by `glossary_id` on `createJob` or `updateJob` | 03 |

11b:131
- | `submitJob` | `POST /v1/jobs/{job_id}/submission` -> `202`, Job `screening` (or already `quoted` / `rejected` when screening finished synchronously) | 05 |
+ | `submitJobForScreening` | `POST /v1/jobs/{job_id}/screenings` -> `200` Job `quoted` or `waitlisted`, `202` Job `screening`, `422 POLICY_REJECTED` (job `rejected`; read `details.job_id`) | 05 |

11b:132
- | `getQuote` | `GET /v1/jobs/{job_id}/quote` | 07, 08 |
+ | `getJobQuote` | `GET /v1/jobs/{job_id}/quote` | 07, 08 |

11b:133, 11b:134, 11b:135
- | `createWaitlistEntry` | `POST /v1/jobs/{job_id}/waitlist-entries` | 07 |
- | `getWaitlistEntry` | `GET /v1/waitlist-entries/{waitlist_entry_id}` | 09 |
- | `deleteWaitlistEntry` | `DELETE /v1/waitlist-entries/{waitlist_entry_id}` | 09 |
+ (three rows removed: the waitlist is a job state, read from `getJob` field `waitlist`; leaving it is `cancelJob`)

11b:136
- | `confirmEscrow` | `POST /v1/jobs/{job_id}/escrow-confirmation` body `{quote_hash, acknowledgements:[string]}` | 08 |
+ | `confirmJob` | `POST /v1/jobs/{job_id}/confirmations` body `{quote_hash, reservation_id?}` (acknowledgements are declared earlier, in `Declarations`) | 08, 11 |

11b:137
- | `getReservationAvailability`+ | `GET /v1/reservations/availability?from=&to=&cells=&job_type=` | 10 |
+ | `getReservationAvailability`+ | `GET /v1/reservations/availability?from=&to=&template_id=&cells=` (`bookable`, `reason`, `price_per_cell_ucr`; an estimate, not a hold) | 10 |

11b:141
- | `activateReservation` | `POST /v1/reservations/{reservation_id}/activation` body `{job_id}` | 11 |
+ (row removed: `confirmJob` with `reservation_id` activates the reservation)

11b:143
- | `listJobCells` / `getJobCell` | `GET /v1/jobs/{job_id}/cells`, `GET /v1/jobs/{job_id}/cells/{cell_id}` (primary cells only) | 13 |
+ | `listJobCells` | `GET /v1/jobs/{job_id}/cells` (primary cells only; outputs by `ordinal` from `listJobResults`) | 13 |

11b:145
- | `cancelJob` | `POST /v1/jobs/{job_id}/cancellation` | 14 |
+ | `cancelJob` | `POST /v1/jobs/{job_id}/cancellation` | 09, 14 |

11b:147
- | `getDeliverable` | `GET /v1/jobs/{job_id}/deliverable` | 16 |
+ | `getJobDeliverable` | `GET /v1/jobs/{job_id}/deliverable` | 16 |

11b:148
- | `downloadDeliverableFile` | `GET /v1/deliverables/{deliverable_id}/files/{file_name}` (bytes via `fetch` with the Bearer header; no query-string secrets, S0.11.1) | 16 |
+ | `getJobDeliverableContent` | `GET /v1/jobs/{job_id}/deliverable/content` (JSON `{media_type, encoding, content, content_hash}`; the client saves it as a file; Bearer header, no query-string secrets, S0.11.1) | 16 |

11b:149
- | `getManifest` | `GET /v1/jobs/{job_id}/manifest?profile=requester` | 16 |
+ | `getJobManifest` | `GET /v1/jobs/{job_id}/manifest` | 16 |

11b:150
- | `createJobRating`+ / `getJobRating`+ | `POST` and `GET /v1/jobs/{job_id}/rating` | 17 |
+ | `rateJob` | `PUT /v1/jobs/{job_id}/rating` (replaces an earlier rating; no read exists yet, 15.C.7 O7) | 17 |

11b:151
- | `createAppeal` / `getAppeal` | `POST /v1/appeals` with `appeal_kind` = `job_rejection`; `GET /v1/appeals/{appeal_id}` | 18 |
+ | `createAppeal`+ / `getAppeal`+ | `POST /v1/appeals` with `kind` = `job_rejection` and `subject_id` = the job id; `GET /v1/appeals/{appeal_id}` | 18 |
```

Prose in 11b that depends on the removed or changed rows (screen sections 03, 04, 07, 09, 11, 13, 16; line numbers not given to this cell) is changed to match [A]:

- Screen 04 (flagged upload): no 'ask for review' button and no note field. It lists the finding codes and counts and offers 'delete upload' or 'submit for screening' (a flagged upload then waits for a human).
- Screen 07 (quote when admission says `waitlist`): no 'join waitlist' button. The job is already `waitlisted` when the screening answer arrives; the screen shows `waitlist.position` and `waitlist.expires_at`.
- Screen 09 (waitlist): reads `getJob`; the 'leave' action is `cancelJob` and says that the job ends (copy from it with `copy_from_job_id` to try again).
- Screen 11 (reservation): 'use this reservation' is the choice of the reservation on the confirm screen (`confirmJob` with `reservation_id`).
- Screen 13 (per-cell map): a cell detail panel uses the list item and `listJobResults`.
- Screen 16 (results): the 'download' control saves the `content` string of `getJobDeliverableContent` under a client-built file name.

### Part 12, public surfaces and growth (spec/12-public-growth.md)

```
12:29
- | Public ledger | `listPublicLedgerCheckpoints`, `getPublicLedgerCheckpoint`, `listPublicLedgerFlows`: `GET /v1/public/ledger-checkpoints`, `GET /v1/public/ledger-checkpoints/{checkpoint_date}`, `GET /v1/public/ledger-flows` | `none` | `ff.public.ledger_page` | `public.counter_refresh_s` (a checkpoint by date is immutable: `ledger.checkpoint_interval_s`) | `SCR-pub-02` |
+ | Public ledger | `listPublicLedgerCheckpoints` (one date: `from` = `to`), `listPublicLedgerDaily`: `GET /v1/public/ledger/checkpoints`, `GET /v1/public/ledger/daily` | `none` | `ff.public.ledger_page` | `public.counter_refresh_s` | `SCR-pub-02` |

12:35
- | Share card payload | `getShareCardPayload` `GET /v1/share-cards/preview` | `member` | `ff.growth.v3_share_card` | `no-store` | in-app, `S11.*` |
+ | Share card payload | `getShareCard` `GET /v1/members/me/share-card` | `member` | `ff.growth.v3_share_card` | `no-store` | in-app, `S11.*` |

12:38
- | Flags and exposure | `listEffectiveFlags` `GET /v1/flags`, `recordExperimentExposure` `POST /v1/experiment-exposures` | `member` | none | `no-store` | none |
+ | Flags and exposure | `getFeatures` `GET /v1/members/me/features`, `recordExperimentExposure` `POST /v1/experiment-exposures` | `member` | none | `no-store` | none |

12:466
- `ineligible_behavior` is `off` for a new feature and `on` for a feature already shipped; it is fixed at lock. `GET /v1/flags` returns the member's effective variants and is the only place assignment is created (lazily, on first evaluation after the experiment is `running`).
+ `ineligible_behavior` is `off` for a new feature and `on` for a feature already shipped; it is fixed at lock. `GET /v1/members/me/features` (`getFeatures`) returns the member's effective flags as booleans, with no arm names, and is the only place assignment is created (lazily, on first evaluation after the experiment is `running`).

12:511
- - The client reports exposure with `POST /v1/experiment-exposures` (`assignment_id`, `surface_key`, `Idempotency-Key`); a server-side effect (for example an invitation created with a bonus) emits it from the server.
+ - The client reports exposure with `POST /v1/experiment-exposures` (`surface_key`, `Idempotency-Key`; the server finds the member's own assignment and answers `204` whether or not an experiment applies); a server-side effect (for example an invitation created with a bonus) emits it from the server.

12.9.2 table (line not given to this cell; match the row text)
- | `leaveTeam` | `DELETE /v1/team-memberships/{membership_id}` (sets `left_at`; the row stays) | required |
+ | `leaveTeam` | `DELETE /v1/teams/{team_id}/memberships/me` (sets `left_at`; the row stays) | optional, honored if sent |

12.9.2 table (line not given to this cell; match the row text)
- | `reportTeam` | `POST /v1/teams/{team_id}/reports` | required |
+ | `reportTeam` | `POST /v1/reports` with `subject_kind` = `team`, `subject_id` = the team id | required |
```

No edit is needed at 12:33 (`/v1/public/teams`) and 12:34 (`/v1/public/experiments`): the rows already match the operations defined in 15.C.4.7 and 15.C.4.8 [D]. The share-card text of 12.8.2 stays as it is, because it is the design that S15a follows (15.C.7 O1).
