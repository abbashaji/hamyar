# FIX-12: API consistency corrections applied to spec/15a-api-core.md

*Cell C-083. Applies the corrections of `spec/15g-api-consistency.md` `## Corrections required` that target `spec/15a-api-core.md`: CR-04, CR-08, CR-15, CR-16, CR-19, CR-29, CR-31, CR-33, CR-36, CR-37, plus the decision-dependent CR-01, CR-02, CR-03 handled by the defaults of `docs/audit/FINAL.md` section 4. Only `spec/15a-api-core.md` and this log were edited. Lines are the ones in the file after the edits (the audit lines had drifted; every place was found within a few lines). Nothing was run: the acceptance scripts run in CI.*

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| CR-04a symmetric wrong_scheme | spec/15a-api-core.md:92 | `member` scheme row only said an admin token here is `401 wrong_scheme` | adds the reverse: a member token on an `admin` route is the same 401 and reason, never 403 or 404, not stored under an idempotency key | applied |
| CR-04b header on none routes | spec/15a-api-core.md:93 | `none` row said nothing about an `Authorization` header | header on a `none` operation is ignored, not evaluated, not logged, response identical; the two dual-scheme rows of part b are the exception | applied |
| CR-04c step-up at step 7 | spec/15a-api-core.md:124-126 | pipeline step 7 listed switches, member status and cooldown only | adds member step-up missing or invalid: 401 AUTH_INVALID (step_up_required, step_up_invalid) | applied |
| CR-04d AC-api-02 | spec/15a-api-core.md:851 | tested steps 1, 3, 4, 8 only | adds the case: valid member token without valid step-up is 401 step_up_required at step 7, before step 8 | applied |
| CR-04e AC-auth-01..03 | spec/15a-api-core.md:868-870 | not present | the three criteria added after AC-api-19, wording of 15g 15.G.3 | applied |
| CR-08 step 7 kill.member | spec/15a-api-core.md:124-126 | step 7 said any kill switch is 503 | 503 limited to the four published keys; kill.member.mem_id is 403 FORBIDDEN (account_frozen) | applied |
| CR-08 ER-01 AUTH_INVALID | spec/15a-api-core.md:611 | reasons ended at key_pending | adds step_up_required, step_up_invalid, assertion_invalid | applied |
| CR-08 ER-02 FORBIDDEN | spec/15a-api-core.md:613 | account_frozen already listed (A12 finding 6); no service_id key | adds service_gate_regressed, second_admin_required, approver_not_distinct and the key service_id | applied |
| CR-08 ER-03 VALIDATION_FAILED | spec/15a-api-core.md:78, 609 | 8 reasons; field codes closed without secret_pattern | adds the 8 reasons of 15.D, 15.E, 15.23; secret_pattern added to the field codes of rule 1 and the row points to rule 1 | applied |
| CR-08 ER-04 STATE_CONFLICT | spec/15a-api-core.md:616 | 12 reasons | adds the 33 reasons of S15b to S15f; approval_guard_failed deliberately not added (15g says keep guard_failed) | applied |
| CR-08 ER-05 UNPROCESSABLE | spec/15a-api-core.md:629 | 7 reasons | adds the 17 reasons listed in ER-05 | applied |
| CR-08 ER-06 ALREADY_EXISTS | spec/15a-api-core.md:618 | 3 reasons | adds appeal_exists, report_exists | applied |
| CR-08 ER-07 PRECONDITION_FAILED | spec/15a-api-core.md:621 | etag_mismatch only | adds version_stale | applied |
| CR-08 ER-08 launch and kill rows | spec/15a-api-core.md:614, 635 | LAUNCH_GATE_CLOSED had no reasons; member key unstated | reasons members_not_open, jobs_not_open, minting_not_open; paragraph says KILL_SWITCH details.switch has four keys and the member key is FORBIDDEN account_frozen | applied |
| CR-08 ER-09 POLICY_REJECTED slugs | spec/15a-api-core.md:635 | four slugs absent | listed in the paragraph under the table, tagged P: S7 owner | applied |
| CR-08 ER-10 RATE_LIMITED | spec/15a-api-core.md:635 | 15b uses RATE_LIMITED for a cap | one sentence: a count cap is CAP_EXCEEDED; the 15b use itself is removed by CR-03 in 15b, not here | applied |
| CR-08 ER-11 details keys | spec/15a-api-core.md:635 | keys missing, blockers, guards, constraints, counts, balance_ucr, state, until, service_id, reasons not catalogued | listed once as optional keys of STATE_CONFLICT, VALIDATION_FAILED, FORBIDDEN (15g gives no per-row assignment) | applied |
| CR-08 copy keys | spec/15a-api-core.md:635 | no rule for added reasons | every added reason has copy.api_error.code.reason, S11 owns the text | applied |
| CR-15a unknown query parameter | spec/15a-api-core.md:78 | rule 1 covered bodies only | unknown query parameter is 400 VALIDATION_FAILED, unknown_field, path = parameter name | applied |
| CR-15b confirmJob reservation_id guard | spec/15a-api-core.md:517 (15.7.2 Confirm bullet) | guard list has no reservation guard | not edited: the guard text is in 15d S2, which 15g does not quote and this cell may not read | skipped-needs-owner |
| CR-16 createReport subjects | spec/15a-api-core.md:367, 372 | result took id<sub>; no team subject | result takes id<sub> or, for the job owner, id<cel>; team added with id<tem> (404 if not readable) | applied |
| CR-19a Member.client_events_enabled | spec/15a-api-core.md:189, 199 | field absent | additive bool on Member, read-only (updateMe does not take it), tagged A and V | applied |
| CR-19b getFeatures reflects the parameter | spec/15a-api-core.md:600 | Feature flags bullet silent on client events | getFeatures also reflects the global client-event parameter of 15f; the name and exact place in Features are 15f's | applied |
| CR-29a createLease gates | spec/15a-api-core.md:145, 345-346 | gates: Commons switch, template and service kill; member-job cells ungated by launch switch | adds kill.all_minting (Commons), launch.member_jobs_enabled (member-job), kill.member 403 account_frozen at step 7, service_gate continue with 403 service_gate_regressed; gate matrix row for member-job cells updated | applied |
| CR-29b listOfferedCells drops | spec/15a-api-core.md:334 | dropped Commons, paused or suspended cells | adds member-job cells while launch.member_jobs_enabled is false and cells with no service passing service_gate continue | applied |
| CR-29c exempt operations | spec/15a-api-core.md:146, 361 | exemption unstated | extendLease, issueLeaseNonce, expandLeasePrompt exempt (matrix row and Lost nonce bullet) | applied |
| CR-29d listOfferedCells and kill.member | spec/15a-api-core.md:334 | unchanged | not edited: 15g names kill.member as missing for both calls but states no list behavior, and the matrix says reads still work | skipped-needs-owner |
| CR-31 RL-PUB equals PUB | spec/15a-api-core.md:702, 712 | RL-PUB vs part b PUB unrelated in text | RL-PUB is the same class as PUB, PUB-V is a sibling; contract tests key on details.class | applied |
| CR-33 payment at acceptance | spec/15a-api-core.md:394 | acceptance posts the entry, no gate named | names the mint gate and service_gate continue; a closed gate keeps verdict pending, no ledger entry, no 503 or 403, mint held (tagged A, P: S6 owner) | applied |
| CR-36a refund read | spec/15a-api-core.md:545 | refund_ucr visible in getJob | read through getSettlementReceipt (part 15d), Job has no refund field | applied |
| CR-36b Job.rating | spec/15a-api-core.md:489, 548 | Job had no rating | Job.rating object (score, comment, updated_at) or null, same shape as the rateJob response | applied |
| CR-37 Team score and Phase 1 listing | spec/15a-api-core.md:586, 597 | Team had verified_cells_30d only; listTeamMembers and alias active | Team.score {week_start, week, all_time} added; listTeamMembers and alias stay defined but off until the part 12 owner enables them (flag name theirs) | applied |
| CR-01, CR-02 admin id rename | spec/15a-api-core.md:19 (15.1 Operation tables) | 15a says admin ids are prefixed admin in the OpenAPI key | unchanged, default-pending D-08 (neither id renamed, both rules written down) | skipped-needs-owner |
| CR-03 share cards | spec/15a-api-core.md:598 | getShareCard computed, no stored link | unchanged, default-pending D-15 (computed card); the deletion is in 15b, not this cell | already-applied |

## Notes and deviations

- `docs/source/Hamyar - Founding Document.md` and `docs/source/prompt.md` were not opened. No edit adds a provider fact, touches volunteer-account handling, or uses the word guaranteed; a reader of FIX-24's re-audit should still check the new text against FD Principle 8 (the `team` report subject and the Team `score`).
- `spec/15d` and `spec/15f` were not read (not in this cell's list). That is why CR-15b is skipped and why CR-19b names no parameter.
- Out of scope, so not edited here: CR-34 (event for an immediate cancel), CR-28 (gates of createJob, submitJobForScreening, confirmJob, createReservation, and AC-api-18) and CR-30 (15.10 rows). `AC-api-18` therefore still speaks only of the minting switch for leases.
- `AC-auth-01` to `AC-auth-03` are defined here; the 15b cell (FIX-13) should reference them instead of defining the same ids again.
- Possible overlap for the S14 and S6 owners: the `submitResult` row of the gate matrix says a switch that pauses the cell revokes the lease (410), while CR-33 holds the mint as `pending` when the mint gate closes without pausing the cell.
- Tags: the new service_gate error on `createLease` and the service gate at acceptance are tagged A (15g gives the gate, not the error).

## Read-back

After all edits every place was read again in the branch file.

- CR-04a, line 92: the member row now ends with the reverse rule, "never `403` or `404`".
- CR-04b, line 93: the `none` row now says the header "is ignored" and the response is identical.
- CR-04c and CR-08 step 7, lines 124-126: step 7 now has three lines; the kill line says "the four published keys", then kill.member 403, then step-up 401.
- CR-04d, line 851: AC-api-02 now continues with the step-up case "answered at step 7".
- CR-04e, lines 868-870: three bullets AC-auth-01, AC-auth-02, AC-auth-03 follow AC-api-19 and precede `## Issues raised`.
- ER-01 to ER-07, lines 609-621: the rows show the added reasons, for example "`version_stale`" on PRECONDITION_FAILED.
- ER-08 to ER-11 and copy keys, line 635: one paragraph under the table covers keys, slugs, the member key and copy keys.
- Rule 1, line 78: the field codes end with `secret_pattern` and the next sentence covers an unknown query parameter.
- CR-16, lines 367 and 372: schema shows `"team"` and `id<tem>`; text names `id<cel>` for the job owner.
- CR-19a, lines 189 and 199: `client_events_enabled: bool` sits after email_notifications; the paragraph calls it read-only.
- CR-19b, line 600: the Feature flags bullet has the added sentence about the global client-event parameter.
- CR-29a, lines 145 and 345-346: the matrix row shows `launch.member_jobs_enabled`; createLease has a separate service gate line.
- CR-29b, line 334: the drop line now includes member-job cells and the service gate condition.
- CR-29c, lines 146 and 361: a matrix row and the Lost nonce bullet both state the exemption.
- CR-31, lines 702 and 712: RL-PUB row mentions `PUB-V`; the first bullet says tests key on `details.class`.
- CR-33, line 394: the Payment bullet says the submission is stored with `verdict` `pending`.
- CR-36, lines 489, 545, 548: Job has a `rating` line; cancelJob points at `getSettlementReceipt`; the Rating bullet ends with `Job.rating`.
- CR-37, lines 586 and 597: Team shows a `score` line; the Teams bullet says the listing and alias are off.
- Skipped rows: line 517 (confirmJob guards) and line 334 are unchanged; line 19 (admin id rule) and line 598 (share card) are unchanged.

Result: DONE WITH SKIPS
