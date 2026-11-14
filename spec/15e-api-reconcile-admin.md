# 15.D API reconciliation (admin tools)

*Spec part 15e · owner cell C-039 · audit and reconcile of the `/v1/admin/*` paths that part 11c (Reviewer and operator tools) and part 13 cite but S15 (15a, 15b) does not define. S15 is canonical: where a cited path means something S15 already defines, the citing part changes, not S15. Nothing here is legal advice and nothing has been verified against any provider's terms or any law [V]. No ID, parameter, endpoint or state of S0 or S15 is renamed by this file; new operations are additions in the table format of 15.21.1.*

## 15.D.1 Method and result [D]

For each cited path the surrounding 12 lines of the citing part were read to learn what the screen or process needs, then the S15 endpoint tables (15.22 to 15.33) were searched for the nearest endpoint. Three outcomes:

- **ALIAS**: the cited path means an existing S15 endpoint. The row says which and what differs (15.D.3). The citing part is corrected (Edits required, last section).
- **NEW**: S15 has no such capability and the capability is legitimate. It is defined in full in 15.D.4 in the S15 table format.
- **REMOVE**: the cited use must not exist (15.D.5), with what the citing part does instead.

Result for the 38 cited paths: 23 ALIAS, 13 NEW, 1 REMOVE, and 1 split (`audit-queue-items`: audits are ALIAS, quarantine is NEW, `gold-views` is REMOVE). Four sub-decisions inside ALIAS rows are also removals (the bulk sign-off, the transaction list, non-public change-log entries, `requeue_at_front`); they are named in 15.D.5. This file adds 20 operations to S15; every one is an admin-surface operation and none touches the member or public surface [D].

| # | Cited path | Cited at | Decision | Resolves to |
| --- | --- | --- | --- | --- |
| 1 | `/v1/admin/abuse-items` | 11c:456 | ALIAS | `listReports`, `getReport`, `triageReport`, `closeReport`; `listAlarms` (`category=abuse`), `acknowledgeAlarm` |
| 2 | `/v1/admin/action-previews` | 11c:205 | NEW | `previewAdminAction` |
| 3 | `/v1/admin/admin-action-verifications` | 11c:210 | NEW | `startAdminActionVerification` |
| 4 | `/v1/admin/admin-actions` | 11c:209 | ALIAS | `listAdminActions`, `getAdminAction` at `/v1/admin/actions` |
| 5 | `/v1/admin/approval-requests` | 11c:206, 11c:207 | ALIAS | `listApprovals`, `getApproval` at `/v1/admin/approvals` |
| 6 | `/v1/admin/approval-requests/{}/approvals` | 11c:207 | ALIAS | `approveApproval` |
| 7 | `/v1/admin/audit-queue-items` | 11c:365 | split | audits: `listAudits`, `getAudit`, `getAuditContent`, `resolveAudit`; quarantine: NEW `listQuarantinedSubmissions` and three more; gold view: REMOVE |
| 8 | `/v1/admin/bottleneck` | 11c:615 | NEW | `getBottleneck` |
| 9 | `/v1/admin/capacity-dashboard` | 11c:615 | ALIAS (+ NEW companion) | `getCapacitySnapshot`, `listCapacityDays`, `listSupplyGauges`; companion `getOperationsSnapshot` |
| 10 | `/v1/admin/cell-overturns` | 11c:461 | NEW | `overturnCells` |
| 11 | `/v1/admin/cells/{}/voidings` | 11c:460 | NEW | `voidCell` |
| 12 | `/v1/admin/change-log-entries` | 11c:557 | ALIAS | `listPublicChangeLog` (reads); `annotateChangeLog` (writes) at `/v1/admin/changelog-entries` |
| 13 | `/v1/admin/handle-resolutions` | 11c:752 | REMOVE | none |
| 14 | `/v1/admin/invariant-checks` | 11c:506 | ALIAS | `listInvariants`, `listInvariantChecks` |
| 15 | `/v1/admin/jobs/{}/stop-requests` | 11c:459 | NEW | `stopJob` |
| 16 | `/v1/admin/kill-switch-engagements` | 11c:700 | ALIAS | `engageKillSwitch` |
| 17 | `/v1/admin/kill-switch-releases` | 11c:701 | ALIAS | `releaseKillSwitch` |
| 18 | `/v1/admin/launch-gate-items/{}` | 11c:648 | ALIAS | `getLaunchGateItem` |
| 19 | `/v1/admin/launch-gate-items/{}/evidence` | 11c:648 | ALIAS | `attachGateEvidence` |
| 20 | `/v1/admin/launch-gates` | 11c:647 | ALIAS | `listLaunchGates`, `getLaunchGate` |
| 21 | `/v1/admin/launch-signoffs` | 11c:650 | ALIAS (bulk part removed) | `signOffGateItem` per item; `changeLaunchSwitch` for the switch |
| 22 | `/v1/admin/launch-status` | 11c:652 | ALIAS | `getLaunchStatus` |
| 23 | `/v1/admin/launch-switch-offs` | 11c:651 | ALIAS | `changeLaunchSwitch` with `value = false` |
| 24 | `/v1/admin/leases` | 11c:800, 11c:801 | NEW | `listLeases` |
| 25 | `/v1/admin/leases/{}/releases` | 11c:801 | NEW | `releaseLease` |
| 26 | `/v1/admin/ledger-accounts` | 11c:502, 11c:505 | ALIAS | `listLedgerAccounts`, `getLedgerAccount` |
| 27 | `/v1/admin/ledger-accounts/{}/credit-lots` | 11c:505 | ALIAS | `listLots` |
| 28 | `/v1/admin/ledger-checkpoints` | 11c:508 | ALIAS | `listLedgerCheckpoints` |
| 29 | `/v1/admin/ledger-entries` | 11c:503 | ALIAS | `listLedgerEntries`, `getLedgerEntry` |
| 30 | `/v1/admin/ledger-reversals` | 11c:509 | ALIAS | `reverseLedgerEntry` |
| 31 | `/v1/admin/ledger-transactions` | 11c:504 | ALIAS (list removed) | `getLedgerTransaction`; list is `listLedgerEntries?txn_kind=` |
| 32 | `/v1/admin/ledger-verifications` | 11c:507 | ALIAS | `startHashChainVerification`, `runInvariant` |
| 33 | `/v1/admin/member-views` | 11c:751 | ALIAS | `getMemberAdmin` |
| 34 | `/v1/admin/metric-snapshots` | 11c:615, 13:51, 13:921 | NEW | `listAdminMetricSnapshots` |
| 35 | `/v1/admin/parameter-change-sets` | 11c:555 | NEW | `createParameterChangeSet` |
| 36 | `/v1/admin/template-versions/{}/check-runs` | 11c:266 | NEW | `runTemplateChecks` |
| 37 | `/v1/admin/work-claims` | 11c:797, 11c:798, 11c:799 | NEW | `listWorkClaims`, `createWorkClaim` |
| 38 | `/v1/admin/work-claims/{}/releases` | 11c:799 | NEW | `releaseWorkClaim` (and `takeoverWorkClaim`) |

The 20 new operations: `previewAdminAction`, `startAdminActionVerification`, `listQuarantinedSubmissions`, `getQuarantinedSubmissionContent`, `releaseQuarantinedSubmission`, `rejectQuarantinedSubmission`, `getBottleneck`, `getOperationsSnapshot`, `overturnCells`, `voidCell`, `stopJob`, `listLeases`, `releaseLease`, `listAdminMetricSnapshots`, `createParameterChangeSet`, `runTemplateChecks`, `listWorkClaims`, `createWorkClaim`, `releaseWorkClaim`, `takeoverWorkClaim` (20 operations) [D].

## 15.D.2 Rules shared by every new operation [D]

1. **Inheritance.** Legend, universal errors, `Idempotency-Key`, cursors, `ETag` and rate-limit classes are those of 15.21 (`A-R`, `A-W`, `A-AUTH`). `Auth` is the `admin` scheme; `SU` and `2P` mean what 15.21.1 says. Nothing is restated.
2. **Audit trail.** Every write below inserts one `AdminAction` in the same transaction (15.21.3 rule 1) and carries `reason` (1..2000 characters). A read of case content (a submission, a lease's cell) is a logged `read` action (15.21.3 rule 3).
3. **Tightening one admin, loosening two (R10).** Stopping, voiding and pausing things is tightening: one admin with step-up. Anything that creates credit or restores a status is loosening: two admins (`2P`). The `2P` names added to `security.two_person_actions` by this file: `cell.overturn` and, for a loosening parameter set, the existing `parameter.loosen` (`ISS-154` already lists the mechanism; `ISS-117` of part 11c proposed `cell.overturn`) [A].
4. **Provider boundary.** None of these endpoints reads, fetches or stores anything from a provider page, a volunteer's chat or a volunteer's account; none accepts a provider credential or session; none submits anything on a volunteer's behalf (ground rule 2). Every address in a request is stored text, never fetched (15.35).
5. **Minimal data.** Responses carry ids, enums, counts, hashes and timestamps. A `mem_` id appears only where the operation's purpose needs it and is named below. No raw IP, e-mail, name, handle or provider identifier appears anywhere in this file.
6. **Permissions** follow `perm.<area>.<action>` (S0 0.8.2). New names are proposals; S10.* owns the matrix and may change holders without touching an endpoint [A]:

| Permission | Default holder | Used by |
| --- | --- | --- |
| `perm.job.stop` | operator | `stopJob` |
| `perm.cell.void`, `perm.cell.overturn`, `perm.cell.release` | operator (`perm.cell.void` also reviewer) | `voidCell`, `overturnCells`, `releaseLease` |
| `perm.lease.read` | operator | `listLeases` |
| `perm.claim.write` | operator, reviewer | work claims |
| `perm.metrics.view` | operator | `listAdminMetricSnapshots` |
| `perm.audit.read`, `perm.audit.resolve` (15.21.4) | reviewer | quarantine operations |

## 15.D.3 ALIAS decisions [D]

Each row: the cited path (and method), the S15 operation it means, and the difference the citing part must absorb. Where S15 and part 11c disagree about behaviour, S15 wins and the difference column says what 11c drops or reroutes.

### 15.D.3.1 Approvals, action log, abuse queue

| Cited path | S15 endpoint | Difference, if any |
| --- | --- | --- |
| `GET /v1/admin/approval-requests[/{apr_id}]` | `listApprovals`, `getApproval`: `GET /v1/admin/approvals[/{apv_id}]` | Entity is `AdminApproval`, id prefix `apv_` (not `ApprovalRequest`, `apr_`). Filter `?state` is `?status` (`pending`, `approved`, `rejected`, `withdrawn`, `expired`, `failed`; 11c lacked `failed`). `initiated_by_me` does not exist: S15 offers `?awaiting_me=true`; a screen that wants "mine" filters on `initiator_admin_id` in the page it holds, or asks for a new filter in a later S15 edit. Permission is `perm.approval.read` (operator, reviewer), not "any admin"; the list carries no `payload`, `getApproval` carries `payload` and `diff`. |
| `POST /v1/admin/approval-requests/{apr_id}/approvals` | `approveApproval`: `POST /v1/admin/approvals/{apv_id}/approvals` | Body is `{step_up}`, not `{payload_hash, reason_code, reason_text}`: the step-up assertion is already bound to the request hash of the STORED payload (15.22.3), so a client-supplied `payload_hash` is redundant and cannot be trusted anyway. A stale or foreign hash is `401 AUTH_INVALID` (`step_up_invalid`), not `409`. `403 FORBIDDEN` for the initiator and for a repeat approver is as in 11c. The `.../rejections` and `.../withdrawals` rows of 11c:208 map to `rejectApproval` (`POST /v1/admin/approvals/{apv_id}/rejections`, body `{reason}`) and `withdrawApproval` (`.../withdrawals`, initiator only); neither takes `reason_code`. |
| `GET /v1/admin/admin-actions[/{act_id}]` | `listAdminActions`, `getAdminAction`: `GET /v1/admin/actions[/{act_id}]` | Path segment is `actions`. Permission is `perm.admin_action.read`, not `perm.audit_trail.read` (S0 and S15 have no `audit_trail` area). Filters are `?admin_id`, `?op`, `?subject_type`, `?subject_id`, `?kind` (`write` or `read`), `?from`, `?to`. 11c's `result` of `refused` is not a field of `AdminAction` in S15: S15 records refused attempts only when they fail for authorization reasons (15.34.1); 11c AC-appr-01 and AC-abuse-02 that expect a refused `AdminAction` for other refusals contradict S15 and are changed to "no row, no event" (15.37 `AC-event-02`). |
| `GET /v1/admin/abuse-items[/{id}]` | Reports: `listReports`, `getReport` at `/v1/admin/reports[/{rpt_id}]`. Alarms: `listAlarms`, `getAlarm` at `/v1/admin/alarms[/{alm_id}]` with `?category=abuse` | S15 has two resources, a report (member-filed) and an alarm (system-raised), and states that an abuse flag IS an alarm (15.29.4). A unified queue is a client-side merge of two cursor streams sorted by `due_at` (reports) and `raised_at` (alarms); there is no union endpoint, because a union endpoint would need a third id space. |
| `POST /v1/admin/abuse-items/{id}/triages`, `.../dismissals`, `.../actions` | `triageReport` (`POST /v1/admin/reports/{rpt_id}/triages`); `closeReport` (`POST /v1/admin/reports/{rpt_id}/outcomes`) with `outcome = dismissed` or `actioned`; for an alarm `acknowledgeAlarm` (`POST /v1/admin/alarms/{alm_id}/acknowledgements`) | There is no `recordAbuseItemAction`: an action is an ordinary call of 15.28 or 15.29.6, and `closeReport` records the `act_` ids it led to (`linked_admin_action_ids`, at least one for `actioned`). An alarm has no "dismiss": acknowledging does not fix its cause (15.29.4). `If-Match` is not used: reports have no `ETag` in S15 (a second triage is `409 STATE_CONFLICT`). |

### 15.D.3.2 Ledger explorer (11c:502 to 11c:509)

| Cited path | S15 endpoint | Difference, if any |
| --- | --- | --- |
| `GET /v1/admin/ledger-accounts[/{lac_id}]` | `listLedgerAccounts`, `getLedgerAccount`: `GET /v1/admin/ledger/accounts[/{lac_id}]` | Path is `ledger/accounts` (a nested segment, not a hyphenated collection). 11c's required `context` for member accounts is replaced by S15's rule: `?member_id` needs `perm.ledger.read_member` and the read is logged as `kind = read` (15.21.3 rule 3). Whether a `context` link should also be required is an open point (last section). |
| `GET /v1/admin/ledger-accounts/{lac_id}/credit-lots` | `listLots`: `GET /v1/admin/ledger/lots?member_id=` | S15 has no per-account lot list; `getLedgerAccount` returns lot totals (`lots: {count, remaining_ucr, expiring_soon_ucr}`), and `listLots` needs `perm.ledger.read_member` with `?member_id` (the `owner_ref` of the account). `?expiring_before` is the only other filter. The read is logged. |
| `GET /v1/admin/ledger-entries[/{lge_id}]` | `listLedgerEntries`, `getLedgerEntry`: `GET /v1/admin/ledger/entries[/{lge_id}]` | Path only. S15 adds range limits (31 days or 1,000,000 `seq` values per scan) and rate class `A-W` for scans. |
| `GET /v1/admin/ledger-transactions[/{txn_id}]` | `getLedgerTransaction`: `GET /v1/admin/ledger/transactions/{txn_id}` | The list does not exist (15.D.5): use `listLedgerEntries?txn_kind=` for a kind, `getLedgerTransaction` for one transaction. Entries of a transaction come back together with `balanced` and `reverses_txn_id`. |
| `GET /v1/admin/invariant-checks` | `listInvariants`: `GET /v1/admin/ledger/invariants` for the overview (last check per invariant); `listInvariantChecks`: `GET /v1/admin/ledger/invariants/{inv_id}/checks` for the history of one; `getInvariantCheck`: `GET /v1/admin/ledger/invariant-checks/{ivc_id}` | S15 reuses the op name `listInvariantChecks` for the per-invariant history. There is no cross-invariant history list; the overview row carries `last_check` and `consecutive_failures`, which is what the screen needs. |
| `POST /v1/admin/ledger-verifications` with `{kind: chain or invariants}` | `kind = chain`: `startHashChainVerification`, `POST /v1/admin/ledger/verifications` `{from_seq, to_seq}`. `kind = invariants`: `runInvariant`, `POST /v1/admin/ledger/invariants/{inv_id}/runs` `{mode}` (once per invariant; the client loops) | A chain verification names a `seq` range (at most 1,000,000 values; larger audits are several calls) because an unbounded recompute is a denial-of-service lever on the ledger. "One at a time" is `409 STATE_CONFLICT` for `runInvariant`; `startHashChainVerification` has no such guard in S15, so two chain runs over disjoint ranges may overlap [A]. S15 answers `202` with `{ivc_id, state: running}`, polled through `getInvariantCheck`; 11c's `429 RATE_LIMITED` for a concurrent run is not used. Permission `perm.ledger.verify` (11c used `perm.ledger.read`, too weak for a heavy scan). |
| `GET /v1/admin/ledger-checkpoints` | `listLedgerCheckpoints`: `GET /v1/admin/ledger/checkpoints` | Path only. |
| `POST /v1/admin/ledger-reversals` | `reverseLedgerEntry`: `POST /v1/admin/ledger/reversals` | `202` carries an `AdminApproval` (`apv_`), body `{entry_id or txn_id, reason_code, reason, linked_ids}`, `SU` required, `required_approvals = ledger.reversal_min_approvers` (constant 2). |

### 15.D.3.3 Launch, kill switches, parameters, capacity, member lookup

| Cited path | S15 endpoint | Difference, if any |
| --- | --- | --- |
| `GET /v1/admin/launch-gates` | `listLaunchGates`, `getLaunchGate`: `GET /v1/admin/launch/gates[/{gate_id}]` | Path has a `launch/` segment. The list returns `{gate_id, state, items_total, items_signed_off}`; items and evidence come from `getLaunchGate`. |
| `GET /v1/admin/launch-gate-items/{lgi_id}` | `getLaunchGateItem`: `GET /v1/admin/launch/gate-items/{lgi_id}` | Path only. |
| `POST /v1/admin/launch-gate-items/{lgi_id}/evidence` | `attachGateEvidence`: `POST /v1/admin/launch/gate-items/{lgi_id}/evidence` | No `If-Match` (an item has `row_version` in no S15 schema); `Idempotency-Key` is required; `STATE_CONFLICT` if the item is `signed_off` (reopen first). The `.../{lgi_id}/reopenings` row of 11c:649 maps to `reopenGateItem` at `/v1/admin/launch/gate-items/{lgi_id}/reopenings`. |
| `POST /v1/admin/launch-signoffs` with `{gate_item_ids, enable_switches, reason}` | `signOffGateItem`: `POST /v1/admin/launch/gate-items/{lgi_id}/signoffs` `{comment}`, one call per item and per signer; enabling a switch is `changeLaunchSwitch` | The bulk call is removed (15.D.5). Sign-off is not an `AdminApproval`: it is native to the item, each signer's step-up is bound to that item's current evidence hash (15.27.2), and the item becomes `signed_off` at `launch.min_signoffs` distinct signers. |
| `POST /v1/admin/launch-switch-offs` | `changeLaunchSwitch`: `POST /v1/admin/launch/switch-changes` with `{switch, value: false, reason}` | `200` at once for one operator (turning off is tightening). 11c:651's separate noun is dropped. |
| `GET /v1/admin/launch-status` | `getLaunchStatus`: `GET /v1/admin/launch/status` | Path only; S15 adds `blockers` per switch (the output of `switchBlockers`), which feeds `BLK-header`. |
| `POST /v1/admin/kill-switch-engagements` with `{switch, reason_code, reason_text, context?}` | `engageKillSwitch`: `POST /v1/admin/kill-switches/{switch_key}/engagements` | `switch` moves into the path; `reason_text` is `reason`; `reason_code` is the S15 enum (`safety_incident`, `integrity_violation`, `provider_notice`, `policy_defect`, `abuse`, `capacity`, `other`); `context` becomes `linked_report_id` and `linked_alarm_id`; `public_text {fa, en}` is required for the four published scopes. |
| `POST /v1/admin/kill-switch-releases` | `releaseKillSwitch`: `POST /v1/admin/kill-switches/{switch_key}/releases` | `switch` in the path; body `{reason, verification: [{check, passed}], public_text?}`; `202` carries an `AdminApproval`. The `release_guard_failed` error lists `details.missing`. |
| `GET /v1/admin/change-log-entries` (includes non-public entries) | Reads: `listPublicChangeLog`, `getPublicChangeLogEntry`: `GET /v1/public/change-log[/{chg_id}]`. Writes: `annotateChangeLog`: `POST /v1/admin/changelog-entries` | S15 spells the admin collection `changelog-entries` (no hyphen between `change` and `log`); 11c's spelling is wrong. S15 has no non-public change-log entries (15.D.5), so an admin list would duplicate the public list; an admin uses the public endpoint (no credential needed). A change awaiting its human explanation is found through the alarm `changelog.explanation_overdue` and `explanation_due_at` on the entry. |
| `GET /v1/admin/capacity-dashboard` | `getCapacitySnapshot` (`GET /v1/admin/capacity`), `listCapacityDays` (`.../capacity/days`), `listSupplyGauges` (`.../capacity/supply-gauges`) | Tiles that S15 does not carry (queue depth, lease health, verification estimates, open alarms and engaged switches in one call) come from the NEW `getOperationsSnapshot` (15.D.4.6) and from `listAlarms`, `listKillSwitches`, `getLaunchStatus`. 11c's "fewer than k" rule is the same as S15's `suppressed: true` with `donors: null`. |
| `POST /v1/admin/member-views` with `{member_id, context:{kind, id}, reason_code, reason_text}` | `getMemberAdmin`: `GET /v1/admin/members/{mem_id}` | S15 makes it a `GET` (logged as an `AdminAction` of kind `read`, 15.21.3 rule 3, so "a POST because it writes a log row" is not needed). The `context` link and the reason are not part of S15; see the open point on member reads. 11c's "no `GET` list or search of members" (`AC-lookup-01`) contradicts S15's `listMembersAdmin` (`GET /v1/admin/members`, filters by status, tier, open report; no search by name, e-mail or handle). S15 is canonical: the list exists and 11c's acceptance criterion is rewritten to "no search by name, e-mail, handle or free text". |

