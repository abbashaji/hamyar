# FINAL-3: readiness report round 3, merging docs/audit/FINAL-3a.md, docs/audit/FINAL-3b.md, docs/audit/FINAL-3c.md and docs/audit/FINAL-3d.md

*Cell C-160. Written by a reviewer who wrote none of the four slice files, the fix logs or the audited parts. Nothing was executed here; CI runs the acceptance commands. I read the four slice files completely, `docs/owner-decisions.md` completely and `docs/audit/FINAL-2.md` lines 1-150 (the 69 rows and the Checked block). Line numbers in the findings are those of the slices; where I opened the line myself and count a different number, the row says so. No file content is pasted.*

## Totals

| Slice | File | Cell | Raw rows | Major | Minor | Blocking | Slice verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | FINAL-3a.md (fix logs R3-01 to R3-06) | C-156 | 17 | 8 | 9 | 0 | NOT READY |
| B | FINAL-3b.md (fix logs R3-07 to R3-12) | C-157 | 15 | 2 | 13 | 0 | NOT READY |
| C | FINAL-3c.md (fix logs R3-13 to R3-18) | C-158 | 16 | 2 | 14 | 0 | READY WITH LOGGED ITEMS |
| D | FINAL-3d.md (contradictions across parts) | C-159 | 13 | 9 | 4 | 0 | NOT READY |
| Sum | | | 61 | 21 | 40 | 0 | |

Ten raw rows merge into others, which leaves **51 open findings: 17 major and 34 minor, none marked blocking**. The merges: 3a-1 with 3d-5 (invite state); 3a-2 and 3a-3 with 3d-6 (key states); 3a-8 with 3d-8 (two-person action names); 3a-14 with 3d-10 (`email_index`); 3b-7 with 3d-12 (`Job.rating` time); 3d-9 with 3d-13 (operation ids); 3a-17, 3b-15, 3c-9 and 3c-10 (line citations in the logs). No slice used the severity blocking. I do not raise any row to blocking, because the rule of the cell leaves that to the owner, but rows 1, 4, 9, 11 and 14 below each make a correct implementation fail or two parts describe incompatible behaviour, and I would hold assembly for them.

None of the four slices reports a false claim of an applied edit except one: R3-01 edit 35 (row 2 below, 3a). The slices together opened about 280 applied edits in the part files (3a more than 70, 3b about 95, 3c 87 of 87; 3d had no log) and found them present. So the fix round did what its logs say; the remaining defects are skipped edits, edits that created a new contradiction, and contradictions that no fix cell was asked to look for.

## Checked

**What I opened.** `FINAL-3a.md` (56 lines), `FINAL-3b.md` (57), `FINAL-3c.md` (52) and `FINAL-3d.md` (54), all four from the first line to the last. `docs/owner-decisions.md` (55 lines): D-01 to D-22 accepted by the owner on 2026-11-19, D-18a and D-23 to D-34 as recorded resolutions. `docs/audit/FINAL-2.md` lines 1-150: the Checked block, the 69 rows and the owner list.

**Spot checks (14 findings, from all four slices, opened by me at the cited place).** Result in each line.

1. 3a-1 and 3d-5, `spec/10a-identity.md:97`: check 6 says the `Invite` must be in state `active`. Reproduced.
2. 3a-2 and 3d-6, `spec/10a-identity.md:139`: the Effect row says the old key becomes `rotated`, not `retiring`. Reproduced. This is the one place where a log claim (R3-01 edit 35) is false.
3. 3a-5, `spec/05a-entities.md:1436-1442`: `devices` still has `creation_ip_hash`, `ip_hash_key_version`, `creation_ip_hash_expires_at`, the CHECK on the pair and the index `devices_ip`. Reproduced. This contradicts the statement of 3d Checked item 1 that the IP hash is closed in 05a, 10a and 10b; 3d read 05a:145, not the DDL. See the conflict note below.
4. 3a-8, `spec/11c-admin-tools.md:195` and `:198`: the catalog row `member.resolve_handle` (`CT3`, 2 approvers) and the sentence naming it among the proposed two-person additions are both still there. Reproduced.
5. 3d-8, `spec/10a-identity.md:759`: it reads that `security.two_person_actions` starts as the four of S0.10.6 plus `member.ban`, `invite.seed_issue`, `admin.role_grant`, `admin.credential_add`, `admin.credential_unlock` and `disclosure.release`. Reproduced as a second default list, but 3d describes it as exactly five names; the line has six additions to S0's four. What S0:832 lists I did not open.
6. 3d-1, `spec/10a-identity.md:85`: the registration pseudocode ends with showing the recovery key screen before leaving onboarding. Reproduced; 11a:298 and 11d:562 were not re-opened by me.
7. 3d-4, `spec/15a-api-core.md:98-103`: five purposes (`create`, `session`, `rotate`, `recover`, `device_link`), and the paragraph at :103 says `create` and `device_link` carry no server challenge. Reproduced; 10a:67 and :95 (seven purposes, a `create` challenge) were read as quoted by 3d and by the check-4 row I saw at 10a:95.
8. 3b-1, `spec/05b-state-machines.md:90` (JT-15): the from list is admitted, running, suspended and assembling, `funding_shortfall` fires when now is at or after `acceptance_deferred_until`, and `overrun_timeout` has its own deadline formula. Reproduced for those two guards. I did not open :187 or :675, so that G-accept sets the deferral to the overrun deadline is the slice's reading; 5.29.8 is unread by every slice.
9. 3b-2, `spec/05b-state-machines.md:326-328`: the `cell_rejection`, `member_suspension` and `member_ban` rows still post a Reserve `grant` with reason `appeal_restitution`. Reproduced against D-03 (Reserve pays nothing beyond grants, `appeal_restitution` stays off).
10. 3b-5, `spec/16-parameters.md:370` and `:372`: `service.min_approvers` and `template.min_reviewers_new` still read 1..5; `template.min_reviewers_edit` at :373 reads 1..2 with a pointer to 0.9.5. Reproduced for the S16 side; the S0 side (00:772, :774) was not opened.
11. 3c-1, `spec/08b-verification.md`: the `verification.risk_class` row says none is `high` by default in Phase 1 (the row is at :33 by my count, the slice says :32). Reproduced; 08a 8.13.2 was not opened.
12. 3c-4, `spec/13-measurement.md:865`: `strata` still lists `trust_tier` and `join_source` and points to S12.11.4, and :864 gives `population` as `external` or `all`. Reproduced.
13. 3c-6, `spec/14-launch-gates.md`: the `cell.leased` row (:551 by my count, the slice says :552) lists `LAUNCH_GATE_CLOSED`, `KILL_SWITCH_ENGAGED` and `FORBIDDEN` with `account_frozen` and not `service_gate_regressed`, while :544 and :550 define that reason with `details.service_id` (singular, as 3c-7 says). Reproduced.
14. 3c-14, `spec/19-risks.md:306`: the paragraph still writes bare `OD-01`, `OD-03`, `OD-02`, `OD-04` and `OD-11`, and :308 says prose never writes a bare id. Reproduced.

All 14 reproduce; none was found false. Two had a one-line offset against the slice (11 and 13), and one slice description was imprecise (5). Every offset I found is listed in the rows below.

**Cross-slice conflicts found while merging.**

- **IP hash.** 3d Checked item 1 says 05a, 10a and 10b now agree that no IP hash is persisted and calls FINAL-2 rows 2 and 13 closed. 3a-5 says the `devices` DDL and clause 5.15.4 of 05a still persist it. I opened the DDL (spot check 3): 3a is right and 3d's item is true only of the prose. FINAL-2 row 13 is therefore closed in text and open in the data model; D-23 is not carried out until the DDL changes.
- **Verdict labels.** 3c ends READY WITH LOGGED ITEMS while A, B and D end NOT READY. The label of one slice describes the edits of its own six logs, not the whole (FINAL-2 made the same point); 3c itself holds two majors (3c-1, 3c-4) that fail an implementation.
- **Key and invite states.** 3a and 3d reach the same defect from two sides (3a-1 and 3d-5, 3a-2 and 3d-6) and neither opened S0 0.8/0.9; they agree with each other, so I merged them, but the canonical value list is unconfirmed (row 2).
- **Closure reasons.** 3b and 3d agree that the nine `closure_reason` values are one list in S0, 05a, 05b and 15a. 3b-1 shows that the exit for the payout guard may still be unreachable, which 3d did not test.

**FINAL-2 rows after round 3** (the 69 rows of `docs/audit/FINAL-2.md`; the slices name the row each time).

- Closed in the text and as far as the slices opened them: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 17, 19, 20 (owner effect remains, row 35 below), 21, 22 (seven files of the candidate list), 23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 37, 39, 42, 43, 44, 45, 46, 47, 48, 50, 52, 53, 54, 55, 56, 59, 60, 62, 63, 65, 66, 69. For 5, `AC-req-75` was not opened; for 42, one residue (row 19 below).
- Closed in a part file and contradicted elsewhere, so open: 13 (DDL, row 4), 64 (05b, row 15), 24 (one check, row 1), 36 (entity table, row 3), 16 (08b, row 16), 57 (13, row 17).
- Open or partly open: 14 (rows 23 and 25 below), 18 (row 14), 25 (row 5), 35 (row 2), 51 (row 22), 61 (row 28), 67 (row 45), 38 (the drift of citations in logs persists, row 51).
- Not assessed by any slice by name: 49 (count in the FIX-07 log) and 68 (cell text pointing to `docs/decisions.md`, an owner action). Rows 40, 41 and 58 are evidenced only by the presence of the R3-05 edits (3a), not by a read-back of the result.

**The four reasons of `docs/audit/FINAL.md` section 5, as 3d judged them and as I judge them after the merge.** Reason 1 (the reconciliation was never applied): not met, because 15a:98-103 contradicts 10a on the challenge model and four 10a operations have no row in 15a 15.5 (rows 11 and 13); 11b, 11c, 12 and 13 were not compared with 15a to 15f by anyone. Reason 2 (the parts disagree on the data model): not met, not partly, because the device hash, the counters, the key and invite states, the tree id and the `devices` DDL still differ (rows 1 to 4, 9, 10, 12). Reason 3 (safety parameters fail open): met for the four ranges 3d read (`retention.ip_hash_ttl_days` 1..30, `appeal.ban_min_reviewers` 2..2, `launch.min_signoffs` 2..5, `launch.min_approved_services` 1..20); the fixed minimum of `security.two_person_actions` disagrees with 10a (row 7) and S16 `service.min_approvers` and `template.min_reviewers_new` still allow 1..5 against 1..2 in the machines (row 28). Reason 4 (owner decisions open): met, D-01 to D-34 are recorded as accepted; I report none of them as open.
