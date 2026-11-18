# FIX-22: requester rejection copy owner, empty eligible set, kill-switch pause reasons

Cell C-093. Sources: docs/audit/A10.md findings 11, 12, 13; docs/audit/FINAL.md sections 3, 4, 5.1 (FIX-22). Files edited: `spec/07-policy.md`, `spec/11b-requester-ux.md`. `spec/11c-admin-tools.md` was read only (11.64.1, 11.64.2). Nothing was executed; acceptance runs in CI. Line numbers are post-edit lines of the branch of this cell.

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E1 global state `kill_switch` lists the member switch (A10 #13) | spec/11b-requester-ux.md:77 (11.33.2) | trigger listed three switches, no `kill.member.<mem_id>`; copy text only | trigger lists four switches; same `copy.req.err_kill_switch` text for every switch, cause never shown, member switch never named or hinted at (consistent with 11c 11.64.1 and 11.64.2) | applied |
| E2 pause reasons per switch (A10 #13) | spec/11b-requester-ux.md:550 and :558-572 (11.39.1) | `kill_switch` row with `copy.req.pause_kill` as if a switch caused it; no mapping | row kept and marked reserved; new table maps `kill.template` to `template_paused`, `kill.service` to `service_paused`, `kill.all_new_jobs` and `kill.member` to no pause (refusal copy only), `kill.all_minting` to nothing | applied |
| E3 acceptance rows for the pauses (A10 #13) | spec/11b-requester-ux.md:618-621 (after AC-req-43) | only AC-req-43 | AC-req-43a, 43b, 43c added (template pause, service pause, no pause for all_new_jobs and member switch); AC-req-43 unchanged | applied |
| E4 11b alias table flagged (A10 #11) | spec/11b-requester-ux.md:883 (11.43.1 table header) | columns `Copy key`, `EN (reason, then what to change)`, `FA` | columns say the keys are aliases of the 7.4.3 keys and that the 11b wording is flagged and not rendered; no row text deleted | applied |
| E5 owner sentence in 11.43.1 (A10 #11) | spec/11b-requester-ux.md:895 | note that C-001 must keep one set and the `copy.req.reason_*` rows are rendered meanwhile | spec/07 7.4.3 is the single owner and its wording is rendered; `copy.req.reason_r1`..`r7`, `copy.req.note_r8` are aliases; `copy.req.err_policy_changed` stays a separate pre-confirmation key (default of D-19 applied: text as written, owner decision open) | applied |
| E6 owner block in spec/07 7.4.3 (A10 #11, #12) | spec/07-policy.md:296-314 | table of copy keys with no statement of ownership, no alias list, no hint text | statement of single ownership, alias map (r1..r7, note_r8, err_no_service, err_policy_changed as not an alias), hint key `copy.policy.R7.no_approved_service.hint` with EN and FA text taken from 11b, and an empty-eligible-set paragraph | applied |
| E7 empty eligible set screen (A10 #12) | spec/11b-requester-ux.md:895 (11.43.1) | two ways stated: R7 sub-code or `422 UNPROCESSABLE` | R7 with `details.sub_code` `no_approved_service` is the owner behaviour (7.4.2, 7.10.7 E1 and E4); hint shown, nothing charged, no advice to change the license; where it appears (`SCR-req-02` at `createJob`, `SCR-req-06` after screening); `UNPROCESSABLE` kept as fallback alias | applied |
| E8 conditions table row for the empty set (A10 #12) | spec/11b-requester-ux.md:913 (11.43.2) | row for `422 UNPROCESSABLE` only | row names `422 POLICY_REJECTED` with R7 and sub-code first and `422 UNPROCESSABLE` as fallback alias; key `copy.req.err_no_service` and its EN and FA text unchanged, now an alias of the 7.4.3 hint | applied |
| E9 acceptance row for the empty set (A10 #12) | spec/11b-requester-ux.md:944 (after AC-req-66) | none | AC-req-66a added | applied |
| E10 conditions table row for the kill switch (A10 #13) | spec/11b-requester-ux.md:905 (11.43.2) | `503 KILL_SWITCH_ENGAGED` with no cause list | cause list with the four switches, cause never shown; EN and FA text unchanged | applied |
| E11 what a targeted member sees under `kill.member.<mem_id>` (A10 #13) | spec/11b-requester-ux.md:77, :905 | generic text only, no decision recorded | no new member-specific copy written; the generic text above is used so that nothing hints at a member switch; whether a targeted member should see anything else is not in FINAL section 4 and has no default | skipped-needs-owner |
| E12 which job pauses under `kill.service.<svc_id>` (A10 #13) | spec/11b-requester-ux.md:560-565 vs spec/07-policy.md 7.10.5 vs spec/11c-admin-tools.md 11.64.2 | 07 pauses a job when its eligible set empties; 11c pauses jobs pinned to the service (`M1`) | 11b table states that the server reports the pause either way; the two conditions are not reconciled (11c is outside allowed paths; S14.* decides) | skipped-needs-owner |

## Read-back

All places below were re-read after the edit (apply_changes base 3c20b8c).

- E1, spec/11b-requester-ux.md:77: the `kill_switch` row lists four switches including `kill.member.<mem_id>`, and its behaviour cell says the text is the same for every switch; it ends with the pointer to `pause_reason` in 11.39.1.
- E2, spec/11b-requester-ux.md:550 and :558-572: the first row of the pause table now reads "reserved" in its value cell; below the table a five-row table lists the switches with their pause value and copy, and a closing paragraph keeps `copy.req.pause_kill` as the display for a future job-pausing global switch.
- E3, spec/11b-requester-ux.md:618-621: AC-req-43 is unchanged and AC-req-43a, 43b and 43c follow it, before AC-req-44.
- E4, spec/11b-requester-ux.md:883: the header cells read as aliases and as flagged 11b wording; the nine rows below are as before.
- E5 and E7, spec/11b-requester-ux.md:895: one paragraph holds the R9 note, the sub-code hint sentence, the empty-set rule, the ownership statement and the note on `copy.req.err_policy_changed`; it ends with the evidence tag.
- E6, spec/07-policy.md:296-314: after the R10 and R8 note there is a bold ownership paragraph, an alias table with four rows, a one-row hint table and a bold empty-set paragraph; the next heading is 7.5.
- E8, spec/11b-requester-ux.md:913: the condition cell begins with `422 POLICY_REJECTED`, then the fallback alias; the EN and FA cells are unchanged.
- E9, spec/11b-requester-ux.md:944: AC-req-66a follows AC-req-66 and ends at the identical-screen clause.
- E10, spec/11b-requester-ux.md:905: the condition cell lists the four switches and says the cause is never shown; EN and FA cells are unchanged.
- E11 and E12: no text was written for them; the table at spec/11b-requester-ux.md:560-565 shows the wording "either way" and the member row names no copy beyond the generic key.

Owner decisions touched: D-19 (copy choices, default: text as written, flagged for human and legal review) for the 11b wording that differs from 07 and for `R9`. E11 and E12 are not in FINAL section 4; they are raised here for the owner and for S14.* and S7.*.

Result: DONE WITH SKIPS
