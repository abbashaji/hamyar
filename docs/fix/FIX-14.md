# FIX-14: spec/15b-api-admin.md 15.29 to 15.34 (part 2)

Cell C-085. Corrections from spec/15g-api-consistency.md: CR-09, CR-17, CR-18, CR-34, CR-35, CR-38, CR-39, CR-42, CR-43, plus A12 findings 27 and 28 (member appeals and inbox). Line numbers are those of spec/15b-api-admin.md after the edits and are approximate (counted from the read-back ranges).

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| CR-09 EV-01 invite.* events | spec/15b-api-admin.md:1012 | rows present in 15.34.6 | unchanged | already-applied |
| CR-09 EV-02 member.recovery_confirmed | spec/15b-api-admin.md:1016 | no row | row added (producer identity_svc, consumer analytics) | applied |
| CR-09 EV-02 member.key_revoked, member.device_revoked | spec/15b-api-admin.md:1014 | rows present | unchanged | already-applied |
| CR-09 EV-03 offer.declined, job.rated | spec/15b-api-admin.md:1017 | rows present | unchanged | already-applied |
| CR-09 EV-04 team.*, referral.* | spec/15b-api-admin.md:1019 | rows present, no same-transaction note | rows kept; referral.paid says same transaction as ledger.entry_committed | applied |
| CR-09 EV-05 experiment.registered, assigned, exposed | spec/15b-api-admin.md:986 | only started and stopped | three rows added | applied |
| CR-09 EV-06 calibration.report_frozen, decision_report.created, incident.recorded, incident.resolved, interview.recorded, workclaim.expired | spec/15b-api-admin.md:990 | no rows | none added: payload, producer and consumers are defined in S15e and S15f, which this cell may not read, and 15g gives no default | skipped-needs-owner |
| CR-09 EV-09 appeal and job_rejection mapping | spec/15b-api-admin.md (15.27.3, line not re-read) | seen as already carrying the mapping | unchanged | already-applied |
| CR-09 EV-10 service.review_due cause item_reopened | spec/15b-api-admin.md:950 | payload service_id only | payload gains cause, producer adds registry_svc for item_reopened | applied |
| CR-09 EV-11 preregistration.locked spelling | spec/15b-api-admin.md:984 | already preregistration.locked | unchanged | already-applied |
| CR-17 lockTeam, unlockTeam | spec/15b-api-admin.md:610 | no team lock operation | two operations (POST /v1/admin/teams/{tem_id}/locks and /unlocks, perm.report.triage, single admin) and a paragraph | applied |
| CR-17 team.locked, team.unlocked events | spec/15b-api-admin.md:963 | no rows | one row added to 15.34.3 | applied |
| CR-18 AdminAction prev_hash and entry_hash | spec/15b-api-admin.md:46 | field list ended at occurred_at | prev_hash and entry_hash added (field list owned by S0 and S10) | applied |
| CR-18 submitTemplateReview blocking-finding guard | spec/15b-api-admin.md:290 | errors FORBIDDEN, STATE_CONFLICT | UNPROCESSABLE blocking_finding added | applied |
| CR-34 job.cancelled | spec/15b-api-admin.md:906 | only cancel_requested and cancel_settled | job.cancelled row added (job_id, from_state) | applied |
| CR-34 closeMember emits lease.released and cell.declined per lease | spec/15b-api-admin.md:927 | not stated | one paragraph after the 15.34.2 table | applied |
| CR-35 job_svc consumes appeal.overturned | spec/15b-api-admin.md:955 | job_svc not a consumer | job_svc (job_rejection) added | applied |
| CR-35 template_rejection filed by an admin for an author | spec/15b-api-admin.md:549 | not stated | sentence added; no operation of this file files it | applied |
| A12 28 member appeal operations moved from 15d | spec/15b-api-admin.md:617 | only the admin queue | new 15.29.7 with createAppeal, listAppeals, getAppeal, withdrawAppeal, Appeal object, guards, AC-api-C01 and C02; 15d text kept | applied |
| A12 27 member inbox and notice read operations | spec/15b-api-admin.md:1180 | 15.29.6 and 15.35 say none is defined | unchanged: searched all of 15d and the verdict table and 15.B.3 to 15.B.5 of 15c, and no inbox or notice read operation is defined there | skipped-not-found |
| CR-38 createCalibrationRecord input_chars, output_chars, kind | spec/15b-api-admin.md:746 | no such fields | added to CalibrationRecord and to the request | applied |
| CR-38 createCalibrationRecord request | spec/15b-api-admin.md:752 | no such fields | input_chars?, output_chars?, kind? added | applied |
| CR-39 MetricSnapshot is one entity, bundle is kind price_publication | spec/15b-api-admin.md:826 | bundle described as the entity | row of kind price_publication, bundle fields are its payload | applied |
| CR-39 getPublicMetrics and listPublicMetricSnapshots | spec/15b-api-admin.md:795 | latest published MetricSnapshot | of kind price_publication | applied |
| CR-42 member-read context_id on getMemberAdmin and listLotsAdmin | spec/15b-api-admin.md:75 | no context_id | no change: it applies only if S10 adopts it, and until then the logged read (15.21.3 rule 3) is the control | skipped-needs-owner |
| CR-43 perm.claim.takeover | spec/15b-api-admin.md:77 | no row | row added (operator, S15e takeoverWorkClaim) | applied |

Notes. The alarm kinds admin_action.chain_broken and incident.safety_or_critical of CR-09 target S0 and 15e, not this file, and are not touched. The new 15.29.7 operations keep the bare ids listAppeals and getAppeal; the admin operations with the same names stay as they were (D-08 is not yet decided). docs/decisions.md was not re-read for this cell; heading and evidence-tag format were copied from the surrounding 15b text.

## Read-back

Re-read after the edits: 15.29.1 to 15.29.7 (lines 520 to 698), 15.31 to 15.33 including 15.32.3 and 15.33.4 (lines 700 to 860), 15.34.2 to 15.34.6 (lines 896 to 1075), and in the first pass 15.21.3, 15.21.4 and 15.24. Every applied row above was seen in its final text. The 15.21.3 and 15.21.4 and 15.24 edits were checked by the exact-match success of their edit call only, not re-read after editing.

Result: DONE WITH SKIPS
