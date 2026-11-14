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

