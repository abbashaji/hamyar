# FIX-10. API reconciliation applied to part 11c, second half

Cell C-081. Source of the edits: the section "Edits required in citing parts" of `spec/15e-api-reconcile-admin.md`, rows citing 11c line 560 and above, the AC rows, and `13:921`. Decisions: `docs/audit/FINAL.md` section 4. Line numbers in the table are where the text was found before the edit; 11c has drifted by about 3 lines since the audit. Nothing was run here; CI runs the acceptance scripts [A].

## Edits

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E1 API paragraph of 11.52.3 (cited 11c:615) | spec/11c-admin-tools.md:618 | `getCapacityDashboard` at `/v1/admin/capacity-dashboard`; `listMetricSnapshots` | `getCapacitySnapshot` at `/v1/admin/capacity`, `listCapacityDays`, `listSupplyGauges`, `getOperationsSnapshot` at `/v1/admin/capacity/operations`; `listAdminMetricSnapshots`; `getBottleneck` (15.D.4.6) | applied |
| E2 same op rename in `AC-capdash-05` (second occurrence of the E1 rename) | spec/11c-admin-tools.md:626 | `getCapacityDashboard` is called | `getCapacitySnapshot` is called | applied |
| E3 gate list and item paths (cited 11c:647) | spec/11c-admin-tools.md:650 | `/v1/admin/launch-gates`, `/v1/admin/launch-gate-items/{lgi_id}` | `/v1/admin/launch/gates[/{gate_id}]`, `/v1/admin/launch/gate-items/{lgi_id}` | applied |
| E4 gate evidence (cited 11c:648) | spec/11c-admin-tools.md:651 | `/v1/admin/launch-gate-items/{lgi_id}/evidence`; `CT1`; `If-Match` | `/v1/admin/launch/gate-items/{lgi_id}/evidence`; `CT1`; no `If-Match`; `Idempotency-Key` required | applied |
| E5 gate reopening (cited 11c:649) | spec/11c-admin-tools.md:652 | `POST .../{lgi_id}/reopenings` | `POST /v1/admin/launch/gate-items/{lgi_id}/reopenings` | applied |
| E6 sign-off row (cited 11c:650) | spec/11c-admin-tools.md:653 | `createLaunchSignoff`, `/v1/admin/launch-signoffs`, body with `gate_item_ids`, `202` | `signOffGateItem`, `/v1/admin/launch/gate-items/{lgi_id}/signoffs`, body `{comment}`, `201`, one call per item, switch on by `changeLaunchSwitch` | applied |
| E7 switch off (cited 11c:651) | spec/11c-admin-tools.md:654 | `createLaunchSwitchOff`, `/v1/admin/launch-switch-offs` | `changeLaunchSwitch`, `/v1/admin/launch/switch-changes` with `{switch, value: false, reason}` | applied |
| E8 launch status (cited 11c:652) | spec/11c-admin-tools.md:655 | `/v1/admin/launch-status` | `/v1/admin/launch/status` | applied |
| E9 kill-switch engagement (cited 11c:700) | spec/11c-admin-tools.md:703 | `/v1/admin/kill-switch-engagements`, body `{switch, reason_code, reason_text, context?}` | `/v1/admin/kill-switches/{switch_key}/engagements`, body `{reason_code, reason, public_text?, linked_report_id?, linked_alarm_id?}` | applied |
| E10 kill-switch release (cited 11c:701) | spec/11c-admin-tools.md:704 | `/v1/admin/kill-switch-releases` | `/v1/admin/kill-switches/{switch_key}/releases`, body `{reason, verification, public_text?}` | applied |
| E11 member lookup op (cited 11c:751) | spec/11c-admin-tools.md:754 | `createMemberView`, `POST /v1/admin/member-views`, body with `context` and `reason_text` | `getMemberAdmin`, `GET /v1/admin/members/{mem_id}`, no body, logged as a `read` `AdminAction`; `Cache-Control: no-store` kept. default-pending D-20: no required `context_id`, the read is logged, not justified [A] | applied |
| E12 handle-resolution op row (cited 11c:752) | spec/11c-admin-tools.md:755 | row `createHandleResolution`, `POST /v1/admin/handle-resolutions` | row deleted (15.D.5) | applied |
| E13 handle-resolution paragraph (cited 11c:752, paragraph before the table) | spec/11c-admin-tools.md:750 | paragraph on `member.resolve_handle` and the HMAC recompute | paragraph deleted (15.D.5) | applied |
| E14 `requeue_at_front` sentence (cited 11c:793) | spec/11c-admin-tools.md:796 | sentence on an optional `requeue_at_front` at the head of the queue | sentence deleted | applied |
| E15 work-claim release row (cited 11c:799) | spec/11c-admin-tools.md:802 | `createWorkClaimRelease`, `createWorkClaimHandover`, `createWorkClaimTakeover`; `.../handovers`; takeover is `CT2` | `releaseWorkClaim`, `takeoverWorkClaim`; `.../releases`, `.../takeovers`; no handover; takeover is operator with step-up | applied |
| E16 lease release op (cited 11c:801) | spec/11c-admin-tools.md:804 | `createLeaseRelease` | `releaseLease` | applied |
| E17 lease release body (cited 11c:801) | spec/11c-admin-tools.md:804 | body `{reason_code, reason_text, requeue_at_front}` | body `{reason_code, reason}` | applied |
| E18 `AC-appr-03` parameter name | spec/11c-admin-tools.md:232 | `security.admin_two_person_pending_ttl_s` | not changed; the edit would rename to `security.approval_ttl_s`, but D-22 lists "name of the approval lifetime" as an owner decision with default "Defaults stand", and 11.58 of this part still defines the old name [A] | skipped-needs-owner |
| E19 `AC-appr-01` refused `AdminAction` | spec/11c-admin-tools.md:230 | new text already present: no row and no event, refused only for authorization failures (15.34.1) | no change | already-applied |
| E20 `AC-abuse-02` refused `AdminAction` | spec/11c-admin-tools.md:468 | new text already present, same wording | no change | already-applied |
| E21 `AC-lookup-02` refused `AdminAction` | spec/11c-admin-tools.md:760 | `422 UNPROCESSABLE`; a refused `AdminAction` is written | `422 UNPROCESSABLE`; no row and no event for a guard refusal (a refused `AdminAction` is written only for authorization failures, 15.34.1) | applied |
| E22 `AC-lookup-01` member search | spec/11c-admin-tools.md:759 | any `GET` list or search of members; `404`; no such route exists | a request that searches members by name, e-mail, handle or free text; `404`; `GET /v1/admin/members` filters by `status`, `trust_tier`, `has_open_report` only. Follows 15e (S15 is canonical); default-pending D-20 [A] | applied |
| E23 `perm.metrics.view_small_cells` (cited 13:921) | spec/13-measurement.md:921 (FINAL.md 3.2 found it at 13:924) | not read by this cell | not edited: part 13 is outside `allowed_paths`; FIX-11 edits 13 | skipped-needs-owner |

Searched for E18 to E23: AC rows read at 11c:228-234, 466-470 and 759-766; part 13 was not opened.

## Read-back

After all edits the edited places were read again from the branch (11c now has 876 lines).

| edit | what the text now says |
| --- | --- |
| E1 | API paragraph names `getCapacitySnapshot`, `getOperationsSnapshot`, `listAdminMetricSnapshots`, `getBottleneck` and ends "(15.D.4.6)"; no `capacity-dashboard` path left |
| E2 | `AC-capdash-05` calls `getCapacitySnapshot`; `getCapacityDashboard` appears nowhere in lines 560 to the end |
| E3 to E8 | The launch op table has `/v1/admin/launch/gates`, `.../launch/gate-items/...` (evidence, reopenings, signoffs), `/launch/switch-changes` and `/launch/status`; the evidence row reads "no `If-Match`" |
| E9, E10 | Engagement is at `/v1/admin/kill-switches/{switch_key}/engagements` with the new body; release is at `.../releases` with `{reason, verification, public_text?}` and still "`202` with an `ApprovalRequest`" |
| E11 | One row, `getMemberAdmin` at `GET /v1/admin/members/{mem_id}`, "No body" |
| E12, E13 | Under the heading "11.55.3 Handle resolution" the paragraph is gone and the op table holds only `getMemberAdmin` |
| E14 | The 11.56.3 paragraph runs from the revoked-lease sentence straight on; `requeue_at_front` is no longer in the paragraph or in the lease row |
| E15, E16, E17 | Work-claim table row reads "No handover; takeover is operator with step-up"; lease row is `releaseLease` with body `{reason_code, reason}` |
| E18 | `AC-appr-03` still names the 11.58 parameter, unchanged by design |
| E19, E20 | Both rows carry the 15.34.1 wording |
| E21, E22 | `AC-lookup-02` ends with the 15.34.1 wording; `AC-lookup-01` says "`GET /v1/admin/members` filters by" three fields |
| E23 | Not edited here |

No path replaced by 15e remains in 11c from line 560 to the end (read in full). Lines below 560 belong to FIX-09 and were read only where an AC row sits.

Left as written because the edit list does not authorize a change (for FIX-21, the re-audit or the owner):

- The prose before the launch op table ("A `launch.signoff` request is the only way to turn a switch on..."), `AC-gate-02` to `AC-gate-04` and the `Launch sign-off` row of 11.44.5 still describe the removed bulk approval; S15 makes sign-off native to the item.
- The op ids `createLaunchGateEvidence`, `createLaunchGateReopening`, `createKillSwitchEngagement` and `createKillSwitchRelease` are not renamed (the edit rows change paths and bodies only). The engage reason codes of 11.54.1 differ from the S15 enum, and the release row still says `ApprovalRequest` where 15e says `AdminApproval`.
- Handle resolution: the heading 11.55.3, the role line, `AC-lookup-07` and `AC-lookup-08`, the `member.resolve_handle` names in 11.58 and `ISS-117` remain. Member view: the "No search" and "Context linkage" rows of 11.55.1, `AC-lookup-02` (context, `createMemberView`) and `AC-lookup-05` describe the lookup 15e replaced.
- Work claims and leases: the hand-over prose of 11.56.2, `AC-claim-04`, `AC-claim-08` (`requeue_at_front`) and `ISS-117` (k) remain.
- The Notes cell "Gates with items and evidence" on the gate list row: S15's list returns counts, items come from `getLaunchGate`.

Result: DONE WITH SKIPS
