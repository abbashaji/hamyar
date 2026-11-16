# FIX-07: API reconciliation applied to the requester screens (11b)

Cell C-078. Sources: `## Edits required in citing parts` of `spec/15d-api-reconcile-requester-growth.md` (read from its start to its end), edit 21 of `spec/15c-api-reconcile-core.md`, and the verdict rows of 15d 15.C.2 for the paths cited in 11b. Target: `spec/11b-requester-ux.md`. Nothing was executed; CI runs the acceptance scripts. Lines are those of the file before the edits (the table rows had not drifted); lines marked ~ are approximate.

## Edits

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| 15d 11b:116 | spec/11b-requester-ux.md:116 | `GET /v1/members/me/balance`, `cap_ucr`, `member_status` | `getBalance` `GET /v1/balance`, `member_cap_ucr`, `held_ucr`; status from `getMe` | applied |
| 15d 11b:117 | spec/11b-requester-ux.md:117 | `listCreditLots`, `lot_id` | `listLots` `GET /v1/balance/lots`, `id`, `remaining_ucr` | applied |
| 15c-21 and 15d 11b:120 (row 17) | spec/11b-requester-ux.md:120 | `getPolicyProfile` `GET /v1/policy-versions/current` | `getPublicPolicy` `GET /v1/public/policy` (15c edit 21 text) | applied |
| 15d row 17 composite (`getTemplate` + `checkJobPolicy`) | spec/11b-requester-ux.md:120 | n/a | not applied: it contradicts 15c edit 21 for the same row; FINAL.md 3.3 (15g CR-14) says use `getPublicPolicy` | skipped-needs-owner |
| 15d 11b:121 | spec/11b-requester-ux.md:121 | `GET /v1/services?state=approved` | `GET /v1/services`, no query, `id`, `display_name` | applied |
| 15d 11b:124 | spec/11b-requester-ux.md:124 | `patchJob` | `updateJob` (same method and path) | applied |
| 15d 11b:125 | spec/11b-requester-ux.md:125 | `POST /v1/jobs/{job_id}/uploads`, `file_name`, `encoding` utf8 or base64, derived body limit (ISS-114) | `POST /v1/uploads`, `{format, filename?, content, content_hash?}`, UTF-8 only, `upload_ids`; the base64 body-limit sentence goes with it | applied |
| 15d 11b:128 | spec/11b-requester-ux.md:128 | `requestUploadReview`+ row | row removed | applied |
| 15d 11b:129 | spec/11b-requester-ux.md:129 | `POST /v1/jobs/{job_id}/glossaries` | `POST /v1/glossaries`, `name`, `source_lang`, `target_lang`, `glossary_id` | applied |
| 15d 11b:131 | spec/11b-requester-ux.md:131 | `submitJob` `POST .../submission` | `submitJobForScreening` `POST .../screenings`, `200`/`202`/`422 POLICY_REJECTED` | applied |
| 15d 11b:132 | spec/11b-requester-ux.md:132 | `getQuote` | `getJobQuote` | applied |
| 15d 11b:133 | spec/11b-requester-ux.md:133 | `createWaitlistEntry` row | row removed | applied |
| 15d 11b:134 | spec/11b-requester-ux.md:134 | `getWaitlistEntry` row | row removed | applied |
| 15d 11b:135 | spec/11b-requester-ux.md:135 | `deleteWaitlistEntry` row | row removed | applied |
| 15d 11b:136 | spec/11b-requester-ux.md:136 | `confirmEscrow` `.../escrow-confirmation`, `acknowledgements` | `confirmJob` `.../confirmations`, `{quote_hash, reservation_id?}`, used by 08, 11 | applied |
| 15d 11b:137 | spec/11b-requester-ux.md:137 | `...&job_type=` | `...&template_id=&cells=`, `bookable`, `reason`, estimate not a hold | applied |
| 15d 11b:141 | spec/11b-requester-ux.md:141 | `activateReservation` row | row removed | applied |
| 15d 11b:143 | spec/11b-requester-ux.md:143 | `listJobCells` / `getJobCell` | `listJobCells` only | applied |
| 15d 11b:145 | spec/11b-requester-ux.md:145 | `cancelJob` used by 14 | used by 09, 14 | applied |
| 15d 11b:147 | spec/11b-requester-ux.md:147 | `getDeliverable` | `getJobDeliverable` | applied |
| 15d 11b:148 | spec/11b-requester-ux.md:148 | `downloadDeliverableFile` `/v1/deliverables/{deliverable_id}/files/{file_name}` | `getJobDeliverableContent` `GET /v1/jobs/{job_id}/deliverable/content`, JSON | applied |
| 15d 11b:149 | spec/11b-requester-ux.md:149 | `getManifest` `...?profile=requester` | `getJobManifest` `GET /v1/jobs/{job_id}/manifest` | applied |
| 15d 11b:150 | spec/11b-requester-ux.md:150 | `createJobRating` / `getJobRating` `POST`, `GET` | `rateJob` `PUT` | applied |
| 15d 11b:151 | spec/11b-requester-ux.md:151 | `appeal_kind` | `kind` and `subject_id` = the job id | applied |
| Prose screen 04 (purpose, actions) | spec/11b-requester-ux.md:~315, ~327 | ask a reviewer, `requestUploadReview`, note | no review button and no note; delete upload or submit for screening | applied |
| Prose screen 07 (states, actions) | spec/11b-requester-ux.md:~372, ~376 | Join waitlist, `createWaitlistEntry`, `getQuote` | no join button; job already `waitlisted`, shows `waitlist.position`; `getJobQuote` | applied |
| Prose screen 09 (actions) | spec/11b-requester-ux.md:~425 | `getWaitlistEntry`, `deleteWaitlistEntry` | `getJob` field `waitlist`; leave is `cancelJob` | applied |
| Prose screen 11 (actions) | spec/11b-requester-ux.md:~455 | `activateReservation`, `confirmEscrow`, `createJob` with `reservation_id` | `confirmJob` with `reservation_id` chosen on the confirm screen | applied |
| Prose screen 08 (actions) | spec/11b-requester-ux.md:~395 | `confirmEscrow` `{quote_hash, acknowledgements}` | `confirmJob` `{quote_hash, reservation_id?}`; ticks client-side only | applied |
| Prose screen 13 (actions) | spec/11b-requester-ux.md:~565 | `getJobCell` | `listJobCells` list item | applied |
| Prose screen 13, outputs from `listJobResults` | spec/11b-requester-ux.md:~565 | n/a | not applied: the sheet shows no output (RD-10), and `JobCell` has no attempt list | skipped-needs-owner |
| Prose screen 16 (blocks, actions) | spec/11b-requester-ux.md:~640 | `getDeliverable`, `downloadDeliverableFile`, `Blob`, `getManifest` | `getJobDeliverable`, `getJobDeliverableContent` saved from `content`, `getJobManifest` | applied |
| Consequent renames: screens 01, 03, 05, 10, 17, 18, 11.33.2, 11.34.1 comments, RD-03, 11.31, AC-req-19, 57, 64, 75, 76 | spec/11b-requester-ux.md:~30-1000 | `getPolicyProfile`, `listCreditLots`, `cap_ucr`, `member_status`, `patchJob`, `submitJob`, `createJobRating`, `appeal_kind`, `job_type`, base64 | `getPublicPolicy`, `listLots`, `member_cap_ucr`, `status` from `getMe`, `updateJob`, `submitJobForScreening`, `rateJob`, `kind`, `template_id`, UTF-8 only | applied |
| AC-req-14 (`requestUploadReview` daily limit) | spec/11b-requester-ux.md:~340 | n/a | not edited: the operation is removed; the AC and the parameter `screen.requester_review_requests_per_day` (11.49) now have no operation | skipped-needs-owner |
| AC-req-25, AC-req-33 (join waitlist, `waitlist_entries` cap) | spec/11b-requester-ux.md:~385, ~430 | n/a | not edited: the requester no longer joins; where the cap is answered (15c edit 23, `waitlist_limit`) is not in the authorized list | skipped-needs-owner |
| AC-req-38 (`activateReservation`, `reservation_cells`) | spec/11b-requester-ux.md:~470 | n/a | not edited: 15d row 24 gives `409 reservation_state_invalid`, not `CAP_EXCEEDED` (15.C.7 O14) | skipped-needs-owner |
| AC-req-58 (`409 ALREADY_EXISTS` on a second rating) | spec/11b-requester-ux.md:~690 | n/a | not edited: `rateJob` is `PUT` and replaces | skipped-needs-owner |
| States `submit_refused` of screen 05 and AC-req-75 (Job stays `draft` after `422`) | spec/11b-requester-ux.md:~340, ~1010 | n/a | operation renamed only: 15d row 12 says the job is `rejected` and the screen reads `details.job_id`; the state design needs a decision | skipped-needs-owner |

No edit used a default of FINAL.md section 4, so no edit is marked as resting on a default.

## Read-back

Re-read after the edits (table lines 113 to 147 of the 1071-line file, and screens 01, 03 and the purpose row of screen 04):

- Balance and lots rows: `getBalance` shows `GET /v1/balance` with `member_cap_ucr`; `listLots` shows `GET /v1/balance/lots`.
- Policy row: `getPublicPolicy` shows `GET /v1/public/policy`; no `policy-versions` path remains in the table.
- Services, `updateJob`, `createUpload` (`POST /v1/uploads`, no base64), `createGlossary` (`POST /v1/glossaries`) rows read as in the table above.
- Rows 128, 133 to 135 and 141 are gone; the table has 34 operation rows and no `waitlist-entries`, `review-requests`, `escrow-confirmation` or `activation` path.
- `submitJobForScreening` shows `.../screenings` with the `422` case; `confirmJob` shows `.../confirmations` used by 08 and 11; availability shows `template_id`.
- `listJobCells` alone; `cancelJob` used by 09, 14; `getJobDeliverable`, `getJobDeliverableContent`, `getJobManifest`, `rateJob` (`PUT`) and the appeals row with `kind` read as in the table above.
- Screen 01 now names `listLots` and `member_cap_ucr`; screen 03 Actions now says "UTF-8 text only"; screen 04 purpose now ends with submitting for screening.

Not re-read in this cell (the tool replied ok, every old text matched exactly once, but the lines were not read back): the prose edits of screens 04 actions, 05, 07, 08, 09, 10, 11, 13, 16, 17, 18, RD-03, 11.31, 11.33.2, 11.34.1 and the four AC renames. A reader should confirm them.

Not touched, outside the authorized edits: 11.49 (`createJob` accepts `reservation_id`; `appeal_kind` list), the upload and deliverable response shapes of 11.34.1 (`file_name`, `files[]`), and the appeal state labels of screen 18.

Result: DONE WITH SKIPS
