# FIX-06: API reconciliation applied to 07, 06b, 04, 05b, 09

*Cell C-077. Source: `spec/15c-api-reconcile-core.md`, section `## Edits required in citing parts`, edits 15 to 18, 20, 22 to 24 and 27, plus the ALIAS and REMOVE verdict rows for every path cited in the five files. Decisions: `docs/audit/FINAL.md` section 4. No owner decision D-01..D-22 is needed by any applied edit, so no row is marked default-pending. Nothing was executed; CI runs the acceptance scripts.*

## Edits

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| 15 | spec/07-policy.md:1067 (cited 1065) | `getOptIns`, `setOptIns`, `PUT /v1/me/opt-ins` | `getOptIns`, `replaceOptIns`, `PUT /v1/members/me/opt-ins` | applied |
| 16 | spec/07-policy.md:1064 (cited 1062) | `previewPolicy`, `POST /v1/policy-previews`, dry run returning the first failing rule | `checkJobPolicy`, `POST /v1/jobs/{job_id}/policy-checks`, dry run on a `draft` job returning every failing rule | applied |
| 17 | spec/07-policy.md:1072 (cited 1070) | `getSupplyGauge`, `GET /v1/admin/supply-gauge`, exact counts | `listSupplyGauges`, `GET /v1/admin/capacity/supply-gauges`, buckets under `analytics.min_cohort_k` suppressed (`null`), public view `GET /v1/public/capacity` | applied |
| 18 | spec/06b-admission.md:543 (cited 523) | `confirmJobQuote`, `POST /v1/jobs/{job_id}/confirmation`, body `{quote_seq}` | `confirmJob`, `POST /v1/jobs/{job_id}/confirmations`, body `{quote_hash, reservation_id?}` | applied |
| 20 | spec/07-policy.md:1065 (cited 1063) | `getCurrentPolicy`, `GET /v1/policy`, auth public | `getPublicPolicy`, `GET /v1/public/policy`, auth none | applied |
| 22 | spec/06b-admission.md:175 (cited 173) | small category shows the string `<k` for both counts | shows `null` with `suppressed: true` for both counts, with the bucket rule of S15.B.8.2 | applied |
| 23 | spec/06b-admission.md:544 (cited 524) | purpose: re-quote while `quoted` or after a release; errors without `409` and `POLICY_REJECTED` | purpose: re-quote while `quoted`, a waitlist release is re-quoted by the system; errors add `409 STATE_CONFLICT`, `422 CAP_EXCEEDED` (`waitlist_limit`), `422 POLICY_REJECTED` | applied |
| 24 | spec/04-architecture.md:607 (cited 583) | detailed readiness is an admin operation (S15.*) | detailed readiness is read from `getLedgerHead`, `getCapacitySnapshot` and `listAlarms` (S15b); no separate readiness endpoint | applied |
| 27a | spec/05b-state-machines.md:197 | `POST /v1/leases/{lease_id}/extension` | `POST /v1/leases/{lease_id}/extensions` | applied |
| 27b | spec/09-result-return.md:81 | `POST /v1/leases/{lease_id}/nonce-rotations` | `POST /v1/leases/{lease_id}/nonces` | applied |
| 27c | spec/09-result-return.md:174 (9.5.4) | `POST /v1/leases/{lease_id}/validations`, operation `validateSubmission` | unchanged | skipped-needs-owner |
| 27d | all five files | `/v1/admin/actions/{act_id}/approvals` | not present | skipped-not-found |

## Read-back

Every edited place was read again after the commits.

- 07:1064 reads `checkJobPolicy` with `POST /v1/jobs/{job_id}/policy-checks`, auth member, note ending "every failing rule".
- 07:1065 reads `getPublicPolicy` with `GET /v1/public/policy`, auth `none`.
- 07:1067 reads `getOptIns`, `replaceOptIns` with `GET`, `PUT /v1/members/me/opt-ins`.
- 07:1072 reads `listSupplyGauges` with `GET /v1/admin/capacity/supply-gauges`; the public view points to `GET /v1/public/capacity`.
- 06b:175 reads "`null` with `suppressed: true` for both counts" followed by the S15.B.8.2 bucket remark.
- 06b:543 reads `confirmJob` with `POST /v1/jobs/{job_id}/confirmations` and body `{quote_hash, reservation_id?}`.
- 06b:544 reads `requestJobQuote` with purpose "Re-quote while `quoted`" and the errors `409 STATE_CONFLICT`, `422 CAP_EXCEEDED` (`waitlist_limit`), `422 POLICY_REJECTED`, `403 LAUNCH_GATE_CLOSED`, `503 KILL_SWITCH_ENGAGED`.
- 04:607 reads "no separate readiness endpoint" after the three S15b operation names.
- 05b:197 reads `POST /v1/leases/{lease_id}/extensions`.
- 09:81 reads `POST /v1/leases/{lease_id}/nonces`, operation id still `rotateLeaseNonce`.
- 09:174 still reads `/validations` (not edited, see Notes).

## Notes

**Search scope.** Every line of `07-policy.md` (1 to 1091), `04-architecture.md` (1 to 970), `05b-state-machines.md` (1 to 818), `09-result-return.md` (1 to 830) and `06b-admission.md` (1 to 641) was read and searched for `/v1/` paths and the words extension, nonce-rotations, validations and approvals. Drift of the cited lines: 07 +2, 06b +2 for line 173 and +19 or +20 for lines 523 and 524, 04 +24; all inside the 60-line limit.

**27c, `/validations`.** 15c marks the path REMOVE, but its own text says no citing line was found and the intent was inferred. 09 does cite it: 9.5.4 defines `validateSubmission` as a dry run, and the capability is also wired into the `Lease.validations` counter, the parameter `lease.max_validations` (9.6, 9.18, constraint `S9-C3`), `AC-submit-16` and `ISS-94`. Removing the call means deleting that content and a parameter, which this cell forbids, and no decision in FINAL section 4 covers it. 15c argues the dry run would give an evasion oracle and break `AC-api-08`, while 09 argues the opposite for the syntactic checks only. The owner of 09 and S15 should decide between dropping 9.5.4 (client checks against the work order, `getLease` for liveness) and adding a validation operation to S15.

**27d, admin approvals.** No file of the five cites `/v1/admin/actions/{act_id}/approvals`; nothing to change.

**Paths cited that have no row in the 15c verdict table (not edited, no authority to change them).** `POST /v1/cells/{id}/leases` (05b, 09:68 as `{cell_id}`), `POST /v1/leases/{id}/submission` (05b, 09:141 as `{lease_id}`), `POST /v1/jobs` in 07 7.9 (`E1`). The audit did not map them to S15 operations. Also the operation ids `rotateLeaseNonce` (09) and `submitResult` stay as written; S15 calls the first one `issueLeaseNonce`.

**Leftovers of the same defect, not covered by the cited text.** 06b `AC-admission-15` (about line 590) still says the small category shows the string `<k`, which now contradicts 06b:175; 06b still uses `quote_seq` for the quote identity in the idempotency note near 6.34.1 and in the quote document, while `confirmJob` now takes `quote_hash`. 07 text outside 7.15.4 that mentions `previewPolicy` or `setOptIns` by name, if any, was not edited. A later cell should align these.

Result: DONE WITH SKIPS
