# Audit FINAL: final readiness report

*Cell C-071 (supersedes C-057). Written by a reviewer who did not write any audited part. Sources: the 15 audit logs `docs/audit/A01.md` .. `A15.md`, `spec/02e-issues-summary.md`, `spec/16d-parameter-consistency.md`, `spec/15g-api-consistency.md` and the edit lists of `spec/15c` .. `15f`. This file edits nothing else and softens no log. Line numbers are the ones the logs gave (most are approximate and pre-edit); where a log gave only a section, this file says so and does not invent a line. Nothing here is legal advice and nothing has been checked against any provider's terms or any law.*

## Checked

- All 15 audit logs were read completely (A15 is the merge of its three parts). Counts in section 1 are re-counted from each log's own findings table, not copied from its summary line. Two summary lines disagree with their tables: A03 says 5 logged-cross-part and the table has 6 (findings 26 to 31); A13 says 15 fixed of 23 and the table shows 13 fixed and 10 logged. The table counts are used.
- `spec/02e-issues-summary.md` (185 lines), `spec/15g-api-consistency.md` (284 lines) and `spec/16d-parameter-consistency.md` (289 lines) were read completely.
- Log cell ids are as the logs state them. A02 and A15 do not name their cell; C-043 and C-056 are inferred from the sequence of the dependency list [A].
- Severity: A04 finding 3 carries the severity word `needs-owner`; it is classed `major` here because with one admin no two-person action can run. A06 and A12 list minor items outside their tables; they are counted in section 1 and not individually carried.
- Nothing was executed here. Acceptance scripts are run by CI (see Not verified).

## 1 One row per audit log

| Log | Cell | Files audited | Verdict (as written) | Findings | Fixed | Logged cross-part | Logged needs-owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A01 | C-042 | `spec/06a-ledger.md` | READY WITH LOGGED ITEMS | 23 | 16 | 3 | 4 |
| A02 | C-043 [A] | `spec/06b-admission.md` | READY WITH LOGGED ITEMS | 28 | 22 | 4 | 2 |
| A03 | C-044 | `spec/14-launch-gates.md`, `spec/07-policy.md` | READY WITH LOGGED ITEMS | 32 | 25 | 6 | 1 |
| A04 | C-045 | `spec/10a-identity.md`, `spec/10b-safety.md` | READY WITH LOGGED ITEMS | 21 | 13 | 6 | 2 |
| A05 | C-046 | `spec/05a-entities.md` | READY WITH LOGGED ITEMS | 29 | 14 | 12 | 3 |
| A06 | C-047 | `spec/05b-state-machines.md`, `spec/09-result-return.md` | READY WITH LOGGED ITEMS | 32 (+8 untabled minor) | 25 | 4 | 3 |
| A07 | C-048 | `spec/04-architecture.md`, `spec/17-build-plan.md` | READY WITH LOGGED ITEMS | 23 | 21 | 0 | 2 |
| A08 | C-049 | `spec/08a-templates.md`, `spec/08b-verification.md` | READY WITH LOGGED ITEMS | 16 | 12 | 3 | 1 |
| A09 | C-050 | `spec/11a-volunteer-ux.md`, `spec/11d-i18n-copy.md` | READY WITH LOGGED ITEMS | 38 | 25 | 7 | 6 |
| A10 | C-051 | `spec/11b-requester-ux.md`, `spec/11c-admin-tools.md` | READY WITH LOGGED ITEMS | 17 | 9 | 6 | 2 |
| A11 | C-052 | `spec/12-public-growth.md`, `spec/13-measurement.md` | READY WITH LOGGED ITEMS | 16 | 7 | 4 | 5 |
| A12 | C-053 | `spec/15a-api-core.md`, `spec/15b-api-admin.md` | READY WITH LOGGED ITEMS | 29 (+6 untabled minor) | 24 | 3 | 2 |
| A13 | C-054 | `spec/16-parameters.md`, `19-risks.md`, `01-purpose.md`, `03-assumptions.md`, `20-glossary.md`, `21-persian-summary.md` | READY WITH LOGGED ITEMS | 23 | 13 | 8 | 2 |
| A14 | C-055 | `spec/18-testing.md`, `spec/02-issues.md` | READY WITH LOGGED ITEMS | 20 | 17 | 3 | 0 |
| A15 | C-056 [A] | `spec/00-conventions.md`, `spec/00-decisions.md` | READY WITH LOGGED ITEMS | 50 (+11 untabled minor) | 30 | 17 | 3 |
| **Total** | | 31 files | all 15: READY WITH LOGGED ITEMS | **397** (+25 untabled) | **273** | **86** | **38** |

Reading the table. 273 of 397 tabled findings were fixed in place (69 percent); 124 were only logged (86 cross-part, 38 needs-owner). No blocking finding is left unfixed: the five blocking findings (A03 findings 1 to 4 and A05 finding 1, and no other) were all fixed. The 25 untabled minor items (A06 8, A12 6, A15 11) were fixed by nobody. Every log ends with the same verdict, so the per-part verdicts say nothing about whether the parts agree with each other; that is what sections 2 and 3 are about. Files with no audit log: `spec/02b..02d`, `02f` (registers), `spec/15c..15g`, `spec/16b..16d` (reconciliation files, inputs here), and any S5 to S16 file not named above.

## Findings

Every blocking or major finding that is not fixed, as the logs report it. No blocking finding is open in the logs. Rows 1 to 44 are logged findings with the logging cell in square brackets; rows 45 to 47 are the register-level blocking and major items that no part edit has closed (from `spec/02e-issues-summary.md`, cell C-060). `file:line` is the log's own location; "no line" means the log gave a section or a pair of files only.

| # | severity | file:line | defect | action |
| --- | --- | --- | --- | --- |
| 1 | major | spec/06a-ledger.md:316 | [A01 / C-042 #6] Reversal of `levy`, `refund` and `escrow_hold` mirrors into the original escrow, which can be closed; credit into a closed escrow breaks INV-L04 and INV-L07 and "escrow accounts never reopen". Owner: restitution to the requester, or `STATE_CONFLICT` for closed escrows | logged-needs-owner |
| 2 | major | spec/06b-admission.md:162 | [A02 / C-043 #9] S0 0.10.6 default formula of `mint.monthly_cap_credits` uses (1 - 0.5); S6 must read the redeemable key instead of the Commons key. Same defect as 16d F-02 and 02e A17/A18 | logged-cross-part |
| 3 | major | spec/06b-admission.md:338 | [A02 #24] A waiting entry blocked by the global scope does not block other categories, so a large early job can starve behind small jobs elsewhere; rule choice is the owner's (open decision 8) | logged-needs-owner |
| 4 | major | spec/14-launch-gates.md:610 | [A03 / C-044 #26] File cites `ISS-141`, `ISS-143`, `ISS-144`, `ISS-147` but has no `## Issues raised` table (S0.4 requires one); `ISS-144` has no stated content. 02e confirms the four ids have no register row | logged-cross-part |
| 5 | major | spec/00-conventions.md:703 | [A03 #27] `launch.min_signoffs` validation is 1..5 (should be 2..5), `launch.min_approved_services` is 0..20 (should be 1..20), and `security.two_person_actions` can drop `launch.signoff` and `killswitch.release`. S14 defends in code only; 16d CR-23 protects `parameter.loosen` only | logged-cross-part |
| 6 | major | spec/14-launch-gates.md:330 | [A03 #32] Who the two admins are, how a second admin is vetted and how the first admin is bootstrapped are owner decisions; until they are made no gate can be signed | logged-needs-owner |
| 7 | major | spec/10a-identity.md:424 | [A04 / C-045 #3] With one admin, `launch.signoff`, `ledger.reversal`, `member.ban` and the other two-person actions cannot run (no bypass by design, ISS-102). Whether to have a second independent admin before Phase 1 is the owner's | logged-needs-owner |
| 8 | major | spec/05a-entities.md:270-340 (vs spec/10a-identity.md:337) | [A04 #6] 05a Member and Invite hold the invite edge permanently with no clearing rule; column and enum names differ from 10a (`invite_id`, `issuer_member_id` against `invited_by_member_id`, `inviter_member_id`) | logged-cross-part |
| 9 | major | spec/05a-entities.md:330-345 | [A04 #15] 05a Device stores an HMAC token hash of 256 bits with retention `short` and `creation_ip_hash` (+ expiry) in the relational table; 10a 10.14.2 item 2 and 10b AC-safety-01 say IP hashes live only in a volatile counter store, never in the database or backups. Direct contradiction on the most safety-critical datum | logged-cross-part |
| 10 | major | spec/10a-identity.md:1-776 (vs spec/10b-safety.md:1-701) | [A04 #18] Heading numbers collide: 10a owns `10.1`..`10.19`, 10b also uses `10.11`..`10.19`; references such as S10.13 are ambiguous (02e B4) | logged-cross-part |
| 11 | major | spec/10a-identity.md (no line) vs spec/10b-safety.md vs spec/05a-entities.md | [A04 #19] Name mismatches: `secret.email_enc_key` / `secret.email_encryption_key`, `secret.email_index_key` / `secret.email_lookup_key`; `MemberKey` `kind`/`state` against `purpose`/`status` with different values; `AdminUser`, `AdminCredential`, `Session`, `AdminAction` states and columns. `g1.secrets_inventory_complete` cannot pass until one set is chosen | logged-cross-part |
| 12 | major | spec/05a-entities.md (5.3.2) vs spec/10b-safety.md:205 | [A04 #20] 05a computes `vol_` on read for public pages; 10b says public surfaces are aggregates and handles are never shown to members or visitors | logged-cross-part |
| 13 | major | spec/05a-entities.md (S5.8.2, no line) vs spec/05b-state-machines.md S5.23.3 | [A05 / C-046 #15] `Lease` has no `hard_expires_at`, `extensions` (05a: `extensions_used`) or `release_reason`; 05b defines submit validity, re-lease and the reaper on `hard_expires_at`, so the 05a reaper index on `expires_at` is wrong for it | logged-cross-part |
| 14 | major | spec/05a-entities.md (S5.7.5, S5.8.1, no line) | [A05 #16] 05b uses Job `pause_causes`, `state_before_pause`, `pause_started_at`, `paused_total_s`, `held_ucr`, `levy_reserved_ucr`, `quote_id`, Cell `acceptance_deferred_until` and `closure_reason` `cells_exhausted`, none in 05a or S0.9.2 | logged-cross-part |
| 15 | major | spec/05a-entities.md (S5.9.2, S5.9.3, no line) | [A05 #17] 05b states `ledger_transactions.idempotency_key` and `ledger_entries.entry_key` UNIQUE; 05a names the transaction key `natural_key` and has no `entry_key` | logged-cross-part |
| 16 | major | spec/05a-entities.md (S5.4, no line) | [A05 #18] 05b adds entity `StateTransition` (`state_transitions`, `stt_`) and a mint-headroom store (`mint_headroom`) that appear neither in S0.7 nor in 05a; monthly mint-cap accounting has no table | logged-cross-part |
| 17 | major | spec/05a-entities.md (S5.6.10, S5.12.3, S5.10.6, S5.13.6, no line) | [A05 #19] Tables classed `permanent` and append-only hold free text that can name a member or tester (`admin_actions.reason`, `kill_switches.reason`, `flag_answers.evidence_note`, `calibration_records.note`), while S0.7 defines `permanent` as no personal data by construction | logged-needs-owner |
| 18 | major | spec/05b-state-machines.md:279 | [A06 / C-047 #27] S0.9.6 has no `suspended` to `in_review` and no `in_review` to `revoked`; a re-review that ends `rejected` pauses no pinned job and applies no `inflight_policy`. 05b added SVT-02 as a convention addition; S0.9.6 itself is unedited | logged-cross-part |
| 19 | major | spec/05b-state-machines.md:97 | [A06 #28] A Commons job has no overrun deadline and a `flagged_for_audit` cell whose audit cell is never executed has no age-out: cell, mint-headroom reservation and job stay open indefinitely | logged-needs-owner |
| 20 | major | spec/05b-state-machines.md:233 | [A06 #31] MT-06 restricts a member on "an anomaly finding of S9.*" with no count or window; one hard duplicate or timing hit could restrict an honest donor; untestable | logged-needs-owner |
| 21 | major | spec/05b-state-machines.md (~SBT-06) and spec/09-result-return.md:392 | [A06 #32] 09 returns a released submission to verification; S0.9.3 and SBT-06 move `quarantined` to `checks_passed` ("no check remains") | logged-cross-part |
| 22 | major | spec/04-architecture.md:566 | [A07 / C-048 #5] The automatic brake on an invariant violation engages only `kill.all_minting` and `kill.all_new_jobs`; payout, settle, expire, grant and retire postings continue on a ledger whose integrity check just failed | logged-needs-owner |
| 23 | major | spec/08b-verification.md:462 | [A08 / C-049 #13] 8.31 excludes Commons cells from member-job v; 06a 6.11.2 counts Commons and member cells of one job type together and publishes `v_commons` and `v_member` separately | logged-cross-part |
| 24 | major | spec/08b-verification.md:511 | [A08 #14] 8.32 says mandatory verification events are never skipped for budget; 06a LD-05 says the scheduler may not create a verification cell the budgets cannot pay (shortfall path open, ISS-85). 02e A2: the register (ISS-16) wins, so 06a, `AC-ledger-03`, `T-unit-01` and 8.32 must change | logged-cross-part |
| 25 | major | spec/11a-volunteer-ux.md:1380 | [A09 / C-050 #26] ISS-113 (recovery key shown after the first accepted cell, not at join) is `needs_owner`; 11a and 11d now agree but the owner has not decided | logged-needs-owner |
| 26 | major | spec/11d-i18n-copy.md:565 | [A09 #27] Join consent: 11d requires every notice in full plus eight unticked boxes (S11.51.F, S11.52, AC-i18n-36); 11a F2/F3 specify one three-fact notice, no checkbox wall, 10 s budget, identity created at Start. Both cannot hold; the sub-60-second path and informed consent (FD 9) conflict | logged-cross-part |
| 27 | major | spec/11b-requester-ux.md:~15 and spec/11c-admin-tools.md:~7 | [A10 / C-051 #10] Both number sub-sections from 11.41 (11b spans 11.31..11.49, 11c 11.41..11.59), so 11.41..11.49 exist twice; 02e B4 adds 11d as a third owner | logged-cross-part |
| 28 | major | spec/11b-requester-ux.md:~860 | [A10 #11] Requester rejection copy has two owners: `copy.policy.<rule>.<slug>` (07 7.4.3) against `copy.req.reason_r1..r7` (11b) with different wording and no `details.sub_code` hints | logged-cross-part |
| 29 | major | spec/11b-requester-ux.md:~213, ~560 vs spec/11c-admin-tools.md:~520 | [A10 #13] 11b shows a job pause caused by a kill switch (`copy.req.pause_kill`, AC-req-43); 11c pauses jobs only for `kill.template.<id>` and `kill.service.<id>`, and 11b omits `kill.member.<mem_id>` | logged-cross-part |
| 30 | major | spec/12-public-growth.md:484-520 (12.16 AC-exp-01..08) | [A11 / C-052 #2] A11 finding 1 is marked fixed only by a precedence rule: S12.11.3 and AC-exp-01..08 still describe counter-based blocks and `experiment.assigned`, S13.8 the `ExperimentBlock` form; S0 and S5 must carry one Experiment state list | logged-cross-part |
| 31 | major | spec/12-public-growth.md:618 | [A11 #4] V2 primary metric `day7_return` and the other `hamyar_growth_*` keys (V1, V3, V5, V6) have no S13 definition, so FD 9 Phase 2 measures are unspecified | logged-cross-part |
| 32 | major | spec/12-public-growth.md:86 | [A11 #5] The live headline counter counts `primary` and `rework` only; a donor can see her own hidden gold or audit cell leave it flat. Residual disclosed, not closed | logged-needs-owner |
| 33 | major | spec/12-public-growth.md:140 | [A11 #6] Consecutive daily `cumulative_mint_ucr` and `reserve_ucr` checkpoints can be subtracted to recover a small group's daily flow; disclosure added, leak not closed | logged-needs-owner |
| 34 | major | spec/12-public-growth.md:343 | [A11 #7] `team.min_public_members` 5 is below `analytics.min_cohort_k` 10: a listed team publishes totals over fewer than k members. 16d F-10 and CR-08 propose 10 | logged-needs-owner |
| 35 | major | spec/15a-api-core.md:600 (vs spec/15b-api-admin.md:1030) | [A12 / C-053 #25] Share cards contradict: 15a returns a computed card with no stored link; 15b creates stored, revocable, token-addressed public cards with a view counter. 15g G-02 picks 15a (CR-03 deletes 15b 15.33.5) but part 12's owner decides | logged-needs-owner |
| 36 | major | spec/15a-api-core.md:518 | [A12 #26] Results, deliverable and manifest exist only for `completed` and `failed` jobs; a `cancelled` job paid for accepted cells but the requester cannot retrieve them (ISS-115 default: partial `Deliverable`) | logged-needs-owner |
| 37 | major | spec/15b-api-admin.md:773 and :1090 | [A12 #27] No member inbox or notice operation exists in any S15 file read, although suspension, ban, policy-rejection and appeal outcomes depend on one (`inbox_proj` has no read endpoint) | logged-cross-part |
| 38 | major | spec/15a-api-core.md:20 | [A12 #28] Member-facing appeal operations (file, list, withdraw) are said to live in the sibling file; 15b has none. 15g shows `createAppeal`, `listAppeals`, `getAppeal` only in overlay 15d | logged-cross-part |
| 39 | major | spec/15a-api-core.md:900 | [A12 #29] 13 parameter names absent from S0 0.10.6 and not confirmed elsewhere (`identity.challenge_ttl_s`, `session.max_active_per_member`, `ratelimit.write_weight`, `ratelimit.member_uploads_per_hour`, `api.deprecation_window_days`, `invite.required_to_join`; in 15b `ratelimit.admin_write_cost`, `ratelimit.admin_auth_attempts_per_hour`, `ratelimit.public_verify_cost`, `session.admin_stepup_ttl_s`, `security.approval_ttl_s`, `launch.require_locked_preregistration`, `growth.share_card_max_active`) | logged-cross-part |
| 40 | major | spec/19-risks.md:301-304 and spec/03-assumptions.md:16-28 | [A13 / C-054 #2] Id series `OD-01`..`OD-12` (S19) and `OD-01`..`OD-13` (S3) collide with different meanings (OD-05 counsel against Commons backlog; OD-03 on-call against hosting); 02e B5 repeats it | logged-cross-part |
| 41 | major | spec/16-parameters.md:437-447 and spec/19-risks.md:110-111 | [A13 #6] TRIP-10, TRIP-11 and TRIP-15 name thresholds locked in the PreRegistration, but 16.15 lists no seed and no `thr.*` key for them | logged-cross-part |
| 42 | major | spec/00-conventions.md:432 | [A15 / C-056 #25] The Submission machine gives states and events but no transitions: targets of `submission.quarantined`, `submission.released_from_quarantine`, `submission.rejected` unstated; `checks_failed` and `rejected` (both T) not told apart; cell state during quarantine undefined | logged-cross-part |
| 43 | major | spec/00-conventions.md:427, 487-496 | [A15 #26] `appeal.overturned` has no named effect for four of six `appeal_kind` values (`cell_rejection`, `job_rejection`, `template_rejection`, `report_outcome`); remedy needs a decision (02e A4: ISS-56 `needs_owner`, `appeal_restitution` stays off) | logged-needs-owner |
| 44 | major | spec/00-conventions.md:460-461, 475-476, 494 | [A15 #29] Approval-count parameters allow 1..5 approvers (`template.min_reviewers_new`, `service.min_approvers`, `appeal.ban_min_reviewers`) while the machines model one second-review step; cap the ranges in 0.10.6 or add a counting rule | logged-cross-part |
| 45 | blocking | spec/02-issues.md (ISS-12 row, no line) | [02e 2.E.1, 2.E.2 A1 / C-060] `ISS-12` (severity blocking, status `proposed`, owner decision `OD-08`): the platform never executes submitted content. `ISS-41`, `ISS-81`, `ISS-91` still allow an isolated runner, and the flag has two names (`ff.verify.sandboxed_tests` in S4, `ff.template.code_change_sandbox` in S8a); 02e says S4, S8a and S9 must drop the runner and `test_run`. Whether they did is checked in section 3 | logged-needs-owner |
| 46 | blocking | spec/02-issues.md (ISS-11 row, no line) | [02e 2.E.1 / C-060] `ISS-11` (severity blocking, status `proposed`, turns on `OD-04`): only `commons_capable` services count toward minting and `launch.min_approved_services`; three predicates for an approved service coexist (02e A8: ISS-11, ISS-23, ISS-71, ISS-72, ISS-77) | logged-needs-owner |
| 47 | major | spec/06a-ledger.md, spec/06b-admission.md, spec/08b-verification.md, spec/18-testing.md (no lines) | [02e A2, A3 / C-060] Who pays when verification costs more than the pool: ISS-16 (hard pool, job stops), ISS-61 (draw on the levy) and ISS-85 (c) disagree; the quote basis of the pool before any measurement exists is undefined (ISS-16 floors against ISS-85 v_prior). The register wins but its claim is called doubtful in 02e | logged-needs-owner |

## 3 Reconciliation edits that are not yet applied in the part files

The edit lists of `spec/15c` to `15f` ("Edits required in citing parts"), the `## Corrections required` of `spec/15g` (CR-01 to CR-09 and CR-11 to CR-44; the file defines no CR-10) and of `spec/16d` (CR-01 to CR-25) all say a later cell applies them. Each was checked by reading the cited line (or the nearest lines, where the file had drifted) in the part file, on the branch of this cell (main plus nothing). Status words: **NOT APPLIED** (the old text the edit names is still there); **APPLIED** (the new text is there); **PARTLY CLOSED** (an audit log reports a fix of the same defect, or one side of a two-sided edit is done; not re-read here beyond the stated lines); **NOT LOCATED** (the cited line is not within a few lines of where it was; the status is unknown); **NOT CHECKED** (not read in this cell). For the verdict, NOT LOCATED and NOT CHECKED count as not applied: no reader has seen them applied.

| Source | Edits listed | Checked and NOT APPLIED | APPLIED or PARTLY CLOSED | NOT LOCATED or NOT CHECKED |
| --- | --- | --- | --- | --- |
| `15c` (27 edits) | 27 | 19 | 0 | 8 |
| `15d` (list read from line 400 of 460 only) | not counted | 8 (`11b:147` to `11b:151`, `12:29`, `12:35`, `12:38`) | 0 | the rest of the list: `12:466`, `12:511`, the 12.9.2 rows, the 11b rows and screen prose before `11b:147` |
| `15e` (list read from line 285 of 332 only) | not counted | 17 (`11c:502` to `11c:509`, `11c:647` to `11c:652`, `11c:700`, `11c:701`, `13:921`) | 0 | the rest: `11c:266`, `457` to `461`, `555`, `557`, `615`, `751`, `752`, `793` to `801`, the `AC-*` rows |
| `15f` (15 edits E1 to E15) | 15 | 7 (E5, E6, E9, E10, E11, E12, E13) | 0 | 8 (E1 to E4, E7, E8, E14, E15) |
| `15g` (43 CR ids) | 43 | 7 | 6 | 30 |
| `16d` (25 CRs) | 25 | 6 | 3 | 16 |

Result. 64 individual edits were checked at the cited place and found unapplied; none was found applied as written; 9 are partly closed by audit fixes. At least 67 listed edits were not located or not checked, plus the unread parts of the `15d`, `15e` and `15f` lists. The reconciliation work is therefore not applied: the part files still cite paths, operation ids, permission names, field names and parameter ranges that S15 and S16 define differently. `scripts/check_refs.py api` cannot show this: `15g` (hand-off 15d O12, accepted there as a known limit) says the script counts a path as defined if it appears anywhere in `spec/15*.md`, including the overlay text of `15c` to `15g` itself. A green `check_refs` is therefore not evidence that citing parts and API files agree.

### 3.1 `15c` edit list (27 edits)

| # | Where | Status and what was seen |
| --- | --- | --- |
| 1 | `10a:62-69` challenge shape and purposes | NOT APPLIED: still `challenge_id \|\| nonce`, the 13 purpose names and `POST /v1/auth-challenges` |
| 2 | `10a:79` registration | NOT APPLIED: still `POST /v1/auth-challenges {purpose: 'register_device'}` |
| 3 | `10a:228`, `10a:712` recovery | NOT APPLIED at 228 (`POST /v1/auth-challenges {purpose: 'recover'}`); 712 not read |
| 4 | `10a:479-480` admin sign-in | NOT APPLIED: `POST /v1/admin/auth-challenges`, `POST /v1/admin/sessions {assertion}` |
| 5 | `10a:727` admin ops table | NOT APPLIED: `createAdminAuthChallenge` row present |
| 6 | `10a:728`, 10.18.2 events | NOT APPLIED: `createAdminAction`, `createAdminActionApproval`, `admin_action.proposed` present |
| 7 | `10a:194-195`, `722` device-link offer | NOT APPLIED: `POST /v1/device-link-offers`, `{offer_id, link_secret` present |
| 8 | `10a:199`, `205`, `723` claim and approval | NOT APPLIED: `/v1/device-link-offers/{offer_id}/claims` present |
| 9 | `10a:222` | NOT CHECKED at 222; the same path `GET /v1/members/me/keys` remains in the 10.18.1 table |
| 10 | `10a:167` key rotation | NOT APPLIED: `POST /v1/members/me/keys {device_pub...` |
| 11 | `10a:718` | NOT APPLIED: `createMemberKey` row present |
| 12 | `10a:719` | NOT APPLIED: `createKeyRevocation` row present |
| 13 | `10a:720` | NOT APPLIED: `createRecoveryKey` row present |
| 14 | `10a:138-139` recovery key effect | NOT APPLIED: "New key `active` and unconfirmed; old key `retiring`" present |
| 15 | `07:1065` | NOT APPLIED: `getOptIns`, `setOptIns` `PUT /v1/me/opt-ins` present |
| 16 | `07:1062` | NOT APPLIED: `previewPolicy` `POST /v1/policy-previews` present |
| 17 | `07:1070` | NOT LOCATED: no `getSupplyGauge` row in `07:1058-1072` |
| 18 | `06b:523` | NOT LOCATED: `confirmJobQuote` row not in `06b:519-531` |
| 19 | `10a:78`, `110`, `114`, `578`, `62` labels | NOT APPLIED at 78, 110 and 62 (`hamyar/v1/...` still used); 114 and 578 not read |
| 20 | `07:1063` | NOT APPLIED: `getCurrentPolicy` `GET /v1/policy` present |
| 21 | `11b:120` | NOT APPLIED: `getPolicyProfile` `GET /v1/policy-versions/current` present |
| 22 | `06b:173` | NOT APPLIED: `shows "<k" for both counts` present |
| 23 | `06b:524` | NOT LOCATED |
| 24 | `04:583` | NOT LOCATED: text not in `04:578-588` |
| 25 | 15b 15.33.1 rule 9 | NOT CHECKED (A12 finding 24 reworded the health references) |
| 26 | `10a:592` | NOT CHECKED |
| 27 | wherever cited (lease extension, nonce, validations, approvals paths) | NOT CHECKED |

### 3.2 `15d`, `15e`, `15f` rows that were checked

| Source | Cited place | Status |
| --- | --- | --- |
| 15d | `11b:147` `getDeliverable`, `148` `downloadDeliverableFile`, `149` `getManifest`, `150` `createJobRating`/`getJobRating`, `151` `createAppeal`/`getAppeal` | NOT APPLIED: all five rows unchanged |
| 15d | `12:29` public ledger row, `12:35` `getShareCardPayload`, `12:38` `listEffectiveFlags` / `GET /v1/flags` | NOT APPLIED: all three rows unchanged |
| 15e | `11c:502` to `509` ledger rows (`ledger-accounts`, `ledger-entries`, `ledger-transactions`, `credit-lots`, `invariant-checks`, `ledger-verifications`, `ledger-checkpoints`, `createLedgerReversal` with `ApprovalRequest`) | NOT APPLIED: eight rows unchanged |
| 15e | `11c:647` to `652` launch rows (`launch-gates`, `launch-gate-items`, `createLaunchSignoff`, `createLaunchSwitchOff`, `launch-status`) | NOT APPLIED: six rows unchanged |
| 15e | `11c:700`, `701` kill-switch engagement and release | NOT APPLIED: `/v1/admin/kill-switch-engagements` still defined |
| 15e, 15g CR-12 | cited `13:921`, found at `13:924` | NOT APPLIED: `perm.metrics.view_small_cells` still named, against 15e's decision that it does not exist |
| 15f | E5 (`approvePreRegistrationLock`), E6 (`getPreRegistrationProof`), E9, E10 (`perm.experiment.manage`), E11, E12 (`getCalibrationStatistics`), E13 | NOT APPLIED: unchanged (cited `13:923-932`, now `13:926-935`) |

### 3.3 `15g` corrections (43 ids)

| CR ids | File and place | Change | Status |
| --- | --- | --- | --- |
| CR-01, CR-02 | S0 0.5; 15b 15.23.1, 15.24, 15.29.2, 15.29.3, 15.30.1; 11b, 11c, 13, 15d, 15e | admin duplicates of 11 ids take the suffix `Admin` | NOT APPLIED, and a different rule is in force: `15b:17-24` (A12 finding 15) prefixes `admin` in the OpenAPI key (`adminListServices`). Two collision rules now exist (decision D-08 below) |
| CR-03 | 15b 15.33.5, 15.33.2, 15.34.4, `AC-public-05` | delete the stored share cards | NOT APPLIED: A12 finding 25 still logs the contradiction; depends on D-15 |
| CR-04, CR-05 | 15a 15.4; 15b 15.21.1, 15.22.1; S0 0.11.2 | `wrong_scheme` rule, four admin bootstrap exceptions, `AC-auth-01..03` | NOT CHECKED |
| CR-06, CR-07 | 15b 15.21.3 rule 4, 15.22.4 | `X` on four login operations, admin idempotency scope, no secret in `AdminApproval.result` | PARTLY CLOSED: A12 finding 17 (enrollment code no longer stored in the result) and 21 (`createStepUpChallenge` key); the rest NOT CHECKED |
| CR-08 | 15a 15.9 | add reasons and `details` keys of ER-01..ER-11 | NOT CHECKED |
| CR-09, CR-34 | S0 0.9; 15b 15.34 | add events EV-01..EV-12 and `job.cancelled` | PARTLY CLOSED: A12 finding 18 added 15.34.6 for eleven part-a events; EV-05 to EV-07 and `job.cancelled` NOT CHECKED |
| CR-11 | 15b 15.32.1, 15.32.2 | `content_hash`, `lock_pending`, status `registered` | NOT CHECKED |
| CR-12 | 15e 15.D.4.6, 15f, `13:921` | one `listMetricSnapshots`, no small-cell permission | NOT APPLIED (cited `13:921`, now `13:924`) |
| CR-13 | 15f, part 13 | drop `ui.variant_exposed`; exposure via `recordExperimentExposure`; `preregistration.locked`; `calibration-proposals` | NOT APPLIED for `calibration-proposals` (cited `13:931`, now `13:934`, unchanged); rest NOT CHECKED |
| CR-14 | 15d row 17, `11b:120` | use `getPublicPolicy` | NOT APPLIED (`11b:120`) |
| CR-15, CR-16, CR-19, CR-36, CR-37 | 15a 15.3, 15.7.3, 15.8 | unknown query parameters, `createReport` subjects, `client_events_enabled`, `Job.rating`, `Team.score` | NOT CHECKED |
| CR-17, CR-18, CR-42, CR-43 | 15b | `lockTeam`, `unlockTeam`, `AdminAction` hashes, member-read `context_id`, `perm.claim.takeover` | NOT CHECKED |
| CR-20, CR-21 | 15b 15.27.1, 15.27.2 | S14 fields on evidence and sign-off; chunked evidence upload | NOT CHECKED |
| CR-22 | 15b 15.27.3, 15.28.3 | `changeLaunchSwitch` uses `evaluate_switch`, authorization, cascade | NOT CHECKED |
| CR-23 | S14.7 | three S15b-only blockers | NOT CHECKED |
| CR-24 | 15b 15.23.4, 15.27.2 | `approvalGuard` flags, `reopenGateItem` to `review_due` | NOT CHECKED |
| CR-25 | S14.9, `AC-launch-52`; 15a 15.9 | member-key refusal is `FORBIDDEN` `account_frozen` | NOT APPLIED on the S14 side (`14:623` still lists only `LAUNCH_GATE_CLOSED` or `KILL_SWITCH_ENGAGED`); 15a side closed by A12 finding 6 |
| CR-26 | S0 `KillSwitch.reason_code`; S14.4.5 | add `legal_hold`; map reason codes | NOT CHECKED |
| CR-27 | 15b 15.28.1 | delete "grants that mint" | NOT CHECKED |
| CR-28 | 15a 15.7.2, 15.7.4; S14.9 | gates on `createJob`, `submitJobForScreening`, `createReservation`, `confirmJob` | PARTLY CLOSED: A12 finding 4 added a gate matrix to 15a 15.4 and `createReservation` gates; S14.9 and `AC-api-18` NOT CHECKED |
| CR-29, CR-33 | 15a 15.6.2, 15.6.4 | lease and acceptance gates; held mint leaves `pending` | NOT CHECKED |
| CR-30 | 15a 15.10 | `R` and `O` rows | PARTLY CLOSED: A12 finding 3 fixed `joinTeam`, `revokeReferral` and added `deleteUpload`, `expandLeasePrompt`, `checkJobPolicy`; `revokeInvite`, `checkInvite`, IG-09, IG-10 NOT CHECKED |
| CR-31 | 15a 15.12 | `RL-PUB` equals `PUB` | NOT CHECKED |
| CR-32 | 15b 15.33.1 rule 9, rule 6, 15.21.4 | `GET /v1/public/health` | NOT CHECKED |
| CR-35 | 15b 15.29.2, 15.34.3 | `job_svc` consumes `appeal.overturned` | NOT CHECKED |
| CR-38, CR-39 | 15b `createCalibrationRecord`, `MetricSnapshot` | optional fields; bundle is a snapshot kind | NOT CHECKED |
| CR-40, CR-41 | S14.9.2 | drop invite redemption from "admit"; name the Commons authoring path | NOT CHECKED |
| CR-44 | S0 0.8.2, S10 matrix | permission mapping S14 to S15b | NOT CHECKED |

### 3.4 `16d` corrections (25)

| CR | File and place | Status |
| --- | --- | --- |
| CR-01 | `16-parameters.md` 16.15 eta label | NOT APPLIED: "Minimum eta (Reserve inflow versus spend)" unchanged (`16-parameters.md:438`) |
| CR-02 | `C13`, mint cap rows, S0 Table A | NOT APPLIED: `C13` still multiplies `admission.phi_ppm` (`16-parameters.md:92`); A13 finding 1 fixed the divisor only |
| CR-03 | `admission.min_window_s`, `admission.window_step_s` ranges | PARTLY CLOSED: min window now `> 0` (A13 finding 13); the step range `1..86,400` and the lower bound at the step are not applied (`16-parameters.md:180-182`) |
| CR-04 | `retention.ip_hash_ttl_days` `0..30` to `1..30` | NOT APPLIED (`16-parameters.md:313`) |
| CR-05 | `C2` gold floor `> 0` | NOT APPLIED (`16-parameters.md:78`: only the audit floor) |
| CR-06 | `change.notice_days_default`, `change.notice_days_price` `0..90` to `1..90` | NOT APPLIED (`16-parameters.md:391-392`) |
| CR-07 | `change.notice_days_price` text adds `reservation.*` | APPLIED in S16 (`16-parameters.md:392`); S0 Table A row NOT CHECKED |
| CR-08 | `team.min_public_members` 5 to 10 | NOT APPLIED in S0 Table C (`00-conventions.md:776`); S16 16.14 row NOT CHECKED; owner decision D-13 |
| CR-20 | S14 text at 14:600 and 14:603 | PARTLY CLOSED: `calibration.min_samples_per_service` 20 to 30 fixed by A03 finding 20; the secret-rotation name is still logged (A03 finding 29) |
| CR-09 to CR-19, CR-21 to CR-25 | S, P, B, C (see the table in `16d`) | NOT CHECKED (16 CRs) |

Two parameter ranges that A03 finding 27 asked to correct are also still open on main: `launch.min_signoffs` is `1..5` and `launch.min_approved_services` is `0..20` in both `00-conventions.md:762-763` and `16-parameters.md:389-390`. S14 enforces the floors in code only (A03 findings 8, 9); the parameter definitions still allow a launch with one sign-off and with no approved service.

### 3.5 `02e` register conflicts

`spec/02e-issues-summary.md` (C-060) lists 18 conflicts of substance (A1 to A18) and 8 clashes of names (B1 to B8) and edits nothing; its 2.E.5 hands the part edits to later audit cells. This cell could not re-check them against S4, S5b, S6a, S6b, S7, S8a, S8b, S9, S11 and S15a. The audit logs show: A7 (K and the cap rule, `T-prop-16`) closed by A14 finding 2; A2 (who pays when verification outruns the pool) still open (A08 finding 14, section 2 rows 24 and 47); B4 (heading and id collisions) still open (rows 10 and 27); B5 (`OD` ids) still open (row 40); B7 (alias parameter names such as `ui.first_load_budget_bytes`) closed in part by A09 finding 5; every other row NOT CHECKED. Nothing in `02e` was found applied.

## 4 Owner-only decisions

One list, merged from the 40 lines of `spec/02e-issues-summary.md` 2.E.3, the `logged-needs-owner` findings of the 15 logs (38) and the founders' decisions named in `spec/16d-parameter-consistency.md` (F-03, F-04, F-10, F-12, F-13, F-17). Each line gives the default the spec uses meanwhile. Until the owner decides, the default stands and nothing below may be read as decided. `02e` counts 23 of its 39 `needs_owner` rows as absent from S3.2 (`no`) and 9 as `partly` present; the S3.2 rows to add are in `02e` 2.E.3.

| # | Decision | Source ids | Default meanwhile | Blocks |
| --- | --- | --- | --- | --- |
| D-01 | How many independent admins and reviewers exist in Phase 1, who they are, how the first admin is bootstrapped, whether `launch.min_signoffs` may be 1, who acts for `founders`-owned parameters | ISS-82, ISS-102, ISS-119 (11c) (a),(b),(d),(e), ISS-168, ISS-196, ISS-16110; A03 #32, #27; A04 #3; A15 #48 | Two-person actions unavailable below two admins; numbers not lowered; no gate can be signed with one admin | every sign-off, ledger reversal, ban |
| D-02 | Seed the Reserve before the pilot or start with grants paused; the seed size | ISS-19, 16d F-13 | Reserve starts empty, grants pause; 16d proposes at least 150 credits (3 x pilot of 50) as a launch precondition [V] | `launch.members_may_join` |
| D-03 | Restitution for an overturned rejection or ban, and whether the Reserve may pay anything beyond starter grants; reversal into a closed escrow; whether an expired escrow slice pays donors; whether the levy follows an overturn; whether a transferred lot restarts the E-day clock | ISS-56, ISS-76, ISS-85 (d), ISS-119 (11c) (c); A01 #6, #18, #20, #23; A15 #26 | Reserve pays nothing beyond grants; `appeal_restitution` stays off; the donor bears the gap (02e A4, A6) | BM7 acceptance |
| D-04 | Verification cost beyond the pool: quote basis before any measurement, high-risk templates, appeals, shortfalls | ISS-16, ISS-61, ISS-85; A02; A08 #14; 02e A2, A3 | Hard pool, the job stops (ISS-16); quote at max(measured v, `price.v_prior`, floor) [A] | BM7 acceptance |
| D-05 | Whether credit held in escrow counts toward K and keeps ageing; reservations against the 14-day accelerated arm; where the large-job trial takes its jobs | A06 #26; 16d F-03, F-17, S16D-C3 | Escrow counts toward K (ISS-18); `ff.job.reservations` stays off for the arm; trial jobs from the standard arm [H] | arm design before the pre-registration lock |
| D-06 | K against `price.v_cap` and the new-member cap multiplier: K = 500, or `admission.max_job_cells` = 200, or accept `CAP_EXCEEDED` with the largest holdable job | 16d F-04; A13 #18; A15 (untabled a) | Defaults stand; the quote returns the largest holdable job for the tier | pilot job sizes |
| D-07 | Meaning of mint-cap and redeemable capacity: min(phi, 1 - phi), or the redeemable share alone | ISS-15, ISS-166, ISS-16108; 16d F-02; A02 #9; 02e A17, A18 | 4,800 unchanged (equal at phi = 0.5) | any change of phi |
| D-08 | One rule for the 11 operation-id collisions: prefix `admin` in the OpenAPI key (as `15b:17-24` states) or suffix `Admin` on the id (as 15g CR-01 proposes); S0 0.5 has no uniqueness rule | 15g G-01, CR-01; A12 #15 | Both rules are written down today; neither id is renamed | OpenAPI generation, contract tests |
| D-09 | Reservation and waiting rules: late-cancel or no-show penalty; guard 4 at activation; starvation of a large early job; Commons overrun and audit age-out; the anomaly criterion of MT-06 | ISS-66; A02 #24, #25; A06 #28, #31 | No money; a cooldown; one live reservation; no criterion | `ff.job.reservations`, restriction of members |
| D-10 | Whether a failed ledger invariant halts all postings or only minting and new jobs; the ledger store under one serialization point | A07 #5; ISS-43 | Brake engages `kill.all_minting` and `kill.all_new_jobs` only; one ledger, one chain | BM1 |
| D-11 | What a requester gets when a job is cancelled or fails, and whether results of a cancelled job are retrievable | ISS-115; A12 #26 | In-flight cells finish, accepted ones are paid, partial `Deliverable`; no retrieval after `cancelled` in 15a | BM7 acceptance |
| D-12 | Data minimization: free text in permanent tables (reason fields) or reason codes; `members.time_zone`; `Team` data when its owner closes; whether `actor_day_hash` exists; whether a member closed for inactivity can return; backup places, retention, key holder; whether lowering `invite.accountability_days` applies to existing edges | A05 #19, #22, #28; A04 #9; A15 #28; ISS-47; ISS-16021 | Free text stays with the limit stated; backups encrypted in two places; edges treated like retention | G1 sign-off |
| D-13 | Exposure through counters and teams: live headline counter against hidden gold; differencing of daily checkpoints; `team.min_public_members` 10 (equal to `analytics.min_cohort_k`) or an exemption for team totals | A11 #5, #6, #7; ISS-122, ISS-126; 16d F-10, CR-08 | Residuals disclosed; team default 5 (below k) with a warning | public counter, teams |
| D-14 | What e-mail is for and how expiry is announced; minimum member age; the gate or info flag and polarity for automation limits | ISS-44, ISS-102 (e-mail), ISS-119 (11d); A15 #17 | In-app notices; e-mail opt-in notices only, never login or recovery; age 0, line not rendered | first member invitation |
| D-15 | Share cards: computed on request (15a) or stored revocable tokens (15b); member token for V3; money-moving rewards | A12 #25; 15g G-02; ISS-124, ISS-127 | Computed card, no stored link (the stricter privacy reading); V3 descriptive; no rewards | CR-03, `ff.growth.v3_share_card` |
| D-16 | Approval predicates and registry: pooling and copy-paste flags in approval; whether regional `no` blocks; license pairing for `P2`, `P3`; human review of the panel repository for G4; whether a sandbox ever runs submitted code; reachability test method; `lease.max_job_share_ratio` value, rounding, visibility; Commons backlog authorship | ISS-71, ISS-72, ISS-73, ISS-49, ISS-81 (OD-08), ISS-197, ISS-105, ISS-16107, ISS-22; 02e A1, A8, A9 | Stricter S7 guard; region never blocks; no `P2`/`P3` rows; G4 open; no sandbox; ratio 0.34 hidden; operator-authored backlog | G0 sign-off, templates |
| D-17 | The exit rule governs launch and not construction; who acts on each alarm; thresholds locked before day 1 of Phase 1; pilot size cap; minimum G5 interviews; the entity form and the project name (counsel questions CQ-01, CQ-07) | ISS-31, ISS-171, ISS-192, ISS-194, ISS-198, ISS-179, ISS-141; A13 #4 | Rule governs launch; every tripwire names who acts; pilot size held by invite supply; no minimum | launch sign-off |
| D-18 | When the recovery key is shown, and whether join consent is one three-fact notice (11a) or all notices plus eight boxes (11d) | ISS-113; A09 #26, #27 | After the first accepted cell with a marker [H]; no single flow is adopted | BM8 screens |
| D-19 | Copy choices: "advance notice" while tightening is immediate; `declared` in limit sentences; job against task wording; the headline "One minute a day"; the byte-exact copy claim [V]; presentation constants without a parameter | A09 #30, #31, #32, #33, #37; A10 #17 | Text as written, flagged for human and legal review | copy sign-off |
| D-20 | Two-person scope: per-member and per-service loosening carve-out; `audit.accept` and `quarantine.release` as two-person actions; a required `context_id` on member reads; whether member lists and invite trees exist for admins | A10 #15; 15e open points 3, 4 | One admin with step-up for audit accept and release; the read is logged, not justified | BM2 |
| D-21 | Template and naming details: the `delimiter_collision` rule for code slots; the name `hamyar_config_epoch_count`; `TH-01` early `fail`; the envelope proposal margin | A08 #16; A07 #23; A11 #14, #15 | As written | none |
| D-22 | Open S3 and parameter values: `retention.ip_hash_ttl_days` = 0 effect; split of `invite.strike_window_days`; floor on `report.decision_sample_rate`; value of `abuse.admin_lookup_rate`; name of the pending-approval lifetime; a platform-wide join limit; S5 file names and heading numbers; the 17 S3.2 rows to add | A13 #21, #22; ISS-16009, ISS-16015, ISS-16017, ISS-16020, ISS-52; 16d F-12; 02e rows New 1 to New 17 | Defaults stand; no value invented | S16 seed (`AC-param-02`), assembly |

## 5 Overall verdict and the next fix round

**Verdict: NOT READY.** The per-part verdicts say READY WITH LOGGED ITEMS fifteen times, and each is true of one part read alone. The specification as a whole is not ready to assemble or to build from, for four reasons:

1. **The reconciliation was never applied.** `15c` to `15g` and `16d` list at least 110 edits for later cells (27 in `15c`, 15 in `15f`, 43 CR ids in `15g`, 25 in `16d`, plus the `15d` and `15e` lists, which were not counted; section 3). Of those checked at the cited line, 64 are unapplied and none is applied as written. The part files still disagree with the API and parameter files on paths, operation ids, field names, permission names and ranges. A build that follows 10a, 11b, 11c, 12 and 13 as written implements different endpoints than S15a and S15b define. The structural check meant to catch this (`check_refs.py api`) counts a path as defined if it appears anywhere in `spec/15*.md`, so it passes while the parts disagree.
2. **The parts disagree with each other on the data model, including the most safety-critical datum.** 05a stores an IP hash in the relational Device table while 10a and 10b promise it exists only in a volatile counter store (row 9); 05a, 05b, 09, 10a and 10b use different column, key, state and entity names (rows 8 and 11 to 16, 21); 11a and 11d specify incompatible join flows (row 26); S12 and S13 specify two experiment machines (row 30). None of the 15 audits read more than its own files plus S0 and the Founding Document (every log's Not verified section says so), so these cross-part contradictions are the only checking the parts have had, and 86 of them are logged and not fixed.
3. **Safety parameters fail open.** `launch.min_signoffs` accepts 1 and `launch.min_approved_services` accepts 0 in S0 and S16 (rows 5 and section 3.4); `change.notice_days_*` and `retention.ip_hash_ttl_days` accept 0; the gold sampling floor may be 0. S14 defends two of these in code, which the parameter table does not say.
4. **Decisions only the owner can take are open and block sign-off.** Two blocking register issues (`ISS-11`, `ISS-12`) are `proposed`, not decided; 22 groups of owner decisions are listed in section 4; with one admin no gate can be signed (row 6).

No blocking finding is open in the logs, 273 of 397 tabled findings were fixed in place, and no log found a ground-rule violation (no provider fact invented, no volunteer-account automation, `declared` not `guaranteed`). That is the state of the parts, not of the whole. The verdict would become READY WITH LOGGED ITEMS when fix tasks FIX-01 to FIX-24 are done and decisions D-01, D-03, D-05, D-07, D-12, D-15, D-17, D-18 and D-20 are taken or their defaults are accepted in writing; the other decisions can ride on their defaults. Nothing was executed anywhere in this audit chain: no script, test, query or simulation was run by any log or by this file, and the numbers in the specification are recomputed on paper only.

### 5.1 Fix tasks for the next round

Each task is one cell: one or two files, an exact edit, an acceptance. No task renames an id, parameter, endpoint or state (cell rule); where a rename is needed it is logged. "Read-back" means the cell reads the cited lines after the edit and states what it saw. The structural scripts are `check_params.py`, `check_refs.py api`, `check_issues.py` and `check_audit.py`; they do not show consistency (section 3), so every task also needs the read-back.

| Task | Files | Edit | Acceptance |
| --- | --- | --- | --- |
| FIX-01 | `spec/00-conventions.md` (Table C), `spec/16-parameters.md` (16.13) | `launch.min_signoffs` range `2..5`, `launch.min_approved_services` `1..20`; `change.notice_days_default`, `change.notice_days_price` `1..90`; `retention.ip_hash_ttl_days` `1..30`; `price.eta_alarm_threshold` `> 0 .. 1` | `check_params.py` passes; read-back of `00-conventions.md:762-763` and `16-parameters.md:313,389-392` shows the new ranges |
| FIX-02 | `spec/16-parameters.md` | 16d CR-01, CR-03, CR-05, CR-09, CR-10, CR-12, CR-15 to CR-19, CR-21 to CR-24 (not CR-02, which waits for D-07) | `check_params.py`; read-back of each cited row |
| FIX-03 | `spec/00-conventions.md` | 16d CR-06, CR-07, CR-09, CR-11 (S0 side) and CR-02 and CR-08 once D-07 and D-13 are taken | `check_params.py`; read-back |
| FIX-04 | `spec/16b-parameters-a.md`, `spec/16c-parameters-b.md` | 16d CR-13, CR-14, CR-22, CR-25; rows for the parameters absent from S0 and S16 (A03 #29, A12 #29, A11 #16) or marked alias | `check_params.py`; every name read in S15, S14, S12, S13 resolves to a row or an alias |
| FIX-05 | `spec/10a-identity.md` | `15c` edits 1 to 14, 19, 26 | read-back: no `/v1/auth-challenges`, `device-link-offers`, `members/me/keys`, `admin/auth-challenges`, `createAdminAction` left; `check_refs.py api` passes |
| FIX-06 | `spec/07-policy.md`, `spec/06b-admission.md`, `spec/04-architecture.md` | `15c` edits 15 to 18, 20, 22 to 24 (locate the drifted lines first) | read-back; `check_refs.py api` |
| FIX-07 | `spec/11b-requester-ux.md` | `15c` edit 21 and every `15d` row for 11b (`11b:147-151` and the rows and screen prose before them) | read-back: every cited `/v1` path exists in S15a to S15d |
| FIX-08 | `spec/12-public-growth.md` | `15d` edits at `12:29-38`, `12:466`, `12:511` and the 12.9.2 rows | read-back |
| FIX-09 | `spec/11c-admin-tools.md` | `15e` rows for ledger, parameters, metrics (`11c:457-461`, `502-509`, `555-557`, `615`) | read-back |
| FIX-10 | `spec/11c-admin-tools.md` | `15e` rows for launch, kill switches, member lookup, work claims and the `AC-*` rows (`11c:266`, `647-652`, `700-701`, `751-752`, `793-801`) | read-back |
| FIX-11 | `spec/13-measurement.md` | `15f` E1 to E15, `perm.metrics.view_small_cells` removed (cited `13:921`), growth metric definitions for V1, V3, V5, V6 (A11 #4), seeds for TRIP-10, 11, 15 (A13 #6) | read-back; `check_params.py` |
| FIX-12 | `spec/15a-api-core.md` | `15g` CR-04, CR-08, CR-15, CR-16, CR-19, CR-29, CR-31, CR-33, CR-36, CR-37 | `check_refs.py api`; read-back |
| FIX-13 | `spec/15b-api-admin.md` (15.21 to 15.28) | `15g` CR-04 to CR-07, CR-11, CR-20 to CR-22, CR-24, CR-27, CR-32 | read-back |
| FIX-14 | `spec/15b-api-admin.md` (15.29 to 15.34) | `15g` CR-09, CR-17, CR-18, CR-34, CR-35, CR-38, CR-39, CR-42, CR-43; merge the member appeal and inbox operations of `15d` so 15a and 15b define them (A12 #27, #28) | read-back; `check_refs.py api` |
| FIX-15 | `spec/14-launch-gates.md` | `15g` CR-23, CR-25, CR-26, CR-28, CR-40, CR-41; add `## Issues raised` for `ISS-141`, `ISS-143`, `ISS-144`, `ISS-147` (A03 #26); correct names (A03 #29, #30) | `check_issues.py`; read-back of `14:623` |
| FIX-16 | `spec/05a-entities.md` | Add the Lease, Job, Cell columns and the key names that 05b and 09 use; add `StateTransition` and `mint_headroom` (A05 #15 to #18, #20, #21, #23 to #27) | read-back: each named column exists; `check_issues.py` |
| FIX-17 | `spec/05a-entities.md` | Device, Member and Invite: move `creation_ip_hash` out of the database to match 10a 10.14.2; clearing rule for the invite edge; `vol_` not computed on public reads (A04 #6, #15, #20, #21) | read-back against `10a` 10.14.2 and `10b` AC-safety-01 |
| FIX-18 | `spec/10a-identity.md`, `spec/10b-safety.md` | One name set for secrets, `MemberKey`, `AdminUser`, `AdminCredential`, `Session`, `AdminAction` (A04 #19) | read-back: `g1.secrets_inventory_complete` names equal in both files and in 05a |
| FIX-19 | `spec/00-conventions.md` (0.9) | Submission transitions, Audit third state, `suspended` to `in_review`, Referral, Alarm, Invite machines, Commons path into `admitted`, early exit for `exhausted` (A15 #21, #22, #25, #33 to #35; A06 #27, #32) | read-back of each machine |
| FIX-20 | `spec/00-conventions.md` (0.10, 0.13) | Approval-count ranges (A15 #29), retention classes for request logs and events (A15 #50), the S11 file row `spec/11-experiences.md` that does not exist (A15 #46), the sub-block rule for parts with more than three files (A15 #47), `BM2` and the service count (A15 #49) | read-back of `00-conventions.md:916-932` |
| FIX-21 | `spec/10b-safety.md`, `spec/11b-requester-ux.md`, `spec/11c-admin-tools.md`, `spec/11d-i18n-copy.md` | One heading numbering plan for S10 and S11 and the references that cite it (A04 #18, A10 #10, 02e B4); remove the duplicate ISS-117 to ISS-119 block | read-back: no heading number defined twice across the files of a part |
| FIX-22 | `spec/11b-requester-ux.md`, `spec/07-policy.md` | One owner for requester rejection copy and for the empty eligible set; the kill-switch pause reasons (A10 #11, #12, #13) | read-back |
| FIX-23 | `spec/12-public-growth.md`, `spec/13-measurement.md` | One Experiment machine and event list in S12.11.3, `AC-exp-01` to `AC-exp-08` and 13.8 (A11 #2) | read-back |
| FIX-24 | `spec/19-risks.md`, `spec/03-assumptions.md` | A cross-reference table between the two `OD` series, with no renaming (A13 #2); the S3.2 rows of `02e` 2.E.3 that are `no` (A13 #22) | read-back; `check_issues.py` |
| FIX-25 | `spec/08b-verification.md`, `spec/06a-ledger.md` | `v_commons` against `v_member` and the shortfall path, after D-04 (A08 #13, #14) | read-back |
| FIX-26 | `spec/06a-ledger.md` | Apply D-03 (closed-escrow reversal, expired slice, levy on overturn, lot clock; A01 #6, #18, #20, #23), after the decision | read-back; `check_issues.py` |
| FIX-27 | any file named by D-08 | Apply the chosen operation-id collision rule everywhere, after the decision | `check_refs.py api` |
| FIX-28 | `scripts/check_refs.py` (owner or Steward, not a spec cell) | Run `api` with the decision tables of `15c` to `15g` excluded, so a path counts as defined only in `15a` to `15b` and the reconciled parts (as 15g says) | the script fails today on the unapplied edits and passes after FIX-05 to FIX-14 |

## Not verified

- Nothing was executed. `scripts/check_audit.py`, `check_params.py`, `check_issues.py` and `check_refs.py` were not run by this reviewer; they run in CI at submission. Whether C-070's one-name fix in `spec/08b-verification.md` (8.29.1) is on main was not re-read. The preflight result is reported in the cell reply, not here.
- The edit lists of `15d` (lines 1 to 399 of 460), `15e` (lines 1 to 284 of 332) and `15f` (lines 1 to 179 of 228) were not read; only their tails were. The 8 `15c`, 30 `15g`, 16 `16d` and the unread `15d`, `15e`, `15f` edits marked NOT CHECKED or NOT LOCATED may be applied; no reader saw them applied.
- Part files drifted by a few lines after the audits' edits, so cited lines were matched to the nearest text; NOT LOCATED rows may be applied elsewhere in the file.
- The `fixed` actions in the 15 logs were taken at their word; this file did not re-read the part files to confirm each fix. Where section 3 says PARTLY CLOSED it relies on the log, not on a re-read.
- Cell ids C-043 (A02) and C-056 (A15) are inferred. The 25 untabled minor items are counted from the logs' prose (A15 part 3 lists "several", counted as 6).
- Lines for rows 8 to 17 and 27 to 29 are the logs' own and approximate (the logs say so); rows 11 to 17 give a section only. The `02e` conflicts A1, A3 to A6, A8 to A16 were not re-checked against the part files.
- The 15 logs themselves were not re-audited: a log that missed a defect is not caught here. None of the 15 audits covers `spec/02b` to `02d`, `02f`, `15c` to `15g`, `16b` to `16d`, `spec/02e`, or any file not named in section 1.
- Persian wording, legal conclusions, provider facts and reachability remain [V] or [H] throughout and were not assessed.

Verdict: NOT READY
